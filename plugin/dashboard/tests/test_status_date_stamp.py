"""Tests for stamp_status_date — a dashboard status change records the date it implies."""
from datetime import date

from serve import stamp_status_date

TODAY = date(2026, 11, 6)
SRC = "---\ncompany: Acme\nstatus: applied\ndate_added: 2026-10-30\n---\nbody\n"


def test_applied_adds_date_applied():
    out = stamp_status_date(SRC, "applied", TODAY)
    assert "date_applied: 2026-11-06" in out
    assert out.endswith("---\nbody\n")


def test_existing_date_is_kept():
    src = SRC.replace("date_added: 2026-10-30", "date_added: 2026-10-30\ndate_applied: 2026-10-31")
    assert stamp_status_date(src, "applied", TODAY) == src


def test_blank_date_is_filled_in_place():
    src = SRC.replace("date_added: 2026-10-30", 'date_applied: ""\ndate_added: 2026-10-30')
    out = stamp_status_date(src, "applied", TODAY)
    assert out.count("date_applied") == 1
    assert "date_applied: 2026-11-06\ndate_added" in out


def test_rejected_and_not_interested():
    assert "date_rejected: 2026-11-06" in stamp_status_date(SRC, "rejected", TODAY)
    assert "date_not_interested: 2026-11-06" in stamp_status_date(SRC, "not_interested", TODAY)


def test_other_status_is_noop():
    assert stamp_status_date(SRC, "interviewing", TODAY) == SRC
    assert stamp_status_date(SRC, "new", TODAY) == SRC
