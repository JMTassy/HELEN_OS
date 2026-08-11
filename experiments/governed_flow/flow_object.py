"""F — the Governed Flow Object. The smallest executable HELEN kernel
primitive.

NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none.

    F = (E, S, X, J, P, A, R, Pi)

The agent is an executor; the flow is the persistent object. This
module makes the Director's recap executable, law by law:

  FLOW IDENTITY != MODEL IDENTITY   flow_identity() hashes operators,
      sources and edge structure — never the actor. Swap the executor
      (goblin, claude, script, human) and the identity is unchanged.

  ONE FLOW -> ONE TRACE -> MANY BOUNDED PROJECTIONS   The trace is a
      causal provenance DAG. Receipts live on EDGES, not nodes:
      M_delta = (S_i, f_i, S_i+1, C_i, tau_i, Pi_i, W_i).

  PROJECTION COUNT != EVIDENCE COUNT   Five views descending from one
      call are ONE witness: evidence_count() is the size of the UNION
      of ancestor source sets, never the number of views.

  CYCLIC INTELLIGENCE ∧ ACYCLIC AUTHORITY   Data may loop through the
      world; the authority graph may not loop at all. An action cannot
      authorize itself retroactively, a receipt cannot mint the
      permission that should have preceded execution, a learned policy
      cannot issue the authority to install itself.

  CAPABILITY != AUTHORITY   Leases are scope-bound and time-bound:
      L = (subject, capability, scope, resource, t_start, t_end,
      constraints, issuer). Valid(L, a, t) or no execution.

  VALID AT INTAKE != VALID AT EXECUTION   High-effect execution is
      Authorize(a,t0) ∧ Revalidate(a,t1) ∧ Execute(a,t1) — lease
      expiry, policy drift, and revocation all break the chain.

  JUDGE = J_E ⊕ J_O   EvidenceSupports(c) never implies Permission(a).

  SOURCE OF TRUTH = TRACE != PROJECTION   Views are regenerated, not
      synchronized; v in Dep(P_i) => Invalidate(P_i) when v changes,
      and ONLY the affected views.

  STORED STATE != REPLAYED STATE   A state without a reconstructible
      path is STORED_STATE_ONLY; with an unreplayed path it is a
      TRANSFORMATION_CLAIM; only replay convergence makes it a
      WITNESSED_TRANSFORMATION.

  LEARN = L0 ⊕ L1 ⊕ L2 ⊕ L3   with authority budgets L0<L1<L2<<L3.
      L3 (constitutional mutation) requires the full meta-change path:
      proposal, compile, attest, decide, activate, audit — in order —
      plus principal admission. Learning never mints a lease.

  CONSERVATION   Q_in = Q_out + Q_retained + Q_loss ± eps, and for
      authority: Effects_executed ⊆ Effects_authorized — governance as
      accounting over bounded quantities.

The four constitutional inequalities are structural, not advisory:
extraction != truth (there is no TRUE in the evidence vocabulary);
evaluation != permission; projection != evidence; learning != authority.

ACT is not re-invented here: the A_E gate (experiments/effect_gate) is
imported and sits at the lease boundary of the cycle.

Deterministic: time is passed in, no randomness, canonical JSON.
"""
from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import dataclass, field, replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "effect_gate"))

from effect_gate import (  # noqa: E402  — A_E, not a copy of it
    Admission,
    EffectProposal,
    NamedLoss,
    admission_gate,
)

SIX_OPS = ("SENSE", "EXTRACT", "JUDGE", "PROJECT", "ACT", "LEARN")

AUTHORITY_ORDER = {"SENSE": 0, "EXTRACT": 0, "JUDGE": 1, "PROJECT": 1,
                   "ACT": 2, "LEARN_PERSISTENT": 3}

# extraction != truth: the vocabulary has no TRUE to promote into.
EVIDENCE_STATES = ("HYPOTHESIS", "REPORTED", "WITNESSED")

LEARN_TIERS = ("L0_EPHEMERAL", "L1_HEURISTIC", "L2_INSTITUTIONAL",
               "L3_CONSTITUTIONAL")

META_CHANGE_STAGES = ("proposal", "compile", "attest", "decide",
                      "activate", "audit")


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


def canon_hash(obj) -> str:
    return hashlib.sha256(canon(obj).encode("utf-8")).hexdigest()


# ── four record types that must never collapse into one "receipt" ──────
# A proposal receipt says SOMETHING WAS STAGED. An authorization record
# says PERMISSION EXISTED AT t0. An execution receipt says THE EFFECT
# RAN AT t1. A replay verdict says THE HISTORY RECONSTRUCTS. Each is a
# distinct type; require_kind makes substitution a refusal, which is
# the authority-acyclicity law enforced at the type level: an execution
# receipt handed back as an authorization is exactly the
# receipt-minted-permission cycle.

