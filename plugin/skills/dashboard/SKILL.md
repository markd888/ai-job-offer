---
name: dashboard
description: This skill should be used when the user asks to "/dashboard", "open the dashboard", "show me my pipeline visually", "launch the dashboard", or wants a browser-based view of their job-search pipeline. Launches a local Python server that serves a React + Mantine SPA reading from `userdata/companies/*/meta.md`, `userdata/strategy.md`, and the latest `userdata/outputs/daily-brief-*.md`. Supports inline status changes and timestamped notes per company. New positions are created via `/job-offer:evaluate-position <link>`, not from the dashboard itself. The dashboard reads and writes the same md files all other skills use — markdown remains the source of truth.
---

# /dashboard

Launches the job-offer visual dashboard.

## What it does

1. Reuses the dashboard already running on port 7890, or starts the local Python server (`plugin/dashboard/serve.py`) there.
2. Opens the user's default browser to `http://localhost:<port>`.
3. Prints the URL to chat so the user can copy it if auto-open fails.
4. Waits in the foreground until the user hits ctrl-C.

The dashboard provides:
- A top status bar showing pipeline counts, weekly progress vs `strategy.md` targets, and days-to-target-offer countdown.
- A grouped applications table (toggle Status / Tier) with inline status dropdowns; click any row to open the notes drawer.
- A bottom panel rendering the latest `daily-brief-*.md` (with a stale-brief banner when older than today).
- To add a new position: run `/job-offer:evaluate-position <link>` in Claude Code. The dashboard does not write new positions itself.

## When to invoke

- User types `/dashboard`.
- User asks to "open the dashboard", "show me my pipeline", "launch the visual view".
- User wants to do bulk pipeline maintenance (status sweeps, quick notes against several companies).

## How to invoke

The dashboard always lives at `http://localhost:7890`. First check whether it's already up:

```bash
curl -s -o /dev/null -w '%{http_code}' http://localhost:7890/api/state
```

- **200** → a dashboard is already serving this workspace. Don't start a second server; open `http://localhost:7890` in the browser and print the launch message.
- **Anything else** → start it in the background (it blocks until ctrl-C):

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/dashboard/serve.py" --userdata "$(pwd)/userdata" --port 7890
```

If port 7890 is taken by something that isn't the dashboard, say what holds it (`lsof -iTCP:7890 -sTCP:LISTEN`) and ask before stopping it; don't drift to another port.

`${CLAUDE_PLUGIN_ROOT}` resolves to the plugin install directory. `$(pwd)` resolves to the user's workspace root (the dir containing `userdata/`).

If the user is running this from somewhere other than their workspace root, ask for the workspace path and pass it explicitly: `--userdata <path>/userdata`.

## Failure modes and what to do

- **Bundle missing** (`error: dashboard bundle not found`). The plugin's `dist/` is not committed or got deleted. Tell the user to reinstall the plugin; this should not happen in a clean install.
- **Port busy** (`error: port 7890 is already in use`). The server never moves to another port. Re-run the `/api/state` check above: if it answers, the dashboard is already up — open it. If not, say what holds the port (`lsof -iTCP:7890 -sTCP:LISTEN`) and ask before stopping it.
- **userdata not found**. The user is in the wrong directory. Ask for the workspace path.

## What this skill does NOT do

- Does not modify md files itself — all writes go through the dashboard's REST API, which uses atomic file writes.
- Does not run `/today`, `/evaluate-position`, or any other skill. The dashboard renders the latest brief; it doesn't recompute it.
- Does not handle authentication, multi-user, or remote access. Local-only.
- Does not add Python dependencies. Server uses stdlib only.

## Launch message

When the server starts and the URL is known, print this to chat:

> Opening your job-search dashboard at http://localhost:<port> — you'll see every role you're tracking in one view. Change a status, add a note, or archive a role inline. To add a new role, drop the link to me here and I'll score and file it.

Where `<port>` is the actual port the server bound to (e.g. 7890). Print that line once.

Then add one context-aware next-step nudge per `${CLAUDE_PLUGIN_ROOT}/references/recommended-flow.md`, derived from what is actually in `userdata/companies/` — for example, unscored roles are worth `/evaluate-position`, a role you've decided to chase with no tailored CV yet is worth `/apply`. One line, naming the real companies. Skip it only if nothing in the pipeline suggests a next step.

Two constraints on that line. Name no files — "you'll need your CV first" says
everything "once you've got a master CV in `userdata/cv.md`" says. And do not
repeat a blocker the conversation has already raised: if an earlier turn has
already told the user their CV is missing, the nudge picks the next thing
instead. On 2026-08-22 the same CV prompt landed in three consecutive turns,
which reads as nagging rather than helping.

If the environment cannot hold a blocking foreground process, say so plainly in one line, give the user the command to run themselves, and still add the nudge — the launch failing is not a reason to end without one.

## In-chat update nudge — fire once per session

The first time per Claude Code session that the user posts a status change in chat (e.g. "mark Plaid to apply", "I rejected the Klarna offer"), append a one-line nudge after confirming the change:

> You can do this in the dashboard too, if you'd rather click than type.

"Once per session" means once per Claude Code conversation. Track via a transient in-memory flag set after the first nudge; do not persist to disk. Do not depend on whether the dashboard is currently running.

**Never justify the nudge by where the data lives.** The earlier wording ended
"— same data underneath", which answers a question nobody asked and tells the
user the two surfaces share storage, a fact that only matters to whoever built
it. The nudge earns its place by offering a faster way to do the thing they just
did; anything past that is plumbing. For the same reason, match the verb to what
actually happened — a status change is not "adding a note", and the 2026-08-22
run offered to add a note the user had never written.

**Confirm the change in the user's own words.** `Zilch — Director of Product is
now to_apply` echoes the stored value back at them; `Marked Zilch — Director of
Product as one to apply for` says the same thing in the language they used to
ask for it.

**Keep the posting link on the line.** The confirmation names an application,
so it carries that role's JD URL like every application row printed in chat:
`Marked Zilch — Director of Product as one to apply for — <link>`. Read `link:`
from the role's `meta.md`; if it is blank, leave the link off rather than
inventing one. The user is about to act on that role, and the link is the
thing they will want next.

(Note: this nudge fires from whatever skill or context handles the status change — typically `/today` or a free-text exchange — because this file is dashboard promotion context, not a separate skill.)

## Tone

Match plugin/TONE.md: low-effort, terse, no marketing voice.
