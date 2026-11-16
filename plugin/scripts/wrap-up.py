#!/usr/bin/env python3
"""Close a search that ended in an accepted offer (/wrap-up), or reopen it.

Every write here runs only after the user's yes in chat; the script is the
write, not the question. Nothing is ever sent.

Usage:
  python3 -I wrap-up.py open     --userdata U --offer <role>
  python3 -I wrap-up.py withdraw --userdata U --role <role> [--role <role> ...] [--date D]
  python3 -I wrap-up.py facts    --userdata U --offer <role> [--date D]
  python3 -I wrap-up.py close    --userdata U --offer <role> [--market-check quarterly|off] [--date D]
  python3 -I wrap-up.py reopen   --userdata U [--date D]

<role> is a folder under userdata/companies/ (Lendable, or Plaid/senior-pm-consumer-credit).

open      — what's still in flight besides the accepted offer: roles to
            withdraw from (applied, interviewing, offer), roles to drop
            (new, to_apply), and people to thank (referrals, intros, anyone
            linked to the accepted role).
withdraw  — status: not_interested with date_not_interested and a History
            line, for roles the user withdrew from.
facts     — the numbers for the retrospective, as markdown: dates and time to
            offer, the funnel overall and by channel, where rejections
            clustered (with the recruiters' notes), outreach.
close     — strategy.md gets search_state: dormant, search_closed,
            accepted_offer and market_check; the offer role gets a History
            line. /today, /job-search and the dashboard go quiet.
reopen    — search_state: active again, with search_reopened.
"""
from __future__ import annotations

import argparse
import importlib.util
import re
import sys
from collections import Counter
from datetime import date
from pathlib import Path


def _load(name: str):
    path = Path(__file__).resolve().parent / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


mf = _load("metafile")
people = _load("people")
funnel = _load("funnel")

WITHDRAW = ("applied", "interviewing", "offer")
DROP = ("new", "to_apply")
SEARCH_STATES = ("active", "dormant")
MARKET_CHECK = ("quarterly", "off")


def roles(userdata: Path) -> list[tuple[str, str]]:
    """(role path relative to companies/, meta.md text) for every role."""
    companies = userdata / "companies"
    metas = sorted(set(companies.glob("*/meta.md")) | set(companies.glob("*/*/meta.md")))
    return [(p.parent.relative_to(companies).as_posix(), p.read_text(encoding="utf-8")) for p in metas]


def _role_meta(userdata: Path, role: str) -> Path:
    p = userdata / "companies" / role / "meta.md"
    if not p.is_file():
        raise SystemExit(f"No role folder companies/{role}/ with a meta.md")
    return p


def _label(meta: str, role: str) -> str:
    return f"{mf.field(meta, 'company') or role.split('/')[0]} — {mf.field(meta, 'position')}"


def _history_date(meta: str, status: str) -> str:
    m = re.findall(rf"^-?\s*(\d{{4}}-\d{{2}}-\d{{2}}):?\s*status\s*→\s*{status}\b", meta, re.M)
    return m[-1] if m else ""


# ----- open ------------------------------------------------------------------


def cmd_open(userdata: Path, offer: str) -> str:
    _role_meta(userdata, offer)
    withdraw, drop = [], []
    for role, meta in roles(userdata):
        if role == offer:
            continue
        status = mf.field(meta, "status")
        line = f"- {role} | {_label(meta, role)} | {status}"
        if status in WITHDRAW:
            nxt = mf.field(meta, "next_event")
            withdraw.append(line + (f" | next: {nxt}" if nxt else ""))
        elif status in DROP:
            drop.append(line)

    thank = []
    for path in people.person_files(userdata):
        text = path.read_text(encoding="utf-8")
        fm = people.frontmatter(text)
        entries, _ = people.parse_log(text)
        helped = [e for e in entries if e["direction"] == "received" and e["kind"] in ("referral", "intro")]
        linked = offer in people.roles_of(fm)
        thanked = any(e["direction"] == "sent" and e["kind"] == "thank-you" for e in entries)
        if helped or linked:
            why = ", ".join(sorted({e["kind"] for e in helped})) or "linked to the accepted role"
            thank.append(f"- {fm.get('name', path.stem)} ({path.name}) | {why}"
                         + (" | already thanked once" if thanked else ""))

    out = ["## Withdraw (still in process)", *(withdraw or ["- none"]),
           "", "## Drop (never applied)", *(drop or ["- none"]),
           "", "## Thank", *(thank or ["- nobody on file"])]
    return "\n".join(out)


