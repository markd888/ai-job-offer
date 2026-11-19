// job-offer opt-in install counter.
// POST /v1/install {id: uuid4, version: semver}  -> stores the id once. No IP or UA is stored.
// GET  /v1/stats  (Authorization: Bearer STATS_TOKEN) -> {installs, by_version}

const UUID4 = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/;
const VERSION = /^\d{1,3}\.\d{1,3}\.\d{1,3}$|^unknown$/;

const json = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json" } });

export default {
  async fetch(request: Request, env: { DB: D1Database; STATS_TOKEN?: string }) {
    const url = new URL(request.url);

    if (request.method === "POST" && url.pathname === "/v1/install") {
      let body: any;
      try {
        body = await request.json();
      } catch {
        return json({ error: "bad json" }, 400);
      }
      const keys = Object.keys(body ?? {}).sort().join(",");
      if (keys !== "id,version" || !UUID4.test(body.id) || !VERSION.test(body.version)) {
        return json({ error: "expected {id: uuid4, version}" }, 400);
      }
      const day = new Date().toISOString().slice(0, 10);
      await env.DB.prepare("INSERT OR IGNORE INTO installs (id, first_version, first_seen) VALUES (?, ?, ?)")
        .bind(body.id, body.version, day)
        .run();
      return new Response(null, { status: 204 });
    }

    if (request.method === "GET" && url.pathname === "/v1/stats") {
      const auth = request.headers.get("authorization") || "";
      if (!env.STATS_TOKEN || auth !== `Bearer ${env.STATS_TOKEN}`) return json({ error: "unauthorized" }, 401);
      const total = await env.DB.prepare("SELECT COUNT(*) AS n FROM installs").first();
      const { results } = await env.DB.prepare(
        "SELECT first_version AS version, COUNT(*) AS n FROM installs GROUP BY first_version ORDER BY version"
      ).all();
      return json({ installs: total.n, by_version: results });
    }

    return json({ error: "not found" }, 404);
  },
};
