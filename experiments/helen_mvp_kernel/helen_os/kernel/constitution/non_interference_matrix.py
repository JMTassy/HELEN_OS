r"""Typed Institutional Non-Interference — NON_INTERFERENCE_MATRIX_V0.

NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none.
STATUS: ARCHITECTURAL_CONJECTURE + EXECUTABLE_FALSIFIER (explicitly
NOT a sealed theorem — the audit's grade, adopted).

The constitutional principle, compactly:

    Cognition may change topology, memory, presentation, consensus and
    computation. None of those changes acquires institutional force
    unless an explicit typed warrant crosses the corresponding
    boundary.

    D_NI(T) = 0  =>  F*(T Sigma) = F*(Sigma)
    D_NI(T) > 0  =>  ADMIT(T) = 0
    i --omega_ij--> j  =>  Verify(omega_ij) = 1

SEVEN CORRECTIONS FROM THE AUDIT, all encoded here rather than
argued:

1. THREE cell states, not two: N_ij in {I, F, L} — invariant-
   preserving (i==j), Forbidden (no warrant can license), Licensed
   (a typed witness may authorize). A matrix with only allow/deny is
   a diagram; with three states it is a transition policy.

2. D_NI = D_cross + D_local. The reference implementation skipped
   i==j as automatically legitimate. That is a bug: A->A can be an
   authority ESCALATION, E->E an evidence CORRUPTION. Local
   invariants are checked too, or "non-interference" means only
   "no cross-talk while the coordinate rots".

3. CHID-02 covariance correction. Rank(Cov(W_1..W_N)) = N_eff is a
   linear-dimensionality measure under a chosen representation. It
   does NOT establish provenance behaviour, in either direction:
   N_eff = 1 can coexist with a genuinely new independent root, and
   N_eff > 1 does not guarantee independent epistemic warrants. So
   N_eff is MEASURED separately and the epistemic invariant is
   stated on its own:  Delta|rho_E| = 0 unless an independent-root
   witness is admitted.  The interesting claim is the
   non-implication  N_eff up  !=>  |rho_E| up.

4. CHID-03 memory != proof. A memory holds observations,
   hypotheses, caches, summaries, invalidated assertions,
   permissions and embeddings — not all of them proofs. An item is
   m = (value, rho_E, tau_persist, Scope(kappa), status). The
   chiddush is narrower and stronger: a memory READ cannot upgrade
   the epistemic status of what is read.  M !-> W,  M !-> A.

5. CHID-04 bisimilarity is too strong. A useful optimized topology
   may legitimately NOT be bisimilar to the original. What must be
   preserved is institutional behaviour, not topological identity:
   Pi_0 !~ Pi_1 is permissible provided F*(Pi_1 x) = F*(Pi_0 x).
   Topological freedom under institutional invariance.

6. CHID-05 roles, not set-disjointness. Issuer and discharger may be
   the same organizational principal in legitimate systems. The
   deeper rule is typed ROLES: Propose != Authorize != Discharge as
   TYPES, not necessarily as entities. Issuer(O) !-> Authority(O),
   and ToolCall !-> Effect unless a valid affine kappa crosses.

7. The monoid hierarchy, stated with its conditions rather than
   asserted: M_I = {T : F*(Tx) = F*(x)} is a monoid only if it
   contains the identity and is closed under composition; Gamma_I =
   Units(M_I) is the reversible sector. Hence
   presentation-transformations  ⊇  M_I  ⊇  Gamma_I.
"""
from __future__ import annotations

import json

COORDINATES = ("Q", "E", "D", "R", "A", "X", "RHO_E", "RHO_A",
               "PI", "M", "P", "C")
CELL_STATES = ("I", "F", "L")

# The only crossings a typed witness may license. Everything else
# off-diagonal is structurally barred: no warrant exists for it.
LICENSED_CROSSINGS = {
    ("PI", "Q"): "W_TOPOLOGY_OPTIMIZATION",
    ("M", "Q"): "W_MEMORY_COMPRESSION",
    ("RHO_E", "E"): "W_INDEPENDENT_ROOT",
    ("RHO_A", "A"): "W_AUTHORITY_DELEGATION",
    ("A", "X"): "W_CAPABILITY_TOKEN",
}

