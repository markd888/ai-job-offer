"""Parsing simulation for ats-check.py (#38 phase 3).

Not a CLI — ats-check.py loads this file by path (scripts run with `python3 -I`).

`parse(text)` turns extracted CV text into the structure an applicant tracking
system tries to build: contacts, summary, employment entries with dates,
education, skills, certifications, languages. Every field may be missing.
A field is {"value", "source_text", "confidence", "warnings"} — `source_text` is
the extracted span it came from, so nothing is filled that isn't in the text.

`compare(parsed, md, text)` checks the parse against the CV markdown a plugin
CV was built from, field by field: EXTRACTED, MISSING, AMBIGUOUS, CONFLICTING,
or NOT_IN_SOURCE (the CV itself doesn't have it — not an extraction failure).

Heuristics are bounded and deterministic: section headings, date ranges, and
the `Title | Company — Place` line cv-build.py emits (also `Title at Company`).
Schema: plugin/schemas/ats-parse.schema.md.
"""
from __future__ import annotations

import re
import unicodedata

EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
PHONE = re.compile(r"\+?\d[\d\s().-]{7,}\d")
LINKEDIN = re.compile(r"(?:https?://)?(?:[a-z]{2,3}\.)?linkedin\.com/in/[\w%-]+/?", re.I)
MONTH = (r"(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\.?|"
         r"(?:янв|фев|мар|апр|ма[йя]|июн|июл|авг|сен|окт|ноя|дек)[а-я]*\.?")
DATE = rf"(?:(?:{MONTH})\s+\d{{4}}|\d{{1,2}}[/.]\d{{4}}|\d{{4}})"
NOW = r"present|current|now|today|настоящее время|н\.в\.|по сей день"
RANGE = re.compile(rf"(?P<start>{DATE})\s*(?:–|—|-|to|до|по)\s*(?P<end>{DATE}|{NOW})", re.I)
LONE_YEAR_LINE = re.compile(rf"^\s*(?P<start>{DATE})\s*$", re.I)
BULLET = re.compile(r"^[\s\x7f•·▪◦‣∙●■*-]+")

SECTIONS = {
    "summary": r"(professional |executive |career )?(summary|profile)|about( me)?|objective|о себе|резюме|профиль",
    "experience": r"(work |professional |employment |career )?(experience|history)|employment|опыт работы|опыт",
    "education": r"education|academic background|qualifications|образование",
    "skills": r"(professional |technical |key |core )?(skills|competencies|expertise)|навыки|компетенции",
    "certifications": r"certifications?|certificates?|licen[cs]es|сертификаты",
    "languages": r"languages|языки",
    "projects": r"(applied |personal |side )?(ai )?projects|проекты",
}
SECTION_RX = {k: re.compile(rf"^\s*(?:{rx})\s*:?\s*$", re.I) for k, rx in SECTIONS.items()}
FIELDS = ("name", "email", "phone", "location", "linkedin")


def field(value=None, source=None, confidence="low", warnings=None) -> dict:
    return {"value": value, "source_text": source, "confidence": confidence if value is not None else None,
            "warnings": warnings or []}


def norm(s: str | None) -> str:
    s = unicodedata.normalize("NFKD", s or "").lower().replace("’", "'")
    return re.sub(r"[^\w@+]+", " ", s).strip()


def section_of(line: str) -> str | None:
    if len(line.split()) > 5:
        return None
    for k, rx in SECTION_RX.items():
        if rx.match(line):
            return k
    return None


def _clean(lines: list[str]) -> list[str]:
    return [ln.strip() for ln in lines]


def _split_sections(lines: list[str]) -> tuple[list[str], dict[str, list[str]], list[str]]:
    """(lines before the first heading, {kind: lines}, headings in order)."""
    head, cur, out, order = [], None, {}, []
    for ln in lines:
        kind = section_of(ln) if ln else None
        if kind:
            cur = kind
            out.setdefault(kind, [])
            order.append(ln)
            continue
        (out[cur] if cur else head).append(ln)
    return head, out, order


def _paragraphs(lines: list[str]) -> list[str]:
    """Join wrapped lines; a blank line or a bullet mark starts a new paragraph."""
    paras, cur = [], []
    for ln in lines:
        if not ln.strip() or BULLET.match(ln) and not BULLET.sub("", ln).strip():
            if cur:
                paras.append(" ".join(cur)); cur = []
            continue
        if BULLET.match(ln) and cur:
            paras.append(" ".join(cur)); cur = []
        cur.append(BULLET.sub("", ln).strip())
    if cur:
        paras.append(" ".join(cur))
    return [p for p in paras if p]


