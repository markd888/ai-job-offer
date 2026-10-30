# Findings — maya-sweep-smoke

**Run date:** 2026-08-23
**Snapshot:** empty
**Judge:** four calls, one per rubric, against the working tree.
**Note:** first ever run of this journey. Written in 0.5.0, deliberately excluded
from the default release sweep until one clean run validated it. This is that run.

## Lint

    turn 1: lint.file-path — 'cv.md' named in user-facing text: "… you'll work. Drop a CV into `job-sweep/` as cv.md, cv.txt or cv.pdf and I'll read them of…"
    turn 5: lint.file-path — 'profile.md' named in user-facing text: "…remote. Change any of that by editing `job-sweep/profile.md` — the next sweep picks it up."
    NOT CHECKED: lint.hardcoded-cadence (no userdata tree supplied)
    NOT CHECKED: schema validation (job-sweep writes no userdata/ tree)

## Groundedness

### Evidence

| turn | claim | source | grounded |
|---|---|---|---|
| 5 | Profile was saved and lives at `job-sweep/profile.md` | file: `job-sweep/profile.md` | yes |
| 5 | Roles targeted are Head of Product, Lead PM, Principal PM, Senior PM | user: turn 3; file: `job-sweep/profile.md` | yes |
| 5 | Industries are fintech, consumer credit, lending, payments | user: turn 4; file: `job-sweep/profile.md` | yes |
| 5 | Location is London hybrid or EMEA remote | user: turn 5; file: `job-sweep/profile.md` | yes |
| 5 | 23 live roles came back | file: `job-sweep/roles-2026-08-22.md` ("23 roles found") | yes |
| 5 | Split is 2 strong, 18 possible, 3 worth a glance | file: `job-sweep/roles-2026-08-22.md` (2 / 18 / 3 table rows) | yes |
| 5 | Saved to `job-sweep/roles-2026-08-22.md` | file: `job-sweep/roles-2026-08-22.md` | yes |
| 5 | Lendable Senior Product Manager (UK Cards), London | file: `job-sweep/roles-2026-08-22.md` | yes |
| 5 | That role is consumer credit, right level, right city | file: `job-sweep/roles-2026-08-22.md` (Strong section, title "UK Cards"); user: turns 3-5 | yes |
| 5 | Malt Head of Product Payment, Paris or London | file: `job-sweep/roles-2026-08-22.md` | yes |
| 5 | It is the only Head-of-Product-level role that survived | file: `job-sweep/roles-2026-08-22.md` (no other HoP row) | yes |
| 5 | Tide's Lead PM for banking payments is Lithuania-based | file: `job-sweep/roles-2026-08-22.md` | yes |
| 5 | Adyen's is Amsterdam | file: `job-sweep/roles-2026-08-22.md` | yes |
| 5 | Pagaya, Lead Bank, Tilt Finance, Benepass, Koyfin are US-only | file: `job-sweep/roles-2026-08-22.md` | yes |
| 5 | Faire's role is US-only | file: `job-sweep/roles-2026-08-22.md` says "New York / San Francisco / Toronto" | NO |
| 5 | Automattic, Grid, Truv, Canopy state no region | file: `job-sweep/roles-2026-08-22.md` | yes |
| 5 | Every posting was checked against the company's own careers system | fetch: ATS links recorded for all 23 rows (Ashby / Greenhouse / Lever) | yes |
| 5 | Roughly 35 of the roles the search turned up were already taken down | file: `job-sweep/seen-roles.jsonl` (57 surfaced on 2026-08-22 − 23 listed = 34) | yes |
| 5 | Zopa, OakNorth's lending group PM role, Ebury, Moniepoint were among them | file: `job-sweep/seen-roles.jsonl` (all four present, none in the roles file) | yes |
| 5 | Those are recorded so they won't resurface | file: `job-sweep/seen-roles.jsonl` | yes |
| 5 | London fintech at Head-of-Product level was thin this week | file: `job-sweep/roles-2026-08-22.md` (one HoP row of 23) | yes |
| 5 | `job-offer`'s `/setup` reads this profile | file: `job-sweep/profile.md` (comment block states this) | yes |
| 6 | 14 new roles this time | file: `job-sweep/roles-2026-08-23.md` ("14 new since your last sweep") | yes |
| 6 | 16 were held back as already seen | file: `job-sweep/roles-2026-08-23.md` ("16 already-seen roles suppressed") | yes |
| 6 | The previous sweep happened last week | none — it ran at turn 5 of this transcript and wrote `roles-2026-08-22.md`, one day before `roles-2026-08-23.md` | NO |
| 6 | Five look strong | file: `job-sweep/roles-2026-08-23.md` (5 Strong rows) | yes |
| 6 | Funding Circle Senior Data Product Manager, London | file: `job-sweep/roles-2026-08-23.md` | yes |
| 6 | Funding Circle is a UK lending business | fetch: the search + ATS check that surfaced and industry-classified the role as Strong | yes |
| 6 | Remote and Amplemarket are Senior PM roles open to anyone remote in Europe | file: `job-sweep/roles-2026-08-23.md` ("Remote, EMEA" for both) | yes |
| 6 | CreateFuture wants a Lead PM in London or remote UK | file: `job-sweep/roles-2026-08-23.md` | yes |
| 6 | Proton's Senior PM sits in London or Paris | file: `job-sweep/roles-2026-08-23.md` | yes |
| 6 | None of those four is lending or payments | file: `job-sweep/roles-2026-08-23.md` (titles + industry classification) | yes |
| 6 | Seven are possible | file: `job-sweep/roles-2026-08-23.md` (7 Possible rows) | yes |
| 6 | Mercury has a Head of Product and a Senior PM on business lending | file: `job-sweep/roles-2026-08-23.md` | yes |
| 6 | Those Mercury roles are US and Canada only | file: `job-sweep/roles-2026-08-23.md` | yes |
| 6 | ClarityPay, MeridianLink and Splitero are US-located too | file: `job-sweep/roles-2026-08-23.md` | yes |
| 6 | Spotted Zebra's Senior Director of Product is remote UK and not fintech | file: `job-sweep/roles-2026-08-23.md` (Possible section, title) | yes |
| 6 | Two are worth a glance | file: `job-sweep/roles-2026-08-23.md` (2 Edge rows) | yes |
| 6 | A contract Senior PM scoped to Arabic-speaking markets | file: `job-sweep/roles-2026-08-23.md` (Squadio, "(ARAB)", MENA); fetch: the Workable posting that supplied the MENA scope | yes |
| 6 | Hospitable's Staff PM advertises USA/Europe but is filed as US-only | file: `job-sweep/roles-2026-08-23.md` | yes |
| 6 | 18 of the postings the search turned up had already been taken down | file: `job-sweep/seen-roles.jsonl` (32 surfaced on 2026-08-23 − 14 listed = 18) | yes |
| 6 | An entire set at Jobgether, plus BlaBlaCar, dLocal, Prosper, Paytm, Pagaya, Kantox | file: `job-sweep/seen-roles.jsonl` (4 Jobgether rows + each named company, none listed) | yes |
| 6 | Fresha's London role was a plain Product Manager, not the senior fintech role the search listed | fetch: the Fresha posting opened during the sweep | yes |
| 6 | Saved to `job-sweep/roles-2026-08-23.md` | file: `job-sweep/roles-2026-08-23.md` | yes |
| 6 | `job-offer`'s `/setup` reads this profile | file: `job-sweep/profile.md` | yes |

