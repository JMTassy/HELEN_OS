"""
Tests for REALITY_COUPLING_WITNESS_V1 (tools/reality_coupling_probe.py).

Acceptance criteria (CTO Guide V1.1 Phase 2):
  - clean repaired ledger          → COUPLED
  - sovereign file modification    → HARD_DRIFT / SOVEREIGN_FILE_DIRTY
  - uncorrected duplicate seq      → HARD_DRIFT / UNANCHORED_DANGLING
  - anchored duplicate (correction)→ COUPLED (not HARD_DRIFT)
  - skill hash mismatch            → HARD_DRIFT / SKILL_HASH_MISMATCH
  - skill missing on disk          → HARD_DRIFT / SKILL_MISSING_ON_DISK
  - chain break                    → HARD_DRIFT / CHAIN_BREAK
"""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Dict
from unittest.mock import patch

import pytest

from tools.reality_coupling_probe import (
    STATUS_COUPLED, STATUS_HARD_DRIFT, STATUS_SOFT_DRIFT,
    _compute_delta, _probe_runtime, _replay_trust, probe,
    RTrust, RRuntime, DriftEvent,
)

# ── Helpers ─────────────────────────────────────────────────────────────────

def _make_entry(seq: int, ev_type: str, payload: dict, prev_cum: str) -> dict:
    ph = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    cum = hashlib.sha256((prev_cum + ph).encode()).hexdigest()
    return {
        "type": ev_type, "seq": seq, "payload": payload, "meta": {},
        "payload_hash": ph, "prev_cum_hash": prev_cum, "cum_hash": cum,
    }


def _write_ledger(path: str, entries: list[dict]):
    with open(path, "w", encoding="utf-8") as f:
        for ev in entries:
            f.write(json.dumps(ev) + "\n")


def _clean_chain(n: int = 5) -> list[dict]:
    entries = []
    prev = "0" * 64
    for i in range(n):
        ev = _make_entry(i, "turn", {"i": i}, prev)
        entries.append(ev)
        prev = ev["cum_hash"]
    return entries


def _promotion_entry(seq: int, skill_id: str, skill_hash: str, prev_cum: str) -> dict:
    payload = {
        "schema_name": "SKILL_PROMOTION_DECISION_V1",
        "schema_version": "1.0.0",
        "decision_id": f"DEC_{skill_id}_{seq}",
        "skill_id": skill_id,
        "candidate_version": "V1",
        "decision_type": "ADMITTED",
        "reason_code": "OK_ADMITTED",
        "candidate_identity_hash": skill_hash,
        "sovereign_promotion": True,
        "receipt_id": f"R-TEST-{seq}",
    }
    ph = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    # Use HELEN_CUM_V1 scheme (matches NDJSONWriter)
    cum = hashlib.sha256(
        b"HELEN_CUM_V1" + bytes.fromhex(prev_cum) + bytes.fromhex(ph)
    ).hexdigest()
    return {
        "type": "SKILL_PROMOTION_DECISION_V1",
        "seq": seq, "payload": payload, "meta": {},
        "payload_hash": ph, "prev_cum_hash": prev_cum, "cum_hash": cum,
    }


def _correction_entry(seq: int, dangling_cum: str, dangling_seq: int, prev_cum: str) -> dict:
    payload = {
        "schema_name": "LEDGER_SEQ_CORRECTION_V1",
        "schema_version": "1.0.0",
        "correction_id": f"CORRECTION_{dangling_seq}_{seq}",
        "correction_type": "ANCHOR_DANGLING_ENTRY",
        "dangling_seq": dangling_seq,
        "dangling_cum_hash": dangling_cum,
        "dangling_decision_id": f"DEC_dangling_{dangling_seq}",
    }
    ph = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    cum = hashlib.sha256(
        b"HELEN_CUM_V1" + bytes.fromhex(prev_cum) + bytes.fromhex(ph)
    ).hexdigest()
    return {
        "type": "LEDGER_SEQ_CORRECTION_V1",
        "seq": seq, "payload": payload, "meta": {},
        "payload_hash": ph, "prev_cum_hash": prev_cum, "cum_hash": cum,
    }


# ── Test 1: clean ledger → COUPLED ───────────────────────────────────────────

