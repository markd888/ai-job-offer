# Transcript — maya-cold-start

**Date:** 2026-11-16
**Snapshot:** empty
**Max turns:** 30

---

## Turn 1 — USER

/job-offer:setup

## Turn 1 — ASSISTANT

Drop your CV into `userdata/` and I'll pull your details out of it — say 'ready' when it's there. Or skip, and I'll just ask you instead.

## Turn 2 — USER

Don't have one handy. Skip, just ask me.

## Turn 2 — ASSISTANT

OK, let's get you set up — nine quick steps, none of it locked in.

What's your name?

## Turn 3 — USER

Maya Patel

## Turn 3 — ASSISTANT

Where are you based? City and country is enough, e.g. London, UK.

## Turn 4 — USER

London, UK

## Turn 4 — ASSISTANT

What's your email? It goes on your tailored CVs and follow-up drafts.

## Turn 5 — USER

maya.patel@example.com

## Turn 5 — ASSISTANT

What roles are you going for? Anything from Senior PM up to Head of Product works. List every one you'd take.

## Turn 6 — USER

Head of Product, Lead PM, Senior PM

## Turn 6 — ASSISTANT

Which industries are you looking at? Fintech, healthcare, climate, enterprise SaaS, whatever fits.

## Turn 7 — USER

Fintech and consumer credit.

## Turn 7 — ASSISTANT

Positioning next: who you are and what you're best at. You've got two options:

- **Write it now.** Give me one to three sentences about yourself and I'll shape them into a paragraph.
- **Skip for now.** You can come back to it once you've seen a few roles.

Which one?

## Turn 8 — USER

Write it now. Senior PM, nine years across consumer credit and growth-stage B2C SaaS. Currently own growth pricing at a Series B BNPL fintech for thin-file customers — ran a pricing-experiment programme that lifted MRR 18% in Q3 with no churn hit, and shipped a 0→1 credit bureau integration that cut thin-file declines 12% without raising defaults.

## Turn 8 — ASSISTANT

Here's a first pass at your positioning:

> Senior PM, nine years across consumer credit and growth-stage B2C SaaS. I own growth pricing at a Series B BNPL fintech serving thin-file customers. Ran a pricing-experiment programme that lifted MRR 18% in Q3 with no churn hit. Shipped a 0→1 credit bureau integration that cut thin-file declines 12% without raising defaults.

Edit anything that doesn't sound like you — drafts are starting points, not finished copy.

## Turn 9 — USER

Looks fine. Keep it as is.

## Turn 9 — ASSISTANT

Where are you looking?

- **On-site in London**
- **Remote**
- **Both**
- **Other** — tell me what you have in mind

## Turn 10 — USER

Both. London hybrid, or remote within EMEA.

## Turn 10 — ASSISTANT

What salary band are you aiming for? Any shape works, like "£110-130K base" or "£120K + equity". Or skip if you'd rather not anchor on a number yet.

## Turn 11 — USER

£90-110K for IC roles, £115-140K for leadership scope.

## Turn 11 — ASSISTANT

When do you want to have signed? Roughly is fine: a couple of months, six months, or an actual date if you have one.

## Turn 12 — USER

About four months.

## Turn 12 — ASSISTANT

Last one. Any red flags, meaning roles you'd skip on sight however good the rest looks? Things like relocation, five days a week in the office, or contract work. Or skip.

## Turn 13 — USER

Relocation outside EMEA, sales-led enterprise B2B with no PLG signal, and anything with more than 8 direct reports.

## Turn 13 — ASSISTANT

You're set up. I've got your profile, and a plan: land the offer by 3 May 2027, which works out at 5 applications and 5 outreach messages a week, with 3 live interview threads at any time. Say the word if those numbers look wrong.

Want your daily brief to run automatically every morning?

- **Yes**
- **No, I'll run it myself**

## Turn 14 — USER

Yes. Also, four months from now is mid-March, not May — make the target March.

