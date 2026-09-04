"""C11 — mutation-surface completeness audit. 🔵 OBSERVED · NON_SOVEREIGN · authority=0.

Target: for every enumerated REACHABLE governed-state mutation sink m,
    SuccessfulMutation(m) ⇒ factors_through_declared_boundary(m).
Any reachable UNCLASSIFIED sink ⇒ C11 = INCOMPLETE.

CRITICAL anti-overclaim law:
    PASS_SCOPED ⊬ (M_enumerated == M_reachable)
PASS_SCOPED means only "no bypass found among the sinks this audit successfully enumerated and
classified on this frame" — NOT that every reachable sink was found.

Governed-state domains D_G — ONLY these count as governed (caches / UI logs / test fixtures are
NON_GOVERNED unless a call/restart path proves otherwise):
    committed_head, transaction_history, capability_spent_set, authoritative_receipts,
    restart_loaded_state.

A grep hit is a CANDIDATE, not a proof. Each surface carries evidence_refs (file:line) and a
reachability_basis; classification is DERIVED from that evidence, never a stored assertion.
MEDIATED is narrow: "the observed path crosses the declared boundary ON THIS FRAME" — it does NOT
imply atomicity, semantic correctness, or global completeness.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

GOVERNED_DOMAINS = (
    "committed_head", "transaction_history", "capability_spent_set",
    "authoritative_receipts", "restart_loaded_state",
)


class Reach(Enum):
    DIRECT_CALL_GRAPH = "DIRECT_CALL_GRAPH"
    IMPORT_PATH = "IMPORT_PATH"
    BOOT_RELOAD_PATH = "BOOT_RELOAD_PATH"
    TEST_ONLY = "TEST_ONLY"
    UNRESOLVED = "UNRESOLVED"


class Cls(Enum):
    MEDIATED = "MEDIATED"
    BYPASS = "BYPASS"
    UNCLASSIFIED = "UNCLASSIFIED"
    NON_GOVERNED = "NON_GOVERNED"


class C11Status(Enum):
    PASS_SCOPED = "PASS_SCOPED"
    FAIL = "FAIL"
    INCOMPLETE = "INCOMPLETE"


@dataclass(frozen=True)
class C11Surface:
    id: str
    evidence_refs: str            # file:line where the mutation occurs
    symbol: str
    state_domain: str             # one of GOVERNED_DOMAINS, or "" if it touches no governed state
    reachability_basis: Reach
    boundary: str                 # the declared boundary this sink must cross (e.g. "TransactionRuntime.commit")
    passes_declared_boundary: bool  # observed to cross `boundary` on this frame
    mutation_kind: str


def classify(s: C11Surface) -> Cls:
    """Derived, never trusted. Fail-closed: unresolved reachability of a governed sink is
    UNCLASSIFIED (not silently MEDIATED)."""
    if s.reachability_basis == Reach.TEST_ONLY:
        return Cls.NON_GOVERNED                 # test-only helper, not production-reachable
    if s.state_domain not in GOVERNED_DOMAINS:
        return Cls.NON_GOVERNED                 # does not touch governed state
    if s.reachability_basis == Reach.UNRESOLVED:
        return Cls.UNCLASSIFIED                 # reachability unknown → fail-closed
    return Cls.MEDIATED if s.passes_declared_boundary else Cls.BYPASS


def c11_status(surfaces):
    """FAIL if any BYPASS; else INCOMPLETE if any UNCLASSIFIED; else PASS_SCOPED (scoped to the
    enumerated surface only)."""
    cls = [classify(s) for s in surfaces]
    if any(c == Cls.BYPASS for c in cls):
        return C11Status.FAIL, "BYPASS_FOUND"
    if any(c == Cls.UNCLASSIFIED for c in cls):
        return C11Status.INCOMPLETE, "UNCLASSIFIED_PRESENT"
    return C11Status.PASS_SCOPED, "NO_BYPASS_OVER_ENUMERATED_SURFACES"


# ---------------------------------------------------------------- frozen current-frame inventory
# Enumerated against helen_os/kernel/ @ c94fe32. evidence_refs are real file:line. Reachability is
# assessed from the local call graph ONLY — the sandbox has no production entrypoint, so a public
# governed-state setter with no proof it CANNOT be reached outside its boundary is UNRESOLVED,
# hence UNCLASSIFIED, hence C11 = INCOMPLETE (fail-closed, honest).
KERNEL_INVENTORY = (
    C11Surface(
        id="tx.commit",
        evidence_refs="helen_os/kernel/transaction.py:102",
        symbol="TransactionRuntime.commit",
        state_domain="committed_head",
        reachability_basis=Reach.DIRECT_CALL_GRAPH,
        boundary="TransactionRuntime.commit",
        passes_declared_boundary=True,          # it IS the boundary
        mutation_kind="commit_head_advance",
    ),
    C11Surface(
        id="tx._advance",
        evidence_refs="helen_os/kernel/transaction.py:67,117",
        symbol="TransactionRuntime._advance",
        state_domain="committed_head",
        reachability_basis=Reach.DIRECT_CALL_GRAPH,   # private; sole caller is commit (line 117)
        boundary="TransactionRuntime.commit",
        passes_declared_boundary=True,
        mutation_kind="head_advance",
    ),
    C11Surface(
        id="capability.consume",
        evidence_refs="helen_os/kernel/capability.py:168",
        symbol="Executor._consumed.add",
        state_domain="capability_spent_set",
        reachability_basis=Reach.DIRECT_CALL_GRAPH,   # inside Executor.invoke, after binding checks
        boundary="Executor.invoke",
        passes_declared_boundary=True,
        mutation_kind="affine_consume",
    ),
    # --- the two honest UNCLASSIFIED sinks that force INCOMPLETE ---
    C11Surface(
        id="store.advance",
        evidence_refs="helen_os/kernel/governed_store.py:38,40",
        symbol="GovernedStore.advance",
        state_domain="committed_head",
        reachability_basis=Reach.UNRESOLVED,    # PUBLIC head-setter; no proof it can't be called
        boundary="TransactionRuntime.commit",   #   outside commit (no production entrypoint graph)
        passes_declared_boundary=False,
        mutation_kind="direct_head_setter",
    ),
    C11Surface(
        id="tx.current_state_hash",
        evidence_refs="helen_os/kernel/transaction.py:62,68",
        symbol="TransactionRuntime.current_state_hash (field)",
        state_domain="committed_head",
        reachability_basis=Reach.UNRESOLVED,    # public mutable field; C14-11 assigned it directly
        boundary="TransactionRuntime.commit",
        passes_declared_boundary=False,
        mutation_kind="direct_field_assignment",
    ),
    C11Surface(
        id="intent_log.commit",
        evidence_refs="helen_os/kernel/intent_log.py:39",
        symbol="IntentLog.commit",
        state_domain="restart_loaded_state",
        reachability_basis=Reach.UNRESOLVED,    # WAL write; recovery-authoritative, gating unproven here
        boundary="TransactionRuntime.commit",
        passes_declared_boundary=False,
        mutation_kind="wal_append",
    ),
)


def run_c11(surfaces=KERNEL_INVENTORY, frame="c94fe32") -> dict:
    """Machine-readable C11 report for the enumerated surface (current frame only)."""
    rows = [(s, classify(s)) for s in surfaces]
    status, reason = c11_status(surfaces)
    count = lambda k: sum(1 for _, c in rows if c == k)
    return {
        "frame": {"commit": frame, "branch": "claude/doctrine-proposals"},
        "governed_state_domains": list(GOVERNED_DOMAINS),
        "enumerated_count": len(surfaces),
        "mediated_count": count(Cls.MEDIATED),
        "bypass_count": count(Cls.BYPASS),
        "unclassified_count": count(Cls.UNCLASSIFIED),
        "non_governed_count": count(Cls.NON_GOVERNED),
        "surfaces": [
            {"id": s.id, "evidence_refs": s.evidence_refs, "symbol": s.symbol,
             "state_domain": s.state_domain, "reachability_basis": s.reachability_basis.value,
             "classification": c.value}
            for s, c in rows
        ],
        "status": status.value,
        "reason": reason,
        "claim_scope": "CURRENT_FRAME_ENUMERATED_SURFACES_ONLY",
    }
