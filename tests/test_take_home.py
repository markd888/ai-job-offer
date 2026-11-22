"""Take-home checks and freeze (plugin/scripts/take-home.py, #10). Synthetic brief and draft only."""
from __future__ import annotations

import json

from scripts_helpers import load, run

th = load("take-home.py")

LIMITS = {"max_words": 400, "max_requirements": 3, "requirements_heading": "Requirements",
          "required_sections": ["Problem", "Assumptions", "Requirements", "Metrics"],
          "assumptions": "marked", "ai_policy": "disclose", "penalise_over_documentation": True}

GOOD = """---
company: Acme Pay
---
# Take-home — Acme Pay

## Problem
Card approvals for new merchants are low [A1]. We need a first version of an approval flow.

## Assumptions
- [A1] New merchants are under 30 days old.
- [A2] Risk scores arrive within two seconds.

## Requirements
1. Score each new merchant on signup [A2].
2. Route low scores to manual review.
   - Reviewers see the score reason.
3. Notify the merchant of the outcome.

## Metrics
- Approval rate for new merchants.

## AI use
Used an assistant to check grammar. Every decision is mine.
"""


def statuses(res):
    return {r["check"]: r["status"] for r in res["results"]}


def test_a_clean_draft_passes():
    res = th.check(GOOD, LIMITS)
    s = statuses(res)
    assert res["exit_code"] == 0
    assert s["words"] == "pass" and s["requirements"] == "pass" and s["assumptions"] == "pass"
    assert s["AI use note"] == "pass" and s["section: Metrics"] == "pass"


def test_word_cap_and_near_cap():
    assert statuses(th.check(GOOD, {"max_words": 20}))["words"] == "fail"
    n = th.words(GOOD)
    assert statuses(th.check(GOOD, {"max_words": n + 1}))["words near cap"] == "warn"


def test_words_ignore_frontmatter_and_code():
    assert th.words("---\na: b c d\n---\nOne two.\n```\nx y z\n```\n") == 2


def test_too_many_requirements_counts_top_level_only():
    draft = GOOD.replace("3. Notify", "3. Log it.\n4. Notify")
    s = statuses(th.check(draft, LIMITS))
    assert s["requirements"] == "fail"
    assert "4 of 3" in next(r["detail"] for r in th.check(draft, LIMITS)["results"] if r["check"] == "requirements")


def test_missing_section_fails():
    draft = GOOD.replace("## Metrics\n- Approval rate for new merchants.\n", "")
    assert statuses(th.check(draft, LIMITS))["section: Metrics"] == "fail"


def test_assumption_markers_must_match_the_log():
    unlogged = GOOD.replace("Notify the merchant", "Notify the merchant [A3]")
    res = th.check(unlogged, LIMITS)
    assert statuses(res)["assumptions"] == "fail"
    assert "A3" in next(r["detail"] for r in res["results"] if r["check"] == "assumptions")
    unused = GOOD.replace("on signup [A2]", "on signup")
    assert "never marked" in next(r["detail"] for r in th.check(unused, LIMITS)["results"] if r["check"] == "assumptions")


def test_ai_policy():
    no_note = GOOD.split("## AI use")[0]
    assert statuses(th.check(no_note, LIMITS))["AI use note"] == "fail"
    assert statuses(th.check(no_note, {"ai_policy": "forbidden"}))["AI policy"] == "warn"
    assert statuses(th.check(no_note, {}))["AI policy"] == "warn"            # unknown → ask
    assert "AI policy" not in statuses(th.check(no_note, {"ai_policy": "allowed"}))


def test_over_documentation_warns_never_fails():
    draft = GOOD + "\n## Appendix: competitor scan\nLong notes.\n\n## Rollout plan\nPhases.\n"
    res = th.check(draft, LIMITS)
    s = statuses(res)
    assert s["over-documentation"] == "warn" and s["unasked sections"] == "warn"
    assert res["exit_code"] == 0


def test_no_limits_means_no_hard_checks():
    assert th.check("# Anything\nsome words", {"ai_policy": "allowed"})["exit_code"] == 0


def test_cli_check_and_freeze(tmp_path):
    draft = tmp_path / "take-home-draft.md"
    draft.write_text(GOOD)
    limits = tmp_path / "limits.json"
    limits.write_text(json.dumps(LIMITS))
    res = run("take-home.py", "check", draft, "--limits", limits)
    assert res.returncode == 0 and "PASS" in res.stdout
    limits.write_text(json.dumps({**LIMITS, "max_words": 10}))
    assert run("take-home.py", "check", draft, "--limits", limits).returncode == 1

    role = tmp_path / "companies" / "Acme Pay"
    role.mkdir(parents=True)
    (role / "meta.md").write_text("---\ncompany: Acme Pay\nstatus: interviewing\n---\n")
    brief = tmp_path / "brief.md"
    brief.write_text("Design an approval flow. 400 words max.")
    res = run("take-home.py", "freeze", role, draft, "--brief", brief, "--limits", limits, "--date", "2026-11-22")
    assert res.returncode == 0
    dest = role / "submitted-take-home-2026-11-22"
    assert {p.name for p in dest.iterdir()} == {"take-home-draft.md", "brief.md", "limits.json", "manifest.md"}
    meta = (role / "meta.md").read_text()
    assert "take-home submitted (take-home-draft.md)" in meta and "status: interviewing" in meta
    again = run("take-home.py", "freeze", role, draft, "--date", "2026-11-22")
    assert again.returncode != 0 and "--force" in again.stderr


def test_section_limits_and_time_box():
    draft = ("## Recommendation\nKeep provider B. Fix retry routing first. Then re-measure.\n\n"
             "## Findings\n- Approval rate 0.8 vs 0.6, e.g. for BR.\n")
    lim = {"section_limits": {"Recommendation": {"max_sentences": 2, "max_words": 60}}, "time_box_minutes": 15,
           "ai_policy": "allowed"}
    res = th.check(draft, lim)
    s = statuses(res)
    assert s["Recommendation: sentences"] == "fail" and s["Recommendation: words"] == "pass"
    assert s["time box"] == "info"
    ok = draft.replace(" Then re-measure.", "")
    assert th.check(ok, lim)["exit_code"] == 0
    assert th.sentences("Rate 0.81 vs 0.65, e.g. on retries.") == 1
    assert statuses(th.check(draft, {"section_limits": {"Summary": {"max_words": 5}}}))["Summary: limit"] == "fail"
