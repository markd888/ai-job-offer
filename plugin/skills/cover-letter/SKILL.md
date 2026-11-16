---
name: cover-letter
description: This skill should be used when the user asks to "/cover-letter <Company>", "write a cover letter for <Company>", "draft a cover note for <Company>", "does <Company> need a cover letter", or accepts /apply's closing offer of a cover letter. Drafts a 150–250-word letter in the user's voice that answers the posting's top two or three needs with one proof point each, every claim traced to the master CV, profile.md, the tailored CV or a user answer; checks it with cover-letter-check.py; writes userdata/companies/<Co>/[<slug>/]cover-<YYYY-MM-DD>.md and builds the PDF in the CV's look with cover-letter-build.py. Lists in chat what it did NOT claim. Never sends anything and never touches meta.md.
---

# /cover-letter — a short letter that answers the posting

A cover letter earns its place when it does one job the CV can't: say which of the posting's needs the user has already met, with one proof each, in their own voice. This skill writes that letter and nothing more. `/job-offer:sent` archives it with the CV when the application goes out.

**Voice:** chat output and the letter follow `${CLAUDE_PLUGIN_ROOT}/TONE.md` and the user's `## Tone of Voice` in `profile.md`. Ask only when the answer changes the letter.

## Inputs

- `<Company>` — matched case-insensitively against `userdata/companies/`; if the company tracks several roles, ask which. No folder → say so and offer `/job-offer:evaluate-position <link>`.
- The role's `meta.md` (position, link) and `research-brief.md` — the posting's needs and the company facts the letter may mention.
- The latest `cv-*.md` in the role folder if `/apply` made one — the letter must not claim more than it. Otherwise the master `userdata/cv.md`.
- `userdata/profile.md` — `## Positioning`, `## Proof Points`, `## Tone of Voice`, `## What NOT to Frame As`.
- `userdata/people/*.md` linked to this role, if any — a referrer can be named only when their log shows a `received referral` (or the user says so now).

## Step 1 — the needs and the proofs (silent)

1. From the posting (fetch `meta.md`'s link if it's live; else the brief), list the 2–3 needs the hiring manager will screen for. Concrete ones — "thin-file underwriting", "owning onboarding end to end" — not "strong communicator".
2. For each, pick **one** proof point from the CV or profile: a role, what the user did, the result with its number exactly as written there. One proof per need; the CV carries the rest.
3. Note every posting need you can't back. These go in the "did NOT claim" list, never in the letter.

If a need matters and nothing backs it but the user might have it (a domain, a tool, a team size), ask — at most two questions, in one message. Otherwise don't ask; draft.

## Step 2 — draft

- **150–250 words.** Plain paragraphs, no headings, no bullets — the builder lays out paragraphs.
- Open with the role by name and one sentence on why this company, from the brief. No "I hope this finds you well", no "I am writing to apply".
- One short paragraph per need: the need in a few words, then the proof — what the user did and what changed, numbers exactly as in the source.
- Close with one line on how they work (from Positioning) if it fits this team, then a low-pressure line in the user's tone. Sign off as `## Tone of Voice` says (first name only, if it says so).
- Greeting: a named person only if the brief, the posting or the user names them; else the team (`Dear <Company> <team> team,`).
- UK or US English as the profile's tone says.

**Hard rule, same as `/apply`:** every claim traces to the master CV, the tailored CV, `profile.md`, the brief (company facts only) or something the user said in this conversation. No invented metrics, scope, tools, team sizes or motives; nothing from `## What NOT to Frame As`. A claim the letter needs but can't trace becomes a `[CONFIRM: …]` marker, never a guess.

## Step 3 — check, save, build

Save to `userdata/companies/<Co>/[<slug>/]cover-<YYYY-MM-DD>.md` (exists already → `-v2`, `-v3`; never overwrite or delete an older letter). Then:

```sh
python3 -I "${CLAUDE_PLUGIN_ROOT}/scripts/cover-letter-check.py" <letter.md> \
  --sources <tailored or master cv.md> userdata/profile.md <role>/research-brief.md
python3 -I "${CLAUDE_PLUGIN_ROOT}/scripts/cover-letter-build.py" <letter.md> \
  <role folder>/<First>_<Last>_Cover_<Company>.pdf --cv <tailored or master cv.md>
```

The check fails on a number or a name that isn't in the sources, on a length outside 150–250 words, and on headings or bullets. Fix the letter — drop or reword the claim, or turn it into a `[CONFIRM: …]` — and re-run until it passes. Add a file of the user's answers to `--sources` when a claim comes from them. A pass means nothing was made up; it doesn't make a claim fair, so still read each one against its source.

The builder takes the name and contact line from the CV, so the letter and CV match. It needs `reportlab` and the Carlito font, like `cv-build.py`; if either is missing, keep the markdown, say in one line that the PDF was skipped and what to install, and carry on.

## Output to chat

> Drafted your cover letter for **<Company> — <Role>** (<N> words).
>
> It answers:
> - <need> — <proof, a few words>
> - <need> — <proof>
> - <need> — <proof>
>
> Did NOT claim (nothing backs it): <need or keyword>, <…>.
>
> <If markers: `<N> [CONFIRM] marker(s) to resolve before sending.`> Edit anything that doesn't sound like you. Tell me once it's sent and I'll record it.

Rules: the "Did NOT claim" line always appears when the posting asked for something the letter skipped — it's the honesty signal, never collapsed into "a few things". Name no files. One closing line only.

When the user says the application went out, hand over to `/job-offer:sent <Company>`, which archives the letter and its PDF with the CV.

## Never

- Never sends, uploads or submits anything.
- Never writes to `meta.md`, the master CV, `profile.md` or the tailored CV.
- Never claims more than the CV that goes with it.
- Never names a referrer, a mutual contact or an interviewer the user's files or words don't name.
- Never pads to reach 150 words — a short letter with three proofs beats a long one with filler; if it can't reach 150 honestly, say so and let the user decide.

## End-of-run nudge

One line per `${CLAUDE_PLUGIN_ROOT}/references/recommended-flow.md` — usually the closing "Tell me once it's sent" already is it. If the role has someone in `userdata/people/` with no referral ask yet, suggest `/job-offer:outreach <Company>` before sending.
