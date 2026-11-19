# ai-job-offer

A Claude Code plugin that runs a senior-PM job search with you — from finding roles to signing the offer. It scores fit, tailors your CV, keeps the pipeline moving, preps you for interviews and tells you honestly when the search isn't working. Everything lives in markdown files on your machine.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/how-it-works-dark.svg">
  <img alt="How job-offer works: five phases — 1 Set up (/setup), 2 Find & score (/job-search, /evaluate-position), 3 Apply (/apply, /ats-check, /cover-letter, /sent), 4 Interview (/interview-prep, /case-practice, simulator, /interview-analysis), 5 Decide (/evaluate-offer, /wrap-up) — with /today, /follow-up, /outreach, /dashboard and career-coach running alongside every day." src="docs/how-it-works-light.svg">
</picture>

Built for senior PMs, lead PMs and heads of product. Based on [pm-job-search](https://github.com/archugunov/pm-job-search) by [@archugunov](https://github.com/archugunov) — see [what this version adds](#what-this-version-adds).

**Contents:** [Quick start](#quick-start) · [How it works](#how-it-works) · [Where your data lives](#where-your-data-lives) · [Skills](#skills) · [Agents](#agents) · [Dashboard](#dashboard) · [Integrations](#integrations) · [Requirements](#requirements) · [job-sweep](#job-sweep--just-the-weekly-role-list) · [Privacy](#privacy)

## Quick start

**1. Install** — inside Claude Code:

```sh
/plugin marketplace add https://github.com/markd888/ai-job-offer.git
/plugin install job-offer@job-offer
```

**2. Set up** — in the folder you'll run your search from. Put your CV at `userdata/cv.md` first and most answers get pre-filled.

```sh
/job-offer:setup        # 10–15 min: target role, salary, hard filters, timeline
```

**3. Run it daily**

```sh
/job-offer:today        # every morning: what changed, top 3 actions, follow-ups due
/job-offer:help         # any time: a one-page map of every skill and agent
```

The pipeline, scoring, prep and coaching need nothing but Claude Code. CV PDFs and the ATS check need a small Python toolchain — see [Requirements](#requirements).

## How it works

The picture at the top is the whole plugin: five phases, the commands for each, and what runs alongside. Below — what happens to one application, and to your day.

### One application, start to finish

Each role is a folder with a `meta.md`; its `status` moves through the stages below. The skills on the arrows are what moves it — status changes only after you confirm.

### Your daily loop

`/today` starts by asking what changed — from your calendar, inbox and meeting notes if they're connected, and from you. Only what you confirm is written down; the brief is built from that.

On the first run of each week it offers a five-minute reflection; when several weeks of numbers say the search itself isn't working, it hands you to `career-coach`.

### Ground rules every skill follows

- **No invented facts.** Every claim in a CV, letter or message traces to your master CV, your profile or your own answers. `/apply` and `/cover-letter` also tell you what they chose *not* to claim.
- **Drafts only.** Nothing is sent on your behalf — follow-ups, referral asks, withdrawals are drafts you send yourself.
- **You confirm changes.** A status, a date or a new fact lands in your files after your yes.
- **Honest over encouraging.** Eight weeks and one live thread? `career-coach` says the search needs a rethink, not more of the same cadence.

## Where your data lives

Everything is plain markdown under `userdata/` in your search folder — gitignored, readable, editable by hand.

```text
userdata/
├── cv.md                    master CV — the only source of facts for every CV and letter
├── profile.md               who you are, positioning, tone, what not to claim
├── strategy.md              targets, weekly cadence, anti-goals, search_state
├── journal.md               dated log of everything you confirmed
├── stories/                 STAR-story bank, each story with 3–5 angles
├── people/                  referrers, recruiters, hiring managers + a log of every ask
├── companies/<Company>/[<role>/]
│   ├── meta.md              status, tier, dates, channel — the pipeline state
│   ├── research-brief.md    200-word brief from /evaluate-position
│   ├── cv-<date>.md + .pdf  tailored CV, ats-check-<date>.md, cover-<date>.md
│   ├── submitted-<date>/    frozen copy of exactly what you sent
│   ├── interview-prep-*.md  interview-debrief-*.md  notes.md
└── outputs/                 daily briefs, applications index, retrospective
```

Want to see a working install first? Two fictional personas live in [`userdata/examples/`](userdata/examples/): **maya** (senior PM in London, fintech — full install) and **diego** (VP Product in Mexico City going after remote US roles — skeletal).

## Skills

All commands are prefixed `/job-offer:` — e.g. `/job-offer:apply Acme`.

| Phase | Skill | What it does |
|---|---|---|
| Start | `/help` | One-page map of every skill and agent; also saved to `userdata/help.md`. |
| | `/setup` | Nine steps → profile, strategy, workspace `CLAUDE.md`. Pre-fills from your CV; re-runnable. |
| | `/integrations` | Finds Granola / Calendar / Gmail MCPs and wires the ones you have. Optional. |
| Daily | `/today` | Confirms what changed, then the brief: top 3 actions, pipeline, follow-ups due, heads-up. |
| | `/dashboard` | The pipeline in a browser at `localhost:7890`; change status and add notes inline. |
| Find | `/job-search` | Weekly sweep: rechecks your P0/P1 companies via Ashby / Greenhouse / Lever, finds new roles, scores and files them. |
| | `/evaluate-position <url>` | Scores one posting against your rubric — hard filters, anti-goals, liveness — and writes the company folder. |
| Apply | `/apply <Company>` | Tailors your master CV for one role: up to five questions, one draft, a one-page PDF. |
| | `/ats-check <Company>` | Reads the PDF the way an applicant tracking system does: pages, contacts, glyphs, section order, keyword coverage. Runs after every `/apply`. |
| | `/cover-letter <Company>` | 150–250 words answering the posting's top 2–3 needs with one proof each; PDF in the CV's look. |
| | `/sent <Company>` | After your yes: status, date, channel, who referred you, and a frozen copy of what you sent. Starts the follow-up clock. |
| | `/follow-up [Company]` | Applications quiet 10+ days → a short nudge (max two), or a thank-you after a round. Records replies. |
| | `/outreach <person or Company>` | People as records in `userdata/people/`; drafts referral asks, intros and thank-yous, logs each once sent. |
| Interview | `/story-builder` | Your STAR-story bank; `--gap-check` finds the senior-PM story types you're missing. |
| | `/interview-prep <Company>` | Adapts 3–5 stories to the round; `--stage` from recruiter screen to final loop or take-home. |
| | `/case-practice [Company]` | Rapid-recognition case drill, scored by failure mode against an 80% readiness gate. |
| | `/interview-analysis` | Debrief from a transcript (pasted, file or Granola): what landed, what didn't, quoted. |
| Decide | `/evaluate-offer` | Verdict on one offer or two: comp shape, archetype fit, anti-patterns, 3–5 negotiation moves. |
| | `/wrap-up` | After you accept: withdrawals, thank-yous, a retro from your own numbers, then quiet mode. `--reopen` starts again. |

Full descriptions: [`plugin/README.md`](plugin/README.md).

## Agents

Ask for them by name or in plain words ("review this case study as a CPO", "I'm stuck").

| Agent | Use it for |
|---|---|
| `cpo-reviewer` | Strategy, scale, business model, judgement under uncertainty |
| `eng-manager-reviewer` | Technical feasibility, trade-offs, working with engineers |
| `design-manager-reviewer` | UX judgement, craft, discovery rigour |
| `interview-coach` | Narrative, clarity, how you come across |
| `career-coach` | Positioning, outreach, anti-goals, cadence, offers, search resets — with an honest-calibration mode |
| `interviewer-simulator` | A full mock round, one question with escalating follow-ups, or a pressure test of your weakest story |

The four reviewers share one output shape — what works, what doesn't, where it sounds weak, one rewrite — so you can run two to four on the same draft and read them as a panel. `--save <Company>` writes the review into the company folder.

## Dashboard

A browser view over the same markdown files — for scanning the pipeline, not for creating anything.

![job-offer dashboard on demo data: interview cards with an editable next step, today's focus, the pipeline by stage with tier filter and search, the funnel, this week's targets, coming-up events, light and dark themes](docs/dashboard-demo.gif)

```sh
/job-offer:dashboard    # http://localhost:7890 — reused if it's already running; ctrl-C to stop
```

Interview cards on top, today's focus and the pipeline by stage below, and on the right the funnel (also split by channel once `/sent` has recorded them), this week's targets and what's coming up. Click a role for its research, notes, prep and debriefs. It writes back two things only — status changes and notes. A read-only copy for your phone can run on Cloudflare Workers behind Cloudflare Access: [`plugin/dashboard/README.md`](plugin/dashboard/README.md). Full-quality video: [docs/dashboard-demo.mp4](docs/dashboard-demo.mp4).

## Integrations

Optional — the plugin works without any of them. Each is a prompt pattern over an MCP server you already run; see [INTEGRATIONS.md](plugin/INTEGRATIONS.md).

| Connect | What it adds |
|---|---|
| Granola | Transcripts for `/interview-analysis`; recordings as things to confirm in `/today` |
| Gmail | Recruiter replies, rejections and offers as things to confirm in `/today` |
| Calendar | Upcoming interviews in the brief; new or moved events to confirm |
| Notion | The pipeline as a database, synced on demand |
| Playwright | Checks that postings are still live; interviewer research |
| Freehire | Live postings from 168 ATS platforms as a `/job-search` Discovery source |
| Slack / Telegram / Discord | `/today` digests to an accountability channel |

## Requirements

| Part | Needs | Install |
|---|---|---|
| Pipeline, scoring, prep, coaching | Claude Code | — |
| CV and cover-letter PDFs | Python 3.10+, `reportlab`, the Carlito font | `pip install -r plugin/scripts/requirements.txt`; Carlito from Google Fonts (macOS) or `apt install fonts-crosextra-carlito` |
| ATS check | `pypdf` or poppler's `pdftotext` | in `requirements.txt` |
| Follow-ups, `/sent`, archive | Python 3.10+, standard library | — |
| Dashboard | Python 3; Node only to rebuild the bundle | — |
| Cloud copy of the dashboard | Node, `wrangler`, Cloudflare Access | [`plugin/dashboard/README.md`](plugin/dashboard/README.md) |

Without the Python packages, `/apply` still writes the tailored CV in markdown and says the PDF step was skipped.

## job-sweep — just the weekly role list

A second, standalone plugin in this repo for when you want one command and nothing else: a weekly list of open product roles that match you, minus everything it already showed you. No pipeline, no company folders.

```sh
/plugin marketplace add https://github.com/markd888/ai-job-offer.git   # skip if already added
/plugin install job-sweep@job-offer
/job-sweep:sweep
```

Move to the full plugin later and `/setup` reads your `job-sweep/profile.md`, so you won't answer the same questions twice. See [`plugin-sweep/README.md`](plugin-sweep/README.md).

## What this version adds

Forked from pm-job-search 0.6.0 (MIT). On top of the original:

- **Application output:** CV → one-page PDF, `/ats-check`, `/cover-letter` with a claim checker.
- **What happens after you apply:** `/sent` records channel and referrer and freezes what you sent; `/follow-up` and `/outreach` work from that copy; people become records.
- **Seeing what works:** the funnel by channel in the dashboard, `/today` and `career-coach`.
- **An end state:** `/wrap-up` closes the search after an accepted offer.
- **Dashboard:** goals from `strategy.md`, interviews first, one fixed port, a read-only cloud copy behind Cloudflare Access.

Release notes: [CHANGELOG.md](CHANGELOG.md).

## Privacy

`userdata/` is gitignored except the fictional examples, so your profile, journal and company notes stay on your machine unless you share them on purpose.

**Install count (opt-in, off unless you say yes).** `/setup` asks once whether the plugin may send a one-time anonymous install count; existing installs are asked once by `/today`. If you say yes, it sends a random ID made on your machine and the plugin version, once. Nothing else: no name, email, CV, profile, companies or journal. The server (`telemetry-worker/`) stores no IP or user agent. Turn it off with "turn off the install count", `"consent": false` in `userdata/telemetry.json`, or `JOB_OFFER_TELEMETRY=0`.

CI scans every push and PR for personal data. The blocklist is personal data itself, so it isn't in the repo — it comes from the `PRIVACY_PATTERNS` repository secret (one regex per line). Forking? Set your own secret, or remove `.github/workflows/privacy-check.yml`. Locally: keep the same list in `.privacy-patterns.local` and run `make privacy-check`.

## Contributing and feedback

[CONTRIBUTING.md](CONTRIBUTING.md) covers the dev loop, the privacy rule and testing. Found a bug or want something? [Open an issue](https://github.com/markd888/ai-job-offer/issues) with the skill you ran, what you expected and what happened.

## Licence

MIT — see [LICENSE](LICENSE).
