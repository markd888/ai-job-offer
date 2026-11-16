# Schema — `userdata/strategy.md`

The user's plan. Read by `/today` (progress tracking), `/evaluate-position` (anti-goals), and `career-coach`. Written by `/setup` (basic) and edited via `career-coach`.

Checked by `scripts/validate_userdata.py` (rules `strategy.required`, `strategy.date-format`, `strategy.forbidden-key`, `strategy.search-state-enum`). The frontmatter's opening `---` may be preceded by blank lines and/or a leading HTML comment block (as in `plugin/templates/strategy.template.md`) — the validator skips past it before parsing.

## Required frontmatter keys

- **`target_offer_date`** — `YYYY-MM-DD`, or `null` (the `/setup` Step 7 "Not sure yet" path). Key must be present either way.
- **`weekly_targets`** — block with `warm_outreach` and/or `applications` (either may be null). Key must be present.

## Forbidden keys (drift signals)

- **`target_date:`** — the documented sub-agent drift misspelling of `target_offer_date:`. Deliberately present in the `contrarian-messy` snapshot as test material.

## Search state (written by `/wrap-up`)

- **`search_state`** — `active` (the default when absent) or `dormant`. `/wrap-up` sets `dormant` after an accepted offer; `/wrap-up --reopen` sets `active` again. While dormant, `/today` writes no brief, `/job-search` runs only a market check, and the dashboard shows a "search closed" banner with no weekly targets.
- **`search_closed`** — `YYYY-MM-DD` the search was closed.
- **`accepted_offer`** — quoted `"Company — Position"` of the accepted role.
- **`market_check`** — `quarterly` or `off`. With `quarterly`, `/today` offers `/job-search --market-check` once 90 days have passed since `search_closed` or `last_market_check`.
- **`last_market_check`** — `YYYY-MM-DD`, written by `/job-search --market-check`.
- **`search_reopened`** — `YYYY-MM-DD`, written by `/wrap-up --reopen`.

## Common optional keys / sections

`pipeline_targets`, `checkpoints`, `## Headline goal`, `## Anti-goals`, `## Checkpoints` prose.
