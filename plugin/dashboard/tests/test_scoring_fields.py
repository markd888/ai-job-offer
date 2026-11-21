"""Scoring v2 fields reach the dashboard; v1 roles are unaffected."""
from pathlib import Path

from serve import collect_companies

V2 = """---
company: Acme Pay
position: "Senior PM"
status: new
tier: P1
link: https://example.com/jobs/1
scoring_version: 2
fit_score: 72.5
eligibility: needs_review
evidence_confidence: medium
predicted_tier: P1
---
"""


def test_v2_fields_pass_through(tmp_path: Path):
    (tmp_path / "companies" / "Acme Pay").mkdir(parents=True)
    (tmp_path / "companies" / "Acme Pay" / "meta.md").write_text(V2)
    [p] = collect_companies(tmp_path)
    assert p["scoring_version"] == "2" and p["fit_score"] == "72.5"
    assert p["eligibility"] == "needs_review" and p["evidence_confidence"] == "medium"
    assert "score" not in p


def test_v1_role_has_no_v2_fields(userdata: Path):
    for p in collect_companies(userdata):
        assert "scoring_version" not in p and "fit_score" not in p
