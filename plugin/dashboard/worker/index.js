// Cloudflare Worker for the read-only cloud copy of the dashboard.
// Static assets (the built SPA plus data/ from scripts/export_cloud.py) are served
// by the assets binding; this script only answers /api/* with those snapshots.

const READ_ONLY = {
  error: "Read-only cloud copy. Change statuses and notes in Claude Code on the Mac.",
};

function json(body, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json; charset=utf-8", "Cache-Control": "no-store" },
  });
}

async function sha1Hex(text) {
  const digest = await crypto.subtle.digest("SHA-1", new TextEncoder().encode(text));
  return [...new Uint8Array(digest)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

async function asset(env, request, path) {
  const res = await env.ASSETS.fetch(new URL(path, request.url));
  return res.ok ? res.json() : null;
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (!url.pathname.startsWith("/api/")) return env.ASSETS.fetch(request);
    if (request.method !== "GET") return json(READ_ONLY, 403);

    if (url.pathname === "/api/state") {
      const state = await asset(env, request, "/data/state.json");
      return state ? json(state) : json({ error: "No snapshot deployed yet." }, 503);
    }

    // /api/positions/<encoded folder_path>/(notes|artifacts)
    const m = url.pathname.match(/^\/api\/positions\/(.+)\/(notes|artifacts)$/);
    if (m) {
      const key = await sha1Hex(decodeURIComponent(m[1]));
      const payload = await asset(env, request, `/data/positions/${key}.json`);
      if (!payload) return json({ error: "position not found" }, 404);
      return json(m[2] === "notes" ? payload.notes : payload.artifacts);
    }
    return json({ error: "not found" }, 404);
  },
};