# The channels through which epistemic status is most likely to be
# illegally amplified, each with the witness/test that closes it.
LEAKAGE_CHANNELS = {
    ("Q", "A"): "composition_test",
    ("P", "F"): "counterfactual_admission",
    ("C", "E"): "tcb_attack",
    ("M", "A"): "memory_status_probe",
    ("PI", "A"): "topology_privilege_probe",
}

ROLES = ("PROPOSE", "AUTHORIZE", "DISCHARGE")


def canon(o):
    return json.dumps(o, sort_keys=True, separators=(",", ":"),
                      default=str)


# ── the matrix as a transition policy ──────────────────────────────────

def cell(i, j) -> dict:
    """N_ij in {I, F, L}. I on the diagonal (local mutation, still
    subject to local invariants), L where a typed witness may
    license, F everywhere else — structurally barred."""
    if i not in COORDINATES or j not in COORDINATES:
        return {"ok": False, "reason": "E_UNKNOWN_COORDINATE"}
    if i == j:
        return {"ok": True, "state": "I",
                "note": "local mutation: legitimacy still depends on "
                        "the coordinate's own invariant"}
    if (i, j) in LICENSED_CROSSINGS:
        return {"ok": True, "state": "L",
                "required_warrant": LICENSED_CROSSINGS[(i, j)]}
    return {"ok": True, "state": "F",
            "note": "no warrant can license this crossing"}


def matrix() -> dict:
    """The full 12x12 policy, computed rather than drawn."""
    m = {i: {j: cell(i, j)["state"] for j in COORDINATES}
         for i in COORDINATES}
    counts = {s: 0 for s in CELL_STATES}
    for i in COORDINATES:
        for j in COORDINATES:
            counts[m[i][j]] += 1
    return {"matrix": m, "counts": counts,
            "n_coordinates": len(COORDINATES),
            "cells": len(COORDINATES) ** 2}


# ── local invariants (correction 2: the skipped-diagonal bug) ──────────

def local_invariant(coord, before, after, witness=None) -> dict:
    """Within-coordinate invariant preservation. A mutation that stays
    inside its coordinate is NOT automatically legitimate: authority
    can escalate, evidence can be corrupted, roots can inflate,
    effects can lose idempotency, memory status can be upgraded."""
    if coord not in COORDINATES:
        return {"ok": False, "reason": "E_UNKNOWN_COORDINATE"}
    b, a = before or {}, after or {}

    if coord == "A":
        # authority attenuates or holds; it never escalates without a
        # delegation witness (affine, strictly decreasing depth)
        if a.get("level", 0) > b.get("level", 0) and \
                witness != "W_AUTHORITY_DELEGATION":
            return {"ok": False,
                    "reason": "E_LOCAL_AUTHORITY_ESCALATION",
                    "delta": a.get("level", 0) - b.get("level", 0)}
        if a.get("depth", 0) > b.get("depth", 0):
            return {"ok": False, "reason": "E_LOCAL_DEPTH_INCREASE"}

    if coord == "E":
        # evidence may be added to, never silently re-rooted
        if b.get("root") and a.get("root") != b.get("root"):
            return {"ok": False,
                    "reason": "E_LOCAL_EVIDENCE_CORRUPTION",
                    "was": b.get("root"), "now": a.get("root")}

    if coord == "RHO_E":
        if a.get("count", 0) > b.get("count", 0) and \
                witness != "W_INDEPENDENT_ROOT":
            return {"ok": False, "reason": "E_LOCAL_ROOT_INFLATION"}

    if coord == "X":
        if a.get("effects", 0) > b.get("effects", 0) and \
                not a.get("idempotency_key"):
            return {"ok": False,
                    "reason": "E_LOCAL_NON_IDEMPOTENT_EFFECT"}

    if coord == "M":
        # correction 4: a read cannot upgrade what it reads
        if a.get("status_rank", 0) > b.get("status_rank", 0) and \
                a.get("via") == "read":
            return {"ok": False,
                    "reason": "E_LOCAL_MEMORY_STATUS_UPGRADE"}

    if coord == "R":
        if b.get("replayable") and not a.get("replayable"):
            return {"ok": False, "reason": "E_LOCAL_REPLAY_LOST"}

    return {"ok": True, "coordinate": coord}


# ── the engine: D_NI = D_cross + D_local ───────────────────────────────

