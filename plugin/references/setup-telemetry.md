# Install counter — the consent question

<!-- Loaded on demand by skills/setup/SKILL.md (closing offers) and skills/today/SKILL.md (once, for installs that predate it). -->

The plugin keeps everything local. The one exception is an **opt-in** install count, so the author knows whether anyone uses it. It is never on without a yes.

## When to ask

Run `python3 -I ${CLAUDE_PLUGIN_ROOT}/scripts/telemetry.py status --userdata userdata`.

- `{"asked": false}` → ask (below), once.
- Anything else → the user already answered. Don't ask again, and say nothing. If `consent` is `true` and `sent` is empty, run `telemetry.py ping` silently (it retries a send that failed before).

## The question

One `AskUserQuestion`, nothing before or after it:

> "One last thing: may the plugin send a one-time anonymous install count? It's a random ID and the plugin version, nothing about you or your search. You can turn it off any time."

Options, in this order: **No, keep everything local** / **Yes, count my install**.

- No → `telemetry.py opt-out`. Reply with nothing extra.
- Yes → `telemetry.py opt-in`. Reply in one clause: `Thanks — counted once.` Don't mention a network failure; the next run retries silently.

## Exactly what is sent

`{"id": "<random uuid4 made on this machine>", "version": "<plugin version>"}`, once per install. No name, email, profile, CV, companies, journal or anything else from `userdata/`. The server stores no IP or user agent.

## Turning it off

Say "turn off the install count" → `telemetry.py opt-out`. Or set `JOB_OFFER_TELEMETRY=0`.
