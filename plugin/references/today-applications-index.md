# /today — applications.md regeneration

<!-- Loaded on demand by skills/today/SKILL.md; part of /today, split out to keep the always-loaded skill small. -->

`applications.md` is a hybrid file: /today owns one HTML-comment-delimited block; the user owns everything outside it. Spec is in plan §I.2.

The GENERATED block looks like:

```markdown
<!-- BEGIN GENERATED — /today regenerates this block. Edit outside the markers, not within. -->

# Applications
Last regenerated: <YYYY-MM-DD HH:MM>

## Active
<table of all status: offer | interviewing | applied | to_apply | new>

## Decided
<table of all status: rejected | not_interested, last 30 days only — older rolls off by date_rejected | date_not_interested>

## Summary
- N active threads (M P0).
- K decided this search.
- Warm-outreach attempts this week: A / B.   (omit this line if no warm_outreach target set)

<!-- END GENERATED -->
```

Rules:

1. **Both markers present** → replace everything between them with a fresh GENERATED block. Preserve the rest of the file byte-for-byte (text above the begin marker, text below the end marker).
2. **File does not exist** → write a fresh file: GENERATED block + a `\n\n## Notes\n\nYour free-text area. /today never touches anything below this line.\n` footer.
3. **File exists but has neither marker** → also write a fresh complete file (same as case 2). The user's previous freeform notes are preserved only if they happen to sit below the new GENERATED block — but since this case implies the file pre-dates the partition convention, an overwrite is acceptable. Print a one-line warning to chat: `applications.md had no markers — regenerated as fresh file.`
4. **Exactly one of the two markers is present** → DO NOT WRITE. Print a clear error to chat: `applications.md has only the <BEGIN|END> marker. Refusing to regenerate to avoid destroying user content. Fix by either adding the missing marker or deleting both.` Continue with the rest of /today (save the daily brief, print to chat).

Active table columns: `| Company | Role | Status | Tier | Link | Last activity |` — same sort as the pipeline_state table in the brief. Company cell links to the company folder: `[Plaid](../companies/Plaid/)` for flat layouts, `[Plaid](../companies/Plaid/<role-slug>/)` for multi-role. The `Link` column contains the JD URL from the company's `meta.md` `link:` field.

Read the `link:` field with the Read tool before rendering it — never synthesize it. If the field is genuinely absent or blank, render a literal em-dash `—` in the cell; NEVER write a placeholder like `(url not captured)` or invent a URL. A blank link is real data (a role logged without a live posting), not a gap to paper over.

Example row:

```markdown
| Company | Role | Status | Tier | Link | Last activity |
|---|---|---|---|---|---|
| Plaid | Senior PM | to apply | P0 | https://jobs.lever.co/plaid/… | 2026-05-25 |
```

Any chat output that prints application rows (pipeline section, status lists, brief output) must include the JD URL inline:

Format: `- <Company> — <Role> — <status> — <url>`. Long URLs are fine; do not shorten or wrap.

Decided table columns: `| Company | Status | Tier | Position | Decided |` where `Decided` is the most recent of `date_rejected` / `date_not_interested`. Sort by Decided descending. Cap at items decided within the last 30 days. (`offer` is intentionally NOT included here — an open offer is a high-signal Active state, not a decided one; surface it in the Active table at the top.)

Summary line counts:
- `N active threads (M P0).` — N = count of meta.md with `status` in `{new, to_apply, applied, interviewing, offer}`. M = subset of those with tier P0.
- `K decided this search.` — K = count of meta.md with `status` in `{rejected, not_interested}`.
- `Warm-outreach attempts this week: A / B.` — A = `sent` lines of kind `reach-out`, `referral-ask`, `intro-ask` or `follow-up` in `userdata/people/*.md` logs dated in the current ISO week (window = `[Monday of this week, today]` inclusive; rule in `${CLAUDE_PLUGIN_ROOT}/schemas/person.md.schema.md`, the same count the dashboard shows). Journal wording is not counted. B = `warm_outreach` target from strategy.md. Omit the entire line if no warm_outreach target set. On Monday morning A is naturally near 0 — that's intentional, it surfaces a fresh week.
