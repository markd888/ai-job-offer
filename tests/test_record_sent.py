"""plugin/scripts/record-sent.py — /sent records an application in one step.

The point of /sent is that a role marked applied gets a date, so follow-ups.py
finds it; the last test checks exactly that, end to end.
"""
from __future__ import annotations

import re
from datetime import date, timedelta

import pytest

from scripts_helpers import ROOT, run, write_meta

import sys
sys.path.insert(0, str(ROOT / "scripts"))
from validate_userdata import parse_frontmatter, validate_tree  # noqa: E402

TODAY = date(2026, 11, 16)


@pytest.fixture
def role(tmp_path):
    folder = tmp_path / "companies" / "Acme"
    write_meta(folder, company="Acme", position="Senior PM, Payments", status="to_apply",
               link="https://jobs.example.com/acme", tier="P1")
    (folder / "cv-2026-11-14.md").write_text("# Alex Example\n")
    (folder / "ats-check-2026-11-14.md").write_text("ATS: pass\n")
    return folder


def fm(role):
    return parse_frontmatter((role / "meta.md").read_text())


def history(role):
    return re.findall(r"^- .+$", (role / "meta.md").read_text().split("## History")[1], re.M)


def test_records_fields_archive_and_one_history_line(role, tmp_path):
    posting = tmp_path / "posting.txt"
    posting.write_text("We are hiring a Senior PM.")
    res = run("record-sent.py", role, "--channel", "referral", "--referred-by", "Dana Lee",
              "--posting", posting, "--date", "2026-11-16")
    assert res.returncode == 0, res.stderr
    f = fm(role)
    assert f["status"] == "applied"
    assert f["date_applied"] == "2026-11-16"
    assert f["channel"] == "referral"
    assert f["referred_by"] == "[[Dana Lee]]"
    assert f["last_activity"] == "2026-11-16"
    assert f["tier"] == "P1"  # untouched
    archive = role / "submitted-2026-11-16"
    assert {p.name for p in archive.iterdir()} >= {"cv-2026-11-14.md", "ats-check-2026-11-14.md",
                                                   "posting.md", "manifest.md"}
    assert "- Channel: referral" in (archive / "manifest.md").read_text()
    lines = history(role)
    assert lines[-1] == ("- 2026-11-16: status → applied via referral (referred by [[Dana Lee]]); "
                         "materials archived in submitted-2026-11-16/")
    assert len(lines) == 2  # 'created' + exactly one new line


def test_written_meta_passes_the_schema_check(role):
    assert run("record-sent.py", role, "--channel", "company-site").returncode == 0
    assert validate_tree(role.parent.parent) == []


def test_unknown_channel_is_refused_and_nothing_changes(role):
    before = (role / "meta.md").read_text()
    res = run("record-sent.py", role, "--channel", "carrier-pigeon")
    assert res.returncode != 0
    assert (role / "meta.md").read_text() == before
    assert not list(role.glob("submitted-*"))


def test_validator_flags_a_channel_outside_the_enum(tmp_path):
    write_meta(tmp_path / "companies" / "Acme", company="Acme", position="PM", status="applied",
               link="https://x.example/1", channel="email")
    rules = [f.rule for f in validate_tree(tmp_path)]
    assert rules == ["meta.channel-enum"]


@pytest.mark.parametrize("status", ["interviewing", "offer", "rejected", "not_interested"])
def test_refuses_a_role_past_the_application(tmp_path, status):
    folder = tmp_path / "companies" / "Acme"
    write_meta(folder, company="Acme", position="PM", status=status, link="https://x.example/1")
    before = (folder / "meta.md").read_text()
    res = run("record-sent.py", folder, "--channel", "linkedin")
    assert res.returncode != 0 and status in res.stderr
    assert (folder / "meta.md").read_text() == before


def test_refuses_a_second_record_without_force(role):
    assert run("record-sent.py", role, "--channel", "linkedin", "--date", "2026-11-10").returncode == 0
    again = run("record-sent.py", role, "--channel", "linkedin", "--date", "2026-11-12")
    assert again.returncode != 0 and "2026-11-10" in again.stderr
    assert fm(role)["date_applied"] == "2026-11-10"
    forced = run("record-sent.py", role, "--channel", "recruiter", "--date", "2026-11-12", "--force")
    assert forced.returncode == 0, forced.stderr
    assert fm(role)["date_applied"] == "2026-11-12" and fm(role)["channel"] == "recruiter"


def test_applied_without_a_date_gets_one(tmp_path):
    folder = tmp_path / "companies" / "Acme"
    write_meta(folder, company="Acme", position="PM", status="applied", link="https://x.example/1")
    res = run("record-sent.py", folder, "--channel", "cold", "--date", "2026-11-03")
    assert res.returncode == 0, res.stderr
    assert fm(folder)["date_applied"] == "2026-11-03"


def test_without_a_cv_it_records_and_says_nothing_was_archived(tmp_path):
    folder = tmp_path / "companies" / "Acme"
    write_meta(folder, company="Acme", position="PM", status="new", link="https://x.example/1")
    res = run("record-sent.py", folder, "--channel", "linkedin", "--date", "2026-11-16")
    assert res.returncode == 0, res.stderr
    assert "nothing was archived" in res.stdout
    assert fm(folder)["status"] == "applied"
    assert history(folder)[-1].endswith("no CV in the folder, nothing archived")


def test_a_sent_role_comes_up_for_follow_up_after_ten_days(role):
    sent_on = (TODAY - timedelta(days=10)).isoformat()
    assert run("record-sent.py", role, "--channel", "company-site", "--date", sent_on).returncode == 0
    userdata = role.parent.parent
    res = run("follow-ups.py", "--userdata", userdata, "--today", TODAY.isoformat())
    due = res.stdout.split("## Close instead")[0]
    assert "- Acme — Senior PM, Payments — applied, quiet 10d" in due
    assert "follow-ups 0/2, archive —" in due  # the archive /sent made is seen

    early = run("follow-ups.py", "--userdata", userdata, "--today", (TODAY - timedelta(days=1)).isoformat())
    assert "Acme" not in early.stdout
