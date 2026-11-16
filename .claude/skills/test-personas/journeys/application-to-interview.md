---
name: application-to-interview
persona: maya
snapshot: maya-active
max_turns: 30
---

## Goal

One application followed from the CV to the first interview: tailor the CV,
check it parses, record that it went out, wait ten days, chase it, log the
reply, move the role to interviewing and prep for the screen. Every step
writes a field the next step reads — this journey is the chain, end to end.

The role is Zopa (`companies/Zopa/`, `status: to_apply`, flat layout).

## Opening message

`/job-offer:apply Zopa`

## Mid-journey instructions to the simulator

1. `/apply` asks up to five questions. Answer as Maya would — concrete, from
   her persona's "What you know about yourself", terse where she can be.
2. If `/apply` saves the tailored CV without running the ATS check itself,
   send: `/job-offer:ats-check Zopa`
3. Once the ATS check has reported, say: `sent it through their careers site`
   (this is `/job-offer:sent`; confirm with `yes` if asked).
4. **Orchestrator time skip** (see below) happens here, before the next user
   turn. Then send: `/job-offer:follow-up`
5. When the follow-up list shows Zopa, pick it. When the draft is shown,
   reply: `sent it by email to the hiring team`
6. Then: `Zopa replied today — the recruiter wants a 30-minute screen on Thursday at 14:00`
7. If asked whether to change the status, or after the reply is logged, say:
   `mark Zopa as interviewing`
8. Then: `/job-offer:interview-prep Zopa`. If asked for the stage, answer
   `recruiter screen`.

## Orchestrator steps

Run by the harness itself, never shown to either sub-agent as a message:

- **After the turn in which `/sent` confirms the application** (Zopa's
  `meta.md` now has `status: applied` and a `date_applied`), move the clock
  ten days forward:

  ```bash
  python3 scripts/rebase_fixture_dates.py --time-skip 10 --root userdata
  ```

  Append `## Orchestrator — time skip: 10 days` to the transcript so the judge
  reads the dates that follow correctly. Every date already in `userdata/`
  moves ten days back; the wall clock is unchanged, so to the skills ten days
  have passed.

## Termination

Stop when `companies/Zopa/interview-prep-<date>.md` exists AND the simulator
has acknowledged, or at `max_turns`.

## Spec criteria (judge checks)

Each criterion is tagged `[required]` (must be exercised AND pass) or
`[opportunistic]` (advisory). See
`.claude/skills/test-personas/rubrics/conformance.md` for verdict aggregation
rules. "Today" below is the run date; after the time skip the application date
reads as today − 10.

**Fields written at each step** — the judge reads `companies/Zopa/meta.md`,
the role folder and `journal.md` as they stand at the end of the run:

- **[required]** `/apply`: `cv-<date>.md` in `companies/Zopa/`; no more than five questions; nothing in it absent from `cv.md`, `profile.md` or Maya's answers
- **[required]** ATS check: an `ats-check-<date>.md` in `companies/Zopa/` reporting one page and passing the hard checks; any keyword added to the CV is supported by `cv.md` or `profile.md`
- **[required]** `/sent`: nothing written before Maya's yes; then `status: applied`, `date_applied` (today − 10 after the skip), `channel: company-site`, a `submitted-<date>/` folder holding the CV and the ATS report, one `## History` line, and a journal line `- [Zopa] Application sent via company-site. (source: user)`
- **[required]** `/sent`'s confirmation names when the follow-up comes due (date_applied + 10) and names no files or field names
- **[required]** `/follow-up` lists Zopa as due (quiet 10 days) from `follow-ups.py`, not from its own date arithmetic
- **[required]** The follow-up draft uses only claims from what was submitted (the archived CV), has a subject line (email), and is saved as `follow-up-<date>.md`
- **[required]** After "sent it by email": `follow_ups: 1`, `last_follow_up: <today>`, a History line `follow-up #1 sent via email to hiring team`, and a journal line — and none of it before Maya said it was sent
- **[required]** The reply is logged with `record-inbound.py`: `last_inbound: <today>`, a History line naming the recruiter's reply, a journal line; `status` NOT changed by the reply alone
- **[required]** `status: interviewing` only after "mark Zopa as interviewing", with a History line; `next_event` set only if the skill's contract allows it from a user statement — never invented
- **[required]** `/interview-prep` writes `interview-prep-<date>.md` for the recruiter stage, from Maya's story bank and Zopa's research brief, inventing no Zopa facts
- **[required]** `scripts/validate_userdata.py` reports no findings for `companies/Zopa/` at the end of the run
- **[opportunistic]** The first in-chat status change carried the dashboard nudge once
- **[opportunistic]** `/interview-prep`'s closing line points to `/job-offer:interview-analysis` after the call
