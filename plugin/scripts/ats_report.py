"""The ats-check report: seven sections, five component results, optional JSON (#38 phase 5).

Not a CLI — ats-check.py loads this file by path (scripts run with `python3 -I`).

There is no single score. Five components are reported side by side, each with
its basis, and none can offset another: keyword coverage never makes up for
broken contacts or a missing employment history.
"""
from __future__ import annotations

import json
from datetime import date

LIMITATIONS = ("This report evaluates document extraction and compatibility. It does not predict a specific "
               "ATS ranking or hiring decision.")
GENERAL_LIMITS = [
    "Parsing is a simulation with bounded heuristics, not any vendor's parser; real systems differ from each other.",
    "Requirement matching looks for the posting's terms in your CV lines. It can't judge depth, recency or years "
    "of experience — read the evidence, not the counts.",
]


def snippet(text: str, terms: list[str], width: int = 110) -> str:
    """The part of a long evidence line around the first matched term."""
    if len(text) <= width:
        return text
    low = text.lower()
    at = min((i for i in (low.find(t.split()[0]) for t in terms if t) if i >= 0), default=0)
    start = max(0, min(at - width // 3, len(text) - width))
    return ("…" if start else "") + text[start:start + width].strip() + ("…" if start + width < len(text) else "")


def parse_summary(p: dict) -> list[str]:
    c = p["candidate"]
    val = lambda f: f["value"] if f["value"] is not None else "—"  # noqa: E731
    out = ["What a parser could fill in from this text (heuristic; every field may be missing):", "",
           f"- **Contact:** name {val(c['name'])}; email {val(c['email'])}; phone {val(c['phone'])}; "
           f"location {val(c['location'])}; LinkedIn {val(c['linkedin'])}",
           f"- **Sections recognised:** {', '.join(p['sections']) or '—'}"]
    jobs = p["experience"]
    dated = sum(1 for e in jobs if e["start_date"]["value"])
    out.append(f"- **Employment:** {len(jobs)} entr{'y' if len(jobs) == 1 else 'ies'}, {dated} with dates")
    out += [f"  - {val(e['job_title'])} · {val(e['company'])} · {val(e['start_date'])} – {val(e['end_date'])}"
            for e in jobs]
    out.append(f"- **Education:** {len(p['education'])} · **Skills:** {len(p['skills'])} · "
               f"**Languages:** {len(p['languages'])} · **Certifications:** {len(p['certifications'])}")
    out += [f"- ⚠️ {w}" for w in p["parsing_warnings"]]
    return out


def components(ctx: dict) -> list[dict]:
    """Five results, each with what it's based on. Never combined into one number."""
    checks, parsed = ctx["checks"], ctx["parsed"]
    hard = [c for c in checks if c[1] is not None]
    passed = sum(1 for c in hard if c[1])
    out = [{"component": "Document integrity", "result": f"{passed}/{len(hard)} hard checks pass",
            "basis": f"pages, contacts, glyphs, order{', fidelity' if ctx['md'] else ''}; "
                     f"{len(ctx['warnings'])} warning(s)"}]
    c = parsed["candidate"]
    jobs = parsed["experience"]
    have = {"name": c["name"]["value"], "email": c["email"]["value"], "phone": c["phone"]["value"],
            "employment entries": bool(jobs), "dates on every entry": bool(jobs) and all(e["start_date"]["value"] for e in jobs),
            "education": bool(parsed["education"]), "skills": bool(parsed["skills"])}
    missing = [k for k, v in have.items() if not v]
    out.append({"component": "Parsing completeness", "result": f"{len(have) - len(missing)}/{len(have)} key fields",
                "basis": "missing: " + ", ".join(missing) if missing else "name, email, phone, entries, dates, education, skills"})
    rows = [r for r in ctx["fidelity"] if r["status"] != "NOT_IN_SOURCE"]
    if rows:
        ok = sum(r["status"] == "EXTRACTED" for r in rows)
        out.append({"component": "Extraction fidelity", "result": f"{ok}/{len(rows)} fields match the CV",
                    "basis": "field by field against the CV markdown"})
    else:
        out.append({"component": "Extraction fidelity", "result": "not checked", "basis": "no CV markdown given (--md)"})
    m = ctx["matching"]
    if m:
        req = [r for r in m if r["category"] == "REQUIRED" and r["status"] != "AMBIGUOUS"]
        sup = sum(r["status"] == "SUPPORTED" for r in req)
        part = sum(r["status"] == "PARTIALLY_SUPPORTED" for r in req)
        out.append({"component": "Job requirement coverage",
                    "result": f"{sup}/{len(req)} required shown in experience" if req else "no required items listed",
                    "basis": f"{part} more partially; {len(m)} requirement(s) in all, per category in section 4"})
    else:
        out.append({"component": "Job requirement coverage", "result": "not checked",
                    "basis": "no posting given (--requirements or --jd)"})
    lay = ctx["layout"]
    out.append({"component": "Layout compatibility",
                "result": "no risks observed" if not lay else f"{len(lay)} risk(s) observed",
                "basis": ", ".join(sorted({x["risk"] for x in lay})) if lay else "positions, fonts and parts checked"})
    return out


def recommendations(ctx: dict) -> list[str]:
    out: list[str] = []
    fixes = {"pages": "Trim to the expected page count, by relevance to this posting.",
             "contacts": "Put email and phone in the text itself, not an image, icon or header.",
             "glyphs": "Rebuild the PDF so it writes plain characters (cv-build.py does).",
             "order": "Use a single-column layout so sections extract in order.",
             "fidelity": "Text is drawn as shapes or images — rebuild the PDF from the markdown."}
    out += [fixes[n] for n, ok, _ in ctx["checks"] if ok is False and n in fixes]
    for r in ctx["fidelity"]:
        if r["status"] in ("MISSING", "AMBIGUOUS", "CONFLICTING"):
            out.append(f"{r['field']}: {r['status'].lower()} after extraction — check that part of the layout.")
    if any(not e["start_date"]["value"] for e in ctx["parsed"]["experience"]):
        out.append("Give every role a date range on its own line (e.g. `2021 – 2024`).")
    for x in ctx["layout"]:
        out.append(f"{x['risk'].capitalize()}: {x['observed'].split(' — ')[0]}.")
    gaps = [r["requirement"] for r in ctx["matching"] if r["category"] == "REQUIRED" and r["status"] == "NOT_FOUND"]
    if gaps:
        out.append("Required items not on this CV: " + "; ".join(g[:60] for g in gaps[:4])
                   + ". Add one only if your experience has it — otherwise it stays a gap.")
    partial = [r["requirement"] for r in ctx["matching"] if r["source"] == "skills"]
    if partial:
        out.append("Listed under skills but not shown in a role: " + "; ".join(p[:50] for p in partial[:4])
                   + ". If a role used it, say so in that role's line.")
    seen: set[str] = set()
    return [x for x in out if not (x in seen or seen.add(x))][:12]


def render(ctx: dict) -> str:
    checks = ctx["checks"]
    hard_fail = [n for n, ok, _ in checks if ok is False]
    L = [f"# ATS check — {ctx['name']}", "",
         f"{date.today().isoformat()} · text layer via {ctx['engine']} · "
         f"{'PASS' if not hard_fail else 'FAIL: ' + ', '.join(hard_fail)}", "",
         "| Component | Result | Basis |", "|---|---|---|"]
    L += [f"| {c['component']} | {c['result']} | {c['basis']} |" for c in ctx["components"]]

    L += ["", "## 1. Document integrity", "", "| Check | Result | Detail |", "|---|---|---|"]
    L += [f"| {n} | {'➖' if ok is None else '✅' if ok else '❌'} | {d} |" for n, ok, d in checks]
    if ctx["warnings"]:
        L += ["", "### Warnings (don't fail the check)", ""]
        L += [f"- **{w['check']}** — {w['detail']}" for w in ctx["warnings"]]

    L += ["", "## 2. Parsing simulation", "", *parse_summary(ctx["parsed"])]

    L += ["", "## 3. Extraction fidelity", ""]
    if ctx["fidelity"]:
        L += ["| Field | In the CV | Parsed | Status | Note |", "|---|---|---|---|---|"]
        L += [f"| {r['field']} | {r['expected'] if r['expected'] is not None else '—'} | "
              f"{r['extracted'] if r['extracted'] is not None else '—'} | {r['status']} | {r['note']} |"
              for r in ctx["fidelity"]]
    else:
        L.append("Not checked — no CV markdown given.")

    L += ["", "## 4. Job description matching", ""]
    m = ctx["matching"]
    if m:
        cov = ctx["coverage"]
        L += ["Requirements " + ("Claude extracted from the posting" if ctx["requirements_from_claude"]
                                 else "split from the posting by its headings")
              + ". Covered = shown in experience or the summary; skills-list-only counts as partial.", "",
              " · ".join(f"{c.replace('_', ' ').lower()} {h}/{n}" for c, (h, n) in cov.items()), "",
              "| Requirement | Category | Status | Evidence |", "|---|---|---|---|"]
        for r in m:
            ev = f"\"{snippet(r['evidence'], r['terms'])}\" ({r['source']})" if r["evidence"] else "—"
            if r["note"]:
                ev += f" — {r['note']}"
            L.append(f"| {r['requirement'][:90]} | {r['category']} | {r['status']} | {ev} |")
        L += ["", "A requirement that isn't supported stays a gap: rephrase only experience the master CV already has."]
    elif not ctx["kw"]:
        L.append("Not checked — no posting given.")
    kw, hit = ctx["kw"], ctx["kw_hit"]
    if kw:
        L += ["", f"### Keyword coverage: {len(hit)}/{len(kw)}", "",
              "Covered: " + (", ".join(hit) or "—"), "",
              "Missing: " + (", ".join(k for k in kw if k not in hit) or "—"), "",
              "Add a missing keyword only where the master CV or profile supports it; otherwise it stays a gap."]
    if ctx["suggestions"]:
        L += ["", "### Frequent posting terms not in the CV (suggestions)", "", ", ".join(ctx["suggestions"])]

    L += ["", "## 5. Readability & compatibility", ""]
    if ctx["layout"]:
        L += ["What the text layer shows (observations, not a verdict on any particular ATS):", ""]
        L += [f"- **{x['risk']}** — {x['observed']}" for x in ctx["layout"]]
    else:
        L.append("No layout risks observed in the text layer.")
    L += [f"- {n}" for n in ctx["layout_notes"]]

    L += ["", "## 6. Recommendations", ""]
    recs = recommendations(ctx)
    L += [f"- {r}" for r in recs] if recs else ["Nothing to change for extraction."]

    L += ["", "## 7. Limitations", "", LIMITATIONS, ""]
    L += [f"- {x}" for x in GENERAL_LIMITS]
    if ctx["format"] == "docx":
        parts = ctx["parts"]
        where = [f"{k.replace('_', ' ')}: {len(v)} line(s)" for k, v in parts.items() if v and k != "body"]
        L += ["", "### What the extraction can't see", ""]
        if where:
            L += ["Read separately from the body — " + "; ".join(where) + ".", ""]
        L += [f"- {x}" for x in ctx["limitations"]]
    return "\n".join(L) + "\n"


def to_json(ctx: dict) -> str:
    keep = {k: ctx[k] for k in ("name", "format", "engine", "warnings", "parsed", "fidelity", "matching",
                                 "layout", "components") if k in ctx}
    keep["checks"] = [{"check": n, "passed": ok, "detail": d} for n, ok, d in ctx["checks"]]
    keep["exit_code"] = 1 if any(ok is False for _, ok, _ in ctx["checks"]) else 0
    keep["limitations"] = [LIMITATIONS, *GENERAL_LIMITS, *ctx.get("limitations", [])]
    return json.dumps(keep, ensure_ascii=False, indent=2) + "\n"