@dataclass(frozen=True)
class ProposalReceipt:
    kind: str = field(default="PROPOSAL_RECEIPT", init=False)
    effect_id: str = ""
    effect_class: str = ""
    t: int = 0
    content_hash: str = ""


@dataclass(frozen=True)
class AuthorizationRecord:
    kind: str = field(default="AUTHORIZATION_RECORD", init=False)
    action_id: str = ""
    lease_id: str = ""
    t0: int = 0
    policy_version: str = ""


@dataclass(frozen=True)
class ExecutionReceipt:
    kind: str = field(default="EXECUTION_RECEIPT", init=False)
    action_id: str = ""
    lease_id: str = ""
    t1: int = 0
    receipt_hash: str = ""


@dataclass(frozen=True)
class ReplayVerdict:
    kind: str = field(default="REPLAY_VERDICT", init=False)
    grade: str = ""
    detail: str = ""


def require_kind(record, expected: str) -> dict | None:
    """None when the record is what it claims to be; a refusal dict
    otherwise. A record of the wrong kind is not a weaker version of
    the right one — it is a category error."""
    got = getattr(record, "kind", None)
    if got != expected:
        return {"verdict": "REFUSED", "reason": "E_RECEIPT_KIND_MISMATCH",
                "expected": expected, "got": got}
    return None


def propose(proposal: EffectProposal, t: int) -> ProposalReceipt:
    """Staging mints a proposal receipt — a record that something
    reached the gate, and nothing more."""
    return ProposalReceipt(
        effect_id=proposal.effect_id, effect_class=proposal.effect_class,
        t=t, content_hash=canon_hash([proposal.effect_id, proposal.kind,
                                      proposal.text]))


# ── durable identity vs mutable runtime instance ────────────────────────

LIFECYCLE = ("CREATED", "SENSE", "EXTRACT", "JUDGE", "PROJECT", "ACT",
             "RECEIPT", "MEMORY", "REPLAY", "LEARN", "QUIESCENT")


@dataclass(frozen=True)
class FlowInstance:
    """The MUTABLE runtime object: a cursor and an executor binding.
    The durable flow is (flow_id, trace, flow_identity); the instance
    is where it currently sits and who is currently turning the crank.
    Killing and restarting an instance loses nothing durable."""
    instance_id: str
    flow_id: str
    executor: str
    stage: str = "CREATED"

    def __post_init__(self):
        if self.stage not in LIFECYCLE:
            raise ValueError("E_UNKNOWN_STAGE")


def advance(inst: FlowInstance) -> FlowInstance:
    i = LIFECYCLE.index(inst.stage)
    if i == len(LIFECYCLE) - 1:
        raise ValueError("E_FLOW_QUIESCENT")
    return replace(inst, stage=LIFECYCLE[i + 1])


def jump(inst: FlowInstance, target: str) -> FlowInstance:
    """One stage at a time. SENSE cannot leap to ACT — the skipped
    stages are exactly where governance lives."""
    if target not in LIFECYCLE:
        raise ValueError("E_UNKNOWN_STAGE")
    if LIFECYCLE.index(target) != LIFECYCLE.index(inst.stage) + 1:
        raise ValueError("E_STAGE_SKIP")
    return replace(inst, stage=target)


def rebind(inst: FlowInstance, executor: str) -> FlowInstance:
    """Swap the enzyme mid-flow. The instance keeps its cursor; the
    flow keeps its identity; only the binding changes."""
    return replace(inst, executor=executor)


# ── the trace: causal provenance DAG, receipts on edges ─────────────────

@dataclass(frozen=True)
class TraceEdge:
    """One witnessed-or-claimed transformation. The receipt belongs
    HERE — to the edge — because STATE != TRANSFORMATION CLAIM."""
    src: str
    dst: str
    operator: str                     # f_i — name in the registry
    actor: str                        # the executor. NOT identity.
    t: int
    evidence_state: str = "REPORTED"
    policy_version: str = "v1"
    lease_ref: str = ""
    receipt: str = ""

    def __post_init__(self):
        if self.evidence_state not in EVIDENCE_STATES:
            raise ValueError("E_UNKNOWN_EVIDENCE_STATE")   # no TRUE exists


