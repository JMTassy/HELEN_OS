<!-- authority=false · canon=false · ledger_effect=none · NON-SOVEREIGN · a spec, not a ruling -->

# HELEN_CONTROL_PLANE_V0 — SPEC

**HELEN does not orchestrate agents. HELEN governs the lineage by which cognition becomes effect.**
`AgentOperations ≠ GovernedExecution`. The V0 is brutally small: four primitives, none absorbing another.

## Four primitives (TG + CC + CG + WA)

    TG  TaskGraph        intent + dependencies           TaskGraph        ⊬ Authority
    CC  ContextCompiler  governed replayable context     ContextCompiler  ⊬ Capability
    CG  CapabilityGate   may actor ATTEMPT this effect    CapabilityGranted⊬ Admission
    WA  Witness/Admission what is done + enters state     Witness          ⊬ Truth

## Flow

    INTENT → TASK GRAPH → CONTEXT COMPILER → CAPABILITY GATE → EXECUTION → WITNESS → VERIFICATION → ADMISSION → RECEIPT → REPLAY

Halts at the first gate that fails (CONTEXT reject / CAPABILITY deny / admission not satisfied) with **no state change**.

## Done semantics — no universal boolean

    Done(t) ⟺ SatisfiesCompletionContract(t)
    completion_contract = { required_witnesses[], verification_policy, admission_authority, required_receipts[] }

`ExitCode(0) ⊬ Done`. A cognitive task's Executed = artifact produced; an external-effect task's Executed = proof-of-effect. Governance lives in the contract, not the generic task word.

## Context Compiler — cognitive provenance

    C(a,t) = f(task, actor, scope, policy, budget, sources, compiler_version)
    invariant:  Context(a,t) ⊆ AuthorizedRead(a,t)          ContextAvailable ⊬ ContextAuthorized

Every compiled context carries `{context_id, task_id, actor_id, source_refs[], source_hashes[], capability_scope, selection_policy, token_budget, compiler_version, content_hash}`. Deterministic → same inputs+policy → same `content_hash`. Answers *"what exactly was knowable to actor a for task t, and why was source s included/excluded?"*

## Execution lineage — the moat object

    L(t) = (intent, task, context, capability, execution, witness, verification, admission, receipt, policy_version, artifact_hashes)

    ExecutionWithoutLineage        = OperationalEvent
    ExecutionWithReplayableLineage = GovernableInstitutionalEvent

    WHY KNOW? → context lineage · WHY ACT? → capability grant · WHY DONE? → witness+verification
    WHY STATE CHANGED? → admission · WHAT CHANGED? → receipt · UNDER WHICH RULES? → policy_version · REBUILD? → artifact_hashes + replay

## Canonical geometry

    Ledger → Reducer → GovernedState → Projection          Projection ⊬ CanonicalTruth
    ProjectionLoss ⊬ InstitutionalLoss:   delete(projection) → replay(ledger) → rebuild(state) → rebuild(projection)

Only `ADMITTED` events change institutional state. SQLite / dashboard / cache are rebuildable projections, never the truth.

## Load-bearing forbidden coercions (the real contract)

    UI ⊬ Truth · AgentReport ⊬ Done · TestsPass ⊬ Admission · ContextAvailable ⊬ ContextAuthorized
    CapabilityGranted ⊬ StateAdmitted · ExitCode(0) ⊬ InstitutionalSuccess · Projection ⊬ CanonicalTruth

## Tests (all PASS in `helen_control_plane_v0.py`)

    T1 report-DONE, required witness missing        → NOT_DONE, no state change
    T2 exit 0, completion contract unsatisfied      → NOT_DONE, no state change
    T3 context includes unauthorized source         → REJECT_CONTEXT
    T4 capability ok, admission authority absent     → NO_STATE_CHANGE (Verified ⊬ Admitted)
    T5 projection deleted → replay ledger → rebuild equivalent projection
    T6 same task + frozen inputs + policy → same context manifest hash
    T7 receipt binds exact policy_version + artifact_hashes

## Scope / status

Not to add now: Kanban, Crew, missions, cron, analytics, voice, SQLite-as-core, fancy UI — all replaceable projections around this spine. Status: `SelfPassed=true · PeerAdversaryValidated=false` — proposer-side, not witnessed. No Γ modification · no auto-admit · no premium FABLE · authority=false · canon=false · ledger_effect=none · not committed.

Build lineage first. Build Mission Control projections later.
