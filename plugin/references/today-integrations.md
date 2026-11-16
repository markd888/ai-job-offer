# /today — integrations

<!-- Loaded on demand by skills/today/SKILL.md; part of /today, split out to keep the always-loaded skill small. -->

Everything here runs only when `userdata/integrations.md` shows the integration as `wired`. Without it, /today works from markdown alone.

## Input phase

### Step 2 — inference pass (when integrations wired)

Read `userdata/integrations.md` to find which MCPs are wired. For each wired integration, scan the window. Same auth-error rule as the existing Integration-data section: surface one line per failed integration at the top of the input phase, do not silently skip, continue with the others.

- **Gmail (when wired).** Reuse the existing gmail filter (saved in integrations.md). Fetch subject + from + date metadata over the window (not the 7d hardcoded in the output-phase fetch). For each result, classify into one of: `recruiter-reply`, `rejection`, `scheduling`, `offer`, `unclear`. Match against `userdata/companies/*/meta.md` + `*/*/meta.md` by alias + domain + recruiter-name-in-journal as the output-phase fetch already does.
- **Calendar (when wired).** Fetch events in the window. Filter by the same keywords as the output-phase fetch (`interview`, `recruiter`, `screen`, `round`, `intro call`, `final loop`, `panel`, `take-home review`) plus matched company names. For each kept event, classify into: `new-event`, `rescheduled`, `cancelled` (rescheduled / cancelled requires comparing against any prior `next_event` value in the matched company's meta.md).
- **Granola (when wired).** Reuse the auto-Granola lookup pattern documented in `/interview-analysis`: call the wired Granola list_meetings tool over the window, match meeting titles against company names + interview/recruiter keywords. For each match, capture title + date.

Dedup across integrations: if the same fact surfaces via two sources (e.g. a calendar event + a gmail confirmation), present it ONCE in the confirms list with both sources noted (`source: calendar + gmail`).

### Step 3 — targeted confirms

Render inferred deltas as a numbered list, grouped by source. Skip this step entirely if step 2 produced no items. Example output shape:

> Since your last entry (2026-05-15), I see:
>
> From calendar:
> 1. Plaid — Round 2 panel scheduled Fri 2026-05-22 14:00
> 2. Klarna — Recruiter call moved from Wed to Thu
>
> From gmail:
> 3. Lendable — Reply from Sarah at Lendable (likely rejection — want me to read it?)
> 4. Stripe — New inbound from a recruiter named James (no company match yet)
>
> From granola:
> 5. Klarna recruiter call transcript captured Mon 2026-05-15
>
> Confirm 1-5 ('all', '1 3 5', or describe corrections). Anything I should edit or skip?

User response handling:
- `all` / `yes` → confirm every inferred item as-is.
- Numbered subset (`1 3 5`) → confirm only those.
- `1 wrong — that was R3 not R2` → confirm with edit applied before write.
- `skip 3` → drop item 3 from this run.
- `4 is for company X` → re-route the unmatched inbound to company X before write.

If the user response is ambiguous, ask one clarifying question rather than guessing. Never write an item the user has not explicitly confirmed.

## Output phase

If `userdata/integrations.md` exists, this skill optionally folds in live data from Calendar and Gmail MCPs to make the brief richer. Both are fully optional — when absent or failing, /today degrades gracefully to the markdown-only flow.

### Calendar fetch (when calendar wired)

When `userdata/integrations.md ## calendar` shows status `wired` with a tool prefix:

1. Call the wired calendar tool to list events in the next 14 days. Match against all `userdata/companies/*/meta.md` (and `*/*/meta.md`) — extract company names + alias each title field — and against keywords: `interview`, `recruiter`, `screen`, `round`, `intro call`, `final loop`, `panel`, `take-home review`. Keep matches; discard the rest.
2. For each kept event, capture: `{Day D Mon, HH:MM}`, matched company (or `unmatched` for keyword-only hits), event type (`interview`, `recruiter`, etc.).

If the calendar tool returns an auth or quota error: do not silently skip. Surface one line at the top of the heads-up section: `Calendar fetch failed (<error type>) — heads-up missing event data this run. Re-auth via your calendar MCP.`

### Gmail fetch (when gmail wired)

When `userdata/integrations.md ## gmail` shows status `wired` with a tool prefix + filter string:

1. Call the wired gmail tool with the saved filter (typically: recruiter / talent / company-domain matches) over the last 7 days.
2. For each result, fetch the subject + from + date metadata (no body).
3. Match each email to a company in `userdata/companies/*/meta.md` (alias-checking the company name, domain in the from-address, and any explicit recruiter name from journal.md). Each email is either `matched-to-<Company>` or `new-inbound` (no company match).

Same auth-error rule as Calendar: surface a single line at the top of heads-up, don't silently skip.

### Granola fetch (when granola wired)

Granola data is consumed by the INPUT phase only — see `## Input phase` Step 2. The output phase (this section's brief enrichments) does not surface anything from Granola. If `userdata/integrations.md ## granola` shows status `wired`, the input phase will list interview / recruiter meeting transcripts captured in the window; the output phase ignores Granola entirely.

### What never happens

- /today never writes to integrations.md.
- /today never persists raw Calendar/Gmail responses verbatim. Only the user-confirmed facts that pass through the input phase land on disk (see `## Input phase` for the contract); the saved brief includes the rendered output, not raw API responses.
- /today never auto-updates `last_inbound` on company meta.md based on Gmail matches alone. It writes `last_inbound` only for contact the user confirmed in Step 3 or stated in Step 4, alongside `next_event`, `status` and the `## History` block.
