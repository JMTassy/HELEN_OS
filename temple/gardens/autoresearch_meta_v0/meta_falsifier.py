#!/usr/bin/env python3
"""
HELEN_AUTORESEARCH_META_20M_V0 — falsifier for the CHAOS→GATE→GENESIS loop.

Reproduces ONE real, file-backed defect in the current AUTORESEARCH loop, then
demonstrates the minimal repair, then attacks the repair, then repairs the repair.
LOCAL_FIRST · FABLE_CALLS=0 · no models · deterministic · authority=false · ΔA=0.

DEFECT (M3 counterexample-amnesia ∧ M7 pass-leakage):
  run_chiddush_gate writes CHIDDUSH_S0.json = survivors[:3] IF survives>=3
  ELSE sorted(results, -fitness)[:3]  ← launders non-survivors into seeds.
  run_genesis_loop.load_seeds() returns CHIDDUSH_S0.json IF it exists (before the
  SEEDS_NOT_READY guard). Net effect: 0 survivors still yields 3 S_0 seeds, and the
  "0 CHIDDUSH survived" falsifier is lost across the iteration boundary.
"""
import json
from pathlib import Path

GARDEN = Path(__file__).resolve().parent.parent / "async_wulmath_chaos_garden_v1"
GATE = GARDEN / "HARD_CHIDDUSH_GATE_RECEIPT.json"
S0 = GARDEN / "CHIDDUSH_S0.json"
FMEM = Path(__file__).resolve().parent / "FALSIFIER_MEMORY.json"


def current_load_seeds(s0_path):
    """Faithful replica of run_genesis_loop.load_seeds() preference branch."""
    if s0_path.exists():
        return json.loads(s0_path.read_text())        # ← returns regardless of verdict
    return None                                         # (else falls to receipt/STOP)


def repaired_load_seeds(s0_seeds, verdict_of):
    """Minimal repair: seed ONLY from real survivors; else SEEDS_NOT_READY."""
    survivors = [s for s in s0_seeds if verdict_of.get(s["lineage"][0]) == "SURVIVES"]
    return survivors  # empty ⇒ genesis must STOP (SEEDS_NOT_READY)


def main():
    gate = json.loads(GATE.read_text())
    s0_seeds = json.loads(S0.read_text())
    verdict_of = {v["name"]: v["verdict"] for v in gate["all_verdicts"]}
    survives = gate["survives"]

    print("─" * 62)
    print("  AUTORESEARCH META — DEFECT REPRODUCTION")
    print("─" * 62)

    # 1) REPRODUCE the defect on current behaviour
    seeds_now = current_load_seeds(S0)
    laundered = [s for s in seeds_now if verdict_of.get(s["lineage"][0]) != "SURVIVES"]
    defect = (survives == 0 and len(seeds_now) > 0 and len(laundered) == len(seeds_now))
    print(f"  gate.survives            = {survives}")
    print(f"  genesis seeds (current)  = {len(seeds_now)}  verdicts="
          f"{[verdict_of.get(s['lineage'][0]) for s in seeds_now]}")
    print(f"  laundered non-survivors  = {len(laundered)}")
    print(f"  DEFECT_REPRODUCED        = {defect}   (0 survivors → {len(seeds_now)} seeds)")

    # 2) MINIMAL REPAIR: survivors-only
    seeds_repaired = repaired_load_seeds(s0_seeds, verdict_of)
    stop = len(seeds_repaired) == 0
    print("─" * 62)
    print(f"  REPAIR (survivors-only)  = {len(seeds_repaired)} seeds → "
          f"{'SEEDS_NOT_READY → STOP' if stop else 'seed'}")
    repair_fixes = (stop is True)
    print(f"  REPAIR_FIXES_DEFECT      = {repair_fixes}")

    # 3) ATTACK THE REPAIR: does it lose the unresolved EVIDENCE_NEEDED? (M10 amnesia)
    dropped = [s for s in s0_seeds if s not in seeds_repaired]
    amnesia = len(dropped) > 0 and not FMEM.exists()
    print("─" * 62)
    print(f"  ATTACK: repair drops {len(dropped)} EVIDENCE_NEEDED with no memory")
    print(f"  REPAIR_INTRODUCES_AMNESIA = {amnesia}   (M10: compression⇒amnesia)")

    # 4) REPAIR²: persist a falsifier memory M_F (carry the obligation forward)
    m_f = {
        "schema": "FALSIFIER_MEMORY_V0", "authority": False, "canon": False,
        "open_obligations": [
            {"obligation": "0 CHIDDUSH survived the hard counterfeit gate",
             "source": "HARD_CHIDDUSH_GATE_RECEIPT.json", "status": "UNRESOLVED",
             "blocks": "GENESIS seeding until a real survivor exists"}],
        "unresolved_candidates": [
            {"name": s["lineage"][0], "verdict": verdict_of.get(s["lineage"][0]),
             "fitness": s.get("fitness"), "status": "HOLD"} for s in dropped],
        "law": "Compress(M) must preserve OpenObligations(M) · Falsifier_t ∈ M_{t+n} until resolved",
    }
    FMEM.write_text(json.dumps(m_f, indent=2, ensure_ascii=False))
    amnesia_after = len(dropped) > 0 and not FMEM.exists()
    print("─" * 62)
    print(f"  REPAIR²: wrote FALSIFIER_MEMORY.json ({len(m_f['unresolved_candidates'])} HOLD + 1 obligation)")
    print(f"  AMNESIA_AFTER_REPAIR2    = {amnesia_after}   (obligations now persisted)")

    verdict = {
        "defect_reproduced": defect, "repair_fixes_defect": repair_fixes,
        "repair_introduced_amnesia": amnesia, "amnesia_resolved_by_MF": (amnesia and not amnesia_after),
        "seeds_current": len(seeds_now), "seeds_repaired": len(seeds_repaired),
        "chain_valid": defect and repair_fixes and amnesia and not amnesia_after,
    }
    print("─" * 62)
    print(f"  CHAIN: defect→repair→attack→repair²  VALID = {verdict['chain_valid']}")
    (Path(__file__).resolve().parent / "META_FALSIFIER_RESULT.json").write_text(
        json.dumps(verdict, indent=2))
    return verdict


if __name__ == "__main__":
    main()