def _candidate(head: list[str], text: str) -> dict:
    c = {k: field() for k in FIELDS}
    lines = [ln for ln in head if ln.strip()] or text.splitlines()[:3]
    if lines:
        first = lines[0].strip()
        words = first.split()
        if 1 < len(words) <= 4 and not re.search(r"[\d@|/]", first):
            c["name"] = field(first, first, "high" if first.isupper() or first.istitle() else "medium")
        else:
            c["name"] = field(warnings=["first line doesn't look like a name"])
    m = EMAIL.search(text)
    if m:
        c["email"] = field(m.group(), m.group(), "high" if any(m.group() in ln for ln in lines) else "medium")
    m = LINKEDIN.search(text)
    if m:
        c["linkedin"] = field(m.group(), m.group(), "high")
    contact = next((ln for ln in lines if EMAIL.search(ln) or PHONE.search(ln)), "")
    m = PHONE.search(contact) or PHONE.search(text)
    if m:
        c["phone"] = field(m.group().strip(), m.group(), "high" if contact and m.group() in contact else "medium")
    for seg in re.split(r"\s*[|·•]\s*", contact):
        seg = seg.strip()
        if seg and not (EMAIL.search(seg) or PHONE.search(seg) or "/" in seg or "." in seg) and re.search(r"[^\W\d]", seg):
            c["location"] = field(seg, seg, "medium")
            break
    return c


def _role_line(line: str) -> tuple[str | None, str | None, str | None]:
    """(title, company, location) from 'Title | Company — Place' or 'Title at Company'."""
    rest = RANGE.sub("", line).strip(" |,–—-")
    loc = None
    if " — " in rest:
        rest, loc = rest.rsplit(" — ", 1)
    if " | " in rest:
        title, company = rest.split(" | ", 1)
        return title.strip() or None, company.strip() or None, (loc or "").strip() or None
    m = re.match(r"(.+?)\s+(?:at|@)\s+(.+)$", rest)
    if m:
        return m.group(1).strip(), m.group(2).strip(), (loc or "").strip() or None
    return None, None, None


def _experience(lines: list[str]) -> tuple[list[dict], list[str]]:
    entries: list[dict] = []
    warnings: list[str] = []
    cur: dict | None = None
    body: list[str] = []

    def close():
        if cur is not None:
            cur["description"] = _paragraphs(body)
            if cur["start_date"]["value"] is None:
                cur["start_date"]["warnings"].append("no date range found for this entry")
            entries.append(cur)

    for ln in lines:
        s = ln.strip()
        if not s:
            body.append("")
            continue
        title, company, loc = _role_line(s) if not BULLET.match(ln) else (None, None, None)
        rng = RANGE.search(s)
        if title and company:
            close()
            body = []
            cur = {"company": field(company, s, "high"), "job_title": field(title, s, "high"),
                   "location": field(loc, s, "medium") if loc else field(),
                   "start_date": field(), "end_date": field(), "description": [], "skills": []}
            if rng:
                cur["start_date"] = field(rng["start"], rng.group(), "high")
                cur["end_date"] = field(rng["end"], rng.group(), "high")
            continue
        if rng and len(s) <= 40 and cur is not None and cur["start_date"]["value"] is None:
            cur["start_date"] = field(rng["start"], rng.group(), "high")
            cur["end_date"] = field(rng["end"], rng.group(), "high")
            continue
        if rng and len(s) <= 40 and (cur is None or cur["start_date"]["value"] is not None):
            close()  # a date line with no recognisable role line before it
            body = []
            cur = {"company": field(warnings=["dates found, but no 'Title | Company' line"]),
                   "job_title": field(), "location": field(),
                   "start_date": field(rng["start"], rng.group(), "medium"),
                   "end_date": field(rng["end"], rng.group(), "medium"), "description": [], "skills": []}
            continue
        if cur is None:
            cur = {"company": field(warnings=["text before the first recognisable entry"]), "job_title": field(),
                   "location": field(), "start_date": field(), "end_date": field(), "description": [], "skills": []}
        body.append(ln)
    close()
    if not entries:
        warnings.append("experience section has no recognisable entries")
    undated = sum(1 for e in entries if e["start_date"]["value"] is None)
    if undated:
        warnings.append(f"{undated} employment entr{'y' if undated == 1 else 'ies'} without dates")
    return entries, warnings


