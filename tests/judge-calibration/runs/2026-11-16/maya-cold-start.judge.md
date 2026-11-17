# Findings — maya-cold-start

**Run date:** 2026-11-16
**Snapshot:** empty

## Lint

No schema drift found.

No lint findings.

## Groundedness

### Evidence

| turn | claim | source | grounded |
|---|---|---|---|
| 8 | Positioning: Senior PM, nine years across consumer credit and growth-stage B2C SaaS; owns growth pricing at a Series B BNPL fintech serving thin-file customers; MRR +18% in Q3 with no churn hit; 0→1 bureau integration cut thin-file declines 12% without raising defaults | user: turn 8 | yes |
| 13 | Target "land the offer by 3 May 2027" | user: turn 12 ("About four months") + file: `plugin/skills/setup/SKILL.md` timeline table ("~4 months or more → today + 24 weeks"; 2026-11-16 + 24 weeks = 2027-05-03) | yes |
| 13 | 5 applications and 5 outreach messages a week, 3 live interview threads | file: `userdata/strategy.md` (weekly_targets 5/5, active_interview_threads 3) | yes |
| 14 | Target date moved to 16 March 2027 | user: turn 14 ("mid-March"); file: `userdata/strategy.md` (target_offer_date: 2027-03-16) | yes |
| 14 | Weekly numbers unchanged: 5 applications, 5 outreach, 3 live interview threads | file: `userdata/strategy.md` | yes |
| 15 | Brief would run every day at 9:00; scheduling not set up from this session | user: turn 15 ("9am"); reporting its own inability, not a fact about external state | yes |
| 17 | Plaid, Klarna, Lendable, Mercury saved to profile as watched companies | file: `userdata/profile.md` (## Companies of interest lists all four) | yes |
| 17 | Found 3 roles worth a look | file: `userdata/companies/{Affirm,Lendable/senior-product-manager-us-cards,Lendable/senior-product-manager-crm-growth}/meta.md` | yes |
| 17 | Lendable Senior PM (US Cards), "card pricing and credit lines, London", URL `https://jobs.ashbyhq.com/lendable/5e6c5b4d-…` | file: `companies/Lendable/senior-product-manager-us-cards/{meta,research-brief}.md` (credit line management, pricing and proposition; London hybrid; link matches) | yes |
| 17 | Lendable Senior PM (CRM & Growth), "right lender, lifecycle not pricing", URL `https://jobs.ashbyhq.com/lendable/58381ca8-…` | file: `companies/Lendable/senior-product-manager-crm-growth/{meta,research-brief}.md` (link matches; brief's "Honest gap") | yes |
| 17 | Affirm Senior PM, "BNPL repayments, remote UK, well paid", URL `https://job-boards.greenhouse.io/affirm/jobs/8020318003` | file: `companies/Affirm/{meta,research-brief}.md` (repayment experience; location Remote UK; comp £120-168K; link matches) | yes |
| 17 | Every open product role at Plaid and Mercury is in the US | fetch: Plaid Ashby and Mercury Greenhouse boards during the recheck (their roles are recorded in `userdata/outputs/seen-roles.jsonl`; locations weren't saved to disk) | yes |
| 17 | Klarna has no product manager roles open right now | fetch: Klarna recheck during this run (no Klarna rows in `seen-roles.jsonl`, consistent with an empty result) | yes |
| 17 | All three roles above are senior IC jobs | file: research briefs (US Cards "Senior PM IC role with no reports"; Affirm "it's an IC role"); all three titles are Senior Product Manager in meta.md | yes |
| 17 | Nothing live at Head of Product or Lead level matched | file: `seen-roles.jsonl` (Head/Lead roles were surfaced, but none was filed as a company folder) | yes |
| 19 | Lendable US Cards marked to apply; CRM & Growth unchanged | file: `companies/Lendable/senior-product-manager-us-cards/meta.md` (status: to_apply); `…/crm-growth/meta.md` (status: new) | yes |
| 19 | User's CV isn't in the folder yet | file: workspace listing (no `userdata/cv.md`); user: turn 2 | yes |
| 20 | Launch command `python3 <plugin-clone>/plugin/dashboard/serve.py --userdata … --port 7890` | file: `plugin/skills/dashboard/SKILL.md` line 41; `plugin/dashboard/serve.py` exists | yes |
| 20 | Opens at http://localhost:7890; change status, add note, archive a role inline | file: `plugin/skills/dashboard/SKILL.md` lines 31, 67 | yes |
| 20 | Affirm and Lendable CRM & Growth still waiting on a yes or no | file: both meta.md files (status: new) | yes |
| 21 | Applications this week 0/5, outreach 0/5 | file: `userdata/strategy.md` (targets 5/5); `userdata/outputs/applications.md` (no applied rows; outreach 0 / 5) | yes |
| 21 | Lendable US Cards marked to apply but no CV in folder | file: US Cards meta.md (to_apply); no `userdata/cv.md` | yes |
| 21 | Affirm and Lendable CRM & Growth still waiting on a decision | file: both meta.md files (status: new) | yes |
| 21 | Active: 3 — 1 to apply (Lendable), 2 new | file: three meta.md files; `userdata/outputs/applications.md` | yes |
| 21 | Saved today's brief | file: `userdata/outputs/daily-brief-2026-11-17.md` (matches turn 21 text) | yes |
| 21 | 9:00 auto-run isn't set up yet | user-visible context: turn 15 | yes |

### Findings

No findings.

### Verdict

**PASS**: every claim traces to a user answer, a file the run read or wrote, or a fetch. The 3 May 2027 date the user rejected comes from setup's documented 24-week rule applied to "about four months", so it is grounded, though it was the wrong call. The Plaid and Mercury location claim rests on ATS fetches whose role lists were saved to disk, but whose locations were not.

## Coherence

### Findings

- **turn 13:** "Want your daily brief to run automatically every morning?" — Rule 1: "your daily brief" arrives with no prior mention or explanation, so the user is asked to automate something they have not been told exists; it only gets explained when `/job-offer:today` renders one in turn 21.
- **turn 14 / turn 15:** "What time should your daily brief run? (e.g. 9am)" then "I'd set your brief to run every day at 9:00, but I can't schedule anything from this session, so that part isn't set up yet." — Rule 4: the assistant offers the automation and asks for a time, then says it cannot set it up, so the user answered two questions for nothing. The limitation is stated plainly, though, and turn 21 stays consistent with it ("since the 9:00 auto-run isn't set up yet").

### Verdict

**PASS** — The conversation holds together. Setup flows into search, then marking a role, then the dashboard and the brief, and each step builds on the last. The CV gap, the two undecided roles and the missing auto-run are carried forward consistently. The only bumps are one unintroduced term ("daily brief") and the offer-then-retract on scheduling, and both are explained right away, so neither would leave the user disoriented.

## Conformance

### Findings

- **turn 19:** "Marked Lendable — Senior Product Manager (US Cards) as one to apply for." — the status-change confirmation renders the application row (company, role, new status) with no JD URL inline, which breaks the [required] journey criterion "The chat rendering of the application row included the URL inline" and the spec's `- <Company> — <Role> — <status> — <url>` row contract; the `/today` brief in turn 21 ("**Lendable (US Cards)** — marked to apply") also gives no URL for this role.

### Verdict

**FAIL** — every other in-scope [required] criterion passed (the CV skip offered in the same message, distinct residence and geography asks, no timezone, LinkedIn, proof-point, moat or companies-of-interest asks in setup, a two-step automation prompt, companies of interest asked and written by `/job-search`, a table with no tiers or scores, Heads-up above count-only Pipeline state, an action on every heads-up, and state-aware closing nudges), but the one application row rendered in chat after the status change left out its JD URL, and under zero tolerance that single [required] miss fails the run.

_Note: judge calls disagreed — re-run manually if FAIL is unexpected._ (Confirmation re-run: PASS.)

## Tone

### Findings

- **turn 13:** "Say the word if those numbers look wrong.  Want your daily brief to run automatically every morning?" — Rule A (one ask per message): it asks the user to check the plan numbers and decide on auto-run in the same message. These are two unrelated decisions, and the user had to answer both together in turn 14.
- **turn 14:** "What time should your daily brief run? (e.g. 9am)" — Low-effort-first: the next turn shows the product can't schedule anything, so this question, and the yes/no before it, used up the user's turns on a setting that was never going to be applied.
- **turn 15:** "I'd set your brief to run every day at 9:00, but I can't schedule anything from this session, so that part isn't set up yet." — Simple language and internal detail leaking: it explains the failure in terms of the assistant's runtime ("this session"), which the user has no way to understand, right after asking for their preference.
- **turn 20:** "I can't keep the dashboard running from this session, so start it yourself from your job-search folder:" — Internal detail leaking, second time: "this session" again describes the assistant's runtime limits instead of what the user can do.
- **turn 20:** "`python3 <plugin-clone>/plugin/dashboard/serve.py --userdata \"$(pwd)/userdata\" --port 7890`" — Simple language: it gives a raw shell command with no explanation, including the plugin's install path, `$(pwd)` and command flags. That is systems vocabulary a PM running a job search has no reason to know.

### Verdict

**FAIL** — Most onboarding and search copy is plain and direct, but the runtime limitation shows up twice ("from this session" in turns 15 and 20, ending in a raw python command for the user to run), and the product asked two questions about automation it then said it couldn't set up. Those come from one systematic cause, and a real user would notice it, so it is a FAIL rather than a set of nitpicks.

## Verdict

    Lint:          PASS
    Groundedness:  PASS
    Coherence:     PASS
    Conformance:   FAIL (one-of-two)
    Tone:          FAIL

    Gate: Lint AND Groundedness AND Conformance

**Overall: FAIL (one-of-two)**
