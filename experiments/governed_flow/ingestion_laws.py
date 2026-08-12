"""Ingestion laws — the six chiddush proposals from the 2026-08-12
dense-ingestion review, executable. Fixtures are deliberately generic:
the source packet's business content is S2/S3/S4 and stays out of this
published repository; only the LAWS cross the membrane.

NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none.

  CH-01  DECISION-STATE LATTICE   PROPOSED < DISCUSSED <
         ACCEPTED_IN_PRINCIPLE < OPERATOR_DECIDED < EXECUTED <
         RECEIPTED. One rung per witnessed crossing, and a generated
         summary is NEVER a witness (E_SUMMARY_IS_NOT_A_VERDICT).
  CH-02  PROVENANCE-EXPANDED DELTA   effective delta = enumeration ∪
         linked-IDs ∪ attachments. Enumeration alone is never an
         exhaustiveness certificate — the falsifier was a real 488 MB
         object visible by stable ID and invisible to search.
  CH-03  SUMMARY IS NOT A VERDICT   Where transcript and summary
         disagree in modality, the more conservative modality wins
         until explicitly witnessed; the summary is flagged OVERSTATED.
  CH-04  CAPACITY IS AN EXECUTION PRECONDITION   Configured workflow +
         valid logic + no capacity = no execution. Correctness
         receipts do not substitute for quota receipts.
  CH-05  FIELD-LEVEL SECRECY   PreservationClass(x) = sup over fields;
         authorized semantic projection excludes restricted fields
         without destroying the usable remainder.
  CH-06  ENGINE-FIRST IMPROVEMENT   Repairing an artifact changes one
         output; improving the generator changes the distribution of
         all future first shots. The two are different move types and
         must not be conflated in learning records.

Deterministic: no wall-time, no randomness, canonical serialization.
"""
from __future__ import annotations

import json

DECISION_LATTICE = ("PROPOSED", "DISCUSSED", "ACCEPTED_IN_PRINCIPLE",
                    "OPERATOR_DECIDED", "EXECUTED", "RECEIPTED")

# witness kinds that can carry a decision upward, one rung at a time.
DECISION_WITNESS_KINDS = frozenset({
    "operator_admission", "signed_instrument", "corporate_record",
    "execution_receipt", "payment_receipt"})

SECRECY_ORDER = ("S0", "S1", "S2", "S3", "S4")


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


def _rank(state: str) -> int:
    if state not in DECISION_LATTICE:
        raise ValueError("E_UNKNOWN_DECISION_STATE")
    return DECISION_LATTICE.index(state)


# ── CH-01: the decision-state lattice ───────────────────────────────────

def promote_decision(current: str, target: str, witness: dict) -> dict:
    """One rung, one source-bound witness. An NLP summary offering
    itself as the witness is the exact laundering this lattice
    exists to stop."""
    i, j = _rank(current), _rank(target)
    if j != i + 1:
        return {"verdict": "REFUSED", "reason": "E_LATTICE_SKIP",
                "from": current, "to": target}
    kind = witness.get("kind", "")
    if kind == "generated_summary":
        return {"verdict": "REFUSED", "reason": "E_SUMMARY_IS_NOT_A_VERDICT",
                "law": "no NLP summary may promote a statement upward"}
    if kind not in DECISION_WITNESS_KINDS or not witness.get("source_ref"):
        return {"verdict": "REFUSED", "reason": "E_UNWITNESSED_PROMOTION",
                "accepted_kinds": sorted(DECISION_WITNESS_KINDS)}
    return {"verdict": "PROMOTED", "from": current, "to": target,
            "witness_kind": kind, "source_ref": witness["source_ref"]}


# ── CH-03: conservative modality wins ───────────────────────────────────

def reconcile_modalities(transcript_state: str, summary_state: str) -> dict:
    """GeneratedSummary never outranks its transcript. The resolved
    state is the MINIMUM; a higher summary is flagged, not adopted."""
    t, s = _rank(transcript_state), _rank(summary_state)
    resolved = DECISION_LATTICE[min(t, s)]
    return {"resolved": resolved,
            "summary_status": "OVERSTATED" if s > t else "CONSISTENT",
            "law": "where transcript and summary differ in modality, "
                   "the more conservative modality wins until "
                   "explicitly witnessed"}


# ── CH-02: provenance-expanded delta ────────────────────────────────────

def effective_delta(enumerated: frozenset, linked_ids: frozenset,
                    attachment_ids: frozenset) -> dict:
    """Delta_effective = Delta_enum ∪ Delta_linked ∪ Delta_attach.
    The exhaustiveness verdict compares enumeration against the union
    — and says FALSE the moment provenance expansion found anything."""
    union = enumerated | linked_ids | attachment_ids
    missed = union - enumerated
    return {"effective_delta": union,
            "enumeration_hits": len(enumerated),
            "found_only_by_provenance": sorted(missed),
            "enumeration_exhaustive": not missed,
            "law": "enumeration is not an exhaustiveness certificate; "
                   "resolve linked stable IDs before declaring a delta "
                   "complete"}


# ── CH-04: capacity is an execution precondition ────────────────────────

def capacity_gate(workflow_configured: bool, logic_valid: bool,
                  capacity_receipt: str = "") -> dict:
    """A correct, configured workflow with zero quota does not run.
    Correctness receipts and capacity receipts are different receipts."""
    if not (workflow_configured and logic_valid):
        return {"verdict": "NOT_RUNNABLE", "reason": "E_NOT_CONFIGURED"}
    if not capacity_receipt:
        return {"verdict": "EXECUTION_DISABLED", "reason": "E_NO_CAPACITY",
                "law": "configured + valid + no capacity = no execution; "
                       "a correctness receipt is not a quota receipt"}
    return {"verdict": "RUNNABLE", "capacity_receipt": capacity_receipt}


# ── CH-05: field-level secrecy ──────────────────────────────────────────

def preservation_class(fields: dict) -> str:
    """PreservationClass(x) = sup over its fields' classes."""
    ranks = [SECRECY_ORDER.index(c) for c in fields.values()
             if c in SECRECY_ORDER]
    if len(ranks) != len(fields):
        raise ValueError("E_UNKNOWN_SECRECY_CLASS")
    return SECRECY_ORDER[max(ranks)] if ranks else "S0"


def semantic_projection(fields: dict, values: dict,
                        max_class: str) -> dict:
    """The authorized projection: fields above max_class are withheld
    BY NAME AND COUNT, never silently — and the remainder stays
    usable. An S4 subfield does not poison the whole object."""
    cap = SECRECY_ORDER.index(max_class)
    kept = {k: values[k] for k, c in fields.items()
            if SECRECY_ORDER.index(c) <= cap}
    withheld = sorted(k for k, c in fields.items()
                      if SECRECY_ORDER.index(c) > cap)
    return {"projected": kept, "withheld_fields": withheld,
            "withheld_count": len(withheld),
            "object_class": preservation_class(fields),
            "law": "restricted atoms are excluded field-wise; the "
                   "business remainder survives"}


# ── CH-06: engine-first improvement ─────────────────────────────────────

def improvement_scope(move: str) -> dict:
    """Two different move types. A learning record must say which one
    it is — conflating them overstates instance fixes and understates
    generator fixes."""
    if move == "instance_repair":
        return {"move": move, "changes": "one artifact",
                "distributional_effect": False}
    if move == "generator_improvement":
        return {"move": move,
                "changes": "distribution of future first shots",
                "distributional_effect": True,
                "note": "strictly stronger: repairing G is weaker than "
                        "improving the generator of G"}
    raise ValueError("E_UNKNOWN_IMPROVEMENT_MOVE")
