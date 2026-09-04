"""COGNITION_REPLACEMENT_INVARIANT_V0 — the enterprise falsifier. 🔵 OBSERVED · authority=false.

The enterprise thesis under test:

    MUTABLE COGNITION + STABLE INSTITUTIONAL SEMANTICS.
    Replace the cognitive substrate C with a deterministically stupid stub C₀ and the
    application's STRUCTURE must be unchanged:  C → C₀  ∧  ΔΠ_struct = 0.

Π_struct captures institutional structure — workflow graph, transition legality, receipt
discipline, gate invocation, tenant isolation, replay, runtime identity — and DELIBERATELY
EXCLUDES cognition-quality-dependent content (extracted values, the recommendation, the final
business outcome). Quality is allowed to collapse; structure is not.

This module is a FALSIFIER, so it ships its own positive control: a `leaky` application in which
cognition's recommendation directly drives a state transition (LLMOutput ⇒ StateTransition, the
forbidden morphism). The leak is invisible under a cooperative C and only surfaces when cognition
is replaced by C₀ — which is exactly what the invariant is meant to detect:

    cognition_replacement_invariant(well_formed, [C, C₀]) is True
    cognition_replacement_invariant(leaky,       [C, C₀]) is False   ← the falsifier must fail here

The laws made executable (each a "no layer mints the next layer's privilege"):
    Recommend ⊬ Authorize ⊬ Execute      LLMOutput ⊬ StateTransition
    WorkerDeath ⊬ KnowledgeLoss          ApplicationSemantics ⊥ ModelSelection
    Replayable ⊬ Correct                 CanRead ⊬ CanReason ⊬ CanPropose ⊬ CanAuthorize ⊬ CanExecute
Determinism: pure. No clock, no randomness.
"""
from __future__ import annotations

from dataclasses import dataclass, field, fields
from typing import Callable, List, Optional, Tuple

# ─────────────────────────── workflow (owns δ, not cognition) ───────────────────────────
NEW, EXTRACTED, VERIFIED, APPROVED, EXECUTED, HOLD, CLOSED = (
    "NEW", "EXTRACTED", "VERIFIED", "APPROVED", "EXECUTED", "HOLD", "CLOSED")

# δ : S × Event ⇀ S — the ONLY legal transitions. Cognition may emit event payloads; it may
# never define this table and may never write a state directly.
TRANSITION_TABLE = {
    (NEW, "extracted"): EXTRACTED,
    (EXTRACTED, "verified_ok"): VERIFIED,
    (EXTRACTED, "verified_hold"): HOLD,
    (VERIFIED, "approved"): APPROVED,
    (VERIFIED, "hold"): HOLD,
    (APPROVED, "executed"): EXECUTED,
    (EXECUTED, "closed"): CLOSED,
    (HOLD, "closed"): CLOSED,
}
WORKFLOW_STATES = (NEW, EXTRACTED, VERIFIED, APPROVED, EXECUTED, HOLD, CLOSED)


def _table_signature() -> Tuple[Tuple[str, str, str], ...]:
    return tuple(sorted((s, e, d) for (s, e), d in TRANSITION_TABLE.items()))


# ─────────────────────────── cognition (a replaceable dependency) ───────────────────────────
ACT, NO_ACTION, OK, TIMEOUT = "ACT", "NO_ACTION", "OK", "__TIMEOUT__"


@dataclass(frozen=True)
class Candidate:
    """A cognitive proposal. Pure data — an event PAYLOAD, never a transition."""
    op: str                       # "extract" | "verify" | "recommend"
    payload: object               # content — VARIES by cognition, excluded from Π_struct
    well_formed: bool = True


class Cognition:
    """Interface. Every method returns a Candidate; none may touch the workflow or the ledger."""
    def extract(self, doc: dict) -> Candidate: raise NotImplementedError
    def verify(self, fields: Optional[dict]) -> Candidate: raise NotImplementedError
    def recommend(self, fields: Optional[dict]) -> Candidate: raise NotImplementedError


class RealCognition(Cognition):
    def extract(self, doc): return Candidate("extract", {"amount": 500, "payee": "ACME"})
    def verify(self, fields): return Candidate("verify", OK)
    def recommend(self, fields): return Candidate("recommend", ACT)


class StubCognition(Cognition):
    """C₀ — deterministically stupid. Permissive at verify (so the recommend-stage leak is
    reachable), then declines to act. Fixed fixtures, no intelligence."""
    def extract(self, doc): return Candidate("extract", {"amount": 0, "payee": "ACME"})
    def verify(self, fields): return Candidate("verify", OK)
    def recommend(self, fields): return Candidate("recommend", NO_ACTION)


class TimeoutCognition(Cognition):
    def extract(self, doc): raise TimeoutError("cognition timed out")
    def verify(self, fields): raise TimeoutError("cognition timed out")
    def recommend(self, fields): raise TimeoutError("cognition timed out")


