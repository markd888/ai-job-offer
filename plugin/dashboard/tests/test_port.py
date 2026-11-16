"""The dashboard binds exactly the port it's given — never the next free one."""
from __future__ import annotations

from pathlib import Path

import pytest

from serve import build_server


def test_busy_port_is_an_error_not_a_drift(userdata: Path):
    first, port = build_server(userdata_root=userdata, preferred_port=0, dist_dir=None)
    try:
        with pytest.raises(RuntimeError, match=rf"port {port} is already in use"):
            build_server(userdata_root=userdata, preferred_port=port, dist_dir=None)
    finally:
        first.server_close()


def test_free_port_is_bound_as_given(userdata: Path):
    probe, port = build_server(userdata_root=userdata, preferred_port=0, dist_dir=None)
    probe.server_close()
    server, bound = build_server(userdata_root=userdata, preferred_port=port, dist_dir=None)
    try:
        assert bound == port
    finally:
        server.server_close()
