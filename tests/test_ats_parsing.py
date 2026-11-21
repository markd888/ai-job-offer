"""ats_parse.py — parsing simulation and field-level fidelity against the CV markdown (#38 phase 3)."""
from __future__ import annotations

from ats_fixtures import make_docx
from scripts_helpers import load, run

P = load("ats_parse.py")

CV_MD = """# ALEX EXAMPLE
Lisbon, Portugal | +351 912 111 222 | alex@example.com | linkedin.com/in/alex-example

## PROFESSIONAL SUMMARY
Senior product manager for payment orchestration.

## WORK EXPERIENCE

### SENIOR PRODUCT MANAGER, Payments | Paycorp — Lisbon
*2024 – Present*
- Unified PSP integrations into one framework.

### PRODUCT MANAGER | Ledgerly — Porto
*Mar 2020 – Dec 2023*
- Built reconciliation tooling.

## PROFESSIONAL SKILLS

**Payments:** PSP integrations, reconciliation, chargebacks

**Data:** SQL, Grafana

**Languages:** English (C1), Portuguese (Native)

## EDUCATION

### MSc Computer Science | Example University
*2014 – 2019*
"""

TEXT = """ALEX EXAMPLE
 Lisbon, Portugal | +351 912 111 222 | alex@example.com | linkedin.com/in/alex-example
PROFESSIONAL SUMMARY
Senior product manager for payment orchestration.
WORK EXPERIENCE
SENIOR PRODUCT MANAGER, Payments | Paycorp — Lisbon
 2024 – Present
\x7f
Unified PSP integrations into one
framework.
PRODUCT MANAGER | Ledgerly — Porto
 Mar 2020 – Dec 2023
\x7f
Built reconciliation tooling.
PROFESSIONAL SKILLS
Payments: PSP integrations, reconciliation, chargebacks
Data: SQL, Grafana
Languages: English (C1), Portuguese (Native)
EDUCATION
MSc Computer Science | Example University
 2014 – 2019
"""


def v(f):
    return f["value"]


def by_field(rows):
    return {r["field"]: r for r in rows}


def test_clean_cv_parses_every_field():
    p = P.parse(TEXT)
    c = p["candidate"]
    assert (v(c["name"]), v(c["email"]), v(c["phone"]), v(c["location"]), v(c["linkedin"])) == (
        "ALEX EXAMPLE", "alex@example.com", "+351 912 111 222", "Lisbon, Portugal", "linkedin.com/in/alex-example")
    jobs = p["experience"]
    assert [(v(j["job_title"]), v(j["company"]), v(j["start_date"]), v(j["end_date"])) for j in jobs] == [
        ("SENIOR PRODUCT MANAGER, Payments", "Paycorp", "2024", "Present"),
        ("PRODUCT MANAGER", "Ledgerly", "Mar 2020", "Dec 2023")]
    assert jobs[0]["description"] == ["Unified PSP integrations into one framework."]   # wrapped line rejoined
    assert [v(e["degree"]) for e in p["education"]] == ["MSc Computer Science"]
    assert v(p["education"][0]["dates"]) == "2014 – 2019"
    assert {v(s) for s in p["skills"]} >= {"PSP integrations", "SQL", "Grafana"}
    assert [v(lang) for lang in p["languages"]] == ["English (C1)", "Portuguese (Native)"]
    assert p["parsing_warnings"] == []


def test_every_field_carries_its_source_text():
    p = P.parse(TEXT)
    for f in [*p["candidate"].values(), *(x for j in p["experience"] for x in (j["company"], j["start_date"]))]:
        if f["value"] is not None:
            assert f["source_text"] and f["source_text"] in TEXT and f["confidence"]


def test_fidelity_all_extracted_on_a_clean_cv():
    rows = P.compare(P.parse(TEXT), CV_MD, TEXT)
    bad = [r for r in rows if r["status"] not in ("EXTRACTED", "NOT_IN_SOURCE")]
    assert bad == []
    assert by_field(rows)["certifications"]["status"] == "NOT_IN_SOURCE"


