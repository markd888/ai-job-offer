"""score.py record/override: the first prediction is never overwritten."""
from __future__ import annotations

import json

from scripts_helpers import run
from test_score import assessment

META = """---
company: Acme Pay
position: "Senior PM"
status: new
tier: P1
score: 12
link: https://example.com/jobs/1
---

Notes.
"""


def setup(tmp_path, a=None):
    role = tmp_path / "Acme Pay"
    role.mkdir()
    (role / "meta.md").write_text(META)
    f = tmp_path / "a.json"
    f.write_text(json.dumps(a or assessment()))
    return role, f


def field(role, key):
    for line in (role / "meta.md").read_text().splitlines():
        if line.startswith(f"{key}:"):
            return line.split(":", 1)[1].strip()
    return None


def test_record_writes_file_and_flat_keys(tmp_path):
    role, f = setup(tmp_path)
    r = run("score.py", "record", role, f, "--today", "2026-11-21")
    assert r.returncode == 0, r.stderr
    saved = json.loads((role / "score-2026-11-21.json").read_text())
    assert saved["result"]["tier"] == "P0" and saved["assessment"]["role"]["company"] == "Acme Pay"
    assert field(role, "scoring_version") == "2"
    assert field(role, "predicted_tier") == "P0" and field(role, "initial_fit_score") == "80.0"
    assert field(role, "eligibility") == "eligible"
    assert field(role, "score") == "12"  # v1 score untouched
    assert "Notes." in (role / "meta.md").read_text()


def test_rescore_adds_new_file_and_keeps_prediction(tmp_path):
    role, f = setup(tmp_path)
    run("score.py", "record", role, f, "--today", "2026-11-21")
    first = (role / "score-2026-11-21.json").read_text()
    f.write_text(json.dumps(assessment(scores=(50,) * 5)))
    r = run("score.py", "record", role, f, "--today", "2026-11-21")
    assert r.returncode == 0, r.stderr
    assert (role / "score-2026-11-21.json").read_text() == first
    assert json.loads((role / "score-2026-11-21-v2.json").read_text())["result"]["tier"] == "P2"
    assert field(role, "tier") == "P2" and field(role, "fit_score") == "50.0"
    assert field(role, "predicted_tier") == "P0" and field(role, "initial_fit_score") == "80.0"


def test_override_keeps_prediction_and_survives_rescore(tmp_path):
    role, f = setup(tmp_path)
    run("score.py", "record", role, f, "--today", "2026-11-21")
    r = run("score.py", "override", role, "--tier", "P1", "--reason", "B2B contract only", "--today", "2026-11-22")
    assert r.returncode == 0, r.stderr
    assert field(role, "tier") == "P1" and field(role, "tier_override") == "P1"
    assert field(role, "override_reason") == '"B2B contract only"' and field(role, "override_date") == "2026-11-22"
    assert field(role, "predicted_tier") == "P0"
    run("score.py", "record", role, f, "--today", "2026-11-23")
    assert field(role, "tier") == "P1" and field(role, "predicted_tier") == "P0"
    assert "tier overridden to P1 by user" in (role / "meta.md").read_text()


def test_override_on_v1_role_preserves_v1_tier_as_prediction(tmp_path):
    role, _ = setup(tmp_path)
    run("score.py", "override", role, "--tier", "P0", "--reason", "warm intro", "--today", "2026-11-22")
    assert field(role, "predicted_tier") == "P1" and field(role, "tier") == "P0"


def test_invalid_assessment_writes_nothing(tmp_path):
    a = assessment(); a["dimensions"].pop("domain")
    role, f = setup(tmp_path, a)
    r = run("score.py", "record", role, f, "--today", "2026-11-21")
    assert r.returncode == 1
    assert not list(role.glob("score-*.json")) and (role / "meta.md").read_text() == META


def test_override_needs_reason(tmp_path):
    role, _ = setup(tmp_path)
    assert run("score.py", "override", role, "--tier", "P0", "--reason", " ").returncode == 1
