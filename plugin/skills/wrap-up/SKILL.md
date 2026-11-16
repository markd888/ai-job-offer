---
name: wrap-up
description: This skill should be used when the user asks to "/wrap-up", "I accepted the offer", "I signed with <Company>", "close my search", "wrap up my job search", "withdraw from my other applications", or "/wrap-up --reopen" / "reopen my search" / "I'm looking again". Closes a search that ended in an accepted offer, one confirmed step at a time — drafts withdrawals for every role still in process and marks them not_interested on a yes, drafts thank-yous for the people who referred or helped, writes a retrospective to userdata/outputs/retro-<date>.md (time to offer, funnel by channel, where rejections clustered, what to keep), proposes story-bank and master-CV updates from the debriefs, and sets search_state: dormant in strategy.md so /today, /job-search and the dashboard go quiet. Drafts only — never sends anything, and changes nothing without a yes.
---

# /wrap-up — close the search after an accepted offer

The search has an end state. Without it, open applications keep generating follow-ups, interviews keep getting prep nudges and `/today` keeps counting a weekly target nobody is chasing. This skill closes each thread properly — politely, on the record — and then turns the plugin quiet.

**Voice:** `${CLAUDE_PLUGIN_ROOT}/TONE.md`; drafted messages use the user's `## Tone of Voice` in `profile.md`. Congratulate once, briefly, at the start — then get on with it.

**The one rule:** nothing is sent, ever, and nothing is written without the user's explicit yes to that step. Each step below shows what it will do, waits, then does it. The user can skip any step; skipping isn't failing.

All writes go through:

```sh
python3 -I "${CLAUDE_PLUGIN_ROOT}/scripts/wrap-up.py" <command> --userdata "$(pwd)/userdata" ...
```

## Step 0 — which offer

Find roles with `status: offer`. One → confirm it's the one accepted (`You accepted Lendable — Head of Product, right?`). Several → ask which. None → if the user names a company, the offer isn't recorded yet: offer to record it first (status `offer` with a History line), on a yes. Use that role folder as `<offer>` below (e.g. `Lendable` or `Plaid/senior-pm-consumer-credit`).

Then run `wrap-up.py open --offer <offer>`. It lists:

- **Withdraw** — roles still `applied`, `interviewing` or `offer` elsewhere, with any upcoming event;
- **Drop** — `new` / `to_apply` roles never applied to;
- **Thank** — people who referred the user or made an intro, and anyone linked to the accepted role.

Show the user this in plain words (no file names) and walk the steps in order.

## Step 1 — withdraw from what's still in process

For each role under **Withdraw**, draft a short, gracious withdrawal (40–80 words): thank them for their time by role or stage, say plainly the user has accepted another offer, leave the door open. Address it to the recruiter or interviewer named in the role's `## History`, journal or people files — never a name you can't find; otherwise "Hi <Company> team". Upcoming interviews first, so nobody prepares for a call that won't happen. Don't name the new employer unless the user wants to.

Show the drafts together. Then: `Once they're sent (or if you'd rather just close them quietly), shall I mark these <N> as withdrawn?` On a yes, for the roles the user confirms:

```sh
python3 -I .../wrap-up.py withdraw --userdata ... --role <role> [--role <role> ...]
```

Then **Drop**: `<N> roles you never applied to — mark them not interested too?` Same command on a yes. A role the user wants to keep watching stays as it is.

## Step 2 — thank the people who helped

For each person under **Thank**, draft a thank-you per `/job-offer:outreach`'s thank-you rules (30–60 words, name what they did, say how it ended). One already thanked gets a short "it worked out" update instead, or nothing. Show the drafts; when the user says which went out, log each with `record-outreach.py --direction sent --kind thank-you` exactly as `/outreach` Step 4 does.

## Step 3 — the retrospective

```sh
python3 -I .../wrap-up.py facts --userdata ... --offer <offer>
```

prints the numbers: dates and days to offer, roles by status, the funnel overall and by channel, rejections by stage with the recruiters' own words, outreach. Quote them as printed — channel rates only where the script gives one (5+ applications), never a benchmark presented as the user's.

Ask two questions, in one message: *What would you keep doing next time? What would you skip?* Then write `userdata/outputs/retro-<YYYY-MM-DD>.md`:

```markdown
# Search retrospective — <YYYY-MM-DD>

Accepted: <Company — Position>.

<the facts output, unchanged>

## What worked
- <2–4 bullets, each tied to a number above or the user's answer>

## What didn't
- <2–4 bullets, same rule — e.g. "careers-site applications: 7, none reached a screen">

## Keep next time
- <the user's own answer, in their words>
```

Show it before writing; write on a yes. No advice the numbers don't support.

## Step 4 — stories and the master CV

Read the `interview-debrief-*.md` files and the accepted role's materials. Collect:

- stories told in interviews that aren't in `userdata/stories/` (debriefs' "Recommended updates") → offer `/job-offer:story-builder --new "<title>"` for each, one at a time, only on a yes;
- metrics or outcomes the user stated in interviews that are sharper than the master CV's bullets → propose each as a before/after line for `userdata/cv.md`;
- the new role itself → propose a header line for the master CV (`### <Position> — <Company> — <year>–present`), to add once they start.

Edit `cv.md` only for the lines the user approves, exactly as approved. Never invent a metric to make a bullet stronger.

## Step 5 — go dormant

Ask: `Last step — I'll switch the plugin to quiet: no daily brief, no job sweep, no targets on the dashboard. Want a light market check every quarter (a quick look at the companies you were watching), or fully off?`

```sh
python3 -I .../wrap-up.py close --userdata ... --offer <offer> --market-check quarterly|off
```

It sets `search_state: dormant`, `search_closed`, `accepted_offer` and `market_check` in `strategy.md`, and adds an "offer accepted" line to the role's History. Then add a journal line under today's heading: `- [<Company>] Accepted the offer; search closed. (source: user)`.

Confirm in one or two plain sentences: what was closed, and how to reopen.

## Reopening

`/wrap-up --reopen`, "reopen my search", "I'm looking again": confirm once, then

```sh
python3 -I .../wrap-up.py reopen --userdata ...
```

Then suggest `/job-offer:setup` to refresh the profile and targets (the old `target_offer_date` is likely in the past) and `/job-offer:job-search` to restock the pipeline.

## Never

- Never sends, posts or schedules a message, and never asks for a login to do so.
- Never changes a role's status, a people file, `strategy.md`, the story bank or `cv.md` without a yes to that specific step.
- Never names a recruiter, interviewer or helper the user's files or words don't name.
- Never marks the accepted role anything but `offer`.
- Never deletes a role folder, a debrief or a draft.

## End-of-run nudge

None while dormant — that's the point. After `--reopen`, the `/setup` + `/job-search` suggestion above is the nudge.