def evaluate(transitions) -> dict:
    """Compute the non-interference defect. Admissible iff D_NI == 0.

    transitions: iterable of dicts with
      source, target, witness (optional), warrant (optional),
      before/after (optional, for the local check)."""
    d_cross, d_local, violations = 0, 0, []
    for t in transitions or ():
        i, j = t.get("source"), t.get("target")
        c = cell(i, j)
        if not c["ok"]:
            d_cross += 1
            violations.append({"code": "E_UNKNOWN_COORDINATE",
                               "transition": (i, j)})
            continue
        state = c["state"]
        if state == "I":
            loc = local_invariant(i, t.get("before"), t.get("after"),
                                  t.get("warrant"))
            if not loc["ok"]:
                d_local += 1
                violations.append({"code": loc["reason"],
                                   "coordinate": i, "class": "local"})
            continue
        if state == "F":
            d_cross += 1
            violations.append({
                "code": "E_FORBIDDEN_INTERFERENCE",
                "transition": (i, j), "class": "cross",
                "note": "structurally barred; no warrant exists"})
            continue
        # state == "L": a typed, verifiable witness is required
        need = c["required_warrant"]
        if t.get("warrant") != need or not t.get("witness"):
            d_cross += 1
            violations.append({
                "code": "E_UNLICENSED_CROSSING",
                "transition": (i, j), "class": "cross",
                "required": need, "got": t.get("warrant"),
                "witness": t.get("witness")})
    d_ni = d_cross + d_local
    return {"D_NI": d_ni, "D_cross": d_cross, "D_local": d_local,
            "admissible": d_ni == 0,
            "violations": tuple(violations),
            "law": "D_NI > 0 => ADMIT = 0"}


def warrant_is_not_assertion(warrant, verified) -> dict:
    """omega_ij is not the mere claim that a crossing is legitimate.
    It must be a typed, verifiable witness."""
    if warrant and not verified:
        return {"licensed": False, "reason": "E_ASSERTED_NOT_VERIFIED",
                "law": "mutation -> crossing -> warrant -> "
                       "verification -> admission"}
    return {"licensed": bool(warrant and verified)}


# ── the five chiddushim, in their CORRECTED form ───────────────────────

def chid01_trace(local_steps_ok, global_valid) -> dict:
    """TraceCompliance(T) !=> StateAdmissibility(Sigma). A trace may
    satisfy every local step contract and still violate a global
    linear resource (double-spend, circular fact dependency). The
    contribution is the second-level operation: project the trace to
    a graph, then compute GlobalValid on it."""
    if local_steps_ok and not global_valid:
        return {"admissible": False,
                "reason": "E_TRACE_COMPLIANT_STATE_INADMISSIBLE",
                "law": "trace validity is LOCAL temporal validity; "
                       "institutional validity is GLOBAL graph "
                       "validity"}
    return {"admissible": bool(local_steps_ok and global_valid),
            "path": "T -> G_T -> GlobalValid(G_T)"}


def chid02_neff(cov_rank, n_workers, delta_rho_e,
                independent_root_witness=None) -> dict:
    """CORRECTED. N_eff is measured; the provenance invariant is
    stated separately; and the non-implication runs in BOTH
    directions — N_eff = 1 does not forbid a new root, N_eff > 1 does
    not supply one."""
    if cov_rank < 0 or n_workers < 1:
        return {"ok": False, "reason": "E_MALFORMED_SWARM"}
    n_eff = min(cov_rank, n_workers)
    root_ok = (delta_rho_e == 0) or bool(independent_root_witness)
    return {"ok": root_ok,
            "N_eff": n_eff, "N_workers": n_workers,
            "reason": None if root_ok else "E_ROOT_WITHOUT_WITNESS",
            "n_eff_implies_roots": False,
            "roots_implied_by_n_eff": None,
            "law": "N_eff up does not imply |rho_E| up; cognitive "
                   "diversity is not epistemic warrant. N_eff is a "
                   "representation measure, |rho_E| an epistemic one"}


