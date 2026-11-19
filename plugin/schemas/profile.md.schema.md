# Schema — `userdata/profile.md`

The user's identity + tier rubric. Read by `/evaluate-position`, `/job-search`, `/apply`, `/interview-prep`, `/today`, and the reviewer agents. Written by `/setup`.

Checked by `scripts/validate_userdata.py` (rules `profile.required`, `profile.positioning`), which the test-personas harness runs in Phase 3.5 and CI runs over `tests/snapshots/`. The frontmatter's opening `---` may be preceded by blank lines and/or a leading HTML comment block (as in `plugin/templates/profile.template.md`) — the validator skips past it before parsing.

## Required frontmatter keys

Every profile.md MUST have these top-level keys with non-empty values:

- **`name`** — the user's name.
- **`target_titles`** — block list of role titles. At least one item.
- **`tier_weights`** — the five-dimension scoring rubric (`role_fit`, `domain_fit`, `business_health`, `location_fit`, `competitive_edge`), each with rubric strings for scores 1–3. `/evaluate-position` cannot run without it.
- **`tier_thresholds`** — `p0` and `p1` integer cut-offs.

## Required body sections

- **`## Positioning`** — may hold placeholder text after a minimal `/setup`, but the heading must exist; `/apply` and the reviewer agents anchor on it.

## Common optional keys (absence allowed, never flagged as drift)

`city`, `timezone`, `email`, `phone` (the number the CV must show — `/ats-check` fails the contacts check without it in the PDF's text), `linkedin_url`, `target_industries`, `geography`, `salary_band`, `hard_filters`, `company_shape_adjustment`, `freehire_filters` (see below), and the `## Proof Points`, `## Moat`, `## Tone of Voice`, `## What NOT to Frame As`, `## Companies of interest` body sections.

## `freehire_filters` (optional)

Search filters for the Freehire Discovery source in `/job-search`. Written by `/setup` when the Freehire MCP is connected; edit freely. Checked by rule `profile.freehire-filters` (values from `plugin/scripts/freehire.py`, which mirrors Freehire's `list_filter_values`).

```yaml
freehire_filters:
  category: [product]                 # Freehire category values
  seniority: [senior, lead]           # intern|junior|middle|senior|lead|staff|principal|c_level
  countries: [ES]                     # ISO alpha-2; searched on-site/hybrid/remote
  on_site_work_modes: [hybrid, onsite] # optional; default hybrid, onsite, remote
  remote_regions: [eu, global]        # remote-only search, run as a SEPARATE call
  salary_min: 70000                   # optional; needs salary_currency
  salary_currency: EUR
  title_allow: [product manager]      # optional; defaults in freehire.py
  title_deny: [product owner]         # optional
  exclude_companies: [SomeAgency]     # optional, on top of the built-in agency list
```

At least one of `countries` / `remote_regions` is required. Freehire ORs country and region filters, so `freehire.py filters` always emits them as two searches.

## When to update this schema

A skill starts requiring a new profile key → add it here AND to `scripts/validate_userdata.py` AND to `/setup`'s writes, in the same change.
