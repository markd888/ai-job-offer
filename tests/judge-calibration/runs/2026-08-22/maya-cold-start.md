# Transcript — maya-cold-start

**Date:** 2026-08-22
**Snapshot:** empty
**Max turns:** 30

---

## Turn 1 — USER

/job-offer:setup

## Turn 1 — ASSISTANT

I've created `userdata/` for you — drop your CV there as cv.md, cv.txt, or cv.pdf. Say 'ready' when it's in.

## Turn 2 — USER

I don't have one handy — carry on without it.

## Turn 2 — ASSISTANT

No CV — we'll do it the long way then. Same questions, you just type more.

OK, let's get you set up — nine quick steps, none of it locked in.

What's your name?

## Turn 3 — USER

Maya Patel

## Turn 3 — ASSISTANT

Where are you based? City + country works (e.g. London, UK).

## Turn 4 — USER

London, UK

## Turn 4 — ASSISTANT

What's your email?

## Turn 5 — USER

maya.patel@example.com

## Turn 5 — ASSISTANT

LinkedIn URL? I'll use it to pre-fill outreach drafts later. Or skip.

## Turn 6 — USER

skip

## Turn 6 — ASSISTANT

I'm seeing your timezone as `Europe/London` — that right? Override if not.

## Turn 7 — USER

Yes, that's right.

## Turn 7 — ASSISTANT

What roles are you targeting? Typical senior-PM examples: Director of Product, Principal PM, Group PM, Staff PM. List as many as you'd take, comma-separated.

## Turn 8 — USER

Head of Product, Lead PM, Senior PM, Principal PM

## Turn 8 — ASSISTANT

What industries are you looking at? E.g. healthcare, climate tech, education, enterprise SaaS. Comma-separated.

## Turn 9 — USER

Fintech, consumer credit, B2C SaaS

## Turn 9 — ASSISTANT

Positioning next — who you are and what you're best at. Two ways to handle this:

A. Write it now — paste 1-3 sentences about yourself and I'll draft it with you.
B. Skip for now.

## Turn 10 — USER

A. Senior PM, nine years in consumer credit and growth-stage B2C SaaS. Currently run the growth pricing surface at a Series B fintech doing a BNPL card for thin-file customers, about £60M ARR. Best at pricing and monetisation work and 0-to-1 underwriting/risk integrations — I ran a pricing experiment programme that lifted MRR 18% in a quarter with no churn hit, and shipped a new credit bureau integration that cut decline rate 12% on thin-file applicants without raising defaults.

## Turn 10 — ASSISTANT

Here's a first pass at your positioning, drafted from what you just said:

Nine years in consumer credit and growth-stage B2C SaaS. Currently own the growth pricing surface at a Series B fintech — a BNPL card for thin-file customers, about £60M ARR. The strongest work is pricing and monetisation, plus 0-to-1 underwriting and risk integrations.

Not "growth PM who runs experiments" — ran a pricing experiment programme that lifted MRR 18% in a quarter with no churn hit, and shipped a new credit bureau integration that cut decline rate 12% on thin-file applicants without raising defaults.

Edit anything that doesn't sound like you — drafts are starting points, not finished copy.

Now the proof points. Give me 3-5 wins, numbered — the two above already count, so 1-3 more. A line each is enough: what you did, what happened, and where.

## Turn 11 — USER

3. Rebuilt the dunning and failed-payment flow at the same fintech, recovered about 30% of involuntary churn. 4. Took the BNPL card's rewards tier from concept to launch — 0 to 1, first product I owned end to end there. 5. Before this, ran the subscription pricing migration at a B2C SaaS, moved 200K users onto new plans with under 2% voluntary cancellation.

## Turn 11 — ASSISTANT

Here's the proof points draft:

- **Pricing experiments:** Ran a pricing experiment programme at the Series B fintech → lifted MRR 18% in a quarter with no churn hit. (Senior PM)
- **Credit bureau integration:** Shipped a new bureau integration for thin-file applicants → cut decline rate 12% without raising defaults. (Senior PM)
- **Dunning and failed payments:** Rebuilt the flow at the same fintech → recovered about 30% of involuntary churn. (Senior PM)
- **BNPL rewards tier:** Took it from concept to launch → 0 to 1, the first product owned end to end there. (Senior PM)
- **Subscription pricing migration:** Moved 200K users onto new plans at a B2C SaaS → under 2% voluntary cancellation.

I left the employers unnamed since you didn't name them — add them if you want them on the page. Edit anything that doesn't sound like you — drafts are starting points, not finished copy.

Last bit of positioning: one sentence on what's the rare thing you bring — the combination other people applying for these roles won't have.

## Turn 12 — USER

