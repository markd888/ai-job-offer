#!/usr/bin/env python3
"""Grade a candidate run of /evaluate-position against the frozen golden labels.

Usage: python3 grade.py results.json

Two result shapes, detected per run:

v2 (scoring v2, every result has "fit_score") — graded against each case's
"label_v2" (all 32 cases). Each result:
  {"id", "eligibility": "eligible|needs_review|blocked",
   "requirements": [{"requirement", "status"}],
   "dimensions": {"<dim>": {"evidence_class", "evidence": [{"quote", "source"}]}},
   "attractiveness", "fit_score", "tier"}
  Gate: tier agreement >= 0.8, eligibility accuracy >= 0.85, every expected
  FAIL detected, no false block, every expected UNKNOWN reported as UNKNOWN
  (never FAIL), fit in range >= 0.7, evidence traceability = 100%.

v1 (legacy, {"id", "tier", "score", "matched_filter"}) — graded against "label"
on the 12 v1 cases only. Gate: tier agreement >= 0.8 and every filter detected.

Exit 0 pass / 1 fail / 2 usage error.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
GATE = 0.8
GATE_V2 = {"tier": 0.8, "eligibility": 0.85, "fit_in_range": 0.7}


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.replace("*", "")).strip().lower()


def load_results(path: Path) -> list[dict] | None:
    try:
        parsed = json.loads(path.read_text())
    except json.JSONDecodeError as e:
        print(f"{path}: not valid JSON ({e})", file=sys.stderr)
        return None
    if not isinstance(parsed, list):
        print(f"{path}: expected a JSON array of result objects, got {type(parsed).__name__}", file=sys.stderr)
        return None
    if not all(isinstance(r, dict) and "id" in r for r in parsed):
        print(f"{path}: each result must be an object with an 'id' key", file=sys.stderr)
        return None
    return parsed


def grade_v1(cases: list[dict], results: dict[str, dict]) -> int:
    cases = [c for c in cases if "label" in c]
    missing = [c["id"] for c in cases if c["id"] not in results]
    tier_hits, tier_total, deltas, filter_misses, rows = 0, 0, [], [], []
    for case in cases:
        if case["id"] in missing:
            continue
        label, got = case["label"], results[case["id"]]
        if label["tier"] == "filtered":
            ok = got.get("matched_filter") == label["hard_filter"]
            if not ok:
                filter_misses.append(case["id"])
            rows.append((case["id"], label["tier"], got.get("tier"), "ok" if ok else "MISSED FILTER"))
        else:
            tier_total += 1
            ok = got.get("tier") == label["tier"]
            tier_hits += ok
            if isinstance(got.get("score"), int):
                deltas.append(abs(got["score"] - label["score"]))
            rows.append((case["id"], label["tier"], got.get("tier"), "ok" if ok else "TIER MISS"))
    for r in rows:
        print(f"  {r[0]:<24} label={r[1]:<9} got={str(r[2]):<9} {r[3]}")
    if missing:
        print(f"  missing from results: {', '.join(missing)}")
    agreement = tier_hits / tier_total if tier_total else 0.0
    print(f"tier agreement: {tier_hits}/{tier_total} = {agreement:.2f} (gate {GATE})")
    if deltas:
        print(f"mean |Δscore|: {sum(deltas) / len(deltas):.2f}")
    failed = bool(missing) or filter_misses or agreement < GATE
    print("FAIL" if failed else "PASS")
    return 1 if failed else 0


def _matches(text: str, needle: str) -> bool:
    return norm(needle)[:40] in norm(text) or norm(text) in norm(needle)


def grade_v2(cases: list[dict], results: dict[str, dict]) -> int:
    corpus = norm((HERE / "profile.md").read_text())
    cv = HERE / "cv.md"
    if cv.exists():
        corpus += " " + norm(cv.read_text())
    missing = [c["id"] for c in cases if c["id"] not in results]
    n = {"tier": [0, 0], "eligibility": [0, 0], "fit_in_range": [0, 0], "evidence_class": [0, 0],
         "fail_detected": [0, 0], "unknown_handled": [0, 0], "quotes_traced": [0, 0]}
    false_blocks, untraced, rows = [], [], []

    def tally(key, ok):
        n[key][0] += bool(ok); n[key][1] += 1

    for case in cases:
        if case["id"] in missing:
            continue
        lab, got = case["label_v2"], results[case["id"]]
        reqs = got.get("requirements") or []
        flags = []
        tier_ok = got.get("tier") == lab["tier"]; tally("tier", tier_ok)
        elig_ok = got.get("eligibility") == lab["eligibility"]; tally("eligibility", elig_ok)
        if lab["eligibility"] != "blocked" and got.get("eligibility") == "blocked":
            false_blocks.append(case["id"])
        for f in lab["must_fail"]:
            ok = any(r.get("status") == "FAIL" and _matches(r.get("requirement", ""), f) for r in reqs)
            tally("fail_detected", ok)
            if not ok: flags.append(f"missed FAIL '{f[:30]}'")
        for kw in lab["must_unknown"]:
            hits = [r for r in reqs if kw.lower() in (r.get("requirement", "") + " " + r.get("jd_quote", "")).lower()]
            ok = any(r.get("status") == "UNKNOWN" for r in hits) and not any(r.get("status") == "FAIL" for r in hits)
            tally("unknown_handled", ok)
            if not ok: flags.append(f"'{kw}' not UNKNOWN")
        if lab["fit_range"] and isinstance(got.get("fit_score"), (int, float)):
            lo, hi = lab["fit_range"]
            ok = lo <= got["fit_score"] <= hi; tally("fit_in_range", ok)
            if not ok: flags.append(f"fit {got['fit_score']} ∉ [{lo},{hi}]")
        dims = got.get("dimensions") or {}
        for k, allowed in lab["evidence"].items():
            tally("evidence_class", (dims.get(k) or {}).get("evidence_class") in allowed)
        for k, d in dims.items():
            for q in (d or {}).get("evidence") or []:
                ok = norm(q.get("quote", "")) in corpus and bool(q.get("quote"))
                tally("quotes_traced", ok)
                if not ok: untraced.append(f"{case['id']}.{k}: {q.get('quote', '')[:50]}")
        status = "ok" if tier_ok and elig_ok and not flags else ", ".join(
            (["TIER"] if not tier_ok else []) + (["ELIG"] if not elig_ok else []) + flags)
        rows.append((case["id"], f"{lab['tier']}/{lab['eligibility']}",
                     f"{got.get('tier')}/{got.get('eligibility')}", status))

    for r in rows:
        print(f"  {r[0]:<28} label={r[1]:<16} got={r[2]:<16} {r[3]}")
    if missing:
        print(f"  missing from results: {', '.join(missing)}")
    rate = {k: (h / t if t else 1.0) for k, (h, t) in n.items()}
    for k, (h, t) in n.items():
        gate = GATE_V2.get(k)
        print(f"{k.replace('_', ' ')}: {h}/{t} = {rate[k]:.2f}" + (f" (gate {gate})" if gate else ""))
    print(f"false blocks: {len(false_blocks)}" + (f" ({', '.join(false_blocks)})" if false_blocks else ""))
    for u in untraced[:10]:
        print(f"  untraced quote: {u}")
    print("override preservation: covered by tests/test_score_immutability.py (not part of a model run)")
    failed = (bool(missing) or bool(false_blocks)
              or any(rate[k] < g for k, g in GATE_V2.items())
              or rate["fail_detected"] < 1 or rate["unknown_handled"] < 1 or rate["quotes_traced"] < 1)
    print("FAIL" if failed else "PASS")
    return 1 if failed else 0


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: grade.py <results.json>", file=sys.stderr)
        return 2
    parsed = load_results(Path(argv[1]))
    if parsed is None:
        return 2
    results = {r["id"]: r for r in parsed}
    cases = [json.loads(p.read_text()) for p in sorted((HERE / "cases").glob("*.json"))]
    if parsed and all("fit_score" in r or r.get("eligibility") == "blocked" for r in parsed) \
            and any("fit_score" in r for r in parsed):
        print("scoring v2 run")
        return grade_v2(cases, results)
    return grade_v1(cases, results)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
