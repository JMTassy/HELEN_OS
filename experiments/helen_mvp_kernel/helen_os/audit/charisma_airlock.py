"""CHARISMA_AIRLOCK_V0 — prestige invariance. 🔵 OBSERVED · authority=false.

HELEN already conserves LAWFUL authority: α(T(x)) ≤ α(x). But there is a second,
undeclared channel — PERCEIVED authority (π): titles, fame, claimed lineage,
initiation grades, endorsement/repetition counts, audience size, symbolic office.
None of these increases truth, independent evidence, or lawful capability, yet a
naive gate lets π leak into admission / evaluation / capability / promotion.

The airlock does NOT decide who is right. It proves whether an UNAUTHORIZED variable
moved the gate, by requiring the decision to be invariant to removal of prestige:

    D(identity, authority, evidence, prestige)  ==  D(identity, authority, evidence, ∅)

Divergence ⇒ HOLD_PRESTIGE_COUPLING — the decision depended on charisma, an
undeclared authority channel. "Charisma is attention with a hidden capability
request. Render it freely; admit none of it implicitly."

Lineage inflation (one source → ten delegated branches → ten agreeing reports ≠ ten
independent witnesses) is the evidential twin of this — handled by epistemic_roots
(N_epi / Λ_proxy). This module guards the *decision* channel; that one guards the
*evidence* channel.
Determinism: pure — the evaluator is passed in; the airlock only compares its verdicts.
"""
from __future__ import annotations

# Variables a governed gate MAY consider.
GOVERNED = frozenset({"identity", "authority", "evidence", "scope", "capability_lease"})

# Prestige variables that must never implicitly move a gate (perceived authority π).
PRESTIGE = frozenset({
    "title", "honorific", "fame", "audience_size", "lineage_claim", "initiation_grade",
    "endorsements", "repetition_count", "symbol", "aesthetic_intensity",
})


def strip_prestige(features: dict) -> dict:
    """Remove every prestige variable — the paired counterfactual for the airlock."""
    return {k: v for k, v in features.items() if k not in PRESTIGE}


def airlock(decision_fn, features: dict):
    """Run the evaluator on the full feature set and on the prestige-stripped set.
    Returns (invariant: bool, verdict: str). invariant=False ⇒ HOLD_PRESTIGE_COUPLING:
    prestige was an undeclared authority channel. Which decision is 'correct' is NOT
    determined here — only that an inadmissible variable influenced the gate."""
    d_full = decision_fn(features)
    d_stripped = decision_fn(strip_prestige(features))
    if d_full != d_stripped:
        return False, "HOLD_PRESTIGE_COUPLING"
    return True, "PRESTIGE_INVARIANT"


def declared_prestige(features: dict) -> set:
    """Which prestige variables are present (for the receipt — render freely, admit none)."""
    return {k for k in features if k in PRESTIGE}
