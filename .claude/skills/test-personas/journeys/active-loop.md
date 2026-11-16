---
name: active-loop
persona: maya
snapshot: maya-active
max_turns: 30
---

## Goal

A mid-search user runs the recurring loop: refresh roles, change a
status in chat, apply for one role, prep for an interview, then ask a
former colleague for a referral.

## Opening message

`/job-offer:job-search`

## Mid-journey instructions to the simulator

1. After `/job-search` prints its run summary, pick one TIER-1 role
   from the summary and say: `mark <Company> to apply`
2. After the status-change confirmation, send:
   `/job-offer:apply <Company>` (substitute the company you just marked).
3. The apply skill will ask up to 5 questions. Answer each as Maya
   would (concrete proof points from her persona's "What you know
   about yourself" section, terse where she can be).
4. After `/apply` saves the tailored CV, send:
   `/job-offer:interview-prep <Company>`
5. The prep skill may ask about target stage. If asked, answer
   `hiring manager`.
6. After `/interview-prep` saves the prep doc, send:
   `/job-offer:outreach Wagestream`
   (Maya's people file for Dana Okafor, a former Brightline Credit
   colleague now at Wagestream, is linked to that role.)
7. If asked what kind of message, answer `referral ask`. When the draft
   is shown, reply `sent it on LinkedIn`.

## Termination

Stop when `/outreach` has logged the referral ask (it confirms the
ask was logged, and `people/dana-okafor.md` gained a
`sent referral-ask` line) AND the simulator has acknowledged.

## Spec criteria (judge checks)

Each criterion is tagged `[required]` (must be exercised AND pass) or `[opportunistic]` (advisory). See `.claude/skills/test-personas/rubrics/conformance.md` for verdict aggregation rules.

- **[required]** `/job-search`'s run summary uses plain prose (no fenced code dump)
- **[required]** `/job-search`'s tier counts are bucketed in the summary
- **[required]** Status change in chat triggered the dashboard nudge ("Tip: you can also click the company row in the dashboard...") at most once per session
- **[required]** `/apply` did not exceed 5 questions
- **[required]** `/apply`'s chat summary uses plain prose + bulleted recap (no fenced key:value dump)
- **[required]** `/apply`'s summary cites positioning angle + which proof points it leaned on
- **[required]** `/apply`'s closing offered a clear next-step nudge (cover note, interview-prep, or career-coach)
- **[required]** `/interview-prep` adapted 3-5 stories from Maya's story bank
- **[required]** `/interview-prep`'s closing nudge was context-aware (mentioned interviewer-simulator or interview-analysis appropriately)
- **[required]** `/outreach` found Dana Okafor from the Wagestream role without asking who Maya knows there
- **[required]** `/outreach`'s referral ask uses only facts from Dana's people file, Maya's profile and CV (Brightline Credit, underwriting) — no invented shared projects, metrics or mutual contacts
- **[required]** `/outreach` included a short forwardable blurb with the referral ask
- **[required]** `/outreach` logged the ask only after Maya said it was sent, as one `sent referral-ask (linkedin)` line in `people/dana-okafor.md`, and the validator reports no `person.*` findings
- **[opportunistic]** `/outreach`'s closing line said when a follow-up would be due if Dana doesn't reply
