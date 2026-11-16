# /today — smoke test against the Maya example

<!-- Maintainer reference for skills/today/SKILL.md; never needed at run time. -->

When debugging this skill, run it against `userdata/examples/maya/` as a synthetic install (treat that subdirectory as if it were the userdata/ root). Maya's snapshot has NO `userdata/integrations.md`. The brief is the 3-section shape (Today → Heads-up → Pipeline state) — there are no "Where you are" or "This week's progress" sections any more.

### Input phase against Maya

- Step 1 (window): Maya's journal currently opens with `## 2026-05-15`. If today is 2026-05-18 in the harness, gap = 3 days → print `Last entry was 3 days ago — pulling the full window.` (Update this assertion if the example install is refreshed with a different most-recent date.)
- Step 2 (inference): integrations.md absent → skipped silently. No items rendered.
- Step 3 (targeted confirms): skipped (step 2 produced nothing).
- Step 4 (open catch-all): single prompt printed. If the user replies with free text mentioning a company, that line should be parsed and routed; if they choose Skip, the input phase exits cleanly with no writes.
- Step 5 (write phase): only runs if the catch-all returned content. With no input from the user, journal.md is not touched and no `## 2026-05-18` heading is created.

To exercise the integration-fold-in code paths AND the targeted-confirms flow, create a temporary `userdata/examples/maya/integrations.md` with `## calendar` / `## gmail` sections wired, dispatch /today, and verify the input phase renders inferred deltas grouped by source.

### Output phase against Maya (after input phase)

With the catch-all skipped, the output phase against Maya's expanded install (8 status slots, Plaid multi-role, Lendable in `offer` status) should produce the 3-section brief:

- **Section 1 "Today"**: (4) Plaid prep — `last_inbound: 2026-05-13` is 5d ago, within 7d → fires. (5) iwoca — `date_applied: 2026-04-22`, no inbound, 26d quiet → `follow-ups.py` lists it under "Follow-up due" → `Follow up with iwoca — quiet 26d` fires. (6) Applications gap — 1/3 = 67% gap, fires. If today is Monday, the Monday warm-outreach batch nudge may also fire (count is at 3/5 — depends on weekend warm-outreach activity). No checkpoint trigger (next is 2026-06-15 = 28d out). No imminent-event or recruiter-reply bullets (no integrations).
- **Section 2 "Heads-up"**: no separate stale-applied bullet; the Follow-ups line leaves out iwoca, which Today already names. Shape-mismatch warning fires for Cleo (180 ppl, no equity signal — though strict reading of the trigger requires the company NOT to be in `target_industries`; Cleo's consumer-finance vertical is borderline against Maya's `fintech` / `consumer credit` targets — an LLM may interpret either way). Late-stage prompts fire for Plaid CC (active interview thread with recent inbound). Trigger A coach nudge may fire (applications cadence under 50% for 3 weeks running — depends on journal counts per week).
- **Section 3 "Pipeline state"**: counts only, no rows. `Active: 7 — 1 offer (Lendable), 2 interviewing, 2 applied, 2 to apply.` Multi-role Plaid contributes two to the counts (one interviewing, one to apply) but is not named, since neither group is a single company. Then the weekly line if targets are set, then `2 decided this search; 1 rejected, 1 not interested.` (Stripe rejected + Atom Bank not interested.) Then the dashboard pointer, since 7 > 3.

If the catch-all DOES return content (e.g. the user types `[Plaid] CPO round confirmed Thu` during step 4), verify that:
- journal.md gains a `## 2026-05-18` heading (if not already present today) with the bullet `- [Plaid] CPO round confirmed Thu (source: user)`.
- `userdata/examples/maya/companies/Plaid/consumer-credit/meta.md` is NOT modified by step 4 alone (free-text doesn't imply a structured field; only inferred + confirmed integration facts update meta.md per the contract).

### Weekly reflection trigger against Maya

- If today is Monday AND `userdata/examples/maya/outputs/.last-weekly-reflection` does not exist AND Maya's journal has entries from the prior ISO week → offer block prints after the brief.
- If today is Monday AND the marker file dates to the prior ISO week AND prior-week journal entries exist → offer block prints.
- If today is Tuesday AND the marker file dates to Monday (same ISO week) → offer block does NOT print.
- If today is Monday AND Maya's journal has NO entries from the prior ISO week → offer block does NOT print (TONE Rule C gate).
- On accept (`y`) → career-coach invoked with `weekly-reflection` mode; on skip → marker file updated, no agent invocation. In both cases, the marker file's content reads today's ISO date as the only line.

### Weekly reflection trigger notes (updated)

The weekly-reflection nudge fires only when BOTH conditions are met: first run of the ISO week AND prior-week journal entries exist. Maya's journal currently has entries from the prior ISO week, so the nudge will fire on the first Monday run.

If the output diverges materially from any of the above against the Maya snapshot, the skill has a bug — fix before promoting.