class MalformedCognition(Cognition):
    def extract(self, doc): return Candidate("extract", object(), well_formed=False)
    def verify(self, fields): return Candidate("verify", object(), well_formed=False)
    def recommend(self, fields): return Candidate("recommend", object(), well_formed=False)


class AdversarialCognition(Cognition):
    """Verifies OK and demands action, but on an out-of-policy effect. The effect gate — not the
    cognition — decides; the demand is denied."""
    def extract(self, doc): return Candidate("extract", {"amount": 10 ** 9, "payee": "GHOST"})
    def verify(self, fields): return Candidate("verify", OK)
    def recommend(self, fields): return Candidate("recommend", ACT)


def _safe(call: Callable[[], Candidate], op: str) -> Candidate:
    """Cognitive failure degrades utility, not structure — a crash becomes a timeout candidate."""
    try:
        return call()
    except Exception:
        return Candidate(op, TIMEOUT, well_formed=False)


# ─────────────────────────── gates, connector, receipts ───────────────────────────
POLICY_MAX_AMOUNT = 100_000
POLICY_PAYEES = frozenset({"ACME", "VENDOR-1"})


@dataclass(frozen=True)
class RuntimeIdentity:
    commit: str
    container_digest: str
    schema_version: str
    workflow_version: str
    policy_version: str
    model_policy_version: str

    def keys(self) -> Tuple[str, ...]:
        return tuple(sorted(f.name for f in fields(self)))


@dataclass(frozen=True)
class Receipt:
    request_id: str
    principal: str
    tenant: str
    from_state: str
    event: str
    to_state: str
    policy_decision: str
    authority: str
    runtime_keys: Tuple[str, ...]


@dataclass
class Connector:
    invocations: List[Tuple[str, bool]] = field(default_factory=list)   # (tau_id, permit_e)

    def invoke(self, tau_id: str, permit_e: bool) -> None:
        self.invocations.append((tau_id, permit_e))


def permit_c(ctx: dict, tenant: str) -> bool:
    """Cognition gate: may this cognition read this tenant? Cross-tenant read is DENIED."""
    return ctx.get("tenant") == tenant


def permit_e(fields: Optional[dict], ctx: dict) -> bool:
    """Effect gate: authority is capability ∧ policy — derived from context, never from cognition."""
    if "execute" not in ctx.get("capabilities", ()):        # capability
        return False
    if not fields:
        return False
    return fields.get("amount", 10 ** 18) <= POLICY_MAX_AMOUNT and fields.get("payee") in POLICY_PAYEES


# ─────────────────────────── the run, its transition log, and Π_struct ───────────────────────────
@dataclass
class _Transition:
    from_state: str
    event: Optional[str]     # None ⇒ a raw state write (a leak: no workflow event)
    to_state: str
    receipt: Optional[Receipt]
    via_engine: bool


@dataclass
class RunResult:
    final_state: str
    transitions: List[_Transition]
    connector: Connector
    permit_c_evaluated: bool
    tenant_isolation_holds: bool
    runtime: RuntimeIdentity


def _fire(run: RunResult, from_state: str, event: str, receipt: Receipt) -> str:
    """Legal, receipted, engine-owned transition."""
    to = TRANSITION_TABLE[(from_state, event)]
    run.transitions.append(_Transition(from_state, event, to, receipt, via_engine=True))
    return to


def _receipt(ctx, event, from_state, to_state, decision, runtime) -> Receipt:
    return Receipt(
        request_id=ctx["request_id"], principal=ctx["principal"], tenant=ctx["tenant"],
        from_state=from_state, event=event, to_state=to_state,
        policy_decision=decision, authority="workflow", runtime_keys=runtime.keys())


