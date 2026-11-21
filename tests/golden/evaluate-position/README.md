# Golden set — /evaluate-position

32 synthetic JDs with frozen labels (`cases/*.json`), scored against the
frozen rubric in `profile.md` (a copy of the maya-active snapshot's —
never rebased, never edited without re-deriving every label).

Each case has `label_v2` (scoring v2 — all 32). The 12 original cases also keep
their v1 `label` as a regression subset; where the v2 tier differs, the case says
why in `tier_change_reason` (the three filter cases become `blocked` → P2 instead
of "not scored", and `p2-principal-devtools` moves to P1 because a 3x-ARR
company lifts a weak fit one tier).

`label_v2` fields: `eligibility` (eligible / needs_review / blocked), `must_fail`
(requirements that must come back FAIL), `must_unknown` (keywords whose
requirement must come back UNKNOWN, never FAIL), `evidence` (allowed evidence
classes per dimension, only where the case tests it), `fit_range`,
`attractiveness` (allowed levels), `tier`, `provenance`, optional `edge_note`.

Two layers:

**CI ($0, every push):** `tests/test_golden_cases.py` checks v1 arithmetic and
that every v2 label is self-consistent under `scoring_schema.py`: each allowed
fit end and attractiveness level must give the labelled tier, so a label that
straddles a threshold fails. `tests/test_golden_grade.py` tests the grader. No LLM.

**Release time (LLM, run with the release-gate journeys):**

1. In a fresh Claude Code session at the repo root, prompt:

   > For each JSON file in tests/golden/evaluate-position/cases/, run the
   > /job-offer:evaluate-position scoring procedure from
   > plugin/references/evaluate-position-scoring.md on the case's "jd" text,
   > using tests/golden/evaluate-position/profile.md as the profile (and as the
   > only evidence source — there is no cv.md). Do NOT write to userdata/ and
   > do NOT ask interactive questions. Write each assessment to a temp file and
   > run `python3 -I plugin/scripts/score.py compute <file> --profile
   > tests/golden/evaluate-position/profile.md`. Collect a JSON array of
   > {"id", "eligibility", "requirements": [{"requirement","status","jd_quote"}],
   > "dimensions": {<dim>: {"evidence_class","evidence"}}, "attractiveness",
   > "fit_score", "tier"} — the requirements, dimensions and attractiveness from
   > your assessment, eligibility / fit_score / tier from score.py. Write it to
   > tests/golden/evaluate-position/results-<YYYY-MM-DD>.json.

2. Grade: `python3 tests/golden/evaluate-position/grade.py tests/golden/evaluate-position/results-<date>.json`
3. Gate (exit 0 required before tagging): tier agreement ≥ 0.8, eligibility
   ≥ 0.85, fit in range ≥ 0.7, every expected FAIL found, every expected UNKNOWN
   reported as UNKNOWN, no false block, every evidence quote found verbatim in
   the profile. On FAIL, the per-case table shows which JD drifted; check the
   reference's guidance first, the label second (labels lose only if the
   procedure genuinely supports the new reading — then fix the label AND say so
   in the commit).

The v1 result shape (`{"id","tier","score","matched_filter"}`) still grades
against the 12 v1 labels, for comparing an old run.

`results-*.json` files are throwaway run artifacts — gitignored, not part
of the set. Provenance: `author-derived-v1` / `author-derived-v2` (derived by
hand from the rubric and the procedure). Upgrade path: replace individual labels
after adjudicated disagreement, bumping provenance.