def chid03_memory(item, operation, status_rank_before,
                  status_rank_after) -> dict:
    """CORRECTED. Memory is not a proof DAG; it is
    (value, rho_E, tau, Scope(kappa), status). The narrow chiddush: a
    READ may not upgrade the epistemic status of what it reads."""
    required = ("value", "root", "tau_persist", "scope", "status")
    missing = tuple(sorted(set(required) - set(item or {})))
    if missing:
        return {"ok": False, "reason": "E_UNGOVERNED_MEMORY_ITEM",
                "missing": missing}
    if operation == "read" and status_rank_after > status_rank_before:
        return {"ok": False, "reason": "E_READ_UPGRADED_STATUS",
                "law": "M !-> W and M !-> A"}
    return {"ok": True,
            "governed_memory": "Memory + Provenance + Scope + Status"}


def chid04_topology(bisimilar, frontier_preserved) -> dict:
    """CORRECTED. Bisimilarity is NOT required — an optimized topology
    may legitimately differ. What must hold is institutional
    invariance: F*(Pi_1 x) = F*(Pi_0 x)."""
    if not frontier_preserved:
        return {"permitted": False,
                "reason": "E_TOPOLOGY_CHANGED_FRONTIER",
                "law": "Delta Pi != 0 does not imply Delta A, Delta W "
                       "or Delta rho_E"}
    return {"permitted": True, "bisimilar": bool(bisimilar),
            "note": "topological freedom under institutional "
                    "invariance: non-bisimilar rewiring is fine while "
                    "F* is preserved"}


def chid05_roles(issuer_principal, authorizer_principal,
                 discharger_principal, roles_typed,
                 kappa_valid=False) -> dict:
    """CORRECTED. Not set-disjointness of principals — typed ROLES.
    The same principal may legitimately hold two roles; what may not
    collapse is the TYPE distinction Propose != Authorize !=
    Discharge, and issuing never confers authority."""
    if not roles_typed:
        return {"ok": False, "reason": "E_ROLES_UNTYPED",
                "law": "Propose != Authorize != Discharge as TYPES, "
                       "not necessarily as entities"}
    same_principal = len({issuer_principal, authorizer_principal,
                          discharger_principal}) < 3
    if not kappa_valid:
        return {"ok": False, "reason": "E_TOOLCALL_WITHOUT_KAPPA",
                "same_principal_permitted": True,
                "law": "Issuer(O) !-> Authority(O); ToolCall !-> "
                       "Effect without a valid affine kappa"}
    return {"ok": True, "same_principal": same_principal,
            "note": "one principal may hold several roles; the types "
                    "stay distinct and kappa still crosses"}


# ── the monoid hierarchy (correction 7) ────────────────────────────────

def in_M_I(frontier_before, frontier_after) -> dict:
    """T in M_I iff F*(Tx) = F*(x)."""
    same = canon(frontier_before) == canon(frontier_after)
    return {"in_M_I": same,
            "reason": None if same else "E_FRONTIER_MOVED"}


def monoid_conditions(has_identity, closed_under_composition) -> dict:
    """M_I is a monoid only WITH these conditions — stated, not
    assumed."""
    if not has_identity:
        return {"is_monoid": False, "reason": "E_NO_IDENTITY"}
    if not closed_under_composition:
        return {"is_monoid": False, "reason": "E_NOT_CLOSED"}
    return {"is_monoid": True}


def gamma_I(t_in_M_I, inverse_exists, inverse_in_M_I) -> dict:
    """Gamma_I = Units(M_I): the reversible symmetry sector. NOT the
    whole of M_I, and M_I is not itself a group."""
    if not t_in_M_I:
        return {"in_Gamma_I": False, "reason": "E_NOT_IN_M_I"}
    if not (inverse_exists and inverse_in_M_I):
        return {"in_Gamma_I": False, "reason": "E_NOT_INVERTIBLE",
                "note": "in M_I but not a unit"}
    return {"in_Gamma_I": True,
            "hierarchy": "presentation ⊇ M_I ⊇ Gamma_I"}


def nim_implies_monoid(d_ni, frontier_before, frontier_after) -> dict:
    """The bridge the audit asked for: NIM(T) = 0 => T in M_I. If the
    defect is zero but the frontier moved anyway, the MATRIX is
    incomplete — that is a falsifier of the specification, not of the
    run."""
    m = in_M_I(frontier_before, frontier_after)
    if d_ni == 0 and not m["in_M_I"]:
        return {"consistent": False,
                "reason": "E_MATRIX_INCOMPLETE",
                "law": "D_NI = 0 with a moved frontier means a "
                       "leakage channel is missing from the matrix"}
    if d_ni > 0 and m["in_M_I"]:
        return {"consistent": True, "note": "defect found; frontier "
                "held anyway — conservative, not a contradiction"}
    return {"consistent": True, "in_M_I": m["in_M_I"]}


