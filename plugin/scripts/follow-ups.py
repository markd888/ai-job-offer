#!/usr/bin/env python3
"""List applications that have gone quiet and are due a follow-up.

A role is due when it is `applied` (or `interviewing` with no upcoming event),
has had no news for --days (default 10) since the latest of date_applied,
last_inbound and last_follow_up, and has had fewer than two follow-ups. Past
--close-after days (default 30, the same rule the history import uses for
silence) it is listed under "close instead": a third nudge doesn't help, a
clean pipeline does. Roles whose company is unknown (imported from an ATS email
with no name) go there too: there is no one to write to.

Usage:
  python3 -I follow-ups.py [--userdata ./userdata] [--days 10] [--close-after 30] [--company NAME]

Read-only: it never writes files. /follow-up drafts the message and records
`follow_ups` and `last_follow_up` in meta.md once the user says it was sent.
"""
from __future__ import annotations

import argparse
import re
from datetime import date
from pathlib import Path

MAX_FOLLOW_UPS = 2


def field(meta: str, key: str) -> str:
    m = re.search(rf"^{key}:\s*\"?([^\"\n]*)\"?\s*$", meta, re.M)
    return m.group(1).strip() if m else ""


def as_date(s: str) -> date | None:
    try:
        return date.fromisoformat(s[:10])
    except ValueError:
        return None


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--userdata", type=Path, default=Path("userdata"))
    ap.add_argument("--days", type=int, default=10)
    ap.add_argument("--close-after", type=int, default=30)
    ap.add_argument("--company", default="")
    ap.add_argument("--today", default=date.today().isoformat())
    a = ap.parse_args()
    root = a.userdata.resolve() / "companies"
    today = date.fromisoformat(a.today)

    due, close = [], []
    for meta_path in sorted(root.glob("*/meta.md")) + sorted(root.glob("*/*/meta.md")):
        meta = meta_path.read_text()
        status = field(meta, "status")
        if status not in ("applied", "interviewing"):
            continue
        if status == "interviewing" and field(meta, "next_event"):
            continue
        company = field(meta, "company")
        if a.company and a.company.lower() not in company.lower():
            continue
        dates = [d for d in (as_date(field(meta, k)) for k in ("date_applied", "last_inbound", "last_follow_up")) if d]
        if not dates:
            continue
        quiet = (today - max(dates)).days
        try:
            sent = int(field(meta, "follow_ups") or 0)
        except ValueError:  # hand-edited junk ("one", "2?") counts as none sent
            sent = 0
        if quiet < a.days:
            continue
        archived = any(meta_path.parent.glob("submitted-*/manifest.md"))
        row = (quiet, company, field(meta, "position"), status, sent, archived,
               str(meta_path.parent.relative_to(root.parent.parent)), field(meta, "link"))
        if quiet > a.close_after or sent >= MAX_FOLLOW_UPS or company.lower().startswith("unknown"):
            close.append(row)
        else:
            due.append(row)

    def show(title: str, rows: list) -> None:
        print(f"## {title} ({len(rows)})")
        # Most recent first (least quiet), as /follow-up shows them; ties by company.
        for q, co, pos, st, sent, arch, folder, link in sorted(rows, key=lambda r: (r[0], r[1].lower())):
            print(f"- {co} — {pos} — {st}, quiet {q}d, follow-ups {sent}/{MAX_FOLLOW_UPS}, "
                  f"{'archive' if arch else 'no archive'} — {folder} — {link or '—'}")
        print()

    show(f"Follow-up due (quiet ≥ {a.days}d)", due)
    show(f"Close instead (quiet > {a.close_after}d, {MAX_FOLLOW_UPS} follow-ups sent, or company unknown)", close)


if __name__ == "__main__":
    main()
