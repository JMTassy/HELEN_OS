"""The seven fixture laws for the CORE_V1 projection itself — plus the
spine's own size discipline. A constitution that cannot fail these
fixtures is prose; this one is executable.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from core_v1 import (
    INVARIANTS,
    MODULES,
    RUNTIME_TRANSITION,
    STATUSES,
    Ledger,
    MemorySnapshot,
    ReceiptCandidate,
    RegistryEntry,
    RenderArtifact,
    RuntimeReport,
    WitnessReceipt,
    admission_gate,
    canon,
    live_claim,
    project_entry,
    promote,
    replay,
    trust_state,
    validate_transition_declaration,
)

W_OK = WitnessReceipt("w1", independent=True,
                      raw_harness_ref="harness://run-001", frame_id="F1")
W_PRODUCER = WitnessReceipt("w2", independent=False,
                            raw_harness_ref="harness://self", frame_id="F1")


# ── 1. candidate ↛ stable ─────────────────────────────────────────────────

def test_candidate_cannot_appear_as_stable():
    lease_algebra = RegistryEntry("REG-LEASE", "capability lease algebra kappa_L",
                                  "execution_gateway", "hypothesis",
                                  historical_refs=("lease investigation, this session",))
    p = project_entry(lease_algebra)
    assert p["display_status"] == "hypothesis"
    assert p["proven"] is False
    # And no amount of prose changes it: an entry STAMPED fixture_green
    # without a witness is demoted on display, never shown proven.
    fake = RegistryEntry("REG-FAKE", "claimed-green thing", "kernel",
                         "fixture_green")   # no evidence
    pf = project_entry(fake)
    assert "DEMOTED" in pf["display_status"] and pf["proven"] is False


# ── 2. reported ↛ proven ──────────────────────────────────────────────────

def test_reported_cannot_appear_as_proven():
    e = RegistryEntry("REG-R", "reported implementation", "kernel", "reported")
    assert project_entry(e)["proven"] is False


# ── 3. render ↛ admission ─────────────────────────────────────────────────

def test_render_cannot_produce_admission():
    beautiful = RenderArtifact("cockpit", "<svg>a very convincing green</svg>")
    r = admission_gate(beautiful)
    assert r["verdict"] == "REJECT" and r["reason"] == "E_RENDER_IS_NOT_A_DOOR"


# ── 4. memory ↛ replay ────────────────────────────────────────────────────

def test_memory_cannot_replace_replay():
    ledger = Ledger((({"k": "GENESIS"}), ({"k": "EVENT", "n": 1})))
    assert trust_state(ledger)["basis"] == "REPLAY"
    memory = MemorySnapshot(claimed_state=replay(ledger))  # even a CORRECT recall
    r = trust_state(memory)
    assert r["basis"] == "REFUSED" and r["reason"] == "E_MEMORY_IS_NOT_LEDGER"


# ── 5. missing contradiction → HOLD ──────────────────────────────────────

def test_missing_contradiction_forces_hold():
    c = ReceiptCandidate("claim", witness=W_OK, contradictions_searched=False)
    r = admission_gate(c)
    assert r["verdict"] == "HOLD" and r["reason"] == "E_CONTRADICTION_UNSEARCHED"
    open_c = ReceiptCandidate("claim", witness=W_OK, contradictions_searched=True,
                              contradictions_found=("counterexample-1",),
                              contradictions_resolved=False)
    assert admission_gate(open_c)["reason"] == "E_CONTRADICTION_OPEN"
    clean = ReceiptCandidate("claim", witness=W_OK, contradictions_searched=True)
    assert admission_gate(clean)["verdict"] == "ELIGIBLE"   # recommends only


# ── 6. missing witness → no promotion ────────────────────────────────────

def test_missing_witness_prevents_promotion():
    e = RegistryEntry("REG-P", "candidate law", "governance", "reported")
    with pytest.raises(ValueError, match="E_NO_WITNESS"):
        promote(e, None)
    with pytest.raises(ValueError, match="E_PRODUCER_ADJACENT_WITNESS"):
        promote(e, W_PRODUCER)
    e2 = promote(e, W_OK)
    assert e2.status == "fixture_green"      # exactly one rung, witness attached
    # And the gate holds unwitnessed candidates too:
    r = admission_gate(ReceiptCandidate("x", witness=None,
                                        contradictions_searched=True))
    assert r["verdict"] == "HOLD" and r["reason"] == "E_NO_INDEPENDENT_WITNESS"


# ── 7. stale runtime report ↛ live state ─────────────────────────────────

def test_stale_report_cannot_become_live_state():
    old = RuntimeReport("dispatcher running on :8080", observed_frame="F0")
    r = live_claim(old, current_frame="F1")
    assert r["verdict"] == "STALE_REPORT" and r["reason"] == "E_NO_LIVE_PROBE"
    probe = WitnessReceipt("probe", True, "harness://probe-now", frame_id="F1")
    assert live_claim(old, "F1", probe)["verdict"] == "LIVE"


# ── the spine's own discipline ───────────────────────────────────────────

def test_exactly_twelve_invariants_and_eight_modules():
    assert len(INVARIANTS) == 12          # a 13th requires pruning, by test
    assert len(MODULES) == 8
    assert len(STATUSES) == 6             # the mandated ladder, no extras


def test_every_arrow_must_declare():
    ok, _ = validate_transition_declaration({
        "input_provenance": "raw_result", "preserved_invariants": ["I02"],
        "tolerated_loss": "none", "effect_ceiling": "read_only",
        "authority_requirements": "none", "witness_requirements": "independent",
        "failure_rollback": "discard"})
    assert ok
    bad, reason = validate_transition_declaration({"input_provenance": "x"})
    assert not bad and "E_UNDECLARED_ARROW" in reason
    assert len(RUNTIME_TRANSITION) == 16 and RUNTIME_TRANSITION[-1] == "shell_projection"


def test_untyped_status_rejected():
    with pytest.raises(ValueError, match="E_UNTYPED_STATUS"):
        RegistryEntry("REG-X", "vague thing", "kernel", "proven-ish")


def test_deterministic():
    e = RegistryEntry("REG-D", "d", "kernel", "hypothesis")
    assert canon(project_entry(e)) == canon(project_entry(e))
