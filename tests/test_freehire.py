"""plugin/scripts/freehire.py — MCP detection, profile filters, ignored_params
guard, title/agency screening and dedup.

The search fixture is shaped like the 2026-11-19 probe (issue #26): the same
role from LinkedIn and the employer's ATS, Product Owner / BA noise, recruiter
reposts, and one role already in the pipeline.
"""
from __future__ import annotations

import json

import pytest

from scripts_helpers import load, run, write_meta

fh = load("freehire.py")

PROFILE = """---
name: Test
target_titles:
  - Senior Product Manager
freehire_filters:
  category: [product]
  seniority:
    - senior
    - lead
  countries: [ES]
  remote_regions: [eu, global]
  salary_min: 70000
  salary_currency: EUR
---

## Positioning
x
"""


def job(company, title, url, slug, **kw):
    return {"company": company, "title": title, "official_job_url": url, "slug": slug, **kw}


PROBE = {
    "jobs": [
        job("Gameloft", "Senior Product Manager", "https://www.linkedin.com/jobs/view/1", "gl-li"),
        job("Gameloft", "Senior Product Manager", "https://gameloft.wd3.myworkdayjobs.com/x/2", "gl-ats"),
        job("Proton", "Senior Product Manager (m/f/d)", "https://job-boards.greenhouse.io/proton/1", "pr-1"),
        job("BVNK", "Product Manager, Reconciliation", "https://jobs.ashbyhq.com/bvnk/1", "bvnk-1"),
        job("Viseven", "Product Owner", "https://viseven.com/careers/1", "vs-po"),
        job("Acme", "Business Analyst - Payments", "https://acme.com/1", "acme-ba"),
        job("Delivery Hero", "Agile Coach", "https://dh.com/1", "dh-agile"),
        job("Jobgether", "Senior Product Manager - Fintech", "https://jobgether.com/1", "jg-1"),
        job("GemPool", "Lead Product Manager", "https://gempool.io/1", "gp-1"),
        job("Panggea", "Area Product Manager", "https://panggea.com/1", "pg-area"),
        job("Nebius", "Senior Product Manager", "https://nebius.com/careers/9", "nb-9"),
    ],
    "meta": {"total": 11, "ignored_params": []},
}


@pytest.fixture
def userdata(tmp_path):
    (tmp_path / "companies").mkdir()
    write_meta(tmp_path / "companies" / "Nebius", company="Nebius", position="Senior Product Manager",
               status="interviewing", link="https://nebius.com/careers/1")
    (tmp_path / "profile.md").write_text(PROFILE)
    return tmp_path


# ---------- detect ----------

@pytest.mark.parametrize("name", ["mcp__freehire__search_jobs", "mcp__Freehire__search_jobs",
                                  "MCP__FREEHIRE__get_job"])
def test_detect_is_case_insensitive(name):
    assert fh.detect(["mcp__granola__x", name]).lower() == "mcp__freehire__"


def test_detect_absent_exits_1():
    r = run("freehire.py", "detect")
    assert r.returncode == 1 and "WebSearch" in r.stdout


# ---------- filters ----------

def test_filters_split_country_and_region(userdata):
    r = run("freehire.py", "filters", "--profile", userdata / "profile.md", "--open-within-days", "7")
    assert r.returncode == 0, r.stderr
    sets = json.loads(r.stdout)
    assert len(sets) == 2
    assert all(not ("countries" in s and "regions" in s) for s in sets)
    assert sets[0]["countries"] == ["ES"] and sets[1]["work_mode"] == ["remote"]
    assert sets[0]["seniority"] == ["senior", "lead"] and sets[0]["posted_within_days"] == 7


@pytest.mark.parametrize("patch, msg", [
    ({"seniority": ["sneior"]}, "seniority"),
    ({"remote_regions": ["europe"]}, "remote_regions"),
    ({"countries": ["Spain"]}, "alpha-2"),
    ({"categroy": ["product"]}, "unknown key"),
    ({"salary_currency": "euro"}, "ISO 4217"),
    ({"on_site_work_modes": ["remote"]}, "remote_regions"),
])
def test_validate_rejects_typos(patch, msg):
    f = {"category": ["product"], "countries": ["ES"], "salary_min": 70000, "salary_currency": "EUR", **patch}
    assert any(msg in e for e in fh.validate(f))


def test_validate_requires_geography():
    assert any("worldwide" in e for e in fh.validate({"category": ["product"]}))


def test_profile_without_block_exits_1(tmp_path):
    p = tmp_path / "profile.md"
    p.write_text("---\nname: x\n---\n")
    assert run("freehire.py", "filters", "--profile", p).returncode == 1


# ---------- screen ----------

def screen(userdata, tmp_path, data):
    f = tmp_path / "res.json"
    f.write_text(json.dumps(data))
    return run("freehire.py", "screen", "--userdata", userdata, "--profile", userdata / "profile.md", f)


def test_ignored_params_guard_stops(userdata, tmp_path):
    data = {**PROBE, "meta": {"ignored_params": ["seniorty"]}}
    r = screen(userdata, tmp_path, data)
    assert r.returncode == 3 and "seniorty" in r.stderr and r.stdout == ""


def test_screen_probe_fixture(userdata, tmp_path):
    r = screen(userdata, tmp_path, PROBE)
    assert r.returncode == 0, r.stderr
    out = json.loads(r.stdout)
    got = {(s["company"], s["freehire_slug"]) for s in out["survivors"]}
    assert got == {("Gameloft", "gl-ats"), ("Proton", "pr-1"), ("BVNK", "bvnk-1")}
    assert out["dropped"] == {"duplicate": 1, "title": 4, "agency": 2, "already tracked": 1}


def test_duplicate_keeps_ats_even_when_board_comes_second(userdata, tmp_path):
    data = {"jobs": [PROBE["jobs"][1], PROBE["jobs"][0]], "meta": {}}
    out = json.loads(screen(userdata, tmp_path, data).stdout)
    assert [s["freehire_slug"] for s in out["survivors"]] == ["gl-ats"]


def test_seen_ledger_and_slug_dedup(userdata, tmp_path):
    (userdata / "outputs").mkdir()
    (userdata / "outputs" / "seen-roles.jsonl").write_text(json.dumps({"freehire_slug": "pr-1"}) + "\n")
    write_meta(userdata / "companies" / "BVNK", company="BVNK", position="Other role", status="new",
               freehire_slug="bvnk-1")
    out = json.loads(screen(userdata, tmp_path, PROBE).stdout)
    assert {s["company"] for s in out["survivors"]} == {"Gameloft"}


def test_validate_userdata_flags_bad_freehire_filters(tmp_path):
    import subprocess
    import sys

    from scripts_helpers import ROOT
    (tmp_path / "profile.md").write_text(PROFILE.replace("- lead", "- sneior"))
    r = subprocess.run([sys.executable, "-I", str(ROOT / "scripts" / "validate_userdata.py"), str(tmp_path)],
                       capture_output=True, text=True)
    assert "profile.freehire-filters" in r.stdout + r.stderr and "sneior" in r.stdout + r.stderr


def test_duplicate_preference_uses_source_field(userdata, tmp_path):
    """MCP previews only carry the Freehire page URL; `source` decides."""
    a = job("Gameloft", "Senior Product Manager", "https://freehire.me/jobs/a", "a", source="linkedin")
    b = job("Gameloft", "Senior Product Manager", "https://freehire.me/jobs/b", "b", source="workday")
    out = json.loads(screen(userdata, tmp_path, {"jobs": [a, b]}).stdout)
    assert [s["freehire_slug"] for s in out["survivors"]] == ["b"]
