#!/usr/bin/env python3
"""Record that a company got in touch: sets last_inbound, logs it in History.

A reply, a scheduling email, a call or an interview all count. last_inbound
restarts the quiet clock that follow-ups.py and /today's quiet-application
rule share, so a company that wrote back three days ago isn't chased. Run it
only for contact the user confirmed or told you about.

Usage:
  python3 -I record-inbound.py <role-dir> --what "reply from Dana (recruiter)"
      [--date YYYY-MM-DD] [--source user|gmail|calendar|granola|interview]

last_inbound and last_activity only ever move forward: logging an older
contact adds the History line but keeps the later dates. Status is never
changed here; a rejection or an offer is still the user's call in /today.
"""
from __future__ import annotations

import argparse
import importlib.util
import sys
from datetime import date
from pathlib import Path

SOURCES = ("user", "gmail", "calendar", "granola", "interview")


def load_metafile():
    path = Path(__file__).resolve().parent / "metafile.py"
    spec = importlib.util.spec_from_file_location("metafile", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("role_dir", type=Path)
    ap.add_argument("--what", required=True, help='what came in, e.g. "reply from Dana (recruiter)"')
    ap.add_argument("--date", default=date.today().isoformat())
    ap.add_argument("--source", default="user", choices=SOURCES)
    a = ap.parse_args()

    try:
        date.fromisoformat(a.date)
    except ValueError:
        sys.exit(f"--date {a.date!r} is not YYYY-MM-DD")
    mf = load_metafile()
    meta_path = mf.role_meta(a.role_dir)
    meta = meta_path.read_text()

    before = mf.field(meta, "last_inbound")
    inbound = mf.later(before, a.date)
    activity = mf.later(mf.field(meta, "last_activity"), a.date)
    meta = mf.set_fields(meta, {"last_inbound": inbound, "last_activity": activity})
    what = " ".join(a.what.split())
    meta = mf.append_history(meta, f"- {a.date}: inbound — {what} ({a.source})")
    meta_path.write_text(meta)

    if inbound == a.date:
        print(f"Recorded: last contact from {mf.field(meta, 'company') or 'the company'} on {a.date}")
    else:
        print(f"Logged the {a.date} contact; last_inbound stays {inbound}, which is later")
    return 0


if __name__ == "__main__":
    sys.exit(main())