@dataclass(frozen=True)
class Trace:
    """Append-only DAG: every new edge must point to an existing src
    and a NEW or existing dst that never creates a back-path. Data may
    cycle through the WORLD; the trace of one flow is causal, forward."""
    flow_id: str
    nodes: tuple = ()                 # node ids, insertion-ordered
    edges: tuple = ()                 # TraceEdge

    def add(self, edge: TraceEdge) -> "Trace":
        if edge.src not in self.nodes:
            raise ValueError("E_EDGE_FROM_NOWHERE")
        nodes = self.nodes if edge.dst in self.nodes else self.nodes + (edge.dst,)
        t2 = replace(self, nodes=nodes, edges=self.edges + (edge,))
        if t2._reaches(edge.dst, edge.src):
            raise ValueError("E_TRACE_CYCLE")
        return t2

    def _reaches(self, a: str, b: str) -> bool:
        seen, stack = set(), [a]
        while stack:
            n = stack.pop()
            if n == b:
                return True
            if n in seen:
                continue
            seen.add(n)
            stack.extend(e.dst for e in self.edges if e.src == n)
        return False

    def ancestors(self, node: str) -> frozenset:
        out, stack = set(), [node]
        while stack:
            n = stack.pop()
            for e in self.edges:
                if e.dst == n and e.src not in out:
                    out.add(e.src)
                    stack.append(e.src)
        return frozenset(out)

    def sources(self) -> frozenset:
        dsts = {e.dst for e in self.edges}
        return frozenset(n for n in self.nodes if n not in dsts)


def start_trace(flow_id: str, source_event: str) -> Trace:
    return Trace(flow_id=flow_id, nodes=(source_event,))


def flow_identity(trace: Trace) -> str:
    """Identity over structure: operators, sources, edge topology,
    evidence states. The ACTOR IS EXCLUDED — swap goblin for claude
    and the flow is the same flow."""
    return canon_hash([(e.src, e.dst, e.operator, e.evidence_state)
                       for e in trace.edges])


# ── projections: bounded views, never evidence ──────────────────────────

@dataclass(frozen=True)
class Projection:
    """P_i : T -> V_i. Carries its dependency set for exact
    invalidation. A view is regenerated, never negotiated with."""
    view_id: str
    deps: frozenset                   # trace node ids this view reads


def evidence_count(trace: Trace, views: tuple) -> dict:
    """|P| = 5 while |union Anc(p_i)| = 1: five artifacts from one
    call are ONE witness. The anti-laundering counter."""
    src = trace.sources()
    union = frozenset().union(*(
        (trace.ancestors(d) | {d}) & src
        for v in views for d in v.deps)) if views else frozenset()
    return {"projection_count": len(views),
            "evidence_count": len(union),
            "independent_witnesses": sorted(union),
            "law": "projection count != evidence count"}


def invalidate(views: tuple, changed_node: str) -> dict:
    """v in Dep(P_i) => Invalidate(P_i) — and ONLY those."""
    hit = tuple(v.view_id for v in views if changed_node in v.deps)
    ok = tuple(v.view_id for v in views if changed_node not in v.deps)
    return {"invalidated": hit, "untouched": ok}


# ── the authority graph: must not cycle ─────────────────────────────────

AUTHORITY_STAGES = ("observe", "propose", "authorize", "act", "receipt")


def check_authority_acyclic(edges: tuple) -> dict:
    """not-exists x : x ~>_GA x. Rejects retroactive self-authorization
    (act -> authorize), receipt-minted permission (receipt ->
    authorize), and self-installing policy (learn -> authorize(learn))."""
    adj: dict = {}
    for a, b in edges:
        adj.setdefault(a, []).append(b)

    WHITE, GRAY, BLACK = 0, 1, 2
    color = {n: WHITE for n in adj} | {b: WHITE for bs in adj.values()
                                       for b in bs}

    def dfs(n, path):
        color[n] = GRAY
        for m in adj.get(n, ()):
            if color[m] == GRAY:
                return path + [n, m]
            if color[m] == WHITE:
                bad = dfs(m, path + [n])
                if bad:
                    return bad
        color[n] = BLACK
        return None

    for n in list(color):
        if color[n] == WHITE:
            bad = dfs(n, [])
            if bad:
                return {"verdict": "E_AUTHORITY_CYCLE", "cycle": bad,
                        "law": "cyclic intelligence, ACYCLIC authority"}
    return {"verdict": "ACYCLIC"}


# ── the capability lease ────────────────────────────────────────────────

