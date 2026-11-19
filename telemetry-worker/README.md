# job-offer telemetry worker

The server half of the opt-in install counter (`plugin/scripts/telemetry.py`). It stores one row per install that said yes: a random ID made on the user's machine, the plugin version, and the day. It stores no IP, no user agent and nothing else. Request logging (`observability`) is off.

- `POST /v1/install` with `{"id": "<uuid4>", "version": "0.8.1"}` → 204. Anything else → 400. Repeats are ignored.
- `GET /v1/stats` with `Authorization: Bearer $STATS_TOKEN` → `{"installs": N, "by_version": [...]}`.

## Deploy (cf CLI)

Live at `https://job-offer.mark-d.dev`. D1 `job-offer-telemetry` (EU jurisdiction). From this folder:

```sh
npm ci
npx cf d1 migrations apply <database id>       # schema in migrations/
npx cf deploy --secrets-file .secrets.json     # {"STATS_TOKEN": "..."}, gitignored
```

If `CF_API_TOKEN` / `CLOUDFLARE_API_TOKEN` is set without D1 and Workers rights, unset it so `cf` uses its OAuth login.

## Read the count

```sh
curl -s -H "Authorization: Bearer $STATS_TOKEN" https://job-offer.mark-d.dev/v1/stats
```
