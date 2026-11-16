# /today — weekly reflection

<!-- Loaded on demand by skills/today/SKILL.md; part of /today, split out to keep the always-loaded skill small. -->

**Weekly-reflection nudge (gated — TONE Rule C):**

After the daily brief has been written to `userdata/outputs/daily-brief-<date>.md`, check ALL of:

1. Is this the first `/today` run of the current ISO week? Determined by the marker file `userdata/outputs/.last-weekly-reflection` — if the file's ISO date is older than the current ISO week's Monday, this is the first run of this week.
   - If the file does not exist → condition met (first run of week).
   - If the file exists, read the single ISO date on the first line. If that date falls in a prior ISO week (compare ISO week numbers, not just day counts), condition met. Otherwise it does not.
   - "ISO week" = ISO-8601 week (Monday is day 1, Sunday is day 7). A Sunday belongs to the ISO week that STARTED on the preceding Monday — not the upcoming one. So `isoweek(Sunday)` equals `isoweek(the preceding Monday)`; the next Monday starts a new ISO week. Compare ISO week numbers, not raw day counts.
2. Are there at least one journal entry (`userdata/journal.md`) from the prior ISO week? If no, skip the nudge entirely — there's nothing to reflect on.

The run must also be non-ephemeral (the `--ephemeral` flag was NOT passed).

**If both yes:**

Use `AskUserQuestion` with **Yes, reflect** / **Skip**:

"It's the start of a new week. Want a 5-min reflection on last week? (y / skip)"

Above the question, print the channel mix in one line when there is one to show. Run `python3 -I "${CLAUDE_PLUGIN_ROOT}/scripts/funnel.py" --userdata "$(pwd)/userdata"`; if at least one channel other than `unknown` has 5+ applications, write one plain sentence from its output — the biggest channel and the best-converting one, counts with their rates, e.g. `Channel mix so far: 12 careers-site applications, none reached a screen; 6 referrals, 3 did (50%).` Otherwise print nothing about channels. Never a rate the script didn't print. This line is the once-a-week channel mention; the daily brief doesn't repeat it.

On **Yes, reflect** → invoke the `job-offer:career-coach` agent with mode hint `weekly-reflection`. The agent reads `journal.md` + `strategy.md`, runs 3-4 reflection prompts, and appends a `## Weekly reflection <YYYY-MM-DD>` block to `journal.md`. See `${CLAUDE_PLUGIN_ROOT}/agents/career-coach.md` for the mode's behaviour.
On **Skip** → do not invoke career-coach.

After the offer (whether accepted or declined), write today's ISO date to the marker file:

```bash
date +%Y-%m-%d > userdata/outputs/.last-weekly-reflection
```

This ensures the offer fires at most once per ISO week regardless of whether the user took it.

If marker write fails, print: "Couldn't write weekly-reflection marker — offer may repeat later this week." and continue.

The weekly reflection is invoked only by the user explicitly accepting the offer; /today never invokes career-coach silently.
