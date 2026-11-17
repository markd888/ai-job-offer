# Findings — maya-application-to-interview

**Run date:** 2026-11-16
**Snapshot:** maya-active

## Lint

No schema drift found.

turn 3: lint.file-path — 'profile.md' named in user-facing text: "…ailored CV would ask again. If you want it on every CV, add a `phone:` line to profile.md."

## Groundedness

### Evidence

| turn | claim | source | grounded |
|---|---|---|---|
| 1 | The Zopa role owns risk-pricing on loans and cards | file: `companies/Zopa/research-brief.md` ("Owns the credit product surface (loans, cards, risk-pricing)") | yes |
| 1 | NorthLoop has price tests / a price-test framework with +18% MRR | file: `cv.md` | yes |
| 1 | Brightline underwriting work: new bureau, 12% lower decline rate for thin-file applicants | file: `cv.md` | yes |
| 2 | Tailored CV drafted and saved for Zopa — Senior PM, Consumer Credit | file: `companies/Zopa/cv-2026-11-06.md`, `companies/Zopa/meta.md` (position) | yes |
| 2 | Proof points: bureau integration (12% decline-rate cut, default flat), credit policy review with Head of Risk, NorthLoop +18% MRR | file: `cv.md` | yes |
| 2 | Dropped the "most technical PM in the room" line from the summary | file: `cv.md` vs `companies/Zopa/cv-2026-11-06.md` | yes |
| 2 | Credit policy review moved to second bullet at Brightline | file: `cv.md` vs `companies/Zopa/cv-2026-11-06.md` | yes |
| 2 | NorthLoop price-test bullet reworded to "what customers pay for the card" | file: `companies/Zopa/cv-2026-11-06.md`; user: turn 2 | yes |
| 2 | First Skills line reordered to lead with credit underwriting | file: `cv.md` vs `companies/Zopa/cv-2026-11-06.md` | yes |
| 2 | Left out: risk-pricing, personal loans | file: `companies/Zopa/ats-check-2026-11-06.md` (Missing); user: turn 2 | yes |
| 2 | No phone number on the CV (initial build) | file: `cv.md`, `profile.md` (neither holds a phone) | yes |
| 2 | One page, text extracts in order, 10 of 12 posting keywords covered | file: `companies/Zopa/ats-check-2026-11-06.md` | yes |
| 3 | Phone now in header next to email and LinkedIn; PDF rebuilt | file: `companies/Zopa/cv-2026-11-06.md`, `companies/Zopa/Maya_Patel_CV_Zopa.pdf` | yes |
| 3 | ATS check passes: one page, phone and email found, text in order, 10 of 12 keywords; gaps risk-pricing and personal loans | file: `companies/Zopa/ats-check-2026-11-06.md` | yes |
| 3 | Master CV and profile don't have the phone number | file: `cv.md`, `profile.md` | yes |
| 5 | Application recorded with the CV kept on file, not the posting text | file: `companies/Zopa/submitted-2026-11-06/manifest.md` ("Posting text was not captured") | yes |
| 5 | Follow-up comes up on 26 Nov | file: `companies/Zopa/meta.md` date_applied (pre-skip 2026-11-16) + 10-day rule in follow-up script | yes |
| 6 | Six applications quiet long enough (Plaid excluded) | file: company `meta.md` files; follow-ups script excludes interviewing roles with a `next_event` (Plaid has one) | yes |
| 6 | Zopa — Senior PM, Consumer Credit — quiet 10d — URL | file: `companies/Zopa/meta.md` (date_applied 2026-11-06, link) | yes |
| 6 | Brex — Lead PM, Spend — quiet 12d — URL | file: `companies/Brex/meta.md` (last_inbound 2026-11-04, link) | yes |
| 6 | Marshmallow — Senior PM, Pricing & Risk — quiet 15d — URL | file: `companies/Marshmallow/meta.md` (date_applied 2026-11-01, link) | yes |
| 6 | Ramp — Group PM, Card — quiet 16d — URL | file: `companies/Ramp/meta.md` (date_applied 2026-10-31, link) | yes |
| 6 | Anthropic — Lead PM, Claude Code — quiet 18d — URL | file: `companies/Anthropic/lead-pm-claude-code/meta.md` (date_applied 2026-10-29, link) | yes |
| 6 | Cleo — Senior PM, Growth — quiet 20d — URL | file: `companies/Cleo/meta.md` (last_inbound 2026-10-27, link) | yes |
| 6 | Zopa: tailored CV sent, exact copy on file | file: `companies/Zopa/submitted-2026-11-06/` | yes |
| 6 | Cleo: HM round with Priya; recruiter's last word on 27 Oct "we'll be back in touch shortly" | file: `companies/Cleo/meta.md` History | yes |
| 6 | Marshmallow is a top-priority role; cover note angle pricing experiments plus consumer-credit risk | file: `companies/Marshmallow/meta.md` (tier P0; 2026-11-01 History line) | yes |
| 6 | iwoca silent 36 days since applying | file: `companies/iwoca/meta.md` (date_applied 2026-10-11) | yes |
| 7 | CV sent on 6 Nov; applied through careers site | file: `companies/Zopa/meta.md`, `submitted-2026-11-06/manifest.md` | yes |
| 7 | Draft content: Brightline bureau integration, 12% decline-rate cut on thin-file, default flat | file: `companies/Zopa/submitted-2026-11-06/cv-2026-11-06.md` | yes |
| 7 | No name or inbox for anyone at Zopa | file: `companies/Zopa/meta.md` (channel company-site, no contact), `notes.md` (empty) | yes |
| 8 | First follow-up logged, sent today by email to hiring team | file: `companies/Zopa/meta.md`, `follow-up-2026-11-16.md`; user: turn 8 | yes |
| 8 | Zopa back on the list 26 Nov for one last nudge; two is the limit | file: `companies/Zopa/meta.md` (last_follow_up 2026-11-16) + follow-up rule (fewer than 2) | yes |
| 8 | Cleo has a named contact | file: `companies/Cleo/meta.md` (Lisa, Priya) | yes |
| 9 | 30-minute screen Thursday 19 Nov at 14:00 | user: turn 9; 2026-11-19 is a Thursday | yes |
| 9 | Zopa still shows as applied | file: `companies/Zopa/meta.md` (status before turn 10) | yes |
| 10 | Zopa marked interviewing, next event the screen | file: `companies/Zopa/meta.md` | yes |
| 11 | Working from the CV sent on 6 Nov | file: `companies/Zopa/submitted-2026-11-06/` | yes |
| 11 | Payments pricing experiment is card pricing and matches the CV | file: `stories/payments-pricing-experiment.md`, `cv.md` | yes |
| 11 | Activation funnel numbers are on the CV | file: `stories/activation-funnel-uplift.md`, `companies/Zopa/cv-2026-11-06.md` (4.1% to 6.8%) | yes |
| 11 | Risk team dissent lowers APR on a loan book | file: `stories/risk-team-dissent.md` | yes |
| 11 | Underwriting zero-to-one builds a lending model | file: `stories/underwriting-zero-to-one.md` | yes |
| 11 | User asked to keep risk-set pricing and loans off the CV | user: turn 2 | yes |
| 11 | Consumer credit onboarding pivot is a lending funnel the CV doesn't mention | file: `stories/consumer-credit-onboarding-pivot.md`, `companies/Zopa/cv-2026-11-06.md` | yes |
| 11 | Pricing story includes late-fee and interchange tests; CV says Lead PM | file: `stories/payments-pricing-experiment.md`, `cv.md` | yes |
| 11 | Pricing story says Senior PM | file: `stories/payments-pricing-experiment.md` ("as the Senior PM on the growth squad") | yes |
| 11 | Monthly-cap test ran on a risk-screened group | file: `stories/payments-pricing-experiment.md` (behaviour-eligibility-screened cohort; cohort selection built with the risk lead) | yes |
| 11 | No story covers the Brightline bureau work | file: `stories/*.md` (none covers it) | yes |
| 12 | Prep saved for Thursday's recruiter screen | file: `companies/Zopa/interview-prep-2026-11-17.md` | yes |
| 12 | Why Zopa: consumer credit, real pricing and risk calls | file: `companies/Zopa/research-brief.md` | yes |
| 12 | Why this role: Brightline bureau, decline rate down 12% on thin-file, default flat | file: `cv.md` | yes |
| 12 | Salary: aim at £110K, push back under £90K | file: `profile.md` (salary_band "£90-110K IC") | yes |
| 12 | Pricing story: framework as 0-to-1, +18% MRR | file: `stories/payments-pricing-experiment.md` | yes |
| 12 | Activation story: own SQL found the split, 4.1% to 6.8% | file: `stories/activation-funnel-uplift.md` | yes |
| 12 | Both stories told as Lead PM, as on the CV | file: `cv.md`, `companies/Zopa/interview-prep-2026-11-17.md` | yes |
| 12 | Four questions for the recruiter incl. salary band, band not found | file: `companies/Zopa/interview-prep-2026-11-17.md` | yes |
| 12 | Three team-running questions parked for the hiring-manager round | file: `companies/Zopa/interview-prep-2026-11-17.md` | yes |

