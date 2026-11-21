"""Scoring v2 coexists with v1: old profiles and meta.md stay valid; outcomes are derived."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

from scripts_helpers import ROOT, load, run
from test_score import assessment

_spec = importlib.util.spec_from_file_location("validate_userdata", ROOT / "scripts" / "validate_userdata.py")
V = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(V)
F = load("funnel.py")

V1_PROFILE = """---
name: Test Person
target_titles: ["Senior PM"]
tier_weights:
  role_fit:
    1: "IC"
tier_thresholds:
  p0: 13
  p1: 11
---

## Positioning

Payments PM.
"""

META = """---
company: Acme Pay
position: "Senior PM"
status: new
tier: P1
score: 12
link: https://example.com/jobs/1
{extra}---
"""


def tree(tmp_path: Path, profile=V1_PROFILE, extra=""):
    (tmp_path / "companies" / "Acme Pay").mkdir(parents=True)
    (tmp_path / "profile.md").write_text(profile)
    (tmp_path / "companies" / "Acme Pay" / "meta.md").write_text(META.format(extra=extra))
    return tmp_path


def rules(tmp_path):
    return {f.rule for f in V.validate_tree(tmp_path)}


def test_v1_profile_and_meta_validate(tmp_path):
    assert rules(tree(tmp_path)) == set()


def test_v1_profile_scores_with_defaults(tmp_path):
    tree(tmp_path)
    f = tmp_path / "a.json"; f.write_text(json.dumps(assessment()))
    r = run("score.py", "compute", f, "--profile", tmp_path / "profile.md")
    assert r.returncode == 0, r.stderr
    assert json.loads(r.stdout)["thresholds"] == {"p0": 80, "p1": 65}


def test_recorded_v2_meta_validates(tmp_path):
    tree(tmp_path)
    f = tmp_path / "a.json"; f.write_text(json.dumps(assessment()))
    role = tmp_path / "companies" / "Acme Pay"
    assert run("score.py", "record", role, f, "--today", "2026-11-21").returncode == 0
    assert run("score.py", "override", role, "--tier", "P1", "--reason", "x", "--today", "2026-11-22").returncode == 0
    assert rules(tmp_path) == set()


def test_v2_profile_keys_validate(tmp_path):
    p = V1_PROFILE.replace("---\n\n##", "fit_weights:\n  domain: 30\nfit_thresholds:\n  p0: 85\n  p1: 70\n---\n\n##")
    assert rules(tree(tmp_path, profile=p)) == set()


def test_bad_v2_profile_keys_flagged(tmp_path):
    p = V1_PROFILE.replace("---\n\n##", "fit_thresholds:\n  p0: 60\n  p1: 70\n---\n\n##")
    assert "profile.fit-config" in rules(tree(tmp_path, profile=p))


@pytest.mark.parametrize("extra,rule", [
    ("eligibility: maybe\n", "meta.eligibility-enum"),
    ("predicted_tier: P9\n", "meta.tier-enum"),
    ("scoring_version: 3\n", "meta.scoring-version"),
    ("tier_override: P0\n", "meta.override"),
    ("fit_score: 140\n", "meta.fit-score"),
    ("evidence_confidence: total\n", "meta.confidence-enum"),
])
def test_bad_v2_meta_flagged(tmp_path, extra, rule):
    assert rule in rules(tree(tmp_path, extra=extra))


@pytest.mark.parametrize("role,expected", [
    ({"status": "new"}, "not_applied"),
    ({"status": "to_apply"}, "not_applied"),
    ({"status": "not_interested"}, "not_applied"),
    ({"status": "not_interested", "date_applied": "2026-10-01"}, "withdrawn"),
    ({"status": "applied"}, "applied"),
    ({"status": "rejected", "rejection_stage": "application"}, "no_response"),
    ({"status": "rejected", "rejection_stage": "application", "last_inbound": "2026-10-05"}, "applied"),
    ({"status": "rejected", "rejection_stage": "screening"}, "hr_rejected"),
    ({"status": "rejected", "rejection_stage": "interview"}, "technical_rejected"),
    ({"status": "rejected", "rejection_stage": "final"}, "final_round"),
    ({"status": "interviewing"}, "hr_passed"),
    ({"status": "interviewing", "max_stage": "interview"}, "technical_passed"),
    ({"status": "interviewing", "max_stage": "final"}, "final_round"),
    ({"status": "offer"}, "offer"),
])
def test_outcome_derivation(role, expected):
    assert F.outcome(role) == expected


def test_outcome_by_tier_prefers_prediction_and_flags_small_samples():
    roles = [{"status": "rejected", "rejection_stage": "application", "tier": "P1", "predicted_tier": "P0"}] * 5 + \
            [{"status": "applied", "tier": "P1"}, {"status": "new", "tier": "P2"}]
    rows = {r["tier"]: r for r in F.outcome_by_tier(roles)["rows"]}
    assert rows["P0"]["no_response"] == 5 and rows["P0"]["too_few"] is False and rows["P0"]["v1_basis"] == 0
    assert rows["P1"]["applied"] == 1 and rows["P1"]["too_few"] is True and rows["P1"]["v1_basis"] == 1 and rows["P2"]["v1_basis"] == 0
    assert rows["P2"]["applied_total"] == 0


def test_by_tier_cli_has_no_probabilities(tmp_path):
    tree(tmp_path)
    r = run("funnel.py", "--userdata", tmp_path, "--by-tier")
    assert r.returncode == 0, r.stderr
    assert "%" not in r.stdout and "probab" not in r.stdout.lower()
