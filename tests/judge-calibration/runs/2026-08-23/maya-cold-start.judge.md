# Findings — maya-cold-start

**Run date:** 2026-08-23
**Snapshot:** empty

_Run against the working tree after the 2026-08-23 fixes to `/setup`,
`/job-search`, `/today`, `/dashboard`, `references/cv-extraction.md`,
`rubrics/tone.md` and `scripts/lint_transcript.py`. The predecessor is
`2026-08-22/maya-cold-start`._

## Lint

    No schema drift found.

    turn 20: lint.file-path — 'applications.md' named in user-facing text: "…d to `userdata/outputs/daily-brief-2026-08-23.md`, and `applications.md` is now generated."
    turn 20: lint.file-path — 'userdata/outputs/daily-brief-2026-08-23.md' named in user-facing text: "Saved to `userdata/outputs/daily-brief-2026-08-23.md`, and `applications.md` is now genera…"

## Groundedness

### Evidence

| turn | claim | source | grounded |
|---|---|---|---|
| 2 | Setup is nine steps | file: `plugin/skills/setup/SKILL.md` (inlined for the run) | yes |
| 8 | Maya has nine years in consumer credit and growth-stage B2C SaaS | user: turn 8 | yes |
| 8 | She owns the growth pricing surface at a Series B fintech building a BNPL card for thin-file customers | user: turn 8 | yes |
| 8 | Her strongest work is pricing and underwriting | user: turn 8 | yes |
| 12 | End of September is about five weeks out from here, not four months | user: turn 12 + run date 2026-08-23 | yes |
| 13 | Target offer date is 2026-09-30 | user: turn 13 | yes |
| 14 | Plan is 12 applications and 10 outreach messages a week, 5 live interview threads | file: `userdata/strategy.md` (written this run) | yes |
| 14 | The date is five weeks out | user: turn 13 + run date | yes |
| 17 | The four named companies were saved to the profile | file: `userdata/profile.md` | yes |
| 17 | Five roles found | fetch: sweep results rendered in the same turn | yes |
| 17 | Lendable — Senior Product Manager (UK Cards), consumer credit, London | fetch: `jobs.ashbyhq.com/lendable/636b90ec…` | yes |
| 17 | Paddle — Staff Product Manager, Checkout | fetch: `jobs.ashbyhq.com/paddle/cde17e70…` | yes |
| 17 | Ebury — Senior Product Manager, Fraud Prevention, London | fetch: `job-boards.eu.greenhouse.io/ebury/jobs/4951646101` | yes |
| 17 | Hopper — Principal Product Manager, Pricing, wrong industry | fetch: `jobs.ashbyhq.com/hopper/0482ca59…` + user: turn 7 | yes |
| 17 | Zopa — Senior Product Manager, B2B, consumer lender, wrong city | fetch: `jobs.lever.co/zopa/9b8b5cdd…` | yes |
| 17 | Ebury KYC/KYB posting shares team and base title with the fraud posting | fetch: `job-boards.eu.greenhouse.io/ebury/jobs/4951647101` | yes |
| 17 | Second Lendable Senior PM posting is based in Virginia | fetch: `jobs.ashbyhq.com/lendable/d676fe6a…` | yes |
| 17 | Plaid's product openings are all SF or NY, except a Product Manager, Europe in London | fetch: `jobs.ashbyhq.com/plaid/29d1f5fc…` | yes |
| 17 | That Plaid role sits a level below Maya's targets | user: turns 6 and 17 fetch | yes |
| 17 | Mercury's roles are US or Canada only, failing the no-relocation line | fetch: sweep + user: turn 14 | yes |
| 17 | Klarna has nothing open in product at any level | fetch: sweep (negative result) | yes |
| 17 | All four named companies set to re-check on future sweeps | file: `userdata/companies/*/meta.md` (written this run) | yes |
| 18 | Lendable — Senior Product Manager (UK Cards) marked to apply | file: `userdata/companies/Lendable/meta.md` | yes |
| 19 | Dashboard is served at `http://localhost:7890` | file: dashboard server launched this run | yes |
| 19 | Lendable is the only role committed to so far | user: turn 18 | yes |
| 20 | Weekly application target is 12; 0 sent | file: `userdata/strategy.md` + `userdata/journal.md` | yes |
| 20 | Active: 5 — 1 to apply (Lendable), 4 new | file: `userdata/companies/*/meta.md` | yes |
| 20 | This week: 0/12 applications, 0/10 outreach | file: `userdata/strategy.md` + `userdata/journal.md` | yes |
| 20 | Brief saved to `userdata/outputs/daily-brief-2026-08-23.md`; `applications.md` regenerated | file: written this run | yes |
| 20 | Four roles still sitting in `new` | file: `userdata/companies/*/meta.md` | yes |

