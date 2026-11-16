#!/usr/bin/env python3
"""Record an application going out, in one step (/sent).

Sets status: applied, date_applied, channel (and referred_by for a referral)
and last_activity in the role's meta.md, freezes what was sent with
archive-application.py's archive(), and appends one ## History line for both.
Run it only after the user has said yes: it is the write, not the question.

Usage:
  python3 -I record-sent.py <role-dir> --channel <channel>
      [--referred-by "Name"] [--posting posting.md] [--date YYYY-MM-DD]
      [--no-archive] [--force]

Channels: referral, cold, recruiter, linkedin, company-site, other.

It refuses, changing nothing, when the role is already recorded as applied
with a date, or is past the application (interviewing, offer, rejected,
not_interested), unless --force. With no CV in the role folder it records the
application anyway and says nothing was archived; --no-archive skips the
archive on purpose. follow-ups.py counts the quiet days from date_applied.
"""
from __future__ import annotations

import argparse
import importlib.util
import sys
from datetime import date
from pathlib import Path

CHANNELS = ("referral", "cold", "recruiter", "linkedin", "company-site", "other")
OPEN_STATUSES = ("new", "to_apply", "applied")


def _load_archiver():
    path = Path(__file__).resolve().parent / "archive-application.py"
    spec = importlib.util.spec_from_file_location("archive_application", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _load_metafile():
    path = Path(__file__).resolve().parent / "metafile.py"
    spec = importlib.util.spec_from_file_location("metafile", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("role_dir", type=Path)
    ap.add_argument("--channel", required=True, choices=CHANNELS)
    ap.add_argument("--referred-by", default="", help="the person who referred you, as their name")
    ap.add_argument("--posting", type=Path, help="file with the posting text, kept in the archive")
    ap.add_argument("--date", default=date.today().isoformat())
    ap.add_argument("--no-archive", action="store_true", help="record the application without archiving files")
    ap.add_argument("--force", action="store_true", help="record over an existing date or a later status")
    a = ap.parse_args()

    try:
        date.fromisoformat(a.date)
    except ValueError:
        sys.exit(f"--date {a.date!r} is not YYYY-MM-DD")
    mf = _load_metafile()
    role = a.role_dir
    meta_path = mf.role_meta(role)
    meta = meta_path.read_text()
    status, applied_on = mf.field(meta, "status"), mf.field(meta, "date_applied")
    if not a.force:
        if status not in OPEN_STATUSES:
            sys.exit(f"Status is '{status}', past the application; pass --force to record it anyway")
        if status == "applied" and applied_on:
            sys.exit(f"Already recorded as applied on {applied_on}; pass --force to record it again")

    archiver = _load_archiver()
    archived = None
    if not a.no_archive and archiver.has_cv(role):
        try:
            archived, rows, posting_note = archiver.archive(role, a.posting, a.channel, a.date, a.force)
        except archiver.ArchiveError as e:
            sys.exit(str(e))

    values = {"status": "applied", "date_applied": a.date, "channel": a.channel,
              "last_activity": mf.later(mf.field(meta, "last_activity"), a.date)}
    referred = a.referred_by.strip().strip("[]")
    if referred:
        values["referred_by"] = '"[[' + referred.replace('"', "'") + ']]"'
    meta = mf.set_fields(meta, values)

    line = f"- {a.date}: status → applied via {a.channel}"
    if referred:
        line += f" (referred by [[{referred}]])"
    if archived:
        line += f"; materials archived in {archived.name}/"
    elif not a.no_archive:
        line += "; no CV in the folder, nothing archived"
    meta_path.write_text(mf.append_history(meta, line))

    print(f"Recorded: applied {a.date} via {a.channel}" + (f", referred by {referred}" if referred else ""))
    if archived:
        print(f"Archived {len(rows)} file(s) to {archived}")
        if posting_note:
            print("  posting text not captured — pass --posting to keep it")
    elif not a.no_archive:
        print("No CV in the role folder, so nothing was archived")
    return 0


if __name__ == "__main__":
    sys.exit(main())