### Findings

No findings.

### Verdict

**PASS** — every company, date, quiet-day count, URL, metric, story detail and file reference traces to a file in the workspace or to the user's own turns, and no claim restates an earlier number differently.

## Coherence

### Findings

- **turn 3:** "It still covers 10 of the 12 posting keywords. The two gaps are risk-pricing and personal loans, which stay out because nothing in your record backs them." (turn 2: "10 of 12 posting keywords covered. The two gaps are the ones above." and "Left out, nothing in your record backs them: risk-pricing, personal loans") — Rule 3: the keyword count, the two gaps and the reason they stay out are said again in full one turn later, when the only new fact is that the phone number fixed the check.
- **turn 12:** "The three questions about how the team runs are parked for the hiring-manager round." — Rule 1: "the three questions" uses a definite article as if the user already knows them, but no team-process questions were mentioned in turn 11 or anywhere earlier, so the user cannot tell which questions are meant.
- **turn 10:** "It won't show up on the follow-up list while that screen is pending." (turn 9: "Zopa is off the quiet list and won't come up for a second nudge.") — Rule 4: turn 9 says Zopa is permanently off the nudge list, and the next turn makes that depend on the screen still being pending. The difference is small, but it leaves the user unsure whether Zopa could come back.

### Verdict

**PASS**: The run hangs together from CV to sent application, follow-up, reply, status change and prep. Each turn builds on the last, the Brightline thread is carried through and explained when the prep moves it from the stories into the pitch, and the three findings are small redundancies or loose phrasings that would not disorient the user.

