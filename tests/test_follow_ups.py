"""plugin/scripts/follow-ups.py — which quiet applications are due a follow-up.

All dates are relative to a pinned --today so the rules (10 days quiet, 30 days
to close, at most two follow-ups) are tested at their boundaries.
"""
from __future__ import annotations

import re
from datetime import date, timedelta

import pytest

from scripts_helpers import run, write_meta

TODAY = date(2026, 11, 16)


def ago(days: int) -> str:
    return (TODAY - timedelta(days=days)).isoformat()


@pytest.fixture
def userdata(tmp_path):
    (tmp_path / "companies").mkdir()
    return tmp_path


def add(userdata, folder: str, *, company: str | None = None, status: str = "applied", **fields):
    name = company or folder.split("/")[0]
    return write_meta(userdata / "companies" / folder, company=name, position="Senior PM", status=status,
                      link=f"https://jobs.example.com/{folder}", **fields)


def sections(out: str) -> tuple[list[str], list[str]]:
    """Company names listed under 'Follow-up due' and 'Close instead', in order."""
    due_part, _, close_part = out.partition("## Close instead")
    names = lambda part: re.findall(r"^- (.+?) — ", part, re.M)  # noqa: E731
    return names(due_part), names(close_part)


def follow_ups(userdata, *extra: str):
    res = run("follow-ups.py", "--userdata", userdata, "--today", TODAY.isoformat(), *extra)
    assert res.returncode == 0, res.stderr
    return res.stdout


def test_quiet_window_boundaries(userdata):
    add(userdata, "Fresh", date_applied=ago(9))
    add(userdata, "Exactly10", date_applied=ago(10))
    add(userdata, "Exactly30", date_applied=ago(30))
    add(userdata, "Over30", date_applied=ago(31))
    due, close = sections(follow_ups(userdata))
    assert due == ["Exactly10", "Exactly30"]
    assert close == ["Over30"]


def test_due_list_is_most_recent_first(userdata):
    add(userdata, "Older", date_applied=ago(25))
    add(userdata, "Newer", date_applied=ago(11))
    add(userdata, "Middle", date_applied=ago(18))
    due, _ = sections(follow_ups(userdata))
    assert due == ["Newer", "Middle", "Older"]


def test_latest_of_applied_inbound_and_follow_up_restarts_the_clock(userdata):
    add(userdata, "Inbound", date_applied=ago(40), last_inbound=ago(3))
    add(userdata, "FollowedUp", date_applied=ago(40), last_follow_up=ago(5), follow_ups=1)
    add(userdata, "StillQuiet", date_applied=ago(40), last_follow_up=ago(12), follow_ups=1)
    due, close = sections(follow_ups(userdata))
    assert due == ["StillQuiet"]
    assert close == []


def test_two_follow_ups_sent_means_close(userdata):
    add(userdata, "Chased", date_applied=ago(25), last_follow_up=ago(11), follow_ups=2)
    due, close = sections(follow_ups(userdata))
    assert due == [] and close == ["Chased"]


def test_unknown_company_goes_to_close(userdata):
    add(userdata, "unknown-1", company="Unknown (ATS email)", date_applied=ago(12))
    due, close = sections(follow_ups(userdata))
    assert due == [] and close == ["Unknown (ATS email)"]


def test_interviewing_with_upcoming_event_is_skipped(userdata):
    add(userdata, "Booked", status="interviewing", date_applied=ago(20), next_event='"R2 panel Fri 2026-11-20"')
    add(userdata, "Waiting", status="interviewing", date_applied=ago(20))
    due, close = sections(follow_ups(userdata))
    assert due == ["Waiting"] and close == []


@pytest.mark.parametrize("status", ["new", "to_apply", "offer", "rejected", "not_interested"])
def test_other_statuses_are_ignored(userdata, status):
    add(userdata, "Other", status=status, date_applied=ago(20))
    assert sections(follow_ups(userdata)) == ([], [])


def test_role_without_any_date_is_ignored(userdata):
    add(userdata, "Undated")
    assert sections(follow_ups(userdata)) == ([], [])


def test_multi_role_company_folders_are_read(userdata):
    add(userdata, "Plaid/senior-pm-credit", company="Plaid", date_applied=ago(12))
    out = follow_ups(userdata)
    assert sections(out)[0] == ["Plaid"]
    assert "companies/Plaid/senior-pm-credit" in out


def test_company_filter_is_case_insensitive_substring(userdata):
    add(userdata, "Stripe", date_applied=ago(12))
    add(userdata, "Adyen", date_applied=ago(12))
    due, _ = sections(follow_ups(userdata, "--company", "strip"))
    assert due == ["Stripe"]


def test_custom_thresholds(userdata):
    add(userdata, "Seven", date_applied=ago(7))
    add(userdata, "Twenty", date_applied=ago(20))
    due, close = sections(follow_ups(userdata, "--days", "7", "--close-after", "14"))
    assert due == ["Seven"] and close == ["Twenty"]


def test_junk_follow_up_count_does_not_crash(userdata):
    add(userdata, "Messy", date_applied=ago(12), follow_ups='"one?"')
    due, _ = sections(follow_ups(userdata))
    assert due == ["Messy"]


def test_reports_archive_presence(userdata):
    add(userdata, "Archived", date_applied=ago(12))
    sub = userdata / "companies" / "Archived" / "submitted-2026-11-04"
    sub.mkdir()
    (sub / "manifest.md").write_text("# Submitted\n")
    add(userdata, "Bare", date_applied=ago(13))
    out = follow_ups(userdata)
    assert re.search(r"^- Archived .*, archive —", out, re.M)
    assert re.search(r"^- Bare .*, no archive —", out, re.M)


def test_is_read_only(userdata):
    meta = add(userdata, "Stripe", date_applied=ago(12))
    before = {p: p.read_bytes() for p in userdata.rglob("*") if p.is_file()}
    follow_ups(userdata)
    after = {p: p.read_bytes() for p in userdata.rglob("*") if p.is_file()}
    assert before == after
    assert meta in after
