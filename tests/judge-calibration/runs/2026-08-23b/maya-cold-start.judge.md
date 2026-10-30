# Findings — maya-cold-start

**Run date:** 2026-08-23 (second run of the day; `2026-08-23` is the first)
**Snapshot:** empty

_First run after the verbatim locks were removed from the skills. Quoted prompts
in the SKILL.mds are now examples rather than strings to recite, so the copy in
this transcript was written fresh by the model against `TONE.md`._

## Lint

    No schema drift found.

    No lint findings.

## Groundedness

_Judged twice per Phase 4b (gating rubric returned FAIL). The two calls
disagreed — verdict is `FAIL (one-of-two)`. Call 1 is reproduced below._

### Evidence

| turn | claim | source | grounded |
|---|---|---|---|
| 12 | Profile has been saved | file: `userdata/profile.md` (written this run) | yes |
| 12 | Target is "signed by 31 December" | user: turn 11 | yes |
| 12 | That is "about four and a half months" | user: turn 11 (computed from 2026-12-31) | yes |
| 12 | Cadence is 5 applications + 5 outreach a week, 3 live threads | file: `userdata/strategy.md` (written this run) | yes |
| 15 | Plaid, Klarna, Lendable, Mercury saved to profile | user: turn 15 + file: `userdata/profile.md` | yes |
| 15 | "Found 8 roles worth a look" (table lists 8) | fetch: sweep | yes |
| 15 | The 8 company / title / link rows in the table | fetch: sweep | yes |
| 15 | Deel and Houseful pages wouldn't open, filed unscored | fetch: failed this run | yes |
| 15 | Plaid is US-only at her level; its one London product role is below her floor | fetch: sweep | yes |
| 15 | Klarna has moved job boards and has nothing in product open | fetch: sweep | yes |
| 15 | Mercury has a Head of Product for business lending; all Mercury roles fenced to US/Canada | fetch: sweep | yes |
| 15 | Ebury and dLocal scored well but are sales-led B2B with no self-serve motion | fetch: sweep + user: turn 12 | yes |
| 16 | Lendable — Senior Product Manager (UK Cards) marked to apply | file: `userdata/companies/Lendable/meta.md` | yes |
| 17 | Dashboard is at `http://localhost:7890` | fetch: local server launched this run | yes |
| 17 | Deel and Houseful still unscored | user-visible: turn 15 | yes |
| 18 | Brief saved | file: `userdata/outputs/daily-brief-2026-08-23.md` | yes |
| 18 | 0 of 5 applications out this week | file: `userdata/journal.md` + strategy cadence | yes |
| 18 | Lendable is the one marked | user: turn 16 | yes |
| 18 | Deel and Houseful filed without a score | user-visible: turn 15 | yes |
| 18 | Paddle, Plum and Tide are "three more roles" | none — turn 15's table holds five roles across those three companies | NO |
| 18 | Those roles score "as high as Lendable" | none — no score was shown for any role; turn 15 called Lendable "the best thing in the sweep" | NO |
| 18 | Those roles are all still undecided | file: `meta.md` status `new` | yes |
| 18 | Active: 10 — 1 to apply, 9 new | user-visible: turn 15 (8 scored + 2 unscored) | yes |
| 18 | This week: 0/5 applications, 0/5 outreach | file: `userdata/strategy.md` + pipeline state | yes |
| 18 | "Nothing's logged from your side yet" | file: `userdata/journal.md` (empty) | yes |

### Findings

- **turn 18:** "**Paddle, Plum and Tide** — three more roles scoring as high as Lendable, all still undecided" — the count is not grounded in turn 15's table, which lists two Plum roles and two Tide roles alongside one Paddle role, so the three named companies hold five undecided roles, not three.
- **turn 18:** "three more roles scoring as high as Lendable" — no score or tier was surfaced for any role anywhere in the run, and this comparative claim restates turn 15's own ranking inaccurately, where the sweep told the user "Lendable's cards role is the best thing in the sweep."

### Verdict

**FAIL** — the /today brief introduces a role count and a comparative score claim that contradict the sweep output the user was shown two turns earlier, and groundedness is zero tolerance.

_Note: judge calls disagreed — re-run manually if FAIL is unexpected._

_Call 2 returned **PASS** with no findings, treating "three more roles scoring as
high as Lendable" as grounded in the tier scores stored in `meta.md`. The
disagreement is substantive and worth adjudicating: call 1's objection is that
the scores were never surfaced to the user and that turn 15 had told her
"Lendable's cards role is the best thing in the sweep", so the brief reverses a
ranking she had already acted on; call 2's position is that a claim can be
grounded in a file the run wrote even if the user never saw it. The rubric's own
"restating in-run content counts" example favours call 1._

## Coherence

### Findings

