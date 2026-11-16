"""The application-to-interview journey's field chain, through the real scripts.

The harness journey (.claude/skills/test-personas/journeys/application-to-interview.md)
judges the conversation; this checks the part a script can: each step writes
the fields the next step reads, and ten days on the clock is what moves a role
onto the follow-up list.

    /sent  →  10 days  →  follow-ups.py lists it  →  follow-up recorded
           →  reply via record-inbound.py  →  off the list  →  interviewing
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
from datetime import date, timedelta

import pytest

from scripts_helpers import ROOT, load, run
from validate_userdata import validate_tree

mf = load("metafile.py")
TODAY = date.today()
DAY0 = TODAY - timedelta(days=10)


@pytest.fixture
def userdata(tmp_path):
    ud = tmp_path / "userdata"
    shutil.copytree(ROOT / "tests" / "snapshots" / "maya-active", ud)
    role = ud / "companies" / "Zopa"
    (role / "cv-2026-08-03.md").write_text("# Maya Patel\n\nSenior PM, consumer credit.\n")
    (role / "ats-check-2026-08-03.md").write_text("# ATS check\n\nPASS — 1 page.\n")
    return ud


def meta(ud):
    return (ud / "companies" / "Zopa" / "meta.md").read_text()


def due(ud) -> str:
    res = run("follow-ups.py", "--userdata", ud, "--today", TODAY.isoformat())
    assert res.returncode == 0, res.stderr
    return res.stdout.split("## Close instead")[0]


def time_skip(ud, days: int):
    res = subprocess.run([sys.executable, str(ROOT / "scripts" / "rebase_fixture_dates.py"),
                          "--time-skip", str(days), "--root", str(ud)], capture_output=True, text=True)
    assert res.returncode == 0, res.stderr


def test_the_chain_from_sent_to_interviewing(userdata):
    role = userdata / "companies" / "Zopa"

    # /sent, today. Recorded, archived, and not yet due.
    res = run("record-sent.py", role, "--channel", "company-site", "--date", TODAY.isoformat())
    assert res.returncode == 0, res.stdout + res.stderr
    m = meta(userdata)
    assert (mf.field(m, "status"), mf.field(m, "channel"), mf.field(m, "date_applied")) == \
        ("applied", "company-site", TODAY.isoformat())
    archive = role / f"submitted-{TODAY.isoformat()}"
    assert {"cv-2026-08-03.md", "ats-check-2026-08-03.md"} <= {p.name for p in archive.iterdir()}
    assert "Zopa" not in due(userdata)

    # Ten days pass. The application date is now today − 10, and it is due.
    time_skip(userdata, 10)
    assert mf.field(meta(userdata), "date_applied") == DAY0.isoformat()
    assert (role / f"submitted-{DAY0.isoformat()}").is_dir()
    assert re.search(r"Zopa .* applied, quiet 10d, follow-ups 0/2", due(userdata))

    # /follow-up step 4, after "sent it by email": the skill's own writes.
    m = mf.set_fields(meta(userdata), {"follow_ups": "1", "last_follow_up": TODAY.isoformat()})
    m = mf.append_history(m, f"- {TODAY}: follow-up #1 sent via email to hiring team")
    (role / "meta.md").write_text(m)
    assert "Zopa" not in due(userdata), "a follow-up sent today restarts the quiet clock"

    # The reply.
    res = run("record-inbound.py", role, "--date", TODAY.isoformat(),
              "--what", "reply from the recruiter (screen Thursday 14:00)", "--source", "user")
    assert res.returncode == 0, res.stderr
    m = meta(userdata)
    assert mf.field(m, "last_inbound") == TODAY.isoformat()
    assert mf.field(m, "status") == "applied", "a reply alone never changes status"
    assert "reply from the recruiter" in m

    # "mark Zopa as interviewing"
    m = mf.set_fields(m, {"status": "interviewing", "last_activity": TODAY.isoformat()})
    (role / "meta.md").write_text(mf.append_history(m, f"- {TODAY}: status → interviewing (recruiter screen booked)"))
    assert "Zopa" not in due(userdata)

    assert [f for f in validate_tree(userdata) if "Zopa" in f.path] == []


def test_time_skip_leaves_test_runs_and_examples_alone(tmp_path):
    ud = tmp_path / "userdata"
    for sub in ("companies/X", "test-runs/2026-08-03", "examples/maya"):
        (ud / sub).mkdir(parents=True)
        (ud / sub / "note.md").write_text("date_applied: 2026-08-03\n")
    time_skip(ud, 10)
    assert (ud / "companies/X/note.md").read_text() == "date_applied: 2026-07-24\n"
    for sub in ("test-runs/2026-08-03", "examples/maya"):
        assert (ud / sub / "note.md").read_text() == "date_applied: 2026-08-03\n"


def test_journey_is_wired_into_the_harness():
    harness = ROOT / ".claude" / "skills" / "test-personas"
    journey = (harness / "journeys" / "application-to-interview.md").read_text()
    assert "--time-skip 10 --root userdata" in journey
    assert "application-to-interview" in (harness / "SKILL.md").read_text()
    assert "application-to-interview" in (harness / "personas" / "maya.md").read_text()
