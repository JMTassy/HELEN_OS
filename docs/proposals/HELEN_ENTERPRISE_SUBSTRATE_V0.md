<!-- authority=false · claim=NO_CLAIM · a proposal, not a ruling -->
# HELEN AS GOVERNED APPLICATION SUBSTRATE — V0

🔵 OBSERVED · NON_SOVEREIGN · authority=false · canon=NO_SHIP · lifecycle=PROPOSAL · memory_class=CANDIDATE_PATTERN

The enterprise turning point: **HELEN is not an "AI system" or a "multi-agent OS." It is a governed
application substrate whose intelligence is one replaceable internal capability.**

```
                    HELEN = governed application substrate with pluggable cognition
```

## 1. The architectural center shifts
From the model-centric stack:
```
Model → Agent → Tool
```
to the application-centric one:
```
Business Object → Workflow State → Policy Decision → Cognitive Operation → Authorized Effect → Audit Event
```
This is durable because models, agent frameworks, and vendors can all change without changing the
application contract. **The LLM owns exactly one transition: cognition.** It owns none of the others.

## 2. The enterprise invariants — the non-amplification law, scaled
These are tonight's `X↑ ⊬ Authority↑` family in enterprise form:

| invariant | meaning |
|---|---|
| `Recommend(a) ⊬ Authorize(a) ⊬ Execute(a)` | semantic authority (a model infers) ≠ operational authority (permission to act) |
| `LLMOutput ⊬ StateTransition` | the workflow engine owns `δ: S × Event ⇀ S`; persuasive text can propose an event, never move the object |
| `WorkerDeath ⊬ KnowledgeLoss` | workers are disposable compute, not identities; if killing a HER/HAL/Goblin loses durable memory, memory was in the wrong layer |
| `ApplicationSemantics ⊥ ModelSelection` | the AI Gateway is a **policy compiler** (`Route(request)→(provider,model,region,policy)`), not a vendor proxy |
| `Replayable ⊬ Correct` | replay gives auditability, not metaphysical truth |
| `Mention ⊬ Grant` · `Proposal ∧ Commit ⊬ Authority` | committing a proposal proves Git persistence, not admission |
| `Client_i → Configuration_i` (not `→ Branch_i`) | configuration-as-data = platform; per-client forks = consulting software |

## 3. The effect transaction (the commercial Γ membrane)
Execution requires a capability-bearing transaction, gated once:
```
τ = (principal, tenant, capability, resource, operation, policy, workflow_state, request_id)
Permit(τ) = Identity ∧ TenantBoundary ∧ Capability ∧ Policy ∧ WorkflowConstraint
```
Only on `Permit(τ)=1` may the application invoke a connector.

## 4. Four memory stores (not "one HELEN memory")
```
S_A  authoritative application state      S_R  derived retrieval/search structures
S_K  governed institutional knowledge     S_C  ephemeral cognitive context
```
Containment: `S_C ⊬ S_K` · `S_R ⊬ S_A`. A vector hit is not a business fact; a model summary is not
institutional memory; a prompt item is not durable state. Promotion path:
`Context → CandidateKnowledge → Evidence/PolicyCheck → KnowledgeStore` — never silent persistence.

## 5. Tenant isolation is a graph invariant, not a DB setting
```
for i≠j :  G_i ∩ G_j ⊆ G_shared-control
```
`G_shared-control` holds code, schemas, policy definitions, deployment manifests, signed binaries —
**never** customer data, embeddings, working context, secrets, workflow state, or temp artifacts.
Cross-tenant leakage becomes an *architectural violation*, not a bug class.

## 6. Proof frontier > confidence score
Return typed, per-claim warrants, not one number:
```
document_identity     : VERIFIED
field_extraction      : VERIFIED
policy_compliance     : HOLD
payment_authorization : NOT_AUTHORIZED
```
Different propositions require different warrants. `proof frontier > global confidence`.

## 7. Bitemporal release identity
Every consequential decision binds to its exact environment:
```
RuntimeIdentity = (commit, containerDigest, schemaVersion, workflowVersion, policyVersion, modelPolicyVersion)
```
so a 2026 decision replays against 2026 policy/model — not today's. Two times: `t_business`, `t_software`.
Continuity plane (`DB + Objects + Config + SecretsBindings + ReleaseManifest + Migrations`) is architecture,
not support documentation.

## 8. The invisibility boundary
- **Internal** (design metaphors): HER · HAL · SOPHIA · Garden · WUL · Goblins.
- **External** (product surface): ContextService · PolicyEngine · EvidenceService · WorkerRuntime ·
  WorkflowEngine · EffectGateway · AuditService · ContinuityService.
The client replaces the AI engine conceptually without losing the business system.

## 9. The stack
```
        Business Applications
                 ↓
   Deterministic Application Platform
                 ↓
     Governed HELEN Cognition Services
                 ↓
         AI / Tool Gateways
                 ↓
      Isolated Tenant Data Plane
transversal: Identity · Capabilities · Policy · Audit · Observability · Continuity
```

## 10. The acceptance test (the sharpest law)
> **Replace every model call with a deterministic stub. The system gets less intelligent, but stays
> structurally intact.** Business objects, workflow states, permissions, tenant boundaries, audit trail,
> receipts, connector contracts, policy evaluation, continuity, and release identity must all still exist.
> If replacing the model destroys any of them, too much application responsibility still lives in the LLM.
```
Cognition may improve application decisions, but it must not define the application's existence.
```

## 11. Connection to the committed kernel
This substrate's membrane is not aspirational — its **non-amplification core is already witnessed on origin**
(the audit-invariant library sealed 2026-08-14/15):
- `graph_ir` I₁–I₇ — composition + linear capability + revocation (the `Permit(τ)` / effect-transaction primitives)
- `epistemic_roots` — `citations ⊬ witnesses` (the evidence/knowledge-promotion discipline, `S_C ⊬ S_K`)
- `cross_model_independence` — `ModelAgreement ⊬ Corroboration` (`ApplicationSemantics ⊥ ModelSelection`)
- `charisma_airlock` — `prestige ⊬ authority` (semantic ≠ operational authority)
- `conjectural_emendation` — material-witness boundary (`D ⊬ M`; receipts bind warrant to effect)

## Product thesis
```
HELEN does not sell agents.
HELEN provides a governed substrate for AI-powered applications whose cognition can evolve
without dissolving workflow, authority, tenancy, provenance, or auditability.
```
Harder to commoditize than "we orchestrate several good models," because the model layer is what
commoditizes fastest — and here the model is the one part the substrate is designed to survive replacing.

## Mode-route (operator-gated)
None self-promotes. `authority=false`. This is a PROPOSAL; promotion past PROPOSAL requires the
`DOCTRINE_ADMISSION_PROTOCOL_V1` route. It edits no reducer, ledger, schema, firewall, or runtime.

*authority=false · canon=NO_SHIP · a proposal, not a ruling.*
