#!/usr/bin/env python3
"""Freeze exactly what was sent for one application.

Copies the CV (PDF + markdown), any cover letter or cover note, the latest ATS
check, and the posting text into <role-dir>/submitted-<date>/, writes a
manifest with file hashes, and appends one line to the role's ## History.
Interview prep and follow-ups then work from what the employer actually read,
not from whatever the CV became later.

Usage:
  python3 -I archive-application.py <role-dir> [--posting posting.md]
      [--channel "company site"] [--date YYYY-MM-DD] [--force]

<role-dir> is the folder holding the role's meta.md. --posting is a file with
the posting text (Claude saves it from the fetched job description). Without it,
the manifest records the link and says the text wasn't captured. Status and
date_applied are left to the skills that own them.
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


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("role_dir", type=Path)
    ap.add_argument("--posting", type=Path, help="file with the posting text")
    ap.add_argument("--channel", default="", help='how it was sent, e.g. "company site", "LinkedIn", "referral"')
    ap.add_argument("--date", default=date.today().isoformat())
    ap.add_argument("--force", action="store_true", help="replace an existing archive for this date")
    a = ap.parse_args()

    role = a.role_dir
    meta_path = role / "meta.md"
    if not meta_path.is_file():
        sys.exit(f"No meta.md in {role}")
    meta = meta_path.read_text()
    out = role / f"submitted-{a.date}"
    if out.exists() and not a.force:
        sys.exit(f"{out.name} already exists; pass --force to replace it")

    picks = {
        "CV (PDF)": latest(role, "*CV*.pdf"),
        "CV (markdown)": latest(role, "cv-*.md"),
        "Cover letter (PDF)": latest(role, "*[Cc]over*.pdf"),
        "Cover letter / note": latest(role, "cover-*.md"),
        "ATS check": latest(role, "ats-check-*.md"),
    }
    if not picks["CV (PDF)"] and not picks["CV (markdown)"]:
        sys.exit(f"No CV found in {role}; build it first")

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
    if a.posting and a.posting.is_file():
        body = a.posting.read_text()
        (out / "posting.md").write_text(f"<!-- captured {a.date} from {link or 'pasted text'} -->\n\n{body}")
        rows.append(f"| Posting | `posting.md` | {sha(out / 'posting.md')} |")
    else:
        posting_note = "\nPosting text was not captured; only the link is recorded.\n"

    manifest = [
        f"# Submitted — {field(meta, 'company')}, {field(meta, 'position')}",
        "",
        f"- Date: {a.date}",
        f"- Link: {link or '—'}",
        f"- Channel: {a.channel or '—'}",
        "",
        "| What | File | sha256 |",
        "|---|---|---|",
        *rows,
        posting_note,
    ]
    (out / "manifest.md").write_text("\n".join(manifest).rstrip() + "\n")

    line = f"- {a.date}: submitted materials archived in {out.name}/" + (f" ({a.channel})" if a.channel else "")
    if "## History" in meta:
        meta = meta.rstrip("\n") + "\n" + line + "\n"
    else:
        meta = meta.rstrip("\n") + "\n\n## History\n" + line + "\n"
    meta_path.write_text(meta)

    print(f"Archived {len(rows)} file(s) to {out}")
    for r in rows:
        print("  " + r.split("|")[2].strip())
    if posting_note:
        print("  posting text not captured — pass --posting to keep it")
    return 0


if __name__ == "__main__":
    sys.exit(main())
