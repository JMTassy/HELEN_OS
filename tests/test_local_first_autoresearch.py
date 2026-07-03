"""Acceptance tests for tools/local_first_autoresearch.py (CHID-LF2-9c1b9af9 repair).

Stubbed HTTP layer — zero model calls. Verifies: failure classification (never
laundered into fake content), ANSI stripping before parse, think:false for qwen
only, and that the FABLE gate input uses the lawful one-bit assay prompt.
NON_SOVEREIGN · authority=false.
"""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))
import local_first_autoresearch as lf  # noqa: E402


class FakeResp:
    def __init__(self, payload):
        self._p = payload

    def read(self):
        return self._p

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def _opener(payload=None, exc=None, capture=None):
    def opener(req, timeout=None):
        if capture is not None:
            capture.update(json.loads(req.data.decode()))
        if exc:
            raise exc
        return FakeResp(payload)
    return opener


def test_strip_control_removes_ansi_and_c0():
    dirty = "Sandbox adapter\x1b[5D\x1b[K as membrane\x07\x00"
    assert lf.strip_control(dirty) == "Sandbox adapter as membrane"


def test_empty_response_classified(monkeypatch):
    monkeypatch.setattr("urllib.request.urlopen", _opener(json.dumps({"response": ""}).encode()))
    r = lf.call_ollama("qwen3.5:9b", "x")
    assert r["status"] == lf.FAILED_EMPTY_RESPONSE


def test_invalid_json_classified(monkeypatch):
    monkeypatch.setattr("urllib.request.urlopen", _opener(b"<<<not json>>>"))
    r = lf.call_ollama("gemma4-12b:latest", "x")
    assert r["status"] == lf.FAILED_INVALID_JSON


def test_timeout_classified(monkeypatch):
    monkeypatch.setattr("urllib.request.urlopen", _opener(exc=TimeoutError()))
    r = lf.call_ollama("qwen3.5:9b", "x")
    assert r["status"] == lf.FAILED_TIMEOUT


def test_no_fabricated_receipts_on_prose_output(monkeypatch):
    monkeypatch.setattr("urllib.request.urlopen",
                        _opener(json.dumps({"response": "no json, just prose"}).encode()))
    q = lf.qwen_compress(["idea one"], "topic")
    assert q["status"] == lf.FAILED_INVALID_JSON
    assert q["receipts"] == []


def test_no_fake_ideas_on_empty_gemma(monkeypatch):
    monkeypatch.setattr("urllib.request.urlopen", _opener(json.dumps({"response": ""}).encode()))
    g = lf.gemma_propose("topic", 5)
    assert g["status"] == lf.FAILED_EMPTY_RESPONSE
    assert g["ideas"] == []


def test_ansi_polluted_receipt_parses_clean(monkeypatch):
    receipt_line = ('{"schema": "CHIDDUSH_RECEIPT_V0", "chiddush_id": "CHID-T", '
                    '"invariant": "pattern: test invariant long enough", '
                    '"source_refs": ["x.py"], "authority": false, "claim": "NO_CLAIM"}'
                    "\x1b[6D\x1b[K")
    monkeypatch.setattr("urllib.request.urlopen",
                        _opener(json.dumps({"response": receipt_line}).encode()))
    q = lf.qwen_compress(["i"], "t")
    assert q["status"] == "OK"
    assert len(q["receipts"]) == 1


def test_fable_gate_uses_lawful_prompt():
    txt = lf.prepare_fable_min_gate({"chiddush_id": "CHID-T"}, "t")
    assert "collapse layer for JMT" not in txt  # unlawful extractor prompt banned


def test_think_false_for_qwen_only(monkeypatch):
    cap = {}
    monkeypatch.setattr("urllib.request.urlopen",
                        _opener(json.dumps({"response": "ok"}).encode(), capture=cap))
    lf.call_ollama("qwen3.5:9b", "x")
    assert cap.get("think") is False
    cap.clear()
    lf.call_ollama("gemma4-12b:latest", "x")
    assert "think" not in cap
