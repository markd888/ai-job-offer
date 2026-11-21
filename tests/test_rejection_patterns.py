"""Where rejections cluster (plugin/scripts/rejection-patterns.py, #11). Synthetic roles only."""
from __future__ import annotations

from scripts_helpers import load, run

rp = load("rejection-patterns.py")


def rej(stage="application", note="", **kw):
    return {"status": "rejected", "rejection_stage": stage, "rejection_note": note,
            "date_applied": "2026-10-01", **kw}


def pats(res):
    return {(p["dimension"], p["group"]): p["pattern"] for p in res["patterns"]}


def test_no_rejections():
    res = rp.analyse([{"status": "applied", "date_applied": "2026-10-01"}])
    assert res["rejected"] == 0 and rp.render(res).startswith("No rejections yet")


def test_never_applied_roles_are_ignored():
    assert rp.analyse([{"status": "new"}, {"status": "to_apply"}])["applied"] == 0


def test_three_rejections_at_one_stage_is_a_pattern_application_never_is():
    res = rp.analyse([rej("interview")] * 3 + [rej("screening")] * 2 + [rej()] * 20)
    p = pats(res)
    assert p[("stage", "interview")] == "repeated"
    assert ("stage", "screening") not in p and ("stage", "application") not in p


def test_low_and_high_reply_rate_by_tier():
    roles = ([rej(tier="P0")] * 19 + [rej("screening", tier="P0")]          # 1/20
             + [rej("screening", tier="P1")] * 4 + [rej(tier="P1")] * 6      # 4/10
             + [rej(tier="P2")] * 10 + [rej("screening", tier="P2")])        # 1/11
    res = rp.analyse(roles)                                                  # overall 6/41 ≈ 15%
    p = pats(res)
    assert p[("tier", "P0")] == "low" and p[("tier", "P1")] == "high"
    assert ("tier", "P2") not in p


def test_small_groups_and_unknowns_are_never_patterns():
    roles = [rej(tier="P2")] * 4 + [rej("screening")] * 2 + [rej()] * 30
    res = rp.analyse(roles)
    assert not any(d in ("tier", "channel") for d, _ in pats(res))
    assert {"dimension": "channel", "unknown": 36, "of": 36} in res["data_gaps"]


def test_zero_of_five_at_a_low_overall_rate_is_not_low():
    roles = [rej(tier="P2")] * 5 + [rej("screening", tier="P0")] * 3 + [rej(tier="P0")] * 40
    assert ("tier", "P2") not in pats(rp.analyse(roles))


def test_predicted_tier_wins_over_current_tier():
    res = rp.analyse([rej(tier="P2", predicted_tier="P0")])
    assert res["dimensions"]["tier"][0]["group"] == "P0"


def test_instant_rejections_are_flagged():
    roles = [rej(date_rejected="2026-10-01")] * 3 + [rej(date_rejected="2026-10-20")] * 5
    p = pats(rp.analyse(roles))
    assert p[("speed", "instant (≤1 day)")] == "instant"


def test_levels_from_titles():
    assert rp.level_of("Head of Product, Payments") == "head"
    assert rp.level_of("Senior Product Manager") == "senior"
    assert rp.level_of("Lead PM, Checkout") == "lead/principal"
    assert rp.level_of("Product Manager") == "pm"
    assert rp.level_of("Application 2026-08-03") == "unknown" and rp.level_of("") == "unknown"


def test_template_notes_are_counted_not_quoted():
    roles = [rej(note="No reply 14+ days after applying; closed as a silent rejection"),
             rej(note="Other candidates align more closely with our current needs"),
             rej("interview", note="Wanted hands-on SQL depth in the case round")]
    res = rp.analyse(roles)
    assert res["template_notes"] == 2
    assert [s["note"] for s in res["specific_reasons"]] == ["Wanted hands-on SQL depth in the case round"]
    assert "Other candidates" not in rp.render(res)


def test_since_filters_by_application_date():
    roles = [rej(date_applied="2026-09-01"), rej(date_applied="2026-11-01")]
    assert rp.analyse(roles, rp.date(2026, 10, 1))["rejected"] == 1


def test_cli_reads_meta_files(tmp_path):
    for i, (stage, tier) in enumerate([("interview", "P0")] * 3 + [("application", "P1")] * 2):
        d = tmp_path / "companies" / f"Acme{i}"
        d.mkdir(parents=True)
        (d / "meta.md").write_text(
            f'---\ncompany: Acme{i}\nposition: "Senior Product Manager"\nstatus: rejected\n'
            f'date_applied: 2026-10-01\nrejection_stage: {stage}\ntier: {tier}\n---\n')
    res = run("rejection-patterns.py", "--userdata", tmp_path)
    assert res.returncode == 0
    assert "interview: 3 rejected  ← repeated stage" in res.stdout
    assert run("rejection-patterns.py", "--userdata", tmp_path / "nope").returncode == 2
