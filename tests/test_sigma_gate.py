"""Tests for src/separation_gate.py — G_σ organ separation gate.

Each test probes one σ predicate independently, plus conjunctive and seam-naming
assertions. Monkeypatch is used to inject violations without touching live files.

authority=false · non-sovereign · no ledger writes
"""
from __future__ import annotations

import ast
import json
import sys
import textwrap
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.separation_gate import (
    SigmaResult,
    _calls_name,
    _imports_module,
    run_gate,
    report,
    sigma1_triage_cannot_consume,
    sigma2_surface_cannot_mark,
    sigma3_proposer_neq_validator,
    sigma4_hal_neq_builder,
    sigma5_dreamt_neq_claimed,
    sigma6_render_neq_state,
)
import src.separation_gate as gate_mod


# ── σ₁: triage cannot consume ──────────────────────────────────────────────

def test_sigma1_passes_when_scanner_does_not_call_mark(monkeypatch, tmp_path):
    src = "def scan(): pass\n"
    f = tmp_path / "autoresearch_scanner.py"
    f.write_text(src)
    monkeypatch.setattr(gate_mod, "REPO", tmp_path.parent)
    # replicate the real path resolution REPO/temple/autoresearch/autoresearch_scanner.py
    (tmp_path.parent / "temple" / "autoresearch").mkdir(parents=True, exist_ok=True)
    (tmp_path.parent / "temple" / "autoresearch" / "autoresearch_scanner.py").write_text(src)
    monkeypatch.setattr(gate_mod, "REPO", tmp_path.parent)
    r = sigma1_triage_cannot_consume()
    assert r.passed


def test_sigma1_fails_when_scanner_calls_mark(monkeypatch, tmp_path):
    src = "def scan(): mark('x', 'acted', '')\n"
    (tmp_path / "temple" / "autoresearch").mkdir(parents=True, exist_ok=True)
    (tmp_path / "temple" / "autoresearch" / "autoresearch_scanner.py").write_text(src)
    monkeypatch.setattr(gate_mod, "REPO", tmp_path)
    r = sigma1_triage_cannot_consume()
    assert not r.passed
    assert "VIOLATION" in r.detail


# ── σ₂: surface cannot mark ────────────────────────────────────────────────

def test_sigma2_passes_when_builder_does_not_call_mark(monkeypatch, tmp_path):
    src = "def build(): return {}\n"
    (tmp_path / "apps" / "goblin-warren").mkdir(parents=True, exist_ok=True)
    (tmp_path / "apps" / "goblin-warren" / "build_warren_home.py").write_text(src)
    monkeypatch.setattr(gate_mod, "REPO", tmp_path)
    r = sigma2_surface_cannot_mark()
    assert r.passed


def test_sigma2_fails_when_builder_calls_mark(monkeypatch, tmp_path):
    src = "import operator_pen as pen\ndef build(): pen.mark(None, None, 'x', 'acted', '')\n"
    (tmp_path / "apps" / "goblin-warren").mkdir(parents=True, exist_ok=True)
    (tmp_path / "apps" / "goblin-warren" / "build_warren_home.py").write_text(src)
    monkeypatch.setattr(gate_mod, "REPO", tmp_path)
    r = sigma2_surface_cannot_mark()
    assert not r.passed
    assert "VIOLATION" in r.detail


# ── σ₃: proposer ≠ validator ───────────────────────────────────────────────

def test_sigma3_passes_when_builder_does_not_import_gate(monkeypatch, tmp_path):
    src = "import json\ndef build(): return {}\n"
    (tmp_path / "apps" / "goblin-warren").mkdir(parents=True, exist_ok=True)
    (tmp_path / "apps" / "goblin-warren" / "build_warren_home.py").write_text(src)
    monkeypatch.setattr(gate_mod, "REPO", tmp_path)
    r = sigma3_proposer_neq_validator()
    assert r.passed


def test_sigma3_fails_when_builder_imports_gate(monkeypatch, tmp_path):
    src = "import separation_gate\ndef build(): return {}\n"
    (tmp_path / "apps" / "goblin-warren").mkdir(parents=True, exist_ok=True)
    (tmp_path / "apps" / "goblin-warren" / "build_warren_home.py").write_text(src)
    monkeypatch.setattr(gate_mod, "REPO", tmp_path)
    r = sigma3_proposer_neq_validator()
    assert not r.passed
    assert "VIOLATION" in r.detail