def _education(lines: list[str]) -> list[dict]:
    out = []
    for p in [ln.strip() for ln in lines if ln.strip()]:
        rng = RANGE.search(p)
        if rng and len(p) <= 40 and out:
            out[-1]["dates"] = field(rng.group(), rng.group(), "high")
            continue
        parts = [x.strip() for x in re.split(r"\s+\|\s+|,\s+", RANGE.sub("", p).strip(" |,"), maxsplit=1)]
        out.append({"degree": field(parts[0], p, "medium"),
                    "institution": field(parts[1], p, "medium") if len(parts) > 1 else field(),
                    "dates": field(rng.group(), rng.group(), "high") if rng else field()})
    return out


LABEL = re.compile(r"^\s*([A-ZА-Я][\w&/ -]{1,30}):\s+")


def _items(lines: list[str]) -> tuple[list[dict], dict[str, str]]:
    """Comma/semicolon list items. A line starting 'Label: …' opens a group; other
    lines continue the previous one (PDF extraction wraps long lines). Labels are
    dropped from the items and returned as {label: text}."""
    groups: list[list[str]] = []   # [label, text]
    for ln in lines:
        s = BULLET.sub("", ln).strip()
        if not s:
            continue
        m = LABEL.match(s)
        if m or not groups:
            groups.append([m.group(1).strip() if m else "", s[m.end():] if m else s])
        else:
            groups[-1][1] += " " + s
    labelled = {lab: txt for lab, txt in groups if lab}
    items = []
    for _, txt in groups:
        txt = re.sub(r"\([^)]*\)", lambda m: m.group().replace(",", " "), txt)
        for raw in re.split(r"[;,•·|]", txt):
            s = raw.strip(" .")
            if s and len(s) <= 60:
                items.append(field(s, s, "medium"))
    return items, labelled


def parse(text: str, engine: str = "", fmt: str = "pdf", pages: int | None = None) -> dict:
    lines = _clean(text.splitlines())
    head, secs, order = _split_sections(lines)
    warnings: list[str] = []
    exp, w = _experience(secs.get("experience", [])) if "experience" in secs else ([], ["no experience section heading found"])
    warnings += w
    skills, labelled = _items(secs.get("skills", []))
    lang_lines = secs.get("languages") or [labelled[k] for k in labelled if re.match(r"languages?|языки", k, re.I)]
    langs, _ = _items(lang_lines) if lang_lines else ([], {})
    lang_n = {norm(lg["value"]) for lg in langs}
    skills = [s for s in skills if norm(s["value"]) not in lang_n]
    certs, _ = _items(secs.get("certifications", []))
    summary = " ".join(_paragraphs(secs.get("summary", []))) or None
    for k in ("education", "skills"):
        if k not in secs:
            warnings.append(f"no {k} section heading found")
    return {
        "document": {"format": fmt, "page_count": pages, "extraction_engine": engine},
        "candidate": _candidate(head, text),
        "summary": field(summary, summary, "high") if summary else field(),
        "sections": order,
        "experience": exp,
        "education": _education(secs.get("education", [])),
        "skills": skills,
        "certifications": certs,
        "languages": langs,
        "parsing_warnings": warnings,
    }


# --- the source: CV markdown as cv-build.py reads it ---------------------------

def parse_md(md: str) -> dict:
    lines = md.splitlines()
    name = next((ln[2:].strip() for ln in lines if ln.startswith("# ")), None)
    contact = next((ln for ln in lines if EMAIL.search(ln) or PHONE.search(ln)), "")
    loc = next((s.strip() for s in re.split(r"\s*[|·•]\s*", contact)
                if s.strip() and not (EMAIL.search(s) or PHONE.search(s) or "/" in s or "." in s)), None)
    jobs, edu, skills_lines, lang_lines, cert_lines, headings = [], [], [], [], [], []
    kind = None
    for i, ln in enumerate(lines):
        if ln.startswith("## "):
            headings.append(ln[3:].strip())
            kind = section_of(ln[3:].strip())
            continue
        if ln.startswith("### ") and kind in ("experience", "education"):
            t, c, place = _role_line(ln[4:].strip())
            nxt = next((x for x in lines[i + 1:i + 3] if x.strip()), "")
            rng = RANGE.search(nxt) if nxt.strip().startswith("*") else None
            if kind == "experience":
                jobs.append({"title": t or ln[4:].strip(), "company": c, "start": rng["start"] if rng else None,
                             "end": rng["end"] if rng else None})
            else:
                edu.append({"degree": t or ln[4:].strip(), "institution": c})
        elif kind == "education" and ln.strip() and not ln.startswith(("*", "#")):
            parts = re.split(r"\s+\|\s+|,\s+", ln.strip(), maxsplit=1)
            edu.append({"degree": parts[0], "institution": parts[1] if len(parts) > 1 else None})
        elif kind == "skills" and ln.strip():
            m = re.match(r"\*\*(.+?):\*\*\s*(.*)", ln.strip())
            if m and re.match(r"languages?|языки", m.group(1), re.I):
                lang_lines.append(f"Group: {m.group(2)}")
            elif m and re.match(r"certif", m.group(1), re.I):
                cert_lines.append(f"Group: {m.group(2)}")
            else:
                skills_lines.append(f"Group: {m.group(2)}" if m else f"Group: {ln}")
        elif kind == "languages" and ln.strip():
            lang_lines.append(f"Group: {ln.lstrip('-* ')}")
        elif kind == "certifications" and ln.strip():
            cert_lines.append(f"Group: {ln.lstrip('-* ')}")
    strip = lambda xs: [re.sub(r"[*_`]", "", x) for x in xs]  # noqa: E731
    return {"name": name, "email": (EMAIL.search(contact) or [None])[0] if contact else None,
            "phone": (PHONE.search(contact).group().strip() if PHONE.search(contact) else None),
            "location": loc, "linkedin": (LINKEDIN.search(md).group() if LINKEDIN.search(md) else None),
            "headings": headings, "jobs": jobs, "education": edu,
            "skills": [s["value"] for s in _items(strip(skills_lines))[0]],
            "languages": [s["value"] for s in _items(strip(lang_lines))[0]],
            "certifications": [s["value"] for s in _items(strip(cert_lines))[0]]}