# ----- withdraw --------------------------------------------------------------


def cmd_withdraw(userdata: Path, role_list: list[str], day: str) -> str:
    paths = [(r, _role_meta(userdata, r)) for r in role_list]
    for r, p in paths:  # check all before writing any
        status = mf.field(p.read_text(encoding="utf-8"), "status")
        if status not in WITHDRAW + DROP:
            raise SystemExit(f"{r} is '{status}' — nothing to withdraw; no role was changed")
    done = []
    for r, p in paths:
        meta = p.read_text(encoding="utf-8")
        before = mf.field(meta, "status")
        meta = mf.set_fields(meta, {"status": "not_interested", "date_not_interested": day,
                                    "last_activity": mf.later(mf.field(meta, "last_activity"), day)})
        why = "withdrew — accepted another offer" if before in WITHDRAW else "dropped — search closed"
        p.write_text(mf.append_history(meta, f"- {day}: status → not_interested ({why})"))
        done.append(r)
    return f"Marked {len(done)} role(s) not_interested: " + ", ".join(done)


# ----- facts -----------------------------------------------------------------


def _days(a: str, b: str) -> int | None:
    try:
        return (date.fromisoformat(b) - date.fromisoformat(a)).days
    except ValueError:
        return None


def cmd_facts(userdata: Path, offer: str, day: str) -> str:
    offer_meta = _role_meta(userdata, offer).read_text(encoding="utf-8")
    all_roles = roles(userdata)
    fields = [{k: mf.field(m, k) for k in ("status", "channel", "date_added", "date_applied", "max_stage",
                                           "rejection_stage", "rejection_note")} for _, m in all_roles]

    applied_dates = sorted(f["date_applied"] for f in fields if f["date_applied"])
    added_dates = sorted(f["date_added"] for f in fields if f["date_added"])
    start = applied_dates[0] if applied_dates else (added_dates[0] if added_dates else "")
    offer_day = _history_date(offer_meta, "offer")
    lines = ["## Numbers", ""]
    lines.append(f"- Accepted: {_label(offer_meta, offer)} (applied {mf.field(offer_meta, 'date_applied') or '—'}"
                 f", channel {mf.field(offer_meta, 'channel') or 'not recorded'}"
                 + (f", referred by {mf.field(offer_meta, 'referred_by').strip('[]')}" if mf.field(offer_meta, 'referred_by') else "")
                 + ")")
    if start:
        d_offer = _days(start, offer_day) if offer_day else None
        lines.append(f"- First application {start}; offer {offer_day or 'date not in History'}; closed {day}"
                     + (f" — {d_offer} days from first application to offer" if d_offer is not None else "")
                     + f", {_days(start, day)} days in all.")
    lines.append(f"- Roles tracked: {len(all_roles)}; "
                 + ", ".join(f"{n} {s}" for s, n in Counter(f["status"] for f in fields).most_common()) + ".")

    reached = [funnel.stage_reached(f) for f in fields]
    counts = [sum(1 for r in reached if r and funnel.STAGES.index(r) >= i) for i in range(len(funnel.STAGES))]
    lines.append("- Funnel: " + " → ".join(f"{n} {s}" for s, n in zip(funnel.STAGES, counts)) + ".")
    lines += ["", funnel.render(funnel.funnel_by_channel(fields))]

    rejected = [f for f in fields if f["status"] == "rejected"]
    lines += ["", "## Where it stopped", ""]
    if rejected:
        by_stage = Counter(f["rejection_stage"] or "not recorded" for f in rejected)
        lines.append("- Rejections by stage: " + ", ".join(f"{s} {n}" for s, n in by_stage.most_common()) + ".")
        notes = [(r, mf.field(m, "rejection_note"), mf.field(m, "rejection_stage"))
                 for r, m in all_roles if mf.field(m, "status") == "rejected" and mf.field(m, "rejection_note")]
        for r, note, stage in notes:
            lines.append(f"- {r} ({stage or 'stage not recorded'}): \"{note}\"")
    else:
        lines.append("- No rejections recorded.")

    sent = received = 0
    for path in people.person_files(userdata):
        entries, _ = people.parse_log(path.read_text(encoding="utf-8"))
        sent += sum(1 for e in entries if e["direction"] == "sent" and e["kind"] in people.OUTREACH_KINDS)
        received += sum(1 for e in entries if e["direction"] == "received" and e["kind"] in ("referral", "intro"))
    lines += ["", "## Outreach", "", f"- {sent} outreach message(s) logged; {received} referral(s) or intro(s) received."]
    return "\n".join(lines)


