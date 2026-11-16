"""plugin/scripts/archive-application.py and cv-build.py.

archive-application freezes what was sent; follow-ups and interview prep trust
that copy, so the manifest, the History line and the refusal to overwrite are
pinned here. cv-build is checked end to end through ats-check: a CV built by it
must pass every hard check, which is the promise /apply makes.
"""
from __future__ import annotations

import os
import re

import pytest

from scripts_helpers import run, write_meta


@pytest.fixture
def role(tmp_path):
    role = tmp_path / "companies" / "Paycorp"
    write_meta(role, company="Paycorp", position="Senior PM, Payments", status="applied",
               link="https://jobs.example.com/paycorp")
    (role / "Alex_Example_CV_Paycorp.pdf").write_bytes(b"%PDF-1.4 fake")
    (role / "cv-2026-11-10.md").write_text("# ALEX EXAMPLE\n")
    (role / "ats-check-2026-11-10.md").write_text("# ATS check\nPASS\n")
    (role / "cover-paycorp.md").write_text("Dear Paycorp,\n")
    return role


def test_archive_freezes_files_with_manifest_and_history(role, tmp_path):
    posting = tmp_path / "posting.txt"
    posting.write_text("Senior PM, Payments. PSP integrations.\n")
    res = run("archive-application.py", role, "--posting", posting, "--channel", "referral", "--date", "2026-11-12")
    assert res.returncode == 0, res.stderr

    out = role / "submitted-2026-11-12"
    assert sorted(p.name for p in out.iterdir()) == sorted([
        "Alex_Example_CV_Paycorp.pdf", "cv-2026-11-10.md", "ats-check-2026-11-10.md",
        "cover-paycorp.md", "posting.md", "manifest.md"])
    assert (out / "Alex_Example_CV_Paycorp.pdf").read_bytes() == b"%PDF-1.4 fake"
    assert "https://jobs.example.com/paycorp" in (out / "posting.md").read_text()

    manifest = (out / "manifest.md").read_text()
    assert "# Submitted — Paycorp, Senior PM, Payments" in manifest
    assert "- Channel: referral" in manifest
    assert len(re.findall(r"\| `[^`]+` \| [0-9a-f]{12} \|", manifest)) == 5

    meta = (role / "meta.md").read_text()
    assert meta.rstrip().endswith("- 2026-11-12: submitted materials archived in submitted-2026-11-12/ (referral)")
    assert meta.count("## History") == 1
    assert "status: applied" in meta  # status is not this script's business


def test_archive_refuses_to_overwrite_without_force(role):
    assert run("archive-application.py", role, "--date", "2026-11-12").returncode == 0
    (role / "cv-2026-11-10.md").write_text("# ALEX EXAMPLE, edited after sending\n")
    again = run("archive-application.py", role, "--date", "2026-11-12")
    assert again.returncode != 0 and "--force" in again.stderr
    assert "edited" not in (role / "submitted-2026-11-12" / "cv-2026-11-10.md").read_text()

    assert run("archive-application.py", role, "--date", "2026-11-12", "--force").returncode == 0
    assert "edited" in (role / "submitted-2026-11-12" / "cv-2026-11-10.md").read_text()


def test_archive_without_posting_says_so(role):
    res = run("archive-application.py", role, "--date", "2026-11-12")
    assert "posting text not captured" in res.stdout
    assert "only the link is recorded" in (role / "submitted-2026-11-12" / "manifest.md").read_text()


def test_archive_adds_history_block_when_missing(tmp_path):
    role = tmp_path / "Acme"
    role.mkdir()
    (role / "meta.md").write_text("---\ncompany: Acme\nposition: PM\nstatus: applied\nlink: https://a.example\n---\n")
    (role / "cv-acme.md").write_text("# X\n")
    assert run("archive-application.py", role, "--date", "2026-11-12").returncode == 0
    assert "\n## History\n- 2026-11-12: submitted materials archived" in (role / "meta.md").read_text()


def test_archive_needs_a_cv(tmp_path):
    role = tmp_path / "Empty"
    write_meta(role, company="Empty", position="PM", status="applied", link="https://e.example")
    res = run("archive-application.py", role)
    assert res.returncode != 0 and "No CV found" in res.stderr
    assert not list(role.glob("submitted-*"))


# --- cv-build -> ats-check ---------------------------------------------------------

FONT_DIRS = [os.path.expanduser("~/Library/Fonts/"), "/Library/Fonts/", "/usr/share/fonts/truetype/crosextra/"]
HAS_CARLITO = any(os.path.exists(d + "Carlito-Regular.ttf") for d in FONT_DIRS)

CV_MD = """<!-- tailored for Paycorp -->
# ALEX EXAMPLE
Lisbon, Portugal | alex@example.com | +34 600 111 222 | linkedin.com/in/alex-example

## PROFESSIONAL SUMMARY
Senior product manager with **seven years** in payment orchestration, PSP integrations and checkout.

## WORK EXPERIENCE
### Senior Product Manager | Paycorp — Lisbon
*2025 – present*
Payment service provider, 400 merchants.
- Unified 100+ PSP integrations into one framework; merchant onboarding time down 30%.
- Built *real-time* monitoring that cut issue detection from days to hours.
- Defined approval-rate dashboards in SQL used by the routing team.

### Product Manager | Checkoutly — Remote
*2023 – 2025*
- Redesigned the checkout API, cutting integration time from weeks to days.
- Shipped plugins for WooCommerce, Shopify, Magento & Wix.

## PROFESSIONAL SKILLS
- Payments: PSP integrations, APMs, reconciliation, card routing
- Tools: SQL, Jira, Figma

## EDUCATION
Engineer's degree, Example University (2011 – 2017)
"""


@pytest.mark.skipif(not HAS_CARLITO, reason="Carlito font not installed")
def test_cv_build_output_passes_the_ats_check(tmp_path):
    pytest.importorskip("reportlab")
    pytest.importorskip("pypdf")
    md = tmp_path / "cv-paycorp.md"
    md.write_text(CV_MD, encoding="utf-8")
    pdf = tmp_path / "Alex_Example_CV_Paycorp.pdf"

    built = run("cv-build.py", md, pdf, "9", "1.15")
    assert built.returncode == 0, built.stderr
    assert pdf.read_bytes().startswith(b"%PDF")

    res = run("ats-check.py", pdf, "--md", md, "--phone", "+34 600 111 222",
              "--keywords", "PSP integrations, reconciliation, SQL, WooCommerce")
    assert res.returncode == 0, res.stdout
    assert "PASS" in res.stdout and "Keyword coverage: 4/4" in res.stdout


def test_cv_build_without_args_prints_usage():
    pytest.importorskip("reportlab")
    if not HAS_CARLITO:
        pytest.skip("cv-build exits on the missing font before parsing args")
    res = run("cv-build.py")
    assert res.returncode != 0 and "Usage" in res.stderr
