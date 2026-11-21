"""plugin/scripts/score.py + scoring_schema.py — scoring v2 arithmetic and rules."""
from __future__ import annotations

import copy
import json

import pytest

from scripts_helpers import SCRIPTS, load, run

S = load("scoring_schema.py")


def dim(score, cls="EXPLICIT", conf="high"):
    ev = [] if cls == "MISSING" else [{"quote": "Shipped the checkout API", "source": "cv"}]
    return {"score": score, "requirement": "r", "explanation": "e", "evidence": ev,
            "evidence_class": cls, "confidence": conf}


def assessment(scores=(80, 80, 80, 80, 80), level="medium", elig=None, classes=None):
    classes = classes or ["EXPLICIT"] * 5
    return {
        "scoring_version": 2,
        "role": {"company": "Acme Pay", "position": "Senior PM"},
        "eligibility": elig if elig is not None else
        [{"requirement": "no relocation", "source": "hard_filter", "status": "PASS", "jd_quote": "Remote EU"}],
        "dimensions": {k: dim(s, c) for k, s, c in zip(S.DIMENSIONS, scores, classes)},
        "attractiveness": {"level": level, "sources": ["posting"] if level != "unknown" else []},
    }


def test_valid_assessment_has_no_errors():
    assert S.validate(assessment()) == []


def test_weighted_fit_uses_default_weights():
    a = assessment(scores=(100, 0, 0, 0, 0))
    assert S.compute(a)["fit_score"] == 30.0
    a = assessment(scores=(100, 100, 100, 100, 100))
    assert S.compute(a)["fit_score"] == 100.0


def test_weights_are_normalised():
    a = assessment(scores=(100, 0, 0, 0, 0))
    w = {k: 1 for k in S.DIMENSIONS}
    assert S.compute(a, w)["fit_score"] == 20.0


@pytest.mark.parametrize("fit,tier", [(80, "P0"), (79.9, "P1"), (65, "P1"), (64.9, "P2")])
def test_threshold_boundaries(fit, tier):
    assert S.tier_for(fit, S.DEFAULT_THRESHOLDS) == tier


def test_fail_is_never_outweighed():
    a = assessment(scores=(100,) * 5, level="high",
                   elig=[{"requirement": "fluent German", "source": "jd", "status": "FAIL",
                          "jd_quote": "Fluent German required"}])
    r = S.compute(a)
    assert r["eligibility"] == "blocked" and r["tier"] == "P2" and r["failed"] == ["fluent German"]


def test_unknown_means_needs_review_not_fail():
    a = assessment(elig=[{"requirement": "EU work permit", "source": "jd", "status": "UNKNOWN",
                          "jd_quote": "not stated"}])
    r = S.compute(a)
    assert r["eligibility"] == "needs_review" and r["pending"] == ["EU work permit"] and r["tier"] == "P0"


def test_not_applicable_is_ignored():
    a = assessment(elig=[{"requirement": "no relocation", "source": "hard_filter",
                          "status": "NOT_APPLICABLE", "jd_quote": "not stated"}])
    assert S.compute(a)["eligibility"] == "eligible"


@pytest.mark.parametrize("level,tier", [("high", "P0"), ("medium", "P1"), ("unknown", "P1"), ("low", "P2")])
def test_attractiveness_moves_at_most_one_tier(level, tier):
    a = assessment(scores=(70,) * 5, level=level)
    assert S.compute(a)["tier"] == tier


def test_attractiveness_cannot_lift_past_p0_or_below_p2():
    assert S.compute(assessment(scores=(90,) * 5, level="high"))["tier"] == "P0"
    assert S.compute(assessment(scores=(10,) * 5, level="low"))["tier"] == "P2"


def test_missing_vs_contradicted():
    a = assessment(classes=["EXPLICIT", "MISSING", "CONTRADICTED", "EXPLICIT", "TRANSFERABLE"])
    r = S.compute(a)
    assert r["missing_evidence"] == ["skills_experience"]
    assert r["confirmed_gaps"] == ["domain"]


@pytest.mark.parametrize("classes,level", [
    (["EXPLICIT"] * 5, "high"),
    (["EXPLICIT", "EXPLICIT", "MISSING", "WEAK", "EXPLICIT"], "medium"),  # 30+25+10 = 65%
    (["MISSING"] * 5, "low"),
])
def test_evidence_confidence(classes, level):
    assert S.compute(assessment(classes=classes))["evidence_confidence"] == level


@pytest.mark.parametrize("mutate,needle", [
    (lambda a: a["dimensions"]["domain"].update(score=101), "score must be a number"),
    (lambda a: a["dimensions"]["domain"].update(evidence=[]), "needs at least one evidence"),
    (lambda a: a["dimensions"]["domain"].update(evidence_class="MISSING"), "MISSING means no evidence"),
    (lambda a: a["dimensions"].pop("domain"), "dimensions.domain: missing"),
    (lambda a: a["eligibility"][0].update(status="MAYBE"), "status must be one of"),
    (lambda a: a["eligibility"][0].pop("jd_quote"), "jd_quote is required"),
    (lambda a: a["attractiveness"].update(sources=[]), "a known level needs sources"),
    (lambda a: a.update(scoring_version=1), "scoring_version"),
])
def test_validation_catches(mutate, needle):
    a = copy.deepcopy(assessment())
    mutate(a)
    assert any(needle in e for e in S.validate(a)), S.validate(a)


def test_config_from_v1_profile_uses_defaults():
    w, t = S.config_from_profile("---\nname: X\ntier_weights:\n  role_fit:\n    1: \"a\"\n---\n")
    assert w == {} and t == S.DEFAULT_THRESHOLDS


def test_config_from_v2_profile():
    text = "---\nfit_weights:\n  domain: 40\n  competitive_advantage: 0\nfit_thresholds:\n  p0: 85\n  p1: 70\n---\n"
    w, t = S.config_from_profile(text)
    assert w == {"domain": 40.0, "competitive_advantage": 0.0} and t == {"p0": 85.0, "p1": 70.0}
    assert S.validate_config(w, t) == []


def test_bad_config_rejected():
    assert S.validate_config({"nope": 1}, {"p0": 50, "p1": 70})


def test_cli_compute(tmp_path):
    f = tmp_path / "a.json"
    f.write_text(json.dumps(assessment()))
    r = run("score.py", "compute", f)
    assert r.returncode == 0, r.stderr
    assert json.loads(r.stdout)["tier"] == "P0"


def test_cli_compute_invalid_exits_1(tmp_path):
    a = assessment(); a["dimensions"]["domain"]["score"] = -5
    f = tmp_path / "a.json"; f.write_text(json.dumps(a))
    r = run("score.py", "compute", f)
    assert r.returncode == 1 and "dimensions.domain" in r.stderr


def test_cli_uses_profile_thresholds(tmp_path):
    f = tmp_path / "a.json"; f.write_text(json.dumps(assessment()))
    p = tmp_path / "profile.md"; p.write_text("---\nfit_thresholds:\n  p0: 90\n  p1: 70\n---\n")
    r = run("score.py", "compute", f, "--profile", p)
    assert json.loads(r.stdout)["tier"] == "P1"
