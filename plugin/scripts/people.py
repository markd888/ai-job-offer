"""People records: userdata/people/<slug>.md. Shared by record-outreach.py,
record-sent.py, the dashboard and the schema validator.

Not a CLI. Scripts run with `python3 -I`, which drops their folder from
sys.path, so callers load this file by path. Stdlib only.

A person file is frontmatter (name, company, relation, channel, roles) plus a
body with a `## Log` section. Each log line is one contact, in one fixed shape
so it can be counted:

    - 2026-11-16 sent referral-ask (linkedin): Asked Dana to refer me for Senior PM, Lending.
    - 2026-11-18 received referral: Dana put my CV forward.

The weekly outreach count is the number of `sent` lines of an OUTREACH_KINDS
kind dated in the current ISO week — not a keyword guess over journal.md.
"""
from __future__ import annotations

import re
import unicodedata
from datetime import date, timedelta
from pathlib import Path

RELATIONS = ("former-colleague", "friend", "recruiter", "hiring-manager", "interviewer",
             "referrer", "peer", "met-at-event", "other")
CHANNELS = ("linkedin", "email", "telegram", "whatsapp", "phone", "in-person", "other")
DIRECTIONS = ("sent", "received")
KINDS = ("reach-out", "referral-ask", "intro-ask", "follow-up", "thank-you", "feedback-ask",
         "update", "reply", "referral", "intro", "feedback", "other")
# What counts toward weekly_targets.warm_outreach: the user starting or chasing a
# conversation. Thank-yous, updates and feedback asks are contact, not outreach.
OUTREACH_KINDS = ("reach-out", "referral-ask", "intro-ask", "follow-up")

LOG_RE = re.compile(
    r"^- (?P<date>\d{4}-\d{2}-\d{2}) (?P<direction>[a-z]+) (?P<kind>[a-z-]+)"
    r"(?: \((?P<channel>[a-z-]+)\))?: (?P<text>.+)$"
)
_KEY_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(.*)$")


def slugify(name: str) -> str:
    """Dana Okafor -> dana-okafor; accents are folded, other scripts kept."""
    folded = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    base = folded if folded.strip() else name
    return re.sub(r"[^\w]+", "-", base.lower(), flags=re.UNICODE).strip("-_") or "person"


def frontmatter(text: str) -> dict[str, str]:
    lines = text.lstrip("﻿").splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    out: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return out
        m = _KEY_RE.match(line)
        if m:
            value = re.sub(r"(?:^|\s)#.*$", "", m.group(2)).strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                value = value[1:-1]
            out[m.group(1)] = value
    return {}


def roles_of(fm: dict[str, str]) -> list[str]:
    """`roles: ["Plaid/senior-pm-consumer-credit", "Wagestream"]` -> the list."""
    return [a or b for a, b in re.findall(r"\"([^\"]+)\"|'([^']+)'", fm.get("roles", ""))]


def log_section(text: str) -> list[str]:
    """The lines under `## Log`, up to the next `## ` heading."""
    m = re.search(r"^## Log[ \t]*$", text, re.M)
    if not m:
        return []
    body = text[m.end():]
    nxt = re.search(r"^## ", body, re.M)
    return [l for l in (body[:nxt.start()] if nxt else body).splitlines() if l.strip()]


def parse_log(text: str) -> tuple[list[dict[str, str]], list[str]]:
    """Return (entries, malformed lines) from a person file's `## Log`."""
    entries, bad = [], []
    for line in log_section(text):
        m = LOG_RE.match(line.strip())
        if (m and m["direction"] in DIRECTIONS and m["kind"] in KINDS
                and (m["channel"] is None or m["channel"] in CHANNELS)):
            try:
                date.fromisoformat(m["date"])
            except ValueError:
                bad.append(line)
                continue
            entries.append(m.groupdict())
        else:
            bad.append(line)
    return entries, bad


def people_dir(userdata: Path) -> Path:
    return userdata / "people"


def person_files(userdata: Path) -> list[Path]:
    d = people_dir(userdata)
    return sorted(p for p in d.glob("*.md") if p.is_file()) if d.is_dir() else []


def find_person(userdata: Path, name: str, company: str = "") -> Path | None:
    """Match on the `name` field (case-insensitive), then company if several."""
    wanted = name.strip().strip("[]").lower()
    hits = [p for p in person_files(userdata)
            if frontmatter(p.read_text()).get("name", "").lower() == wanted]
    if company and len(hits) > 1:
        hits = [p for p in hits
                if frontmatter(p.read_text()).get("company", "").lower() == company.lower()] or hits
    return hits[0] if hits else None


def new_person_path(userdata: Path, name: str, company: str = "") -> Path:
    d = people_dir(userdata)
    path = d / f"{slugify(name)}.md"
    if path.exists() and company:
        path = d / f"{slugify(name + ' ' + company)}.md"
    n = 2
    stem = path.stem
    while path.exists():
        path = d / f"{stem}-{n}.md"
        n += 1
    return path


def render_person(name: str, company: str, relation: str, channel: str, roles: list[str]) -> str:
    fields = [f"name: {name}"]
    if company:
        fields.append(f"company: {company}")
    fields.append(f"relation: {relation}")
    if channel:
        fields.append(f"channel: {channel}")
    fields.append("roles: [" + ", ".join(f'"{r}"' for r in roles) + "]")
    return "---\n" + "\n".join(fields) + f"\n---\n\n# {name}\n\n## Log\n"


def set_roles(text: str, roles: list[str]) -> str:
    line = "roles: [" + ", ".join(f'"{r}"' for r in roles) + "]"
    if re.search(r"^roles:.*$", text, re.M):
        return re.sub(r"^roles:.*$", line, text, count=1, flags=re.M)
    return re.sub(r"\A(---\n(?:.*\n)*?)---\n", lambda m: m.group(1) + line + "\n---\n", text, count=1)


def add_log_line(text: str, line: str) -> str:
    """Append a line at the end of `## Log` (creating it), keeping date order loose."""
    m = re.search(r"^## Log[ \t]*$", text, re.M)
    if not m:
        return text.rstrip("\n") + "\n\n## Log\n" + line + "\n"
    rest = text[m.end():]
    nxt = re.search(r"^## ", rest, re.M)
    if nxt:
        head, tail = rest[:nxt.start()].rstrip("\n"), rest[nxt.start():]
        return text[:m.end()] + head + "\n" + line + "\n\n" + tail
    return text.rstrip("\n") + "\n" + line + "\n"


def format_log(day: str, direction: str, kind: str, channel: str, text: str) -> str:
    chan = f" ({channel})" if channel else ""
    return f"- {day} {direction} {kind}{chan}: {' '.join(text.split())}"


def count_outreach(userdata: Path, today: date) -> int:
    """`sent` outreach lines dated in [Monday of this week, today]."""
    start = today - timedelta(days=today.weekday())
    n = 0
    for p in person_files(userdata):
        entries, _ = parse_log(p.read_text())
        for e in entries:
            d = date.fromisoformat(e["date"])
            if e["direction"] == "sent" and e["kind"] in OUTREACH_KINDS and start <= d <= today:
                n += 1
    return n
