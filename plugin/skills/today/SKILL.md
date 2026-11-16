---
name: today
description: This skill should be used when the user asks for "/today", "my daily brief", "today's brief", "where am I in my job search", "what should I work on today", "pipeline state", or wants a sorted view of every active company plus today's actions. Two-phase: input phase captures fresh facts since the last journal entry (via wired Calendar/Gmail/Granola integrations + an open catch-all prompt), then writes them to userdata/journal.md and relevant userdata/companies/*/meta.md; output phase reads userdata/strategy.md + all meta.md + the current ISO week of journal.md, writes a 3-section daily brief (top actions, heads-up, pipeline) to userdata/outputs/daily-brief-<date>.md, regenerates the GENERATED block of userdata/outputs/applications.md, and on the first run of each ISO week (when prior-week journal entries exist) offers a hand-off to job-offer:career-coach for a weekly reflection.
---

# /today — daily brief

Produce a short (~half a screen) snapshot that combines: where the user is against their stated strategy, what to actually do next, and a sorted view of the pipeline. Save the brief, regenerate the applications.md index, then print the brief to chat.

**Voice:** all chat output and drafted content (the daily brief, summary lines, warnings) follows `${CLAUDE_PLUGIN_ROOT}/TONE.md`.

## Closed search (check first)

Read `search_state` in `userdata/strategy.md`'s frontmatter. If it is `dormant` (set by `/job-offer:wrap-up` after an accepted offer), do **none** of the rest of this skill — no input phase, no brief, no applications.md, no weekly reflection. Print one line instead:

> Your search is closed — you accepted <accepted_offer> on <search_closed>. Say "reopen my search" to start again.

One exception: if `market_check: quarterly` and 90+ days have passed since the later of `search_closed` and `last_market_check`, add `It's been a quarter — want a quick look at the companies you were watching? (/job-offer:job-search --market-check)`. Nothing else. Absent or `active` → carry on below.

## Input phase (runs before brief generation)

Capture fresh facts since the last journal entry. Each confirmed fact gets appended to `userdata/journal.md` and — when it has structured implications — pushed to the relevant `userdata/companies/<Co>/meta.md`. Then the output phase runs against the just-written state.

This phase always runs (even with no integrations wired) but degrades gracefully — inference and confirms are skipped when there is nothing to scan, and the catch-all prompt becomes the only input surface.

