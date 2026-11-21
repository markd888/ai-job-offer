"""ats_match.py — JD requirement categories and evidence-backed matching (#38 phase 4)."""
from __future__ import annotations

import hashlib
import json

from ats_fixtures import make_docx
from scripts_helpers import load, run
from test_ats_parsing import CV_MD, TEXT

AM = load("ats_match.py")
P = load("ats_parse.py")

JD = """# Senior PM, Payments

## What you'll do
- Own the reconciliation roadmap end to end
- Partner with finance on chargebacks

## Requirements
- 5+ years with PSP integrations
- Must be fluent in SQL
- Excellent communication skills

## Nice to have
- Kotlin
- Experience with Grafana dashboards
"""


def rows_by_req(rows):
    return {r["requirement"]: r for r in rows}


def test_requirements_from_jd_headings_and_wording():
    got = {r["requirement"]: r["category"] for r in AM.requirements_from_jd(JD)}
    assert got == {
        "Own the reconciliation roadmap end to end": "RESPONSIBILITY",
        "Partner with finance on chargebacks": "RESPONSIBILITY",
        "5+ years with PSP integrations": "REQUIRED",
        "Must be fluent in SQL": "REQUIRED",
        "Excellent communication skills": "REQUIRED",
        "Kotlin": "PREFERRED",
        "Experience with Grafana dashboards": "PREFERRED",
    }


def test_statuses_and_evidence():
    rows = rows_by_req(AM.match(AM.requirements_from_jd(JD), P.parse(TEXT)))
    psp = rows["5+ years with PSP integrations"]
    assert psp["status"] == "SUPPORTED" and psp["evidence"] == "Unified PSP integrations into one framework."
    assert psp["source"] == "Paycorp"
    own = rows["Own the reconciliation roadmap end to end"]   # reconciliation shown, roadmap ownership not
    assert own["status"] == "PARTIALLY_SUPPORTED" and own["terms"] == ["reconciliation", "roadmap"]
    assert rows["Kotlin"]["status"] == "NOT_FOUND" and rows["Kotlin"]["evidence"] is None
    assert rows["Excellent communication skills"]["status"] == "AMBIGUOUS"


def test_skills_list_only_is_at_most_partial():
    # SQL and Grafana appear only under skills in the fixture CV — listed, not demonstrated.
    rows = rows_by_req(AM.match(AM.requirements_from_jd(JD), P.parse(TEXT)))
    for req in ("Must be fluent in SQL", "Experience with Grafana dashboards"):
        r = rows[req]
        assert r["status"] == "PARTIALLY_SUPPORTED" and r["source"] == "skills" and "not shown in experience" in r["note"]


def test_every_positive_status_quotes_the_cv():
    parsed = P.parse(TEXT)
    for r in AM.match(AM.requirements_from_jd(JD), parsed):
        if r["status"] in ("SUPPORTED", "PARTIALLY_SUPPORTED"):
            assert r["evidence"] and (r["evidence"] in TEXT.replace("\n", " ") or r["source"] == "skills")


def test_profile_support_is_flagged_not_counted_as_supported():
    profile = "## Proof Points\n- Ran Kotlin service migrations for the payouts platform\n"
    r = rows_by_req(AM.match([{"requirement": "Kotlin service migrations", "category": "PREFERRED"}],
                             P.parse(TEXT), profile))["Kotlin service migrations"]
    assert r["status"] == "PARTIALLY_SUPPORTED" and r["source"] == "profile" and "not on this CV" in r["note"]


def test_claude_terms_override_derived_terms():
    reqs = [{"requirement": "Payments platform depth", "category": "DOMAIN", "terms": ["reconciliation"]}]
    (r,) = AM.match(reqs, P.parse(TEXT))
    assert r["status"] == "SUPPORTED" and r["category"] == "DOMAIN"


def test_unknown_category_falls_back_to_required():
    (r,) = AM.match([{"requirement": "Kotlin", "category": "WHATEVER"}], P.parse(TEXT))
    assert r["category"] == "REQUIRED"


def test_coverage_per_category_leaves_ambiguous_out():
    cov = AM.coverage(AM.match(AM.requirements_from_jd(JD), P.parse(TEXT)))
    assert cov["REQUIRED"] == (1, 2) and cov["PREFERRED"] == (0, 2) and cov["RESPONSIBILITY"][1] == 2


def _docx(tmp_path):
    body = [ln.strip() for ln in TEXT.replace("\x7f\n", "").splitlines() if ln.strip()]
    return make_docx(tmp_path / "cv.docx", body)


def test_cli_report_section_and_exit_code_unchanged(tmp_path):
    jd = tmp_path / "posting.md"; jd.write_text(JD)
    md = tmp_path / "cv.md"; md.write_text(CV_MD)
    res = run("ats-check.py", _docx(tmp_path), "--md", md, "--jd", jd, "--phone", "+351 912 111 222")
    assert res.returncode == 0, res.stdout
    assert "## Job description matching" in res.stdout and "split from the posting by its headings" in res.stdout
    assert "| Kotlin | PREFERRED | NOT_FOUND | — |" in res.stdout
    assert "## Keyword coverage" not in res.stdout or "Covered:" in res.stdout   # legacy section kept when asked


def test_cli_uses_claude_requirements_file(tmp_path):
    req = tmp_path / "req.json"
    req.write_text(json.dumps([{"requirement": "PSP integrations", "category": "DOMAIN"}]))
    res = run("ats-check.py", _docx(tmp_path), "--requirements", req, "--phone", "+351 912 111 222",
              "--keywords", "PSP integrations, Kotlin")
    assert "Claude extracted from the posting" in res.stdout and "| PSP integrations | DOMAIN | SUPPORTED |" in res.stdout
    assert "## Keyword coverage: 1/2" in res.stdout


def test_cli_never_writes_to_the_cv(tmp_path):
    jd = tmp_path / "posting.md"; jd.write_text(JD)
    md = tmp_path / "cv.md"; md.write_text(CV_MD)
    cv = _docx(tmp_path)
    before = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in (cv, md)}
    run("ats-check.py", cv, "--md", md, "--jd", jd, "--keywords", "Kotlin", "--out", tmp_path / "r.md")
    assert before == {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in (cv, md)}
    assert "Kotlin" not in md.read_text()
