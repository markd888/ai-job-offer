// Cloudflare Worker for the read-only cloud copy of the dashboard.
//
// Every request — the SPA, the /data snapshots and /api/* — runs through this
// script first (run_worker_first: true in wrangler.jsonc), and nothing is served
// unless the request carries a valid Cloudflare Access token. The snapshot holds
// notes, briefs and interview debriefs, so the check fails closed:
//
//   ACCESS_TEAM_DOMAIN / ACCESS_AUD not set  -> 503, nothing served
//   no Cf-Access-Jwt-Assertion header        -> 403 (Access isn't in front of the Worker)
//   token with a bad signature/aud/iss/exp   -> 403
//
// Set both once as secrets (they survive every deploy):
//   npx wrangler secret put ACCESS_TEAM_DOMAIN   # https://<team>.cloudflareaccess.com
//   npx wrangler secret put ACCESS_AUD           # the Access application's AUD tag
//
// ctx.access isn't used: Workers with Static Assets don't receive it, so the
// token from the header is verified here (RS256 against the team's public keys).

const READ_ONLY = {
  error: "Read-only cloud copy. Change statuses and notes in Claude Code on the Mac.",
};

const JWKS_TTL_MS = 60 * 60 * 1000;
const CLOCK_SKEW_S = 60;
let jwksCache = { url: "", keys: [], fetchedAt: 0 };

function json(body, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json; charset=utf-8", "Cache-Control": "no-store" },
  });
}

function denied(status, reason) {
  return new Response(reason + "\n", {
    status,
    headers: { "Content-Type": "text/plain; charset=utf-8", "Cache-Control": "no-store" },
  });
}

function b64urlBytes(s) {
  const b64 = s.replace(/-/g, "+").replace(/_/g, "/").padEnd(Math.ceil(s.length / 4) * 4, "=");
  return Uint8Array.from(atob(b64), (c) => c.charCodeAt(0));
}

function b64urlJson(s) {
  return JSON.parse(new TextDecoder().decode(b64urlBytes(s)));
}

export function teamOrigin(domain) {
  const d = (domain || "").trim().replace(/\/+$/, "");
  if (!d) return "";
  return d.startsWith("https://") ? d : `https://${d}`;
}

async function signingKeys(team, { refresh = false } = {}) {
  const url = `${team}/cdn-cgi/access/certs`;
  const fresh = jwksCache.url === url && Date.now() - jwksCache.fetchedAt < JWKS_TTL_MS;
  if (fresh && !refresh) return jwksCache.keys;
  const res = await fetch(url);
  if (!res.ok) throw new Error(`certs fetch failed: ${res.status}`);
  const { keys = [] } = await res.json();
  jwksCache = { url, keys, fetchedAt: Date.now() };
  return keys;
}

// Returns the token's payload, or throws with the reason it was rejected.
export async function verifyAccessJwt(token, { team, aud, now = Date.now() / 1000 }) {
  const parts = token.split(".");
  if (parts.length !== 3) throw new Error("malformed token");
  const [h, p, sig] = parts;
  const header = b64urlJson(h);
  const payload = b64urlJson(p);
  if (header.alg !== "RS256") throw new Error(`unexpected alg ${header.alg}`);

  let jwk = (await signingKeys(team)).find((k) => k.kid === header.kid);
  if (!jwk) jwk = (await signingKeys(team, { refresh: true })).find((k) => k.kid === header.kid); // key rotation
  if (!jwk) throw new Error("unknown signing key");

  const key = await crypto.subtle.importKey(
    "jwk",
    { kty: jwk.kty, n: jwk.n, e: jwk.e, alg: "RS256", ext: true },
    { name: "RSASSA-PKCS1-v1_5", hash: "SHA-256" },
    false,
    ["verify"],
  );
  const ok = await crypto.subtle.verify(
    "RSASSA-PKCS1-v1_5", key, b64urlBytes(sig), new TextEncoder().encode(`${h}.${p}`),
  );
  if (!ok) throw new Error("bad signature");

  const auds = Array.isArray(payload.aud) ? payload.aud : [payload.aud];
  if (!auds.includes(aud)) throw new Error("wrong audience");
  if (payload.iss !== team) throw new Error("wrong issuer");
  if (typeof payload.exp !== "number" || payload.exp + CLOCK_SKEW_S < now) throw new Error("expired");
  if (typeof payload.nbf === "number" && payload.nbf - CLOCK_SKEW_S > now) throw new Error("not yet valid");
  return payload;
}

async function sha1Hex(text) {
  const digest = await crypto.subtle.digest("SHA-1", new TextEncoder().encode(text));
  return [...new Uint8Array(digest)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

async function asset(env, request, path) {
  const res = await env.ASSETS.fetch(new URL(path, request.url));
  return res.ok ? res.json() : null;
}

async function api(request, env, url) {
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
}

export default {
  async fetch(request, env) {
    const team = teamOrigin(env.ACCESS_TEAM_DOMAIN);
    const aud = (env.ACCESS_AUD || "").trim();
    if (!team || !aud) {
      return denied(503, "Access check not configured: set ACCESS_TEAM_DOMAIN and ACCESS_AUD (wrangler secret put).");
    }

    const token = request.headers.get("Cf-Access-Jwt-Assertion");
    if (!token) return denied(403, "Cloudflare Access is not in front of this Worker.");
    try {
      await verifyAccessJwt(token, { team, aud });
    } catch (err) {
      return denied(403, `Access token rejected: ${err.message}`);
    }

    const url = new URL(request.url);
    return url.pathname.startsWith("/api/") ? api(request, env, url) : env.ASSETS.fetch(request);
  },
};

// For tests only.
export function _resetJwksCache() {
  jwksCache = { url: "", keys: [], fetchedAt: 0 };
}