def test_incomplete_dates_are_explicit():
    text = TEXT.replace(" Mar 2020 – Dec 2023\n", "")
    p = P.parse(text)
    assert v(p["experience"][1]["start_date"]) is None
    assert "no date range" in p["experience"][1]["start_date"]["warnings"][0]
    assert "1 employment entry without dates" in p["parsing_warnings"]
    assert by_field(P.compare(p, CV_MD, text))["job: Ledgerly · dates"]["status"] == "MISSING"


def test_missing_contacts_are_missing_not_guessed():
    text = TEXT.replace("+351 912 111 222 | alex@example.com | ", "")
    p = P.parse(text)
    assert v(p["candidate"]["email"]) is None and v(p["candidate"]["phone"]) is None
    rows = by_field(P.compare(p, CV_MD, text))
    assert rows["email"]["status"] == rows["phone"]["status"] == "MISSING"


def test_jumbled_two_column_text_is_ambiguous_not_missing():
    # The role line split across columns: the company is in the text, not parsed as an entry.
    text = TEXT.replace("PRODUCT MANAGER | Ledgerly — Porto\n Mar 2020 – Dec 2023\n", "PRODUCT MANAGER Porto\nLedgerly\n")
    row = by_field(P.compare(P.parse(text), CV_MD, text))["job: Ledgerly"]
    assert row["status"] == "AMBIGUOUS" and "not recognised" in row["note"]


def test_conflicting_title():
    text = TEXT.replace("PRODUCT MANAGER | Ledgerly", "PRODUCT OWNER | Ledgerly")
    assert by_field(P.compare(P.parse(text), CV_MD, text))["job: Ledgerly · title"]["status"] == "CONFLICTING"


def test_title_at_company_and_month_dates():
    p = P.parse("EXPERIENCE\nProduct Manager at Acme Pay\nJan 2021 - Present\n- Did things\n")
    (j,) = p["experience"]
    assert (v(j["job_title"]), v(j["company"]), v(j["start_date"]), v(j["end_date"])) == (
        "Product Manager", "Acme Pay", "Jan 2021", "Present")


def test_no_sections_at_all_is_said():
    p = P.parse("Alex Example\nalex@example.com\nI did payments for a while.")
    assert "no experience section heading found" in p["parsing_warnings"]
    assert p["experience"] == []


def test_russian_headings():
    p = P.parse("Алекс Пример\nОпыт работы\nПродакт-менеджер | Пэйкорп — Лиссабон\nянв 2021 – настоящее время\nОбразование\nМГУ\n")
    (j,) = p["experience"]
    assert v(j["company"]) == "Пэйкорп" and v(j["end_date"]) == "настоящее время"


def test_docx_contacts_in_a_table(tmp_path):
    body = ["ALEX EXAMPLE", [["alex@example.com", "+351 912 111 222"]], "WORK EXPERIENCE",
            "PRODUCT MANAGER | Ledgerly — Porto", "Mar 2020 – Dec 2023", "Built reconciliation tooling."]
    res = run("ats-check.py", make_docx(tmp_path / "cv.docx", body), "--phone", "+351 912 111 222")
    assert "email alex@example.com; phone +351 912 111 222" in res.stdout
    assert "PRODUCT MANAGER · Ledgerly · Mar 2020 – Dec 2023" in res.stdout


def test_cli_report_has_parsing_and_fidelity_sections(tmp_path):
    md = tmp_path / "cv.md"
    md.write_text(CV_MD, encoding="utf-8")
    body = [ln.strip() for ln in TEXT.replace("\x7f\n", "").splitlines() if ln.strip()]
    res = run("ats-check.py", make_docx(tmp_path / "cv.docx", body), "--md", md, "--phone", "+351 912 111 222")
    assert "## 2. Parsing simulation" in res.stdout and "## 3. Extraction fidelity" in res.stdout
    assert "| job: Paycorp · dates | 2024 – Present | 2024 – Present | EXTRACTED |" in res.stdout
