#!/usr/bin/env python3
"""Funnel by application channel: which way of applying actually gets replies.

Shared by the dashboard (serve.py exposes funnel_by_channel in /api/state),
career-coach and /today's weekly reflection, so all three quote the same
numbers.

Usage:
  python3 -I funnel.py --userdata ./userdata [--json]

A role counts once it was applied to; how far it got is the deeper of
max_stage and rejection_stage (status interviewing means at least screening,
offer means offer). The logic matches stageReached() in
plugin/dashboard/src/components/funnel.ts — change both together.

Channels come from meta.md's `channel`, written by /sent. A role with no
channel, or one outside the enum, is counted as `unknown`. A channel with
fewer than MIN_SAMPLE applications is marked small_sample: show its counts,
not its rates.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable

CHANNELS = ("referral", "cold", "recruiter", "linkedin", "company-site", "other")
STAGES = ("applied", "screening", "interview", "final", "offer")
MIN_SAMPLE = 5
_DEPTH = {"application": 0, "screening": 1, "interview": 2, "final": 3}


def stage_reached(role: dict[str, Any]) -> str | None:
    """Deepest stage a role reached, or None if it was never applied to."""
    status = role.get("status") or ""
    if status == "offer":
        return "offer"
    if status == "interviewing":
        return ("screening", "screening", "interview", "final")[_DEPTH.get(role.get("max_stage") or "screening", 1)]
    deepest = max(_DEPTH.get(role.get("rejection_stage") or "application", 0),
                  _DEPTH.get(role.get("max_stage") or "application", 0))
    applied = status in ("applied", "rejected") or bool(role.get("date_applied")) or deepest >= 1
    if not applied:
        return None
    return ("applied", "screening", "interview", "final")[deepest]


def channel_of(role: dict[str, Any]) -> str:
    ch = (role.get("channel") or "").strip()
    return ch if ch in CHANNELS else "unknown"


def funnel_by_channel(roles: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Counts per channel of roles that reached each stage, and rates from applied.

    Rates are fractions of that channel's applications (None for a small sample).
    Rows are sorted by applications, most first; `unknown` always last."""
    counts: dict[str, list[int]] = {}
    for role in roles:
        stage = stage_reached(role)
        if stage is None:
            continue
        row = counts.setdefault(channel_of(role), [0] * len(STAGES))
        for i in range(STAGES.index(stage) + 1):
            row[i] += 1

    rows = []
    for ch, c in counts.items():
        applied = c[0]
        small = applied < MIN_SAMPLE
        row: dict[str, Any] = {"channel": ch, **dict(zip(STAGES, c)), "small_sample": small}
        for stage in STAGES[1:]:
            row[f"{stage}_rate"] = None if small else round(row[stage] / applied, 3)
        rows.append(row)
    rows.sort(key=lambda r: (r["channel"] == "unknown", -r["applied"], r["channel"]))
    return {"min_sample": MIN_SAMPLE, "rows": rows}


# ----- reading userdata ------------------------------------------------------

_FIELDS = ("status", "channel", "date_applied", "max_stage", "rejection_stage")


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


def _pct(x: float | None) -> str:
    return "" if x is None else f" ({round(x * 100)}%)"


def render(result: dict[str, Any]) -> str:
    rows = result["rows"]
    if not rows:
        return "No applications yet, so no funnel by channel."
    lines = ["Funnel by channel — of the roles applied to through each channel, how many reached each stage:"]
    for r in rows:
        if r["channel"] == "unknown":
            lines.append(f"- unknown (channel not recorded): {r['applied']} applied, "
                         f"{r['screening']} screening, {r['interview']} interview, {r['offer']} offer")
            continue
        steps = ", ".join(f"{r[s]} {s}{_pct(r[f'{s}_rate'])}" for s in STAGES[1:])
        note = f" — under {result['min_sample']} applications, too few for a rate" if r["small_sample"] else ""
        lines.append(f"- {r['channel']}: {r['applied']} applied → {steps}{note}")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--userdata", type=Path, default=Path("userdata"))
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    if not (a.userdata / "companies").is_dir():
        sys.exit(f"No companies/ under {a.userdata}")
    result = funnel_by_channel(read_roles(a.userdata))
    print(json.dumps(result, indent=2) if a.json else render(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
