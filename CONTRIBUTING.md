# Contributing to job-offer

Thanks for taking a look. This plugin is small enough that contribution is mostly: file an issue, propose a fix, send a PR.

## What this plugin is for

Senior PM / Head of Product job searches. The tier rubric, status pipeline, story shape, and reviewer agents are tuned for that target. Different role family (engineer, designer, marketer)? Fork it — the architecture is reusable, the defaults aren't.

## Install for development

Clone, install as a Claude Code plugin pointing at your local checkout:

```bash
git clone https://github.com/archugunov/pm-job-search.git
cd job-offer
```

Then in any Claude Code workspace, install from your local path:

```
/plugin install <path-to-clone>/plugin
```

Or install from the published GitHub:

```
/plugin marketplace add https://github.com/archugunov/pm-job-search.git
/plugin install job-offer@job-offer
```

When developing, you'll want to test changes against the example installs in `userdata/examples/maya/` (full) and `userdata/examples/diego/` (skeletal). Maya stress-tests the rich-pipeline case; Diego stress-tests the missing-files case.

## Developing

Run the plugin straight from your clone, in the folder where your real search
lives, so there is one copy of the code. A marketplace install is a second copy
in `~/.claude/plugins/cache/`, which is how a fix made in the clone ends up
missing from the dashboard you actually use.

1. **Clone once**, anywhere — these steps use `~/job-offer`:

   ```bash
   git clone <repo-url> ~/job-offer
   ```

2. **Turn the installed copy off for that search folder**, so its skills don't
   load next to the clone's (two `job-offer:today` skills, two dashboards):

   ```bash
   cd ~/my-search          # the folder that holds userdata/
   claude plugin disable job-offer@job-offer --scope local
   ```

   `--scope local` keeps the change in this folder only, so other workspaces
   keep using the released plugin.

3. **Start Claude Code with the clone loaded**:

   ```bash
   claude --plugin-dir ~/job-offer/plugin
   ```

   `${CLAUDE_PLUGIN_ROOT}` now points at `~/job-offer/plugin`, so every skill,
   script, reference and agent comes from the clone. An alias saves typing:
   `alias jo='claude --plugin-dir ~/job-offer/plugin'`.

4. **Edit, then re-run.** Skills, references and scripts are read when they're
   used, so a changed `SKILL.md` or script applies the next time you invoke it;
   start a new session if a change to a skill's `description:` or to an agent
   doesn't show up.

5. **The dashboard from the clone:**

   ```bash
   python3 ~/job-offer/plugin/dashboard/serve.py --userdata "$(pwd)/userdata" --port 7890
   ```

   After a change under `plugin/dashboard/src/`, run `npm run build` in
   `plugin/dashboard` and reload the page; commit `dist/` with the source (CI's
   verify-dist check fails otherwise).

6. **Mind the checked-out branch.** Your search runs on whatever the clone has
   checked out. Keep `main` checked out there and do feature work in a
   worktree (`git -C ~/job-offer worktree add ../job-offer-feat feat/x`); point
   `--plugin-dir` at the worktree only to try the branch on real data.

7. **Never run the test harness in your search folder.** `/test-personas`
   resets `userdata/` from a snapshot. Run it from the clone, where `userdata/`
   holds only the examples and test runs.

To go back to the released plugin: `claude plugin enable job-offer@job-offer
--scope local` and start Claude Code without `--plugin-dir`.
`claude plugin details job-offer` shows each component's projected token cost —
useful after touching an always-loaded skill like `/today` (kept at ≤ 20 KB by
`tests/test_skill_size.py`).

## Plugin shape

```
plugin/
├── .claude-plugin/
│   ├── plugin.json         # plugin manifest
│   └── marketplace.json    # marketplace manifest (lives at repo root, points at ./plugin)
├── skills/<name>/SKILL.md  # 13 user-facing skills
├── agents/<name>.md         # 6 agents
├── templates/               # profile / strategy / CLAUDE templates
├── TONE.md                  # voice + UX guidelines — read this before editing user-facing copy
└── README.md
```

Only `plugin/` installs. The maintainer test harness lives at
`.claude/skills/test-personas/`, outside it, because it needs the snapshots in
`tests/` and those never ship — it loads as a project skill for anyone working
in a clone, and is invisible to people who just install the plugin.

The TONE.md file is the most important thing to read before submitting any change that touches user-facing text. It locks in voice (casual yet professional, simple language, direct asks) and the low-effort-first UX principle (auto-detect before asking, skip-and-fill-later always, defaults > prompts).

## Privacy hard rule

This repo must contain **zero personal data**. The blocklist itself is personal data, so it never lives in the repo:

- **CI** reads it from the `PRIVACY_PATTERNS` repository secret (one regex per line, `#` comments allowed) and scans every tracked file on each push and PR via `.github/workflows/privacy-check.yml`. If the secret isn't set, the check fails rather than passing silently.
- **Locally**, keep the same list in `.privacy-patterns.local` at the repo root (gitignored) or point `PRIVACY_PATTERNS_FILE` at a file outside the repo, then run:

  ```bash
  make privacy-check
  ```

