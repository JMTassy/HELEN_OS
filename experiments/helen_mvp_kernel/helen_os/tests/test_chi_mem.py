"""χ_mem — deterministic replay under declared inputs. 🔵 OBSERVED."""
import pytest

from helen_os.ledger.hash_chain import (
    GENESIS_HASH, ChainBreak, canonical_json, compute_event_hash, sha256_hex,
    verify_chain,
)

EVENTS_SRC = [{"op": "add", "v": 1}, {"op": "add", "v": 2}, {"op": "mul", "v": 3}]


def _fold(g0: int, events: list[dict]) -> int:
    g = g0
    for e in events:
        g = g + e["v"] if e["op"] == "add" else g * e["v"]
    return g


def _replay_cert(g0, events, declared_inputs: dict) -> str:
    """Replay certificate: UNKNOWN when any declared input is missing —
    never a silent match."""
    if any(v is None for v in declared_inputs.values()):
        return "UNKNOWN"
    return "sha256:" + sha256_hex(canonical_json({"g": _fold(g0, events)}))


def test_mem_01_deterministic_replay():
    a = _replay_cert(0, EVENTS_SRC, {"g0": 0, "log": "declared"})
    b = _replay_cert(0, EVENTS_SRC, {"g0": 0, "log": "declared"})
    assert a == b and a.startswith("sha256:")


def test_mem_02_incomplete_inputs_never_silent_match():
    assert _replay_cert(0, EVENTS_SRC, {"g0": 0, "log": None}) == "UNKNOWN"


def test_mem_03_wrong_prev_hash_breaks_chain():
    e1 = {"seq": 1, "prev_event_hash": GENESIS_HASH, "data": "x"}
    e1["event_hash"] = compute_event_hash(e1)
    e2 = {"seq": 2, "prev_event_hash": "f" * 64, "data": "y"}  # wrong prev
    e2["event_hash"] = compute_event_hash(e2)
    with pytest.raises(ChainBreak):
        verify_chain([e1, e2])
    e2_ok = {"seq": 2, "prev_event_hash": e1["event_hash"], "data": "y"}
    e2_ok["event_hash"] = compute_event_hash(e2_ok)
    verify_chain([e1, e2_ok])  # positive control: correct chain verifies


@pytest.mark.skip(reason="cross-seat replay not yet run — chi_mem is PASS_SCOPED(seat=laptop) only")
def test_mem_04_cross_seat_replay_parity():
    """Same (G0, L, Θ) on a second machine must hash-match. Pending second seat."""
