# ATS check example (synthetic)

`/ats-check` run on a synthetic one-page CV. The CV is the `clean-pdf` case
from `tests/ats_fixtures.py`: "Alex Example", fictional companies and contacts.
The command was:

```sh
python3 -I plugin/scripts/ats-check.py clean-pdf.pdf --md cv.md \
  --requirements req.json --keywords "PSP integrations, reconciliation, SQL, Kafka" --out report.md
```

`req.json` holds seven requirements Claude would list from a posting: three
required, one preferred, one responsibility, one domain, and "clear written
communication", which has nothing concrete to look for.

How to read the result:

- **Hard checks.** All five pass, so the exit code is 0.
- **Fit against the posting.** Two of three must-haves are shown in
  experience, with the line quoted. SQL appears only in the skills list, so it
  counts as partial. Kafka is not on the CV and stays a gap; the report
  doesn't suggest adding it.
- **No overall score.** There are five component results, each with its basis.

Section 7 states the report's limits: it doesn't predict any ATS ranking or
hiring decision.

---

# ATS check — clean-pdf.pdf

2026-11-21 · text layer via pypdf · PASS

| Component | Result | Basis |
|---|---|---|
| Document integrity | 5/5 hard checks pass | pages, contacts, glyphs, order, fidelity; 0 warning(s) |
| Parsing completeness | 7/7 key fields | name, email, phone, entries, dates, education, skills |
| Extraction fidelity | 14/14 fields match the CV | field by field against the CV markdown |
| Job requirement coverage | 2/3 required shown in experience | 1 more partially; 7 requirement(s) in all, per category in section 4 |
| Layout compatibility | no risks observed | positions, fonts and parts checked |

## 1. Document integrity

| Check | Result | Detail |
|---|---|---|
| pages | ✅ | 1 page(s), expected 1 |
| contacts | ✅ | email found: alex@example.com; phone +351 912 111 222 found |
| glyphs | ✅ | clean |
| order | ✅ | headings in order |
| fidelity | ✅ | 100% of CV words extracted |

## 2. Parsing simulation

What a parser could fill in from this text (heuristic; every field may be missing):

- **Contact:** name ALEX EXAMPLE; email alex@example.com; phone +351 912 111 222; location Lisbon, Portugal; LinkedIn —
- **Sections recognised:** PROFESSIONAL SUMMARY, WORK EXPERIENCE, PROFESSIONAL SKILLS, EDUCATION
- **Employment:** 2 entries, 2 with dates
  - SENIOR PRODUCT MANAGER, Payments · Paycorp · 2024 – Present
  - PRODUCT MANAGER · Ledgerly · 2020 – 2023
- **Education:** 1 · **Skills:** 5 · **Languages:** 0 · **Certifications:** 0

## 3. Extraction fidelity

| Field | In the CV | Parsed | Status | Note |
|---|---|---|---|---|
| name | ALEX EXAMPLE | ALEX EXAMPLE | EXTRACTED |  |
| email | alex@example.com | alex@example.com | EXTRACTED |  |
| phone | +351 912 111 222 | +351 912 111 222 | EXTRACTED |  |
| location | Lisbon, Portugal | Lisbon, Portugal | EXTRACTED |  |
| linkedin | — | — | NOT_IN_SOURCE |  |
| section: PROFESSIONAL SUMMARY | PROFESSIONAL SUMMARY | PROFESSIONAL SUMMARY | EXTRACTED |  |
| section: WORK EXPERIENCE | WORK EXPERIENCE | WORK EXPERIENCE | EXTRACTED |  |
| section: PROFESSIONAL SKILLS | PROFESSIONAL SKILLS | PROFESSIONAL SKILLS | EXTRACTED |  |
| section: EDUCATION | EDUCATION | EDUCATION | EXTRACTED |  |
| job: Paycorp · title | SENIOR PRODUCT MANAGER, Payments | SENIOR PRODUCT MANAGER, Payments | EXTRACTED |  |
| job: Paycorp · dates | 2024 – Present | 2024 – Present | EXTRACTED |  |
| job: Ledgerly · title | PRODUCT MANAGER | PRODUCT MANAGER | EXTRACTED |  |
| job: Ledgerly · dates | 2020 – 2023 | 2020 – 2023 | EXTRACTED |  |
| education: MSc Computer Science | MSc Computer Science | MSc Computer Science | EXTRACTED |  |
| skills | 5 item(s) | 5 as skills | EXTRACTED |  |
| languages | — | — | NOT_IN_SOURCE |  |
| certifications | — | — | NOT_IN_SOURCE |  |

## 4. Job description matching

Requirements Claude extracted from the posting. Covered = shown in experience or the summary; skills-list-only counts as partial.

required 2/3 · preferred 0/1 · responsibility 0/1 · domain 1/1

| Requirement | Category | Status | Evidence |
|---|---|---|---|
| 3+ years owning PSP integrations or payment orchestration | REQUIRED | SUPPORTED | "Unified PSP integrations into one framework and cut merchant onboarding time." (Paycorp) |
| Reconciliation and settlement with finance teams | REQUIRED | SUPPORTED | "Built reconciliation tooling with the finance team." (Paycorp) |
| Fluent in SQL | REQUIRED | PARTIALLY_SUPPORTED | "SQL" (skills) — listed under skills, not shown in experience |
| Kafka or event streaming | PREFERRED | NOT_FOUND | — |
| Own the approval-rate roadmap | RESPONSIBILITY | PARTIALLY_SUPPORTED | "Launched approval-rate dashboards and decline analysis for card payments." (Ledgerly) — 50% of the terms in one line |
| Card payments | DOMAIN | SUPPORTED | "Launched approval-rate dashboards and decline analysis for card payments." (Ledgerly) |
| Clear written communication | REQUIRED | AMBIGUOUS | — — no concrete skill, tool or domain to look for |

A requirement that isn't supported stays a gap: rephrase only experience the master CV already has.

### Keyword coverage: 3/4

Covered: PSP integrations, reconciliation, SQL

Missing: Kafka

Add a missing keyword only where the master CV or profile supports it; otherwise it stays a gap.

## 5. Readability & compatibility

No layout risks observed in the text layer.
- Fonts in the text layer: Helvetica.

## 6. Recommendations

- Listed under skills but not shown in a role: Fluent in SQL. If a role used it, say so in that role's line.

## 7. Limitations

This report evaluates document extraction and compatibility. It does not predict a specific ATS ranking or hiring decision.

- Parsing is a simulation with bounded heuristics, not any vendor's parser; real systems differ from each other.
- Requirement matching looks for the posting's terms in your CV lines. It can't judge depth, recency or years of experience — read the evidence, not the counts.