def test_clean_ledger_coupled(tmp_path):
    """A clean ledger with matching skill hashes must return COUPLED."""
    skill_file = tmp_path / "skill.py"
    skill_file.write_bytes(b"# skill v1\n")
    skill_hash = "sha256:" + hashlib.sha256(b"# skill v1\n").hexdigest()

    ledger = str(tmp_path / "ledger.ndjson")
    chain = _clean_chain(3)
    promo = _promotion_entry(3, "TEST_SKILL_V1", skill_hash, chain[-1]["cum_hash"])
    chain.append(promo)
    _write_ledger(ledger, chain)

    with patch("tools.reality_coupling_probe._skill_id_to_skill_file",
               return_value=skill_file), \
         patch("tools.reality_coupling_probe._probe_runtime") as mock_rt:
        mock_rt.return_value = RRuntime(
            skill_hashes={"TEST_SKILL_V1": skill_hash},
            sovereign_git_dirty=[],
        )
        result = probe(ledger)

    assert result["status"] == STATUS_COUPLED
    assert result["delta"] == []


# ── Test 2: uncorrected duplicate seq → HARD_DRIFT ───────────────────────────

def test_unanchored_dangling_is_hard_drift(tmp_path):
    """A dangling entry with no correction entry must trigger HARD_DRIFT."""
    ledger = str(tmp_path / "ledger.ndjson")
    chain = _clean_chain(5)

    # Inject a dangling entry at seq=2 (same seq, different cum_hash)
    dangling = dict(chain[2])
    dangling["cum_hash"] = "d" * 64   # different cum_hash → never referenced

    # Write: normal entries 0-4, plus extra dangling copy of seq=2
    entries = chain + [dangling]
    _write_ledger(ledger, entries)

    trust = _replay_trust(ledger)
    assert len(trust.dangling_cum_hashes) >= 1

    events = _compute_delta(trust, RRuntime())
    codes = {e.code for e in events}
    assert "UNANCHORED_DANGLING" in codes

    severities = {e.severity for e in events if e.code == "UNANCHORED_DANGLING"}
    assert "HARD" in severities


# ── Test 3: anchored duplicate → COUPLED ─────────────────────────────────────

def test_anchored_dangling_not_hard_drift(tmp_path):
    """A dangling entry covered by LEDGER_SEQ_CORRECTION_V1 must not cause HARD_DRIFT."""
    ledger = str(tmp_path / "ledger.ndjson")
    chain = _clean_chain(5)

    # Dangling at seq=2
    dangling = dict(chain[2])
    dangling["cum_hash"] = "e" * 64

    # Correction referencing the dangling cum_hash
    corr = _correction_entry(
        seq=5,
        dangling_cum="e" * 64,
        dangling_seq=2,
        prev_cum=chain[-1]["cum_hash"],
    )

    entries = chain + [dangling, corr]
    _write_ledger(ledger, entries)

    trust = _replay_trust(ledger)
    # Should be anchored, not unanchored
    assert "e" * 64 in trust.anchored_cum_hashes
    assert "e" * 64 not in trust.dangling_cum_hashes

    events = _compute_delta(trust, RRuntime())
    assert not any(e.code == "UNANCHORED_DANGLING" for e in events)

    with patch("tools.reality_coupling_probe._probe_runtime",
               return_value=RRuntime(skill_hashes={}, sovereign_git_dirty=[])):
        result = probe(ledger)

    assert result["status"] == STATUS_COUPLED, result["delta"]


# ── Test 4: skill hash mismatch → HARD_DRIFT ─────────────────────────────────

def test_skill_hash_mismatch_hard_drift(tmp_path):
    """If skill.py has changed since promotion, SKILL_HASH_MISMATCH must fire."""
    old_hash   = "sha256:" + "a" * 64
    fresh_hash = "sha256:" + "b" * 64

    trust = RTrust()
    trust.active_sovereign_skills["MY_SKILL_V1"] = {
        "candidate_identity_hash": old_hash,
        "decision_id": "DEC_MY_SKILL_V1_1",
        "seq": 42,
    }

    runtime = RRuntime(
        skill_hashes={"MY_SKILL_V1": fresh_hash},
        sovereign_git_dirty=[],
    )

    events = _compute_delta(trust, runtime)
    assert any(e.code == "SKILL_HASH_MISMATCH" and e.severity == "HARD" for e in events)


# ── Test 5: skill missing on disk → HARD_DRIFT ───────────────────────────────

