"""Regression: empty or failed inference must not be success:true.

Bug: query_auto() returned {"success": True, "response": ""} when the
inference layer produced an empty string.  The response shape was
structurally valid but semantically a lie — the client sees "success"
when no useful inference occurred.

Fix: empty response → 503 + success:false + failure_code:empty_inference_response.

Doctrine: HTTP 200 ⊬ truth / success:true ⊬ semantic success.
"""
from __future__ import annotations

import time
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import helen_api_server_v1 as server

if server.helen is None:
    server.initialize()

client = server.app.test_client()


def _patch_query(fn):
    orig = server.helen.query
    server.helen.query = fn
    try:
        yield
    finally:
        server.helen.query = orig


def test_empty_inference_returns_503_not_success() -> None:
    orig = server.helen.query
    server.helen.query = lambda *a, **kw: ""
    try:
        resp = client.post("/query", json={"prompt": "test"})
        body = resp.get_json()
        assert resp.status_code != 200 or body.get("success") is not True, (
            f"Empty inference must not be success:true (got status={resp.status_code}, success={body.get('success')})"
        )
        assert body.get("failure_code") == "empty_inference_response", (
            f"Empty inference must set failure_code=empty_inference_response, got {body.get('failure_code')!r}"
        )
    finally:
        server.helen.query = orig


def test_empty_inference_is_5xx() -> None:
    orig = server.helen.query
    server.helen.query = lambda *a, **kw: ""
    try:
        resp = client.post("/query", json={"prompt": "test"})
        assert resp.status_code in {503, 500}, (
            f"Empty inference should be 503, got {resp.status_code}"
        )
    finally:
        server.helen.query = orig


def test_whitespace_only_inference_is_rejected() -> None:
    orig = server.helen.query
    server.helen.query = lambda *a, **kw: "   \n\t  "
    try:
        resp = client.post("/query", json={"prompt": "test"})
        body = resp.get_json()
        assert body.get("success") is not True, (
            "Whitespace-only inference must not be success:true"
        )
    finally:
        server.helen.query = orig


def test_valid_inference_still_returns_200_success() -> None:
    orig = server.helen.query
    server.helen.query = lambda *a, **kw: "This is a valid response."
    try:
        resp = client.post("/query", json={"prompt": "test"})
        body = resp.get_json()
        assert resp.status_code == 200 and body.get("success") is True, (
            f"Valid inference must still return success:true, got status={resp.status_code}"
        )
    finally:
        server.helen.query = orig


def test_empty_inference_latency_under_50ms() -> None:
    orig = server.helen.query
    server.helen.query = lambda *a, **kw: ""
    try:
        start = time.perf_counter()
        client.post("/query", json={"prompt": "test"})
        elapsed_ms = (time.perf_counter() - start) * 1000
        assert elapsed_ms < 50, f"Empty-inference rejection must respond in <50 ms, took {elapsed_ms:.1f} ms"
    finally:
        server.helen.query = orig
