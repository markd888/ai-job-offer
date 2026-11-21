#!/usr/bin/env python3
"""Funnel by application channel: which way of applying actually gets replies.

Shared by the dashboard (serve.py exposes funnel_by_channel in /api/state),
career-coach and /today's weekly reflection, so all three quote the same
numbers.

Usage:
  python3 -I funnel.py --userdata ./userdata [--json]
  python3 -I funnel.py --userdata ./userdata --by-tier [--json]   predicted tier vs outcome

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


OUTCOMES = ("not_applied", "applied", "no_response", "hr_rejected", "hr_passed",
            "technical_rejected", "technical_passed", "final_round", "offer", "withdrawn")
PREDICTION_TIERS = ("P0", "P1", "P2")
MIN_PER_TIER = 5


def outcome(role: dict[str, Any]) -> str:
    """Application outcome derived from existing fields — never stored.

    Mapping (score.schema.md / #37): new|to_apply → not_applied; not_interested
    → withdrawn if it was applied to, else not_applied; offer → offer; a
    rejection at a stage → <stage>_rejected (application with no reply →
    no_response); otherwise the deepest stage reached."""
    status = role.get("status") or ""
    if status == "offer":
        return "offer"
    if status == "not_interested":
        return "withdrawn" if role.get("date_applied") else "not_applied"
    if status in ("new", "to_apply", ""):
        return "not_applied"
    if status == "rejected":
        rs = role.get("rejection_stage") or "application"
        if rs == "application":
            return "applied" if role.get("last_inbound") else "no_response"
        if rs == "screening":
            return "hr_rejected"
        if rs == "interview":
            return "technical_rejected"
        return "final_round"  # rejected at final
    reached = stage_reached(role)
    return {"screening": "hr_passed", "interview": "technical_passed",
            "final": "final_round"}.get(reached or "", "applied")


def prediction_of(role: dict[str, Any]) -> tuple[str, str]:
    """(tier, basis). v2 roles keep their first prediction in predicted_tier; a v1
    role only has its current tier, which a manual adjustment may have replaced."""
    if role.get("predicted_tier") in PREDICTION_TIERS:
        return role["predicted_tier"], "predicted"
    if role.get("tier") in PREDICTION_TIERS:
        return role["tier"], "v1_tier"
    return "unscored", "none"


def outcome_by_tier(roles: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Counts of derived outcomes per predicted tier. Counts only — no rates, no
    probabilities. Tiers with fewer than MIN_PER_TIER applied roles are marked
    too_few, so nobody reads a pattern into three data points."""
    rows: dict[str, dict[str, Any]] = {}
    for r in roles:
        tier, basis = prediction_of(r)
        row = rows.setdefault(tier, {"tier": tier, **{o: 0 for o in OUTCOMES}, "applied_total": 0,
                                     "v1_basis": 0})
        o = outcome(r)
        row[o] += 1
        if o not in ("not_applied",):
            row["applied_total"] += 1
        if basis == "v1_tier":
            row["v1_basis"] += 1
    order = {t: i for i, t in enumerate((*PREDICTION_TIERS, "unscored"))}
    out = sorted(rows.values(), key=lambda x: order[x["tier"]])
    for row in out:
        row["too_few"] = row["applied_total"] < MIN_PER_TIER
    return {"rows": out, "min_per_tier": MIN_PER_TIER}


def render_by_tier(result: dict[str, Any]) -> str:
    rows = [r for r in result["rows"] if r["applied_total"]]
    if not rows:
        return "No applications yet, so nothing to compare predictions with."
    lines = ["Predicted tier vs what happened (counts of roles applied to):"]
    for r in rows:
        parts = ", ".join(f"{r[o]} {o.replace('_', ' ')}" for o in OUTCOMES[1:] if r[o])
        note = f" — under {result['min_per_tier']} applications, too few to conclude" if r["too_few"] else ""
        v1 = f" ({r['v1_basis']} scored before v2)" if r["v1_basis"] else ""
        lines.append(f"- {r['tier']}: {r['applied_total']} applied{v1} → {parts}{note}")
    return "\n".join(lines)


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

_FIELDS = ("status", "channel", "date_applied", "max_stage", "rejection_stage",
           "last_inbound", "tier", "predicted_tier")


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
    ap.add_argument("--by-tier", action="store_true", help="predicted tier vs derived outcome")
    a = ap.parse_args()
    if not (a.userdata / "companies").is_dir():
        sys.exit(f"No companies/ under {a.userdata}")
    roles = read_roles(a.userdata)
    if a.by_tier:
        result = outcome_by_tier(roles)
        print(json.dumps(result, indent=2) if a.json else render_by_tier(result))
        return 0
    result = funnel_by_channel(roles)
    print(json.dumps(result, indent=2) if a.json else render(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