def test_skill_missing_on_disk_hard_drift():
    """If skill.py is not on disk for an active sovereign skill, HARD_DRIFT fires."""
    trust = RTrust()
    trust.active_sovereign_skills["GHOST_SKILL_V1"] = {
        "candidate_identity_hash": "sha256:" + "c" * 64,
        "decision_id": "DEC_GHOST_1",
        "seq": 99,
    }

    runtime = RRuntime(
        skill_hashes={"GHOST_SKILL_V1": None},  # file not found
        sovereign_git_dirty=[],
    )

    events = _compute_delta(trust, runtime)
    assert any(e.code == "SKILL_MISSING_ON_DISK" and e.severity == "HARD" for e in events)


# ── Test 6: sovereign file dirty → HARD_DRIFT ───────────────────────────────

def test_sovereign_file_dirty_hard_drift():
    """A modified sovereign file triggers SOVEREIGN_FILE_DIRTY / HARD_DRIFT."""
    trust   = RTrust()
    runtime = RRuntime(
        skill_hashes={},
        sovereign_git_dirty=["oracle_town/kernel/kernel_daemon.py"],
    )

    events = _compute_delta(trust, runtime)
    assert any(e.code == "SOVEREIGN_FILE_DIRTY" and e.severity == "HARD" for e in events)


# ── Test 7: chain break (unexplained) → HARD_DRIFT ───────────────────────────

def test_chain_break_hard_drift(tmp_path):
    """A genuine chain linkage break (prev_cum_hash points nowhere) must be HARD_DRIFT."""
    ledger = str(tmp_path / "ledger.ndjson")
    chain = _clean_chain(5)

    # Corrupt entry 3's prev_cum_hash so it doesn't match any earlier cum
    corrupt = dict(chain[3])
    corrupt["prev_cum_hash"] = "0" * 64   # nothing has cum_hash = 0*64 at this point

    entries = chain[:3] + [corrupt] + chain[4:]
    _write_ledger(ledger, entries)

    trust = _replay_trust(ledger)
    assert len(trust.chain_breaks) >= 1

    events = _compute_delta(trust, RRuntime())
    assert any(e.code == "CHAIN_BREAK" and e.severity == "HARD" for e in events)


# ── Test 8: live ledger → COUPLED (integration) ───────────────────────────────

def test_live_ledger_coupled():
    """
    The actual town/ledger_v1.ndjson must return COUPLED.
    seq=287 dangling is anchored by seq=295 correction — must not cause HARD_DRIFT.
    """
    live_ledger = str(
        Path(__file__).parents[2] / "town" / "ledger_v1.ndjson"
    )
    if not os.path.exists(live_ledger):
        pytest.skip("live ledger not present")

    result = probe(live_ledger)

    assert result["status"] == STATUS_COUPLED, (
        f"Live ledger must be COUPLED after seq=287 repair. "
        f"Drift events: {result['delta']}"
    )
    assert result["r_trust"]["unanchored_dangling_count"] == 0, (
        "All dangling entries must be anchored by correction entries"
    )
    assert result["r_trust"]["chain_break_count"] == 0
    assert result["r_trust"]["anchored_dangling_count"] == 1, (
        "seq=287 must be counted as anchored (1 correction exists)"
    )
    assert result["r_trust"]["correction_count"] == 1


# ── Test 9: empty ledger → COUPLED ───────────────────────────────────────────

def test_empty_ledger_coupled(tmp_path):
    ledger = str(tmp_path / "empty.ndjson")
    open(ledger, "w").close()
    result = probe(ledger)
    assert result["status"] == STATUS_COUPLED
    assert result["delta"] == []


# ── Test 10: classify helper ──────────────────────────────────────────────────

def test_classify_no_events_is_coupled():
    from tools.reality_coupling_probe import _classify
    assert _classify([]) == STATUS_COUPLED


def test_classify_soft_event_is_soft_drift():
    from tools.reality_coupling_probe import _classify
    assert _classify([DriftEvent("SOFT", "SOFT_CODE", "detail")]) == STATUS_SOFT_DRIFT


def test_classify_hard_beats_soft():
    from tools.reality_coupling_probe import _classify
    events = [
        DriftEvent("SOFT", "SOFT_CODE", "soft"),
        DriftEvent("HARD", "HARD_CODE", "hard"),
    ]
    assert _classify(events) == STATUS_HARD_DRIFT
