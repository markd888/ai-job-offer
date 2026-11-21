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


# --- Job description matching (#38 phase 4) ---------------------------------------
#
# Requirements come from Claude (the skill writes them to a JSON file and passes
# --requirements) or, without one, from a deterministic split of the posting
# text by its own section headings. The script only matches: it never writes to
# the CV, so an unsupported keyword can't be inserted.
#
# Vocabulary shared with scoring v2 (0.8.4): every positive match quotes the CV
# line it rests on; "the CV doesn't show it" is NOT_FOUND, never a gap claim.

CATEGORIES = ("REQUIRED", "PREFERRED", "RESPONSIBILITY", "DOMAIN", "TOOLS_AND_TECHNOLOGIES")
MATCH_STATUSES = ("SUPPORTED", "PARTIALLY_SUPPORTED", "NOT_FOUND", "AMBIGUOUS")
SUPPORTED_SHARE = 0.6          # of a requirement's terms, found together in one experience line

GENERIC = STOP | set("""experience experienced years year proven strong solid excellent good great deep
knowledge understanding ability able skills skill track record background familiarity familiar hands
plus bonus nice preferred required requirement requirements must minimum least ideally ideal etc
environment environments fast paced passion passionate love comfortable demonstrated level senior
product products manager management managing work closely partner partners stakeholders cross
functional across own owning drive driving lead leading build building help define defining
communication communicator communicate written verbal collaboration collaborative teamwork team player
interpersonal problem solving solver detail oriented organised organized self starter motivated proactive
curious curiosity attitude mindset end clear concise effective fluent ownership accountable accountability adaptable flexible""".split())

HEADING_CATEGORY = [
    (re.compile(r"nice to have|preferred|bonus|plus|desirable|would be great|желательно|будет плюсом", re.I), "PREFERRED"),
    (re.compile(r"requirements?|qualifications?|must have|what you (?:need|bring|have)|who you are|about you|"
                r"you have|you bring|требования|мы ждём", re.I), "REQUIRED"),
    (re.compile(r"responsibilit|what you(?:'|’)?ll do|the role|your role|day to day|you will|обязанности|задачи", re.I),
     "RESPONSIBILITY"),
    (re.compile(r"tech stack|tools|technolog|стек", re.I), "TOOLS_AND_TECHNOLOGIES"),
]
BULLET_RX = re.compile(r"^\s*(?:[-*•·▪◦‣●■]|\d+[.)])\s+")


def terms_of(requirement: str) -> list[str]:
    """Content words of a requirement — what has to appear in a CV line for it to count."""
    out: list[str] = []
    for w in words(md_plain(requirement)):
        if len(w) > 2 and w not in GENERIC and not w.isdigit() and w not in out:
            out.append(w)
    return out


def requirements_from_jd(jd: str) -> list[dict]:
    """Bullets under the posting's own headings; category from the heading, then from
    the bullet's wording. A rough fallback — Claude's --requirements file is better."""
    out, cat = [], None
    for raw in jd.splitlines():
        line = raw.strip()
        if not line:
            continue
        is_bullet = bool(BULLET_RX.match(line))
        text = BULLET_RX.sub("", line).strip(" *#:")
        if not is_bullet and len(text.split()) <= 8:
            hit = next((c for rx, c in HEADING_CATEGORY if rx.search(text)), None)
            if hit or line.startswith("#") or text.endswith(":"):
                cat = hit
            continue
        if not is_bullet or cat is None:
            continue
        c = cat
        if re.search(r"\b(nice to have|preferred|a plus|bonus|ideally)\b", text, re.I):
            c = "PREFERRED"
        elif re.search(r"\b(must|required|essential|minimum)\b", text, re.I) and c != "RESPONSIBILITY":
            c = "REQUIRED"
        out.append({"requirement": text, "category": c})
    return out


def _cv_lines(parsed: dict) -> tuple[list[tuple[str, str]], list[str]]:
    """(demonstrated lines as (where, text), listed skills). Demonstrated = experience
    descriptions, role lines and the summary; listed = the skills section."""
    shown: list[tuple[str, str]] = []
    for e in parsed["experience"]:
        where = e["company"]["value"] or "experience"
        if e["job_title"]["value"]:
            shown.append((where, e["job_title"]["value"]))
        shown += [(where, x) for d in e["description"] for x in _sentences(d)]
    if parsed["summary"]["value"]:  # last, so on a tie an experience line is the quote
        shown += [("summary", x) for x in _sentences(parsed["summary"]["value"])]
    return shown, [s["value"] for s in parsed["skills"]]


def _sentences(text: str) -> list[str]:
    return [x.strip() for x in re.split(r"(?<=[.;!?])\s+(?=[A-ZА-Я0-9])", text) if x.strip()]


def _best(terms: list[str], lines: list[tuple[str, str]]) -> tuple[float, tuple[str, str] | None]:
    best, at = 0.0, None
    for where, line in lines:
        ln = norm(line)
        share = sum(covered(t, ln) for t in terms) / len(terms)
        if share > best:
            best, at = share, (where, line)
    return best, at


def match(requirements: list[dict], parsed: dict, profile_text: str = "") -> list[dict]:
    """One row per requirement: status plus the quote it rests on.

    SUPPORTED            ≥ 60% of the terms together in one experience/summary line
    PARTIALLY_SUPPORTED  some terms in experience; or only in the skills list
                         (listed, not demonstrated); or only in profile.md
    NOT_FOUND            nothing on the CV or in the profile
    AMBIGUOUS            the requirement has no concrete terms to look for
    """
    shown, listed = _cv_lines(parsed)
    prof = [("profile", ln.strip(" -*")) for ln in profile_text.splitlines() if len(ln.split()) >= 3]
    rows = []
    for r in requirements:
        terms = [norm(t) for t in r.get("terms") or terms_of(r["requirement"])]
        row = {"requirement": r["requirement"], "category": r.get("category") if r.get("category") in CATEGORIES
               else "REQUIRED", "terms": terms, "status": "NOT_FOUND", "evidence": None, "source": None, "note": ""}
        if not terms:
            row.update(status="AMBIGUOUS", note="no concrete skill, tool or domain to look for")
            rows.append(row); continue
        share, at = _best(terms, shown)
        if share >= SUPPORTED_SHARE - 1e-9:
            row.update(status="SUPPORTED", evidence=at[1], source=at[0])
        else:
            in_skills = [s for s in listed if any(covered(t, norm(s)) for t in terms)]
            if share > 0:
                row.update(status="PARTIALLY_SUPPORTED", evidence=at[1], source=at[0],
                           note=f"{share:.0%} of the terms in one line")
            elif in_skills:
                row.update(status="PARTIALLY_SUPPORTED", evidence=", ".join(in_skills[:3]), source="skills",
                           note="listed under skills, not shown in experience")
            else:
                pshare, pat = _best(terms, prof)
                if pshare >= SUPPORTED_SHARE - 1e-9:
                    row.update(status="PARTIALLY_SUPPORTED", evidence=pat[1], source="profile",
                               note="in your profile, not on this CV")
        rows.append(row)
    return rows


def coverage(rows: list[dict]) -> dict[str, tuple[int, int]]:
    """Per category: (supported, total), AMBIGUOUS left out. Never summed across categories."""
    out: dict[str, tuple[int, int]] = {}
    for c in CATEGORIES:
        rs = [r for r in rows if r["category"] == c and r["status"] != "AMBIGUOUS"]
        if rs:
            out[c] = (sum(r["status"] == "SUPPORTED" for r in rs), len(rs))
    return out
