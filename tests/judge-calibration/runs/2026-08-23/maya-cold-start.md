# Transcript — maya-cold-start

**Date:** 2026-08-23
**Snapshot:** empty
**Max turns:** 30

---

## Turn 1 — USER

/job-offer:setup

## Turn 1 — ASSISTANT

Drop your CV into `userdata/` and I'll pull your details out of it — say 'ready' when it's there. Or skip, and I'll just ask you instead.

## Turn 2 — USER

Don't have one handy, just ask me.

## Turn 2 — ASSISTANT

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

What roles are you targeting? Anything from Senior PM up to Head of Product — list as many as you'd take.

## Turn 6 — USER

Head of Product, Lead PM, Senior PM

## Turn 6 — ASSISTANT

What industries are you looking at? Fintech, healthcare, climate, enterprise SaaS — whatever fits.

## Turn 7 — USER

Fintech and consumer credit

## Turn 7 — ASSISTANT

Positioning next — who you are and what you're best at. Two ways to handle this:

A. Write it now — paste 1-3 sentences and I'll draft it with you.
B. Skip for now.

## Turn 8 — USER

Senior PM, nine years in consumer credit and growth-stage B2C SaaS. Right now I run the growth pricing surface at a Series B fintech doing a BNPL card for thin-file customers. Best at pricing and underwriting work where the numbers move.

## Turn 8 — ASSISTANT

Here's your positioning:

Senior PM, nine years in consumer credit and growth-stage B2C SaaS. Right now I own the growth pricing surface at a Series B fintech building a BNPL card for thin-file customers. Not a generalist growth PM — the work I'm best at is pricing and underwriting, where the numbers move.

Edit anything that doesn't sound like you — drafts are starting points, not finished copy.

## Turn 9 — USER

That works, keep it.

## Turn 9 — ASSISTANT

Where are you looking?

- On-site in London
- Remote
- Both
- Other — tell me the shape

## Turn 10 — USER

Both

## Turn 10 — ASSISTANT

What salary band are you aiming for? Whatever shape works — '£90-110K' or '$190-230K base + equity', or skip if you'd rather not anchor a number yet.

## Turn 11 — USER

£90-110K for IC, £115-140K if it's a leadership role

## Turn 11 — ASSISTANT

When do you want to have signed? Roughly is fine — a couple of months, six months, or an actual date if you have one.

## Turn 12 — USER

I'm aiming to land by end of September, so about four months out.

## Turn 12 — ASSISTANT

End of September is about five weeks out from here, not four months — those point at very different plans. Which one do you mean?

## Turn 13 — USER

End of September — the date's what matters, I was counting from the wrong month. Call it 2026-09-30.

## Turn 13 — ASSISTANT

Got it — 2026-09-30.

Last one. Any red flags — roles you'd skip on sight, whatever else is right about them? Relocation, five-day office, contract work, that kind of thing. Or skip.

## Turn 14 — USER

No relocation outside EMEA, no sales-led enterprise B2B without a PLG angle, and nothing with more than 8 direct reports — that's GM scope, not what I want.

## Turn 14 — ASSISTANT

Setup's done. I've got your profile, and a plan: land the offer by 2026-09-30, which works out at 12 applications and 10 outreach messages a week, with 5 live interview threads at any time. That's a fast cadence because the date's five weeks out — say the word if those numbers look wrong.

Want `/job-offer:today` to run automatically every day?

- Yes
- No, I'll run it manually

## Turn 15 — USER

No, I'll run it manually.

## Turn 15 — ASSISTANT

Setup done. Run `/job-offer:job-search` and I'll go find roles that match.

## Turn 16 — USER

/job-offer:job-search

## Turn 16 — ASSISTANT

Before I sweep — any companies you already have in mind? I'll seed the search with them. Or skip.

## Turn 17 — USER

Plaid, Klarna, Lendable, Mercury

## Turn 17 — ASSISTANT

Saved those four to your profile.

Found 5 roles worth a look.

| Company | Role | Why it fits | Link |
|---|---|---|---|
| Lendable | Senior Product Manager (UK Cards) | consumer credit, London, growth experiments | [open](https://jobs.ashbyhq.com/lendable/636b90ec-028d-461a-b358-c7b871918dd8) |
| Paddle | Staff Product Manager, Checkout | pricing surface at real scale | [open](https://jobs.ashbyhq.com/paddle/cde17e70-5be2-4b2f-86c0-26591c168cec) |
| Ebury | Senior Product Manager, Fraud Prevention | risk decisioning, London fintech | [open](https://job-boards.eu.greenhouse.io/ebury/jobs/4951646101) |
| Hopper | Principal Product Manager, Pricing | elasticity work, wrong industry | [open](https://jobs.ashbyhq.com/hopper/0482ca59-d815-42cb-850d-2d229cb9d9a0) |
| Zopa | Senior Product Manager, B2B | consumer lender, wrong city | [open](https://jobs.lever.co/zopa/9b8b5cdd-7805-4dd1-a9ca-8e4f1bd3ff4d) |

Two I skipped as likely repeats:

- Ebury — Senior Product Manager, Financial Crime (KYC/KYB) — https://job-boards.eu.greenhouse.io/ebury/jobs/4951647101 — same team and base title as the fraud one. Say "file Ebury KYC" if you want it tracked separately.
- Lendable — Senior Product Manager — https://jobs.ashbyhq.com/lendable/d676fe6a-8645-4180-8017-d53d83a4feb7 — same title as the cards role, but it's based in Virginia.

On the four you named: Lendable is the only one that delivered, and it delivered the best role of the sweep. Plaid's product openings are all San Francisco or New York, except a Product Manager, Europe in London that sits a level below what you're targeting — https://jobs.ashbyhq.com/plaid/29d1f5fc-d986-4a5d-9c42-0c05d9326f9d. Mercury's are US or Canada only, so they fail your no-relocation line. Klarna has nothing open in product at any level right now — I've set all four to be re-checked on future sweeps.

Open `/job-offer:dashboard` to sort through these — or just tell me here which ones you want to go after.

## Turn 18 — USER

Lendable, mark it to apply.

## Turn 18 — ASSISTANT

Marked Lendable — Senior Product Manager (UK Cards) as one to apply for.

You can do this in the dashboard too, if you'd rather click than type.

## Turn 19 — USER

/job-offer:dashboard

## Turn 19 — ASSISTANT

Opening your job-search dashboard at http://localhost:7890 — you'll see every role you're tracking in one view. Change a status, add a note, or archive a role inline. To add a new role, drop the link to me here and I'll score and file it.

Lendable's the only one you've committed to so far — run `/job-offer:apply Lendable` when you want it tailored.

## Turn 20 — USER

/job-offer:today

## Turn 20 — ASSISTANT

## Today

- Send 12 more applications this week (0/12).

## Heads-up

Nothing flagged today.

## Pipeline state

Active: 5 — 1 to apply (Lendable), 4 new.

This week: 0/12 applications, 0/10 outreach.

Full list in the dashboard — /job-offer:dashboard.

---

Saved to `userdata/outputs/daily-brief-2026-08-23.md`, and `applications.md` is now generated.

Four roles are still sitting in `new` — tell me which ones you want and I'll mark them, otherwise they just age.

## Turn 21 — USER

got it, thanks

