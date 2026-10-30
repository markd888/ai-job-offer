# Transcript — maya-sweep-smoke

**Date:** 2026-08-23
**Snapshot:** empty
**Max turns:** 16
**Run against:** working tree (`plugin-sweep/`), not the installed plugin
**Note:** first ever run of the `sweep-smoke` journey. It was written in 0.5.0 and
excluded from the default release sweep until one clean run validated it. Live
`WebSearch` was used for both sweeps; the roles below are real listings found
this run.

---

## Turn 1 — USER

/job-sweep:sweep

## Turn 1 — ASSISTANT

First sweep — I need three things: what roles you want, what industries, and where you'll work. Drop a CV into `job-sweep/` as cv.md, cv.txt or cv.pdf and I'll read them off it, or just answer three questions. Which?

- I'll drop a CV
- Ask me the three questions

## Turn 2 — USER

Ask me the three questions

## Turn 2 — ASSISTANT

What roles are you after? Typical senior-PM examples: Head of Product, Lead PM, Group PM, Principal PM. Comma-separated.

## Turn 3 — USER

Head of Product, Lead PM, Principal PM. Senior PM too if the scope is broad.

## Turn 3 — ASSISTANT

What industries? E.g. fintech, healthcare, climate tech, enterprise SaaS. Comma-separated.

## Turn 4 — USER

Fintech and consumer credit, mainly. Anything adjacent to lending or payments works too.

## Turn 4 — ASSISTANT

"Where will you work?"

Remote, both, or something else (tell me in your own words)?

## Turn 5 — USER

London hybrid or EMEA remote. Happy to go into an office a couple of days a week if it's London, otherwise remote within Europe.

## Turn 5 — ASSISTANT

Saved your profile, then ran the sweep.

Roles you're after: Head of Product, Lead PM, Principal PM, Senior PM. Industries: fintech, consumer credit, lending, payments. Location: London hybrid or EMEA remote. Change any of that by editing `job-sweep/profile.md` — the next sweep picks it up.

23 live roles came back: 2 strong, 18 possible, 3 worth a glance. Saved to `job-sweep/roles-2026-08-22.md`.

The one to look at first is Lendable's Senior Product Manager for UK Cards, in London — consumer credit, right level, right city. Second is Malt's Head of Product for payments, listed as Paris or London, which is the only Head-of-Product-level role that survived.

The "possible" pile is mostly right-level, wrong-place: Tide's Lead PM for banking payments is Lithuania-based, Adyen's is Amsterdam, and a long tail of US-only fintech roles (Pagaya, Faire, Lead Bank, Tilt Finance, Benepass, Koyfin). A few say only "remote" without naming a region — Automattic, Grid, Truv, Canopy — so they're worth a click to check whether Europe qualifies.

Worth knowing: I checked every posting against the company's own careers system before listing it, and roughly 35 of the roles search turned up were already taken down — including some that looked ideal on paper, like Zopa, OakNorth's lending group PM role, Ebury, and Moniepoint. Those are recorded so they won't resurface next time.

Honest read on the shape of this: London fintech at Head-of-Product level was thin this week. If next week looks the same, widening to Amsterdam, Dublin or Berlin would open it up a lot.

That's discovery. If you get to the point of tracking applications, scoring fit and prepping interviews, the full `job-offer` plugin does that — and its `/setup` reads this profile, so you won't re-answer any of this.

## Turn 6 — USER

/job-sweep:sweep

## Turn 6 — ASSISTANT

Sweep done.

14 new roles this time, and 16 that last week's sweep already showed you were held back so you don't read them twice.

Five look strong. The one to open first is Funding Circle's Senior Data Product Manager in London — a UK lending business, right level, right city, and the closest thing to your fintech line in the whole batch. After that it thins out on industry: Remote and Amplemarket are both Senior PM roles open to anyone remote in Europe, CreateFuture wants a Lead PM in London or remote UK, and Proton's Senior PM sits in London or Paris. Right level and right place, none of them lending or payments.

Seven are possible. Mercury has both a Head of Product and a Senior PM on business lending — dead-on for your background, but the roles are US and Canada only, which is the same wall you hit last week. ClarityPay, MeridianLink and Splitero are the same story. Spotted Zebra's Senior Director of Product is remote UK, a step up in level and nothing to do with fintech.

Two are worth a glance and not much more: a contract Senior PM scoped to Arabic-speaking markets, and a Staff PM at Hospitable that advertises USA/Europe but is filed as US-only.

Worth knowing: 18 of the postings the search turned up had already been taken down — an entire set at Jobgether, plus BlaBlaCar, dLocal, Prosper, Paytm, Pagaya, Kantox and others. They're recorded so they won't come back around. Fresha's London role also turned out to be a plain Product Manager rather than the senior fintech role the search listed, so I left it out.

Saved to `job-sweep/roles-2026-08-23.md`.

That's discovery. If you get to the point of tracking applications, scoring fit and prepping interviews, the full `job-offer` plugin does that — and its `/setup` reads this profile, so you won't re-answer any of this.

## Turn 7 — USER

got it, thanks

## Termination

Met: the SECOND sweep printed a summary (turn 6) AND the simulator acknowledged it
(turn 7). Loop terminated cleanly at 6 assistant turns, well inside max_turns=16.