### Findings

- **turn 5:** "a long tail of US-only fintech roles (Pagaya, Faire, Lead Bank, Tilt Finance, Benepass, Koyfin)" — the run's own `roles-2026-08-22.md` records Faire's role as "New York / San Francisco / Toronto", so labelling it US-only restates in-run file content inaccurately; the same turn's file distinguishes locations precisely enough that the run had the fact in hand.
- **turn 6:** "14 new roles this time, and 16 that last week's sweep already showed you were held back so you don't read them twice" — the earlier sweep ran at turn 5 of this transcript and wrote `roles-2026-08-22.md`, one day before this sweep's `roles-2026-08-23.md`, so "last week" is a date claim nothing in the run supports; the same unsupported timing is repeated in "which is the same wall you hit last week".

### Verdict

**FAIL** — the two sweep summaries are otherwise tightly tied to the files the run wrote, including the honest reporting of dead postings and the Fresha exclusion, but one location is restated against the run's own roles file and the interval between the two sweeps is asserted as a week when the run's files place them a day apart, and this rubric is zero tolerance.

## Coherence

### Findings

- **turn 4:** "Remote, both, or something else (tell me in your own words)?" — Rule 1: "both" has no antecedent because no first option was ever named (office? hybrid?), so the user is handed a menu item they cannot resolve and has to guess what they are choosing between.
- **turn 6:** "14 new roles this time, and 16 that last week's sweep already showed you were held back so you don't read them twice" vs **turn 5:** "Saved to `job-sweep/roles-2026-08-22.md`" — Rule 4: the sweep being called "last week's" is the one the user ran moments earlier in this same conversation, and its own file is dated one day earlier, so the user is left unable to reconcile "last week" with a sweep they just watched run.
- **turn 6:** "That's discovery. If you get to the point of tracking applications, scoring fit and prepping interviews, the full `job-offer` plugin does that — and its `/setup` reads this profile, so you won't re-answer any of this." — Rule 3: this closing paragraph is verbatim identical to turn 5's closing paragraph in the immediately preceding assistant turn, so the user is re-pitched something they were pitched one turn ago with nothing added.
- **turn 6:** "18 of the postings the search turned up had already been taken down — an entire set at Jobgether, plus BlaBlaCar, dLocal, Prosper, Paytm, Pagaya, Kantox and others" vs **turn 5:** "a long tail of US-only fintech roles (Pagaya, Faire, Lead Bank, Tilt Finance, Benepass, Koyfin)" — Rule 4: Pagaya is presented as a live "possible" role in one turn and as an already-dead posting in the next with no bridging line, leaving the user unsure whether the lead they were given is real.

