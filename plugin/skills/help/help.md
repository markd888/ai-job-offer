# job-offer

A Claude Code plugin for senior product leaders running a job search. Finds open roles, scores fit, tracks your pipeline, runs live interview practice, and gives you an honest career coach.

Pure markdown by default — optional browser dashboard and MCP integrations (Granola / Calendar / Gmail) on top.

## Who it's for

Senior PM, lead PM, or head of product running an active search. A different role? You can fork the architecture, but the defaults will need rework.

## The 5 phases

| # | Phase | Skill(s) |
|---|---|---|
| 1 | Setup | `/job-offer:setup` |
| 2 | Discover & score | `/job-offer:job-search` · `/job-offer:evaluate-position <url>` |
| 3 | Apply | `/job-offer:apply <Company>` |
| 4 | Interview | `/job-offer:story-builder` · `/job-offer:interview-prep <Company>` · `/job-offer:case-practice` · `job-offer:interviewer-simulator` · `/job-offer:interview-analysis` |
| 5 | Decide | `/job-offer:evaluate-offer` |

## Running alongside

| Skill | When |
|---|---|
| `/job-offer:today` | Every morning. |
| `job-offer:career-coach` | Anytime you're stuck or weighing something strategic. |
| `/job-offer:dashboard` | When you want a visual scan of the pipeline. |
| `/job-offer:integrations` | At setup, or after installing a new MCP server. |

## Skills (13)

Reference

| Skill | What it does | Use when |
|---|---|---|
| `/help` | This card: every skill + agent, grouped, with use-when triggers. Prints to chat and saves to `userdata/help.md`. | Any time you want the map. |

One-time setup

| Skill | What it does | Use when |
|---|---|---|
| `/setup` | Nine steps, writes profile + strategy + workspace CLAUDE.md. Drop a CV into `userdata/cv.md` first and it pre-fills facts, target titles, industries, and positioning. | First install, or you want to update positioning / salary band / target date. |

Daily and weekly

| Skill | What it does | Use when |
|---|---|---|
| `/today` | Two-phase daily brief: catches fresh facts from Calendar/Gmail/Granola, then prints top 3 actions + pipeline + heads-up. | Starting your day. |
| `/job-search` | Weekly sweep. Rechecks P0/P1 companies via ATS APIs, discovers new roles via scoped search. | Once a week, or any time you want fresh roles. |
| `/evaluate-position <url-or-paste>` | Scores one posting, writes the company folder + 200-word research brief. | A single role landed in your inbox. |
| `/apply <Company>` | Tailors your master CV for one role. Up to 5 clarifying questions, then a single-pass draft. | You've decided to apply. |
| `/dashboard` | Browser view of your pipeline; inline status changes + notes. | You want a visual scan instead of reading meta.md files. |
| `/integrations` | Wires in Granola / Calendar / Gmail MCPs if installed. | Setting up, or after installing a new MCP server. |

Interview cluster

| Skill | What it does | Use when |
|---|---|---|
| `/story-builder` | Maintains the universal STAR-story bank. | You remember a story worth capturing, or you want a `--gap-check` of missing senior-PM story types. |
| `/interview-prep <Company>` | Adapts 3–5 stories for a specific round. `--stage` shapes the prep. | You have an interview coming up. |
| `/case-practice [Company]` | MC rapid-recognition drill for product cases. Scores each pick by the failure mode it shows, tracks an 80% readiness gate, writes a session log. | You have a case / product-sense round coming up and want to drill recognition. |
| `/interview-analysis` | Debriefs a transcript (pasted, file, or auto-Granola). Quotes the transcript, flags what landed, names deltas vs prep. | A round just finished. |

Offer decision

| Skill | What it does | Use when |
|---|---|---|
| `/evaluate-offer` | Sense-check verdict, comp shape, archetype fit, anti-pattern scan, 3–5 negotiation moves. | You have an offer (or two) to weigh. |

## Agents (6)

Reviewer panel — invoke 1–4 in parallel on the same draft (case study, prep doc, outreach, take-home). Each returns the same four-section output: what works · what doesn't · weak spots · one rewrite suggestion.

| Agent | Lens | Use when |
|---|---|---|
| `job-offer:cpo-reviewer` | CPO: strategy clarity, scale-readiness, business-model fit, judgement under uncertainty. | You want the strategic read. |
| `job-offer:eng-manager-reviewer` | EM: technical feasibility, honest trade-offs, collaboration shape. | The draft makes technical claims. |
| `job-offer:design-manager-reviewer` | DM: UX judgement, discovery depth, craft, designer treatment. | The draft touches product craft. |
| `job-offer:interview-coach` | Narrative: clarity, pacing, voice authenticity, how you come across. | You want a "does this land?" read. |

Strategy and practice

| Agent | What it does | Use when |
|---|---|---|
| `job-offer:career-coach` | The honest coach. Offer evaluation, positioning sharpening, anti-goals, search-strategy resets, "something feels off" diagnostics. | You're stuck, weighing something strategic, or your search itself isn't working. |
| `job-offer:interviewer-simulator` | Live interview practice. Three modes: full mock round (6–10 questions + pushback), single-question deep-dive, pressure-test on one story's weak angle. | You want to rehearse, not review. |

## Recommended first week

| When | Do this |
|---|---|
| Day 1 | Drop a CV at `userdata/cv.md` if you have one, then `/setup`. Optionally `/integrations`. |
| Day 1–2 | `/job-search` to seed the pipeline, or `/evaluate-position <url>` for one-off roles. |
| Daily | `/today` every morning. |
| Anytime | `job-offer:career-coach` when you're stuck or weighing something. |
