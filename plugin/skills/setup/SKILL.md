---
name: setup
description: This skill should be used when the user asks for "start", "/setup", "set up the plugin", "first-time setup", "install job-offer", "configure my profile", "create my profile", or wants to onboard onto job-offer for the first time (or re-run onboarding to update a field). Conducts a nine-step conversational install that pre-fills answers from the user's CV where one is available. Writes userdata/profile.md, a placeholder userdata/strategy.md, an empty userdata/journal.md, three .gitkeep files, and a CLAUDE.md at the workspace root resolved from the plugin template.
---

# /setup — first-run install and re-configure

Onboard the user onto job-offer by filling in `userdata/profile.md` and scaffolding the rest of the userdata tree. Idempotent — safe to re-run.

**Voice:** every prompt and message in this skill follows the plugin's tone-of-voice + low-effort-first guidelines in `${CLAUDE_PLUGIN_ROOT}/TONE.md`. `TONE.md` governs; the quoted lines below are examples of what a step should get at and roughly how it should sound, not strings to recite.

What must not drift is the **order** of the steps, **what** each asks, and what each is told not to do; the sentence itself is yours. If an example and `TONE.md` disagree, `TONE.md` wins. **Interaction form does not unlock:** a step that says select gets a select (or, without `AskUserQuestion`, prose offering the same closed choices); a step that says prose stays prose.

**Opening line** (after Step 0, fresh install only):

> "OK, let's get you set up — nine quick steps, none of it locked in."

Don't wait for a confirmation — go straight into Step 1 in the same message.

## Mode detection

Run this BEFORE asking the first question:

1. If `userdata/profile.md` exists → enter **re-run mode**: read the file, ask "keep current / update / skip" per field, never wipe existing answers.
2. If `userdata/profile.md` does NOT exist → enter **fresh-install mode**: walk all nine steps in order.
3. `--refresh` flag → re-run mode, but only re-resolve the workspace-root `CLAUDE.md` from the template using the current `profile.md` content. Skip all questions. Useful after manual edits to profile.md.

CV detection, file-format handling and the drop prompt are defined in
`${CLAUDE_PLUGIN_ROOT}/references/cv-extraction.md`. Read that file before Step 0.
Do not re-implement its rules here.

## Templates

Read these from the plugin install dir (use `${CLAUDE_PLUGIN_ROOT}` if available):

- `${CLAUDE_PLUGIN_ROOT}/templates/profile.template.md` — source for `userdata/profile.md`.
- `${CLAUDE_PLUGIN_ROOT}/templates/strategy.template.md` — source for `userdata/strategy.md`.
- `${CLAUDE_PLUGIN_ROOT}/templates/CLAUDE.template.md` — source for workspace-root `CLAUDE.md`.

Do not edit these template files. Always treat them as read-only inputs.

## The nine steps

Ask one at a time. Use AskUserQuestion where a step has a clear, closed option
set (Steps 2, 3, 4, 5); otherwise plain conversational ask. Steps 7 and 8 are
deliberately NOT selects — see each step for why. Skipping is allowed on
salary (Step 6), timeline (Step 7), hard filters (Step 8), and
positioning (Step 4 option B) — skipped forms are in `${CLAUDE_PLUGIN_ROOT}/references/setup-file-writes.md` (§1 for profile fields, §2 for timeline).

Each step below shows an example prompt in quotes. Write your own in that
register — one direct ask, no preamble, skip offered where the step is
skippable. Hold the step order and the substance of the ask; the phrasing is
yours.

Where a CV was found at Step 0, Steps 1-4 arrive pre-filled per
`${CLAUDE_PLUGIN_ROOT}/references/cv-extraction.md`. Where none was found, the
same steps run with nothing pre-filled — the questions are identical, the user
just types more. **There is one flow, not two.**

0. **CV intake** — runs before the opening line, straight after mode detection.

   Follow `${CLAUDE_PLUGIN_ROOT}/references/cv-extraction.md` § "Finding the CV".
   State directory: `userdata/`. Scaffold files: `userdata/companies/.gitkeep`,
   `userdata/stories/.gitkeep`, `userdata/outputs/.gitkeep` (the same three
   written by the file-writes step later — creating them here just means they
   already exist by then). If a readable CV is found, say one line and move
   on:

   > "Got your CV — I'll fill in what I can and you just correct me."

   If none is found and the user declines the drop, say nothing about it and go
   straight into Step 1. There is no line to print here. A run without a CV is
   the ordinary case; announcing it — "we'll do it the long way", "you just type
   more" — costs a turn and tells the user they made the worse choice.

   **If `job-sweep/profile.md` exists** (the user ran the standalone `job-sweep` plugin), read `${CLAUDE_PLUGIN_ROOT}/references/setup-job-sweep-import.md` and follow it: it carries `target_titles`, `target_industries`, `geography` and the seen-roles ledger over, confirmed rather than auto-accepted.

