"""Text normalisation and keyword matching for ats-check.py.

Not a CLI — ats-check.py loads this file by path (scripts run with `python3 -I`).
Phase 4 of #38 adds JD requirement categories and evidence matching here.
"""
from __future__ import annotations

import re
import unicodedata
from collections import Counter

STOP = set("""a an and are as at be by for from has have in into is it its of on or our that the their this to
we will with you your who what when where which while within without across about over under per via than then
they them these those all any can more most other such not only also may must should would could role team work
working years year experience strong ability skills including new using help make based well both each own""".split())


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
