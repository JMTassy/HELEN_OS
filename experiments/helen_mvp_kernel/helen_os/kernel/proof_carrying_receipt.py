"""PROOF_CARRYING_RECEIPT — a research epoch that carries its own claim boundary. 🔵 OBSERVED · authority=false.
NON-SOVEREIGN. canon=false · ledger_effect=none.

Governed-causal-discovery unit: the value of an epoch is not the result, it is
    Result + WhatItDiscriminates + WhatItDoesNotEstablish.
A receipt is ADMISSIBLE only if it is PROOF-CARRYING:
  1. PREREG fixed before observation (hypothesis_set, discriminator, stop_rule).
  2. INTERVENTION records changed vs frozen variables.
  3. OBSERVATION records raw result + variance.
  4. HYPOTHESES: each hypothesis gets a disposition {KILLED, WEAKENED, SURVIVES, UNRESOLVED}.
  5. CAUSAL_GRAPH: removed / surviving / unresolved edges.
  6. CLAIM_BOUNDARY: licensed_claim (only on SURVIVING hypotheses) AND forbidden_extrapolations
     (must explicitly disclaim EVERY unresolved hypothesis).
Invariants (fail-closed):
  - No claim_boundary, or empty forbidden set ⇒ REJECT ("a result without its boundary is not proof-carrying").
  - A licensed claim resting on a KILLED/UNRESOLVED hypothesis ⇒ REJECT (overclaim beyond discrimination).
  - An unresolved hypothesis not disclaimed ⇒ REJECT.
  - AuthorityGain = 0 ALWAYS: a receipt is a candidate, never an admission. authority=true ⇒ REJECT.
Disposition of a VALID receipt: PROGRESS (≥1 hypothesis moved off UNRESOLVED) else HOLD ("no discriminating
evidence under budget" — knowledge about the limit, not failure).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

DISPOSITIONS = {"KILLED", "WEAKENED", "SURVIVES", "UNRESOLVED"}


@dataclass(frozen=True)
class Prereg:
    hypothesis_set: Tuple[str, ...]        # H-ids, fixed BEFORE observation
    discriminator: str                     # the experiment that separates them
    expected_outcomes: Dict[str, str]      # per-hypothesis predicted signature
    stop_rule: str


@dataclass(frozen=True)
class Intervention:
    changed_variables: Tuple[str, ...]
    frozen_variables: Tuple[str, ...]


@dataclass(frozen=True)
class Observation:
    raw_result: Dict[str, float]
    variance: str


@dataclass(frozen=True)
class CausalGraph:
    removed_edges: Tuple[str, ...]
    surviving_edges: Tuple[str, ...]
    unresolved_edges: Tuple[str, ...]


@dataclass(frozen=True)
class ClaimBoundary:
    licensed_claim: str
    licensed_refs: Tuple[str, ...]         # hypothesis ids the claim rests on (must all SURVIVE)
    forbidden_extrapolations: Tuple[str, ...]
    forbidden_refs: Tuple[str, ...]        # hypothesis ids explicitly disclaimed (must cover all UNRESOLVED)


@dataclass(frozen=True)
class ProofCarryingEpoch:
    epoch_id: str
    prereg: Prereg
    intervention: Intervention
    observation: Observation
    hypotheses: Dict[str, str]             # H-id -> disposition
    causal_graph: CausalGraph
    claim_boundary: ClaimBoundary
    authority: bool = False                # ALWAYS false; validator enforces


def validate(e: ProofCarryingEpoch) -> Tuple[str, List[str]]:
    """Deterministic gate. Returns (verdict, reasons). verdict ∈ {ADMIT_RECEIPT, REJECT}."""
    R: List[str] = []
    # --- authority leak (fail-closed) ---
    if e.authority is not False:
        R.append("AUTHORITY_LEAK: a receipt never grants authority")
    # --- prereg must exist and precede observation ---
    if not e.prereg.hypothesis_set:
        R.append("NO_PREREG_HYPOTHESES")
    if not e.prereg.discriminator or not e.prereg.stop_rule:
        R.append("NO_DISCRIMINATOR_OR_STOP_RULE")
    # --- every prereg hypothesis has a valid disposition ---
    for h in e.prereg.hypothesis_set:
        d = e.hypotheses.get(h)
        if d not in DISPOSITIONS:
            R.append(f"HYPOTHESIS_UNDISPOSED:{h}")
    for h, d in e.hypotheses.items():
        if d not in DISPOSITIONS:
            R.append(f"BAD_DISPOSITION:{h}={d}")
    # --- claim boundary is mandatory and must state what is NOT established ---
    cb = e.claim_boundary
    if not cb.forbidden_extrapolations:
        R.append("NO_FORBIDDEN_EXTRAPOLATIONS: result without boundary is not proof-carrying")
    # --- a licensed claim may rest ONLY on SURVIVING hypotheses (no overclaim) ---
    for h in cb.licensed_refs:
        if e.hypotheses.get(h) != "SURVIVES":
            R.append(f"OVERCLAIM: licensed claim rests on non-surviving {h}={e.hypotheses.get(h)}")
    # --- every UNRESOLVED hypothesis must be explicitly disclaimed ---
    unresolved = {h for h, d in e.hypotheses.items() if d == "UNRESOLVED"}
    undisclaimed = unresolved - set(cb.forbidden_refs)
    if undisclaimed:
        R.append(f"UNDISCLAIMED_UNRESOLVED:{sorted(undisclaimed)}")
    verdict = "ADMIT_RECEIPT" if not R else "REJECT"
    return verdict, R


def disposition(e: ProofCarryingEpoch) -> str:
    """For a VALID receipt: PROGRESS if ≥1 hypothesis moved off UNRESOLVED, else HOLD (limit-knowledge)."""
    moved = sum(1 for d in e.hypotheses.values() if d in ("KILLED", "WEAKENED", "SURVIVES"))
    return "PROGRESS" if moved > 0 else "HOLD"


def summarize(e: ProofCarryingEpoch) -> dict:
    v, reasons = validate(e)
    return {"epoch_id": e.epoch_id, "receipt_verdict": v, "reasons": reasons,
            "disposition": disposition(e) if v == "ADMIT_RECEIPT" else "N/A",
            "hypotheses": e.hypotheses,
            "surviving_edges": list(e.causal_graph.surviving_edges),
            "removed_edges": list(e.causal_graph.removed_edges),
            "unresolved_edges": list(e.causal_graph.unresolved_edges),
            "licensed_claim": e.claim_boundary.licensed_claim,
            "forbidden_extrapolations": list(e.claim_boundary.forbidden_extrapolations),
            "authority": e.authority}


# ── DOGFOOD: the witnessed AR leave-one-law-out ablation as a proof-carrying receipt ──
def ar_ablation_receipt() -> ProofCarryingEpoch:
    """Baseline K7=0.5964 · remove L1→+0.009 · L2→−0.093 · L3→−0.077 · L4→−0.030 · L5-L7 NOT RUN (wall cap)."""
    H = ("H_L1", "H_L2", "H_L3", "H_L4", "H_L5", "H_L6", "H_L7")  # "Li is load-bearing"
    return ProofCarryingEpoch(
        epoch_id="AR_KERNEL_PROMPT_V0/leave-one-law-out",
        prereg=Prereg(
            hypothesis_set=H,
            discriminator="leave-one-law-out over K7; ΔQ_discrim vs full-K7 baseline on 28 frozen V3 fixtures, 2B, temp0 seed0",
            expected_outcomes={h: "ΔQ<0 ⇒ load-bearing" for h in H},
            stop_rule="10 epochs OR 1200s wall (whichever first)"),
        intervention=Intervention(changed_variables=("system_prompt(one law removed)",),
                                  frozen_variables=("fixtures(28)", "scorer", "model(2B)", "temp0", "seed0", "budget")),
        observation=Observation(
            raw_result={"K7": 0.5964, "minus_L1": 0.6054, "minus_L2": 0.5036, "minus_L3": 0.5196, "minus_L4": 0.5661},
            variance="single run, no seed repeats — deltas descriptive not inferential"),
        hypotheses={"H_L1": "KILLED",       # removing L1 did NOT drop Q (+0.009) ⇒ 'L1 load-bearing' killed
                    "H_L2": "SURVIVES",     # −0.093
                    "H_L3": "SURVIVES",     # −0.077
                    "H_L4": "WEAKENED",     # −0.030 (small)
                    "H_L5": "UNRESOLVED", "H_L6": "UNRESOLVED", "H_L7": "UNRESOLVED"},  # not run (wall cap)
        causal_graph=CausalGraph(
            removed_edges=("L1→Q (not load-bearing here)",),
            surviving_edges=("L2(cognition≠effect)→Q", "L3(what-licenses-the-arrow)→Q"),
            unresolved_edges=("L5→Q", "L6→Q", "L7→Q")),
        claim_boundary=ClaimBoundary(
            licensed_claim="On 2B / this scorer / this budget, L2 and L3 are load-bearing (removing either drops Q by ≥0.077).",
            licensed_refs=("H_L2", "H_L3"),
            forbidden_extrapolations=(
                "L5-L7 never ran (wall cap) — no claim about them",
                "2B only — no claim about 9B or general HELEN",
                "single scorer/budget, single run — not a general constitutional truth",
                "load-bearing-here ≠ constitutionally-necessary"),
            forbidden_refs=("H_L5", "H_L6", "H_L7")),
        authority=False)