@dataclass(frozen=True)
class Lease:
    """L = (subject, capability, scope, resource, t_start, t_end,
    constraints, issuer). Capability != authority; the lease is the
    only bridge, and it is narrow and it expires."""
    lease_id: str
    subject: str                      # a flow id — not a model name
    capability: str                   # SEND_EMAIL | WRITE_CRM | ...
    scope: str
    resource: str
    t_start: int
    t_end: int
    constraints: tuple = ()           # sorted (k, v) pairs
    issuer: str = ""

    def __post_init__(self):
        if not self.issuer:
            raise ValueError("E_LEASE_WITHOUT_ISSUER")
        if self.t_end < self.t_start:
            raise ValueError("E_LEASE_INVERTED_WINDOW")


@dataclass(frozen=True)
class FlowAction:
    action_id: str
    subject: str                      # the flow executing it
    capability: str
    resource: str
    content_hash: str = ""
    fields: tuple = ()                # sorted (k, v) pairs for constraints


def lease_valid(lease: Lease, action: FlowAction, t: int) -> dict:
    checks = {
        "subject": lease.subject == action.subject,
        "capability": lease.capability == action.capability,
        "resource": lease.resource == action.resource,
        "window": lease.t_start <= t <= lease.t_end,
        "constraints": all(kv in dict(action.fields).items()
                           for kv in lease.constraints),
    }
    return {"valid": all(checks.values()), "checks": checks,
            "lease_id": lease.lease_id, "t": t}


# ── authorize / revalidate / execute: the three-step ────────────────────

def authorize(action: FlowAction, lease: Lease, t0: int,
              policy_version: str):
    """Success mints an AuthorizationRecord — the ONLY type revalidate
    will accept. Refusals stay dicts; refusals are not records."""
    v = lease_valid(lease, action, t0)
    if not v["valid"]:
        return {"verdict": "REFUSED", "reason": "E_NO_VALID_LEASE",
                "checks": v["checks"]}
    return AuthorizationRecord(action_id=action.action_id,
                               lease_id=lease.lease_id, t0=t0,
                               policy_version=policy_version)


def revalidate(auth, action: FlowAction, lease: Lease, t1: int,
               policy_version_now: str, revoked: bool = False) -> dict:
    """Valid(a, t0) never implies Valid(a, t1). And only an
    AuthorizationRecord enters: an ExecutionReceipt presented here IS
    the receipt-minted-permission cycle, refused at the type."""
    bad = require_kind(auth, "AUTHORIZATION_RECORD")
    if bad:
        return bad
    if revoked:
        return {"verdict": "REFUSED", "reason": "E_CONSENT_REVOKED"}
    if policy_version_now != auth.policy_version:
        return {"verdict": "REFUSED", "reason": "E_POLICY_DRIFT",
                "was": auth.policy_version, "now": policy_version_now}
    v = lease_valid(lease, action, t1)
    if not v["valid"]:
        return {"verdict": "REFUSED", "reason": "E_STALE_AUTHORITY",
                "checks": v["checks"], "t1": t1}
    return {"verdict": "REVALIDATED", "t1": t1}


def execute(action: FlowAction, auth, reval: dict,
            proposal: EffectProposal, admission: Admission | None):
    """The full gate stack: lease three-step AND A_E. Neither alone.
    Success mints an ExecutionReceipt — a record that the effect RAN,
    which no upstream gate will ever accept as permission."""
    bad = require_kind(auth, "AUTHORIZATION_RECORD")
    if bad:
        return {**bad, "executed": False}
    if reval.get("verdict") != "REVALIDATED":
        return {"verdict": "REFUSED", "reason": reval.get(
            "reason", "E_NOT_REVALIDATED"), "executed": False}
    ae = admission_gate(proposal, admission)
    if ae["verdict"] not in ("ADMITTED_BY_PRINCIPAL", "PASS_UNGATED"):
        return {"verdict": "REFUSED", "reason": f"A_E:{ae['reason']}"
                if "reason" in ae else "A_E:HOLD",
                "a_e": ae, "executed": False}
    return ExecutionReceipt(
        action_id=action.action_id, lease_id=auth.lease_id, t1=reval["t1"],
        receipt_hash=canon_hash([action.action_id, auth.lease_id,
                                 reval["t1"]]))


# ── JUDGE = J_E ⊕ J_O ───────────────────────────────────────────────────

def j_e(claim: str, evidence_refs: tuple) -> dict:
    """Epistemic judgment. Its codomain contains no permissions and no
    TRUE — support is the ceiling."""
    return {"claim": claim,
            "verdict": "SUPPORTED" if evidence_refs else "UNKNOWN",
            "evidence": tuple(evidence_refs)}


def j_o(action: FlowAction, leases: tuple, t: int) -> dict:
    """Operational judgment. Its codomain contains no truth-values."""
    for lease in leases:
        if lease_valid(lease, action, t)["valid"]:
            return {"verdict": "PERMITTED", "lease_id": lease.lease_id}
    return {"verdict": "REFUSED", "reason": "E_NO_VALID_LEASE",
            "note": "EvidenceSupports(c) does not imply Permission(a)"}


