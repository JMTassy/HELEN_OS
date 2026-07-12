"""Executable witness for the L2 Gerald's Bridge quest packet.

Checks the quest economy against Law 3 of WARREN_COMPOST_CALCULUS_V1
(tight backing bound) and the telephone's replay determinism contract.
Stdlib only. NON_SOVEREIGN. authority=false.
"""

import json
from pathlib import Path

PACKET = Path(__file__).resolve().parents[2] / "warren_quests" / "l2_geralds_bridge.json"


def _load():
    return json.loads(PACKET.read_text(encoding="utf-8"))


def test_packet_parses_and_declares_no_authority():
    q = _load()
    assert q["schema"] == "WARREN_QUEST_PACKET_V1"
    assert q["authority"] is False and q["canon"] is False
    assert q["ledger_effect"] == "none"


def test_economy_respects_mass_conserving_compost():
    e = _load()["economy"]
    assert e["kappa"] <= 1.0 - e["rho"] + 1e-12          # Law 3 condition
    # kappa = 1-rho makes repeated compost mint exactly the deposit:
    # sum_k lambda*kappa*rho^k*w0 = lambda*w0*kappa/(1-rho) = lambda*w0
    total = e["lambda"] * e["kappa"] / (1.0 - e["rho"])
    assert abs(total - e["lambda"]) < 1e-12


def test_total_payout_is_tight_against_law3_bound():
    q = _load()
    e = q["economy"]
    deposits = 6 * e["slot_deposit_w0"] + e["counterexample_deposit_w0"]   # 100
    payouts = sum(t["mint_zol"] for t in q["tiers"]) + q["jackpot"]["mint_zol"]
    bound = e["lambda"] * deposits
    assert payouts <= bound + 1e-9                        # Law 3 holds
    assert abs(payouts - bound) < 1e-9                    # ...and is TIGHT
    assert abs(bound - 100.0) < 1e-9                      # JACKPOT board value


def test_every_slot_has_a_deterministic_mutation():
    q = _load()
    slot_ids = {s["id"] for s in q["slots"]}
    mutations = q["telephone"]["mutations"]
    assert set(mutations.keys()) == slot_ids              # total function: no gap un-mutated
    hops = set(q["telephone"]["hops"])
    outcomes = [m["outcome"] for m in mutations.values()]
    assert len(outcomes) == len(set(outcomes))            # distinct comedy per gap
    assert all(m["hop"] in hops for m in mutations.values())


def test_tier_requirements_are_monotone():
    """Higher tiers require a superset of lower-tier slots (deepening =
    same law, higher stakes — Atlas design thesis)."""
    q = _load()
    t1, t2, t3 = (set(t["requires_slots"]) for t in q["tiers"])
    assert t1 <= t2 <= t3
    assert "requires_counterexample" in q["tiers"][2]