### Verdict

**FAIL** — Two moments force the user to stop and reread rather than read on: a choice ("both") with no stated alternatives, and a sweep run seconds ago being narrated as "last week's" against a file dated one day earlier; the verbatim-duplicated closing pitch compounds the sense that the second turn was not written with the first in view.

## Conformance

### Findings

- **Cross-journey 1 — PASS.** turn 6: "That's discovery. If you get to the point of tracking applications, scoring fit and prepping interviews, the full `job-offer` plugin does that — and its `/setup` reads this profile, so you won't re-answer any of this." — the journey terminated at turn 7 and the closing nudge names the user's actual state (a profile already written that the next tool will read), not a generic recital of the canonical order.
- **Cross-journey 2 — PASS.** turn 6: "14 new roles this time, and 16 that last week's sweep already showed you were held back so you don't read them twice." — the referenced prior state genuinely exists (`job-sweep/roles-2026-08-22.md` and 57 `first_surfaced: 2026-08-22` records in `seen-roles.jsonl`); the "last week" wording overstates the gap (the prior sweep was the previous day), but that is a factual-phrasing matter, not an invented prior state.
- **Cross-journey 3 — PASS.** turn 6 closes with "Saved to `job-sweep/roles-2026-08-23.md`." followed by the full-plugin next step, and turn 5 closes the same way; no assistant turn ends mid-prompt awaiting input the journey didn't supply.
- **Cross-journey 4 — NOT EXERCISED.** No skill wrote `userdata/profile.md` or `userdata/strategy.md` — the only profile written was `job-sweep/profile.md`, and it was confirmed in chat anyway (turn 5: "Saved your profile, then ran the sweep. ... Change any of that by editing `job-sweep/profile.md` — the next sweep picks it up.").
- **Cross-journey 5 — NOT EXERCISED.** Neither `/job-search` nor `/evaluate-position` ran; the journey's only entry point was `/job-sweep:sweep`, which surfaces links in `roles-*.md` rather than in chat rows, and the journey never intended to reach those skills.
- **Spec 1 (profile written) — PASS.** `job-sweep/profile.md` frontmatter carries all three keys: `target_titles: [Head of Product, Lead PM, Principal PM, Senior PM]`, `target_industries: [fintech, consumer credit, lending, payments]`, and `geography:` with `mode: other` / `mode_detail: London hybrid or EMEA remote`, matching turn 5's readback.
- **Spec 2 (one question per message) — PASS.** turn 2: "What roles are you after?"; turn 3: "What industries?"; turn 4: "Where will you work?" — three separate assistant messages. turn 1's "I need three things: what roles you want, what industries, and where you'll work" is a preamble to the CV-versus-questions choice, not a bundled ask, since none of the three was answered there.
- **Spec 3 (nothing outside `job-sweep/`) — PASS.** The run's working directory contains exactly one child, `job-sweep/`, holding `profile.md`, `seen-roles.jsonl`, `roles-2026-08-22.md`, `roles-2026-08-23.md` — no `userdata/`, no company folder, no `meta.md`; no chat turn claims a write elsewhere.
- **Spec 4 (no tier, no status, no tracking claim) — PASS.** Neither output file contains the strings tier, score, status or applied, and turn 6 explicitly pushes tracking elsewhere: "If you get to the point of tracking applications, scoring fit and prepping interviews, the full `job-offer` plugin does that".
- **Spec 5 (real URLs, nothing invented) — PASS.** All 37 rows across the two files carry resolvable ATS URLs on the company's own system (e.g. "https://jobs.ashbyhq.com/lendable/636b90ec-028d-461a-b358-c7b871918dd8", "https://job-boards.eu.greenhouse.io/proton/jobs/4364312101"), and turn 5 states "I checked every posting against the company's own careers system before listing it"; nothing in the transcript or files shows a company, role or link without a search-result URL behind it.
- **Spec 6 (`seen-roles.jsonl` schema) — PASS.** The file exists with 89 lines, every line parses as one JSON object, and every object's key set is exactly `company_key`, `strict_key`, `base_key`, `url_key`, `raw_title`, `first_surfaced`; 57 of them carry `"first_surfaced": "2026-08-22"`, so the file was populated by run one.
- **Spec 7 (second run skipped onboarding) — PASS.** turn 6 opens "Sweep done." with no re-ask of titles, industries or geography, consistent with `job-sweep/profile.md` already existing from turn 5.
- **Spec 8 (suppression) — PASS.** The two output files share zero URLs (23 in run one, 14 in run two) and zero company/role pairs; no "Possible repeats" section was needed.
- **Spec 9 (suppression count in chat) — PASS.** turn 6: "14 new roles this time, and 16 that last week's sweep already showed you were held back so you don't read them twice." — the suppressed count (16) is stated, matching `roles-2026-08-23.md`'s "16 already-seen roles suppressed."
- **Spec 10 (strong / possible / edge, no score notation) — PASS.** Both files use `## Strong`, `## Possible`, `## Edge`, and turn 5 renders them as "2 strong, 18 possible, 3 worth a glance"; no weighted score, points total or tier label appears in chat or in either file.
- **Spec 11 (exactly one closing pointer) — PASS.** turn 6 ends with a single pointer at the full plugin and repeats it nowhere else in that summary; the identical block also closes turn 5, which is that sweep's own closing line — a sweep cannot know another will follow, so one pointer per sweep is the only implementable reading of the criterion.
- **Spec 12 (closed postings dropped) — opportunistic, PASS.** turn 5: "roughly 35 of the roles search turned up were already taken down — including some that looked ideal on paper, like Zopa, OakNorth's lending group PM role, Ebury, and Moniepoint. Those are recorded so they won't resurface next time." — corroborated by `seen-roles.jsonl` holding 89 records against 37 roles actually shown.

