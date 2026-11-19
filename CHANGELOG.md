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

- `plugin/scripts/freehire.py` — Freehire Discovery groundwork (#26): case-insensitive MCP detection, `freehire_filters` in `profile.md` with enum validation (also rule `profile.freehire-filters` in `validate_userdata.py`), the `ignored_params` guard, title allow/deny, agency exclusion and dedup that prefers the employer's ATS link. `/setup` writes the filters when the MCP is connected. Wiring into `/job-search` follows separately.

### Fixed

- Freehire screening (#26): a company name with the job's city appended ("Gameloft Barcelona" from LinkedIn, "Gameloft" from the ATS) is now one employer, so the role isn't kept twice; the default title allowlist also passes `PM` / `GPM` abbreviations ("Senior PM, Payments") and "Head of <area> Product", while deny words still win; aggregator copies (Adzuna, Arbeitnow, Himalayas, Just Join IT, WTTJ, SpainJobs, Jobindex) lose to the employer's ATS link like LinkedIn does.

## [0.8.0] — 2026-11-17

The application loop closes end to end: record what was sent and by which channel, track the people who help, chase quiet applications from one rule, write cover letters, see the funnel by channel, and wrap up a search after an offer.

### Added
- `/sent <Company>` records an application going out in one step after the user's yes: `status: applied`, `date_applied`, `channel`, optional `referred_by`, the `submitted-<date>/` archive and one History line (`plugin/scripts/record-sent.py`). Before, nothing wrote `date_applied`, so a role marked applied in chat never came up in `/follow-up`.
- `channel` (`referral`, `cold`, `recruiter`, `linkedin`, `company-site`, `other`) and `referred_by` in the meta.md schema; `validate_userdata.py` checks `channel` against the enum (rule `meta.channel-enum`).
- `last_inbound` is written now (`plugin/scripts/record-inbound.py`): by `/today` for contact the user confirms or mentions, by `/interview-analysis` for the interview date, and by `/follow-up` when the user says a company wrote back. It only moves forward. Before, nothing wrote it, so `/today`'s active-interview rule never fired and a company that had replied could still be chased.
- `/interview-prep` works from what the employer read: the latest `submitted-*/` archive (CV and posting as sent), else the CV dated on or before `date_applied`, and says which it used (`**Sent materials:**` in the doc header). `interviewer-simulator` drills the sent CV too.
- `/help`, `plugin/README.md` and `references/recommended-flow.md` list `/ats-check`, `/sent` and `/follow-up`; end-of-skill nudges can suggest them (record a sent application, chase a quiet one, re-check an edited CV, thank an interviewer). `tests/test_help_card.py` fails when a skill ships without a help-card entry.
- `date_rejected`, `rejection_stage`, `rejection_note` and `date_not_interested` are documented in the meta.md schema.
- People as records: `userdata/people/<slug>.md` with relation, channel, linked roles and a `## Log` of every ask and reply in one fixed line shape (`schemas/person.md.schema.md`; rules and enums in `plugin/scripts/people.py`). `validate_userdata.py` adds `person.required`, `person.relation-enum`, `person.channel-enum`, `person.role-link`, `person.log-format`.
- `/outreach <person|Company>` drafts a referral ask (with a forwardable blurb), intro ask, reach-out, follow-up or thank-you from facts only — the person file, profile, master CV, submitted materials — and logs it after the user says it went out (`plugin/scripts/record-outreach.py`). Drafts only.
- `/sent --referred-by` logs the referral on the referrer's people file (creating it if new) and links the role.
- Maya's example install and the `maya-active` snapshot have three people (a former colleague at Wagestream, a referrer, Lendable's CEO); the `active-loop` harness journey ends with a referral ask.
- `/cover-letter <Company>` writes a 150–250-word letter answering the posting's top two or three needs with one proof point each, from the tailored or master CV, profile, research brief and the user's answers; it lists in chat what it did NOT claim, saves `cover-<date>.md` and builds the PDF with `cover-letter-build.py`. `/sent` already archives both. `/apply` now offers it in its closing question instead of forbidding cover letters.
- `plugin/scripts/cover-letter-check.py` — the mechanical backstop the skill runs before showing a letter: fails on any number or capitalised name not found in the sources, on a length outside 150–250 words, and on headings or bullets; counts `[CONFIRM: …]` markers.
- `tests/fixtures/cover-letter/` — a letter for Maya's Plaid role with a claim-by-claim trace to her CV, profile and the brief; `tests/test_cover_letter.py` checks every sentence is a traced claim or declared framing, the check catches an invented metric and employer, the PDF builds to one page, and `/sent`'s archive picks up the letter and its PDF.
- Funnel by channel: `plugin/scripts/funnel.py` counts, per `channel` (`unknown` when none is recorded), how many applications reached screening, interview, final and offer, with rates only from 5 applications. `serve.py` exposes it as `funnel_by_channel` in `/api/state` (also in the cloud export and demo snapshot), and the dashboard shows it as a table under the funnel. `career-coach` quotes its output — never a withheld rate or a benchmark as the user's own — and adds a channel-mismatch calibration trigger; `/today`'s weekly-reflection offer opens with one line on the channel mix.
- Maya's example and the `maya-active` snapshot record `channel` on every application (one left blank to show `unknown`), and Lendable's `referred_by`.
- `/wrap-up` closes a search after an accepted offer, one confirmed step at a time: withdrawal drafts for every role still in process (marked `not_interested` with `date_not_interested` on a yes), thank-you drafts for referrers and helpers from `people/`, a retrospective in `outputs/retro-<date>.md` built from the user's own numbers (days to offer, funnel overall and by channel, rejections by stage with the recruiters' notes, outreach), story-bank and master-CV proposals from the debriefs, and finally `search_state: dormant` in `strategy.md`. `/wrap-up --reopen` sets it back to `active`. Writes go through `plugin/scripts/wrap-up.py` (`open`, `withdraw`, `facts`, `close`, `reopen`); nothing is sent.
- A closed search is honoured everywhere: `/today` prints one line instead of a brief (plus a quarterly market-check offer if opted in), `/job-search` only runs `--market-check` (recheck of watched companies, files nothing, stamps `last_market_check`), and the dashboard shows a "search closed" banner and hides the weekly targets and offer countdown. `strategy.md` schema documents `search_state`, `search_closed`, `accepted_offer`, `market_check`, `last_market_check`, `search_reopened`; the validator adds `strategy.search-state-enum` and date checks.
- Harness journey `application-to-interview` (Maya, Zopa): `/apply` → ATS check → `/sent` → ten days → `/follow-up` → reply → interviewing → `/interview-prep`, with judge criteria on the fields each step writes. Run by name; not in the default sweep. Journeys can declare `## Orchestrator steps`, run by the harness between turns.
- `scripts/rebase_fixture_dates.py --time-skip N --root userdata` moves every date (and dated file or folder name) in a working userdata tree N days back — the harness clock for "ten days later". `test-runs/` and `examples/` are left alone.
- `tests/test_application_to_interview.py` runs the same field chain through the real scripts; `tests/test_skill_size.py` keeps `/today` and `/setup` at ≤ 20 KB and checks every split-out reference is still pointed at.
- CONTRIBUTING "Developing": run the plugin from the clone with `claude --plugin-dir`, the installed copy disabled for that folder only, and the dashboard served from the clone.

