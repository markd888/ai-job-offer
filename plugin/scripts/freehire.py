#!/usr/bin/env python3
"""Freehire as a /job-search Discovery source: the deterministic parts.

The skill calls the Freehire MCP itself; this script does what must not be left
to judgement:

  detect     Read tool names (one per line) on stdin, print the Freehire MCP
             prefix as the session spells it (case-insensitive). Exit 1 if absent.
  filters    Validate `freehire_filters` in profile.md and print the search_jobs
             argument sets as JSON. Country and remote-region filters are a
             UNION on Freehire's side, so they are always emitted as separate
             calls, never one.
  screen     Read saved search_jobs responses (JSON files), stop if Freehire
             ignored any parameter, then drop off-target titles, agencies and
             duplicates (within the batch and against userdata/companies).
             Print survivors + a dropped-by-reason summary as JSON.

Usage:
  python3 -I freehire.py detect < tool-names.txt
  python3 -I freehire.py filters --profile userdata/profile.md [--open-within-days 7]
  python3 -I freehire.py screen --userdata userdata RESULT.json [RESULT.json ...]

Exit codes: 0 ok, 1 not found / invalid filters, 3 ignored_params guard tripped.
Read-only: it never writes files.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path
from urllib.parse import urlparse

# Enums as search_jobs / list_filter_values report them (checked 2026-11-19).
SENIORITY = {"intern", "junior", "middle", "senior", "lead", "staff", "principal", "c_level"}
REGIONS = {"global", "north_america", "latam", "eu", "uk", "mena", "africa", "apac", "cis"}
WORK_MODES = {"remote", "hybrid", "onsite"}
CATEGORIES = {
    "product", "project_management", "business_analysis", "data_analytics", "finance",
    "operations", "software_engineering", "backend", "frontend", "fullstack", "devops",
    "data_engineering", "data_science", "ml_ai", "ai_engineering", "design", "marketing",
    "sales", "support", "customer_success", "solutions_engineering", "security", "qa",
    "architecture", "sre", "mobile", "hr", "recruiting", "legal", "technical_writing",
    "developer_relations", "blockchain", "other",
}
KEYS = {"category", "seniority", "countries", "on_site_work_modes", "remote_regions",
        "salary_min", "salary_currency", "title_allow", "title_deny", "exclude_companies"}

DEFAULT_ALLOW = ["product manager", "head of product", "group product manager",
                 "product lead", "lead product", "director of product", "vp product"]
DEFAULT_DENY = ["product owner", "business analyst", "agile", "scrum master",
                "product marketing", "project manager", "area product manager"]
# Recruiter reposts and staffing agencies: never the employer.
AGENCIES = {"jobgether", "gempool", "hays", "randstad", "michael page", "adecco",
            "robert half", "crossover", "toptal", "turing", "andela"}
JOB_BOARDS = ("linkedin.", "indeed.", "glassdoor.", "freehire.me",
              # aggregators Freehire also reads: never the employer's own ATS
              "adzuna.", "arbeitnow.", "himalayas.", "justjoin.", "wttj.",
              "welcometothejungle.", "spainjobs.", "jobindex.")
# Title shapes a substring list misses: "Senior PM, Payments", "GPM",
# "Head of Payments Product". Used only with the default allow list.
ALLOW_PATTERNS = [re.compile(p) for p in (
    r"\b(?:senior |lead |principal |staff |group )?g?pm\b",
    r"\bhead of (?:\w+ ){0,3}product\b",
)]


# ---------- profile ----------

def _scalar(v: str):
    v = v.split(" #")[0].strip()
    if v.startswith("[") and v.endswith("]"):
        return [x.strip().strip("\"'") for x in v[1:-1].split(",") if x.strip()]
    v = v.strip("\"'")
    return int(v) if re.fullmatch(r"\d+", v) else v


def read_filters(profile_text: str) -> dict | None:
    """The `freehire_filters:` block from the frontmatter: `key: value`,
    `key: [a, b]` or `key:` followed by `- item` lines. None if absent."""
    m = re.search(r"^---\s*\n(.*?)^---\s*$", profile_text, re.S | re.M)
    fm = m.group(1) if m else ""
    b = re.search(r"^freehire_filters:\s*\n((?:[ \t]+.*\n?|\s*\n)*)", fm, re.M)
    if not b:
        return None
    out: dict = {}
    key = None
    for line in b.group(1).splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        item = re.match(r"\s+-\s*(.+)$", line)
        if item and key:
            out.setdefault(key, [])
            if isinstance(out[key], list):
                out[key].append(_scalar(item.group(1)))
            continue
        kv = re.match(r"\s+(\w+):\s*(.*)$", line)
        if kv:
            key = kv.group(1)
            out[key] = _scalar(kv.group(2)) if kv.group(2).strip() else []
    return out


def _as_list(v) -> list:
    return v if isinstance(v, list) else [v]


def validate(f: dict) -> list[str]:
    errs = []
    for k in f:
        if k not in KEYS:
            errs.append(f"unknown key '{k}' (allowed: {', '.join(sorted(KEYS))})")
    for k, enum in (("category", CATEGORIES), ("seniority", SENIORITY),
                    ("remote_regions", REGIONS), ("on_site_work_modes", WORK_MODES)):
        bad = [str(x) for x in _as_list(f.get(k, [])) if str(x).lower() not in enum]
        if bad:
            errs.append(f"{k}: not a Freehire value: {', '.join(bad)}")
    if "remote" in [str(x).lower() for x in _as_list(f.get("on_site_work_modes", []))]:
        errs.append("on_site_work_modes: 'remote' belongs in remote_regions")
    bad = [str(c) for c in _as_list(f.get("countries", [])) if not re.fullmatch(r"[A-Za-z]{2}", str(c))]
    if bad:
        errs.append(f"countries: not ISO 3166-1 alpha-2: {', '.join(bad)}")
    if not f.get("countries") and not f.get("remote_regions"):
        errs.append("set countries and/or remote_regions — without either the search is worldwide")
    if "salary_min" in f and not isinstance(f["salary_min"], int):
        errs.append("salary_min: must be a whole number")
    if "salary_min" in f and not re.fullmatch(r"[A-Z]{3}", str(f.get("salary_currency", ""))):
        errs.append("salary_currency: ISO 4217 code (e.g. EUR) required with salary_min")
    if not f.get("category"):
        errs.append("category: required (e.g. [product])")
    return errs


def search_sets(f: dict, open_within_days: int | None = None) -> list[dict]:
    """One search_jobs argument set per geography — never countries and regions
    together, since Freehire ORs them."""
    base: dict = {"category": [str(x).lower() for x in _as_list(f["category"])]}
    if f.get("seniority"):
        base["seniority"] = [str(x).lower() for x in _as_list(f["seniority"])]
    if "salary_min" in f:
        base["salary_min"] = f["salary_min"]
        base["salary_currency"] = f["salary_currency"]
    if open_within_days:
        base["posted_within_days"] = open_within_days
    sets = []
    if f.get("countries"):
        modes = _as_list(f.get("on_site_work_modes") or ["hybrid", "onsite", "remote"])
        sets.append({**base, "countries": [str(c).upper() for c in _as_list(f["countries"])],
                     "work_mode": [str(m).lower() for m in modes]})
    if f.get("remote_regions"):
        sets.append({**base, "regions": [str(r).lower() for r in _as_list(f["remote_regions"])],
                     "work_mode": ["remote"]})
    return sets


# ---------- screening ----------

def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    s = re.sub(r"\(.*?\)|\[.*?\]", " ", s)
    s = re.sub(r"\b(sr|snr)\b\.?", "senior", s)
    s = re.sub(r"\b(m/w/d|m/f/d|f/m/d|h/f|all genders)\b", " ", s)
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def norm_company(s: str) -> str:
    s = re.sub(r"\b(inc|ltd|gmbh|sl|sa|bv|plc|llc|ag|group|technologies|labs?)\b", "", norm(s))
    return " ".join(s.split())


def company_key(job: dict) -> str:
    """Company name for dedup: trailing words that also appear in the job's
    location are dropped, so "Gameloft Lisbon" and "Gameloft" match."""
    words = norm_company(_company(job)).split()
    loc = set(norm(" ".join(str(job.get(k) or "") for k in ("location", "city", "cities"))).split())
    while len(words) > 1 and words[-1] in loc:
        words.pop()
    return " ".join(words)


def _company(job: dict) -> str:
    c = job.get("company") or job.get("company_name") or ""
    return c.get("name", "") if isinstance(c, dict) else str(c)


def _url(job: dict) -> str:
    return job.get("official_job_url") or job.get("apply_url") or job.get("url") or ""


def is_job_board(job: dict) -> bool:
    """True when the posting came via a job board rather than the employer's
    ATS: by Freehire's `source` field (MCP previews carry only the Freehire page
    URL), else by the link's host."""
    src = str(job.get("source") or "").lower()
    if src:
        return any(src.startswith(b.rstrip(".")) for b in JOB_BOARDS)
    host = urlparse(_url(job)).netloc.lower()
    return not host or any(b in host for b in JOB_BOARDS)