# ----- close / reopen --------------------------------------------------------


def _strategy(userdata: Path) -> Path:
    p = userdata / "strategy.md"
    if not p.is_file():
        raise SystemExit("No userdata/strategy.md — nothing to mark")
    return p


def cmd_close(userdata: Path, offer: str, market_check: str, day: str) -> str:
    offer_path = _role_meta(userdata, offer)
    offer_meta = offer_path.read_text(encoding="utf-8")
    if mf.field(offer_meta, "status") != "offer":
        raise SystemExit(f"{offer} is '{mf.field(offer_meta, 'status')}', not 'offer' — record the offer first")
    sp = _strategy(userdata)
    label = _label(offer_meta, offer).replace('"', "'")
    sp.write_text(mf.set_fields(sp.read_text(encoding="utf-8"), {
        "search_state": "dormant", "search_closed": day,
        "accepted_offer": f'"{label}"', "market_check": market_check}))
    offer_path.write_text(mf.append_history(offer_meta, f"- {day}: offer accepted; search closed"))
    return f"Search closed {day}: accepted {label}; market check {market_check}."


def cmd_reopen(userdata: Path, day: str) -> str:
    sp = _strategy(userdata)
    text = sp.read_text(encoding="utf-8")
    if mf.field(text, "search_state") != "dormant":
        raise SystemExit("The search isn't closed — nothing to reopen")
    sp.write_text(mf.set_fields(text, {"search_state": "active", "search_reopened": day}))
    return f"Search reopened {day}."


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("open", "withdraw", "facts", "close", "reopen"):
        p = sub.add_parser(name)
        p.add_argument("--userdata", type=Path, default=Path("userdata"))
        p.add_argument("--date", default=date.today().isoformat())
        if name in ("open", "facts", "close"):
            p.add_argument("--offer", required=True, help="the accepted role, e.g. Lendable")
        if name == "withdraw":
            p.add_argument("--role", action="append", required=True)
        if name == "close":
            p.add_argument("--market-check", choices=MARKET_CHECK, default="off")
    a = ap.parse_args()
    try:
        date.fromisoformat(a.date)
    except ValueError:
        sys.exit(f"--date {a.date!r} is not YYYY-MM-DD")
    u = a.userdata.resolve()
    out = {
        "open": lambda: cmd_open(u, a.offer),
        "withdraw": lambda: cmd_withdraw(u, a.role, a.date),
        "facts": lambda: cmd_facts(u, a.offer, a.date),
        "close": lambda: cmd_close(u, a.offer, a.market_check, a.date),
        "reopen": lambda: cmd_reopen(u, a.date),
    }[a.cmd]()
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