# ── conservation: governance as accounting ──────────────────────────────

def conserve(q_in: float, q_out: float, q_retained: float, q_loss: float,
             eps: float = 1e-9) -> dict:
    gap = q_in - (q_out + q_retained + q_loss)
    if abs(gap) <= eps:
        return {"verdict": "BALANCED", "gap": 0.0}
    return {"verdict": "E_CONSERVATION_VIOLATION", "gap": gap,
            "note": "mass/money/evidence left the books"}


def authority_conservation(executed: frozenset, authorized: frozenset) -> dict:
    """Effects_executed ⊆ Effects_authorized — the one inclusion that
    is never allowed to leak."""
    rogue = executed - authorized
    if rogue:
        return {"verdict": "E_UNAUTHORIZED_EFFECT",
                "unauthorized": sorted(rogue)}
    return {"verdict": "CONSERVED",
            "unused_authorizations": sorted(authorized - executed)}


# ── replay: stored state != replayed state ──────────────────────────────

def replay(s0: dict, edges: tuple, registry: dict) -> dict:
    s = s0
    for e in edges:
        if e.operator not in registry:
            raise ValueError(f"E_OPERATOR_NOT_IN_REGISTRY:{e.operator}")
        s = registry[e.operator](s)
    return s


def state_grade(stored_sn: dict, s0: dict | None, edges: tuple,
                registry: dict) -> ReplayVerdict:
    """The three-rung ladder: STORED_STATE_ONLY (no path) <
    TRANSFORMATION_CLAIM (path, unreplayed/diverged) <
    WITNESSED_TRANSFORMATION (path replays to the stored state).
    Returns a ReplayVerdict — which authorizes nothing and executes
    nothing; it only grades history."""
    if s0 is None or not edges:
        return ReplayVerdict(grade="STORED_STATE_ONLY",
                             detail="a state without a reconstructible "
                                    "path is epistemically weakest")
    got = replay(s0, edges, registry)
    if canon(got) == canon(stored_sn):
        return ReplayVerdict(grade="WITNESSED_TRANSFORMATION",
                             detail=f"replay_hash={canon_hash(got)}")
    return ReplayVerdict(grade="TRANSFORMATION_CLAIM",
                         detail=f"E_REPLAY_DIVERGENCE stored="
                                f"{canon_hash(stored_sn)} replayed="
                                f"{canon_hash(got)}")


# ── LEARN = L0 ⊕ L1 ⊕ L2 ⊕ L3 ──────────────────────────────────────────

def learn(tier: str, payload: str, receipt: str = "",
          principal_admission: Admission | None = None,
          meta_path: tuple = ()) -> dict:
    """Authority budgets L0 < L1 < L2 << L3. No tier's result ever
    contains a lease — learning cannot mint the authority to install
    itself."""
    if tier not in LEARN_TIERS:
        raise ValueError("E_UNKNOWN_LEARN_TIER")
    if tier == "L0_EPHEMERAL":
        return {"verdict": "ADOPTED", "tier": tier, "persists": False}
    if tier == "L1_HEURISTIC":
        if not receipt:
            return {"verdict": "HOLD", "reason": "E_HEURISTIC_NEEDS_RECEIPT"}
        return {"verdict": "ADOPTED", "tier": tier, "persists": True,
                "receipt": receipt}
    if tier == "L2_INSTITUTIONAL":
        if not receipt:
            return {"verdict": "HOLD", "reason": "E_HEURISTIC_NEEDS_RECEIPT"}
        if principal_admission is None:
            return {"verdict": "HOLD", "reason": "E_AWAITING_PRINCIPAL"}
        return {"verdict": "ADOPTED", "tier": tier, "persists": True,
                "receipt": receipt,
                "admitted_by": principal_admission.principal}
    # L3: constitutional mutation — the full meta-change path, in order
    stages = tuple(s for s, _detail in meta_path)
    if stages != META_CHANGE_STAGES:
        return {"verdict": "REFUSED", "reason": "E_META_PATH_INCOMPLETE",
                "required": META_CHANGE_STAGES, "got": stages,
                "law": "rules that judge rule changes are not weakened "
                       "by the system being judged"}
    if principal_admission is None:
        return {"verdict": "HOLD", "reason": "E_AWAITING_PRINCIPAL"}
    return {"verdict": "ADOPTED", "tier": tier, "persists": True,
            "meta_path": stages,
            "admitted_by": principal_admission.principal}