def load_results(paths: list[Path]) -> tuple[list[dict], list[str]]:
    jobs, ignored = [], []
    for p in paths:
        data = json.loads(p.read_text())
        meta = (data.get("meta") or {}) if isinstance(data, dict) else {}
        for x in meta.get("ignored_params") or []:
            ignored.append(f"{p.name}: {x}")
        if isinstance(data, list):
            items = data
        else:
            items = next((data[k] for k in ("jobs", "results", "data", "items") if isinstance(data.get(k), list)), [])
        jobs.extend(items)
    return jobs, ignored


def tracked(userdata: Path) -> tuple[set, set, set]:
    keys, slugs, links = set(), set(), set()
    root = userdata / "companies"
    for p in list(root.glob("*/meta.md")) + list(root.glob("*/*/meta.md")):
        t = p.read_text()
        g = lambda k: (re.search(rf"^{k}:\s*\"?([^\"\n]*)\"?\s*$", t, re.M) or [None, ""])[1].strip()  # noqa: E731
        keys.add((norm_company(g("company") or p.parts[-2]), norm(g("position"))))
        if g("freehire_slug"):
            slugs.add(g("freehire_slug"))
        if g("link"):
            links.add(g("link").split("?")[0].rstrip("/"))
    seen = userdata / "outputs" / "seen-roles.jsonl"
    if seen.exists():
        for line in seen.read_text().splitlines():
            try:
                r = json.loads(line)
            except ValueError:
                continue
            if r.get("freehire_slug"):
                slugs.add(r["freehire_slug"])
            if r.get("link"):
                links.add(str(r["link"]).split("?")[0].rstrip("/"))
            if r.get("company") and (r.get("position") or r.get("title")):
                keys.add((norm_company(r["company"]), norm(r.get("position") or r.get("title"))))
    return keys, slugs, links


