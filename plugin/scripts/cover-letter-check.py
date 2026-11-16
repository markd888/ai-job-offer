#!/usr/bin/env python3
"""Mechanical backstop for /cover-letter's no-invention rule.

Usage:
  python3 -I cover-letter-check.py <letter.md> --sources <cv.md> <profile.md> [<research-brief.md> ...]
      [--min-words 150] [--max-words 250]

Checks the letter body against the files its claims may come from:
  - every number (12%, 4.1, ~200K, £60M, 18) appears in a source;
  - every capitalised name that isn't the first word of a sentence (a company,
    a product, a tool) appears in a source;
  - the word count is within range;
  - no markdown headings or bullets (cover-letter-build.py lays out plain
    paragraphs);
  - [CONFIRM: ...] markers are counted, so the user resolves them before sending.

Exits 1 when a number or name can't be traced, the length is out of range, or
the layout is wrong. A pass doesn't prove a claim is fair — "led" vs "helped"
still needs reading — it proves nothing was made up out of thin air.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

NUMBER_RE = re.compile(r"(?<![\w.])[£$€~+]?(\d+(?:[.,]\d+)?)\s*(%|[KkMmBb]\b)?")
NAME_RE = re.compile(r"[A-Z][\w&'’-]*")
SENTENCE_END = re.compile(r"[.!?:—]\s*$")
FIRST_PERSON = {"I", "I'm", "I’m", "I've", "I’ve", "I'd", "I’d", "I'll", "I’ll"}
CONFIRM_RE = re.compile(r"\[CONFIRM:[^\]]*\]")


def words(text: str) -> int:
    return len(re.findall(r"[\w'’%.+~£$-]+", CONFIRM_RE.sub("", text)))


def numbers(text: str) -> list[str]:
    out = []
    for m in NUMBER_RE.finditer(text):
        out.append(m.group(1) + (m.group(2) or "").upper())
    return out


def names(text: str) -> list[str]:
    """Capitalised words that aren't the first word of a paragraph or sentence."""
    out = []
    for para in re.split(r"\n\s*\n", text):
        for m in NAME_RE.finditer(para):
            before = para[:m.start()]
            if not before.strip() or SENTENCE_END.search(before) or m.group() in FIRST_PERSON:
                continue
            out.append(m.group().rstrip("'’-"))
    return out


def traced(token: str, sources: str) -> bool:
    # Whole numbers only: "8" must not match the 8 in "18". "200K" in the
    # letter also matches a bare 200 in a source, so the unit can be added.
    for t in (token, re.sub(r"[^\d.]", "", token)):
        if t and re.search(rf"(?<![\d.]){re.escape(t)}(?![\d])", sources, re.I):
            return True
    return False


def check(letter: str, sources: str, min_words: int, max_words: int) -> dict:
    lowered = sources.lower()
    return {
        "words": words(letter),
        "untraced_numbers": sorted({n for n in numbers(CONFIRM_RE.sub("", letter)) if not traced(n, sources)}),
        "untraced_names": sorted({n for n in names(CONFIRM_RE.sub("", letter)) if n.lower() not in lowered}),
        "layout": [l for l in letter.splitlines() if re.match(r"\s*(#|[-*] |\d+\. )", l)],
        "confirm": len(CONFIRM_RE.findall(letter)),
        "min": min_words,
        "max": max_words,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("letter", type=Path)
    ap.add_argument("--sources", type=Path, nargs="+", required=True)
    ap.add_argument("--min-words", type=int, default=150)
    ap.add_argument("--max-words", type=int, default=250)
    a = ap.parse_args()

    sources = "\n".join(p.read_text(encoding="utf-8") for p in a.sources if p.is_file())
    r = check(a.letter.read_text(encoding="utf-8"), sources, a.min_words, a.max_words)
    problems = []
    if not a.min_words <= r["words"] <= a.max_words:
        problems.append(f"{r['words']} words; aim for {a.min_words}–{a.max_words}")
    if r["untraced_numbers"]:
        problems.append("numbers not found in the sources: " + ", ".join(r["untraced_numbers"]))
    if r["untraced_names"]:
        problems.append("names not found in the sources: " + ", ".join(r["untraced_names"]))
    if r["layout"]:
        problems.append("headings or list lines (use plain paragraphs): " + "; ".join(l.strip() for l in r["layout"]))

    print(f"{r['words']} words, {r['confirm']} [CONFIRM] marker(s)")
    for p in problems:
        print("FAIL " + p)
    if not problems:
        print("PASS every number and name traces to a source")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