**First-run detection (TONE Rule C — don't ask about prior state on first run):**

Before prompting for updates, check `userdata/journal.md`. If the file does not exist, is empty, or contains no entries, skip the entire input phase and go straight to output generation. Do not ask "anything that moved since last time?" — there is no last time.

### Step 1 — determine the input window

Read `userdata/journal.md`. Find the most recent dated heading (`## YYYY-MM-DD`).

- Gap < 24h → window = 24h. Print nothing; this is the normal daily case.
- Gap 1–6 days → window = the actual gap. Print one line: `Last entry was N days ago — pulling the full window.`
- Gap ≥ 7 days → window = the actual gap. Print: `You've been away N days — heavier sweep ahead, may take a moment.`
- `journal.md` absent or empty → window = 24h. Treat as a fresh install. Do not print anything special.

### Steps 2–3 — integrations (only when wired)

If `userdata/integrations.md` lists a wired Calendar, Gmail or Granola integration, read `${CLAUDE_PLUGIN_ROOT}/references/today-integrations.md` now and follow it: the inference pass over the window, the numbered confirms, and the calendar/gmail fetches that Today rules 1 and 3 and the heads-up use. No integrations file, or nothing wired → skip straight to Step 4; nothing in that file applies.

### Step 4 — open catch-all

After targeted confirms (or in place of them when step 2 produced nothing):

**Input prompt (subsequent runs only):**

Use `AskUserQuestion` with two options:

Question: "Want to log updates since your last brief? Mock interviews, prep work, energy notes, new leads, anything structural."
Options: **Share updates** / **Skip**

If **Share updates** → open a free-text follow-up: "Go ahead — what's new?"
If **Skip** → proceed to output phase silently.

Do not rely on enter-to-skip. Do not chain a second question after this one (TONE Rule A — one ask per message).

User responds in free text. Parse for company tags: explicit `[Plaid]`, `Plaid:`, or first-token match against the company list. Lines without a company tag are logged to `journal.md` only (no meta.md write, no guessing). Lines WITH a company tag are also logged to `journal.md` only — catch-all input is free text and never changes status, events or anything else in meta.md, even when the tag matches a known company. Only integration-sourced facts that pass through the Step 3 confirm flow may update meta.md.

One exception, because it is the user's own statement of a fact: a tagged line that plainly says the company got in touch (replied, called, wrote, scheduled, sent a rejection or an offer) also records that contact with `record-inbound.py` (see "meta.md updates" below), dated as the user said or today. Nothing else changes, and the write confirmation names it (`Noted that Plaid got back to you today.`). A line about the user's own action ("I chased Plaid") is not inbound.

### Step 5 — write phase

Commit the confirmed facts. See "Write contracts" section below for the exact journal.md and meta.md formats.

Writes are idempotent per `/today` run: if the user runs `/today` twice the same day with no new facts (step 2 finds nothing new, step 4 skipped), no journal write occurs and no `## YYYY-MM-DD` heading is added or modified.

**Dashboard nudge cross-reference.** When confirming an in-chat status change (e.g. user says "mark Plaid to apply"), check whether the "In-chat update nudge — fire once per session" rule in `${CLAUDE_PLUGIN_ROOT}/skills/dashboard/SKILL.md` should fire. If this is the first status-change-in-chat of the current Claude Code conversation, append the tip line per that rule. Track the once-per-session flag transiently in conversation context, not on disk.

After step 5 completes, proceed to the existing "Output: the daily brief" section.

## Write contracts

Before Step 5 writes anything, read `${CLAUDE_PLUGIN_ROOT}/references/today-write-contracts.md` — the journal bullet shape (`- [<Company>] <fact>. (source: <integration|user>[, confirmed])`, appended under today's `## YYYY-MM-DD`, never editing earlier bullets) and which `meta.md` fields the input phase may touch (`last_inbound` via `record-inbound.py`, `next_event`, `status` only for a confirmed rejection or offer, `## History`). Nothing to write → don't load it.

## Inputs

Read in this order. Skip gracefully if a file is missing — the brief degrades section-by-section, never errors out wholesale.

1. `userdata/strategy.md` — frontmatter (`weekly_targets`, `pipeline_targets`, `checkpoints`). Used by Top-3-actions trigger rules and the warm-outreach summary line in applications.md. The `## Headline goal` paragraph and `target_offer_date` are not read by the brief itself.
2. All company `meta.md` files. Use BOTH globs (companies are either flat or in role-slug subfolders):
   - `userdata/companies/*/meta.md`
   - `userdata/companies/*/*/meta.md`
3. `userdata/journal.md` — last 7 days of entries (entries are dated `## YYYY-MM-DD` headings; take everything with a date within the last 7 days).
4. `userdata/outputs/applications.md` if it exists (needed for the partition rewrite — see "applications.md regeneration" below).
5. `userdata/integrations.md` if it exists — parse the `## calendar` and `## gmail` sections for wired-status + tool prefix. See "Integration data" below. Skip silently if the file is absent — the brief still produces a complete output from markdown alone.

Do not read `userdata/profile.md`. /today does not need profile content; trust strategy.md and the per-company meta.

## Output: the daily brief

Three sections, in this order, ~half a screen total. Never longer. Skip a whole section (do not pad with "N/A") when the underlying data is unavailable. No headline-goal restatement, no progress meter.

Section order: **Today → Heads-up → Pipeline state.**

### 1. `## Today`

At most three bullets. Each bullet is concrete and anchored to a company name or a strategy element. Surface bullets by running the trigger rules below, in this priority order, and stopping at three:

The heading is `## Today` (not "Top 3 actions"): one bullet is often the honest number. Don't pad to three, don't number them.

1. **Imminent calendar event (when calendar wired)** — any matched event within the next 48 hours → `<Day HH:MM> — <Company> <event-type>: prep with /interview-prep <Company>` (cap at two; most-soonest first).
2. **Checkpoint due in ≤14 days** → `Review checkpoint due <date>: <condition> → <action>` (one bullet per upcoming checkpoint; cap at one if multiple).
3. **Recruiter email needing reply (when gmail wired)** — any matched email from the Gmail fetch where the from-address is recruiter/talent AND the company is in `status: interviewing` or `status: applied` AND no reply has gone out (cannot fully verify; use it as a prompt regardless) → `Reply to <name> at <Company> re: "<subject>"` (cap at one).
4. **Active interview thread** — any meta.md with `status: interviewing` AND `last_inbound` within the last 7 days → `Prep for <Company> — pull stories with /interview-prep <Company>` (one bullet per qualifying company, most recent inbound first; cap at two).
5. **Quiet application** — the one quiet-application rule, shared with `/job-offer:follow-up`: run `python3 -I "${CLAUDE_PLUGIN_ROOT}/scripts/follow-ups.py" --userdata "$(pwd)/userdata"` once per brief (the heads-up line below reuses the same output). Quiet means no news for 10+ days since the latest of `date_applied`, `last_inbound` and `last_follow_up`, so a company that wrote back recently is never chased. Pick the first role under "Follow-up due" with a named contact, a tailored CV or tier P0/P1 (else the first listed) → `Follow up with <Company> — quiet <N>d → /job-offer:follow-up <Company>`. If nothing is due but roles are listed under "Close instead" → `Close <Company> — quiet <N>d, <reason> → mark it rejected?`. Cap at one. Do not compute a separate day count here.
6. **Weekly-target gap >50%** (warm_outreach OR applications, whichever is further behind) → `Send <N> more <warm outreach|applications> this week (<count>/<target>)`. Skip if no target set. "This week" = current ISO week, Monday → today inclusive; same window as the applications.md warm-outreach summary line. Count outreach from people logs, as in the applications.md summary line below. When outreach is the one behind, name a person or a role to start with — a `to_apply` P0/P1 role with someone in `userdata/people/` linked to it beats a generic count — and point to `/job-offer:outreach`.

   Skip it entirely when no roles are filed at all (the user needs `/job-search` first). When both are equally behind, pick `applications`. Report only one, never both.
7. **Founder outreach line (conditional on `strategy.md`)** — Read `userdata/strategy.md`. If `weekly_targets.founder_outreach` exists with a numeric target N, and today is Monday AND the warm-outreach count for Saturday + Sunday is 0, render: `Founder outreach — N this week (M done so far).` Where M is counted from journal entries tagged or describing founder DMs in the current ISO week. If `weekly_targets.founder_outreach` is absent, missing, or zero, do not render any founder line at all. Do not invent a target.

If fewer than three triggers fire, output fewer bullets. Do not invent filler. If zero triggers fire, replace the body with: `Nothing forcing action today — pick from the pipeline below.`

### 2. `## Heads-up`

**Heads-up section — what to surface:**

Non-obvious risks or opportunities — technical, tactical, or strategic — derived from current state across all `userdata/companies/*/meta.md`, recent journal entries (`userdata/journal.md`), and `userdata/strategy.md`. Valid surfaces include but are not limited to:

- **Integration auth failures (when applicable):** single line per failed integration, e.g. `Calendar fetch failed (token expired) — heads-up missing event data this run. Re-auth via your calendar MCP.` These appear FIRST in heads-up so degradation is visible.
- Interview scheduled within 48 hours with no `interview-prep-<date>.md` for that company.
- Company in status `to apply` for 14+ days with no journal movement.
- Offer-evaluation deadline within `strategy.md`'s walk-away window.
- Contradiction between two recent journal entries (e.g. "wants remote" vs "took the on-site interview").
- Strategy weekly_target with significant under/over-pace.
- **Upcoming events this week (when calendar wired):** matched events within the next 7 days, sorted soonest first, e.g. `Wed 21 May 14:00 — Plaid (cpo-round), Fri 23 May 11:00 — N26 (recruiter)`. Skip if none.
- **New inbound (when gmail wired):** unmatched relevant emails (recruiter/talent senders or pipeline-keyword subjects) where no company in `userdata/companies/` matches. Format: `<count> — <Company-guess from sender domain> ("<subject>")`. Each is a prompt to evaluate adding to the pipeline. Skip if none.
- **Checkpoints due within 14d:** comma-separated list of `<date> (<condition>)`. Skip if none.
- **Follow-ups due.** From the same `follow-ups.py` output as Today rule 5 — the brief's only quiet-application signal; there is no separate "stale applied" count. When anything is due, add one line: `**Follow-ups** — <n> applications quiet 10+ days (<top 2 companies>) → /job-offer:follow-up drafts them`. When it lists roles to close, add them to the same line. Leave out the role Today already names. Skip if nothing is due.
- **Pattern checks** — evaluate these conditions; when one holds, read `${CLAUDE_PLUGIN_ROOT}/references/today-coach-triggers.md` for the exact trigger, precedence and wording, and surface at most one coach nudge:
  - *Shape mismatch* — a `status: interviewing` role at a company over 150 people, outside `target_industries`, with no equity or brand signal.
  - *Coach A* — weekly targets missed by >50% three weeks running. *Coach B* — 3+ `not_interested` roles and an empty `## Anti-goals`. *Coach C* (wins over A and B) — 8+ weeks in with <2 interviewing and no offer, or 3+ rejections at the same `rejection_stage`, or cadence under 50% four weeks running.
  - *Profile gaps* — `## Proof Points` or `## Moat` empty in `profile.md`, at least one role filed, `/setup` not run this session, not surfaced in the last 7 days.

- **Late-stage interview prompts.** Trigger: any company with `status: interviewing` AND `last_inbound` within the last 7 days. When triggered, surface a context-aware prompt to review the interview thread and prepare for the next stage. Companies in `interviewing` whose `last_inbound` is older than 7 days do NOT trigger this — they belong to the "stale items" treatment above.

Two clauses max per bullet (per TONE.md "Briefs, heads-up, and bullet content"). Lead with the entity, bold it.

**Every heads-up ends in something the user can do:** `**<Entity>** — <what's true> → <what to do>` — a skill, a decision or a one-line instruction, specific enough to act on without a follow-up question. If you can't name a move, drop the item. Suppress any heads-up about something written during this run (a strategy written minutes ago has no checkpoints yet — that's not the user's gap).

**If nothing flags:** render the literal line `Nothing flagged today.` Do not pad with low-value items.

### 3. `## Pipeline state`

**No roles at all** (no `meta.md` anywhere): keep the heading and render only `No companies tracked yet — run /job-offer:job-search to start your pipeline.`

Otherwise: **counts and progress, not a roster** — about four lines; the dashboard lists roles.

Render two lines, then the decided-history line:

> Active: `<N>` — `<n>` offer, `<n>` interviewing, `<n>` applied, `<n>` to apply, `<n>` new.
>
> This week: `<n>`/`<target>` applications, `<n>`/`<target>` outreach.

Rules:

- Drop any zero-count clause from the Active line. `Active: 11 — 1 to apply, 10 new.` is the whole line on a fresh pipeline.
- Drop the "This week" line entirely when `strategy.md` has no weekly targets set.
- Name companies ONLY where a status is a single company and that name is the point — `1 offer (Lendable)`. Never name more than two in this section; if there are three or more in a group, the count stands alone.
- No per-role rows, no tier labels, no scores, no URLs, no "last activity" column. Anything a user would want to click belongs in the dashboard, and any role that genuinely needs attention today should have surfaced in `## Today` or `## Heads-up` already.

Then one summary line for decided history:

> N decided this search; M rejected, K not interested.

Where `N = M + K`, `rejected` = roles with `status: rejected`, and `not interested` = `status: not_interested`. Drop zero-count clauses: if K=0, render `N decided this search; M rejected.`; if M=0, render `N decided this search; K not interested.`; if both zero, skip the line entirely.

Close the section with a pointer, only when the pipeline holds more than three roles:

> `Full list in the dashboard — /job-offer:dashboard.`

## Save behaviour

Default: write the full brief to `userdata/outputs/daily-brief-<YYYY-MM-DD>.md` (today's date in the user's timezone — assume system local). Overwrite if the file already exists for today (no merge — the brief is a single-shot snapshot).

**Name no files in chat** — "Saved today's brief" is enough. If a save fails, say what didn't happen, still not the path.

Also regenerate `userdata/outputs/applications.md` (see next section).

If invoked with `--ephemeral`, skip BOTH saves and print the brief to chat only. Useful for quick spot-checks. `--ephemeral` suppresses the brief and applications.md writes only — the input phase still runs and writes confirmed facts to journal.md + meta.md. Choose 'Skip' at the catch-all prompt for a fully no-side-effect spot-check.

Always print the brief to chat regardless of save mode.

## Weekly reflection

After the brief is saved, on a non-`--ephemeral` run: if this is the first `/today` of the ISO week (marker `userdata/outputs/.last-weekly-reflection` absent or dated in an earlier ISO week) AND `journal.md` has entries from the prior ISO week, read `${CLAUDE_PLUGIN_ROOT}/references/today-weekly-reflection.md` and follow it (the channel-mix line, the offer, the career-coach hand-off, the marker write). Otherwise skip it.

## End-of-run nudge

After the brief renders and the weekly-reflection check completes, compose a single one-line context-aware next-step nudge per `${CLAUDE_PLUGIN_ROOT}/references/recommended-flow.md`. Skip the nudge entirely if no useful next step is obvious (e.g. the pipeline is healthy and there's nothing time-sensitive to flag).

## `applications.md` regeneration

Every saved run also regenerates the GENERATED block of `userdata/outputs/applications.md` (Active table, Decided table for the last 30 days, Summary with warm outreach from people logs). The block format, the four marker cases (never write when only one marker is present), the columns and the counts are in `${CLAUDE_PLUGIN_ROOT}/references/today-applications-index.md` — read it when you get to this step. Any chat line that prints an application row includes the JD URL: `- <Company> — <Role> — <status> — <url>`.

## Dedup and discovery rules

Two glob patterns expose all roles:
- `userdata/companies/*/meta.md` — single-role companies (flat).
- `userdata/companies/*/*/meta.md` — multi-role companies (role-slug subfolders).

A company may appear in BOTH globs if a 1→2 migration is mid-way; in practice the migration code (other skills) ensures only one layout per company. If both layouts exist for the same company, prefer the role-slug-subfolder entries and print one warning line: `<Company>: both flat and subfolder meta.md present — using subfolder entries.`

Each meta.md represents one `(company, position)` pair. Counts (active threads, applications-this-week, etc.) are over distinct meta.md files. Two different positions at the same company count as two rows in pipeline_state and applications.md.

## Date handling

- "Today" is the system local date. Format dates as `YYYY-MM-DD`.
- "Within last N days" means `today - (N-1) <= date <= today` (inclusive — last 7 days includes today and the prior 6). Used by triggers tied to recency (stale `applied`, late-stage interview prompts, active-interview-thread detection, integration fetch windows).
- "Current ISO week" / "this week" means `today - today.weekday() <= date <= today` (inclusive — Monday of this week through today; collapses to a single day on Monday, grows to 7 days by Sunday). Used by weekly-progress tracking (warm-outreach summary line, weekly-target gap trigger).
- A missing date field is "unknown" — treat as oldest (so it does NOT trigger "within N days" rules) and rank last when sorting "most recent activity".
- "Nd ago" rendering: `0` → `today`, `1` → `1d ago`, etc.

## What /today never does

- Never writes `userdata/profile.md`, `userdata/strategy.md`, or `userdata/integrations.md`.
- Never touches text outside the GENERATED markers in `applications.md`.
- Never invents data. If `last_inbound` is missing, do not guess; rank by what is available.
- Never persists Calendar / Gmail / Granola responses to disk verbatim. Integration data lives in-context for the run; only the user-confirmed facts written to journal.md and meta.md persist.
- Never writes to journal.md or meta.md without explicit user confirmation in the input phase. Inferred facts must be confirmed (or corrected) before they land — no silent writes from integration data.
- Never auto-fills meta.md fields beyond the input-phase contract (`next_event`, `status`, `last_inbound`, `## History` block). Other skills still own positions, tier, link, date_applied, date_added.

## Smoke test

Expected behaviour against Maya's example install, for debugging this skill: `${CLAUDE_PLUGIN_ROOT}/references/today-smoke-test.md`. Not needed at run time.
