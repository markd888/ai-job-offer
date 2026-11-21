#!/usr/bin/env python3
"""Where rejections cluster: stage, predicted tier, channel, role level, time to reject.

Read by career-coach's rejection review (#11), /today's monthly prompt and
/wrap-up's retrospective, so all three quote the same numbers.

Usage:
  python3 -I rejection-patterns.py --userdata ./userdata [--since YYYY-MM-DD] [--json]

A rejection is a role with status `rejected`. Most applications end in one, so
the useful comparison is the reply rate: the share of a group's applications
that got past the application stage (a screen or further, rejected or not).

- A stage is a pattern at STAGE_SAMPLE or more rejections past the application
  (the same rule as /today's coach trigger).
- Any other group is a pattern when it has MIN_SAMPLE or more applications and
  its reply rate is at most half the overall rate ("low"), or at least double
  it with 2+ replies ("high"). "Low" also needs 2+ replies to have been
  expected at the overall rate. Groups that are unknown or unscored are never
  patterns: they describe missing data, not you.

Rejection notes are sorted into templates ("other candidates", "no reply 14+
days") and specific reasons. Only specific reasons are quoted: a template
says nothing about why.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any, Iterable

MIN_SAMPLE = 5
STAGE_SAMPLE = 3
UNKNOWN = ("unknown", "unscored")
INSTANT_DAYS = 1    # rejected within a day of applying: likely an automatic filter
STAGES = ("application", "screening", "interview", "final")
DIMENSIONS = ("stage", "tier", "channel", "level", "speed")

_TEMPLATE = re.compile(
    r"no reply|no response|silent|closed as|standard template|generic|template|"
    r"(other|several) (candidates|profiles)|closer match|more closely|current needs|"
    r"not (to )?(take|move|proceed)|decided not|no specific reason|unfortunately|"
    r"not moving forward|other applicants", re.I)

_LEVELS = (("head", r"\bhead of\b|\bvp\b|vice president|\bcpo\b|chief"),
           ("director", r"\bdirector\b"),
           ("lead/principal", r"\blead\b|\bprincipal\b|\bstaff\b|\bgroup\b"),
           ("senior", r"\bsenior\b|\bsr\.?\b"),
           ("pm", r"product (manager|owner)|\bpm\b"))


def level_of(position: str) -> str:
    p = (position or "").lower()
    if not p or re.match(r"application\b", p):   # imported from an email, no title
        return "unknown"
    for name, rx in _LEVELS:
        if re.search(rx, p):
            return name
    return "other"


def _date(s: str) -> date | None:
    try:
        return date.fromisoformat((s or "")[:10])
    except ValueError:
        return None


def speed_of(role: dict[str, Any]) -> str:
    a, r = _date(role.get("date_applied", "")), _date(role.get("date_rejected", ""))
    if not a or not r:
        return "unknown"
    days = (r - a).days
    if days <= INSTANT_DAYS:
        return "instant (≤1 day)"
    return "within 2 weeks" if days <= 14 else "after 2 weeks"


def is_template(note: str) -> bool:
    return not note.strip() or bool(_TEMPLATE.search(note))


def _key(role: dict[str, Any], dim: str) -> str:
    if dim == "stage":
        return role.get("rejection_stage") or "application"
    if dim == "tier":
        return role.get("predicted_tier") or role.get("tier") or "unscored"
    if dim == "channel":
        return role.get("channel") or "unknown"
    if dim == "level":
        return level_of(role.get("position", ""))
    return speed_of(role)


def _applied(role: dict[str, Any]) -> bool:
    return role.get("status") in ("applied", "interviewing", "offer", "rejected") or bool(role.get("date_applied"))


def replied(role: dict[str, Any]) -> bool:
    """Got past the application stage: a screen or further."""
    if role.get("status") in ("interviewing", "offer"):
        return True
    return any((role.get(k) or "application") != "application" for k in ("rejection_stage", "max_stage"))


def analyse(roles: Iterable[dict[str, Any]], since: date | None = None) -> dict[str, Any]:
    roles = [r for r in roles if _applied(r)]
    if since:
        roles = [r for r in roles if (_date(r.get("date_applied", "")) or date.min) >= since]
    rejected = [r for r in roles if r.get("status") == "rejected"]
    overall = sum(map(replied, roles)) / len(roles) if roles else 0.0
    out: dict[str, Any] = {"applied": len(roles), "rejected": len(rejected), "replied": sum(map(replied, roles)),
                           "reply_rate": round(overall, 3), "min_sample": MIN_SAMPLE,
                           "stage_sample": STAGE_SAMPLE, "dimensions": {}, "patterns": [],
                           "specific_reasons": [], "template_notes": 0, "data_gaps": []}
    for dim in DIMENSIONS:
        groups: dict[str, list[dict[str, Any]]] = {}
        for r in (rejected if dim in ("stage", "speed") else roles):
            groups.setdefault(_key(r, dim), []).append(r)
        rows = []
        for k, rs in sorted(groups.items(), key=lambda kv: (-len(kv[1]), kv[0])):
            if dim in ("stage", "speed"):
                row = {"group": k, "rejected": len(rs)}
                row["pattern"] = ("repeated" if dim == "stage" and k != "application"
                                  and len(rs) >= STAGE_SAMPLE else None)
                row["small_sample"] = len(rs) < (STAGE_SAMPLE if dim == "stage" else MIN_SAMPLE)
            else:
                rep = sum(map(replied, rs))
                rate = rep / len(rs)
                row = {"group": k, "applied": len(rs), "replied": rep,
                       "rejected": sum(r.get("status") == "rejected" for r in rs),
                       "reply_rate": round(rate, 3), "small_sample": len(rs) < MIN_SAMPLE, "pattern": None}
                if not row["small_sample"] and k not in UNKNOWN and overall > 0:
                    # "low" needs enough applications that 2+ replies were expected,
                    # or 0 of 5 at a 9% overall rate would look like a finding.
                    if rate <= overall / 2 and len(rs) * overall >= 2:
                        row["pattern"] = "low"
                    elif rate >= overall * 2 and rep >= 2:
                        row["pattern"] = "high"
            if dim == "speed" and k.startswith("instant") and len(rs) >= STAGE_SAMPLE:
                row["pattern"] = "instant"
            rows.append(row)
            if row["pattern"]:
                out["patterns"].append({"dimension": dim, **row})
        out["dimensions"][dim] = rows
        unknown = sum(r.get("applied", r.get("rejected", 0)) for r in rows if r["group"] in UNKNOWN)
        base = len(rejected) if dim in ("stage", "speed") else len(roles)
        if base and unknown / base > 0.5:
            out["data_gaps"].append({"dimension": dim, "unknown": unknown, "of": base})
    for r in rejected:
        note = (r.get("rejection_note") or "").strip()
        if is_template(note):
            out["template_notes"] += bool(note)
        else:
            out["specific_reasons"].append({"note": note, "stage": _key(r, "stage"),
                                            "position": r.get("position", "")})
    return out


def _pct(x: float) -> str:
    return f"{round(100 * x)}%"


_LABEL = {"repeated": "repeated stage", "low": "low reply rate", "high": "high reply rate",
          "instant": "instant rejections — likely an automatic filter"}


def render(res: dict[str, Any]) -> str:
    if not res["rejected"]:
        return f"No rejections yet ({res['applied']} applications)."
    lines = [f"Rejections: {res['rejected']} of {res['applied']} applications. "
             f"{res['replied']} got a reply past the application ({_pct(res['reply_rate'])}).", ""]
    names = {"stage": "By stage reached", "tier": "By predicted tier", "channel": "By channel",
             "level": "By role level", "speed": "By time to rejection"}
    for dim in DIMENSIONS:
        lines.append(f"{names[dim]}:")
        for row in res["dimensions"][dim]:
            mark = f"  ← {_LABEL[row['pattern']]}" if row["pattern"] else (
                "  (small sample)" if row["small_sample"] else "")
            if "applied" in row:
                rate = "" if row["small_sample"] else f" ({_pct(row['reply_rate'])})"
                lines.append(f"  {row['group']}: {row['replied']} {'reply' if row['replied'] == 1 else 'replies'} of {row['applied']} applied{rate}{mark}")
            else:
                lines.append(f"  {row['group']}: {row['rejected']} rejected{mark}")
        lines.append("")
    pats = res["patterns"]
    lines.append(f"Patterns: {len(pats)}" + ("" if pats else
                 f" — nothing clears the bar ({res['stage_sample']}+ rejections at one stage past the "
                 f"application, or {res['min_sample']}+ applications with a reply rate half or double "
                 "the overall)."))
    for g in res["data_gaps"]:
        lines.append(f"Data gap: {g['dimension']} unknown for {g['unknown']} of {g['of']} — "
                     "not enough to read a pattern there.")
    lines.append(f"Reasons: {len(res['specific_reasons'])} specific, {res['template_notes']} template "
                 "(templates aren't quoted — they say nothing about why).")
    for s in res["specific_reasons"]:
        lines.append(f'  - [{s["stage"]}] "{s["note"]}"')
    return "\n".join(lines).rstrip()


_FIELDS = ("status", "channel", "date_applied", "date_rejected", "rejection_stage", "rejection_note",
           "tier", "predicted_tier", "position", "max_stage")


def _field(text: str, key: str) -> str:
    m = re.search(rf"^{key}:\s*\"?([^\"\n#]*?)\"?\s*(#.*)?$", text, re.M)
    return m.group(1).strip() if m else ""


def read_roles(userdata: Path) -> list[dict[str, str]]:
    companies = userdata / "companies"
    metas = sorted(set(companies.glob("*/meta.md")) | set(companies.glob("*/*/meta.md")))
    out = []
    for path in metas:
        text = path.read_text(encoding="utf-8")
        head = text.split("\n---", 2)[0] if text.startswith("---") else ""
        out.append({k: _field(head, k) for k in _FIELDS})
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--userdata", required=True, type=Path)
    ap.add_argument("--since", type=date.fromisoformat, help="only applications on or after this date")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    if not (a.userdata / "companies").is_dir():
        print(f"No companies folder under {a.userdata}", file=sys.stderr)
        return 2
    res = analyse(read_roles(a.userdata), a.since)
    print(json.dumps(res, ensure_ascii=False, indent=2) if a.json else render(res))
    return 0


if __name__ == "__main__":
    sys.exit(main())
