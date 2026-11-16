"""plugin/scripts/ats-check.py — reading a CV PDF the way an ATS does.

Two layers:
- end-to-end on real PDFs drawn with reportlab's built-in Helvetica (no font
  install needed), so page count, contacts, order, fidelity and keywords are
  checked against an actual text layer;
- the glyph and ordering rules on crafted text layers, by swapping out the
  extractor — a ligature or a (cid:N) code is hard to produce on purpose with
  a standard font, and this keeps the rule tested without one.
"""
from __future__ import annotations

import sys

import pytest

from scripts_helpers import load, run

pytest.importorskip("pypdf")
canvas = pytest.importorskip("reportlab.pdfgen.canvas")
from reportlab.lib.pagesizes import A4  # noqa: E402

CV_MD = """# ALEX EXAMPLE
Lisbon, Portugal | alex@example.com | +351 912 111 222

## PROFESSIONAL SUMMARY
Senior product manager for payment orchestration and PSP integrations.

## WORK EXPERIENCE
### Senior PM | Paycorp — Lisbon
*2024 – 2026*
- Unified PSP integrations into one framework and cut merchant onboarding time.
- Built reconciliation tooling and approval-rate dashboards in SQL.

## EDUCATION
Engineer's degree, Example University
"""


def md_lines(md: str) -> list[str]:
    return [line.lstrip("#*- ").rstrip("*") for line in md.splitlines() if line.strip()]


def draw_pdf(path, pages: list[list[str]]):
    c = canvas.Canvas(str(path), pagesize=A4)
    for lines in pages:
        y = A4[1] - 50
        for line in lines:
            c.drawString(40, y, line)
            y -= 14
        c.showPage()
    c.save()
    return path


@pytest.fixture
def cv(tmp_path):
    md = tmp_path / "cv-paycorp.md"
    md.write_text(CV_MD, encoding="utf-8")
    pdf = draw_pdf(tmp_path / "Alex_Example_CV_Paycorp.pdf", [md_lines(CV_MD)])
    return pdf, md


def check(*args):
    return run("ats-check.py", *args)


def rows(stdout: str) -> dict[str, bool]:
    """Check name → passed, from the report table."""
    out = {}
    for line in stdout.splitlines():
        parts = [p.strip() for p in line.split("|")]
        if len(parts) >= 4 and parts[2] in ("✅", "❌"):
            out[parts[1]] = parts[2] == "✅"
    return out


def test_clean_cv_passes_every_hard_check(cv, tmp_path):
    pdf, md = cv
    report = tmp_path / "ats-check-2026-11-16.md"
    res = check(pdf, "--md", md, "--phone", "+351 912 111 222", "--out", report)
    assert res.returncode == 0, res.stdout + res.stderr
    assert rows(res.stdout) == {"pages": True, "contacts": True, "glyphs": True, "order": True, "fidelity": True}
    assert "PASS" in res.stdout
    assert report.read_text(encoding="utf-8") == res.stdout.rstrip("\n") + "\n"


def test_keyword_coverage_handles_plural_and_hyphen_variants(cv):
    pdf, md = cv
    res = check(pdf, "--md", md, "--phone", "+351912111222",
                "--keywords", "PSP integration, approval rate, SQL, payment-orchestration, Kubernetes")
    assert "Keyword coverage: 4/5" in res.stdout
    assert "Missing: Kubernetes" in res.stdout
    assert res.returncode == 0  # keywords are reported, never a hard failure


def test_two_pages_fail(cv, tmp_path):
    _, md = cv
    lines = md_lines(CV_MD)
    pdf = draw_pdf(tmp_path / "cv.pdf", [lines[:6], lines[6:]])
    res = check(pdf, "--md", md, "--phone", "+351 912 111 222")
    assert res.returncode == 1
    assert rows(res.stdout)["pages"] is False
    assert check(pdf, "--md", md, "--phone", "+351 912 111 222", "--pages", "2").returncode == 0


def test_phone_must_match_the_expected_number(cv):
    pdf, md = cv
    res = check(pdf, "--md", md, "--phone", "+351 919 999 999")
    assert res.returncode == 1
    assert rows(res.stdout)["contacts"] is False
    assert "MISSING" in res.stdout


