"""Rules added after the 2026-11-16 harness run, one per gate finding
(tests/judge-calibration/runs/2026-11-16/SUMMARY.md)."""
from scripts_helpers import ROOT

SKILLS = ROOT / "plugin" / "skills"


def test_status_change_confirmation_keeps_the_posting_link():
    # cold-start turn 19: "Marked Lendable — … as one to apply for." with no URL.
    text = (SKILLS / "dashboard" / "SKILL.md").read_text()
    assert "as one to apply for — <link>" in text


def test_interview_prep_always_closes_with_the_interview_nudge():
    # active-loop turn 8: the closing asked about the application instead.
    text = (SKILLS / "interview-prep" / "SKILL.md").read_text()
    end = text[text.index("## End-of-run nudge"):]
    assert "/job-offer:interview-analysis <Co>" in end
    assert "never stands in for the interview nudge" in end


def test_apply_offers_to_save_a_phone_instead_of_asking_for_a_hand_edit():
    # application-to-interview turn 3: "add a `phone:` line to profile.md".
    text = (SKILLS / "apply" / "SKILL.md").read_text()
    assert "Want me to keep that number for your next CVs too?" in text
    assert "Never tell the user to edit a file or add a field themselves" in text
