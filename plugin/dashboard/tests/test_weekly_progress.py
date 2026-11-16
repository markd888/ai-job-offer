"""Tests for count_warm_outreach (people logs) / count_recent_applications / count_feedback_requests.

Window is the current ISO week: [Monday of this week, today] inclusive.
TODAY is fixed to Friday 2026-05-15 so the window is Mon 2026-05-11 → Fri 2026-05-15.
Anything before 2026-05-11 or after 2026-05-15 is out of window.
"""
from __future__ import annotations

from datetime import date
from textwrap import dedent

from serve import count_feedback_requests, count_recent_applications, count_warm_outreach, compute_weekly_progress


TODAY = date(2026, 5, 15)  # Friday — week runs Mon 2026-05-11 through Fri 2026-05-15.


# ----- count_warm_outreach (userdata/people/*.md logs) ------------------------


def _person(root, slug, *log_lines, relation="former-colleague"):
    d = root / "people"
    d.mkdir(exist_ok=True)
    (d / f"{slug}.md").write_text(
        f"---\nname: {slug.title()}\nrelation: {relation}\nroles: []\n---\n\n# {slug.title()}\n\n## Log\n"
        + "".join(line + "\n" for line in log_lines)
    )


def test_no_people_folder_counts_zero(tmp_path):
    assert count_warm_outreach(tmp_path, TODAY) == 0


def test_sent_outreach_kinds_in_window_counted(tmp_path):
    _person(tmp_path, "dana",
            "- 2026-05-11 sent reach-out (linkedin): Catch-up ask.",          # Monday — counts
            "- 2026-05-13 sent referral-ask (linkedin): Referral for Senior PM.",  # counts
            "- 2026-05-14 received reply (linkedin): Said yes.",              # theirs — no
            "- 2026-05-15 sent thank-you (linkedin): Thanks for the referral.")  # not outreach
    _person(tmp_path, "sam",
            "- 2026-05-12 sent intro-ask (email): Intro to the Head of Credit.",   # counts
            "- 2026-05-14 sent follow-up (email): Nudge on the intro.",           # counts
            "- 2026-05-14 sent feedback-ask (email): Asked why not.")             # not outreach
    assert count_warm_outreach(tmp_path, TODAY) == 4


def test_outreach_outside_window_not_counted(tmp_path):
    _person(tmp_path, "dana",
            "- 2026-05-10 sent reach-out (linkedin): Sunday of last week.",
            "- 2026-05-16 sent reach-out (linkedin): Tomorrow.")
    assert count_warm_outreach(tmp_path, TODAY) == 0


def test_malformed_log_lines_are_not_counted(tmp_path):
    _person(tmp_path, "dana",
            "- 2026-05-13 messaged Dana about a referral",        # free text, no kind
            "- 2026-05-13 sent coffee (linkedin): Unknown kind.",  # kind not in the enum
            "- 13/05/2026 sent reach-out: Wrong date format.")
    assert count_warm_outreach(tmp_path, TODAY) == 0


def test_journal_wording_no_longer_counts(tmp_path):
    (tmp_path / "journal.md").write_text("## 2026-05-13\n- Outreach sent on LinkedIn to 4 people. DM to Jo.\n")
    assert compute_weekly_progress(tmp_path, [], today=TODAY)["warm_outreach"] == 0


# ----- count_recent_applications ---------------------------------------------


def test_application_in_window_counted():
    companies = [{"date_applied": "2026-05-13"}]
    assert count_recent_applications(companies, TODAY) == 1


def test_application_at_week_boundaries_counted():
    companies = [
        {"date_applied": "2026-05-11"},  # Monday — week start
        {"date_applied": "2026-05-15"},  # Friday — today
    ]
    assert count_recent_applications(companies, TODAY) == 2


def test_application_outside_window_not_counted():
    companies = [
        {"date_applied": "2026-05-10"},  # Sunday of previous week
        {"date_applied": "2026-05-16"},  # Saturday — tomorrow
    ]
    assert count_recent_applications(companies, TODAY) == 0


def test_missing_or_malformed_dates_skipped():
    companies = [
        {},
        {"date_applied": ""},
        {"date_applied": "not-a-date"},
        {"date_applied": "2026-05-13"},
    ]
    assert count_recent_applications(companies, TODAY) == 1


# ----- compute_weekly_progress ----------------------------------------------


def test_window_days_matches_position_in_iso_week(tmp_path):
    # Monday → 1, Wednesday → 3, Sunday → 7.
    cases = [
        (date(2026, 5, 18), 1),  # Monday
        (date(2026, 5, 20), 3),  # Wednesday
        (date(2026, 5, 24), 7),  # Sunday
    ]
    for today, expected in cases:
        out = compute_weekly_progress(tmp_path, [], today=today)
        assert out["window_days"] == expected, f"{today}: expected {expected}, got {out['window_days']}"


# ----- count_feedback_requests ------------------------------------------------


def test_feedback_requests_counted_in_window_only():
    journal = dedent(
        """\
        ## 2026-05-08
        - [Old] Feedback request sent by email to the recruiter. (source: user)

        ## 2026-05-13
        - [Monzo] Feedback request sent by email to Chloe on the EU rejection. (source: user)
        - [Tabby] Messaged Aleksandr: referral ask, plus asked for feedback on the rejection. (source: user)
        """
    )
    assert count_feedback_requests(journal, TODAY) == 2


def test_feedback_given_or_promised_is_not_a_request():
    journal = dedent(
        """\
        ## 2026-05-13
        - [Payment Genes] James will give feedback on the CV by the end of the week. (source: user)
        - [Rooh] Rejected after the tech check (Alena, written feedback). (source: user)
        """
    )
    assert count_feedback_requests(journal, TODAY) == 0
