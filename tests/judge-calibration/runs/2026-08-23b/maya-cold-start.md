# Transcript — maya-cold-start

**Date:** 2026-08-23
**Snapshot:** empty
**Max turns:** 30

---

## Turn 1 — USER

/job-offer:setup

## Turn 1 — ASSISTANT

Drop your CV into `userdata/` and I'll pull your details out of it — say "ready" when it's there. Or skip, and I'll just ask you instead.

## Turn 2 — USER

Don't have one handy, just ask me.

## Turn 2 — ASSISTANT

Right — nine quick steps, nothing locked in.

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

What roles are you after? Anything from Senior PM up to Head of Product — name as many as you'd take.

## Turn 6 — USER

Head of Product, Lead PM, Senior PM — in that order of preference.

## Turn 6 — ASSISTANT

What industries are you aiming at? Fintech, healthcare, climate, enterprise SaaS — whatever fits.

## Turn 7 — USER

Fintech and consumer credit.

## Turn 7 — ASSISTANT

Positioning next — who you are and what you're best at. Two ways to do it: write it now, or skip and I'll ask again once you've seen a few roles.

If you want to do it now, paste one to three sentences on what you're best at and I'll shape it into a paragraph. Otherwise say skip and we'll keep moving.

## Turn 8 — USER

Skip — I'll do it once I've seen a few roles.

## Turn 8 — ASSISTANT

Fine — I'll come back to it once you've seen a few roles.

Where are you looking? On-site in London, remote, both, or something else.

## Turn 9 — USER

Both — London hybrid or fully remote in EMEA.

## Turn 9 — ASSISTANT

Got it — both.

What salary band are you aiming for? Whatever shape works — "£90-110K" or "£120K base + equity" — or skip if you'd rather not put a number down yet.

## Turn 10 — USER

£90-110K if it's an IC role, £115-140K for leadership scope.

## Turn 10 — ASSISTANT

When do you want to have signed? Roughly is fine — a couple of months, six months, or an actual date if you've got one.

## Turn 11 — USER

September was the plan, but that's a week away now, so call it four months out — end of December, 2026-12-31.

## Turn 11 — ASSISTANT

Last one. Any red flags — roles you'd pass on however good the rest looks? Relocation, five days in the office, contract-only, that sort of thing. Or skip.

## Turn 12 — USER

No relocation outside EMEA, no sales-led enterprise B2B without a PLG motion, and nothing with more than eight direct reports — that's GM scope, not what I want.

## Turn 12 — ASSISTANT

That's everything. Your profile's saved.

The plan: signed by 31 December. That's about four and a half months, which works out at 5 applications and 5 outreach messages a week, and 3 live interview threads running at any time. Tell me if those numbers feel off and I'll redo them.

One thing before we're done — want your daily brief to run automatically each day, or would you rather kick it off yourself?

## Turn 13 — USER

Numbers are fine. I'll kick it off myself.

## Turn 13 — ASSISTANT

All yours to run, then.

Run `/job-offer:job-search` and I'll go find roles that match.

## Turn 14 — USER

/job-offer:job-search

## Turn 14 — ASSISTANT

Before I sweep — any companies you already have in mind? I'll seed the search with them. Or skip and I'll go wide.

## Turn 15 — USER

Plaid, Klarna, Lendable, Mercury.

## Turn 15 — ASSISTANT

Saved Plaid, Klarna, Lendable and Mercury to your profile, then swept.

Found 8 roles worth a look.

| Company | Role | Why it fits | Link |
|---|---|---|---|
| Lendable | Senior Product Manager (UK Cards) | consumer credit, in London | https://jobs.ashbyhq.com/lendable/636b90ec-028d-461a-b358-c7b871918dd8 |
| Plum | Lead Product Manager, Cash Products | lead level, consumer money app | https://apply.workable.com/j/273DD48807 |
| Paddle | Staff Product Manager (Checkout) | payments at scale, London | https://jobs.ashbyhq.com/paddle/cde17e70-5be2-4b2f-86c0-26591c168cec |
| Tide | Senior Product Manager, Ongoing Monitoring | UK fintech, fraud and risk | https://job-boards.greenhouse.io/tide/jobs/7863571003 |
| Plum | Senior Product Manager, Core Product | same company, one level down | https://apply.workable.com/j/E437B89970 |
| Tide | Lead Product Manager, Banking Payments | right level, wrong country | https://job-boards.greenhouse.io/tide/jobs/7783199003 |
| Raisin | Senior Product Manager, Investment & Pension Products | savings fintech, Berlin relocation | https://job-boards.eu.greenhouse.io/raisin/jobs/4928564101 |
| Moniepoint | Senior Product Manager | credit fintech, Spain-remote only | https://job-boards.eu.greenhouse.io/moniepoint/jobs/4823390101 |

Two pages wouldn't open, so I've filed them unscored rather than guess:

- Deel — Principal Product Manager, FinTech — https://jobs.ashbyhq.com/deel/99c6563a-a503-4f57-90cf-69122fb473c7
- Houseful — Senior Product Manager (Fintech / Proptech) — https://apply.workable.com/houseful/j/AF74EAA141

On your four: Lendable's cards role is the best thing in the sweep. Plaid is US-only at your level — its one London product role is a rung below your floor. Klarna has moved job boards and has nothing in product open at all. Mercury has a Head of Product for business lending, but every Mercury role is fenced to the US and Canada.

Two more scored well and I left them out because they're sales-led B2B with no self-serve motion, which is on your no-go list — Ebury (https://job-boards.eu.greenhouse.io/ebury/jobs/4951646101) and dLocal (https://jobs.lever.co/dlocal/7617a2ef-75a9-4dfb-8288-19da352217bf). Say the word and I'll file them.

Open `/job-offer:dashboard` to sort through these — or just tell me here which ones you want to go after.

## Turn 16 — USER

Lendable, then — mark Lendable to apply.

## Turn 16 — ASSISTANT

Marked Lendable — Senior Product Manager (UK Cards) as one to apply for.

You can do this in the dashboard too, if you'd rather click than type.

## Turn 17 — USER

/job-offer:dashboard

## Turn 17 — ASSISTANT

Opening your job-search dashboard at http://localhost:7890 — you'll see every role you're tracking in one view. Change a status, add a note, or archive a role inline. To add a new role, drop the link to me here and I'll score and file it.

Deel and Houseful are still sitting there without a score, since neither page would open for me — paste either link back and I'll have another go.

## Turn 18 — USER

/job-offer:today

## Turn 18 — ASSISTANT

Saved today's brief.

## Today

**Applications** — 0 of 5 out this week → Lendable is the one you've marked, tailor it with `/job-offer:apply Lendable`.

## Heads-up

**Deel and Houseful** — filed without a score because neither page would open → paste either link back and I'll have another go.

**Paddle, Plum and Tide** — three more roles scoring as high as Lendable, all still undecided → pick or drop them before Monday.

## Pipeline state

Active: 10 — 1 to apply (Lendable), 9 new.

This week: 0/5 applications, 0/5 outreach.

Full list in the dashboard — `/job-offer:dashboard`.

---

Nothing's logged from your side yet, so this brief is running on the pipeline alone — tell me what you get done each day and it'll sharpen up fast.

## Turn 19 — USER

Thanks, got it.

