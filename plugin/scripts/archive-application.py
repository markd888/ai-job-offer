#!/usr/bin/env python3
"""Freeze exactly what was sent for one application.

Copies the CV (PDF + markdown), any cover letter or cover note, the latest ATS
check, and the posting text into <role-dir>/submitted-<date>/, writes a
manifest with file hashes, and appends one line to the role's ## History.
Interview prep and follow-ups then work from what the employer actually read,
not from whatever the CV became later.

Usage:
  python3 -I archive-application.py <role-dir> [--posting posting.md]
      [--channel company-site] [--date YYYY-MM-DD] [--force] [--no-history]

<role-dir> is the folder holding the role's meta.md. --posting is a file with
the posting text (Claude saves it from the fetched job description). Without it,
the manifest records the link and says the text wasn't captured. Status,
date_applied and channel are written by record-sent.py (/sent), which calls
archive() and writes one History line for both; --no-history skips this
script's own line.
"""
from __future__ import annotations

import argparse
import hashlib
import re
import shutil
import sys
from datetime import date
from pathlib import Path


def latest(folder: Path, pattern: str) -> Path | None:
    files = [p for p in folder.glob(pattern) if p.is_file()]
    return max(files, key=lambda p: (p.stat().st_mtime, p.name)) if files else None


def field(meta: str, key: str) -> str:
    m = re.search(rf"^{key}:\s*\"?([^\"\n]*)\"?\s*$", meta, re.M)
    return m.group(1).strip() if m else ""


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()[:12]


class ArchiveError(Exception):
    pass


def has_cv(role: Path) -> bool:
    return bool(latest(role, "*CV*.pdf") or latest(role, "cv-*.md"))


def archive(role: Path, posting: Path | None, channel: str, day: str, force: bool) -> tuple[Path, list[str], str]:
    """Copy what was sent into <role>/submitted-<day>/ and write its manifest.

    Returns (archive folder, manifest rows, note about the posting). Raises
    ArchiveError when there is no meta.md, no CV, or an archive for that day
    already exists and force is off. Never touches meta.md."""
    meta_path = role / "meta.md"
    if not meta_path.is_file():
        raise ArchiveError(f"No meta.md in {role}")
    meta = meta_path.read_text()
    out = role / f"submitted-{day}"
    if out.exists() and not force:
        raise ArchiveError(f"{out.name} already exists; pass --force to replace it")

    picks = {
        "CV (PDF)": latest(role, "*CV*.pdf"),
        "CV (markdown)": latest(role, "cv-*.md"),
        "Cover letter (PDF)": latest(role, "*[Cc]over*.pdf"),
        "Cover letter / note": latest(role, "cover-*.md"),
        "ATS check": latest(role, "ats-check-*.md"),
    }
    if not picks["CV (PDF)"] and not picks["CV (markdown)"]:
        raise ArchiveError(f"No CV found in {role}; build it first")

    if out.exists():
        shutil.rmtree(out)
    out.mkdir()
    rows = []
    for label, src in picks.items():
        if src:
            shutil.copy2(src, out / src.name)
            rows.append(f"| {label} | `{src.name}` | {sha(out / src.name)} |")

    link = field(meta, "link")
    posting_note = ""
    if posting and posting.is_file():
        body = posting.read_text()
        (out / "posting.md").write_text(f"<!-- captured {day} from {link or 'pasted text'} -->\n\n{body}")
        rows.append(f"| Posting | `posting.md` | {sha(out / 'posting.md')} |")
    else:
        posting_note = "\nPosting text was not captured; only the link is recorded.\n"

    manifest = [
        f"# Submitted — {field(meta, 'company')}, {field(meta, 'position')}",
        "",
        f"- Date: {day}",
        f"- Link: {link or '—'}",
        f"- Channel: {channel or '—'}",
        "",
        "| What | File | sha256 |",
        "|---|---|---|",
        *rows,
        posting_note,
    ]
    (out / "manifest.md").write_text("\n".join(manifest).rstrip() + "\n")
    return out, rows, posting_note


def append_history(meta_path: Path, line: str) -> None:
    meta = meta_path.read_text()
    if "## History" in meta:
        meta = meta.rstrip("\n") + "\n" + line + "\n"
    else:
        meta = meta.rstrip("\n") + "\n\n## History\n" + line + "\n"
    meta_path.write_text(meta)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("role_dir", type=Path)
    ap.add_argument("--posting", type=Path, help="file with the posting text")
    ap.add_argument("--channel", default="", help="how it was sent, e.g. company-site, linkedin, referral")
    ap.add_argument("--date", default=date.today().isoformat())
    ap.add_argument("--force", action="store_true", help="replace an existing archive for this date")
    ap.add_argument("--no-history", action="store_true", help="don't append a line to ## History")
    a = ap.parse_args()

    try:
        out, rows, posting_note = archive(a.role_dir, a.posting, a.channel, a.date, a.force)
    except ArchiveError as e:
        sys.exit(str(e))
    if not a.no_history:
        append_history(a.role_dir / "meta.md", f"- {a.date}: submitted materials archived in {out.name}/"
                       + (f" ({a.channel})" if a.channel else ""))

    print(f"Archived {len(rows)} file(s) to {out}")
    for r in rows:
        print("  " + r.split("|")[2].strip())
    if posting_note:
        print("  posting text not captured — pass --posting to keep it")
    return 0


if __name__ == "__main__":
    sys.exit(main())
