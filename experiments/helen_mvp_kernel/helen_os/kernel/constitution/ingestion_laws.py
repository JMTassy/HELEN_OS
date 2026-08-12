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

# CORRECTED 2026-08-12: the decision state is PARTIALLY ORDERED, not a
# scalar chain. The operator ruling: "EXECUTED and DECIDED describe
# different dimensions; something can be operationally executed without
# a legitimate corporate decision, which is precisely the failure HELEN
# must detect." A chain cannot represent that pathology at all — it is
# the same correction the historical benchmark forced when CLAIM /
# DEMONSTRATION / JUDGMENT / ROBUSTNESS stopped being one ladder.
DECISION_AXES = ("proposal", "discussion", "approval", "authority",
                 "execution", "receipt")

# which witness kinds can establish which axis. No kind establishes two.
AXIS_WITNESS_KINDS = {
    "proposal": frozenset({"source_statement", "written_proposal"}),
    "discussion": frozenset({"transcript", "minutes"}),
    "approval": frozenset({"operator_admission", "corporate_record"}),
    "authority": frozenset({"signed_instrument", "corporate_record"}),
    "execution": frozenset({"execution_receipt", "system_log"}),
    "receipt": frozenset({"payment_receipt", "counterparty_receipt"}),
}

# retained for the legacy linear reading ONLY where a crossing really is
# sequential; never used to decide a decision state.
DECISION_LATTICE = ("PROPOSED", "DISCUSSED", "ACCEPTED_IN_PRINCIPLE",
                    "OPERATOR_DECIDED", "EXECUTED", "RECEIPTED")

DECISION_WITNESS_KINDS = frozenset().union(*AXIS_WITNESS_KINDS.values())

SECRECY_ORDER = ("S0", "S1", "S2", "S3", "S4")


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


def _rank(state: str) -> int:
    if state not in DECISION_LATTICE:
        raise ValueError("E_UNKNOWN_DECISION_STATE")
    return DECISION_LATTICE.index(state)


# ── CH-01: the decision-state lattice ───────────────────────────────────

def establish_axis(axis: str, witness: dict) -> dict:
    """Establish ONE axis of the decision signature. Axes are
    independent: establishing 'execution' says nothing about
    'approval'. A generated summary establishes nothing, ever."""
    if axis not in DECISION_AXES:
        raise ValueError("E_UNKNOWN_DECISION_AXIS")
    kind = witness.get("kind", "")
    if kind == "generated_summary":
        return {"verdict": "REFUSED", "reason": "E_SUMMARY_IS_NOT_A_VERDICT",
                "law": "a summarizer may reduce information; it may "
                       "never upgrade decision status"}
    if kind not in AXIS_WITNESS_KINDS[axis] or not witness.get("source_ref"):
        return {"verdict": "REFUSED", "reason": "E_UNWITNESSED_AXIS",
                "axis": axis,
                "accepted_kinds": sorted(AXIS_WITNESS_KINDS[axis])}
    return {"verdict": "ESTABLISHED", "axis": axis, "witness_kind": kind,
            "source_ref": witness["source_ref"]}


def decision_signature(witnesses: tuple) -> dict:
    """sigma(x) = (proposal, discussion, approval, authority,
    execution, receipt) — six independent credentials. Flags the
    pathology a scalar chain cannot express: EXECUTED without
    APPROVAL/AUTHORITY, i.e. something operationally done that no
    legitimate decision ever authorized."""
    sig = {a: "UNKNOWN" for a in DECISION_AXES}
    for w in witnesses:
        r = establish_axis(w["axis"], w)
        if r["verdict"] == "ESTABLISHED":
            sig[w["axis"]] = "WITNESSED"
    executed_unapproved = (sig["execution"] == "WITNESSED" and
                           (sig["approval"] != "WITNESSED" or
                            sig["authority"] != "WITNESSED"))
    return {"signature": sig,
            "executed_without_decision": executed_unapproved,
            "alarm": ("E_EXECUTED_WITHOUT_DECISION" if executed_unapproved
                      else None),
            "law": "EXECUTED and DECIDED are different dimensions; a "
                   "scalar chain cannot represent their divergence"}


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


def retention_decision(secrecy_class: str, minimization_basis: str = "",
                       retention_obligation: str = "") -> dict:
    """OPERATOR TIGHTENING 2026-08-12: 'full-private preservation' for
    S3 is a POLICY decision, not a constitutional default.

        PRIVATE does not imply PRESERVE_ALL.

    For PII — CVs, reservations, health remarks — minimization and
    retention obligations may argue for deliberately NOT keeping
    everything forever. A high secrecy class raises the protection
    bar; it never by itself authorizes indefinite retention."""
    if secrecy_class not in SECRECY_ORDER:
        raise ValueError("E_UNKNOWN_SECRECY_CLASS")
    if SECRECY_ORDER.index(secrecy_class) < SECRECY_ORDER.index("S3"):
        return {"verdict": "ORDINARY_RETENTION", "class": secrecy_class}
    if not (minimization_basis and retention_obligation):
        return {"verdict": "RETENTION_UNDECIDED",
                "reason": "E_PRESERVE_ALL_IS_NOT_A_DEFAULT",
                "missing": [n for n, v in
                            (("minimization_basis", minimization_basis),
                             ("retention_obligation", retention_obligation))
                            if not v],
                "law": "PRIVATE does not imply PRESERVE_ALL; secrecy "
                       "class raises protection, never retention rights"}
    return {"verdict": "RETENTION_DECIDED", "class": secrecy_class,
            "minimization_basis": minimization_basis,
            "retention_obligation": retention_obligation}


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
