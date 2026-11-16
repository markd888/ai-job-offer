# /setup — importing a job-sweep install

<!-- Loaded on demand by skills/setup/SKILL.md; part of /setup, split out to keep the always-loaded skill small. -->

**If `job-sweep/profile.md` exists**, read it first. It means the user already
ran the standalone `job-sweep` plugin, and it holds `target_titles`,
`target_industries` and `geography` — three of the answers to Steps 2, 3 and 5. Say one line:

> "Found your job-sweep profile — I'll carry those answers over so you don't repeat them."

Carry the values into Steps 2, 3 and 5 as the pre-filled defaults, and confirm
them there exactly as you would confirm CV-derived values — shown, never
auto-accepted. A sweep profile is a stronger source than a CV inference,
because the user already confirmed it once; it is still not a reason to skip
the confirmation.

Both a CV and a sweep profile may exist. The sweep profile wins for
`target_titles`, `target_industries` and `geography` — the user confirmed those
answers; the CV only implies them. The CV still supplies everything else.

**If `job-sweep/seen-roles.jsonl` also exists**, carry it over so the roles
the user already saw in `job-sweep` don't come back as `status: new` once
`/job-search` starts reading the full ledger. Create `userdata/outputs/` if it
doesn't exist yet, then:
- `userdata/outputs/seen-roles.jsonl` does not exist → copy the sweep ledger
  to it verbatim.
- `userdata/outputs/seen-roles.jsonl` already exists → append only the lines
  from the sweep ledger whose `strict_key` is not already present in it. Never
  overwrite an existing line, never duplicate one.

Say one line: `"Also carried over your job-sweep history — already-seen roles
won't resurface as new."`
