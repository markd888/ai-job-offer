---
name: cold-start
persona: maya
snapshot: empty
max_turns: 30
---

## Goal

A new user goes from empty userdata to a working daily loop. Tests
the onboarding spine: `/setup` → `/job-search` → `/dashboard` → first `/today`.

## Opening message

`/job-offer:setup`

## Mid-journey instructions to the simulator

The simulator follows these scripted hand-offs when the plugin reaches
each checkpoint, otherwise stays in persona.

1. When `/setup` Step 0 prompts to drop a CV and says "say 'ready' when
   it's in", decline — reply that you don't have one handy — and let
   `/setup` continue without a CV. This journey's `snapshot: empty` has
   no CV file to drop; don't stall on this blocking ask.
2. After `/setup` wraps (look for "Saved as profile.md", "Let's wrap",
   or a clear closing nudge), send: `/job-offer:job-search`
3. After `/job-search` finishes its run summary (look for "Filed N new
   roles" or similar), pick the top-listed role from the run summary
   and say: `mark <Company> to apply` (substitute the actual company
   name from the summary).
4. After the status-change confirmation, send: `/job-offer:dashboard`
5. After the dashboard launch message, send: `/job-offer:today`

## Termination

Stop when `/today`'s brief has printed (transcript contains `## Heads-up`
or `Nothing flagged today.`) AND the simulator has acknowledged it
with a brief reply.

## Spec criteria (judge checks)

Each criterion is tagged `[required]` (must be exercised AND pass) or `[opportunistic]` (advisory). See `.claude/skills/test-personas/rubrics/conformance.md` for verdict aggregation rules.

- **[required]** `/setup` precreated `userdata/` (or confirmed it already existed) before the CV prompt
- **[required]** The CV prompt offered the skip in the same message as the ask, and did not spend a second turn on the user declining
- **[required]** `/setup` asked one residence question (Step 1 "city + country") and one geography question (Step 5 "where are you looking") — distinct asks, not redundant
- **[required]** `/setup` did NOT ask the user to confirm a timezone — it is derived from the city, never surfaced
- **[required]** `/setup` did NOT ask for a LinkedIn URL
- **[required]** `/setup` did NOT ask for proof points or a moat — positioning stops at the one-paragraph draft
- **[required]** `/setup` did NOT ask about companies of interest (it moved to `/job-search`)
- **[required]** `/job-search` asked the companies-of-interest question on its first run and wrote a `## Companies of interest` section to `profile.md`
- **[required]** `/setup` did NOT show the weekly-reflection nudge (it was moved to `/today`)
- **[required]** `/setup` did NOT offer the career-coach positioning interview — its closing nudge points at `/job-search`
- **[required]** `/setup`'s automation prompt was 2-step (y/n first, then time) — not bundled
- **[required]** `/job-search` started sweeping without a "say go" style confirmation after the companies question
- **[required]** `/job-search` auto-filed at least one role with `status: new` in `meta.md`
- **[required]** `/job-search` rendered the roles as a table, not a bulleted list, and did not label any row tier-1 / tier-2 or show a score
- **[deterministic]** `/job-search` set `link:` in every new `meta.md`'s frontmatter — decided by `scripts/validate_userdata.py`, never by the judge. Do not assess it from the transcript.
- **[deterministic]** `applications.md` GENERATED block contains a `Link` column — file-side and NOT currently covered by any script (`validate_userdata.py` does not read `applications.md`). A known gap, listed here so it is not mistaken for covered. Do not assess it from the transcript.
- **[required]** The chat rendering of the application row included the URL inline
- **[required]** `/today`'s first run skipped the input-loop prompt entirely (no "anything that moved since last time")
- **[required]** `/today`'s brief rendered Heads-up section ABOVE Pipeline state
- **[required]** `/today`'s Pipeline state gave counts and progress only — no per-role table, no tier labels
- **[required]** Every `/today` heads-up item named an action, not just an observation
- **[required]** `/today` did NOT flag a gap in a file written during this same run
- **[required]** `/today` did NOT include a hardcoded founder-outreach number (no "10 founders")
- **[required]** Each skill's closing message included a context-aware next-step nudge
- **[required]** No assistant turn named a plugin-owned file or a path below `userdata/` — decided by `scripts/lint_transcript.py`'s `lint.file-path` rule, never by the judge. Do not assess it from the transcript.
- **[required]** With no CV present, `/setup` still walked all nine steps and never claimed to have read a CV
- **[required]** `/setup` asked for timeline in one open question with examples in the sentence, not a five-option select, and the resulting `strategy.md` still holds a concrete `YYYY-MM-DD`
- **[required]** `/setup` asked for hard filters in one open question with examples in the sentence, not a six-option multi-select
- **[required]** Geography (Step 5) offered a closed set of named choices (on-site / remote / both / other) rather than an open question — it is the one step whose options stayed prescribed

  *Judge this on what the transcript shows the user, not on which tool produced it.* The criterion used to read "was still offered as an option-based select", and a transcript cannot distinguish an `AskUserQuestion` select from prose listing the same four choices — so the judge scored it PASS on prose and was neither right nor wrong, because the question was unanswerable. What matters to the user is whether the choices were named for them or left open; that is visible, so that is what is asked., because its options are exhaustive and mutually exclusive
