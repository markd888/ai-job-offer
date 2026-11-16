# Changelog

All notable changes to pm-job-search are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/), and the project aims for
[Semantic Versioning](https://semver.org/).

## job-sweep

`job-sweep` is a second plugin in this repo and versions independently of
pm-job-search. Its releases are listed here under their own heading.

### job-sweep [0.1.0] — 2026-08-05

First release. A standalone weekly sweep for open product roles, installable
without adopting the pipeline tracker.

- Single skill, `/job-sweep:sweep`. Discovery only — no tracking, no scoring, no
  company folders.
- First run takes a CV or three questions; geography is always asked, never
  inferred, because a CV says where you have lived rather than where you want to
  work.
- Keeps `job-sweep/seen-roles.jsonl` so the second week does not re-surface the
  first week's roles. Schema is identical to the full plugin's ledger, so moving
  up loses nothing.
- Roles bucket into strong / possible / edge. No weighted rubric — there is no
  rubric in this profile.
- `/setup` in the full plugin now pre-fills from `job-sweep/profile.md`.
- Five reference files are shared with pm-job-search from a single source under
  `plugin/`; `make sync-sweep` copies them and CI fails the build on drift.
- The sweep says what it's looking for before it starts — your titles, your
  industries, where you'll work, and which job boards it reaches. A profile
  that's drifted out of date shows up in that line, rather than in twenty
  minutes of results aimed at the wrong level. It doesn't wait for you to
  confirm; you already asked for the sweep.
- Each role carries a short reason for where it landed, and every file says what
  the match was made on: the job title, and the location the posting gives.
  Nothing here reads the body of a posting or weighs it against your CV, and a
  strong match means a strong title-and-place match rather than a verdict on the
  role.
- Every file closes with what the sweep couldn't reach — companies that post
  only on their own careers site or through Workday, and anything put up in the
  last day or two. On a week that comes back empty that moves to the top, where
  it explains the silence instead of letting it read as an empty market.

---

## [Unreleased]

### Added
- `/sent <Company>` records an application going out in one step after the user's yes: `status: applied`, `date_applied`, `channel`, optional `referred_by`, the `submitted-<date>/` archive and one History line (`plugin/scripts/record-sent.py`). Before, nothing wrote `date_applied`, so a role marked applied in chat never came up in `/follow-up`.
- `channel` (`referral`, `cold`, `recruiter`, `linkedin`, `company-site`, `other`) and `referred_by` in the meta.md schema; `validate_userdata.py` checks `channel` against the enum (rule `meta.channel-enum`).
- `last_inbound` is written now (`plugin/scripts/record-inbound.py`): by `/today` for contact the user confirms or mentions, by `/interview-analysis` for the interview date, and by `/follow-up` when the user says a company wrote back. It only moves forward. Before, nothing wrote it, so `/today`'s active-interview rule never fired and a company that had replied could still be chased.

### Changed
- One quiet-application rule: `/today` drops its own 14-day "Chase or close" rule and "stale applied" heads-up and uses `follow-ups.py` (10 days since the latest of `date_applied`, `last_inbound`, `last_follow_up`) for both following up and closing.
- `record-sent.py` and `record-inbound.py` share `plugin/scripts/metafile.py` for frontmatter edits.
- `/apply` no longer archives anything or writes to `meta.md`; when the application goes out it hands over to `/sent`.
- `archive-application.py` exposes `archive()` for `record-sent.py` and takes `--no-history`.

## [0.7.2] — 2026-11-16

Tests for the fork's scripts, documented schemas, and a fail-closed Access gate for the cloud copy.

### Fixed
- `follow-ups.py` lists due roles most recent first, as `/follow-up` says; a non-numeric `follow_ups:` no longer crashes it.
- Cloud copy: the Worker now runs first on every request and serves nothing without a valid Cloudflare Access token (RS256 checked against the team's keys, `aud`, `iss`, `exp`). It fails closed until `ACCESS_TEAM_DOMAIN` and `ACCESS_AUD` are set. Before, the raw `/data/*.json` snapshots were served straight from the asset store and protection depended entirely on Access being configured in the dashboard.
- `build_cloud.sh` reads `userdata/` from the directory it's run in (or a path argument) instead of `plugin/userdata`, and stops if it isn't there.

### Added
- Tests for `follow-ups.py`, `ats-check.py`, `archive-application.py` and `cv-build.py`; a Node test for the Worker's Access gate. CI installs the scripts' requirements and the Carlito font so the PDF tests run instead of skipping.
- `plugin/scripts/requirements.txt`; README lists what each part needs. `/apply` says when it skips the PDF and ATS check for want of them.

### Changed
- Schemas document the fork's fields: `phone` (profile), `follow_ups`, `last_follow_up`, `max_stage`, plus `date_applied`, `last_inbound`, `next_event` that `/follow-up` reads.
- `__pycache__/` is no longer committed.
- The privacy scan reads its blocklist from the `PRIVACY_PATTERNS` repo secret instead of a list in the repo.

## [0.7.1] — 2026-11-16

Brings the plugin's dashboard up to the one in daily use.

### Added
- Edit an interview card's next step in place (`next_event`; steps split on new lines or `;`).
- A status change from the dropdown stamps the date it implies (`date_applied`, `date_rejected`, `date_not_interested`) when the role has none.
- Feedback-request counter in the week's progress; warm outreach counts people, not journal lines.
- Briefcase favicon.

### Changed
- Dashboard redesign on one grid and spacing scale, with a claude.ai look; the mini funnel counts each role by the deeper of `rejection_stage` and `max_stage`.
- Active cards are the same size: the role title clamps to two lines and cards share one flexible width.
- Interview rows scroll, the heads-up list is capped, and the side column order is fixed.

## [0.7.0] — 2026-10-30

First release of job-offer, forked from pm-job-search 0.6.0 and renamed (skills are `/job-offer:<skill>`).

### Added
- `scripts/cv-build.py`: one-page CV PDF from the tailored CV markdown; `scripts/cover-letter-build.py` reuses its header.
- `/ats-check` skill and `scripts/ats-check.py`; the expected phone comes from `phone:` in profile.md (new optional field).
- `/follow-up` skill and `scripts/follow-ups.py`; `/today` adds a follow-ups line to the heads-up.
- `scripts/archive-application.py`: `/apply` freezes what was sent when an application goes out.

### Changed
- `/apply` builds the PDF and runs the ATS check before showing the CV.
- Dashboard replaced with the reworked one (strategy-driven goals, interviews first, no Funnel tab, Cloudflare read-only copy). `/dashboard` reuses a server already on port 7890 and never drifts to another port.

## [0.6.0] — 2026-08-25

The voice guidelines were teaching the leaks they banned. `TONE.md` has always
prohibited showing you a file the plugin writes, then sixty lines later handed
the model `"Saved as <path>."` as its template for confirming a write. A
concrete example beats an abstract prohibition, which is why every skill named a
path at exactly that moment. This release fixes the guidelines and the ten
skills that had copied them.

### Changed
- Chat copy no longer names files, paths or raw status values. Confirming a
  write says what changed, not where it lives.
- Internal terms are never shown, rather than "explained the first time". Every
  skill decided its own case was the explained one, which is how `meta.md`,
  `--refresh`, "triage", HTTP codes and "sub-agent context" reached users.
- `/setup` asks less, and asks better. The LinkedIn question is gone — an
  optional field whose value you cannot judge at the moment of asking belongs at
  the point of use. Timezone is derived from your city instead of confirmed. The
  "Ready?" gate before the sweep is removed, since you have already run the
  skill. Timeline and hard filters are open questions rather than option lists
  to pick from; the open hard-filters question immediately drew out two red
  flags that its six-item predecessor had no box for.
- Role suggestions no longer out-rank the person being asked, and proof points
  and moat move out of onboarding into `/today`.
- Found roles are shown as a table, without tier labels or scores.
- Chat summaries have a length budget: one line of framing, the result, and at
  most two short paragraphs. A set of comparable things — roles, companies,
  options — is a table sorted best-first with a short reason against each row.
  What the skill did to get there, how many results came back and which sources
  answered, is no longer reported; it was never yours to act on.
- `/today`'s heads-up items each carry an action, and its pipeline state is
  reduced to counts and progress.
- Two voice rules added: a question must state what the product does with the
  answer or be cut, and the two-clause limit now applies to questions, not only
  to briefs.
- Prompt wording quoted in a `SKILL.md` is an example rather than a fixed
  string, and `TONE.md` governs. Step order, the substance of each ask, each
  step's explicit don'ts, and the interaction form a step specifies all still
  hold. Stated rather than discovered later: copy is now generated per run, so
  run-to-run variance is real.

### Fixed
- `/setup --refresh` skipped positioning entirely, running 1 → 2 → 3 → 5 → 6 → 7
  → 8. It is now offered as a single keep / update / skip.
- `templates/profile.template.md` named specific job titles in a comment, so
  every profile the plugin had written inherited them. Both template comments
  now describe the field instead.
- `/apply`'s missing-CV error is a plain sentence rather than a spec dump.
- `TONE.md`'s own examples. "What's the best email for you?" was listed under
  phrasing that matches the voice, and the hard-filters example offered "no GM
  roles" — which contradicts the target titles of anyone aiming at a GM-shaped
  seat. Examples in that file get copied into skills, so a bad one ships
  everywhere.

### Added
- `job-sweep` has behavioural coverage for the first time. `sweep-smoke` was
  written in 0.5.0 and held out of the release gate until one clean run.

### Internal
The maintainer harness (`tests/judge-calibration/`, which does not ship) scores
a run on five checks:

- `lint` — deterministic, no judge. `scripts/lint_transcript.py` and
  `scripts/validate_userdata.py`: references to skills or files that don't
  resolve, internal jargon and plugin-owned paths in user-facing copy, bare
  fenced blocks used as chat summaries, prior-state prompts on a first run, and
  cadence numbers that don't trace to the user's own plan.
- `groundedness` (gating, new) — every fact, number, name, date, filename and
  URL must trace to a file read this run, a fetch this run, or an earlier user
  turn. One ungrounded claim fails the run.
- `conformance` (gating) — the journey's required criteria. Renamed from
  `spec-criteria`.
- `coherence` (advisory, new) — nothing arrives cold, recent context outweighs
  old, no repetition or self-contradiction, stable vocabulary across skills.
- `tone` (advisory) — `TONE.md`, judged holistically, with a recurring pattern
  counting as a failure however small each instance.

The gate is lint AND groundedness AND conformance. `open-critique` and
`lint-checklist` are deleted; six of the latter's seven rules are now scripts,
and the seventh was already duplicated in `tone.md`. The judge runs once per
rubric and no longer decides the deterministic checks — it transcribes them.
Rubrics are validated against human labels, and each carries a worked-examples
section of borderline cases, enforced by a test.

---

## [0.5.0] — 2026-08-10

The test strategy inverted. Almost all testing weight used to sit in an
expensive LLM-judged conversation harness that ran every few weeks; the
deterministic layer underneath barely existed. This release flips that.

### Changed
- Test harness restructured: journeys cut 8 → 3 (+ sweep-smoke, run-by-name);
  `cold-start-cv`, `reflection`, and both `case-practice` journeys retired.
- Judge calibration is now per rubric, not per run. Label files carry
  separate Hard-violations and Spec-gaps verdicts; the overall verdict is
  derived from those two rather than recorded by hand, and a mismatch
  between the judge's stated overall and its own sub-verdicts is reported
  as a self-contradiction.
- Phase 3.5 schema validation now runs `scripts/validate_userdata.py`
  (meta.md + profile.md + strategy.md + research-brief), shared with CI.

### Added
- `harness-checks` CI: deterministic pytest layer over snapshots, schemas,
  and golden-set labels — 73 tests, $0, every push.
- Golden set for `/evaluate-position` (12 labeled synthetic JDs) with a
  release-time agreement gate (`tests/golden/evaluate-position/`).
- Judge-calibration tooling: `tests/judge-calibration/grade-judge.html`, a
  single-file browser tool for grading the judge with a blind-pass gate and
  a live precision/recall readout, and `tests/judge-calibration/stats.py`,
  its command-line equivalent, with the adjudication protocol in
  `tests/judge-calibration/README.md`. The tool shows the transcript and the
  rubric beside the findings, and links a finding to the transcript turn it
  cites; the blind-pass gate keeps every judge-derived value — findings,
  verdicts, advisory counts and the sidebar readout — out of the page until
  you have written your own list.
- Frozen judge-calibration corpus: 31 files across 11 judged runs in 7
  dated directories, scrubbed and committed under
  `tests/judge-calibration/runs/`.
- `plugin/skills/test-personas/manual-checklist.md` — the four manual
  release checks, out of chat lore and into the repo.
- Schema docs: `plugin/schemas/profile.md.schema.md`,
  `plugin/schemas/strategy.md.schema.md`,
  `plugin/schemas/research-brief.md.schema.md`.

### Fixed
- Privacy blocklist gained one more city-name term surfaced during
  calibration-corpus scrubbing (`.github/workflows/privacy-check.yml`,
  `CONTRIBUTING.md`).
- 22 research briefs across the test snapshots gained the
  `**Source:** <url>` first line `plugin/skills/evaluate-position/SKILL.md`
  requires, and `tests/snapshots/contrarian-messy/profile.md` gained the
  tier rubric it was missing — fixture repairs the new schema validator
  surfaced.

## [0.4.0] — 2026-08-04

CV-first onboarding. `/setup` now reads a CV up front and pre-fills what it can,
so most steps are a confirmation rather than a blank box.

### Changed

- `/setup` is nine steps instead of twelve questions. When a CV is found, name,
  city, email and LinkedIn arrive as a single confirmation line, and target
  titles and industries are offered as multi-selects derived from the CV, each
  shown with the roles the inference came from.
- Timeline is a bucket choice (under 2 months / 2-4 / 4+ / exact date) rather than
  a typed date. A concrete `target_offer_date` is still what gets stored, so
  `/today`'s countdown is unaffected.
- Hard filters are a multi-select over common red flags, with a free-text escape.
- Salary band is the one step deliberately left as free text. Generating bands
  would mean inventing market data the plugin has no source for. Everywhere
  else offers structured input — though with no CV, the name/city/email,
  target-title and industry steps still fall back to typing, and several
  steps keep a free-text escape alongside their options.
- "Companies of interest" moved out of `/setup` and into the first `/job-search`
  run, where the context makes it answerable.

### Added

- `plugin/references/cv-extraction.md` — shared CV-reading rules, split by
  confidence: facts read off the page, inferences derived from the CV's shape.
  Carries the governing rule that a field the CV lacks is asked, never guessed.
- `cold-start-cv` test journey and its `empty-with-cv` snapshot, covering the
  CV-present path. `cold-start` now covers the no-CV path.

## [0.3.0] — 2026-07-11

First stable cut of the 0.3 line (developed across `v0.3.0-beta.1`…`beta.6`).
Adds a case-interview practice track, an end-to-end test harness, and a
structural fix for sub-agent data drift.

### Added
- `/case-practice [Company]` — multiple-choice rapid-recognition drill across the
  MC-able case types (product sense, metric movement, metric tree, prioritisation,
  behavioural-signal), scored against an 80% readiness gate, with an 8-type
  case-interview reference and a 5-drill practice-methodology guide.
- `test-personas` — maintainer-only end-to-end harness (5-phase pipeline, 3
  personas, 6 journeys, LLM judge with 4 rubrics, Phase 3.5 schema validation)
  plus `plugin/memory.md` as a regression-lessons log. Filtered from `/help`.
- `plugin/schemas/meta.md.schema.md` — canonical `meta.md` contract (required
  keys, status enum, forbidden drift keys) shared by every reader.
- `/job-search` anti-repeat: a persistent append-only seen-ledger
  (`userdata/outputs/seen-roles.jsonl`) plus a shared `dedup-normalization.md`
  reference so a role stays suppressed even after its folder is deleted, and
  near-duplicate titles surface as "likely repeats" instead of re-filing.

### Changed
- `tier:` notation is now canonically `P0` / `P1` / `P2` / `unscored` across the
  schema, templates, and skills, matching what the dashboard already renders.
- `/job-search` sub-agent contracts key `position` (never `role`) and dedup on
  `(company, position)`; both sub-agent prompts carry an explicit output contract.
- Docs corrected to the true inventory (13 user-facing skills + 6 agents) with the
  `case-practice` row added; `CONTRIBUTING.md` no longer claims integrations are
  out of scope (they ship opt-in via `/integrations`).

### Fixed
- Sub-agent fidelity drift — added post-write validation gates (`/job-search`) and
  read-back assertions (`/evaluate-position`, `/today`) that reject invented field
  names, bad status values, and placeholder links like `(url not captured)`.
- Privacy CI now scans all branches (not just `main`); the workspace `CLAUDE.md`
  and author-private files are gitignored so they can't be committed accidentally.

## [0.2.1] — 2026-05-25

First public release: the pure-markdown core (8 skills + 6 reviewer/coach agents),
the opt-in `/integrations` MCP layer (Granola / Calendar / Gmail), the browser
dashboard, and the TONE.md voice guidelines with a lint checklist.

[0.4.0]: https://github.com/archugunov/pm-job-search/releases/tag/v0.4.0
[0.3.0]: https://github.com/archugunov/pm-job-search/releases/tag/v0.3.0
[0.2.1]: https://github.com/archugunov/pm-job-search/releases/tag/v0.2.1
