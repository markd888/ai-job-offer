"""Rules for /evaluate-position scoring v2: validation, fit arithmetic, eligibility, tiers.

Not a CLI — score.py loads this file by path (scripts run with `python3 -I`).
Claude fills the assessment JSON (requirements, evidence, explanations); this
module owns every number and every rule, so the skill never restates them.
Schema and examples: plugin/schemas/score.schema.md.
"""
from __future__ import annotations

import re
from typing import Any

SCORING_VERSION = 2

DIMENSIONS = ("role_responsibility", "skills_experience", "domain", "seniority_ownership",
              "competitive_advantage")
DEFAULT_WEIGHTS = {"role_responsibility": 30, "skills_experience": 25, "domain": 20,
                   "seniority_ownership": 15, "competitive_advantage": 10}
DEFAULT_THRESHOLDS = {"p0": 80, "p1": 65}

ELIGIBILITY_STATUSES = ("PASS", "FAIL", "UNKNOWN", "NOT_APPLICABLE")
REQUIREMENT_SOURCES = ("hard_filter", "jd")
EVIDENCE_CLASSES = ("EXPLICIT", "TRANSFERABLE", "WEAK", "MISSING", "CONTRADICTED")
EVIDENCE_SOURCES = ("cv", "profile")
CONFIDENCE = ("high", "medium", "low")
ATTRACTIVENESS = ("high", "medium", "low", "unknown")
TIERS = ("P0", "P1", "P2")

# Share of weight backed by EXPLICIT or TRANSFERABLE evidence → evidence_confidence.
CONFIDENCE_CUTS = (("high", 0.8), ("medium", 0.5))


def _err(errors: list[str], path: str, msg: str) -> None:
    errors.append(f"{path}: {msg}")


def validate(a: Any) -> list[str]:
    """Every problem with an assessment, as 'path: message'. Empty means valid."""
    e: list[str] = []
    if not isinstance(a, dict):
        return ["$: assessment must be a JSON object"]
    if a.get("scoring_version") != SCORING_VERSION:
        _err(e, "scoring_version", f"must be {SCORING_VERSION}")
    role = a.get("role")
    if not isinstance(role, dict) or not all(isinstance(role.get(k), str) and role.get(k)
                                             for k in ("company", "position")):
        _err(e, "role", "needs non-empty company and position")

    elig = a.get("eligibility")
    if not isinstance(elig, list):
        _err(e, "eligibility", "must be a list (empty when nothing is mandatory)")
        elig = []
    for i, r in enumerate(elig):
        p = f"eligibility[{i}]"
        if not isinstance(r, dict):
            _err(e, p, "must be an object"); continue
        if not r.get("requirement"):
            _err(e, p, "requirement is required")
        if r.get("source") not in REQUIREMENT_SOURCES:
            _err(e, p, f"source must be one of {REQUIREMENT_SOURCES}")
        if r.get("status") not in ELIGIBILITY_STATUSES:
            _err(e, p, f"status must be one of {ELIGIBILITY_STATUSES}")
        if not isinstance(r.get("jd_quote"), str) or not r.get("jd_quote"):
            _err(e, p, 'jd_quote is required — the JD text, or "not stated"')
        if r.get("status") == "UNKNOWN" and r.get("jd_quote") not in (None, "", "not stated") \
                and not r.get("note"):
            _err(e, p, "UNKNOWN with a JD quote needs a note saying why it can't be decided")

    for i, w in enumerate(a.get("warnings") or []):
        if not isinstance(w, dict) or not w.get("anti_goal"):
            _err(e, f"warnings[{i}]", "needs anti_goal")

    dims = a.get("dimensions")
    if not isinstance(dims, dict):
        _err(e, "dimensions", "must be an object"); dims = {}
    for k in DIMENSIONS:
        d = dims.get(k)
        p = f"dimensions.{k}"
        if not isinstance(d, dict):
            _err(e, p, "missing"); continue
        s = d.get("score")
        if not isinstance(s, (int, float)) or isinstance(s, bool) or not 0 <= s <= 100:
            _err(e, p, "score must be a number 0–100")
        for f in ("requirement", "explanation"):
            if not d.get(f):
                _err(e, p, f"{f} is required")
        cls = d.get("evidence_class")
        if cls not in EVIDENCE_CLASSES:
            _err(e, p, f"evidence_class must be one of {EVIDENCE_CLASSES}")
        if d.get("confidence") not in CONFIDENCE:
            _err(e, p, f"confidence must be one of {CONFIDENCE}")
        ev = d.get("evidence")
        if not isinstance(ev, list):
            _err(e, p, "evidence must be a list"); ev = []
        if cls not in ("MISSING", None) and not ev:
            _err(e, p, f"{cls} needs at least one evidence quote")
        if cls == "MISSING" and ev:
            _err(e, p, "MISSING means no evidence — drop the quotes or change the class")
        for j, q in enumerate(ev):
            if not isinstance(q, dict) or not q.get("quote") or q.get("source") not in EVIDENCE_SOURCES:
                _err(e, f"{p}.evidence[{j}]", f"needs quote and source in {EVIDENCE_SOURCES}")
    for k in dims:
        if k not in DIMENSIONS:
            _err(e, f"dimensions.{k}", f"unknown dimension; expected {DIMENSIONS}")

    att = a.get("attractiveness")
    if not isinstance(att, dict) or att.get("level") not in ATTRACTIVENESS:
        _err(e, "attractiveness", f"needs level in {ATTRACTIVENESS}")
    elif att.get("level") != "unknown" and not att.get("sources"):
        _err(e, "attractiveness", "a known level needs sources")
    return e


