"""Funnel by application channel (plugin/scripts/funnel.py): the numbers the
dashboard, career-coach and /today's weekly reflection all quote."""
from __future__ import annotations

from scripts_helpers import ROOT, load, run

funnel = load("funnel.py")


def role(status, channel="", **kw):
    return {"status": status, "channel": channel, **kw}


def rows(roles):
    return {r["channel"]: r for r in funnel.funnel_by_channel(roles)["rows"]}


def test_empty_pipeline_has_no_rows():
    assert funnel.funnel_by_channel([]) == {"min_sample": 5, "rows": []}
    # Roles never applied to don't count anywhere.
    assert funnel.funnel_by_channel([role("new", "referral"), role("to_apply")])["rows"] == []


def test_one_channel_counts_cumulatively_and_rates_from_applied():
    roles = ([role("applied", "cold")] * 6
             + [role("rejected", "cold", rejection_stage="screening")] * 2
             + [role("interviewing", "cold", max_stage="interview")]
             + [role("offer", "cold")])
    r = rows(roles)["cold"]
    assert (r["applied"], r["screening"], r["interview"], r["final"], r["offer"]) == (10, 4, 2, 1, 1)
    assert (r["screening_rate"], r["interview_rate"], r["offer_rate"]) == (0.4, 0.2, 0.1)
    assert r["small_sample"] is False


def test_missing_or_unknown_channel_goes_to_unknown_and_sorts_last():
    roles = [role("applied")] * 7 + [role("applied", "carrier-pigeon")] + [role("applied", "referral")] * 5
    result = funnel.funnel_by_channel(roles)["rows"]
    assert [r["channel"] for r in result] == ["referral", "unknown"]
    assert result[1]["applied"] == 8


def test_small_sample_keeps_counts_but_drops_rates():
    r = rows([role("offer", "referral")] * 4)["referral"]
    assert r["applied"] == 4 and r["offer"] == 4 and r["small_sample"] is True
    assert r["screening_rate"] is r["offer_rate"] is None


def test_stage_matches_the_dashboard_funnel_rules():
    assert funnel.stage_reached(role("interviewing")) == "screening"
    assert funnel.stage_reached(role("interviewing", max_stage="final")) == "final"
    assert funnel.stage_reached(role("not_interested", max_stage="interview")) == "interview"
    assert funnel.stage_reached(role("not_interested", date_applied="2026-01-01")) == "applied"
    assert funnel.stage_reached(role("not_interested")) is None
    assert funnel.stage_reached(role("rejected", rejection_stage="final", max_stage="screening")) == "final"


def test_cli_on_maya_quotes_counts_and_withholds_small_rates():
    res = run("funnel.py", "--userdata", ROOT / "tests" / "snapshots" / "maya-active")
    assert res.returncode == 0, res.stderr
    assert "- company-site: 7 applied → 0 screening (0%)" in res.stdout
    assert "- referral: 1 applied → 1 screening, 1 interview, 1 final, 1 offer — under 5 applications" in res.stdout
    assert "- unknown (channel not recorded): 1 applied" in res.stdout


def test_career_coach_and_today_quote_the_script_not_their_own_numbers():
    coach = (ROOT / "plugin" / "agents" / "career-coach.md").read_text()
    # /today's channel line lives in the weekly-reflection reference it loads on demand.
    today = (ROOT / "plugin" / "references" / "today-weekly-reflection.md").read_text()
    assert "today-weekly-reflection.md" in (ROOT / "plugin" / "skills" / "today" / "SKILL.md").read_text()
    assert "scripts/funnel.py" in coach and "scripts/funnel.py" in today
    assert "fewer than 5 applications" in coach and "too few to read" in coach
    assert "Never a rate the script didn't print" in today