def _status(expected, got, text_n: str) -> str:
    if expected in (None, "", []):
        return "NOT_IN_SOURCE"
    if got in (None, ""):
        return "AMBIGUOUS" if norm(expected) and norm(expected) in text_n else "MISSING"
    return "EXTRACTED" if norm(expected) == norm(got) else "CONFLICTING"


def compare(parsed: dict, md: str, text: str) -> list[dict]:
    """Rows of {field, expected, extracted, status, note}."""
    src = parse_md(md)
    text_n = norm(text)
    rows: list[dict] = []

    def row(f, exp, got, note=""):
        rows.append({"field": f, "expected": exp, "extracted": got, "status": _status(exp, got, text_n), "note": note})

    cand = parsed["candidate"]
    for k in FIELDS:
        got = cand[k]["value"]
        if k == "phone" and got and src["phone"]:
            got = src["phone"] if re.sub(r"\D", "", got) == re.sub(r"\D", "", src["phone"]) else got
        row(k, src[k], got)

    found = {section_of(h) for h in parsed["sections"]}
    for h in src["headings"]:
        k = section_of(h)
        rows.append({"field": f"section: {h}", "expected": h, "extracted": h if k in found else None,
                     "status": "EXTRACTED" if k in found else ("AMBIGUOUS" if norm(h) in text_n else "MISSING"),
                     "note": "" if k else "not a heading kind parsers know"})

    for j in src["jobs"]:
        match = next((e for e in parsed["experience"] if e["company"]["value"]
                      and norm(e["company"]["value"]) == norm(j["company"])), None)
        label = f"job: {j['company'] or j['title']}"
        if match is None:
            st = "AMBIGUOUS" if j["company"] and norm(j["company"]) in text_n else "MISSING"
            rows.append({"field": label, "expected": f"{j['title']} · {j['start']}–{j['end']}", "extracted": None,
                         "status": st, "note": "text is there, not recognised as an entry" if st == "AMBIGUOUS" else ""})
            continue
        row(f"{label} · title", j["title"], match["job_title"]["value"])
        row(f"{label} · dates", f"{j['start']} – {j['end']}" if j["start"] else None,
            f"{match['start_date']['value']} – {match['end_date']['value']}" if match["start_date"]["value"] else None)

    for e in src["education"]:
        got = next((p for p in parsed["education"] if norm(p["degree"]["value"]) == norm(e["degree"])), None)
        row(f"education: {e['degree']}", e["degree"], got["degree"]["value"] if got else None)

    for kind in ("skills", "languages", "certifications"):
        exp = src[kind]
        if not exp:
            rows.append({"field": kind, "expected": None, "extracted": None, "status": "NOT_IN_SOURCE", "note": ""})
            continue
        got_n = {norm(s["value"]) for s in parsed[kind]}
        hit = [s for s in exp if norm(s) in got_n]
        in_text = [s for s in exp if s not in hit and norm(s) in text_n]
        share = len(hit) / len(exp)
        st = "EXTRACTED" if share >= 0.9 else "AMBIGUOUS" if hit or in_text else "MISSING"
        rows.append({"field": kind, "expected": f"{len(exp)} item(s)", "extracted": f"{len(hit)} as {kind}",
                     "status": st, "note": f"{len(in_text)} more in the text but not read as {kind}" if in_text else ""})
    return rows