Pricing and monetisation depth plus credit risk and underwriting — most growth PMs can run a pricing test but can't reason about decline rates and default risk, and most risk PMs can't move revenue.

## Turn 12 — ASSISTANT

Here's the moat:

Pricing and monetisation on one side, credit risk and underwriting on the other — most growth PMs can run a pricing test but can't reason about decline rates and default risk, and most risk PMs can't move revenue.

Edit anything that doesn't sound like you — drafts are starting points, not finished copy.

Where are you looking?

- On-site in London
- Remote
- Both
- Other (tell me the shape)

## Turn 13 — USER

Both

## Turn 13 — ASSISTANT

What salary band are you aiming for? Whatever shape works — '£90-110K' or '$190-230K base + equity', or skip if you'd rather not anchor a number yet.

## Turn 14 — USER

£90-110K if it's an IC role, £115-140K for anything with leadership scope.

## Turn 14 — ASSISTANT

When do you want the offer signed? A rough window is fine — it sets how hard the weekly targets push.

- Under 2 months
- 2-4 months
- 4+ months
- I have an exact date
- Not sure yet

## Turn 15 — USER

2-4 months

## Turn 15 — ASSISTANT

Last one. Any red flags — roles you'd skip on sight, whatever else is right about them?

- No companies under 50 people
- No five-day in-office
- No relocation
- No contract or interim roles
- No agency or consultancy
- No roles without a product team already in place

Pick all that apply, add your own, or skip.

## Turn 16 — USER

No relocation, no five-day in-office, no contract or interim. Also no sales-led enterprise B2B without a PLG angle, and nothing with more than 8 direct reports.

## Turn 16 — ASSISTANT

Profile, strategy, and journal are written.

One thing before I finish: `CLAUDE.md` exists at workspace root and was not generated by job-offer. Overwrite (y/N)?

## Turn 17 — USER

no, leave it

## Turn 17 — ASSISTANT

You're set up. Wrote:

- `userdata/profile.md` — identity, target roles, positioning, salary, red flags
- `userdata/strategy.md` — headline goal + target offer date 2026-11-14 (from your "2-4 months" answer) + derived weekly targets (8 applications/wk, 8 outreach/wk, 4 active interview threads floor). Edit these if they feel off — or ask `job-offer:career-coach` to help you set anti-goals and checkpoints.
- `userdata/journal.md` — empty, append daily notes here

I left your `CLAUDE.md` alone as you asked. That means your positioning won't load automatically into every session — you can paste it in yourself later if you want that.

Want to sharpen your positioning before we wrap? I can pull in the `job-offer:career-coach` agent — quick 5-min back-and-forth, it'll suggest a tighter version. Or skip and edit `profile.md` whenever.

## Turn 18 — USER

/job-offer:job-search

## Turn 18 — ASSISTANT

Pipeline's empty — nothing to recheck, so this is a pure discovery sweep.

Before I sweep — any companies you already have in mind? I'll seed the search with them. Or skip.

## Turn 19 — USER

Plaid, Klarna, Lendable, Mercury

## Turn 19 — ASSISTANT

Saved to `profile.md` under a new "Companies of interest" section — I'll seed the sweep with Plaid, Klarna, Lendable, Mercury.

Nothing in `userdata/companies/` yet and no seen-ledger, so there's no exclusion set and no recheck watchlist — this run is discovery only. Say go and I'll start the sweep: site-scoped searches across the ATS boards for Head of Product / Lead PM / Senior PM / Principal PM in fintech, consumer credit and B2C SaaS around London and EMEA remote, plus targeted passes on those four companies. Everything that survives gets scored against your tier rubric and filed with status `new`.

## Turn 20 — USER

go

## Turn 20 — ASSISTANT

Sweep's done. Everything below I confirmed live today against each company's own job board.

Filed 11 new roles — 8 tier-1, 3 tier-2, all sitting as new.

Tier-1:
- Zilch — Director of Product — https://jobs.ashbyhq.com/zilch/5b436621-870c-42eb-960e-3f8821b86c7b
- Lendable — Senior Product Manager (UK Cards) — https://jobs.ashbyhq.com/lendable/636b90ec-028d-461a-b358-c7b871918dd8
- APEXX Global — Head of Product — https://jobs.ashbyhq.com/apexx/17be72a3-184d-4abc-aa2f-3bb717719249
- Monzo — Senior Product Manager, EU — https://job-boards.greenhouse.io/monzo/jobs/7622551
- GoCardless — Senior Product Manager — https://job-boards.greenhouse.io/gocardless/jobs/8064518
- Checkatrade — Principal Product Manager, Matching & Monetisation — https://jobs.ashbyhq.com/checkatrade/e9e67918-8652-41b1-ad28-d7e326e52ee0
- Tide — Senior Product Manager, Ongoing Monitoring — https://job-boards.greenhouse.io/tide/jobs/7863571003
- Deliveroo — Group Product Manager, Regulatory Finance — https://jobs.ashbyhq.com/deliveroo/05f9d362-1718-4109-80cc-eff5eea038f8

