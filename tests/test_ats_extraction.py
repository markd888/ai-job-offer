"""ats_extract.py — DOCX via the standard library, and ats-check.py on a .docx (#38 phase 1)."""
from __future__ import annotations

from ats_fixtures import make_docx
from scripts_helpers import load, run

AX = load("ats_extract.py")

CV_MD = """# ALEX EXAMPLE
Lisbon, Portugal | alex@example.com | +351 912 111 222

## PROFESSIONAL SUMMARY
Senior product manager for payment orchestration.

## WORK EXPERIENCE
### Senior PM | Paycorp — Lisbon
*2024 – 2026*
- Unified PSP integrations into one framework.

## EDUCATION
Engineer's degree, Example University
"""

BODY = ["ALEX EXAMPLE", "Lisbon, Portugal | alex@example.com | +351 912 111 222",
        "PROFESSIONAL SUMMARY", "Senior product manager for payment orchestration.",
        "WORK EXPERIENCE", "Senior PM | Paycorp — Lisbon", "2024 – 2026",
        "Unified PSP integrations into one framework.",
        "EDUCATION", "Engineer's degree, Example University"]


def test_plain_paragraphs_in_order(tmp_path):
    x = AX.extract(make_docx(tmp_path / "cv.docx", BODY))
    assert x["format"] == "docx" and x["engine"] == "docx-xml" and x["pages"] == 1
    assert x["text"].splitlines() == BODY
    assert x["parts"]["tables"] == [] and x["limitations"]


def test_tables_read_row_by_row(tmp_path):
    body = ["ALEX EXAMPLE", [["alex@example.com", "+351 912 111 222"], ["Lisbon", "linkedin.com/in/alex"]], "EDUCATION"]
    x = AX.extract(make_docx(tmp_path / "cv.docx", body))
    assert x["parts"]["tables"] == ["alex@example.com | +351 912 111 222", "Lisbon | linkedin.com/in/alex"]
    assert x["text"].splitlines() == ["ALEX EXAMPLE", *x["parts"]["tables"], "EDUCATION"]


def test_headers_footers_and_text_boxes_kept_apart(tmp_path):
    x = AX.extract(make_docx(tmp_path / "cv.docx", ["Body line", {"text_box": "Skills\nSQL"}],
                             header=["alex@example.com"], footer=["Page 1"]))
    p = x["parts"]
    assert p["headers"] == ["alex@example.com"] and p["footers"] == ["Page 1"]
    assert p["text_boxes"] == ["Skills\nSQL"]          # once, not again from mc:Fallback
    assert p["body"] == ["Body line"]                  # the box isn't folded into its anchor paragraph
    assert x["text"].count("SQL") == 1


def test_missing_page_count_is_unknown_not_a_guess(tmp_path):
    x = AX.extract(make_docx(tmp_path / "cv.docx", BODY, pages=None))
    assert x["pages"] is None and any("page count" in s for s in x["limitations"])


def test_pdf_suffix_still_uses_the_pdf_path(tmp_path, monkeypatch):
    monkeypatch.setattr(AX, "extract_pdf", lambda p: ("text", 1, "pypdf"))
    assert AX.extract(tmp_path / "cv.PDF")["format"] == "pdf"


def _cli(tmp_path, docx, *extra):
    md = tmp_path / "cv.md"
    md.write_text(CV_MD, encoding="utf-8")
    return run("ats-check.py", docx, "--md", md, "--phone", "+351 912 111 222", *extra)


def test_cli_passes_a_clean_docx_and_lists_limitations(tmp_path):
    res = _cli(tmp_path, make_docx(tmp_path / "cv.docx", BODY))
    assert res.returncode == 0, res.stdout + res.stderr
    assert "docx-xml" in res.stdout and "What the extraction can't see" in res.stdout


def test_cli_docx_without_page_count_skips_the_page_check(tmp_path):
    res = _cli(tmp_path, make_docx(tmp_path / "cv.docx", BODY, pages=None))
    assert res.returncode == 0, res.stdout
    assert "| pages | ➖ |" in res.stdout


def test_cli_docx_missing_contacts_still_fails(tmp_path):
    body = [b for b in BODY if "@" not in b]
    res = _cli(tmp_path, make_docx(tmp_path / "cv.docx", body))
    assert res.returncode == 1 and "| contacts | ❌ |" in res.stdout


def test_cli_reports_where_text_sat(tmp_path):
    res = _cli(tmp_path, make_docx(tmp_path / "cv.docx", BODY, header=["alex@example.com"]))
    assert "headers: 1 line(s)" in res.stdout


def test_out_file_for_pdf_has_no_docx_section(tmp_path):
    canvas = __import__("pytest").importorskip("reportlab.pdfgen.canvas")
    pdf = tmp_path / "cv.pdf"
    c = canvas.Canvas(str(pdf))
    y = 800
    for line in BODY:
        c.drawString(40, y, line.replace("—", "-").replace("–", "-")); y -= 14
    c.save()
    out = tmp_path / "r.md"
    _cli(tmp_path, pdf, "--out", out)
    assert "What the extraction can't see" not in out.read_text()