def validate_config(weights: dict, thresholds: dict) -> list[str]:
    e: list[str] = []
    for k, v in weights.items():
        if k not in DIMENSIONS:
            e.append(f"fit_weights.{k}: unknown dimension; expected {DIMENSIONS}")
        elif not isinstance(v, (int, float)) or v < 0:
            e.append(f"fit_weights.{k}: must be a non-negative number")
    if sum(v for v in weights.values() if isinstance(v, (int, float))) <= 0:
        e.append("fit_weights: must not all be zero")
    for k in ("p0", "p1"):
        v = thresholds.get(k)
        if not isinstance(v, (int, float)) or not 0 <= v <= 100:
            e.append(f"fit_thresholds.{k}: must be a number 0–100")
    if not e and thresholds["p0"] < thresholds["p1"]:
        e.append("fit_thresholds: p0 must be >= p1")
    return e


def normalise(weights: dict) -> dict[str, float]:
    """Missing dimensions take their default; the result sums to 1."""
    full = {k: float(weights.get(k, DEFAULT_WEIGHTS[k])) for k in DIMENSIONS}
    total = sum(full.values())
    return {k: v / total for k, v in full.items()}


def eligibility_status(reqs: list[dict]) -> tuple[str, list[str], list[str]]:
    """(status, failed requirements, unknown requirements). NOT_APPLICABLE is ignored."""
    failed = [r["requirement"] for r in reqs if r["status"] == "FAIL"]
    unknown = [r["requirement"] for r in reqs if r["status"] == "UNKNOWN"]
    return ("blocked" if failed else "needs_review" if unknown else "eligible"), failed, unknown


def evidence_confidence(dims: dict, w: dict[str, float]) -> str:
    backed = sum(w[k] for k in DIMENSIONS if dims[k]["evidence_class"] in ("EXPLICIT", "TRANSFERABLE"))
    for level, cut in CONFIDENCE_CUTS:
        if backed >= cut - 1e-9:
            return level
    return "low"


def tier_for(fit: float, thresholds: dict) -> str:
    return "P0" if fit >= thresholds["p0"] else "P1" if fit >= thresholds["p1"] else "P2"


def shift(tier: str, steps: int) -> str:
    return TIERS[max(0, min(len(TIERS) - 1, TIERS.index(tier) - steps))]


def compute(a: dict, weights: dict | None = None, thresholds: dict | None = None) -> dict:
    """The derived result. Assumes validate(a) and validate_config passed.

    Tier rule (documented in score.schema.md):
      1. fit tier from fit_score and thresholds;
      2. attractiveness high → up one tier, low → down one, medium/unknown → none
         (at most one step, by construction);
      3. eligibility blocked → capped at P2 (attractiveness can't lift it past);
      4. needs_review keeps the tier and lists what's pending.
    """
    w = normalise(weights or {})
    t = {**DEFAULT_THRESHOLDS, **(thresholds or {})}
    dims = a["dimensions"]
    fit = round(sum(dims[k]["score"] * w[k] for k in DIMENSIONS), 1)
    status, failed, unknown = eligibility_status(a["eligibility"])
    fit_tier = tier_for(fit, t)
    level = a["attractiveness"]["level"]
    tier = shift(fit_tier, {"high": 1, "low": -1}.get(level, 0))
    if status == "blocked":
        tier = "P2"
    gaps = [k for k in DIMENSIONS if dims[k]["evidence_class"] == "CONTRADICTED"]
    missing = [k for k in DIMENSIONS if dims[k]["evidence_class"] == "MISSING"]
    return {
        "scoring_version": SCORING_VERSION,
        "fit_score": fit,
        "fit_tier": fit_tier,
        "attractiveness": level,
        "tier": tier,
        "eligibility": status,
        "failed": failed,
        "pending": unknown,
        "warnings": [x["anti_goal"] for x in a.get("warnings") or []],
        "evidence_confidence": evidence_confidence(dims, w),
        "confirmed_gaps": gaps,
        "missing_evidence": missing,
        "weights": {k: round(v * 100, 2) for k, v in w.items()},
        "thresholds": t,
    }


def _block(text: str, key: str) -> dict[str, float] | None:
    """A flat `key:` map of numbers from profile frontmatter; None when absent."""
    m = re.search(rf"^{key}:[^\n]*\n((?:[ \t]+[A-Za-z_0-9]+:[^\n]*\n?)+)", text, re.M)
    if not m:
        return None
    out: dict[str, float] = {}
    for line in m.group(1).splitlines():
        k, _, v = line.strip().partition(":")
        v = v.split("#", 1)[0].strip()
        try:
            out[k] = float(v)
        except ValueError:
            out[k] = v  # type: ignore[assignment]  # validate_config reports it
    return out


def config_from_profile(text: str) -> tuple[dict, dict]:
    """(fit_weights, fit_thresholds) from profile.md; defaults fill what's absent.
    A v1 profile (tier_weights only) gets the defaults."""
    fm = text.split("---", 2)[1] if text.startswith("---") else text
    return _block(fm, "fit_weights") or {}, {**DEFAULT_THRESHOLDS, **(_block(fm, "fit_thresholds") or {})}
