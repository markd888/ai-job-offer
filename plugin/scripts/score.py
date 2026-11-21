#!/usr/bin/env python3
"""Scoring v2 for /evaluate-position and /job-search: compute, record, override.

Claude writes the assessment JSON (eligibility per requirement, evidence per
dimension, company attractiveness). This script validates it, does all the
arithmetic and tier rules (scoring_schema.py), and records the result. The
first assessment of a role is never edited: each run writes a new dated
score-<date>.json, and meta.md's predicted_tier / initial_fit_score are set once.

Commands:
  compute  ASSESSMENT.json [--profile profile.md]
           Validate and print the result as JSON. Writes nothing.
  record   ROLE_DIR ASSESSMENT.json [--profile profile.md] [--today YYYY-MM-DD]
           Write ROLE_DIR/score-<date>.json and the summary keys in meta.md.
  override ROLE_DIR --tier P0|P1|P2 --reason "..." [--today YYYY-MM-DD]
           Record the user's tier override. The prediction stays.

Exit codes: 0 ok, 1 invalid assessment/config (errors on stderr), 2 usage.
Schema: plugin/schemas/score.schema.md.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, HERE / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


S = _load("scoring_schema")
MF = _load("metafile")


def _fail(errors: list[str]) -> int:
    for e in errors:
        print(e, file=sys.stderr)
    return 1


def _config(profile: Path | None) -> tuple[dict, dict]:
    if profile and profile.is_file():
        return S.config_from_profile(profile.read_text())
    return {}, dict(S.DEFAULT_THRESHOLDS)


def evaluate(assessment_path: Path, profile: Path | None) -> tuple[dict | None, dict | None, list[str]]:
    try:
        a = json.loads(assessment_path.read_text())
    except (OSError, ValueError) as e:
        return None, None, [f"{assessment_path}: {e}"]
    errors = S.validate(a)
    w, t = _config(profile)
    errors += S.validate_config(w or S.DEFAULT_WEIGHTS, t)
    if errors:
        return a, None, errors
    return a, S.compute(a, w, t), []


def next_free(role: Path, today: str) -> Path:
    p = role / f"score-{today}.json"
    n = 2
    while p.exists():
        p = role / f"score-{today}-v{n}.json"
        n += 1
    return p


def record(role: Path, a: dict, result: dict, today: str) -> Path:
    meta_path = MF.role_meta(role)
    out = next_free(role, today)
    out.write_text(json.dumps({"assessed": today, "assessment": a, "result": result},
                              indent=2, ensure_ascii=False) + "\n")
    meta = meta_path.read_text()
    values = {
        "scoring_version": str(S.SCORING_VERSION),
        "fit_score": str(result["fit_score"]),
        "tier": result["tier"],
        "eligibility": result["eligibility"],
        "evidence_confidence": result["evidence_confidence"],
    }
    # Set once: the system's first prediction is what outcomes get compared with.
    if not MF.field(meta, "predicted_tier"):
        values["predicted_tier"] = result["tier"]
    if not MF.field(meta, "initial_fit_score"):
        values["initial_fit_score"] = str(result["fit_score"])
    # A standing override still wins over a rescore's tier.
    if MF.field(meta, "tier_override"):
        values["tier"] = MF.field(meta, "tier_override")
    meta = MF.set_fields(meta, values)
    meta = MF.append_history(meta, f"- {today} — scored v{S.SCORING_VERSION}: fit {result['fit_score']}, "
                                   f"{result['tier']}, {result['eligibility']} ({out.name})")
    meta_path.write_text(meta)
    return out


def override(role: Path, tier: str, reason: str, today: str) -> None:
    meta_path = MF.role_meta(role)
    meta = meta_path.read_text()
    values = {"tier": tier, "tier_override": tier, "override_reason": json.dumps(reason, ensure_ascii=False),
              "override_date": today}
    if not MF.field(meta, "predicted_tier") and MF.field(meta, "tier"):
        values["predicted_tier"] = MF.field(meta, "tier")  # v1 role: keep what the system said
    meta = MF.set_fields(meta, values)
    meta = MF.append_history(meta, f"- {today} — tier overridden to {tier} by user: {reason}")
    meta_path.write_text(meta)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("compute"); c.add_argument("assessment", type=Path); c.add_argument("--profile", type=Path)
    r = sub.add_parser("record"); r.add_argument("role", type=Path); r.add_argument("assessment", type=Path)
    r.add_argument("--profile", type=Path); r.add_argument("--today", default=date.today().isoformat())
    o = sub.add_parser("override"); o.add_argument("role", type=Path)
    o.add_argument("--tier", required=True, choices=S.TIERS); o.add_argument("--reason", required=True)
    o.add_argument("--today", default=date.today().isoformat())
    a = ap.parse_args(argv)

    if a.cmd == "override":
        if not a.reason.strip():
            return _fail(["--reason must not be empty"])
        override(a.role, a.tier, a.reason.strip(), a.today)
        print(f"overridden: {a.tier}")
        return 0
    assessment, result, errors = evaluate(a.assessment, a.profile)
    if errors:
        return _fail(errors)
    if a.cmd == "compute":
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    out = record(a.role, assessment, result, a.today)
    print(json.dumps({**result, "file": out.name}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