def run_application(cognition: Cognition, ctx: dict, runtime: RuntimeIdentity, *, leaky: bool) -> RunResult:
    """Drive one invoice through the substrate with a given cognition. `leaky=True` installs the
    forbidden morphism (recommendation directly closes the object) to serve as the positive control."""
    doc = {"raw": "invoice.pdf"}
    run = RunResult(
        final_state=NEW, transitions=[], connector=Connector(),
        permit_c_evaluated=False,
        tenant_isolation_holds=(permit_c({"tenant": "other"}, ctx["tenant"]) is False),
        runtime=runtime)

    run.permit_c_evaluated = True
    if not permit_c(ctx, ctx["tenant"]):
        return run

    state = NEW
    # extract → EXTRACTED
    ce = _safe(lambda: cognition.extract(doc), "extract")
    fields = ce.payload if (ce.well_formed and isinstance(ce.payload, dict)) else None
    state = _fire(run, state, "extracted", _receipt(ctx, "extracted", state, EXTRACTED, "n/a", runtime))

    # verify → VERIFIED or HOLD (business OUTCOME; structure identical either way)
    cv = _safe(lambda: cognition.verify(fields), "verify")
    ok = cv.well_formed and cv.payload == OK and fields is not None
    ev = "verified_ok" if ok else "verified_hold"
    state = _fire(run, state, ev, _receipt(ctx, ev, state, TRANSITION_TABLE[(state, ev)], "n/a", runtime))

    if state == VERIFIED:
        cr = _safe(lambda: cognition.recommend(fields), "recommend")
        wants_act = cr.well_formed and cr.payload == ACT
        if leaky and not wants_act:
            # ── THE LEAK ── cognition's non-recommendation directly writes state: no event, no
            # receipt, no gate. Invisible under RealCognition; detonates under C₀.
            run.transitions.append(_Transition(state, None, CLOSED, None, via_engine=False))
            state = CLOSED
        elif wants_act:
            allowed = permit_e(fields, ctx)                 # effect gate is the authority
            if allowed:
                run.connector.invoke(ctx["request_id"], permit_e=True)   # only under Permit_E
                state = _fire(run, state, "approved", _receipt(ctx, "approved", state, APPROVED, "PERMIT", runtime))
                state = _fire(run, state, "executed", _receipt(ctx, "executed", state, EXECUTED, "PERMIT", runtime))
            else:
                state = _fire(run, state, "hold", _receipt(ctx, "hold", state, HOLD, "DENY", runtime))
        else:
            state = _fire(run, state, "hold", _receipt(ctx, "hold", state, HOLD, "NO_ACTION", runtime))

    if state in (EXECUTED, HOLD):
        state = _fire(run, state, "closed", _receipt(ctx, "closed", state, CLOSED, "n/a", runtime))

    run.final_state = state
    return run


# structural predicates — each TRUE for any well-formed run, whatever cognition produced
def _all_transitions_legal(run: RunResult) -> bool:
    return all(t.event is not None and TRANSITION_TABLE.get((t.from_state, t.event)) == t.to_state
               for t in run.transitions)


def _every_transition_has_receipt(run: RunResult) -> bool:
    return all(t.receipt is not None for t in run.transitions)


def _cognition_never_wrote_state(run: RunResult) -> bool:
    return all(t.via_engine for t in run.transitions)


def _replay_reconstructs_final(run: RunResult) -> bool:
    state = NEW
    for t in run.transitions:
        if t.event is None or (state, t.event) not in TRANSITION_TABLE:
            return False
        state = TRANSITION_TABLE[(state, t.event)]
    return state == run.final_state


def _connector_only_under_permit_e(run: RunResult) -> bool:
    return all(permit for _, permit in run.connector.invocations)


RECEIPT_SCHEMA = tuple(sorted(f.name for f in fields(Receipt)))


def pi_struct(run: RunResult) -> Tuple:
    """Canonical STRUCTURAL signature. Excludes final_state, field values, recommendation, receipt
    count, connector call count — everything that legitimately varies with cognition quality."""
    return (
        ("workflow_states", WORKFLOW_STATES),
        ("transition_table", _table_signature()),
        ("all_transitions_legal", _all_transitions_legal(run)),
        ("every_transition_has_receipt", _every_transition_has_receipt(run)),
        ("cognition_never_wrote_state", _cognition_never_wrote_state(run)),
        ("connector_only_under_permit_e", _connector_only_under_permit_e(run)),
        ("permit_c_evaluated", run.permit_c_evaluated),
        ("tenant_isolation_holds", run.tenant_isolation_holds),
        ("replay_reconstructs_final", _replay_reconstructs_final(run)),
        ("receipt_schema", RECEIPT_SCHEMA),
        ("runtime_identity_keys", run.runtime.keys()),
    )


DEFAULT_RUNTIME = RuntimeIdentity(
    commit="d8ab22f", container_digest="sha256:stub", schema_version="1",
    workflow_version="1", policy_version="1", model_policy_version="1")


def _default_ctx() -> dict:
    return {"request_id": "req-1", "principal": "operator", "tenant": "tenant-A",
            "capabilities": ("read", "execute")}


def cognition_replacement_invariant(cognitions, *, leaky: bool,
                                    ctx: Optional[dict] = None,
                                    runtime: Optional[RuntimeIdentity] = None):
    """Run the substrate with each cognition; return (holds, signatures).

    `holds` is True iff Π_struct is identical across all cognitions — i.e. the application's
    institutional structure survived replacement of its intelligence. ΔΠ_struct = 0."""
    ctx = ctx or _default_ctx()
    runtime = runtime or DEFAULT_RUNTIME
    sigs = [pi_struct(run_application(c, dict(ctx), runtime, leaky=leaky)) for c in cognitions]
    holds = all(s == sigs[0] for s in sigs)
    return holds, sigs