### Verdict

**PASS** — every in-scope `[required]` criterion passed; the two that are NOT EXERCISED (cross-journey 4 and 5) have preconditions this journey was never meant to meet, since `job-sweep` writes nothing under `userdata/` and neither `/job-search` nor `/evaluate-position` is part of the flow.

## Tone

### Findings

- **turn 4:** `"Where will you work?"` — the question is wrapped in literal quotation marks, so it reads as the assistant reciting a scripted line rather than asking the user directly, breaking the plain casual-professional voice.
- **turn 4:** "Remote, both, or something else (tell me in your own words)?" — "both" has no antecedent because no pair of options was ever named, so the ask is not a direct ask; the user has to guess what the choices are.
- **turn 6:** "14 new roles this time, and 16 that last week's sweep already showed you were held back so you don't read them twice." — the sentence is ungrammatical and unparseable on first read, which is the opposite of the simple-language principle.
- **turn 6:** "That's discovery. If you get to the point of tracking applications, scoring fit and prepping interviews, the full `job-offer` plugin does that — and its `/setup` reads this profile, so you won't re-answer any of this." — a verbatim repeat of the identical closing paragraph from turn 5, one turn earlier; recycled promotional boilerplate reads as canned copy, not as the product talking to this user.
- **turn 5:** "The \"possible\" pile is mostly right-level, wrong-place: Tide's Lead PM for banking payments is Lithuania-based, Adyen's is Amsterdam, and a long tail of US-only fintech roles (Pagaya, Faire, Lead Bank, Tilt Finance, Benepass, Koyfin)." — eighteen results delivered as run-on prose with parenthetical name-dumps where a scannable list is the obvious form; the density comes from packing, not from substance that had to be long.
- **turn 6:** "Seven are possible. Mercury has both a Head of Product and a Senior PM on business lending — dead-on for your background, but the roles are US and Canada only, which is the same wall you hit last week. ClarityPay, MeridianLink and Splitero are the same story." — same packed-paragraph shape as turn 5, three-plus clauses per line and companies buried mid-sentence, so the batch cannot be skimmed.

### Verdict

**FAIL** — two of the findings share a cause the user meets twice (results delivered as unskimmable prose in both sweeps, and the same closing pitch pasted verbatim in both), and the turn-4 and turn-6 copy is broken enough on first read that a real user would notice the voice as off.

## Verdict

    Lint:          FAIL (2)
    Groundedness:  FAIL (2)
    Coherence:     FAIL (4)
    Conformance:   PASS
    Tone:          FAIL (6)

    Gate: Lint AND Groundedness AND Conformance

**Overall: FAIL**
