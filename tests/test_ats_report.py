"""The ten synthetic cases from #38, the seven-section report, components and JSON (phase 5)."""
from __future__ import annotations

import json
import re

import pytest

from ats_fixtures import CASES, build_case
from scripts_helpers import run

pytest.importorskip("pypdf")
pytest.importorskip("reportlab")

PHONE = "+351 912 111 222"
REQS = [{"requirement": "PSP integrations", "category": "REQUIRED"},
        {"requirement": "Kubernetes in production", "category": "REQUIRED"},
        {"requirement": "Kafka streaming", "category": "PREFERRED"}]
SECTIONS = ["## 1. Document integrity", "## 2. Parsing simulation", "## 3. Extraction fidelity",
            "## 4. Job description matching", "## 5. Readability & compatibility", "## 6. Recommendations",
            "## 7. Limitations"]


def check(tmp_path, name, *extra):
    cv, md = build_case(name, tmp_path)
    (tmp_path / "cv.md").write_text(md, encoding="utf-8")
    (tmp_path / "req.json").write_text(json.dumps(REQS))
    out = tmp_path / "result.json"
    res = run("ats-check.py", cv, "--md", tmp_path / "cv.md", "--phone", PHONE,
              "--requirements", tmp_path / "req.json", "--json", out, *extra)
    return res, json.loads(out.read_text())


def risks(j):
    return {x["risk"] for x in j["layout"]}


def fid(j):
    return {r["field"]: r["status"] for r in j["fidelity"]}


@pytest.mark.parametrize("name", CASES)
def test_every_case_reports_all_seven_sections_and_the_limitation(tmp_path, name):
    res, j = check(tmp_path, name)
    for s in SECTIONS:
        assert s in res.stdout, s
    assert "does not predict a specific ATS ranking or hiring decision" in res.stdout
    assert j["exit_code"] == res.returncode
    assert [c["component"] for c in j["components"]] == [
        "Document integrity", "Parsing completeness", "Extraction fidelity", "Job requirement coverage",
        "Layout compatibility"]


@pytest.mark.parametrize("name", CASES)
def test_no_probability_or_ranking_claims(tmp_path, name):
    res, _ = check(tmp_path, name)
    body = res.stdout.split("## 7. Limitations")[0].lower()
    assert "%" not in re.sub(r"\d+% of (cv words|the terms)", "", body).replace("agree on", "")
    for word in ("probability", "chance", "likely to pass", "will be rejected", "ats score"):
        assert word not in body


def test_1_clean_single_column_pdf(tmp_path):
    res, j = check(tmp_path, "clean-pdf")
    assert res.returncode == 0 and j["layout"] == []
    assert {s for s in fid(j).values()} <= {"EXTRACTED", "NOT_IN_SOURCE"}


def test_2_two_column_pdf_is_observed(tmp_path):
    _, j = check(tmp_path, "two-column-pdf")
    obs = next(x for x in j["layout"] if x["risk"] == "multi-column layout")
    assert "x≈40pt" in obs["observed"] and "x≈340pt" in obs["observed"]
    # …and the interleaving shows up where it hurts: entries no longer parse cleanly.
    assert "AMBIGUOUS" in fid(j).values() or "CONFLICTING" in fid(j).values()


def test_3_icon_font_in_contact_block(tmp_path):
    _, j = check(tmp_path, "icon-contacts-pdf")
    assert "icon font" in risks(j)
    assert "ZapfDingbats" in next(x["observed"] for x in j["layout"] if x["risk"] == "icon font")


def test_4_broken_glyphs_fail_hard(monkeypatch, tmp_path, capsys):
    from scripts_helpers import load
    import sys
    mod = load("ats-check.py")
    cv, md = build_case("broken-glyphs-pdf", tmp_path)
    (tmp_path / "cv.md").write_text(md)
    text = "\n".join(__import__("ats_fixtures").case_lines()).replace("reconciliation", "reconcili(cid:42)tion")
    monkeypatch.setattr(mod, "extract", lambda _p: (text, 1, "fake"))
    monkeypatch.setattr(sys, "argv", ["ats-check.py", str(cv), "--md", str(tmp_path / "cv.md"), "--phone", PHONE])
    assert mod.main() == 1
    out = capsys.readouterr().out
    assert "| glyphs | ❌ | (cid:N) codes |" in out and "Rebuild the PDF so it writes plain characters" in out


def test_5_unusual_reading_order(tmp_path):
    res, j = check(tmp_path, "reading-order-pdf")
    assert res.returncode == 1 and "order" in res.stdout.split("FAIL:")[1].splitlines()[0]
    assert "Use a single-column layout" in res.stdout


def test_6_missing_contacts(tmp_path):
    res, j = check(tmp_path, "no-contacts-pdf")
    assert res.returncode == 1
    assert fid(j)["email"] == "MISSING" and fid(j)["phone"] == "MISSING"
    assert "missing: email, phone" in next(c["basis"] for c in j["components"] if c["component"] == "Parsing completeness")


def test_7_plain_docx(tmp_path):
    res, j = check(tmp_path, "plain-docx")
    assert res.returncode == 0 and j["format"] == "docx"
    assert "What the extraction can't see" in res.stdout


def test_8_docx_contacts_in_a_table(tmp_path):
    res, j = check(tmp_path, "tables-docx")
    assert "tables" in risks(j)
    assert fid(j)["email"] == "EXTRACTED"


def test_9_incomplete_dates(tmp_path):
    res, j = check(tmp_path, "undated-pdf")
    assert "1 employment entry without dates" in j["parsed"]["parsing_warnings"]
    assert "Give every role a date range" in res.stdout
    assert "missing: dates on every entry" in res.stdout


def test_10_keywords_listed_without_experience(tmp_path):
    res, j = check(tmp_path, "skills-only-pdf")
    m = {r["requirement"]: r for r in j["matching"]}
    assert m["PSP integrations"]["status"] == "SUPPORTED"
    for req in ("Kubernetes in production", "Kafka streaming"):
        assert m[req]["status"] == "PARTIALLY_SUPPORTED" and m[req]["source"] == "skills"
    assert "Listed under skills but not shown in a role" in res.stdout


def test_components_never_combine_into_one_score(tmp_path):
    res, j = check(tmp_path, "clean-pdf")
    assert "overall" not in res.stdout.lower() and "total score" not in res.stdout.lower()
    assert all(set(c) == {"component", "result", "basis"} for c in j["components"])


def test_apply_invocation_unchanged(tmp_path):
    # /apply's exact call: pdf, --md, --keywords, --out — no new flags needed, exit 0 on a clean CV.
    cv, md = build_case("clean-pdf", tmp_path)
    (tmp_path / "cv.md").write_text(md)
    out = tmp_path / "ats-check-2026-11-21.md"
    res = run("ats-check.py", cv, "--md", tmp_path / "cv.md", "--keywords", "PSP integrations, SQL",
              "--out", out, "--phone", PHONE)
    assert res.returncode == 0 and out.read_text() == res.stdout + "\n" or out.read_text().strip() == res.stdout.strip()