def test_phone_defaults_to_profile_md(cv, tmp_path):
    _, md = cv
    role = tmp_path / "userdata" / "companies" / "Paycorp"
    role.mkdir(parents=True)
    (tmp_path / "userdata" / "profile.md").write_text('---\nname: Alex\nphone: "+351 912 111 222"\n---\n')
    pdf = draw_pdf(role / "cv.pdf", [md_lines(CV_MD)])
    assert check(pdf, "--md", md).returncode == 0

    (tmp_path / "userdata" / "profile.md").write_text('---\nname: Alex\nphone: "+44 7700 900000"\n---\n')
    res = check(pdf, "--md", md)
    assert res.returncode == 1 and "+44 7700 900000 MISSING" in res.stdout


def test_missing_email_fails_contacts(tmp_path):
    lines = [l.replace("alex@example.com", "email on request") for l in md_lines(CV_MD)]
    res = check(draw_pdf(tmp_path / "cv.pdf", [lines]), "--phone", "+351 912 111 222")
    assert rows(res.stdout)["contacts"] is False


def test_text_drawn_as_shapes_fails_fidelity(cv, tmp_path):
    _, md = cv
    # The header survives; the bullets were "printed" as images, so their words are gone.
    kept = [l for l in md_lines(CV_MD) if not l.startswith(("Unified", "Built", "Senior product"))]
    res = check(draw_pdf(tmp_path / "cv.pdf", [kept]), "--md", md, "--phone", "+351 912 111 222")
    assert res.returncode == 1
    assert rows(res.stdout)["fidelity"] is False


def test_jd_terms_are_suggested_not_required(cv, tmp_path):
    pdf, md = cv
    jd = tmp_path / "posting.md"
    jd.write_text("We need fraud prevention experience. Fraud prevention is core. "
                  "Chargebacks and chargebacks again. PSP integrations matter.\n")
    res = check(pdf, "--md", md, "--phone", "+351912111222", "--jd", jd)
    assert res.returncode == 0
    assert "fraud prevention" in res.stdout.split("suggestions)")[1]


# --- rules on crafted text layers -------------------------------------------------

GOOD_TEXT = "\n".join(md_lines(CV_MD))


@pytest.fixture
def ats(monkeypatch, tmp_path, capsys):
    mod = load("ats-check.py")
    md = tmp_path / "cv.md"
    md.write_text(CV_MD, encoding="utf-8")

    def go(text: str, pages: int = 1) -> tuple[int, dict[str, bool]]:
        monkeypatch.setattr(mod, "extract", lambda _pdf: (text, pages, "fake"))
        monkeypatch.setattr(sys, "argv", ["ats-check.py", str(tmp_path / "cv.pdf"), "--md", str(md),
                                          "--phone", "+351 912 111 222"])
        code = mod.main()
        return code, rows(capsys.readouterr().out)

    return go


def test_crafted_clean_text_passes(ats):
    assert ats(GOOD_TEXT) == (0, {"pages": True, "contacts": True, "glyphs": True, "order": True, "fidelity": True})


@pytest.mark.parametrize("bad", ["Uniﬁed PSP", "(cid:42)", "�", " Lisbon"],
                         ids=["ligature", "cid-code", "replacement-char", "icon-font-glyph"])
def test_glyph_problems_fail(ats, bad):
    code, result = ats(GOOD_TEXT + "\n" + bad)
    assert code == 1 and result["glyphs"] is False


def test_two_column_extraction_order_fails(ats):
    # A two-column layout often extracts the sidebar (education) before the main column.
    lines = GOOD_TEXT.splitlines()
    edu = lines.index("EDUCATION")
    reordered = "\n".join(lines[:2] + lines[edu:] + lines[2:edu])
    code, result = ats(reordered)
    assert code == 1 and result["order"] is False


def test_missing_heading_fails_order(ats):
    code, result = ats(GOOD_TEXT.replace("EDUCATION", "Studies"))
    assert code == 1 and result["order"] is False
