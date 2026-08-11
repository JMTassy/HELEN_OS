"""Kernel invariants — HAL's executable answer to HER pass 2.

NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none.

The flagged chiddush: GATE != INVARIANT. A gate evaluates whether a
transition may occur; an invariant constrains every reachable state;
a type makes the forbidden state unrepresentable. Three rungs:

    gated  <  invariant_checked  <  structurally_impossible

A gate-only system is exactly as safe as its coverage: one ungated
maintenance path and the forbidden state is reached SILENTLY. An
invariant catches it on any path. A type refuses to even express it.
Whitworth's force balancing is the 1851 instance of the top rung:
no agent decides to cancel the disturbance — the topology does.

Also executable here, from the same HER pass:

  LOCAL ⊬ COMPOSITIONAL   Two actions, each inside its own lease, can
      jointly violate a global invariant. Admissibility does not
      distribute over parallel composition.
  COMPOSABLE != COMPOSED   Adjacent-possible motif compositions carry
      status ADJACENT_POSSIBLE at the type (init=False — no
      constructor argument can set it higher); only a page witness
      promotes, through a function that demands the page.
  NO NAMESPACE, NO SEMANTICS   The same needle movement decodes to
      different symbols under different codebooks: m ⊬ A, only
      (m, C) ⊢ A. decode() without a codebook refuses.
  ROOTS, NOT PASSAGES   Thirty agreeing passages from one catalogue
      are one provenance root. Authority functions consume root
      counts; retrieval density is not epistemic independence.
  NOVELTY IS FOUR-AXIS   (N_P, N_M, N_C, N_G) — primitive, motif,
      composition, governance. No aggregate without declared weights.
  MODEL-OPTIMAL != WORLD-ADMISSIBLE   A recommendation never executes;
      argmin(distance) != argmin(practical cost).

Deterministic: no wall-time, no randomness, canonical serialization.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field

SAFETY_STRENGTH = ("gated", "invariant_checked", "structurally_impossible")


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


def canon_hash(obj) -> str:
    return hashlib.sha256(canon(obj).encode("utf-8")).hexdigest()


# ── rung 1 vs rung 2: the gate-coverage hole, demonstrated ─────────────
# World: a shared budget. Steps carry a 'gated' flag — the gate refuses
# overspend, but ONLY on steps that actually pass through it.

def run_gate_only(budget: float, steps: tuple) -> dict:
    """A gate-only system. The ungated path is the hole: the gate is
    never consulted, so the forbidden state is reached silently."""
    spent = 0.0
    for s in steps:
        if s.get("gated") and spent + s["amount"] > budget:
            continue                        # the gate refuses, when asked
        spent += s["amount"]
    return {"spent": spent, "budget": budget,
            "forbidden_state_reached": spent > budget,
            "detected": False}              # nothing was watching states


def run_with_invariant(budget: float, steps: tuple) -> dict:
    """Same steps, plus an invariant over every reachable state:
    I(s) := spent <= budget. Path-independent detection."""
    spent = 0.0
    for i, s in enumerate(steps):
        if s.get("gated") and spent + s["amount"] > budget:
            continue
        spent += s["amount"]
        if spent > budget:
            return {"verdict": "E_INVARIANT_VIOLATION", "at_step": i,
                    "spent": spent, "budget": budget, "detected": True}
    return {"verdict": "INVARIANT_HELD", "spent": spent, "detected": True}


@dataclass(frozen=True)
class BoundedBudget:
    """Rung 3: the forbidden state is unrepresentable. There is no
    'detect' — there is nothing to detect, ever."""
    allocated: float
    spent: float

    def __post_init__(self):
        if self.spent > self.allocated:
            raise ValueError("E_UNREPRESENTABLE_STATE")


# ── LOCAL ⊬ COMPOSITIONAL ──────────────────────────────────────────────

def compositional_admissibility(amounts: tuple, lease_caps: tuple,
                                shared_budget: float) -> dict:
    """Each action inside its own lease; the composition tested against
    the global invariant separately. The two verdicts are independent
    axes, and the second never follows from the first."""
    local = tuple(a <= c for a, c in zip(amounts, lease_caps))
    joint = sum(amounts) <= shared_budget
    return {"local_admissible": all(local),
            "per_action": local,
            "compositional_admissible": joint,
            "joint_total": sum(amounts),
            "shared_budget": shared_budget,
            "law": "LOCAL_ADMISSIBILITY does not imply "
                   "COMPOSITIONAL_ADMISSIBILITY"}


# ── COMPOSABLE != COMPOSED ─────────────────────────────────────────────

@dataclass(frozen=True)
class LatentComposition:
    """L = (M_1..M_k, phi) in Adj(C_1851). The status field takes no
    constructor argument: nothing built by composition can be born
    witnessed."""
    latent_id: str
    motif_ids: tuple
    interface_map: tuple              # ((out_of, into), ...) declared
    status: str = field(default="ADJACENT_POSSIBLE", init=False)


def compose_adjacent(latent_id: str, motif_ids: tuple,
                     interface_map: tuple) -> LatentComposition:
    if not interface_map:
        raise ValueError("E_NO_DECLARED_INTERFACE")
    if len(motif_ids) < 2:
        raise ValueError("E_NOTHING_TO_COMPOSE")
    return LatentComposition(latent_id, tuple(motif_ids),
                             tuple(interface_map))


def witness_composition(latent: LatentComposition,
                        page_witness: str = "") -> dict:
    """The only promotion door, and it demands a page."""
    if not page_witness:
        return {"verdict": "REFUSED", "reason": "E_COMPOSABLE_IS_NOT_COMPOSED",
                "status": latent.status}
    return {"verdict": "WITNESSED_COMPOSITION", "latent_id": latent.latent_id,
            "page_witness": page_witness}


def freeze_latent_set(latents: tuple) -> dict:
    """Hash the adjacent-possible set BEFORE any post-1851 exposure —
    the clean half of the blind experiment."""
    return {"latent_freeze_hash": canon_hash(
                [(l.latent_id, l.motif_ids, l.interface_map)
                 for l in latents]),
            "count": len(latents),
            "all_adjacent_possible": all(
                l.status == "ADJACENT_POSSIBLE" for l in latents)}


# ── NO NAMESPACE, NO SEMANTICS ─────────────────────────────────────────

def decode(movement: str, codebook: dict | None = None) -> dict:
    """m ⊬ A. Only (m, C) ⊢ A. The telegraph's needle carries no
    meaning as physical substance; the code supplies interpretation."""
    if codebook is None:
        return {"verdict": "REFUSED", "reason": "E_NO_NAMESPACE",
                "law": "representation without namespace cannot carry "
                       "sovereign semantics"}
    if movement not in codebook:
        return {"verdict": "UNKNOWN", "movement": movement}
    return {"verdict": "DECODED", "symbol": codebook[movement],
            "under": sorted(codebook.items()).__len__() and "codebook"}


# ── ROOTS, NOT PASSAGES ────────────────────────────────────────────────

def independent_roots(witnesses: tuple) -> dict:
    """A(q) = f(independent roots, directness, source class, temporal
    fit) — never f(number of agreeing passages)."""
    roots = {w["root"] for w in witnesses}
    return {"passages": len(witnesses),
            "independent_roots": len(roots),
            "roots": sorted(roots),
            "law": "retrieval density != epistemic independence"}


# ── NOVELTY IS FOUR-AXIS ───────────────────────────────────────────────

@dataclass(frozen=True)
class NoveltyDecomposition:
    """N = (N_P, N_M, N_C, N_G). The axes never self-aggregate."""
    n_primitive: float
    n_motif: float
    n_composition: float
    n_governance: float

    def aggregate(self, weights: dict) -> float:
        required = {"n_primitive", "n_motif", "n_composition",
                    "n_governance"}
        if set(weights) != required:
            raise ValueError("E_WEIGHTS_UNDECLARED")
        return sum(getattr(self, k) * weights[k] for k in required)


# ── MODEL-OPTIMAL != WORLD-ADMISSIBLE ──────────────────────────────────

def recommend(model_optimal: str, practical_constraints: tuple) -> dict:
    """The Great Circle indicator's own caveat, as law: the geometric
    optimum may be operationally unusable, and the output is a
    recommendation either way — never an actuation."""
    return {"recommendation": model_optimal,
            "executes": False,
            "constraints_noted": tuple(practical_constraints),
            "world_admissibility": ("UNKNOWN" if practical_constraints
                                    else "UNCONSTRAINED_AS_DECLARED"),
            "law": "argmin(distance) != argmin(practical cost)"}
