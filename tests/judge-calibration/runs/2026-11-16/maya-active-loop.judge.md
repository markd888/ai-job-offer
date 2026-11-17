# Findings — maya-active-loop

**Run date:** 2026-11-16
**Snapshot:** maya-active

## Lint

No schema drift found.

No lint findings.

## Groundedness

### Evidence

| turn | claim | source | grounded |
|---|---|---|---|
| 1 | Found 8 roles worth a look (Monzo x4, Stripe x3, Bondora x1) | file: `companies/Monzo/senior-product-manager{,-web-growth,-eu,-subscriptions}/meta.md`, `companies/Stripe/{staff-product-manager-issuing,senior-staff-product-manager-risk,staff-product-manager-mobile}/meta.md`, `companies/Bondora/meta.md` (8 files filed this run) | yes |
| 1 | Monzo Senior PM, Web Growth — London, in band, link `.../monzoreferrals/jobs/8317736` | file: `companies/Monzo/senior-product-manager-web-growth/meta.md` (location, comp_band £100-125K, link); `research-brief.md` ("That's inside your band") | yes |
| 1 | Stripe Staff PM, Issuing — BNPL card overlap, London, link `.../stripe/jobs/8043083` | file: `companies/Stripe/staff-product-manager-issuing/meta.md`; `cv.md` (BNPL card at NorthLoop) | yes |
| 1 | Stripe Senior Staff PM, Risk — credit risk, link `.../stripe/jobs/8273741` | file: `companies/Stripe/senior-staff-product-manager-risk/meta.md` | yes |
| 1 | Monzo Senior PM (loyalty) — 0→1 build, link `.../8352202` | file: `companies/Monzo/senior-product-manager/meta.md` ("new loyalty proposition from discovery through launch") | yes |
| 1 | Monzo Senior PM, Subscriptions — [city] only, link `.../8180407` | file: `companies/Monzo/senior-product-manager-subscriptions/meta.md` (location: [city]) | yes |
| 1 | Monzo Senior PM, EU — EU launch, link `.../7622551` | file: `companies/Monzo/senior-product-manager-eu/meta.md` | yes |
| 1 | Stripe Staff PM, Mobile — founder adoption, EMEA remote, link `.../8140438` | file: `companies/Stripe/staff-product-manager-mobile/meta.md` | yes |
| 1 | Bondora Senior PM (Identity) — consumer lender, compliance, Tallinn, link `.../bondora/jobs/5013581101` | file: `companies/Bondora/meta.md` | yes |
| 1 | Lending role "you're already tracking" | file: `companies/Monzo/lead-pm-lending/meta.md` | yes |
| 1 | Monzo also hiring three Lead PMs (Growth 8317756, Monzo Mobile 8370847, Core Banking 8355492); first matches activation story, £120-140K | fetch: Monzo Greenhouse board pulled by the job-search recheck this run (evidenced by `outputs/seen-roles.jsonl` rows for 8317756 and 8370847 and the Monzo metas filed from it); the detail itself was not persisted to a file | yes |
| 1 | Plaid, Lendable and Klarna postings found have been taken down | fetch: job-search liveness check this run (Plaid/Lendable postings in `outputs/seen-roles.jsonl`); not persisted | yes |
| 1 | Mercury's openings are all US or Canada only | fetch: Mercury Greenhouse board this run (`outputs/seen-roles.jsonl` Mercury rows); not persisted | yes |
| 1 | Marshmallow and ClearScore have no product roles up | fetch: job-search recheck this run; not persisted | yes |
| 1 | These are from "your list of companies" | file: `profile.md` `## Companies of interest` (Plaid, Klarna, Lendable, Mercury, Monzo, Marshmallow, ClearScore) | yes |
| 1 | Stripe and Monzo far over the 150-person line in your search plan | file: `strategy.md` anti-goals (">150 ppl"); Monzo meta (~2500 ppl); Stripe metas ("large late-stage org") | yes |
| 2 | Monzo Web Growth marked to apply | file: `companies/Monzo/senior-product-manager-web-growth/meta.md` (status: to_apply, history line) | yes |
| 3 | Posting is web acquisition: landing pages on monzo.com, web signup funnel; wants an experimentation engine built | file: Web Growth `meta.md` + `research-brief.md` | yes |
| 3 | Lumio work: ~40 A/B tests; 4.1% → 6.8% conversion | file: `cv.md` | yes |
| 4 | Proof points: ~40-test programme, 4.1% → 6.8% on ~200K monthly signups, three NorthLoop price tests | file: `cv.md`, `cv-2026-11-17.md` | yes |
| 4 | Positioning angle: post-PMF growth needing careful instrumentation | file: `profile.md` `## Positioning` | yes |
| 4 | Dropped nothing; summary rewritten; Lumio bullets reordered; 3 bullets reworded; Skills line 1 reordered; keywords injected/not injected | file: `cv.md` vs `companies/Monzo/senior-product-manager-web-growth/cv-2026-11-17.md` | yes |
| 4 | PDF is one page, extracts cleanly; 10 of 18 keywords; 8 missing are the web-acquisition gaps | file: `ats-check-2026-11-17.md` (Keyword coverage 10/18; 8 missing, all web-acquisition terms) | yes |
| 4 | No phone number on your CV | file: `cv.md` (header has no phone) | yes |
| 5 | Added +44 7700 900123; passes; one page; email and phone extract; keywords unchanged at 10/18 | user: turn 5; file: `cv-2026-11-17.md` header, `ats-check-2026-11-17.md` (PASS) | yes |
| 5 | Master CV and profile don't have the number | file: `cv.md`, `profile.md` | yes |
| 6 | Web Growth is the only Monzo role you're going after; application not sent; no interview on record | file: Monzo metas (only Web Growth at to_apply; others new) | yes |
| 7 | Working from the Monzo CV drafted today | file: `cv-2026-11-17.md` | yes |
| 7 | Activation story: team-vs-solo split found in SQL | file: `stories/activation-funnel-uplift.md` | yes |
| 7 | Pricing story: the test framework as the thing built | file: `stories/payments-pricing-experiment.md` | yes |
| 7 | Onboarding pivot: telling a launch dip from a broken funnel | file: `stories/consumer-credit-onboarding-pivot.md` | yes |
| 7 | CV leads with the ~40-test programme; no saved story covers it | file: `cv-2026-11-17.md` summary; `stories/*.md` | yes |
| 7 | Pricing story has you as Senior PM, CV says Lead PM at NorthLoop | file: `stories/payments-pricing-experiment.md` ("as the Senior PM"); `cv-2026-11-17.md` | yes |
| 7 | Activation story has you newly promoted to Lead in late 2022; CV has Lead from 2020 | file: `stories/activation-funnel-uplift.md` ("By Q4 2022… I'd just been promoted to Lead PM"); `cv-2026-11-17.md` (2020–2023) | yes |
| 7 | Instalments launch you killed | file: `stories/instalments-failed-launch.md` | yes |
| 8 | Prep saved; same three stories; "an analyst's data rigour" tie | file: `interview-prep-2026-11-17.md`; `research-brief.md` | yes |
| 8 | Prep uses Lead PM at NorthLoop and Lumio; flags the ~40-test programme and that the onboarding pivot isn't on the CV | file: `interview-prep-2026-11-17.md`; `cv-2026-11-17.md` | yes |
| 8 | Salary: aim for £120K+, push back below £110K; five questions; three things to steer clear of | file: `interview-prep-2026-11-17.md` | yes |
| 9 | Dana Okafor is your only contact at Wagestream; she said the lending team is hiring | file: `people/dana-okafor.md` (log 2026-11-09); no other `people/` file mentions Wagestream | yes |
| 9 | Role is Senior PM, Consumer Lending; link `https://example.com/wagestream-jobs/senior-pm-consumer-lending` | file: `companies/Wagestream/meta.md` | yes |
| 9 | Worked together at Brightline on underwriting, bureau data and credit policy | file: `people/dana-okafor.md`; `cv.md` | yes |
| 9 | Led growth pricing on a BNPL card for thin-file customers at NorthLoop | file: `cv.md` | yes |
| 9 | Nine years; bureau integration cut thin-file decline rate 12% with defaults flat; three price tests lifted MRR 18% with no churn lift | file: `cv.md` | yes |
| 10 | Logged referral ask to Dana | file: `people/dana-okafor.md` log 2026-11-17; `journal.md` | yes |
| 10 | Follow-up if nothing by Tuesday 24 November | file: `people/dana-okafor.md` last_contact 2026-11-17 (a Tuesday) + 7 days = Tue 2026-11-24 | yes |

