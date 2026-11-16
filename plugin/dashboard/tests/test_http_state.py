"""Tests for the HTTP layer — exercise the request handler via in-process invocation."""
from __future__ import annotations

import json
import threading
import urllib.request
from pathlib import Path
from typing import Iterator

import pytest

from serve import build_server


@pytest.fixture
def running_server(userdata: Path) -> Iterator[str]:
    """Start the server on a free port in a background thread; yield the base URL."""
    server, port = build_server(userdata_root=userdata, preferred_port=0, dist_dir=None)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://localhost:{port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def _get_json(url: str) -> dict:
    with urllib.request.urlopen(url) as r:
        return json.loads(r.read())


def test_state_endpoint_returns_companies(running_server: str):
    body = _get_json(f"{running_server}/api/state")
    companies = {p["company"] for p in body["companies"]}
    assert companies == {"Plaid", "Stripe"}


def test_state_endpoint_returns_strategy(running_server: str):
    body = _get_json(f"{running_server}/api/state")
    assert body["strategy"]["target_offer_date"] == "2026-06-28"
    assert body["strategy"]["weekly_targets"] == {"outreach": 7, "applications": 3}


def test_state_endpoint_returns_latest_brief(running_server: str):
    body = _get_json(f"{running_server}/api/state")
    assert body["latest_brief"]["date"] == "2026-05-18"


def test_state_endpoint_returns_null_brief_when_absent(running_server: str, userdata: Path):
    (userdata / "outputs" / "daily-brief-2026-05-18.md").unlink()
    body = _get_json(f"{running_server}/api/state")
    assert body["latest_brief"] is None


def test_state_endpoint_returns_userdata_root_absolute(running_server: str, userdata: Path):
    body = _get_json(f"{running_server}/api/state")
    assert body["userdata_root"] == str(userdata.resolve())


def test_state_endpoint_returns_weekly_progress_shape(running_server: str):
    body = _get_json(f"{running_server}/api/state")
    wp = body["weekly_progress"]
    assert set(wp.keys()) == {"warm_outreach", "feedback_requests", "applications", "window_days"}
    # window_days is days-into-the-current-ISO-week (Mon=1, Sun=7). Varies by
    # the real wall-clock day this test runs on.
    assert isinstance(wp["window_days"], int)
    assert 1 <= wp["window_days"] <= 7
    assert isinstance(wp["warm_outreach"], int)
    assert isinstance(wp["applications"], int)


def test_state_endpoint_returns_funnel_by_channel(running_server: str, userdata: Path):
    plaid = userdata / "companies" / "Plaid" / "meta.md"
    plaid.write_text(plaid.read_text().replace("status: interviewing", "status: interviewing\nchannel: referral", 1))
    body = _get_json(f"{running_server}/api/state")
    fbc = body["funnel_by_channel"]
    assert fbc["min_sample"] == 5
    referral = next(r for r in fbc["rows"] if r["channel"] == "referral")
    assert referral["applied"] == 1 and referral["screening"] == 1 and referral["small_sample"] is True
    plaid_record = next(c for c in body["companies"] if c["company"] == "Plaid")
    assert plaid_record["channel"] == "referral"