## Turn 14 — ASSISTANT

You're right, my mistake. I've moved your target date to 16 March 2027. The weekly numbers stay the same: 5 applications and 5 outreach messages a week, with 3 live interview threads at any time.

What time should your daily brief run? (e.g. 9am)

## Turn 15 — USER

9am

## Turn 15 — ASSISTANT

I'd set your brief to run every day at 9:00, but I can't schedule anything from this session, so that part isn't set up yet.

Setup done. Run `/job-offer:job-search` and I'll go find roles that match.

## Turn 16 — USER

/job-offer:job-search

## Turn 16 — ASSISTANT

Before I search, are there any companies you already have your eye on? I'll check them first alongside everything else. Or skip.

## Turn 17 — USER

Plaid, Klarna, Lendable, Mercury.

## Turn 17 — ASSISTANT

Saved those four to your profile as companies you're watching.

Found 3 roles worth a look.

| Company | Role | Why it fits | Link |
|---|---|---|---|
| Lendable | Senior Product Manager (US Cards) | card pricing and credit lines, London | https://jobs.ashbyhq.com/lendable/5e6c5b4d-11d8-4773-bc71-0b0a0b974ff9 |
| Lendable | Senior Product Manager (CRM & Growth) | right lender, lifecycle not pricing | https://jobs.ashbyhq.com/lendable/58381ca8-8588-4c33-af30-3fb4c54a89fd |
| Affirm | Senior Product Manager | BNPL repayments, remote UK, well paid | https://job-boards.greenhouse.io/affirm/jobs/8020318003 |

On the others you named: every product role open at Plaid and Mercury is in the US, which breaks your no-relocation-outside-EMEA rule. Klarna has no product manager roles open right now. All three roles above are senior individual-contributor jobs. Nothing live at Head of Product or Lead level matched this time.

Open `/job-offer:dashboard` to sort through your new roles, or just tell me here which ones you want to go after.

## Turn 18 — USER

mark Lendable to apply

## Turn 18 — ASSISTANT

You've got two Lendable roles in there. Which one should I mark?

- **Senior Product Manager (US Cards)**
- **Senior Product Manager (CRM & Growth)**
- **Both**

## Turn 19 — USER

US Cards.

## Turn 19 — ASSISTANT

Marked Lendable — Senior Product Manager (US Cards) as one to apply for. The CRM & Growth role stays where it was.

You can do this in the dashboard too, if you'd rather click than type.

Next is a CV tailored to this role. You'll need your own CV in first, then run `/job-offer:apply Lendable`.

## Turn 20 — USER

/job-offer:dashboard

## Turn 20 — ASSISTANT

I can't keep the dashboard running from this session, so start it yourself from your job-search folder:

`python3 <plugin-clone>/plugin/dashboard/serve.py --userdata "$(pwd)/userdata" --port 7890`

It opens at http://localhost:7890 with every role you're tracking in one view. Change a status, add a note, or archive a role inline. To add a new role, drop the link to me here and I'll score and file it.

Affirm and Lendable's CRM & Growth role are still waiting on a yes or no from you, so that's a quick first job once it's open.

## Turn 21 — USER

/job-offer:today

## Turn 21 — ASSISTANT

## Today

- Send 5 more applications this week (0/5) — Lendable's US Cards role is first in line.

## Heads-up

- **Lendable (US Cards)** — marked to apply, but there's no CV of yours in the folder yet → drop it into `userdata/`, then run `/job-offer:apply Lendable`.
- **Affirm and Lendable (CRM & Growth)** — still waiting on a yes or no → tell me "to apply" or "not interested" for each, here or in the dashboard.

## Pipeline state

Active: 3 — 1 to apply (Lendable), 2 new.

This week: 0/5 applications, 0/5 outreach.

Saved today's brief. Run `/job-offer:today` again tomorrow morning, since the 9:00 auto-run isn't set up yet.

## Turn 22 — USER

got it, thanks.

