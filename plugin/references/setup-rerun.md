# /setup — re-run mode question loop

<!-- Loaded on demand by skills/setup/SKILL.md; part of /setup, split out to keep the always-loaded skill small. -->

When `userdata/profile.md` exists, iterate fields in the same order as the fresh
walk (Steps 1-8). The tier rubric is NOT offered — same reason it is not asked on
a fresh install (see the tier-rubric note after Step 8 in the skill). Step 0 does not apply — re-run never
re-reads the CV, because the fields it would fill are already populated.

Step 1 is ONE field here, not five. Show the whole facts line and take a single
keep / update / skip on it, mirroring the fresh-install shape. On `update`, apply
whichever value the user names and leave the others alone — never re-ask all five.

**Step 4 is offered, and it is positioning only.** Show the current `##
Positioning` paragraph and take one keep / update / skip on it like any other
field. On `update`, run Mode A against the user's new sentences.

Proof points and moat are NOT offered here, in either mode — `/setup` stopped
asking for them on a fresh install too, and `/today` picks them up once the user
has seen real roles. Skipping the whole of Step 4 was the actual behaviour until
2026-08-24, when manual check 1 caught the loop running 1 → 2 → 3 → 5 → 6 → 7 →
8; positioning is the one thing in a profile that people genuinely revise as a
search progresses, so silently never offering it was the wrong half to drop.

The rule below about freeform sections does not cover positioning: `##
Positioning` is a documented section that this skill writes, not one of the
user's own. That ambiguity is what produced the contradiction.

For each field:

1. Show the current value on one line, then ask:

   > "Currently: `<value>`. Keep, update, or skip?"

2. Read the answer as `keep`, `update`, or `skip` (skip means "leave as-is for now,
   ask again next /setup").
3. If `update`: prompt for the new value using the same conversational pattern —
   and in the same register — as that step's fresh-install ask.

Never overwrite a non-empty field with an empty answer in re-run mode. If the user updates a field but provides empty input, ask once more; if still empty, treat as `skip` and leave the current value.

The user's freeform body sections (`## Tone of Voice`, `## What NOT to Frame As`, and any `##` section they added below the documented ones) are NEVER touched in re-run mode — they belong to the user. `## Positioning`, `## Proof Points` and `## Moat` are not in this set: they are sections this skill authors. Positioning is offered per the rule above; the other two are left alone because nothing asks for them here, not because they are the user's to guard.
