"""Document-integrity warnings for ats-check.py (#38 phase 2).

Not a CLI — ats-check.py loads this file by path (scripts run with `python3 -I`).

Every check here is a WARNING: it never changes ats-check.py's exit code.
Promoting one to a hard failure is a separate decision, because it would block
/apply runs that pass today.

Each warning is {"check", "detail"}; `detail` says what was observed.
"""
from __future__ import annotations

import re
from collections import Counter

MIN_WORDS = 80                     # a one-page CV has several hundred
DUP_MIN_WORDS = 6                  # shorter repeated lines (dates, "Remote") are normal
AGREEMENT_MIN = 0.9                # share of words both extractors see

# UTF-8 read as Latin-1/CP1252: "â€™" for ’, "Ã©" for é, "Ð¿" for п.
MOJIBAKE = re.compile(r"â€[\x80-\xbf™œ“”˜š›ž]|Ã[\x80-\xbf©¨¡¢£¤¥¦§ª«¬®¯°±²³´µ¶·¸¹º»¼½¾¿]|[ÐÑ][\x80-\xbf°±²³´µ¶·¸¹º»¼½¾¿]")
CONTROL = re.compile(r"[\x00-\x08\x0b\x0e-\x1f\x7f]")

# What every CV needs, in the words CVs use for it (English and Russian).
SECTION_KINDS = {
    "experience": r"experience|employment|work history|career history|professional background|опыт работы|опыт",
    "education": r"education|academic|qualifications|degree|university|образование",
    "skills": r"skills|competenc|expertise|technolog|tools|навыки|компетенции",
}


def _words(text: str) -> list[str]:
    return re.findall(r"[^\W_]{2,}", text.lower())


def empty(text: str) -> list[dict]:
    n = len(_words(text))
    if n == 0:
        return [{"check": "empty", "detail": "no text at all — the file is likely a scanned image"}]
    if n < MIN_WORDS:
        return [{"check": "empty", "detail": f"only {n} words extracted — most of the CV may be images or vector text"}]
    return []


def duplicates(text: str) -> list[dict]:
    lines = [re.sub(r"\s+", " ", ln).strip().lower() for ln in text.splitlines()]
    counts = Counter(ln for ln in lines if len(ln.split()) >= DUP_MIN_WORDS)
    rep = [(ln, n) for ln, n in counts.items() if n > 1]
    if not rep:
        return []
    sample = "; ".join(f"\"{ln[:60]}\" ×{n}" for ln, n in rep[:3])
    return [{"check": "duplicates", "detail": f"{len(rep)} line(s) extracted more than once — often an overlapping "
                                               f"text layer, so a parser may read them twice: {sample}"}]


def encoding(text: str) -> list[dict]:
    out = []
    bad = MOJIBAKE.findall(text)
    if bad:
        out.append({"check": "encoding", "detail": f"{len(bad)} mis-decoded sequence(s) such as "
                                                    f"{', '.join(sorted(set(bad))[:4])} — text saved in one encoding and read as another"})
    bullets = len(re.findall(r"^\x7f\s*$|^\x7f", text, re.M))
    ctl = len(CONTROL.findall(text)) - bullets
    if bullets:
        out.append({"check": "encoding", "detail": f"{bullets} bullet mark(s) extract as an invisible control character "
                                                    "(U+007F) rather than a bullet — most parsers drop it, so the bullet "
                                                    "text still reads, but the list structure is lost"})
    if ctl:
        out.append({"check": "encoding", "detail": f"{ctl} control character(s) in the text layer"})
    return out


def sections(text: str, md_headings: list[str]) -> list[dict]:
    """Which of experience / education / skills has no heading at all.

    With the CV markdown, its own `##` headings are the expected set (the hard
    `order` check already covers them); this only adds what the CV lacks as a kind.
    """
    pool = "\n".join(md_headings) if md_headings else text
    missing = [k for k, rx in SECTION_KINDS.items() if not re.search(rx, pool, re.I)]
    if not missing:
        return []
    where = "the CV's headings" if md_headings else "the extracted text"
    return [{"check": "sections", "detail": f"no {', no '.join(missing)} section found in {where} — "
                                             "parsers file entries under section headings"}]


def agreement(primary: str, other: str, other_engine: str) -> list[dict]:
    a, b = set(_words(primary)), set(_words(other))
    if not a and not b:
        return []
    share = len(a & b) / max(len(a | b), 1)
    if share >= AGREEMENT_MIN:
        return []
    only = sorted(b - a)[:6] or sorted(a - b)[:6]
    return [{"check": "extractors", "detail": f"{other_engine} and the main extractor agree on {share:.0%} of words "
                                               f"(e.g. {', '.join(only)}) — different parsers may read this file differently"}]


def check(text: str, md_headings: list[str], second: tuple[str, str] | None = None) -> list[dict]:
    """All integrity warnings. `second` is (text, engine) from another extractor, if one ran."""
    out = empty(text) + duplicates(text) + encoding(text) + sections(text, md_headings)
    if second:
        out += agreement(text, *second)
    return out
