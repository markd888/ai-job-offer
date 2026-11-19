"""plugin/scripts/telemetry.py — opt-in install counter.

Nothing may leave the machine without consent; what does leave is exactly an
install ID and the plugin version. A local HTTP server stands in for the worker.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

from scripts_helpers import SCRIPTS


class Sink(BaseHTTPRequestHandler):
    received: list = []
    agents: list = []
    status = 204

    def do_POST(self):  # noqa: N802
        n = int(self.headers.get("Content-Length", 0))
        Sink.received.append(json.loads(self.rfile.read(n)))
        Sink.agents.append(self.headers.get("User-Agent", ""))
        self.send_response(Sink.status)
        self.end_headers()

    def log_message(self, *a):
        pass


@pytest.fixture
def server():
    Sink.received, Sink.agents, Sink.status = [], [], 204
    srv = HTTPServer(("127.0.0.1", 0), Sink)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{srv.server_port}/v1/install"
    srv.shutdown()


def tel(userdata, *args, url="", env_extra=None):
    env = {**os.environ, "JOB_OFFER_TELEMETRY_URL": url, **(env_extra or {})}
    env.pop("JOB_OFFER_TELEMETRY", None) if not env_extra or "JOB_OFFER_TELEMETRY" not in env_extra else None
    r = subprocess.run([sys.executable, "-I", str(SCRIPTS / "telemetry.py"), *args, "--userdata", str(userdata),
                        "--today", "2026-11-19"], capture_output=True, text=True, env=env)
    assert r.returncode == 0, r.stderr
    return r.stdout.strip()


def state(userdata):
    return json.loads((userdata / "telemetry.json").read_text())


def test_never_asked_status(tmp_path):
    assert json.loads(tel(tmp_path, "status")) == {"asked": False}


def test_ping_without_consent_sends_nothing(tmp_path, server):
    assert tel(tmp_path, "ping", url=server) == "skipped: no consent"
    assert Sink.received == []


def test_opt_out_records_answer_and_never_sends(tmp_path, server):
    assert tel(tmp_path, "opt-out", url=server) == "off"
    assert tel(tmp_path, "ping", url=server) == "skipped: no consent"
    assert Sink.received == [] and state(tmp_path) == {"consent": False, "asked": "2026-11-19"}


def test_opt_in_sends_only_id_and_version_once(tmp_path, server):
    assert tel(tmp_path, "opt-in", url=server) == "sent"
    s = state(tmp_path)
    assert Sink.received == [{"id": s["install_id"], "version": Sink.received[0]["version"]}]
    assert set(Sink.received[0]) == {"id", "version"}
    assert s["sent"] == "2026-11-19"
    assert tel(tmp_path, "ping", url=server) == "skipped: already sent"
    assert tel(tmp_path, "opt-in", url=server) == "skipped: already sent"
    assert len(Sink.received) == 1


def test_env_off_switch_wins_over_consent(tmp_path, server):
    out = tel(tmp_path, "opt-in", url=server, env_extra={"JOB_OFFER_TELEMETRY": "0"})
    assert out == "skipped: JOB_OFFER_TELEMETRY=0" and Sink.received == []
    assert state(tmp_path)["consent"] is True and state(tmp_path)["sent"] is None


def test_network_failure_is_silent_and_retried(tmp_path, server):
    Sink.status = 500
    assert tel(tmp_path, "opt-in", url=server).startswith("failed")
    assert state(tmp_path)["sent"] is None
    Sink.status = 204
    assert tel(tmp_path, "ping", url=server) == "sent"


def test_unreachable_endpoint_is_silent(tmp_path):
    assert tel(tmp_path, "opt-in", url="http://127.0.0.1:9/v1/install").startswith("failed")


def test_no_endpoint_configured_is_a_noop(tmp_path):
    assert tel(tmp_path, "opt-in", url="") == "skipped: no endpoint"


def test_sends_own_user_agent(tmp_path, server):
    """Cloudflare blocks the default Python-urllib agent with error 1010."""
    tel(tmp_path, "opt-in", url=server)
    assert Sink.agents and Sink.agents[0].startswith("job-offer-telemetry/")
