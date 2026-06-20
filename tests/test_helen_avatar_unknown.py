"""Regression: unknown avatar name must not leak into current_avatar state.

Bug: switch_avatar() accepted any name string, set current_avatar to the
unknown key, and returned it in the response even though the avatar object
fell back silently to helen.  The response avatar key was then inconsistent
with every key in the registry.

Fix: return 404 when the requested avatar name is not in AvatarRegistry.AVATARS.
"""
from __future__ import annotations

import time
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import helen_api_server_v1 as server
from helen_test_avatar_v1 import AvatarRegistry

if server.helen is None:
    server.initialize()

client = server.app.test_client()


def test_unknown_avatar_returns_404() -> None:
    resp = client.post("/avatar/unknown_xyz_does_not_exist")
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}"
    body = resp.get_json()
    assert "error" in body, "404 response must include an error field"
    assert "available" in body, "404 response must include available avatars"


def test_unknown_avatar_does_not_corrupt_current_avatar() -> None:
    client.post("/avatar/helen")
    client.post("/avatar/unknown_xyz_does_not_exist")
    status_resp = client.get("/status")
    assert status_resp.status_code == 200
    body = status_resp.get_json()
    known_keys = set(AvatarRegistry.AVATARS.keys())
    assert body.get("avatar") in known_keys, (
        f"current_avatar should remain a known key after failed switch, got {body.get('avatar')!r}"
    )


def test_known_avatars_still_switch_correctly() -> None:
    for key in AvatarRegistry.AVATARS:
        resp = client.post(f"/avatar/{key}")
        assert resp.status_code == 200, f"Switching to known avatar {key!r} should return 200"
        body = resp.get_json()
        assert body.get("avatar") == key, f"Response avatar key should be {key!r}"


def test_unknown_avatar_latency_under_50ms() -> None:
    start = time.perf_counter()
    client.post("/avatar/latency_test_unknown_xyz")
    elapsed_ms = (time.perf_counter() - start) * 1000
    assert elapsed_ms < 50, f"Unknown avatar rejection must respond in <50 ms, took {elapsed_ms:.1f} ms"
