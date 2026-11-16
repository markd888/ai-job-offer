---
name: follow-up
description: This skill should be used when the user asks to "/follow-up", "/follow-up <Company>", "who should I chase", "draft a follow-up for <Company>", "nudge <Company>", "send a thank-you to <Company>", "<Company> replied", "<Company> got back to me", or when /today's heads-up lists follow-ups due. Lists applications quiet for 10+ days (at most two follow-ups each), drafts a short follow-up or post-interview thank-you in the user's voice using only claims from what was actually submitted, records it in meta.md once the user says it was sent, and records a company's reply (last_inbound) when the user mentions one. Drafts only — never sends anything.
---

# /follow-up — chase quiet applications, thank interviewers

Voice follows `${CLAUDE_PLUGIN_ROOT}/TONE.md`.

## Modes

- `/follow-up` — list what's due, then draft for the one the user picks.
- `/follow-up <Company>` — draft for that company (ask once which role if there are several).
- `/follow-up thanks <Company>` — thank-you note after an interview stage; offered automatically when an interview is logged in chat or by `/today`.

## Step 1 — what's due

```sh
python3 -I "${CLAUDE_PLUGIN_ROOT}/scripts/follow-ups.py" --userdata "$(pwd)/userdata"   # add --company <name> to narrow
```

Rules the script applies: status `applied` (or `interviewing` with no upcoming event), quiet ≥ 10 days since the latest of `date_applied`, `last_inbound`, `last_follow_up`, fewer than 2 follow-ups. Quiet over 30 days, two follow-ups already sent, or an unknown company → "close instead": propose `rejected` with `rejection_stage: application` (silence), and change it only on a yes.

Show the due list as `- <Company> — <Role> — quiet <N>d — <url>`, most recent first, at most 8. Recommend the 2–3 worth a nudge: roles with a named contact, a tailored CV, or a tier P0/P1. Ask which.

## Step 2 — gather what the employer saw

In the role folder, in this order:

1. `submitted-*/` — the CV, cover note and posting exactly as sent. This is the only source of claims.
2. If there's no archive: the role's `cv-*.md` dated on or before `date_applied`. Say once that the draft is based on the CV on file, not a frozen copy.
3. If neither exists (most imported history): no claims about experience — a plain two-line check-in.
4. `meta.md` (`channel`, `referred_by`, both written by `/job-offer:sent`) and `journal.md` lines tagged `[<Company>]` for the contact's name, the channel (email, LinkedIn, Telegram, ATS) and anything already said. A referral or recruiter beats a generic inbox.

## Step 3 — draft

- **Follow-up #1:** 50–80 words. Role name and date applied; one line tying the most relevant submitted proof point to the posting's main need; a light ask ("happy to share more on X", "is the role still open?"). No "just checking in", no guilt, no attachments unless asked.
- **Follow-up #2** (at least 7 days after #1): 30–50 words, adds one new thing (a relevant recent result, an article, availability) or simply closes the loop politely.
- **Thank-you** (same or next day after an interview): 60–100 words, names one specific thing discussed (from the debrief, Granola notes or journal) and one line on fit. Nothing that wasn't said or submitted.
- Match the channel: email gets a subject line; LinkedIn/Telegram drop it and shorten.
- Language follows the conversation with that company (the language that company has been writing in, English by default).
- Claims only from Step 2. If a stronger proof point exists in the master CV but wasn't submitted, don't use it — offer it separately as "could mention".

Save the draft to `<role folder>/follow-up-<YYYY-MM-DD>.md` with the channel and recipient on top, and show it in chat with: *Edit anything that doesn't sound like you.*

## Step 4 — record it (only after the user says it went out)

- `meta.md` frontmatter: `follow_ups: <n+1>`, `last_follow_up: <YYYY-MM-DD>` (add the fields if missing; keep the rest untouched).
- `## History`: `- <date>: follow-up #<n> sent via <channel> to <name or "hiring team">`.
- `journal.md`, under today's heading: `- [<Company>] Follow-up #<n> sent via <channel>. (source: user)`

For a thank-you, record the History and journal lines only; it doesn't count toward the two follow-ups.

## When the company writes back

Whenever the user says a company replied, called or scheduled something — here, after a follow-up, or anywhere in the conversation — record it, so the role leaves the quiet list:

```sh
python3 -I "${CLAUDE_PLUGIN_ROOT}/scripts/record-inbound.py" <role folder> --date <YYYY-MM-DD> \
  --what "<reply from Dana (recruiter)>" --source user
```

Plus a journal line: `- [<Company>] <what came in>. (source: user)`. A rejection or an offer still needs the user's yes before the status changes.

## Never

- Never sends, posts or schedules anything. Drafts only.
- Never more than two follow-ups per application.
- Never invents a contact, a conversation or a result.
- Never changes `status` without an explicit yes.
