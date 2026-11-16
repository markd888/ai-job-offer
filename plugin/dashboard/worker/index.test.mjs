// node --test plugin/dashboard/worker/
// The Access gate in front of the cloud copy: it has to fail closed.
import assert from "node:assert/strict";
import { beforeEach, test } from "node:test";

import worker, { _resetJwksCache, teamOrigin } from "./index.js";

const TEAM = "https://acme.cloudflareaccess.com";
const AUD = "aud-tag-123";
const ENV_OK = { ACCESS_TEAM_DOMAIN: TEAM, ACCESS_AUD: AUD };

const b64url = (bytes) => Buffer.from(bytes).toString("base64url");
const enc = (obj) => b64url(new TextEncoder().encode(JSON.stringify(obj)));

async function keypair(kid) {
  const kp = await crypto.subtle.generateKey(
    { name: "RSASSA-PKCS1-v1_5", modulusLength: 2048, publicExponent: new Uint8Array([1, 0, 1]), hash: "SHA-256" },
    true, ["sign", "verify"],
  );
  const pub = await crypto.subtle.exportKey("jwk", kp.publicKey);
  return { kid, privateKey: kp.privateKey, jwk: { kid, kty: "RSA", alg: "RS256", use: "sig", n: pub.n, e: pub.e } };
}

const signer = await keypair("k1");
const stranger = await keypair("k1"); // same kid, different key: a forged token

async function token(claims = {}, { key = signer, header = {} } = {}) {
  const now = Math.floor(Date.now() / 1000);
  const h = enc({ alg: "RS256", kid: key.kid, typ: "JWT", ...header });
  const p = enc({ aud: [AUD], iss: TEAM, exp: now + 600, iat: now, email: "mark@example.com", ...claims });
  const sig = await crypto.subtle.sign("RSASSA-PKCS1-v1_5", key.privateKey, new TextEncoder().encode(`${h}.${p}`));
  return `${h}.${p}.${b64url(new Uint8Array(sig))}`;
}

let certFetches;
let served;
const assets = {
  async fetch(req) {
    const url = new URL(req.url ?? req);
    served.push(url.pathname);
    if (url.pathname === "/data/state.json") return Response.json({ companies: [] });
    return new Response("<html>spa</html>", { headers: { "Content-Type": "text/html" } });
  },
};

beforeEach(() => {
  _resetJwksCache();
  certFetches = 0;
  served = [];
  globalThis.fetch = async (url) => {
    assert.equal(String(url), `${TEAM}/cdn-cgi/access/certs`);
    certFetches += 1;
    return Response.json({ keys: [signer.jwk] });
  };
});

async function get(path, { jwt, env = ENV_OK, method = "GET" } = {}) {
  const headers = jwt ? { "Cf-Access-Jwt-Assertion": jwt } : {};
  return worker.fetch(new Request(`https://dash.example.workers.dev${path}`, { method, headers }), { ...env, ASSETS: assets });
}

test("not configured: nothing is served", async () => {
  for (const env of [{}, { ACCESS_TEAM_DOMAIN: TEAM }, { ACCESS_AUD: AUD }]) {
    const res = await get("/data/state.json", { jwt: await token(), env });
    assert.equal(res.status, 503);
  }
  assert.deepEqual(served, []);
});

test("no Access token: 403 for the SPA, the raw snapshot and the API", async () => {
  for (const path of ["/", "/data/state.json", "/data/positions/abc.json", "/api/state"]) {
    assert.equal((await get(path)).status, 403, path);
  }
  assert.deepEqual(served, []);
});

test("valid token: SPA and API are served", async () => {
  const jwt = await token();
  const spa = await get("/", { jwt });
  assert.equal(spa.status, 200);
  assert.match(await spa.text(), /spa/);
  const state = await get("/api/state", { jwt });
  assert.equal(state.status, 200);
  assert.deepEqual(await state.json(), { companies: [] });
  assert.equal(certFetches, 1, "signing keys are cached between requests");
});

test("writes stay read-only even with a valid token", async () => {
  const res = await get("/api/positions/x/notes", { jwt: await token(), method: "POST" });
  assert.equal(res.status, 403);
  assert.match((await res.json()).error, /Read-only/);
});

const rejected = {
  "forged signature": () => token({}, { key: stranger }),
  "wrong audience": () => token({ aud: ["someone-else"] }),
  "wrong issuer": () => token({ iss: "https://evil.cloudflareaccess.com" }),
  "expired": () => token({ exp: Math.floor(Date.now() / 1000) - 3600 }),
  "not yet valid": () => token({ nbf: Math.floor(Date.now() / 1000) + 3600 }),
  "alg none": async () => {
    const [, p] = (await token()).split(".");
    return `${enc({ alg: "none", kid: "k1" })}.${p}.`;
  },
  "unknown kid": () => token({}, { header: { kid: "k9" } }),
  "garbage": async () => "not-a-jwt",
};

for (const [name, make] of Object.entries(rejected)) {
  test(`rejects: ${name}`, async () => {
    const res = await get("/data/state.json", { jwt: await make() });
    assert.equal(res.status, 403);
    assert.deepEqual(served, []);
  });
}

test("aud may be a plain string", async () => {
  assert.equal((await get("/api/state", { jwt: await token({ aud: AUD }) })).status, 200);
});

test("unknown kid refetches the keys once (rotation)", async () => {
  const rotated = await keypair("k2");
  let calls = 0;
  globalThis.fetch = async () => {
    calls += 1;
    return Response.json({ keys: calls === 1 ? [signer.jwk] : [signer.jwk, rotated.jwk] });
  };
  assert.equal((await get("/api/state", { jwt: await token() })).status, 200);
  assert.equal((await get("/api/state", { jwt: await token({}, { key: rotated }) })).status, 200);
  assert.equal(calls, 2);
});

test("team domain is normalised", () => {
  assert.equal(teamOrigin("acme.cloudflareaccess.com"), TEAM);
  assert.equal(teamOrigin(`${TEAM}/`), TEAM);
  assert.equal(teamOrigin("  "), "");
});