Update the list by editing your local file and re-uploading it: `gh secret set PRIVACY_PATTERNS < .privacy-patterns.local`. Keep terms specific enough not to hit the example data (`Stripe`, `Finom`, `N26`, `n8n` already appear in `userdata/examples/` and `tests/`); use `\b…\b` for short words.

`userdata/` is gitignored except `userdata/examples/`, so your own search data stays local while you use the plugin.

## Testing changes

Two example installs exist for testing: `userdata/examples/maya/` (full — profile + strategy + journal + 2 companies + 2 stories + applications.md) and `userdata/examples/diego/` (skeletal — profile + strategy + 1 company + 1 story, no journal). When changing a skill, mentally trace its behaviour against both:

- Maya covers: rich pipeline, multiple companies in different statuses, two stories with frontmatter, fully populated install
- Diego covers: missing journal, missing applications.md, only 1 story (tests the "<3 stories in bank" branch), no `monitoring: true` companies

For larger spec changes, consider running through one of the multi-step skills (`/job-offer:setup` end-to-end, or `/job-offer:interview-prep <Company>` end-to-end) mentally and writing out what each step would produce.

## Modifying the dashboard

The visual dashboard at `plugin/dashboard/` is a React + Mantine + Vite app. Its
built output (`plugin/dashboard/dist/`) is **committed** to this repo so plugin
users install zero JS dependencies. When you modify dashboard source, you MUST
rebuild and commit `dist/` in the same PR.

```bash
cd plugin/dashboard
npm install            # one-time per fresh checkout
npm run build          # produces dist/
cd ../..
git add plugin/dashboard/src/ plugin/dashboard/dist/
git commit -m "feat(dashboard): <what you changed>"
```

Contributors need Node 20+ (any modern LTS). The `dashboard-build-check` CI
workflow will fail if `dist/` is out of date relative to `src/`.

### Running the Python tests

```bash
cd plugin/dashboard
pip install -r requirements-dev.txt  # one-time, in a venv if you prefer
python3 -m pytest -v
```

### Running the dashboard locally

```bash
python3 plugin/dashboard/serve.py --userdata <path-to-userdata>
```

## Commit messages

Lower-case, verb-first, scope-prefixed where it helps. Examples from the repo:

- `add /interview-prep skill`
- `/today: collapse tier-rubric YAML wall into 3 clean options`
- `career-coach: refactor strategy-reflection around user complaints`
- `tone: drop superlatives from career-coach proposed reframes`

Co-authored-by lines are welcome but not required.

## Issues

File issues for:
- Bugs in skill behaviour (output diverges from the SKILL.md spec)
- Spec gaps surfaced during real use (the behaviour is undefined for case X)
- TONE.md violations in user-facing copy
- Privacy gaps (a blocklist term needs to be added)

Please don't file issues for:
- Feature requests outside the senior-PM scope (fork it instead)
- Requests to make an external tool a hard dependency. Integrations are opt-in only: `/integrations` wires Granola / Calendar / Gmail via MCP when you have them, and `plugin/INTEGRATIONS.md` documents Notion / Playwright / Slack as manual setup — every one degrades silently to markdown-only when absent. The pure-markdown core (read md, write md) is never allowed to depend on a live external service — see "Why pure markdown" in the README.

## License

MIT. Contributing code means you license your contribution under MIT. Author block stays generic ("job-offer contributors") rather than tracking individual contributors — fork attribution lives in git history.

### Shared files between the two plugins

Five files are used by both `job-offer` and `job-sweep`:
`references/cv-extraction.md`, `references/site-queries.md`,
`references/dedup-normalization.md`, `references/role-filters.md`, and `TONE.md`.

The single source of truth is under `plugin/`. `plugin-sweep/references/` holds
copies. **Never edit a file under `plugin-sweep/references/`** — edit the source
under `plugin/` and run:

```sh
make sync-sweep
```

CI runs `make check-sweep-sync` on every push and pull request and fails the build
if a copy has drifted. If that job fails, you edited a copy — move your change to
the source and re-sync.

One consequence worth knowing: because these files are shared, guidance in them
must hold for both plugins. A line that assumes a pipeline tracker, a maintainer
log, or a multi-skill flow will be wrong for `job-sweep`, which has none of those.
Write shared guidance conditionally, or keep it in a skill-private reference.

## Release checklist

1. The version bump in `plugin/.claude-plugin/plugin.json` and the CHANGELOG section land in the **same PR** as the release.
2. Before asking for a merge, check that the remote branch holds every commit: `git fetch && git log --oneline origin/main..origin/<branch>`, and that `gh pr view <n> --json commits` counts the same.
3. After the merge: tag `vX.Y.Z` on `main`, then update the plugin.
