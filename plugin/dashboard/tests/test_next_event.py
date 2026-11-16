"""Tests for editing next_event (the card's "Next step") from the dashboard."""
from __future__ import annotations

import json
import threading
import urllib.request
from datetime import date
from pathlib import Path
from typing import Iterator

import pytest

from serve import build_server, normalize_next_event, parse_frontmatter, rewrite_next_event

TODAY = date(2026, 11, 6)
BASE = "---\ncompany: Acme\nstatus: interviewing\n---\n# Acme\n"


def test_adds_field_and_history_when_absent():
    out = rewrite_next_event(BASE, "Call with Myles", TODAY)
    fm, body = parse_frontmatter(out)
    assert fm["next_event"] == "Call with Myles"
    assert fm["status"] == "interviewing"
    assert '## History\n- 2026-11-06: next_event → "Call with Myles" (dashboard)' in body


def test_replaces_existing_value_and_appends_to_history():
    md = '---\ncompany: Acme\nnext_event: "old"\n---\n# Acme\n\n## History\n- 2026-11-01: x\n'
    out = rewrite_next_event(md, "new", TODAY)
    assert out.count("next_event:") == 1
    assert parse_frontmatter(out)[0]["next_event"] == "new"
    assert out.endswith('- 2026-11-01: x\n- 2026-11-06: next_event → "new" (dashboard)\n')


def test_newlines_become_steps_and_quotes_are_safe():
    assert normalize_next_event('Wait for "NDA"\n\nFollow up Fri ') == "Wait for 'NDA'; Follow up Fri"


def test_clear_writes_empty_value_and_history():
    md = '---\ncompany: Acme\nnext_event: "old"\n---\n# Acme\n'
    out = rewrite_next_event(md, "  ", TODAY)
    assert parse_frontmatter(out)[0]["next_event"] == ""
    assert "next_event cleared (dashboard)" in out


def test_unchanged_value_is_a_no_op():
    md = '---\ncompany: Acme\nnext_event: "same"\n---\n# Acme\n'
    assert rewrite_next_event(md, "same", TODAY) == md
    assert rewrite_next_event(BASE, "", TODAY) == BASE


def test_no_frontmatter_raises():
    with pytest.raises(ValueError):
        rewrite_next_event("# no frontmatter\n", "x", TODAY)


@pytest.fixture
def running_server(userdata: Path) -> Iterator[tuple[str, Path]]:
    server, port = build_server(userdata_root=userdata, preferred_port=0, dist_dir=None)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://localhost:{port}", userdata
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def _patch(url: str, body: dict) -> int:
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"}, method="PATCH")
    try:
        with urllib.request.urlopen(req) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code


def test_http_patch_writes_meta(running_server: tuple[str, Path]):
    base, root = running_server
    assert _patch(f"{base}/api/positions/Plaid/next_event", {"next_event": "Panel Fri\nSend thanks"}) == 200
    fm, _ = parse_frontmatter((root / "companies" / "Plaid" / "meta.md").read_text())
    assert fm["next_event"] == "Panel Fri; Send thanks"


def test_http_patch_rejects_bad_input(running_server: tuple[str, Path]):
    base, _ = running_server
    assert _patch(f"{base}/api/positions/Plaid/next_event", {}) == 400
    assert _patch(f"{base}/api/positions/Nope/next_event", {"next_event": "x"}) == 404
    assert _patch(f"{base}/api/positions/..%2F..%2Fetc/next_event", {"next_event": "x"}) == 400