# ── σ₄: hal ≠ builder ──────────────────────────────────────────────────────

def test_sigma4_passes_when_builder_does_not_call_gate_fns(monkeypatch, tmp_path):
    src = "def build(): return {}\n"
    (tmp_path / "apps" / "goblin-warren").mkdir(parents=True, exist_ok=True)
    (tmp_path / "apps" / "goblin-warren" / "build_warren_home.py").write_text(src)
    monkeypatch.setattr(gate_mod, "REPO", tmp_path)
    r = sigma4_hal_neq_builder()
    assert r.passed


def test_sigma4_fails_when_builder_calls_run_gate(monkeypatch, tmp_path):
    src = "def build(): run_gate()\n"
    (tmp_path / "apps" / "goblin-warren").mkdir(parents=True, exist_ok=True)
    (tmp_path / "apps" / "goblin-warren" / "build_warren_home.py").write_text(src)
    monkeypatch.setattr(gate_mod, "REPO", tmp_path)
    r = sigma4_hal_neq_builder()
    assert not r.passed
    assert "VIOLATION" in r.detail


# ── σ₅: dreamt ≠ claimed ───────────────────────────────────────────────────

def test_sigma5_passes_with_all_false_authority(monkeypatch, tmp_path):
    lines = [
        json.dumps({"authority": False, "decision": "acted"}),
        json.dumps({"authority": False, "decision": "rejected"}),
    ]
    log = tmp_path / "temple" / "autoresearch" / "consumption_log.ndjson"
    log.parent.mkdir(parents=True, exist_ok=True)
    log.write_text("\n".join(lines) + "\n")
    monkeypatch.setattr(gate_mod, "REPO", tmp_path)
    r = sigma5_dreamt_neq_claimed()
    assert r.passed


def test_sigma5_fails_when_entry_has_true_authority(monkeypatch, tmp_path):
    lines = [
        json.dumps({"authority": False, "decision": "acted"}),
        json.dumps({"authority": True, "decision": "acted"}),
    ]
    log = tmp_path / "temple" / "autoresearch" / "consumption_log.ndjson"
    log.parent.mkdir(parents=True, exist_ok=True)
    log.write_text("\n".join(lines) + "\n")
    monkeypatch.setattr(gate_mod, "REPO", tmp_path)
    r = sigma5_dreamt_neq_claimed()
    assert not r.passed
    assert "VIOLATION" in r.detail


def test_sigma5_vacuously_true_with_no_log(monkeypatch, tmp_path):
    (tmp_path / "temple" / "autoresearch").mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(gate_mod, "REPO", tmp_path)
    r = sigma5_dreamt_neq_claimed()
    assert r.passed
    assert "vacuously" in r.detail


# ── σ₆: render ≠ state ─────────────────────────────────────────────────────

def test_sigma6_passes_on_real_render_js():
    r = sigma6_render_neq_state()
    assert r.passed, r.detail


def test_sigma6_fails_when_render_js_claims_admission(monkeypatch, tmp_path):
    src = textwrap.dedent("""\
        import json
        def render_js(payload):
            return "window.WARREN_HOME = IS ADMITTED;\\n"
    """)
    (tmp_path / "apps" / "goblin-warren").mkdir(parents=True, exist_ok=True)
    (tmp_path / "apps" / "goblin-warren" / "build_warren_home.py").write_text(src)
    pen_dir = tmp_path / "temple" / "autoresearch"
    pen_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(gate_mod, "REPO", tmp_path)
    r = sigma6_render_neq_state()
    assert not r.passed
    assert "VIOLATION" in r.detail


# ── conjunctive: G_σ = all six ─────────────────────────────────────────────

def test_run_gate_passes_on_live_codebase():
    ok, results = run_gate()
    assert len(results) == 6
    assert ok, "\n" + report(results)


# ── seam naming: failing results name their seam ───────────────────────────

def test_failing_result_names_seam():
    failing = SigmaResult(name="σ₂", passed=False,
                          seam="build_warren_home.py ⊬ mark()",
                          detail="VIOLATION: test")
    text = report([failing])
    assert "build_warren_home.py ⊬ mark()" in text
    assert "FAIL seams:" in text