### Findings

No findings.

### Verdict

**PASS** — every claim traces to a user turn, a file the run wrote, or a posting the sweep fetched; counts and cadence numbers stay identical across turns 14, 17, 18 and 20, and the sweep reports its negative results (Klarna, Mercury, Plaid) rather than filling the gaps in.

## Coherence

### Findings

- **turn 14 / turn 15:** "Setup's done. I've got your profile, and a plan..." then, one turn later, "Setup done. Run `/job-offer:job-search` and I'll go find roles that match." — Rule 3: the same completion beat lands twice in adjacent turns with near-identical phrasing, so the user is told the setup finished twice with nothing new added the second time.
- **turn 17 / turn 18:** "Open `/job-offer:dashboard` to sort through these — or just tell me here which ones you want to go after." then, after the user chose to tell it here, "You can do this in the dashboard too, if you'd rather click than type." — Rule 3: the dashboard-vs-chat choice is re-offered immediately after the user resolved it, which reads as not having tracked the answer they just gave.
- **turn 20:** "Send 12 more applications this week (0/12)." — Rule 4: "more" presupposes applications already sent, which the same line's own counter and the pipeline block ("This week: 0/12 applications") contradict, leaving the user unsure whether the brief thinks they have started.

### Verdict

**PASS** — The thread holds together throughout: the date discrepancy at turn 12 is resolved and correctly carried into turn 14's cadence, the sweep at turn 17 answers the four companies named at turn 17, and turn 20's brief reconciles cleanly with the five roles and the one `to_apply` decision; the three findings are small redundancies and one loose word, none of which would make the user stop and reread.

## Conformance

### Findings

No findings.

### Verdict

**PASS** — Every in-scope `[required]` criterion held: `/setup` walked all nine steps with no CV and no timezone, LinkedIn, proof-point, moat, companies, or reflection asks (Turns 2-14), timeline and hard filters came as single open questions with in-sentence examples while geography stayed an option select (Turns 9, 11, 13), the automation prompt was y/n-first (Turn 14), `/job-search` asked the companies question and swept without a go-confirmation, rendered a table with inline links and no tier labels or scores, and confirmed the profile write ("Saved those four to your profile," Turn 17), `/today`'s first run skipped the input loop and put Heads-up above a counts-only Pipeline state with no invented gaps (Turn 20), and each skill closed on a state-aware nudge ("Four roles are still sitting in `new` — tell me which ones you want and I'll mark them, otherwise they just age").

## Tone

### Findings

- **turn 8:** "Edit anything that doesn't sound like you — drafts are starting points, not finished copy." — the second clause restates the first as a generic aphorism, which is filler in a voice that is otherwise plain and direct.
- **turn 15:** "Setup done." — turn 14 already opened with "Setup's done."; repeating the completion line one turn later is restatement the user has already read.
- **turn 17:** "| Hopper | Principal Product Manager, Pricing | elasticity work, wrong industry |" — the column is headed "Why it fits" and the cell gives a reason it doesn't, so the label works against its own content (same in the Zopa row: "consumer lender, wrong city").
- **turn 17:** "I've set all four to be re-checked on future sweeps." — "future sweeps" is the plugin's internal name for its recheck pass; the user has no model of a sweep schedule, especially having just declined the daily automation.
- **turn 18:** "You can do this in the dashboard too, if you'd rather click than type." — an unsolicited nudge delivered immediately after the user completed the task successfully by typing, which is asking after the value was already delivered.
- **turn 19:** "To add a new role, drop the link to me here and I'll score and file it." — "score and file" is internal pipeline vocabulary (a tier score the user has never been shown, plus writing to disk), not something the user asked about.
- **turn 20:** "Send 12 more applications this week (0/12)." — "more" implies applications already sent, which contradicts the 0/12 in the same line.
- **turn 20:** "Four roles are still sitting in `new`" — `new` is the raw internal state value, backticked in chat, exposing the pipeline's own vocabulary to the user.
- **turn 20:** "otherwise they just age" — a faintly nagging close on a brief that had already said everything it needed to, in a register the product doesn't otherwise use.

### Verdict

**FAIL** — the voice is mostly plain and direct (the date-conflict catch in turn 12 and the terse setup asks are good), but three separate turns leak the assistant's own machinery to the user — "future sweeps", "score and file", and the raw `new` state — and that shared cause is a systematic problem rather than a set of individually forgivable nitpicks.

## Verdict

    Lint:          FAIL (2)
    Groundedness:  PASS
    Coherence:     PASS
    Conformance:   PASS
    Tone:          FAIL (9)

    Gate: Lint AND Groundedness AND Conformance

**Overall: FAIL**
