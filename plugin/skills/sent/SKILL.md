---
name: sent
description: This skill should be used when the user asks to "/sent <Company>", says "I applied to <Company>", "sent the application to <Company>", "submitted my CV to <Company>", "<Company> application is out", or accepts /apply's closing offer to record an application. Records an application going out in one step after an explicit yes — status applied, date_applied, channel (referral / cold / recruiter / linkedin / company-site / other), optional referred_by, a frozen copy of the CV, cover note, ATS check and posting in submitted-<date>/, and one History line. This is what starts the follow-up clock. Never sends anything.
---

# /sent — record an application going out

One transaction for the moment an application leaves: the role's `meta.md` gets `status: applied`, `date_applied`, `channel` and, for a referral, `referred_by`; what was sent is frozen in `submitted-<date>/`; `## History` gets one line. Without `date_applied`, `/job-offer:follow-up` never finds the role, and without `channel` there is no funnel by channel.

Voice follows `${CLAUDE_PLUGIN_ROOT}/TONE.md`.

## Step 1 — find the role

`<Company>` is matched case-insensitively against `userdata/companies/`; fuzzy-suggest on a miss (`No 'Plad' folder. Did you mean Plaid?`). If the company tracks several roles, ask which. If there's no folder at all, say so and offer `/job-offer:evaluate-position <link>` first — don't create one here.

Read `meta.md`:

- `new` / `to_apply` → the normal case.
- `applied` with no `date_applied` (flipped in chat or by hand) → fill in the gaps; say so in the confirmation.
- `applied` with a `date_applied` → `Already recorded as sent on <date>. Record it again?` Only on a yes, add `--force`.
- `interviewing`, `offer`, `rejected`, `not_interested` → `<Company> is already <plain-English state> — /sent is for the moment an application goes out.` Stop unless the user insists; then `--force`.

## Step 2 — the channel, and the yes

Infer what you can before asking: the conversation, `journal.md` lines tagged `[<Company>]`, `## History`. Channel values:

| `channel` | When |
|---|---|
| `referral` | someone inside put the CV forward; ask for their name if it isn't known |
| `recruiter` | through an agency or in-house recruiter who reached out |
| `linkedin` | LinkedIn Easy Apply or a LinkedIn message |
| `company-site` | the company's careers page or ATS form |
| `cold` | a direct email or DM to someone at the company, unsolicited |
| `other` | anything else |

Then confirm in one line, in the user's words, and wait for the yes:

> Recording your Plaid application as sent today via a referral from Dana, with the CV from 14 Nov archived. OK?

Ask the channel only if you couldn't infer it (AskUserQuestion with the likeliest four). The date is today unless the user says otherwise ("I sent it Friday" → that date). Nothing is written before the yes.

## Step 3 — write it

If the posting text is at hand (a fetched JD, `research-brief.md`'s source fetched now, or pasted text), save it to a temp file for the archive. Then:

```sh
python3 -I "${CLAUDE_PLUGIN_ROOT}/scripts/record-sent.py" <role folder> --channel <channel> \
  [--referred-by "<Name>"] [--posting <file>] [--date YYYY-MM-DD]
```

It writes the frontmatter, archives the latest CV (PDF and markdown), cover letter or note, ATS check and posting into `submitted-<date>/` with a manifest, and appends one History line. With no CV in the folder (applied with the master CV, say) it still records the application and says nothing was archived. If it refuses, tell the user why in one line; don't edit `meta.md` by hand instead.

Then append to `journal.md` under today's heading: `- [<Company>] Application sent via <channel>. (source: user)`.

## Step 4 — confirm

One or two plain sentences: what was recorded and what happens next — `Recorded. If Plaid stays quiet, the follow-up comes up on 26 Nov.` (date_applied + 10 days). If nothing was archived or the posting text wasn't kept, say it in a clause. Name no files and no field names.

## Never

- Never writes before the user's yes, and never infers that an application went out from a CV having been drafted.
- Never sends, submits or uploads anything — it records what the user already did.
- Never edits the CV, cover note or posting it archives.
- Never touches another role's `meta.md`.
