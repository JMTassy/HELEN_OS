"""GOVERNED_EPOCH_V0 — ONE complete governed-causal-discovery epoch (not another framework). authority=false.
NON-SOVEREIGN. canon=false · ledger_effect=none. Reuses the FROZEN proof_carrying_receipt (unchanged).

Chiddush frozen here:
    HELEN research progress = WITNESSED CONTRACTION, not persuasive convergence.

An epoch is progress iff the live hypothesis set strictly shrinks AND every elimination is licensed by the
raw observation:  H_after ⊊ H_before  with  (H_before minus H_after) ⊆ {hypotheses the receipt marks KILLED}.
If nothing is eliminable ⇒ 🟠 HOLD (reason=discriminator_insufficient) — knowledge about the limit, not failure.

Two SEPARATE gates (the load-bearing separation):
    Γ_E — epistemic update gate: CONTRACT | HOLD | REJECT_RECEIPT over the hypothesis space.
    Γ_I — institutional admission gate: a research contraction NEVER admits governed state.
    Γ_E(H_i)=KILL  ⇏  Γ_I(action)=ADMIT.        ΔKnowledge ⇏ ΔAuthority.  AuthorityGain=0 always.

Replay(receipt) = (H_before, H_after, B_forbidden) with zero unjustified elimination.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import FrozenSet, List, Tuple

from helen_os.kernel.proof_carrying_receipt import (
    ProofCarryingEpoch, validate, ar_ablation_receipt,
)


@dataclass(frozen=True)
class GovernedEpoch:
    receipt: ProofCarryingEpoch
    hypotheses_before: FrozenSet[str]      # explicit — so the contraction is replayable/checkable
    hypotheses_after: FrozenSet[str]


def _killed(r: ProofCarryingEpoch) -> FrozenSet[str]:
    return frozenset(h for h, d in r.hypotheses.items() if d == "KILLED")


def contraction_count(g: GovernedEpoch) -> int:
    return len(g.hypotheses_before) - len(g.hypotheses_after)


def gamma_E(g: GovernedEpoch) -> dict:
    """Epistemic update gate. A contraction is licensed ONLY if the receipt is proof-carrying AND every
    eliminated hypothesis is marked KILLED (backed by the observation)."""
    v, reasons = validate(g.receipt)
    if v != "ADMIT_RECEIPT":
        return {"gate": "Γ_E", "verdict": "REJECT_RECEIPT", "reasons": reasons}
    if g.hypotheses_before != frozenset(g.receipt.prereg.hypothesis_set):
        return {"gate": "Γ_E", "verdict": "REJECT_RECEIPT", "reasons": ["H_before ≠ prereg hypothesis_set"]}
    eliminated = g.hypotheses_before - g.hypotheses_after
    unjustified = sorted(h for h in eliminated if g.receipt.hypotheses.get(h) != "KILLED")
    if unjustified:
        return {"gate": "Γ_E", "verdict": "REJECT_RECEIPT",
                "reasons": ["UNJUSTIFIED_ELIMINATION:" + ",".join(unjustified)]}
    cc = len(eliminated)
    if cc == 0:
        return {"gate": "Γ_E", "verdict": "HOLD", "reason": "discriminator_insufficient",
                "H_before": sorted(g.hypotheses_before), "H_after": sorted(g.hypotheses_after)}
    return {"gate": "Γ_E", "verdict": "CONTRACT", "contraction_count": cc,
            "eliminated": sorted(eliminated),
            "H_before": sorted(g.hypotheses_before), "H_after": sorted(g.hypotheses_after)}


def gamma_I(g: GovernedEpoch) -> dict:
    """Institutional admission gate. A research epoch NEVER mutates governed state, whatever Γ_E decided."""
    return {"gate": "Γ_I", "verdict": "NO_ADMISSION",
            "reason": "epistemic update (Γ_E) ⇏ institutional admission (Γ_I); ΔKnowledge ⇏ ΔAuthority",
            "authority_gain": 0, "ledger_effect": "none"}


def replay(g: GovernedEpoch) -> dict:
    """Deterministic replay: reconstruct (H_before, H_after, B_forbidden); verify zero unjustified elimination."""
    eliminated = g.hypotheses_before - g.hypotheses_after
    unjustified = sorted(h for h in eliminated if g.receipt.hypotheses.get(h) != "KILLED")
    return {"H_before": sorted(g.hypotheses_before), "H_after": sorted(g.hypotheses_after),
            "B_forbidden": list(g.receipt.claim_boundary.forbidden_extrapolations),
            "eliminated": sorted(eliminated), "unjustified_eliminations": unjustified,
            "contraction_count": len(eliminated), "replay_valid": not unjustified}


def build_ar_epoch() -> GovernedEpoch:
    """The witnessed AR ablation as ONE complete epoch: the hypothesis 'L1 is load-bearing' is eliminated
    (removing L1 → +0.009, no drop); L2/L3 survive; L5-L7 stay live (unresolved). Contraction = 1."""
    r = ar_ablation_receipt()
    before = frozenset(r.prereg.hypothesis_set)          # {H_L1..H_L7}
    after = before - _killed(r)                          # minus {H_L1}
    return GovernedEpoch(r, before, after)


def run_one_epoch() -> dict:
    g = build_ar_epoch()
    return {"epoch": g.receipt.epoch_id,
            "Γ_E": gamma_E(g), "Γ_I": gamma_I(g), "replay": replay(g),
            "gate_separation_holds": (gamma_E(g)["verdict"] == "CONTRACT"
                                      and gamma_I(g)["verdict"] == "NO_ADMISSION"),
            "chiddush": "research progress = witnessed contraction, not persuasive convergence",
            "authority": False}
