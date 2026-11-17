# Test run — 2026-11-16

| Journey | Overall | Lint | Ground. | Conform. | Coher.* | Tone* |
|---|---|---|---|---|---|---|
| cold-start | FAIL (one-of-two) | PASS | PASS | FAIL (one-of-two) | PASS | FAIL |
| active-loop | FAIL (one-of-two) | PASS | PASS | FAIL (one-of-two) | PASS | PASS |
| application-to-interview | FAIL | FAIL (1) | PASS | PASS | PASS | FAIL (6) |

\* advisory — reported, never in the gate.

Run notes: first run after /today and /setup were split into on-demand references (#9), and the first run of `application-to-interview`. Maya's `maya-active` copies were rebased +15 weeks to the run date; the snapshots themselves were not changed. The run crossed midnight and paused twice on rate limits (resumed at the same turn). In this run the plugin agent could not schedule anything or keep the dashboard running, which shows in cold-start turns 15 and 20.

See per-journey `.judge.md` files for details.

## Files in this run

- maya-cold-start.md (transcript), maya-cold-start.judge.md (findings)
- maya-active-loop.md (transcript), maya-active-loop.judge.md (findings)
- maya-application-to-interview.md (transcript), maya-application-to-interview.judge.md (findings)

## Candidate memory entries

- **2026-11-16** — status-change confirmation omits the JD URL
  - Journey: cold-start (turn 19)
  - Surfaced in: this test run
  - Watch for: "Marked <Co> — <Role> as one to apply for" with no link, though every printed application row must carry it
- **2026-11-16** — /interview-prep closes without its own end-of-run nudge
  - Journey: active-loop (turn 8)
  - Surfaced in: this test run
  - Watch for: a closing that asks about the application instead of pointing to interview-analysis after the call
- **2026-11-16** — /apply tells the user to hand-edit profile.md
  - Journey: application-to-interview (turn 3)
  - Surfaced in: this test run
  - Watch for: "add a `phone:` line to profile.md" — offer to save it instead, and name no files
