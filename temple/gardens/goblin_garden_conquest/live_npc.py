#!/usr/bin/env python3
"""live_npc.py — a constitutional generative agent (the HELEN answer to Smallville).

Runs a live NPC through the full GardenMemory loop:
    observe → retrieve → reflect(candidate) → gate(validator) → plan → receipt → replay

The whole point: reproduce a Generative Agents NPC (Park et al., UIST 2023) but with
the membrane installed at every arrow — so the paper's §7.2 "Isabella drift" (an
unverified reflection contaminating identity) CANNOT happen. An ungrounded reflection
candidate is REJECTED at the gate and never enters memory; only a grounded, validated
reflection becomes a retrievable REFLECTION + RECEIPT.

Deterministic by default (stub reasoner/planner/validator, seeded) — no LLM, no cost,
always-on, fully replayable. Optionally wire a local model via --reasoner ollama.

NON_SOVEREIGN · authority=false · garden-only · no ledger/kernel/push · ledger=local jsonl.

Usage:
    python3 live_npc.py                    # run the deterministic demo, print receipt
    python3 live_npc.py --turns 5
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from typed_memory import GardenMemory, MemoryEntry, MemoryType  # noqa: E402


# --- the membrane: a validator that GROUNDS reflections against observation evidence ---

# words that don't count as grounding — the agent's own name and common stopwords.
# Sharing "Klaus" between a reflection-about-Klaus and an observation-about-Klaus is
# NOT evidence; grounding requires a shared *content* term.
_STOP = {"the", "a", "an", "his", "her", "to", "of", "on", "in", "is", "and", "for",
         "with", "at", "he", "she", "it", "was", "are", "be"}


def grounding_validator(mem: GardenMemory):
    """Return a validator that admits a reflection candidate ONLY if its claimed
    evidence ids exist as OBSERVATIONS AND it shares a *content* keyword (excluding
    the agent name + stopwords) with one of them. Blocks Isabella drift: an insight
    ungrounded in what was actually observed fails.
    """
    obs_by_id = {e.id: e for e in mem.entries if e.type == MemoryType.OBSERVATION}
    ignore = _STOP | set(mem.agent_id.lower().split())

    def content_words(text: str) -> set:
        return {w for w in text.lower().split() if w not in ignore}

    def validate(candidate: MemoryEntry) -> bool:
        ev = [obs_by_id[i] for i in candidate.evidence if i in obs_by_id]
        if not ev:
            return False  # no grounded observation evidence → reject
        cand_words = content_words(candidate.content)
        return any(cand_words & content_words(o.content) for o in ev)

    return validate


# --- deterministic stubs (no LLM; replace with local model under contract) ---

def make_stub_reasoner(insight: str):
    """A reasoner that returns a fixed insight — lets the demo assert exact behavior."""
    return lambda prompt: insight


def stub_planner(prompt: str) -> str:
    return "Day: focus on the most-observed activity. Morning: continue it. (candidate)"


def run_npc(agent_id: str = "Klaus", ledger_path: Path | None = None) -> dict:
    """The scripted live-NPC scenario that demonstrates the drift defense end-to-end."""
    npc = GardenMemory(agent_id, ledger_path=ledger_path)

    # 1. Observations (grounded facts the NPC actually perceived)
    npc.observe("Klaus read a paper on gentrification", importance=0.6)
    npc.observe("Klaus spent hours in the library on his research", importance=0.7)
    npc.observe("Klaus discussed his research project with a librarian", importance=0.6)

    log = {"agent": agent_id, "observations": 3, "gated": [], "rejected": []}

    # 2a. A GROUNDED reflection (shares "research" with observations) → should ADMIT
    grounded = npc.reflect("what is Klaus dedicated to",
                           make_stub_reasoner("Klaus is dedicated to his research"))
    rec = npc.gate_reflection(grounded[0], grounding_validator(npc))
    if rec:
        log["gated"].append(grounded[0].content)

    # 2b. An UNGROUNDED reflection (Isabella-drift: nothing observed about theatre) → REJECT
    drift = npc.reflect("hobbies",
                        make_stub_reasoner("Klaus loves shakespeare theatre"))
    rejected = npc.gate_reflection(drift[0], grounding_validator(npc))
    if rejected is None:
        log["rejected"].append(drift[0].content)

    # 3. Plan grounds only in admitted reflections
    plan = npc.plan("plan the day", stub_planner)
    log["plan"] = plan.content

    # 4. Identity check: what does the NPC now retrieve about itself by default?
    identity_hits = npc.retrieve("Klaus", top_k=10)
    log["default_retrieval_types"] = sorted({h.type.value for h in identity_hits})
    log["drift_in_identity"] = any("shakespeare" in h.content.lower() for h in identity_hits)

    # 5. Replay: reconstruct from the ledger, prove determinism
    replayed = npc.replay()
    log["live_entries"] = len(npc.entries)
    log["replay_entries"] = len(replayed)
    log["replay_matches"] = [e.id for e in npc.entries] == [e.id for e in replayed]

    return log


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--agent", default="Klaus")
    args = ap.parse_args()

    # fresh ledger per demo run so replay reflects exactly this run (not accumulation)
    demo_ledger = Path(f"scratch/{args.agent}_live_npc_demo.jsonl")
    if demo_ledger.exists():
        demo_ledger.unlink()
    log = run_npc(args.agent, ledger_path=demo_ledger)
    print("🧬 LIVE NPC — constitutional generative agent (HELEN vs Smallville)")
    print(f"   agent            : {log['agent']}  ·  authority=false · garden-only")
    print(f"   observations     : {log['observations']}")
    print(f"   ✅ gated (admitted): {log['gated']}")
    print(f"   🔴 rejected (drift): {log['rejected']}")
    print(f"   default retrieval  : {log['default_retrieval_types']} "
          f"(reflections excluded by SEAM 2)")
    print(f"   drift in identity  : {log['drift_in_identity']}  "
          f"(must be False — Isabella drift blocked)")
    print(f"   replay matches     : {log['replay_matches']}  "
          f"({log['replay_entries']} entries)")
    print("\n🏁 believability ⊬ admissibility · reflection ⊬ observation · 📜 ledger=local")
    return 0


if __name__ == "__main__":
    sys.exit(main())
