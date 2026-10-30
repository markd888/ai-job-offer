#!/usr/bin/env python3
"""Check a CV PDF the way an applicant tracking system reads it.

An ATS parses the PDF's embedded text layer, not the rendered page. This script
extracts that layer and checks what a parser would choke on:

  pages      the CV is exactly one page
  contacts   email and phone come through as literal text
  glyphs     no (cid:N) codes, replacement characters, private-use icon glyphs
             or ligatures (ﬁ, ﬂ) that break keyword matching
  order      section headings appear in the same order as in the CV markdown
  fidelity   ≥ 95% of the words in the CV markdown survive extraction
  keywords   which of the posting's keywords the CV text covers (report only:
             a keyword the profile doesn't support stays a gap, never stuffed in)

Usage:
  python3 -I ats-check.py CV.pdf [--md cv.md] [--phone "+44 7700 900000"]
      [--keywords "payments orchestration, PSP integrations, SQL"]
      [--jd posting.md] [--out report.md]

--phone defaults to the `phone:` field of userdata/profile.md, found by walking
up from the PDF; without either, the contacts check looks for any phone number.

--keywords is the curated list Claude picks from the posting; --jd adds
frequent posting terms as suggestions. Exit code 1 when a hard check fails.
Text extraction uses pypdf, falling back to pdftotext (poppler).
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import unicodedata
from collections import Counter
from datetime import date
from pathlib import Path

EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
LIGATURES = "ﬀﬁﬂﬃﬄﬅﬆ"
DEFAULT_HEADINGS = ["PROFESSIONAL SUMMARY", "WORK EXPERIENCE", "PROFESSIONAL SKILLS", "EDUCATION"]
STOP = set("""a an and are as at be by for from has have in into is it its of on or our that the their this to
we will with you your who what when where which while within without across about over under per via than then
they them these those all any can more most other such not only also may must should would could role team work
working years year experience strong ability skills including new using help make based well both each own""".split())


def extract(pdf: Path) -> tuple[str, int, str]:
    try:
        from pypdf import PdfReader

        reader = PdfReader(str(pdf))
        return "\n".join(p.extract_text() or "" for p in reader.pages), len(reader.pages), "pypdf"
    except ImportError:
        pass
    if not shutil.which("pdftotext"):
        sys.exit("No text extractor: install pypdf (pip install pypdf) or poppler (pdftotext).")
    text = subprocess.run(["pdftotext", str(pdf), "-"], capture_output=True, text=True, check=True).stdout
    pages = text.count("\f") or 1
    if shutil.which("pdfinfo"):
        info = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout
        m = re.search(r"^Pages:\s+(\d+)", info, re.M)
        pages = int(m.group(1)) if m else pages
    return text, pages, "pdftotext"


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).lower()
    s = re.sub(r"[‐-―−]", "-", s)
    return re.sub(r"\s+", " ", s)


def words(s: str) -> list[str]:
    return re.findall(r"[a-zа-я0-9][a-zа-я0-9+#.\-]*[a-zа-я0-9+#]|[a-z0-9]", norm(s))


def md_plain(md: str) -> str:
    md = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", md)
    return re.sub(r"[*_`#>|]", " ", md)


def covered(term: str, text_n: str) -> bool:
    t = norm(term).strip()
    if not t:
        return True
    alts = {t, t.rstrip("s"), t + "s", t.replace("-", " "), t.replace(" ", "-")}
    return any(re.search(r"(?<![a-z0-9])" + re.escape(a) + r"(?![a-z0-9])", text_n) for a in alts if a)


def jd_terms(jd: str, limit: int = 25) -> list[str]:
    toks = [w for w in words(md_plain(jd)) if len(w) > 2 and w not in STOP and not w.isdigit()]
    grams = Counter(toks)
    grams.update(f"{a} {b}" for a, b in zip(toks, toks[1:]) if a not in STOP and b not in STOP)
    picked = [g for g, n in grams.most_common(200) if n >= 2]
    out: list[str] = []
    for g in picked:  # prefer a bigram over the single words inside it
        if " " not in g and any(g in o.split() for o in out):
            continue
        out.append(g)
    return out[:limit]


def profile_phone(start: Path) -> str:
    """The `phone:` field of the nearest userdata/profile.md above start (or in the cwd)."""
    for d in [start.resolve().parent, *start.resolve().parents, Path.cwd()]:
        for p in (d / "profile.md", d / "userdata" / "profile.md"):
            if p.is_file():
                m = re.search(r"^phone:\s*\"?([^\"#\n]*)", p.read_text(encoding="utf-8"), re.M)
                return m.group(1).strip() if m else ""
    return ""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pdf", type=Path)
    ap.add_argument("--md", type=Path, help="CV markdown the PDF was built from (order + fidelity checks)")
    ap.add_argument("--keywords", default="", help="comma-separated keywords picked from the posting")
    ap.add_argument("--jd", type=Path, help="posting text; frequent terms are reported as suggestions")
    ap.add_argument("--pages", type=int, default=1, help="expected page count (default 1)")
    ap.add_argument("--out", type=Path, help="also write the report to this file")
    ap.add_argument("--phone", default=None, help="phone that must appear (default: profile.md phone:)")
    a = ap.parse_args()

    text, pages, engine = extract(a.pdf)
    text_n = norm(text)
    checks: list[tuple[str, bool, str]] = []

    checks.append(("pages", pages == a.pages, f"{pages} page(s), expected {a.pages}"))

    emails = EMAIL.findall(text)
    digits = re.sub(r"\D", "", text)
    phone = a.phone or profile_phone(a.pdf)
    if phone:
        phone_ok = re.sub(r"\D", "", phone) in digits
        label = phone
    else:
        phone_ok = bool(re.search(r"\+?\d[\d\s().-]{7,}\d", text))
        label = "(any number)"
    checks.append(("contacts", bool(emails) and phone_ok,
                   f"email {'found: ' + emails[0] if emails else 'MISSING'}; phone {label} {'found' if phone_ok else 'MISSING'}"))

    bad = []
    if re.search(r"\(cid:\d+\)", text):
        bad.append("(cid:N) codes")
    if "�" in text:
        bad.append("replacement characters")
    pua = sorted({c for c in text if 0xE000 <= ord(c) <= 0xF8FF})
    if pua:
        bad.append(f"{len(pua)} private-use icon glyph(s)")
    lig = sorted({c for c in text if c in LIGATURES})
    if lig:
        bad.append("ligatures " + " ".join(lig))
    checks.append(("glyphs", not bad, "clean" if not bad else ", ".join(bad)))

    md = a.md.read_text() if a.md and a.md.is_file() else ""
    headings = [h.strip() for h in re.findall(r"^##\s+(.+)$", md, re.M)] or DEFAULT_HEADINGS
    positions = []
    missing_h = []
    for h in headings:
        i = text_n.find(norm(h))
        (missing_h.append(h) if i < 0 else positions.append((i, h)))
    in_order = [h for _, h in sorted(positions)] == [h for h in headings if h not in missing_h]
    checks.append(("order", in_order and not missing_h,
                   "headings in order" if in_order and not missing_h
                   else f"missing: {', '.join(missing_h) or '—'}; order {'ok' if in_order else 'WRONG: ' + ' → '.join(h for _, h in sorted(positions))}"))

    if md:
        md_words = [w for w in words(md_plain(md)) if len(w) >= 4]
        text_words = set(words(text))
        lost = [w for w in md_words if w not in text_words]
        ratio = 1 - len(lost) / max(len(md_words), 1)
        sample = ", ".join(sorted(set(lost))[:12])
        checks.append(("fidelity", ratio >= 0.95, f"{ratio:.0%} of CV words extracted" + (f"; lost e.g. {sample}" if lost else "")))

    kw = [k.strip() for k in a.keywords.split(",") if k.strip()]
    kw_hit = [k for k in kw if covered(k, text_n)]
    kw_miss = [k for k in kw if k not in kw_hit]
    sugg = []
    if a.jd and a.jd.is_file():
        sugg = [t for t in jd_terms(a.jd.read_text()) if not covered(t, text_n) and t not in map(norm, kw)]

    hard_fail = [n for n, ok, _ in checks if not ok]
    lines = [f"# ATS check — {a.pdf.name}", "",
             f"{date.today().isoformat()} · text layer via {engine} · {'PASS' if not hard_fail else 'FAIL: ' + ', '.join(hard_fail)}", "",
             "| Check | Result | Detail |", "|---|---|---|"]
    lines += [f"| {n} | {'✅' if ok else '❌'} | {d} |" for n, ok, d in checks]
    if kw:
        lines += ["", f"## Keyword coverage: {len(kw_hit)}/{len(kw)}", "",
                  "Covered: " + (", ".join(kw_hit) or "—"), "",
                  "Missing: " + (", ".join(kw_miss) or "—"), "",
                  "Add a missing keyword only where the master CV or profile supports it; otherwise it stays a gap."]
    if sugg:
        lines += ["", "## Frequent posting terms not in the CV (suggestions)", "", ", ".join(sugg)]
    report = "\n".join(lines) + "\n"
    print(report)
    if a.out:
        a.out.write_text(report)
    return 1 if hard_fail else 0


if __name__ == "__main__":
    sys.exit(main())