- **turn 12:** "One thing before we're done — want your daily brief to run automatically each day, or would you rather kick it off yourself?" — Rule 1: the daily brief has not been mentioned once in the preceding eleven turns and is never described, so the user is asked to make a scheduling decision about an artefact she cannot picture; turn 13's "All yours to run, then." closes the thread without ever naming the command that runs it, leaving her holding a commitment with no mechanism (she has to guess `/job-offer:today` unaided at turn 18).
- **turn 15:** "| Company | Role | Why it fits | Link |" against the rows "right level, wrong country", "savings fintech, Berlin relocation" and "credit fintech, Spain-remote only" — Rule 4: a column promising why each role fits, inside a list introduced as "Found 8 roles worth a look", contains three entries whose stated content is why the role does not fit, so the user cannot tell whether these are recommendations or exclusions.
- **turns 15 and 17:** turn 15 — "Two pages wouldn't open, so I've filed them unscored rather than guess: - Deel … - Houseful …"; turn 17 — "Deel and Houseful are still sitting there without a score, since neither page would open for me — paste either link back and I'll have another go." — Rule 3: the same status and the same remedy land twice two turns apart with nothing added, and turn 18's heads-up repeats the closing clause verbatim a third time ("paste either link back and I'll have another go").
- **turns 15 and 16:** turn 15 — "Open `/job-offer:dashboard` to sort through these — or just tell me here which ones you want to go after."; turn 16 — "You can do this in the dashboard too, if you'd rather click than type." — Rule 3: the click-or-type choice is offered again in the immediately following turn, after the user has already answered it by typing, which reads as not having noticed her answer.
- **turns 15 and 18:** turn 15 — "On your four: Lendable's cards role is the best thing in the sweep."; turn 18 — "**Paddle, Plum and Tide** — three more roles scoring as high as Lendable, all still undecided → pick or drop them before Monday." — Rule 4: the sweep named Lendable the single best result and the user acted on that in turn 16, then the brief silently asserts three roles score as high, reversing the basis of a decision she has already made without acknowledging the change.

### Verdict

**FAIL** — the setup flow itself is well sequenced, but the brief at turn 18 contradicts the sweep's headline claim that "Lendable's cards role is the best thing in the sweep" after the user had already committed to Lendable on that basis, and the turn 15 table files three non-fit reasons under a "Why it fits" header, giving the user two moments where she must stop and work out which statement to believe.

## Conformance

### Findings

- No findings.

### Verdict

**PASS** — All five cross-journey criteria held (Turn 18's `/today` close names the user's actual state and next move; Turn 15's "Saved Plaid, Klarna, Lendable and Mercury to your profile" confirms the profile write; the sweep table carries a live URL per row; no skill ended mid-prompt; the only past-activity reference, "Nothing's logged from your side yet," is accurate for a first run), and every in-scope journey spec criterion was exercised and met — the CV prompt bundled its skip and cost no extra turn, residence (Turn 3) and geography (Turn 8) were distinct asks with geography still option-based, timezone / LinkedIn / proof-points / moat / companies-of-interest were never asked in `/setup`, timeline (Turn 10) and hard filters (Turn 11) were single open questions with in-sentence examples yielding a concrete 2026-12-31, the automation prompt was y/n-first, `/setup` closed pointing at `/job-search`, `/job-search` asked the companies question and swept without a "say go", filed roles as `new`, and rendered them as a table with no tier labels or scores, and `/today` skipped the input loop, put Heads-up above a counts-only Pipeline state, and gave every heads-up item an action.

## Tone

### Findings

- **turn 7:** "If you want to do it now, paste one to three sentences on what you're best at and I'll shape it into a paragraph. Otherwise say skip and we'll keep moving." — Restates the fork the sentence above it already gave ("Two ways to do it: write it now, or skip"), so the one long question in setup is long because of repetition, not substance.
- **turn 12:** "Tell me if those numbers feel off and I'll redo them.\n\nOne thing before we're done — want your daily brief to run automatically each day, or would you rather kick it off yourself?" — Rule A violation: two unrelated decisions (whether the weekly cadence is right, and whether the brief runs itself) bundled into one message, and the user's reply has to answer both.
- **turn 15:** "| Tide | Lead Product Manager, Banking Payments | right level, wrong country |" — The column is headed "Why it fits" but three rows carry reasons the role does *not* fit ("wrong country", "Berlin relocation", "Spain-remote only"), forcing the user to re-read a table built to be skimmed.
- **turn 15:** "Say the word and I'll file them.\n\nOpen `/job-offer:dashboard` to sort through these — or just tell me here which ones you want to go after." — Rule A violation again: a yes/no on filing the two excluded roles is stacked under a separate ask about which of the eight to pursue, and the first ask is dropped by the user and never picked back up by the assistant.
- **turn 18:** "**Deel and Houseful** — filed without a score because neither page would open → paste either link back and I'll have another go." — Near-verbatim repeat of turn 17's "Deel and Houseful are still sitting there without a score, since neither page would open for me — paste either link back and I'll have another go", the third time in four turns the user is told the same thing.

### Verdict

**FAIL** — The voice itself is clean throughout (direct single-line asks, plain English, skip offered on the optional questions, no internal vocabulary or motivational register), but bundled asks recur in turns 12 and 15 rather than appearing once, and in turn 15 the bundling visibly costs the user a decision that then goes unanswered by both sides.

## Verdict

    Lint:          PASS
    Groundedness:  FAIL (2, one-of-two)
    Coherence:     FAIL (5)
    Conformance:   PASS
    Tone:          FAIL (5)

    Gate: Lint AND Groundedness AND Conformance

**Overall: FAIL**
