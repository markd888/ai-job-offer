#!/usr/bin/env python3
"""Opt-in anonymous install counter.

Nothing is sent unless the user said yes. When they did, one request goes out
per install: a random install ID generated here and the plugin version. No
name, email, profile, company or pipeline data, ever.

State lives in userdata/telemetry.json:
  {"consent": true|false, "install_id": "<uuid4>", "sent": "YYYY-MM-DD"|null, "asked": "YYYY-MM-DD"}

Commands:
  status    Print the state as JSON; "asked": false when the user was never asked.
  opt-in    Record consent (creates the install ID), then try to send.
  opt-out   Record refusal. Nothing is sent, now or later.
  ping      Send once if consented and not yet sent. Silent no-op otherwise.

Usage:
  python3 -I telemetry.py status  --userdata userdata
  python3 -I telemetry.py opt-in  --userdata userdata
  python3 -I telemetry.py opt-out --userdata userdata
  python3 -I telemetry.py ping    --userdata userdata

Off switches: "consent": false in telemetry.json, or JOB_OFFER_TELEMETRY=0.
JOB_OFFER_TELEMETRY_URL overrides the endpoint (tests, self-hosting).
A network failure is silent; the next ping retries.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
import uuid
from datetime import date
from pathlib import Path

ENDPOINT = "https://job-offer.mark-d.dev/v1/install"
PLUGIN_JSON = Path(__file__).resolve().parent.parent / ".claude-plugin" / "plugin.json"


def version() -> str:
    try:
        return json.loads(PLUGIN_JSON.read_text())["version"]
    except (OSError, ValueError, KeyError):
        return "unknown"


def load(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError):
        return None


def save(path: Path, state: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=2) + "\n")
    tmp.replace(path)


def disabled_by_env() -> bool:
    return os.environ.get("JOB_OFFER_TELEMETRY", "").strip().lower() in {"0", "false", "off", "no"}


def payload(state: dict) -> dict:
    """Exactly what leaves the machine."""
    return {"id": state["install_id"], "version": version()}


def ping(path: Path, today: str) -> str:
    state = load(path)
    if not state or state.get("consent") is not True:
        return "skipped: no consent"
    if disabled_by_env():
        return "skipped: JOB_OFFER_TELEMETRY=0"
    if state.get("sent"):
        return "skipped: already sent"
    url = os.environ.get("JOB_OFFER_TELEMETRY_URL", ENDPOINT)
    if not url:
        return "skipped: no endpoint"
    req = urllib.request.Request(url, data=json.dumps(payload(state)).encode(),
                                 headers={"Content-Type": "application/json",
                                          # Cloudflare rejects the default Python-urllib agent (error 1010)
                                          "User-Agent": f"job-offer-telemetry/{version()}"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=4) as r:
            if r.status >= 300:
                return f"failed: HTTP {r.status}"
    except Exception as e:  # network trouble never bothers the user
        return f"failed: {type(e).__name__}"
    state["sent"] = today
    save(path, state)
    return "sent"


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["status", "opt-in", "opt-out", "ping"])
    ap.add_argument("--userdata", type=Path, default=Path("userdata"))
    ap.add_argument("--today", default=date.today().isoformat())
    a = ap.parse_args(argv)
    path = a.userdata / "telemetry.json"
    state = load(path)

    if a.cmd == "status":
        print(json.dumps(state or {"asked": False}))
        return 0
    if a.cmd == "opt-out":
        save(path, {"consent": False, "asked": a.today})
        print("off")
        return 0
    if a.cmd == "opt-in":
        if not (state and state.get("consent") is True and state.get("install_id")):
            state = {"consent": True, "install_id": str(uuid.uuid4()), "sent": None, "asked": a.today}
            save(path, state)
    print(ping(path, a.today))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