### Findings

No findings.

### Verdict

**PASS** — Every claim traces to a file the run wrote or read, the user's own turns, or the job-search posting fetches this run made. The Turn 1 notes on unfiled and taken-down roles were never written to a file but match the boards the recheck pulled.

## Coherence

### Findings

- **turn 1:** "Monzo is also hiring three Lead PMs that look like repeats of the Lending role you're already tracking. The first one is your activation story almost word for word, at £120-140K. I left them unfiled." — Rule 1: Growth, Mobile and Core Banking roles are called "repeats" of a Lending role with no explanation of why different teams count as the same role, and the best-fitting one is left unfiled in the same breath, so the user has to work out the logic alone.
- **turn 6 / turn 7:** "You haven't sent the application yet and there's no interview on record" (turn 6) then "You haven't sent the application yet, so I'm working from the Monzo CV drafted today" (turn 7) — Rule 3: the same caveat opens two adjacent turns. The second adds only a small point (which CV it's working from), and turn 8 comes back to it again with "Tell me once the application's sent".
- **turn 7 / turn 8:** turn 7 lists the CV mismatches before asking "Go with these three, or swap any?" (the ~40-test programme and the two title conflicts). Turn 8 then adds "Second, where the onboarding pivot happened, because the CV they'll read doesn't mention it." — Rule 1: a new problem with story 3 shows up only after the user approved the set based on turn 7's list, so they agreed without knowing about it.
- **turn 8:** the story table repeats turn 7's almost row for row ("Activation funnel uplift | the team-vs-solo split you found in SQL", "Consumer credit onboarding pivot | telling a launch dip from a broken funnel"), with only the last column renamed from "Why here" to "Monzo tie" — Rule 3: the user approved this exact table one turn earlier, so showing it again adds nothing.

### Verdict

**PASS**: Each turn picks up from the one before (file the role → mark it → tailor the CV → add the phone number → prep → outreach → log it), and the findings are small: one unexplained dedup call, one repeated caveat, one late-raised story issue and one repeated table. None of them would stop the user and make them reread.

## Conformance

### Findings

- **turn 8:** "Tell me once the application's sent and I'll record it." — The `/interview-prep` closing is the only next step offered and mentions neither interviewer-simulator (a natural rehearsal step for a hiring-manager round) nor `/job-offer:interview-analysis` (the skill's own documented end-of-run nudge), so the required criterion "`/interview-prep`'s closing nudge was context-aware (mentioned interviewer-simulator or interview-analysis appropriately)" is not met.

### Verdict

**FAIL** — Every other in-scope required criterion passed (no fenced dump in the search summary, one dashboard tip in turn 2, two `/apply` questions plus the phone ask, a bulleted recap naming the angle and proof points, a cover-letter nudge, three adapted stories, Dana found without asking, a grounded referral ask with a forwardable blurb, the ask logged once after "sent it on LinkedIn", and JD links in the turn 1 table; profile and strategy were not written, so criterion 4 was not exercised). The search summary has no tier-count buckets, but I did not count that as a finding because the job-search skill and TONE Rule D now ban tier labels in that summary, so the journey criterion is out of date. The one finding is the `/interview-prep` closing that skips both interview-stage skills, and under zero tolerance that makes the run a FAIL.

_Note: judge calls disagreed — re-run manually if FAIL is unexpected._ (Confirmation re-run: PASS.)

## Tone

### Findings

- **turn 4:** "Injected JD keywords: experimentation, conversion funnel, data analysis" — Simple language: "injected" is the skill's own internal operation word, and the "Did NOT inject (no supporting evidence)" line beside it carries on in the same voice, so the change summary reads like a build log, not a note to the user.
- **turn 5:** "Want a cover letter for Monzo too, or is the CV enough?" — Low-effort-first ("stop asking after value is delivered"): the CV is built and passes the check, and this adds an extra ask the user didn't need and then ignored.
- **turn 8:** "| 1 | Activation funnel uplift | the team-vs-solo split you found in SQL | \"an analyst's data rigour\" |" — Restatement: the turn repeats almost the same three-row story table the user approved one turn earlier, so it adds length without adding anything new.

### Verdict

**PASS** — The voice is plain, direct and in one register throughout. Each question is a single ask with a recommended default, and the outreach draft is free of superlatives and clichés. The three findings have different causes and are mild, so they don't add up to a pattern a user would notice.

## Verdict

    Lint:          PASS
    Groundedness:  PASS
    Coherence:     PASS
    Conformance:   FAIL (one-of-two)
    Tone:          PASS

    Gate: Lint AND Groundedness AND Conformance

**Overall: FAIL (one-of-two)**
