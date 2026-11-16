---
name: outreach
description: This skill should be used when the user asks to "/outreach <person or Company>", "ask <name> for a referral", "draft a referral ask", "ask for an intro to <Company>", "message <name> about <Company>", "thank <name> for the referral", "who do I know at <Company>", or when another skill suggests a warm route into a role. Keeps people as records in userdata/people/<slug>.md (relation, channel, linked roles, a log of every ask and reply), drafts a referral ask, warm intro ask, reach-out, follow-up or thank-you in the user's voice using only facts from the person file, profile, master CV and what was actually submitted, and logs it after the user says it went out. Drafts only — never sends anything.
---

# /outreach — people, referral asks and warm intros

Referrals and direct contact with a hiring manager are the channel that works best for senior roles; this skill gives them a place. Each person is a file in `userdata/people/` (schema: `${CLAUDE_PLUGIN_ROOT}/schemas/person.md.schema.md`). The skill drafts the message and, once the user has sent it, logs it — that log is what `/today` and the dashboard count as weekly outreach.

Voice follows `${CLAUDE_PLUGIN_ROOT}/TONE.md` and the user's `## Tone of Voice` in `profile.md`.

## Step 1 — who, and about what

- **`/outreach <name>`** — find the person by `name` in `userdata/people/*.md` (case-insensitive; ask if two match). Unknown name → Step 1b.
- **`/outreach <Company>`** — list people whose `roles` include a role at that company, or whose `company` is it. One → use them. Several → ask which (AskUserQuestion, at most four, the one with the latest `last_contact` first). None → say so in one line and ask whether the user knows anyone there; never suggest names you made up or found on the web as if they were contacts.
- **No argument** — show people with a `sent` ask and no reply for 7+ days (follow-up candidates), then people linked to `to_apply` / `new` P0–P1 roles with no ask yet. Ask which.

**1b — a new person.** Ask only what you can't infer, in one message: how they know each other (→ `relation`), where they talk (→ `channel`), where they work now. The person file is created when the first message is logged (Step 4), not before; record the user's own words about how they know each other in the body.

Then the kind of message, inferred when you can:

| Kind | When |
|---|---|
| `referral-ask` | the person works at the company and the user wants their CV put forward |
| `intro-ask` | the person knows someone at the company (a hiring manager, a team lead) |
| `reach-out` | reconnecting, or a first message with no ask yet |
| `follow-up` | an earlier ask got no reply (at least 7 days, at most two per ask) |
| `thank-you` | after a referral, an intro or an interview they helped with |

## Step 2 — gather facts (nothing else goes in the draft)

1. The person file: relation, how they know each other, the `## Log` (what was already asked or promised — never ask twice for the same thing without saying so).
2. The role, if there is one: `meta.md` (position, link, status) and `research-brief.md`.
3. What was sent, if the user already applied: the latest `submitted-*/` archive — the CV there is the one the referral would forward.
4. Otherwise `profile.md` (`## Positioning`, `## Proof Points`) and the master CV.

Same hard rule as `/apply`: every claim in the message traces to the person file, the profile, the master CV, the submitted materials, or something the user said in this conversation. No invented shared history ("great working with you on X" only if the person file or the user says they did), no invented mutual contacts, no inflated metrics, nothing from `## What NOT to Frame As`. If a stronger message needs a fact you don't have, ask for it (one question) or leave a `[CONFIRM: …]` marker.

## Step 3 — draft

- **Referral ask:** 60–110 words. Open with the shared context in one clause; name the role and link; one line on why it fits, from Positioning or the submitted CV; make it easy to say no; offer to send a short blurb they can forward — and include that blurb (40–60 words, third person) below the message.
- **Intro ask:** 50–90 words, plus a forwardable blurb (40–60 words) the person can paste to their contact.
- **Reach-out:** 30–70 words, no ask beyond a conversation.
- **Follow-up:** 25–50 words, one new thing or a polite close; never a third nudge.
- **Thank-you:** 30–60 words, name what they did; say what happened next if known.
- Channel fits the person's `channel`: email gets a subject line; LinkedIn / Telegram / WhatsApp are shorter and drop it.
- Language: the one the user uses with this person (from the log or the conversation), English by default.

Save to `userdata/people/drafts/<slug>-<kind>-<YYYY-MM-DD>.md` with recipient, channel and role on top. Show it in chat with: *Edit anything that doesn't sound like you.* Then one line: `Tell me when it's sent and I'll log it.`

## Step 4 — log it (only after the user says it went out)

```sh
python3 -I "${CLAUDE_PLUGIN_ROOT}/scripts/record-outreach.py" --userdata "$(pwd)/userdata" \
  --name "<Name>" --direction sent --kind <kind> --channel <channel> \
  --text "<one line: what was asked>" [--role <Company or Company/role-slug>] \
  [--company "<their company>" --relation <relation>]   # the last two only for a new person
```

It creates the person file on first contact, appends the log line, links the role and updates `last_contact`. If it stops because someone with that name is on file at another company, ask the user whether it's the same person; add `--new` only if it isn't. Then add a journal line under today's heading: `- [<Company>] <Kind in plain words> to <Name> via <channel>. (source: user)`.

**Replies.** When the user says the person answered — "Dana said yes", "she referred me", "he introduced me to Sam" — log it the same way with `--direction received` and `--kind reply | referral | intro | feedback`. A referral that turns into an application is recorded by `/job-offer:sent <Company>` with `--referred-by "<Name>"`, which logs the referral on this file too; offer it when the user says the application went out.

Confirm in one plain sentence (`Logged your referral ask to Dana.`). Name no files.

## Never

- Never sends, posts or schedules anything, and never asks for the user's login to do so.
- Never invents a person, a relationship, a conversation, a mutual contact or a result.
- Never contacts or drafts for someone the user hasn't named or confirmed as a contact.
- Never logs a message before the user says it went out.
- Never more than two follow-ups on one ask.
- Never writes to a role's `meta.md` — status and `referred_by` belong to `/sent`.

## End-of-run nudge

One line per `${CLAUDE_PLUGIN_ROOT}/references/recommended-flow.md`. Typical: after a referral ask, nothing until they reply (say when a follow-up would be due — 7 days out); after a `received referral`, `/job-offer:sent <Company>` once the application is in; after a thank-you, nothing.