1. **Facts** (`{{NAME}}`, `{{CITY}}`, `{{TIMEZONE}}`, `{{EMAIL}}`) — one confirmation.

   Extract per `cv-extraction.md` § "Tier 1 — facts". Present everything found as
   one line and ask once:

   > "From your CV: <Name> · <City> · <email>. All right?"

   Omit any clause whose value is absent — never render an empty slot or a
   placeholder. A correction arrives as plain text ("email's the other one,
   x@y.com"); apply it and move on. Do not re-ask the whole line.

   If the CV supplied none of the three facts, skip this confirmation line
   entirely — don't render `"From your CV: . All right?"` — and go straight to
   the individual asks below.

   **Fields the CV did not supply are asked individually, here, before moving on:**

   > "What's your name?"

   > "Where are you based? City + country works (e.g. London, UK)."

   > "What's your email?"

   With no CV at all, this step is simply those three questions in that order.

   **Timezone is derived, never asked** — from the city (system timezone if ambiguous); don't print or confirm it.

   **LinkedIn is not asked at setup.** Leave `linkedin_url:` empty; the skill that needs it asks at the point of use.

2. **Target titles** (`{{TARGET_TITLES}}`) — multi-select.

   Derive 3-5 candidates per `cv-extraction.md` § "Tier 2 — inferences". Ask via
   AskUserQuestion with `multiSelect: true`, one option per derived title, plus
   the automatic "Other" escape for anything the user wants to add:

   > "Roles you'd take. I've pulled these from your CV — <evidence line>. Pick all that apply."

   The evidence line is the roles the inference came from, e.g. `from Lead PM at
   Monzo, Senior PM at Wise`. Show it — the user cannot judge a wrong inference
   without it.

   When the values came from `job-sweep/profile.md` rather than the CV, the
   evidence line reads `from your job-sweep profile` instead of naming CV roles.

   With no CV, ask plainly instead:

   > "What roles are you targeting? Anything from Senior PM up to Head of Product — list as many as you'd take."

   With no CV, name a range, not a ladder of titles — a list of example titles anchors the answer.

   Never auto-accept this step, even when every option came from the CV. A wrong
   target title propagates into every `/job-search` sweep and every
   `/evaluate-position` score.

3. **Target industries** (`{{TARGET_INDUSTRIES}}`) — multi-select.

   Derive 3-5 candidates per `cv-extraction.md` § "Tier 2 — inferences". Ask via
   AskUserQuestion with `multiSelect: true`:

   > "Industries. From your CV I'd guess these — <evidence line>. Pick all that apply."

   When the values came from `job-sweep/profile.md` rather than the CV, the
   evidence line reads `from your job-sweep profile` instead of naming CV roles.

   With no CV:

   > "What industries are you looking at? Fintech, healthcare, climate, enterprise SaaS — whatever fits."

   Substitute as a YAML inline list, same form as Step 2. Never add "Comma-separated." to either ask.

4. **Positioning** (`{{POSITIONING}}` + `{{PROOF_POINTS}}` + `{{MOAT}}`) — two paths. **The default order matters**: present them in the order below. A readable CV found at Step 0 bypasses this question entirely. Writing positioning by hand is 5-10 minutes of real reflection — don't force it during onboarding when the user has a faster path.

   The CV has already been located at Step 0 per `${CLAUDE_PLUGIN_ROOT}/references/cv-extraction.md`. If a readable one was found, go straight to **Mode B (CV draft)**.

   If no readable CV exists, ask via AskUserQuestion. Two options, framed like this:

   > "Positioning next — who you are and what you're best at. Two ways to handle this:"

   - **A. Write it now** → **Mode A** (paste 1-3 sentences and walk the conversational draft).
   - **B. Skip for now** — print: *"Skipped — I'll ask again once you've seen a few roles."* Never name the `--refresh` flag to the user; it is a command they did not ask for and will not remember. Write `userdata/profile.md` with the three positioning sections empty under a `<!-- TODO: fill in via /job-offer:setup --refresh, or paste your CV at userdata/cv.md and re-run --refresh -->` comment. Onboarding finishes fast.

   **Mode A (paste-now):** ask for 1-3 sentences of self-positioning and draft one `## Positioning` paragraph. Proof points and moat are NOT asked — leave both empty under the TODO comment; `/today` asks later.

   **Mode B (CV draft):** draft a positioning paragraph (≤4 sentences), 5-7 proof points and a one-sentence moat from the CV; show them; save only after the user edits or accepts. Discarded → the three sections empty under the TODO comment, never a literal `{{POSITIONING}}`.

   **Before drafting in either mode, read `${CLAUDE_PLUGIN_ROOT}/references/setup-positioning-drafting.md`** — voice, the "Not X — Y" pattern, proof-point shape, banned phrases, first person with no pronoun for the user, no invented numbers or anchors, and the once-per-run edit line.

5. **Geography** (`{{GEOGRAPHY_MODE}}` + `{{GEOGRAPHY_DETAIL}}`) — single-select via AskUserQuestion. Ask:
   > "Where are you looking?"

   Options (in this order): `On-site in <city-from-Step1>` / `Remote` / `Both` / `Other (free text)`. The first option dynamically uses the city captured in Step 1. If the user picks "Other", capture free-text into `mode_detail` and set `mode: other`.

   When `job-sweep/profile.md` supplied `geography`, pre-select the matching
   option rather than asking cold — the user already answered this.

6. **Salary band** (`{{SALARY_BAND}}`) — single open string. Skippable. Ask:
   > "What salary band are you aiming for? Whatever shape works — '£90-110K' or '$190-230K base + equity', or skip if you'd rather not anchor a number yet."

   Free text, no generated bands (no market data to back them), no validation.

7. **Timeline** — plain ask, examples inside the sentence. Ask:

   > "When do you want to have signed? Roughly is fine — a couple of months, six months, or an actual date if you have one."

   Do NOT render this as a select — examples belong in the sentence.

   Parse whatever comes back into a concrete date:

   | What the user says | Stored `target_offer_date` |
   |---|---|
   | anything under ~2 months | today + 6 weeks |
   | ~2 to 4 months | today + 12 weeks |
   | ~4 months or more | today + 24 weeks |
   | an actual date, in any format | that date, as `YYYY-MM-DD` |
   | "not sure", "no idea", or a skip | `null` |

   The three windows land unambiguously inside one cadence bucket each in the
   derivation table below, so a rough answer loses nothing. Do not ask a
   follow-up to sharpen a rough answer into an exact one.

   Always store a concrete `YYYY-MM-DD` — never a bucket label. `/today`'s
   countdown reads that field directly.

   Skipping is allowed: set `target_offer_date: null`, skip the cadence
   derivation below, and `/today` degrades gracefully (no countdown, no progress
   section).

8. **Hard filters** (`{{HARD_FILTERS}}`) — plain ask, examples inside the sentence, skippable. Ask:

   > "Last one. Any red flags — roles you'd skip on sight, whatever else is right about them? Relocation, five-day office, contract work, that kind of thing. Or skip."

   Do NOT render this as a multi-select — the real red flags are the ones nobody would put on a list.

   Take whatever the user gives, verbatim, as a list. Do not normalise their
   wording into the old canned phrasings.

   Write the selections as a YAML inline list of quoted strings:
   `["no companies under 50 people", "no five-day in-office"]`. If skipped or
   nothing selected, write `[]`. (Inline form keeps the trailing template comment
   intact, same reasoning as Step 2.)

After Step 7 (only if target date was set), silently derive cadence targets based on weeks-to-target. Compute `W = (target_offer_date − today) / 7`, then:

| W | weekly_targets.applications | weekly_targets.warm_outreach | pipeline_targets.active_interview_threads | pipeline_targets.p0_pipeline_size |
|---|---|---|---|---|
| W < 8 (under 2 mo) | 12 | 10 | 5 | 8 |
| W = 8-16 (2-4 mo) | 8 | 8 | 4 | 6 |
| W ≥ 16 (4+ mo) | 5 | 5 | 3 | 5 |

Rationale (don't surface to user unless asked): shorter timeline → higher concurrent activity needed to hit ~2 offers in hand by deadline, assuming ~30% offer rate on active interview threads and ~15% interview rate on applications.

Regardless of whether Step 7 was answered, silently auto-compose `## Headline goal` for strategy.md from profile.md frontmatter. Format:

> "Sign a `<target_titles joined by ' / '>` role at a `<target_industries joined by ', '>` company by `<target_offer_date>`. `<geography phrasing — 'Fully remote', 'London hybrid', etc.>`. Base `<salary_band>`."

Skip clauses where the source field is unset (e.g. if salary skipped, drop the base clause).

Leave `## Anti-goals` empty and `checkpoints: []` — those need deeper reflection and belong to the user's later editing or to a `career-coach` conversation.

Once all steps above are answered: proceed straight to file writes. Do NOT prompt the user about the tier rubric.

The senior-PM-default `tier_weights` + `tier_thresholds` get written into `profile.md` from the template automatically. Tier rubric terms (P0/P1/P2, role_fit, etc.) are too technical to introduce here without context — the user encounters them organically the first time `/evaluate-position` runs and shows a scoring breakdown. That's the right teach-moment.

If the user wants to tune the rubric, they edit `profile.md` directly. The re-run mode of `/setup` (where field-by-field keep/update/skip is offered) does NOT include the tier rubric either — same reason.

## Re-run mode

When `userdata/profile.md` exists, read `${CLAUDE_PLUGIN_ROOT}/references/setup-rerun.md` and follow its keep / update / skip loop instead of the fresh walk. Never wipe an answer, never touch the user's own body sections, never offer the tier rubric.

## File writes

After the last answer, read `${CLAUDE_PLUGIN_ROOT}/references/setup-file-writes.md` and do its writes in order: `profile.md` from the template (skipped placeholders as empty values, never a literal `{{…}}`), `strategy.md` and `journal.md` only if absent, the three `.gitkeep` files, and the workspace-root `CLAUDE.md` (left alone, silently, if the user wrote their own).

## Closing offers

First, confirm what was captured — in plain language, naming no files. The user
needs to know their answers were saved and what the plan now says; they do not
need the storage layout. If Step 7 produced a target date, include the derived
cadence so they can spot-check it. Example with target date set:

> "You're set up. I've got your profile, and a plan: land the offer by `<YYYY-MM-DD>`, which works out at 8 applications and 8 outreach messages a week, with 4 live interview threads at any time. Say the word if those numbers look wrong."

When Step 7 was skipped, drop the date and cadence clauses entirely: *"You're
set up. No target date yet, so there are no weekly numbers — tell me when you
want to have signed and I'll work them out."*

Confirming the write is required (a silent write to a user's own file is
indistinguishable from data loss), but the confirmation is about *what changed*,
not *where it lives*. "I've got your profile" carries the whole message;
`userdata/profile.md — identity, target role, salary, hard filters` carries a
directory listing.

**Do not offer the career-coach positioning interview here.** Setup's last word
belongs to the next step in the search, and that step is the first sweep — a
user who has just answered nine questions wants roles, not a fifth conversation
about themselves. The offer moves to `/today`, which surfaces it once the
profile has been used in anger and the user can tell whether it is landing.

**Automation offer (split per TONE.md Rule A — one ask per message):**

Step 1 — ask:
> "Want `/job-offer:today` to run automatically every day? (y / n)"

Use `AskUserQuestion` with two options: **Yes** / **No, I'll run it manually**.

If No → skip to closing nudge.

Step 2 (only if Yes) — ask:
> "What time? (e.g. 9am)"

Free-text answer. Parse to HH:MM.

Step 3 (only if Yes) — write the schedule via `/schedule` automatically and reply:
> "Done — your brief runs daily at <HH:MM>. That needs Claude Code open; if you'd rather it run in the background, say so and I'll set that up."

**Closing nudge:**

After all setup files are written (and after the automation step completes or is skipped), read `${CLAUDE_PLUGIN_ROOT}/references/recommended-flow.md` and compose a single one-line context-aware next-step nudge based on the user's current state. For a fresh setup with no companies yet, the nudge should be:

> "Setup done. Run `/job-offer:job-search` and I'll go find roles that match."

Do not list all three steps as numbered bullets; the recommended-flow reference
handles ordering. Do not offer `/today` as an alternative on a fresh install
either — the pipeline is empty, so a brief has nothing to report, and a choice
between a useful action and an empty one is not a choice worth presenting.

## What /setup never does

- Never edits `.claude/settings.json` or any Claude Code system config.
- Never runs `git init` or `git commit`. The repo lives in the user's workspace; the user manages it.
- Never validates any external service (no MCP, no API).
- Never writes `userdata/companies/*`, `userdata/stories/*`, or `userdata/outputs/daily-brief-*.md` — those belong to other skills.
- Never overwrites `userdata/strategy.md` if it exists. `/strategy` owns updates.
- Never overwrites `userdata/profile.md`'s body sections in re-run mode (only frontmatter fields the user explicitly updates).
- Never invents proof-point numbers. If the CV in Mode B doesn't have a metric for a bullet, surface it as a draft bullet without numbers and ask the user to fill in.

## Smoke test

Expected behaviour against Maya's example install, for debugging this skill: `${CLAUDE_PLUGIN_ROOT}/references/setup-smoke-test.md`. Not needed at run time.
