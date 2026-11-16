"""/cover-letter: a letter for an example persona whose every sentence traces
to the master CV, profile or research brief, and the mechanical check the
skill runs before showing a letter.
"""
from __future__ import annotations

import json
import re
import shutil

import pytest

from scripts_helpers import ROOT, load, run
from test_archive_and_cv_build import HAS_CARLITO

FIX = ROOT / "tests" / "fixtures" / "cover-letter"
LETTER = FIX / "maya-plaid.md"
TRACE = json.loads((FIX / "maya-plaid.trace.json").read_text())
PERSONA = ROOT / TRACE["persona"]
ROLE = PERSONA / TRACE["role"]
SOURCES = {"cv.md": PERSONA / "cv.md", "profile.md": PERSONA / "profile.md",
           "research-brief.md": ROLE / "research-brief.md"}

check = load("cover-letter-check.py")


def sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+(?=[A-Z])|\n\s*\n", text) if s.strip()]


def source_text() -> str:
    return "\n".join(p.read_text() for p in SOURCES.values())


# ----- the fixture letter ----------------------------------------------------


@pytest.mark.parametrize("claim", TRACE["claims"], ids=lambda c: c["letter"][:40])
def test_each_claim_quotes_its_source_verbatim(claim):
    assert claim["letter"] in LETTER.read_text(), "claim text drifted from the letter"
    assert claim["quote"] in SOURCES[claim["source"]].read_text(), \
        f"{claim['source']} no longer says: {claim['quote']}"


def test_every_sentence_is_a_traced_claim_or_declared_framing():
    claims = [c["letter"] for c in TRACE["claims"]]
    untraced = [s for s in sentences(LETTER.read_text())
                if s not in TRACE["framing"] and not any(c in s or s in c for c in claims)]
    assert untraced == []


def test_framing_sentences_carry_no_facts():
    for s in TRACE["framing"]:
        assert not re.search(r"\d", s), s
        assert check.names(s) == [], s


def test_letter_answers_three_posting_needs_and_lists_what_it_did_not_claim():
    assert len(TRACE["posting_needs"]) == 3
    assert TRACE["did_not_claim"], "the chat summary's 'did NOT claim' list must not be empty here"


def test_letter_stays_clear_of_what_not_to_frame_as():
    text = LETTER.read_text().lower()
    for banned in ("passionate", "highly strategic", "deeply collaborative", "machine learning", "stakeholder"):
        assert banned not in text


# ----- cover-letter-check.py -------------------------------------------------


def checked(letter_text: str, tmp_path):
    p = tmp_path / "cover-2026-08-03.md"
    p.write_text(letter_text)
    return run("cover-letter-check.py", p, "--sources", *SOURCES.values())


def test_check_passes_the_fixture(tmp_path):
    res = checked(LETTER.read_text(), tmp_path)
    assert res.returncode == 0, res.stdout
    assert "PASS" in res.stdout


def test_check_catches_an_invented_metric_and_employer(tmp_path):
    # Neither 37% nor Revolut appears anywhere in Maya's CV, profile or the brief.
    bad = LETTER.read_text().replace("12%", "37%").replace("At NorthLoop", "At Revolut")
    res = checked(bad, tmp_path)
    assert res.returncode == 1
    assert "numbers not found in the sources: 37%" in res.stdout
    assert "names not found in the sources: Revolut" in res.stdout


def test_check_flags_length_and_layout(tmp_path):
    res = checked("## Why me\n\n- I build things.\n\nMaya\n", tmp_path)
    assert res.returncode == 1
    assert "words; aim for 150–250" in res.stdout
    assert "headings or list lines" in res.stdout


def test_confirm_markers_are_counted_not_traced(tmp_path):
    text = LETTER.read_text().replace("Happy to talk", "[CONFIRM: notice period 3 months?] Happy to talk")
    res = checked(text, tmp_path)
    assert res.returncode == 0, res.stdout
    assert "1 [CONFIRM] marker(s)" in res.stdout


def test_numbers_match_across_formats():
    assert check.traced("200K", "a base of ~200K monthly signups")
    assert check.traced("18", "for 18 months")
    assert not check.traced("8", "for 18 months")
    assert not check.traced("25%", "cut by 12%")


# ----- PDF and archive -------------------------------------------------------


@pytest.mark.skipif(not HAS_CARLITO, reason="Carlito font not installed")
def test_letter_builds_to_one_page_with_the_cv_header(tmp_path):
    pytest.importorskip("reportlab")
    pypdf = pytest.importorskip("pypdf")
    pdf = tmp_path / "Maya_Patel_Cover_Plaid.pdf"
    res = run("cover-letter-build.py", LETTER, pdf, "--cv", PERSONA / "cv.md")
    assert res.returncode == 0, res.stderr
    reader = pypdf.PdfReader(str(pdf))
    assert len(reader.pages) == 1
    text = reader.pages[0].extract_text()
    assert "Maya Patel" in text and "Brightline Credit" in text


def test_sent_archives_the_letter_and_its_pdf(tmp_path):
    role = tmp_path / "Plaid"
    shutil.copytree(ROLE, role)
    shutil.copy(LETTER, role / "cover-2026-08-03.md")
    (role / "Maya_Patel_Cover_Plaid.pdf").write_bytes(b"%PDF-1.4 letter")
    (role / "Maya_Patel_CV_Plaid.pdf").write_bytes(b"%PDF-1.4 cv")
    archiver = load("archive-application.py")
    out, rows, _ = archiver.archive(role, None, "company-site", "2026-08-03", False)
    names = {p.name for p in out.iterdir()}
    assert {"cover-2026-08-03.md", "Maya_Patel_Cover_Plaid.pdf", "Maya_Patel_CV_Plaid.pdf"} <= names