# ── status ─────────────────────────────────────────────────────────────

def status() -> dict:
    """The audit's grade, adopted verbatim: this is a conjecture with
    an executable falsifier, not a sealed theorem."""
    return {"status": "ARCHITECTURAL_CONJECTURE",
            "falsifier": "EXECUTABLE",
            "sealed_theorem": False,
            "authority": False, "canon": False,
            "ledger_effect": "none",
            "note": "the literature validates the PROBLEM SPACE; it "
                    "does not validate this architecture"}


# ── correction 8: what F* conserves (operator, mid-turn) ───────────────

def institutional_invariance(inv_before, inv_after,
                             q_before, q_after,
                             action_before=None, action_after=None) -> dict:
    """The operator's correction: F* must range over the INSTITUTIONAL
    OBLIGATIONS to be preserved, never over the final answer. Read as
    'same output', it would forbid precisely the improvement sought.

        Invariant_I(Pi_0) AND Invariant_I(Pi_1) AND Q(Pi_1) > Q(Pi_0)

    Two policies may choose DIFFERENT actions, each authorized, while
    conserving the same obligations. Different action is not a
    violation; a changed obligation is."""
    inv_held = (canon(inv_before) == canon(inv_after))
    if not inv_held:
        return {"ok": False, "reason": "E_INSTITUTIONAL_INVARIANT_MOVED",
                "note": "this is the violation — not the action change"}
    return {"ok": True,
            "invariants_held": True,
            "actions_differ": action_before != action_after,
            "quality_gain": round(q_after - q_before, 6),
            "improvement": q_after > q_before,
            "law": "F* conserves obligations, not answers; differing "
                   "authorized actions are permitted and are the point"}


# ── correction 9: the completeness conjecture needs an OUTSIDE eye ─────

def independent_observer(state_before, state_after) -> dict:
    """Deliberately does NOT consult the matrix, the declared
    transitions, or any NIM control. It reads the RESULTING STATE and
    asks whether authority, provenance roots or executed effects
    actually moved. A transition that was never DECLARED is invisible
    to the matrix and visible here — which is the blind spot the
    operator named."""
    b, a = state_before or {}, state_after or {}
    findings = []
    if a.get("authority_level", 0) > b.get("authority_level", 0):
        findings.append("AUTHORITY_ROSE")
    if a.get("root_count", 0) > b.get("root_count", 0):
        findings.append("ROOTS_ROSE")
    if a.get("effects_executed", 0) > b.get("effects_executed", 0):
        findings.append("EFFECT_EXECUTED")
    if a.get("admitted_claims", 0) > b.get("admitted_claims", 0):
        findings.append("CLAIM_ADMITTED")
    return {"violation": 1 if findings else 0,
            "findings": tuple(findings),
            "method": "outcome_state_audit",
            "independent_of": "declared-transition matrix controls"}


def completeness_conjecture(nim_defect, observer) -> dict:
    """NIM(T) = 0 => T in M_I is a COMPLETENESS CONJECTURE relative to
    the declared domain and observations — a zero defect does not
    establish absence of leakage. The sought counterexample is

        NIM(T) = 0  AND  Violation_I(T) = 1

    When it appears, the completeness CLAIM is invalidated and the
    faulty run is kept as a witness; the matrix is what was refuted,
    never the observation."""
    if nim_defect == 0 and observer.get("violation", 0) == 1:
        return {"completeness_claim": "INVALIDATED",
                "reason": "E_MATRIX_INCOMPLETE",
                "counterexample": True,
                "witness_retained": True,
                "leaked": observer.get("findings"),
                "law": "a null defect is not the absence of leakage; "
                       "it is the absence of DECLARED leakage"}
    if nim_defect > 0 and observer.get("violation", 0) == 0:
        return {"completeness_claim": "UNREFUTED_THIS_RUN",
                "counterexample": False,
                "note": "matrix caught what the observer did not — "
                        "conservative, not proof"}
    return {"completeness_claim": "UNREFUTED_THIS_RUN",
            "counterexample": False,
            "caveat": "unrefuted on the declared domain and "
                      "observations only; not a completeness proof"}