Tier-2:
- Eucalyptus — Senior Product Manager, Growth (Berlin or London) — https://job-boards.greenhouse.io/eucalyptus/jobs/4709381005
- APEXX Global — Senior Product Manager, Self-Service & Onboarding — https://jobs.ashbyhq.com/apexx/468057df-6924-4fe8-801e-5974054884ea
- Checkatrade — Senior Product Manager — https://jobs.ashbyhq.com/checkatrade/fdc126ab-4568-420a-850b-6ff902b460ec

Zilch is the standout and the only 15 out of 15 on the page — a BNPL card business, five squads, P&L ownership, five direct reports, London hybrid. It's the one role here that hits both halves of your moat at leadership level.

Skipped as a likely repeat: Eucalyptus — Senior Product Manager, Growth (Germany), London, UK — https://job-boards.greenhouse.io/eucalyptus/jobs/4710123005. Shares a base title with the one I filed. Say "file Eucalyptus" if it's genuinely a second role.

On your four companies. Lendable came through with the cards role above. Plaid's only open product job is a Product Manager seat in San Francisco pitched at someone earlier in their career — wrong level, wrong continent. Klarna's posting had been taken down and their old job board doesn't answer at all any more. Mercury has a Head of Product for Business Lending that reads well until the location line: San Francisco, New York, Portland, or remote inside the US and Canada only.

One near-miss I left out: Zopa's Senior Product Manager for B2B is real and open, but it's Manchester hybrid, so it means moving. Say the word and I'll file it anyway.

Worth knowing how much attrition there was — 22 of the 30 postings the first search pass turned up had already been pulled by the time I checked them. That's why I went at the job boards directly for the second pass.

Open the dashboard to sort through these — or tell me here which ones you want to go after, and which to drop.

## Turn 21 — USER

mark Zilch to apply

## Turn 21 — ASSISTANT

Zilch — Director of Product is now `to_apply`.

Tip: you can also click the company row in the dashboard and add this note directly — same data underneath.

Next step when you're ready: `/job-offer:apply Zilch` — but it reads `userdata/cv.md` as the master CV, and you skipped the CV at setup. Drop your CV in there first, or tell me and I'll build the master from your profile.

## Turn 22 — USER

/job-offer:dashboard

## Turn 22 — ASSISTANT

Opening your job-search dashboard at http://localhost:7890 — you'll see every role you're tracking in one view. Change a status, add a note, or archive a role inline. To add a new role, drop the link to me here and I'll score and file it.

Zilch is sitting in `to_apply` with no CV drafted yet — `/job-offer:apply Zilch` is the next move once you've got a master CV in `userdata/cv.md`.

## Turn 23 — USER

/job-offer:today

## Turn 23 — ASSISTANT

Saved to `userdata/outputs/daily-brief-2026-08-22.md`.

## Top 3 actions today

1. **Applications** — send 8 more this week (0/8).

## Heads-up

- **Zilch** — the only role you've picked to chase, and there's no master CV saved yet to build the application from.
- **Your plan** — no review points set between now and the 2026-11-14 target, so nothing will tell you if the search is drifting.

## Pipeline state

| Status | Company | Tier | Position | Last activity |
|---|---|---|---|---|
| To apply | Zilch | Tier 1 | Director of Product | today |
| New | APEXX Global | Tier 1 | Head of Product | today |
| New | Lendable | Tier 1 | Senior Product Manager (UK Cards) | today |
| New | Deliveroo | Tier 1 | Group Product Manager, Regulatory Finance | today |
| New | GoCardless | Tier 1 | Senior Product Manager | today |
| New | Monzo | Tier 1 | Senior Product Manager, EU | today |
| New | Tide | Tier 1 | Senior Product Manager, Ongoing Monitoring | today |
| New | Checkatrade | Tier 1 | Principal Product Manager, Matching & Monetisation | today |
| New | Eucalyptus | Tier 2 | Senior Product Manager - Growth (Berlin, Germany OR London, UK) | today |
| New | APEXX Global | Tier 2 | Senior Product Manager - Self-Service & Onboarding | today |
| New | Checkatrade | Tier 2 | Senior Product Manager | today |

Nothing goes out this week without a master CV — say the word and I'll build one from your profile.

## Turn 24 — USER

got it, thanks