### Changed
- `/today` (48.6 → 19.6 KB) and `/setup` (36.7 → 19.2 KB) load their rarely-hit parts on demand from `plugin/references/`: `today-integrations`, `today-write-contracts`, `today-coach-triggers`, `today-weekly-reflection`, `today-applications-index`, `setup-job-sweep-import`, `setup-positioning-drafting`, `setup-rerun`, `setup-file-writes`, and the smoke tests (`today-smoke-test`, `setup-smoke-test`). Each skill names the file and the condition it is read under; rules are unchanged, rationale prose is shortened. TONE.md and the three reviewer agents point at the moved drafting rules.
- Weekly outreach — in the dashboard and `/today` — is the number of `sent` reach-out / referral-ask / intro-ask / follow-up lines in people logs this ISO week. The journal keyword regex and head-count parsing (`_WARM_OUTREACH_KEYWORDS`) are gone: journal wording no longer counts. Feedback requests are still counted from the journal.
- One quiet-application rule: `/today` drops its own 14-day "Chase or close" rule and "stale applied" heads-up and uses `follow-ups.py` (10 days since the latest of `date_applied`, `last_inbound`, `last_follow_up`) for both following up and closing.
- `record-sent.py` and `record-inbound.py` share `plugin/scripts/metafile.py` for frontmatter edits.
- `/apply` no longer archives anything or writes to `meta.md`; when the application goes out it hands over to `/sent`.
- `archive-application.py` exposes `archive()` for `record-sent.py` and takes `--no-history`.

### Fixed
- From the 2026-11-16 harness run: a status change confirmed in chat now carries the role's posting link; `/interview-prep` always closes with the after-the-call `/interview-analysis` nudge (optionally a simulator rehearsal) instead of replacing it with another question; `/apply` offers to keep a phone number the user gives for the CV (writing `phone:` to the profile on a yes) instead of telling them to edit the profile by hand.
- The dashboard server binds exactly the port it's given (7890) and stops with a clear message when it's busy, instead of silently moving to 7891–7899 and leaving two dashboards; the `/dashboard` skill's port-range text is gone.
- `recommended-flow.md` used `status: interview` and `to apply`, which aren't status values.

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