def screen(jobs: list[dict], userdata: Path, allow=None, deny=None, exclude=()) -> dict:
    patterns = ALLOW_PATTERNS if not allow else []
    allow = [norm(a) for a in (allow or DEFAULT_ALLOW)]
    deny = [norm(d) for d in (deny or DEFAULT_DENY)]
    excluded = {norm_company(c) for c in exclude} | AGENCIES
    keys, slugs, links = tracked(userdata)
    dropped: dict[str, list[str]] = {}
    best: dict[tuple, dict] = {}

    def drop(reason, job):
        dropped.setdefault(reason, []).append(f"{_company(job)} — {job.get('title', '')}")

    for job in jobs:
        title, company = norm(job.get("title", "")), company_key(job)
        url = _url(job).split("?")[0].rstrip("/")
        if any(d in title for d in deny) or not (any(a in title for a in allow)
                                                 or any(p.search(title) for p in patterns)):
            drop("title", job); continue
        if company in excluded or job.get("via_recruiter") is True:
            drop("agency", job); continue
        if (job.get("slug") in slugs or (url and url in links) or (company, title) in keys
                or (norm_company(_company(job)), title) in keys):
            drop("already tracked", job); continue
        k = (company, title)
        if k in best:
            # Prefer the employer's own ATS link over a job-board copy.
            if is_job_board(best[k]) and not is_job_board(job):
                drop("duplicate", best[k]); best[k] = job
            else:
                drop("duplicate", job)
            continue
        best[k] = job
    survivors = [{"company": _company(j), "title": j.get("title", ""), "freehire_slug": j.get("slug", ""),
                  "link": _url(j), "location": j.get("location", ""), "work_mode": j.get("work_mode", ""),
                  "reality": j.get("reality", ""), "source": j.get("source", "")} for j in best.values()]
    return {"survivors": survivors, "dropped": {k: len(v) for k, v in dropped.items()},
            "dropped_detail": dropped}


# ---------- CLI ----------

def detect(names: list[str]) -> str | None:
    for n in names:
        m = re.match(r"(mcp__freehire__)", n.strip(), re.I)
        if m:
            return m.group(1)
    return None


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("detect")
    f = sub.add_parser("filters")
    f.add_argument("--profile", type=Path, required=True)
    f.add_argument("--open-within-days", type=int)
    s = sub.add_parser("screen")
    s.add_argument("--userdata", type=Path, required=True)
    s.add_argument("--profile", type=Path)
    s.add_argument("results", type=Path, nargs="+")
    a = ap.parse_args(argv)

    if a.cmd == "detect":
        prefix = detect(sys.stdin.read().split())
        if not prefix:
            print("Freehire MCP not connected — use WebSearch Discovery.")
            return 1
        print(prefix)
        return 0

    profile = a.profile.read_text() if getattr(a, "profile", None) else ""
    filt = read_filters(profile) if profile else None

    if a.cmd == "filters":
        if filt is None:
            print("profile.md has no freehire_filters block.", file=sys.stderr)
            return 1
        errs = validate(filt)
        if errs:
            print("\n".join(f"freehire_filters: {e}" for e in errs), file=sys.stderr)
            return 1
        print(json.dumps(search_sets(filt, a.open_within_days), indent=2))
        return 0

    jobs, ignored = load_results(a.results)
    if ignored:
        print("Freehire ignored these parameters — the results are broader than asked. "
              "Fix the filter and search again:\n" + "\n".join(f"  {x}" for x in ignored), file=sys.stderr)
        return 3
    filt = filt or {}
    out = screen(jobs, a.userdata, filt.get("title_allow"), filt.get("title_deny"),
                 _as_list(filt.get("exclude_companies", [])))
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
