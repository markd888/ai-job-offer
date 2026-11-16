# job-offer dashboard

React + Mantine SPA served by a Python stdlib HTTP server. Launched via the
`/dashboard` skill in the parent plugin.

- **Spec:** [docs/superpowers/specs/2026-05-18-dashboard-design.md](../../docs/superpowers/specs/2026-05-18-dashboard-design.md)
- **Rebuild:** `cd plugin/dashboard && npm install && npm run build` (then commit `dist/`)
- **Test (Python):** `python3 -m pytest -v`
- **Test (cloud Worker):** `node --test worker/index.test.mjs`
- **Run locally:** `python3 serve.py --userdata <path-to-userdata>`

Users do not need to run any of the above. The committed `dist/` bundle and
the stdlib-only Python server are everything required at install time.

## Read-only cloud copy (optional)

A snapshot of the role cards on Cloudflare Workers, for checking the pipeline
from a phone. It holds notes, briefs and debriefs, so the Worker refuses every
request — the page, the API and the raw `/data/*.json` — that doesn't carry a
valid Cloudflare Access token. Without the two settings below it serves nothing.

1. **Build** from your workspace (the folder that holds `userdata/`):
   `sh <plugin>/dashboard/scripts/build_cloud.sh` — or pass the path:
   `sh build_cloud.sh /path/to/userdata`.
2. **Deploy** from `plugin/dashboard/`: `npx wrangler deploy`.
3. **Put Access in front:** Workers & Pages → the Worker → Settings → Domains &
   Routes → *Enable Cloudflare Access* on `workers.dev`, and allow only your email.
4. **Tell the Worker what to check** (once; secrets survive deploys):
   ```sh
   npx wrangler secret put ACCESS_TEAM_DOMAIN   # https://<team>.cloudflareaccess.com
   npx wrangler secret put ACCESS_AUD           # Zero Trust → Access → Applications → the app → AUD tag
   ```
5. **Check:** in a private window the URL should send you to the Access login;
   `curl -i https://job-search-dashboard.<subdomain>.workers.dev/data/state.json`
   should return 302/403, never JSON.

Re-run steps 1–2 to refresh the snapshot. It's read-only: statuses and notes
change only through Claude Code on your machine.
