"""HELEN constitutional algebra — the deployable surface.

NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none.

This package is the single import point for the constitutional stack
built as falsifier-backed experiments. It bootstraps the experiment
paths ONCE, here, instead of the 22 scattered sys.path inserts that
made the algebra testable but not deployable.

The stack, bottom-up:

    Admissible Causal Morphism   the constitutional atom
      m : S_t --> S_{t+1} admitted only with a proof pi
    Causal Commit Cell           smallest persisted unit
    Transformation Motif         M = (I,G,T,O,R), authority-free
    Governed Flow Object         F = (E,S,X,J,P,A,R,Pi)
    History Fiber                state is a quotient of history
    Effect Admission gate        a gate with a named loss
    Ingestion Commit Cell        provenance-closed intake

The one law underneath all of it:

    Computation may transform representation; only witnessed
    admission may increase institutional reality or authority.

Usage:

    from helen_kernel.constitution import verify_constitution
    receipt = verify_constitution()
    assert receipt["verdict"] == "CONSTITUTION_HELD"

or from a shell:

    python -m helen_kernel.constitution
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_EXPERIMENTS = _REPO / "experiments"

# the ONE bootstrap. Deployment blocker retired here, not per-module.
for _sub in ("governed_flow", "crystal_palace", "effect_gate"):
    _p = str(_EXPERIMENTS / _sub)
    if _p not in sys.path:
        sys.path.insert(0, _p)

# ── the algebra, re-exported under one namespace ────────────────────────

from admissible_morphism import (  # noqa: E402
    CandidateMorphism,
    Graphs,
    LeaseBook,
    Proof,
    admit,
    authority_nonexpansive,
    constitutional_equiv,
    normalize as replay_normalize,
    project_evidence,
)
from causal_commit_cell import (  # noqa: E402
    CommitCell,
    amend,
    commit_cell,
    replay_chain,
    rewrite,
)
from transformation_motif import (  # noqa: E402
    Guard,
    TransformationMotif,
    decompose_self_acting,
    execute_motif,
    layer_promotion,
)
from flow_object import (  # noqa: E402
    AuthorizationRecord,
    ExecutionReceipt,
    FlowInstance,
    Lease,
    ProposalReceipt,
    ReplayVerdict,
    Trace,
    TraceEdge,
    authorize,
    check_authority_acyclic,
    evidence_count,
    execute,
    flow_identity,
    j_e,
    j_o,
    learn,
    revalidate,
    state_grade,
)
from history_fiber import (  # noqa: E402
    HF_INVARIANTS,
    DischargeReceipt,
    History,
    Movement,
    Obligation,
    causal_aliasing,
    conserve_obligations,
    discharges,
    equal_state_different_history_bead,
    reducer_conservation,
    safe_reduce,
)
from kernel_invariants import (  # noqa: E402
    BoundedBudget,
    NoveltyDecomposition,
    compositional_admissibility,
    decode,
    independent_roots,
    run_gate_only,
    run_with_invariant,
)
from effect_gate import (  # noqa: E402
    Admission,
    EffectProposal,
    NamedLoss,
    admission_gate,
    fallback_arm,
)
from ingestion_commit_cell import (  # noqa: E402
    DiscoveryOperators,
    IngestionCell,
    ResourceLease,
    admit_ingestion,
    can_execute,
    cursor_sequence_valid,
)
from ingestion_laws import decision_signature, establish_axis  # noqa: E402

from .verify import verify_constitution  # noqa: E402

__all__ = [
    "verify_constitution",
    # atom
    "CandidateMorphism", "Proof", "admit", "LeaseBook", "Graphs",
    "authority_nonexpansive", "project_evidence", "constitutional_equiv",
    "replay_normalize",
    # commit cell
    "CommitCell", "commit_cell", "amend", "rewrite", "replay_chain",
    # motif
    "TransformationMotif", "Guard", "execute_motif",
    "decompose_self_acting", "layer_promotion",
    # flow
    "Trace", "TraceEdge", "Lease", "FlowInstance", "flow_identity",
    "authorize", "revalidate", "execute", "evidence_count",
    "check_authority_acyclic", "j_e", "j_o", "learn", "state_grade",
    "ProposalReceipt", "AuthorizationRecord", "ExecutionReceipt",
    "ReplayVerdict",
    # history fiber
    "History", "Movement", "Obligation", "DischargeReceipt",
    "discharges", "conserve_obligations", "causal_aliasing",
    "equal_state_different_history_bead", "safe_reduce",
    "reducer_conservation", "HF_INVARIANTS",
    # invariants
    "BoundedBudget", "run_gate_only", "run_with_invariant",
    "compositional_admissibility", "decode", "independent_roots",
    "NoveltyDecomposition",
    # effect gate
    "NamedLoss", "EffectProposal", "Admission", "admission_gate",
    "fallback_arm",
    # ingestion
    "IngestionCell", "DiscoveryOperators", "ResourceLease",
    "admit_ingestion", "can_execute", "cursor_sequence_valid",
    "decision_signature", "establish_axis",
]
