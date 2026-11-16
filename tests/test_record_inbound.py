"""plugin/scripts/record-inbound.py — last_inbound, the other half of the quiet clock.

follow-ups.py is the single quiet-application rule (/today uses its output);
these tests check that recording contact from the company is what takes a role
off that list, including on the maya-active snapshot.
"""
from __future__ import annotations

import re
import shutil
from datetime import date, timedelta

import pytest

from scripts_helpers import ROOT, run, write_meta

import sys
sys.path.insert(0, str(ROOT / "scripts"))
from validate_userdata import parse_frontmatter, validate_tree  # noqa: E402

TODAY = date(2026, 11, 16)
SNAPSHOT = ROOT / "tests" / "snapshots" / "maya-active"
SNAPSHOT_TODAY = "2026-08-05"


def ago(days: int, today: date = TODAY) -> str:
    return (today - timedelta(days=days)).isoformat()


@pytest.fixture
def role(tmp_path):
    folder = tmp_path / "companies" / "Acme"
    write_meta(folder, company="Acme", position="Senior PM", status="applied",
               link="https://jobs.example.com/acme", date_applied=ago(20), last_activity=ago(20))
    return folder


def fm(role):
    return parse_frontmatter((role / "meta.md").read_text())


def due_companies(userdata, today: str) -> list[str]:
    res = run("follow-ups.py", "--userdata", userdata, "--today", today)
    assert res.returncode == 0, res.stderr
    return re.findall(r"^- (.+?) — ", res.stdout.split("## Close instead")[0], re.M)


def test_sets_last_inbound_activity_and_one_history_line(role):
    res = run("record-inbound.py", role, "--what", "reply from Dana  (recruiter)",
              "--date", ago(3), "--source", "gmail")
    assert res.returncode == 0, res.stderr
    f = fm(role)
    assert f["last_inbound"] == ago(3) and f["last_activity"] == ago(3)
    assert f["status"] == "applied"  # never touched
    assert (role / "meta.md").read_text().rstrip().endswith(
        f"- {ago(3)}: inbound — reply from Dana (recruiter) (gmail)")
    assert validate_tree(role.parent.parent) == []


def test_never_moves_dates_backwards(role):
    assert run("record-inbound.py", role, "--what", "call", "--date", ago(2)).returncode == 0
    res = run("record-inbound.py", role, "--what", "older email", "--date", ago(5))
    assert res.returncode == 0 and "stays" in res.stdout
    assert fm(role)["last_inbound"] == ago(2) and fm(role)["last_activity"] == ago(2)
    assert f"- {ago(5)}: inbound — older email (user)" in (role / "meta.md").read_text()


def test_bad_date_or_source_changes_nothing(role):
    before = (role / "meta.md").read_text()
    assert run("record-inbound.py", role, "--what", "x", "--date", "16/11/2026").returncode != 0
    assert run("record-inbound.py", role, "--what", "x", "--source", "pigeon").returncode != 0
    assert (role / "meta.md").read_text() == before


def test_reply_three_days_ago_suppresses_the_follow_up(role):
    userdata = role.parent.parent
    assert due_companies(userdata, TODAY.isoformat()) == ["Acme"]
    assert run("record-inbound.py", role, "--what", "reply", "--date", ago(3)).returncode == 0
    assert due_companies(userdata, TODAY.isoformat()) == []
    # ...and the clock restarts from the reply, not from the application.
    assert due_companies(userdata, ago(-7)) == ["Acme"]


def test_snapshot_inbound_reply_suppresses_the_follow_up(tmp_path):
    """maya-active: iwoca is due on the snapshot date; a reply 3 days earlier takes it off."""
    userdata = tmp_path / "maya-active"
    shutil.copytree(SNAPSHOT, userdata)
    today = date.fromisoformat(SNAPSHOT_TODAY)
    before = due_companies(userdata, SNAPSHOT_TODAY)
    assert "iwoca" in before

    iwoca = userdata / "companies" / "iwoca"
    res = run("record-inbound.py", iwoca, "--what", "reply from the recruiter", "--date", ago(3, today))
    assert res.returncode == 0, res.stderr
    after = due_companies(userdata, SNAPSHOT_TODAY)
    assert after == [c for c in before if c != "iwoca"]
    assert validate_tree(userdata) == validate_tree(SNAPSHOT)


def test_record_sent_and_record_inbound_share_one_clock(tmp_path):
    folder = tmp_path / "companies" / "Acme"
    write_meta(folder, company="Acme", position="PM", status="to_apply", link="https://x.example/1")
    assert run("record-sent.py", folder, "--channel", "linkedin", "--date", ago(15)).returncode == 0
    assert due_companies(tmp_path, TODAY.isoformat()) == ["Acme"]
    assert run("record-inbound.py", folder, "--what", "screen invite", "--date", ago(1)).returncode == 0
    assert due_companies(tmp_path, TODAY.isoformat()) == []
