"""HELEN_CORE_V1 — the constitutional spine as a typed, executable projection.

NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none.

This is not another organ. It is a compression: the eight durable
modules, exactly twelve constitutional invariants, the canonical
runtime transition, and a typed evidence/status registry — extracted
from the overgrown corpus so the spine is findable again. References
back to the historical material live in the registry entries, not here.

The spine:
    Meaning may bloom freely. State must be earned.
    Trust Reality = Replay(ledger).
    memory != ledger · admission != external truth · render != authority.

The anti-narrative-virus law (the Gnostic-trap chiddush) is structural:
an uncertified gap is preserved as UNKNOWN/HOLD, never story-bridged.
Narrative is strictly orthogonal to state mutation: N(x) ⊥ ΔG.

Deterministic: no wall-time, no randomness; frames are inputs.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field

# ═══ The eight modules, with authority boundaries ═══════════════════════

MODULES = {
    "kernel":        {"authority": "SOVEREIGN_MINIMAL",
                      "owns": "identity law, reducer, append-only ledger, replay, receipt admission"},
    "governance":    {"authority": "CONSTITUTIONAL",
                      "owns": "invariants, authority classes, effect ceilings, admission rules"},
    "context_compiler": {"authority": "NONE",
                      "owns": "intent routing, scope isolation, evidence selection, omission records"},
    "memory_fabric": {"authority": "NONE",
                      "owns": "retrieval, dedup, continuity, belief candidates — recall, never truth"},
    "execution_gateway": {"authority": "LEASED",
                      "owns": "sandbox boundaries, capability leases, budgets, rollback"},
    "evidence_witness_plane": {"authority": "NONE",
                      "owns": "provenance, claim status, contradictions, independent recomputation"},
    "evaluator_adaptation": {"authority": "NONE_OVER_LAW",
                      "owns": "metrics, calibration, routing adaptation — never sovereign law"},
    "shell_experiences": {"authority": "NONE",
                      "owns": "cockpit, Garden, Warren, WULMOJI, games — visibility, never truth"},
}

# ═══ Exactly twelve constitutional invariants (fixture-enforced) ═════════

INVARIANTS = (
    ("I01", "SPEC != IMPL != RUN != WITNESSED_RUN != SYSTEM_PROPERTY"),
    ("I02", "P(x) does not transport to P(f(x)) without a transport witness"),
    ("I03", "PASS@F0 does not imply PASS@F1"),
    ("I04", "W@F0 does not imply W@F1 — evidence is non-fungible across frames"),
    ("I05", "no coverage certificate => UNKNOWN, never TRANSPORT"),
    ("I06", "D(W) = D+ u D-; U nonempty => UNKNOWN when the property may depend on U"),
    ("I07", "derive root -> bind -> execute -> typed emit; no caller-trust anywhere"),
    ("I08", "any state delta must pass through the governed commit boundary"),
    ("I09", "Fresh != ValidByTransport != Valid-as-object"),
    ("I10", "memory != ledger; render != authority; admission != external truth"),
    ("I11", "proposer != validator != sealer"),
    ("I12", "narrative is orthogonal to state; Garden A=0 mints no kappa, appends no ledger"),
)

# ═══ Canonical runtime transition ═══════════════════════════════════════

RUNTIME_TRANSITION = (
    "user", "intent+authority_router", "operation_boundary", "scope_isolation",
    "constitutional_context_compilation", "init_airlock", "proposal",
    "capability_check", "sandboxed_execution", "raw_result",
    "independent_witness", "receipt_candidate", "admission_gate",
    "ledger", "replayed_state", "shell_projection",
)

TRANSITION_DECLARATION_FIELDS = frozenset({
    "input_provenance", "preserved_invariants", "tolerated_loss",
    "effect_ceiling", "authority_requirements", "witness_requirements",
    "failure_rollback",
})


def validate_transition_declaration(decl: dict) -> tuple[bool, str]:
    missing = TRANSITION_DECLARATION_FIELDS - set(decl)
    if missing:
        return False, f"E_UNDECLARED_ARROW:{','.join(sorted(missing))}"
    return True, "OK"


# ═══ Typed evidence/status registry ═════════════════════════════════════

# The mandatory evidence-status ladder. Order is law: promotion climbs one
# rung at a time, and every rung above 'reported' costs a witness.
STATUSES = ("hypothesis", "reported", "fixture_green",
            "frame_bound_pass", "transported", "admitted")
PROVEN_STATUSES = frozenset({"fixture_green", "frame_bound_pass",
                             "transported", "admitted"})


@dataclass(frozen=True)
class WitnessReceipt:
    witness_id: str
    independent: bool                 # producer, verifier, sealer distinct
    raw_harness_ref: str              # inspectable raw artifact, not prose
    frame_id: str


@dataclass(frozen=True)
class RegistryEntry:
    entry_id: str
    title: str
    module: str
    status: str                       # one of STATUSES
    evidence: tuple = ()              # WitnessReceipts
    superseded_by: str = ""
    historical_refs: tuple = ()       # pointers back into the big corpus

    def __post_init__(self):
        if self.status not in STATUSES:
            raise ValueError(f"E_UNTYPED_STATUS:{self.status}")


def project_entry(entry: RegistryEntry) -> dict:
    """What retrieval/rendering may show. A hypothesis can NEVER surface
    as stable; a report can NEVER surface as proven. Display status is
    computed from evidence, never copied from prose."""
    witnessed = any(w.independent and w.raw_harness_ref for w in entry.evidence)
    if entry.status in PROVEN_STATUSES and not witnessed:
        display = f"{entry.status}_UNWITNESSED(DEMOTED:reported)"
        proven = False
    else:
        display = entry.status
        proven = entry.status in PROVEN_STATUSES and witnessed
    return {"entry_id": entry.entry_id, "display_status": display,
            "proven": proven, "superseded": bool(entry.superseded_by)}


def promote(entry: RegistryEntry, witness: WitnessReceipt | None) -> RegistryEntry:
    """Climb exactly one rung of the ladder. Every rung above 'reported'
    requires an independent witness with an inspectable raw harness —
    missing witness prevents promotion, producer-adjacent does not count."""
    idx = STATUSES.index(entry.status)
    if idx + 1 >= len(STATUSES) and entry.status == "admitted":
        raise ValueError("E_ALREADY_TOP")
    target = STATUSES[idx + 1]
    if target != "reported":
        if witness is None:
            raise ValueError("E_NO_WITNESS")
        if not witness.independent:
            raise ValueError("E_PRODUCER_ADJACENT_WITNESS")
        if not witness.raw_harness_ref:
            raise ValueError("E_NO_RAW_HARNESS")
        new_evidence = entry.evidence + (witness,)
    else:
        new_evidence = entry.evidence
    return RegistryEntry(entry.entry_id, entry.title, entry.module,
                         target, new_evidence,
                         entry.superseded_by, entry.historical_refs)


# ═══ Admission gate (recommends; owns no ledger) ════════════════════════

@dataclass(frozen=True)
class ReceiptCandidate:
    payload: str
    witness: WitnessReceipt | None
    contradictions_searched: bool = False
    contradictions_found: tuple = ()
    contradictions_resolved: bool = False


@dataclass(frozen=True)
class RenderArtifact:
    """A shell projection. Deliberately has no fields the gate reads."""
    surface: str
    content: str


def admission_gate(x) -> dict:
    """Only a ReceiptCandidate may even be considered. A RenderArtifact —
    however beautiful — is not a door (render cannot produce admission).
    The gate emits ELIGIBLE/HOLD recommendations; it writes nothing."""
    if isinstance(x, RenderArtifact):
        return {"verdict": "REJECT", "reason": "E_RENDER_IS_NOT_A_DOOR"}
    if not isinstance(x, ReceiptCandidate):
        return {"verdict": "REJECT", "reason": "E_ILL_TYPED"}
    if x.witness is None or not x.witness.independent:
        return {"verdict": "HOLD", "reason": "E_NO_INDEPENDENT_WITNESS"}
    if not x.contradictions_searched:
        return {"verdict": "HOLD", "reason": "E_CONTRADICTION_UNSEARCHED"}
    if x.contradictions_found and not x.contradictions_resolved:
        return {"verdict": "HOLD", "reason": "E_CONTRADICTION_OPEN"}
    return {"verdict": "ELIGIBLE", "reason": "OK"}   # operator/kernel admits


# ═══ Trust Reality = Replay(ledger) ═════════════════════════════════════

@dataclass(frozen=True)
class Ledger:
    events: tuple


@dataclass(frozen=True)
class MemorySnapshot:
    claimed_state: str


def replay(ledger: Ledger) -> str:
    h = hashlib.sha256()
    for e in ledger.events:
        h.update(json.dumps(e, sort_keys=True, separators=(",", ":")).encode())
    return h.hexdigest()


def trust_state(source) -> dict:
    """Memory cannot replace replay: only a Ledger yields Trust Reality."""
    if isinstance(source, Ledger):
        return {"trust_state": replay(source), "basis": "REPLAY"}
    if isinstance(source, MemorySnapshot):
        return {"trust_state": None, "basis": "REFUSED",
                "reason": "E_MEMORY_IS_NOT_LEDGER"}
    return {"trust_state": None, "basis": "REFUSED", "reason": "E_ILL_TYPED"}


# ═══ Live-state decay: no probe, no present tense ═══════════════════════

@dataclass(frozen=True)
class RuntimeReport:
    claim: str
    observed_frame: str


def live_claim(report: RuntimeReport, current_frame: str,
               probe_receipt: WitnessReceipt | None = None) -> dict:
    """A stale runtime report cannot become live state. Present-tense
    claims require a probe receipt bound to the current frame."""
    if probe_receipt is not None and probe_receipt.frame_id == current_frame:
        return {"verdict": "LIVE", "claim": report.claim}
    if report.observed_frame == current_frame:
        return {"verdict": "LIVE", "claim": report.claim}
    return {"verdict": "STALE_REPORT", "reason": "E_NO_LIVE_PROBE",
            "observed_frame": report.observed_frame}


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)
