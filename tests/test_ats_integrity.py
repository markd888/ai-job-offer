"""ats_integrity.py — integrity warnings that never change the exit code (#38 phase 2)."""
from __future__ import annotations

import sys

import pytest

from ats_fixtures import make_docx
from scripts_helpers import load, run

AI = load("ats_integrity.py")

SENTENCES = [f"Shipped payments change number {i} with merchants, risk and finance partners across regions."
             for i in range(12)]
FULL = ("ALEX EXAMPLE\nalex@example.com +351 912 111 222\nPROFESSIONAL SUMMARY\n"
        + "\n".join(SENTENCES[:4]) + "\nWORK EXPERIENCE\nSenior PM | Paycorp\n" + "\n".join(SENTENCES[4:])
        + "\nSKILLS\nSQL, Python\nEDUCATION\nEngineer's degree, Example University\n")


def kinds(ws):
    return [w["check"] for w in ws]


def test_clean_cv_has_no_warnings():
    assert AI.check(FULL, []) == []


@pytest.mark.parametrize("text,detail", [("", "no text at all"), ("Alex Example product manager", "only 4 words")])
def test_empty_or_near_empty(text, detail):
    (w,) = AI.empty(text)
    assert detail in w["detail"]


def test_repeated_block_is_reported_with_a_sample():
    line = "Unified PSP integrations into one framework and cut onboarding time"
    (w,) = AI.duplicates(f"{line}\nother\n{line}\n")
    assert "×2" in w["detail"] and "unified psp" in w["detail"]


def test_short_repeated_lines_are_normal():
    assert AI.duplicates("2024 – 2026\nRemote\n2024 – 2026\nRemote\n") == []


def test_mojibake_detected_but_real_unicode_is_fine():
    assert kinds(AI.encoding("Iâ€™ve led PSP work in SÃ£o Paulo")) == ["encoding"]
    assert AI.encoding("I’ve led PSP work in São Paulo — опыт работы, Zürich") == []


def test_control_characters_flagged():
    assert "control character" in AI.encoding("Senior\x07 PM")[0]["detail"]


def test_missing_section_kinds_from_text_and_from_md_headings():
    (w,) = AI.sections("SUMMARY\nPayments PM\nWORK EXPERIENCE\nPaycorp", [])
    assert "no education, no skills" in w["detail"]
    assert AI.sections("anything", ["PROFESSIONAL SUMMARY", "WORK EXPERIENCE", "SKILLS", "EDUCATION"]) == []
    assert "no skills" in AI.sections("", ["Опыт работы", "Образование"])[0]["detail"]


def test_bullet_glyph_as_del_is_named_not_counted_as_noise():
    (w,) = AI.encoding("Led the PSP work.\n\x7f\nBuilt the ledger.\n\x7fShipped it")
    assert "2 bullet mark(s)" in w["detail"] and "U+007F" in w["detail"]


def test_extractors_disagree():
    (w,) = AI.agreement("alpha beta gamma delta", "alpha beta epsilon zeta", "pdftotext")
    assert w["check"] == "extractors" and "33%" in w["detail"]
    assert AI.agreement("alpha beta", "beta alpha", "pdftotext") == []


# --- through the CLI: warnings appear, exit code doesn't move -------------------

@pytest.fixture
def ats(monkeypatch, tmp_path, capsys):
    mod = load("ats-check.py")

    def go(text: str) -> tuple[int, str]:
        monkeypatch.setattr(mod, "extract", lambda _p: (text, 1, "fake"))
        monkeypatch.setattr(sys, "argv", ["ats-check.py", str(tmp_path / "cv.pdf"), "--phone", "+351 912 111 222"])
        return mod.main(), capsys.readouterr().out

    return go


def test_warnings_never_fail_the_check(ats):
    line = "Unified PSP integrations into one framework and cut onboarding time"
    code, out = ats(FULL.replace("WORK EXPERIENCE", "WORK EXPERIENCE\n" + line + "\n" + line + "\nâ€™")
                    .replace("SKILLS\n", "PROFESSIONAL SKILLS\n"))
    assert code == 0, out
    assert "## Warnings (don't fail the check)" in out and "**duplicates**" in out and "**encoding**" in out


def test_no_warnings_section_when_clean(ats):
    code, out = ats(FULL.replace("SKILLS\n", "PROFESSIONAL SKILLS\n"))
    assert code == 0 and "## Warnings" not in out


def test_docx_with_only_a_name_warns_empty(tmp_path):
    res = run("ats-check.py", make_docx(tmp_path / "cv.docx", ["Alex Example", "alex@example.com +351 912 111 222"]),
              "--phone", "+351 912 111 222")
    assert "**empty**" in res.stdout
