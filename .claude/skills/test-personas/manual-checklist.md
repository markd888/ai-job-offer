# Manual release checks — no journey covers these

Run all four before tagging a release, after the 3 release-gate journeys
and the golden-set grade pass. Back up `userdata/` first (it is
gitignored): `cp -R userdata ~/job-offer-userdata-backup-$(date +%F)`.

## 1. /setup re-run mode (~2 min)

With an existing `userdata/profile.md`, run `/job-offer:setup`. It
must enter re-run mode, not fresh-install: current value shown one at a
time, keep / update / skip, Steps 1–8 in order. Confirm:

- it does NOT re-read the CV (Step 0 does not apply on re-run)
- it does NOT ask about companies of interest (that question lives in
  /job-search Phase 0 now)
- `keep` on everything changes no file under `userdata/` — verify with
  `diff -rq tests/snapshots/maya-active/ userdata/ --exclude=test-runs
  --exclude=examples`
- the workspace CLAUDE.md is re-resolved **only if it was plugin-generated**,
  i.e. it begins with the template's header comment. Against a hand-written one,
  `/setup` leaves it alone and says nothing, and that is a pass, not a miss
  (rule added 2026-08-23). Check which case your workspace is in before reading
  this line as a failure.
- freeform `## Tone of Voice` and `## What NOT to Frame As` sections
  survive untouched

Found a real self-contradiction on 2026-08-04 — this check earns its keep.

**Why 2 and 3 stay manual, and 1 and 4 need not.** Checks 1 and 4 act on
`userdata/`, so the harness can set them up: Phase 1 rsyncs a snapshot
there and the conversation loop does the rest. Checks 2 and 3 need a
`job-sweep/` tree — a sibling of `userdata/` at the workspace root — and
Phase 1 syncs exactly one snapshot into exactly one place. Every snapshot
is a `userdata/` tree, so nothing here can create the precondition. That
is a fixture-and-plumbing gap rather than an inherent one: a snapshot
carrying two trees plus a Phase 1 that knows where each goes would make
both automatable.

## 2. job-sweep → /setup handoff (~5 min)

Hand-build `job-sweep/profile.md` and `job-sweep/seen-roles.jsonl`
(two-three rows), run `/job-offer:setup`. Confirm both carry over
and the ledger append de-duplicates on `strict_key`.

## 3. CV dropped into job-sweep/ (~2 min)

Place a CV at `job-sweep/cv.md`, run `/job-sweep:sweep`. Confirm
extraction lands under `job-sweep/` and nothing is written to
`userdata/`. (The `cv-extraction.md` call site with zero journey
coverage — sweep-smoke deliberately takes the no-CV path.)

## 4. /setup CV-first path (~5 min)

The `cold-start-cv` journey that used to cover this was retired; the
`profile.md` schema check replaces only one of its twelve criteria, and
only partly. Cheap to run by hand — the `empty-with-cv` snapshot still
exists for it: copy its `cv.md` into a scratch `userdata/`, run
`/job-offer:setup` against it. Confirm:

- the CV is auto-detected without asking the user to drop one
- name, city and email are confirmed in a SINGLE message, not three
  separate questions (LinkedIn was dropped from `/setup` on 2026-08-23 —
  it is not asked here, and the timezone is derived from the city rather
  than confirmed, so neither should appear in this message)
- target titles and industries are each offered as a multi-select with
  an evidence line naming source material from the CV
- nothing in the written `profile.md` is absent from the CV and
  unconfirmed by the user — nothing was invented to fill a field
