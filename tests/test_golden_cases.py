"""Golden-set label integrity: every case's arithmetic must be internally
consistent with the frozen profile's thresholds. Catches label typos and
silent edits to the frozen profile — with zero LLM calls."""
import json
from pathlib import Path

import pytest

GOLDEN = Path(__file__).resolve().parent / "golden" / "evaluate-position"
ALL = sorted((GOLDEN / "cases").glob("*.json"))
CASES = [p for p in ALL if "label" in json.loads(p.read_text())]  # v1 regression subset
P0, P1 = 13, 11  # frozen thresholds — must match tests/golden/evaluate-position/profile.md
DIMS = ["role_fit", "domain_fit", "business_health", "location_fit", "competitive_edge"]


def test_profile_thresholds_still_frozen():
    text = (GOLDEN / "profile.md").read_text()
    assert "p0: 13" in text and "p1: 11" in text, \
        "frozen profile thresholds changed — every golden label is now suspect"


@pytest.mark.parametrize("path", CASES, ids=lambda p: p.stem)
def test_case_labels_consistent(path):
    case = json.loads(path.read_text())
    assert case["synthetic"] is True
    assert len(case["jd"].split()) >= 60, "JD too thin to score five dimensions"
    label = case["label"]
    if label["tier"] == "filtered":
        assert label["hard_filter"], "filter case must name the expected filter"
        assert label["score"] is None and label["dimensions"] is None
        return
    dims = label["dimensions"]
    assert set(dims) == set(DIMS)
    assert all(v in (1, 2, 3) for v in dims.values())
    assert label["score"] == sum(dims.values()) + label["shape_adjustment"]
    expected_tier = "P0" if label["score"] >= P0 else "P1" if label["score"] >= P1 else "P2"
    assert label["tier"] == expected_tier


def test_case_count_and_spread():
    labels = [json.loads(p.read_text())["label"] for p in CASES]
    tiers = [l["tier"] for l in labels]
    assert len(CASES) == 12
    assert tiers.count("filtered") == 3
    assert {"P0", "P1", "P2"} <= set(tiers)


# ---- scoring v2 labels (all cases) -----------------------------------------
import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "scoring_schema", Path(__file__).resolve().parent.parent / "plugin" / "scripts" / "scoring_schema.py")
S = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(S)
FILTERS = [
    "More than 500 employees AND enterprise/sales-led AND no PLG signal",
    "More than 8 direct reports (GM scope)",
    "Requires relocation outside EMEA",
    "Crypto-native companies (out of scope by preference)",
]


def _tier(fit, level, elig):
    base = S.tier_for(fit, S.DEFAULT_THRESHOLDS)
    step = {"high": 1, "low": -1}.get(level, 0)
    t = S.shift(base, 0 if step > 0 and base == "P2" else step)
    return "P2" if elig == "blocked" else t


def test_v2_case_count_and_spread():
    labels = [json.loads(p.read_text())["label_v2"] for p in ALL]
    assert 30 <= len(labels) <= 50
    elig = [l["eligibility"] for l in labels]
    assert elig.count("blocked") >= 5 and elig.count("needs_review") >= 4
    assert {"P0", "P1", "P2"} <= {l["tier"] for l in labels}
    classes = {c for l in labels for allowed in l["evidence"].values() for c in allowed}
    assert {"EXPLICIT", "TRANSFERABLE", "WEAK", "MISSING", "CONTRADICTED"} <= classes


@pytest.mark.parametrize("path", ALL, ids=lambda p: p.stem)
def test_v2_label_consistent(path):
    case = json.loads(path.read_text())
    assert case["synthetic"] is True and len(case["jd"].split()) >= 60
    lab = case["label_v2"]
    assert lab["provenance"].startswith("author-derived-v2")
    assert lab["eligibility"] in ("eligible", "needs_review", "blocked")
    assert lab["tier"] in S.TIERS and lab["attractiveness"]
    assert all(a in S.ATTRACTIVENESS for a in lab["attractiveness"])
    for dim, allowed in lab["evidence"].items():
        assert dim in S.DIMENSIONS and allowed and all(c in S.EVIDENCE_CLASSES for c in allowed)
    assert (lab["eligibility"] == "blocked") == bool(lab["must_fail"])
    if lab["eligibility"] == "needs_review":
        assert lab["must_unknown"], "needs_review must name what's unknown"
    if lab["eligibility"] == "blocked":
        assert lab["tier"] == "P2"
        return
    lo, hi = lab["fit_range"]
    assert 0 <= lo < hi <= 100
    # Every combination the label allows must give the labelled tier — a range that
    # straddles a threshold, or an attractiveness set that would change it, is a typo.
    got = {_tier(f, a, lab["eligibility"]) for f in (lo, hi) for a in lab["attractiveness"]}
    assert got == {lab["tier"]}, f"label allows tiers {got}"


@pytest.mark.parametrize("path", CASES, ids=lambda p: p.stem)
def test_v1_cases_keep_their_tier_or_say_why(path):
    case = json.loads(path.read_text())
    v1, v2 = case["label"]["tier"], case["label_v2"]["tier"]
    if v1 != v2 and not (v1 == "filtered" and v2 == "P2"):
        assert case["label_v2"]["tier_change_reason"], f"{v1} → {v2} needs tier_change_reason"
    if v1 == "filtered":
        assert case["label_v2"]["eligibility"] == "blocked"
        assert case["label"]["hard_filter"] in case["label_v2"]["must_fail"]


def test_v2_must_fail_filters_are_real():
    for p in ALL:
        lab = json.loads(p.read_text())["label_v2"]
        for f in lab["must_fail"]:
            assert f in FILTERS or f in json.loads(p.read_text())["jd"], f
