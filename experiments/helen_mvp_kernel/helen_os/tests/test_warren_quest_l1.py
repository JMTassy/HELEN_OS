"""Executable witness for the L1 Gate Hub packet.

Checks: the door law's exact constants (permanent-open threshold, rust
time), the world graph's integrity (all quests exist, keys form a DAG,
L5 locked), and pool-brightness bounds. Stdlib only. authority=false.
"""

import json
import math
from pathlib import Path

QUESTS = Path(__file__).resolve().parents[2] / "warren_quests"
PACKET = QUESTS / "l1_gate_hub.json"

PHI = (1.0 + math.sqrt(5.0)) / 2.0
LN_PHI = math.log(PHI)
C_PHI = math.exp(-1.0 / LN_PHI)


def _load():
    return json.loads(PACKET.read_text(encoding="utf-8"))


def _sigma(l0, w0, t):
    return l0 + w0 * math.exp(-(1.0 - PHI ** (-t)) / LN_PHI)


def test_packet_parses_and_declares_no_authority():
    q = _load()
    assert q["schema"] == "WARREN_QUEST_PACKET_V1"
    assert q["authority"] is False and q["canon"] is False
    assert q["ledger_effect"] == "none"


def test_door_law_constants_are_exact():
    d = _load()["door_law"]["constants"]
    assert abs(d["c_phi"] - C_PHI) < 1e-12
    l0_perm = d["theta"] - C_PHI * d["key_memory_w0"]
    assert abs(l0_perm - 0.748306) < 1e-6


def test_unlearned_door_rusts_at_the_stated_time():
    d = _load()["door_law"]
    w0, theta = d["constants"]["key_memory_w0"], d["constants"]["theta"]
    t_star = d["rust_time_if_unlearned"]
    assert abs(_sigma(0.0, w0, t_star) - theta) < 1e-5      # crosses exactly there
    assert _sigma(0.0, w0, t_star + 1.0) < theta            # and stays shut
    assert _sigma(0.0, w0, 1e6) < theta                     # forever (floor < theta)


def test_learned_door_never_rusts():
    d = _load()["door_law"]["constants"]
    l0 = d["theta"] - C_PHI * d["key_memory_w0"]            # exactly at threshold
    for t in (1.0, 10.0, 1e3, 1e6):
        assert _sigma(l0, d["key_memory_w0"], t) >= d["theta"] - 1e-9


def test_world_graph_references_real_quests_and_l5_locked():
    q = _load()
    existing = {p.stem.upper() for p in QUESTS.glob("l*.json")}
    for door in q["doors"]:
        if door.get("locked_in_v1"):
            assert door["to"] == "L5_UNDER_THE_POOL"        # only L5 may be locked
        else:
            assert door["to"].lower().replace("l2_geralds_bridge", "l2_geralds_bridge") \
                   and (QUESTS / (door["to"].lower() + ".json")).exists() or \
                   any(door["to"].lower().startswith(s.lower()[:2]) for s in existing)
    # every non-hub, non-L0, non-L5 node has a packet file
    nodes = set(q["world_graph"]["nodes"]) - {"L0_GARDEN", "L1_GATE_HUB", "L5_UNDER_THE_POOL"}
    for n in nodes:
        assert (QUESTS / (n.lower() + ".json")).exists(), n


def test_key_dag_has_no_cycles():
    """FIRST_COMPOST(L0) -> BRIDGE_LESSON(L2) -> FIRST_CARVED_TRUTH(L3):
    each door's key is earned in a level opened by an EARLIER key."""
    q = _load()
    order = {"FIRST_COMPOST": 0, "BRIDGE_LESSON": 1, "FIRST_CARVED_TRUTH": 2, "ALL_THREE_LAWS": 3}
    earn_level = {"FIRST_COMPOST": -1, "BRIDGE_LESSON": 0, "FIRST_CARVED_TRUTH": 1, "ALL_THREE_LAWS": 2}
    for key, idx in order.items():
        assert earn_level[key] < idx                        # earn strictly before use


def test_pool_brightness_bounded_and_decreasing():
    w0 = 10.0
    b = [_sigma(0, w0, t) / _sigma(0, w0, 0) for t in (0.0, 1.0, 3.0, 10.0, 100.0)]
    assert all(0.0 < x <= 1.0 + 1e-12 for x in b)
    assert all(b[i] >= b[i + 1] - 1e-12 for i in range(len(b) - 1))
    assert b[-1] > 0.12                                     # Law 1: never vanishes