## Conformance

### Findings

No findings.

### Verdict

**PASS** — every in-scope [required] criterion was exercised and matched its contract: /apply asked three questions and wrote `cv-2026-11-06.md` using only master-CV, profile and answer content; the ATS report is one page with all hard checks passing and no keywords added; /sent asked before writing ("I'll record your Zopa application as sent today... OK?") and its confirmation named the due date ("the follow-up comes up on 26 Nov") with no files or field names; meta.md, the `submitted-2026-11-06/` archive, the History and journal lines for sent, follow-up #1, the recruiter reply and the interviewing transition are all present and written in the right order; the reply alone left status at applied ("Zopa still shows as applied. Should I move it to interviewing...?"); the follow-up draft uses only the archived CV's Brightline claim, has a subject line and is saved as `follow-up-2026-11-16.md`; the recruiter-stage prep is built from the two chosen stories and the research brief with no invented Zopa facts; profile.md and strategy.md are unchanged apart from date rebasing; and the run ends with a state-aware nudge ("After Thursday, run `/job-offer:interview-analysis Zopa`"). Criterion 5 (JD link in a new-role chat row) was not exercised because neither /job-search nor /evaluate-position ran.

## Tone

### Findings

- **turn 3:** "If you want it on every CV, add a `phone:` line to profile.md." — Internal detail leaking (low-effort-first too): it tells the user to hand-edit a raw config key instead of offering to save the number, and exposes storage syntax they had no reason to see.
- **turn 4:** "I'll record your Zopa application as sent today through their careers site, and keep a copy of today's tailored CV as the version you sent. OK?" — A question the product should answer for itself: the user had just said "sent it through their careers site", so this confirmation turn adds nothing their answer didn't already settle.
- **turn 5:** "Recorded, with the CV you sent kept on file, though not the posting text itself." — Internal detail leaking: an unprompted aside about what is and isn't stored, the same shape as the calibration example "same `meta.md` underneath".
- **turn 6:** "I'll only do that if you say yes. Which one should I draft first?" — Rule A, one ask per message: closing out iwoca and choosing which follow-up to draft are unrelated decisions bundled into one message, and the user answered only one of them.
- **turn 9:** "Zopa still shows as applied. Should I move it to interviewing, with the screen as the next thing coming up?" — A question the product should answer for itself: a scheduled recruiter screen settles the status, yet the user has to spend a turn ("mark Zopa as interviewing") saying so. This is the second time in the run, after turn 4, that an obvious update was held behind a permission question.
- **turn 11:** "Risk team dissent lowers APR on a loan book and Underwriting zero-to-one builds a lending model, and you told me to keep risk-set pricing and loans off this CV." — Simple language / prose too dense to skim: story titles run unmarked into the sentence, so it reads like a garbled claim rather than two named stories being set aside, inside an already heavy paragraph.

### Verdict

**FAIL** — The drafted nudge and most turns read cleanly, but two causes repeat: internal storage detail reaches the user (turns 3, 5), and the run asks permission for updates the user had already settled (turns 4, 9). Under the rubric, a repeated cause is a voice problem, not a set of nitpicks.

## Verdict

    Lint:          FAIL (1)
    Groundedness:  PASS
    Coherence:     PASS
    Conformance:   PASS
    Tone:          FAIL (6)

    Gate: Lint AND Groundedness AND Conformance

**Overall: FAIL**
