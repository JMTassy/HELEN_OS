"""HAL pass 2 — deterministic adjudication of HER's frozen compost.

NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none.

HER pass 2 delivered twelve candidate chiddushes and froze. HAL's rule
for this pass: a SHIP verdict must cite the EXECUTABLE that enforces
the law — module:function, resolvable by import. A law that exists
only as prose has not shipped; it is HOLD wearing confidence.

HER's own framing binds this pass: HER is an interpretive role, not an
independent witness — reasoning about the same pages adds zero
authority (that is item 12, applied to items 1-11).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from crystal_palace import canon_hash  # noqa: E402

HER_COMPOST_PASS2 = (
    {"id": 1, "claim": "recursive transformation grammar across "
                       "building/taxonomy/machine scales"},
    {"id": 2, "claim": "supervised autonomy with failover (CP-527): "
                       "authority scheduling over time"},
    {"id": 3, "claim": "topology over monitoring: robustness can be "
                       "structural, not cognitive (CP-546)"},
    {"id": 4, "claim": "individually admissible transformations can "
                       "compose into a globally inadmissible state"},
    {"id": 5, "claim": "causal transmission and semantic interpretation "
                       "are different transformations (CP-699)"},
    {"id": 6, "claim": "model-optimal != world-admissible (Great "
                       "Circle indicator's own caveat)"},
    {"id": 7, "claim": "TRACE = value + time + provenance of capture "
                       "(Dollond)"},
    {"id": 8, "claim": "SELF-ACTING is a lexical label, not an "
                       "operational ontology"},
    {"id": 9, "claim": "GATE != INVARIANT: kernel needs both, and "
                       "impossibility-by-construction outranks judgment"},
    {"id": 10, "claim": "COMPOSABLE != COMPOSED: adjacent-possible "
                        "compositions never promote to historical fact"},
    {"id": 11, "claim": "novelty is four-axis: (N_P, N_M, N_C, N_G)"},
    {"id": 12, "claim": "retrieval density != epistemic independence"},
)


def freeze_her_pass2() -> dict:
    return {"her_pass2_hash": canon_hash(HER_COMPOST_PASS2),
            "items": len(HER_COMPOST_PASS2)}


# Verdict classes: SHIP requires an importable executable. HOLD names
# the missing witness. SHIP_KERNEL_CORRECTION marks an architecture
# change adopted into the kernel modules themselves.

HAL_PASS2_BOARD = (
    {"id": 1, "verdict": "HOLD",
     "missing": "three scales is a candidate homology; needs a "
                "falsifier against scale cherry-picking before it is "
                "more than a pattern-claim",
     "executable": None},
    {"id": 2, "verdict": "SHIP",
     "executable": "effect_gate:fallback_arm",
     "note": "the arm law (recoverable -> act owing compost; "
             "unrecoverable -> hold) IS authority scheduling, priced "
             "by named loss; CP-527 cited as precedent in the code"},
    {"id": 3, "verdict": "SHIP",
     "executable": "kernel_invariants:BoundedBudget",
     "note": "the three-rung ladder gated < invariant_checked < "
             "structurally_impossible; Whitworth is the 1851 instance "
             "of the top rung"},
    {"id": 4, "verdict": "SHIP",
     "executable": "kernel_invariants:compositional_admissibility",
     "note": "new kernel falsifier: two valid leases, one violated "
             "global invariant"},
    {"id": 5, "verdict": "SHIP",
     "executable": "kernel_invariants:decode",
     "note": "m never entails A; (m, C) entails A; decode() without a "
             "codebook refuses with E_NO_NAMESPACE"},
    {"id": 6, "verdict": "SHIP",
     "executable": "kernel_invariants:recommend",
     "note": "recommendation never executes; feasibility separate "
             "from optimality"},
    {"id": 7, "verdict": "SHIP",
     "executable": "flow_object:TraceEdge",
     "note": "receipts on edges with t and provenance; HER's source-"
             "class caveat on Dollond stands recorded in atlas batch 2"},
    {"id": 8, "verdict": "SHIP",
     "executable": "transformation_motif:decompose_self_acting",
     "note": "the label mints nothing; five witnessed fields mint M"},
    {"id": 9, "verdict": "SHIP_KERNEL_CORRECTION",
     "executable": "kernel_invariants:run_with_invariant",
     "note": "the flagged chiddush survives attack: run_gate_only "
             "reaches the forbidden state SILENTLY via the ungated "
             "path; the invariant catches it on any path; the type "
             "cannot express it. Kernel rule adopted: express "
             "constitutional impossibilities as types/topology where "
             "possible, gates otherwise, prose never"},
    {"id": 10, "verdict": "SHIP_EXPERIMENT",
     "executable": "kernel_invariants:compose_adjacent",
     "note": "LatentComposition.status is init=False ADJACENT_POSSIBLE "
             "— nothing composed is born witnessed; freeze_latent_set "
             "is the clean half of the blind experiment; the blind "
             "lane itself still requires a fresh seat"},
    {"id": 11, "verdict": "SHIP",
     "executable": "kernel_invariants:NoveltyDecomposition",
     "note": "four axes, no aggregate without declared weights; the "
             "empirical distribution over the axes stays HOLD"},
    {"id": 12, "verdict": "SHIP",
     "executable": "kernel_invariants:independent_roots",
     "note": "authority consumes provenance roots, never passage "
             "counts; joins T11 (coherence never raises authority)"},
)
