# /today — write contracts

<!-- Loaded on demand by skills/today/SKILL.md; part of /today, split out to keep the always-loaded skill small. -->

### journal.md format

The existing free-form append convention is preserved. The input phase adds two conventions on top:

- Bullets begin with `[<Company>]` when the fact is company-scoped. Bullets without a tag are global / personal (mock interviews, energy notes, structural reflections).
- Bullets end with `(source: <integration|user>[, confirmed])`. The `, confirmed` trailer applies only to integration-sourced facts that the user explicitly approved in Step 3 — never to user-sourced bullets from the catch-all (those are inherently the user's own input). So: `(source: calendar, confirmed)` is valid, `(source: user, confirmed)` is not — user-sourced bullets always read `(source: user)`.
- Provenance lets future skills filter by trust level.

One bullet per fact. Multi-fact compound entries get split into separate bullets.

Example block written by a single input phase:

```
## 2026-05-18
- [Plaid] Round 2 panel scheduled Fri 2026-05-22 14:00. (source: calendar, confirmed)
- [Lendable] Reply from Sarah, declined — seniority mismatch cited. (source: gmail, confirmed)
- Mock with Sasha on pricing story — felt rusty, need to re-practise. (source: user)
```

Rules:
- If today's `## YYYY-MM-DD` heading already exists in journal.md (e.g. a prior /today run today added entries), append the new bullets beneath the existing heading rather than creating a duplicate heading.
- If today's heading does not exist, create it at the end of the file (with a blank line before it).
- Never edit or remove bullets that were already in journal.md — the file is append-only from /today's perspective.

### meta.md updates

Per-company meta.md uses (or gains, if not already present) the fields below, written by the input phase. Existing fields owned by other skills — `company`, `position`, `tier`, `link`, `date_applied`, `date_added`, `monitoring`, `rejection_stage`, `date_rejected`, `date_not_interested` — are untouched.

- **`last_inbound:`** — date the company last got in touch. Written for every confirmed fact that is contact *from* the company: a `recruiter-reply`, `rejection`, `scheduling` or `offer` email, a `new-event` or `rescheduled` calendar item the company sent, a captured Granola call, or a catch-all line as described in Step 4. Use the email's or meeting's date, not today's. Write it with the script, which keeps the later date and adds the History line itself:

  ```sh
  python3 -I "${CLAUDE_PLUGIN_ROOT}/scripts/record-inbound.py" <role folder> --date <YYYY-MM-DD> \
    --what "<reply from Sarah (recruiter)>" --source <gmail|calendar|granola|user>
  ```

  `follow-ups.py` and the quiet-application rule count from it, so a role that just heard back drops off the follow-up list.

- **`next_event:`** — string, free-form. Examples: `"R2 panel Fri 2026-05-22 14:00"`, `"Recruiter call Thu 2026-05-21 10:00"`. Cleared (set to empty string or removed) when the input phase confirms the event passed without follow-up OR when it was cancelled. Updated in-place when an event is rescheduled.
- **`status:`** — enum, one of: `new`, `to_apply`, `applied`, `interviewing`, `offer`, `rejected`, `not_interested`. The input phase only transitions OUT of an active state when a fact unambiguously implies it: a confirmed rejection → `rejected`, a confirmed offer → `offer`. Confirmed scheduling events do NOT auto-promote `applied` → `interviewing` (other skills own that transition based on richer signal).
- **`## History` block** — chronological list of state transitions, one line per change. Format: `2026-05-18: status → rejected (seniority mismatch — Sarah at Lendable, gmail confirmed)`. Append to the end of the block; create the `## History` heading at the bottom of meta.md if it doesn't exist.

Rules:
- When an event is rescheduled, update `next_event` AND append a History line: `2026-05-18: next_event → "R2 panel Fri 2026-05-22 14:00" (rescheduled from Wed, calendar confirmed)`.
- When an event passes without action (e.g. yesterday's recruiter call happened), clear `next_event` and append: `2026-05-18: next_event cleared (passed, no follow-up captured yet)`.
- When the input phase has no implication for a given company in meta.md, do not touch that file at all.
- Frontmatter changes are YAML-safe: preserve other fields, preserve quoting style, preserve trailing comments.
