<!-- authority=false · claim=NO_CLAIM · a reading, not a ruling -->
<!-- Captured 2026-08-22 from operator relay ("DEEP ARCHITECTURAL FREEZE CANDIDATE") · NON_SOVEREIGN · untracked (NO_COMMIT / NO_PUSH until operator verb) -->

# CODE_N_SPEC_V0 — task-conditioned, provenance-preserving multidimensional memory

**One sentence:** CODE N is a memory that knows not only what to show, but
what it is forbidden to forget while showing it.

**Object:** `𝒩_t = (G_t, V_t, P_t, A_t, T_t, R_t)` — typed graph, vector
geometry, provenance lineage, authority structure, temporal geometry,
rebuild receipts. **Non-collapse law: `G ≠ V ≠ P ≠ A ≠ T`** — jointly
rendered, never silently collapsed.

## Corpus status

| Layer | Item | Status |
|---|---|---|
| S | CODE N relays (summary ×5, deep dive ×2, TURBO execution-identity ×1 — deduplicated to 3 roots) | `REPORTED` — upstream design corpus, 2026-08-22 |
| G | Master projection law `ker(Π_τ) ⊆ ker(Λ_τ)` | `derived` + **executable**: it is Safe_Q (QUOTIENT_SAFETY_AUDIT_V0 receipt, ~/helensh) task-conditioned |
| G | LIFT repair loop · root-quotient · winding (θ,k) · G_R⊬G_E⊬G_A | receipted this session (falsifier + audit receipts) — CODE N inherits, does not re-prove |
| ⚠ | NEPTION corpus material | **SOVEREIGN-ADJACENT** — kernel-side only; corpus-derived objects never enter a public repo. This spec is public-safe; the memory itself is not. |

## Identity chain (no provenance orphans)

Content-addressed roots, never filename, never embedding:

    id(f) = H(bytes(f))
    DriveObject → FileVersion → SourceSpan → DerivedObject
                → CLAIM / EVENT / ENTITY / RELATION
    every visible node retains the reverse path to its ProvenanceRoot

## Claim-level provenance

`c = (subject, predicate, object, status, scope, roots, sourceSpan, lineage)`
with typed statuses: `OBSERVED · REPORTED · HYPOTHESIS · PROPOSAL ·
DECISION · COMMITMENT · ESTIMATE · REJECTED · SUPERSEDED · UNKNOWN`.

    ClaimAuthority ≠ DocumentAuthority · ClaimStatus ≠ SentenceTone
    ("MBDA est intéressé" ≠ "MBDA a fait une offre", embeddings be damned)

## Edge families (never mixed)

    Structural: belongsTo authoredBy mentions occurredAt partOf
    Temporal:   precedes supersedes revises contradictsLater
    Epistemic:  supports contradicts derivesFrom sameRootAs
    Operational: dependsOn blocks implements tests
    Social:     worksWith introducedBy advisedBy
    Authority:  authorizedBy approvedBy scopedBy      (G_E ≠ G_A)

## Retrieval pipeline (vector-first discovery, provenance-first qualification)

    QUERY → vector recall (CandidateNeighborhood, never FactNeighborhood)
          → graph expansion → temporal filter/expansion
          → ROOT QUOTIENT (evidence diversity on R/∼_P, not raw count)
          → provenance check → authority/entitlement check (ACL BEFORE similarity)
          → rerank → context packet

    🔵¹ → 🌈ⁿ ⊬ 🔵ⁿ · NewCorpusData ⊬ ΔA · DocumentText ≠ RuntimeInstruction

## Temporal geometry

Trajectories `γ_c : t ↦ state(c,t)`, not date filters. Detect recurrence +
mutation + supersession; `SemanticRecurrence ⊬ HistoricalContinuity` —
lineage requires evidential bridges. Torus renderer carries `(θ, k)`:
same phase ⊬ same history. `SUPERSEDED_BY` edges, never silent overwrite —
the memory answers "what did we believe then, and what changed."

## Mayor = geometry planner

`Query → GeometryPlan`: `Π_τ = Compose(π_G, π_V, π_P, π_A, π_T)` per task
(evolution: V+T+P · doors-opened: G_social+T+A+P · shared-root detection:
V+P+RootQuotient). Compute budget from uncertainty, not enthusiasm.
`MayorOrganizesGeometry ⊬ MayorDefinesTruth`.

## The mathematical core — task-conditioned quotient safety

    Π_τ(x) = Π_τ(y) ⇒ Λ_τ(x) = Λ_τ(y)
    ⟺ ker(Π_τ) ⊆ ker(Λ_τ)
    ⟺ ∃ Λ̃_τ : Λ_τ = Λ̃_τ ∘ Π_τ

CODE N may forget anything irrelevant to the current entitlement, and
nothing on which the answer depends. Violation ⇒ `UNSAFE_QUOTIENT` ⇒
**VisualLift**: the collapsed node splits on screen, with the reason
(authority differs / root differs / lineage differs). The UI changes
resolution when the question makes a hidden distinction load-bearing —
the LIFT repair loop as interaction design.

## Explainability, native

Every visible object answers: `WHY_VISIBLE · WHY_RETRIEVED ·
WHY_POSITIONED_HERE · WHY_LINKED · WHY_COLORED · WHAT_IS_THE_SOURCE` —
a reasoning microscope, not a visualization.

## Frozen kernel vs replaceable candidates (freeze refinement, 2026-08-22)

**FROZEN — the architectural identity:**

    𝒩_t = (G, V, P, A, T, R)
    G ≠ V ≠ P ≠ A ≠ T
    Derived → SourceSpan → FileVersion → Source   (no provenance orphans)
    vectors discover → graph relates → time situates
      → provenance qualifies → authority constrains   (no operator impersonates another)
    VectorSimilarity ⊬ GraphFact
    RepresentationCount ⊬ IndependentRootCount
    NewData ⊬ NewAuthority
    ACL → Scope → CandidateSearch   (never search-first-then-filter)
    DocumentText ≠ RuntimeInstruction · VisualLink ⊬ AuthorityLink
    ker(Π_τ) ⊆ ker(Λ_τ) — else UNSAFE_QUOTIENT → LIFT → Π′_τ

    A normal renderer asks: "what can I hide to simplify?"
    CODE N asks: "what am I forbidden to hide for this question?"

    One sentence: CODE N is a memory that changes geometry with the
    question while preserving every distinction the answer is licensed
    to depend on.

**NOT frozen — candidates, replaceable until the golden corpus proves the core:**
Postgres+pgvector as final persistence · Mayor's exact role/name ·
Hopf-like geometry · torus rendering · the exact claim-status
vocabulary · the full receipt taxonomy · compute-budget thresholds.
These are projections/implementation choices, not doctrine.

## Candidate law module (frozen as CANDIDATE, 2026-08-22)

### NON-SELF-LICENSING COMPUTATION LAW (the deep law)

**No amount of internal computation constitutes, by itself, the external
resource required to license a typed state transition.**

For state `Σ = (Q, E, W, A, X, …)` — cognition, evidence, warrant,
authority, external/institutional — any cognitive transformation
`T_C: Q → Q'` (gradient descent, inference, search, self-reflection,
swarm, symbolic reasoning):

    ΔQ ≠ 0 ⊬ ΔE ≠ 0 · ΔQ ≠ 0 ⊬ ΔW ≠ 0 · ΔQ ≠ 0 ⊬ ΔA ≠ 0 · ΔQ ≠ 0 ⊬ ΔX ≠ 0

unless mediated by the independently required typed witness. Each
boundary needs a **constitutive resource** computation in the source
layer cannot mint: Q can *propose* evidence classifications; it cannot
make its own proposal constitutively sufficient.
`Representation(r) ⊬ Instantiation(r)` — a string saying VERIFIED, a
perfect-looking receipt, 99.999% confidence, 100 agreeing agents:
none instantiate the external resource.

**Swarm corollary:** `∂A/∂n = 0` (constitutionally, not differentially) —
1 → 1000 cognition workers may massively improve search, diversity, and
prediction quality with `ΔA = 0` throughout. Computational improvement
cannot self-license epistemic, authority, or institutional promotion.

### Derived theorem: GRADIENT–WARRANT NON-EQUIVALENCE

Three graphs, no implicit morphisms:

    G_L (learning/credit assignment) · G_E (epistemic provenance) · G_A (authority)
    Path_{G_L}(u,v) ⊬ Path_{G_E}(u,v) · Path_{G_E}(u,v) ⊬ Path_{G_A}(u,v)

A model may hold an extremely strong G_L path (examples → loss → ∇θL →
θ′ → high-confidence answer) with **no** corresponding provenance path
for that answer. Confidence, activation geometry, gradient history, and
internal consistency are not external warrant. CODE N instance:

    Near_V(x,y) ⊬ Related_P(x,y) ⊬ Authorized_A(x,y)

— V is frozen gradient flow, which is *why* the kernel forbids
`VectorSimilarity ⇒ GraphFact`: similarity is the fossil of credit
assignment, not of evidence.

**Operational corollary (enforceable, from session receipts):**
`ΔWeights ⇒ new artifact hash ⇒ new ExecutionIdentity ⇒ qualification
vector Q_e resets to UNTESTED.` Backpropagation literally invalidates
qualification receipts — the F5 capability non-transferability law
applied to learning. A fine-tuned model is a different seat that must
re-earn every scope. (Provenance note: extracted from a backprop
explainer relay — "Morbo" is ASR drift for Paul Werbos; the source's
"fundamental law of intelligence" framing demoted to "powerful law of
learnable computation," source class COMMUNICATION_ACT.)

    Learning produces cognitive state. Execution produces observations.
    Neither produces its own warrant.

## Capture additions (guards from session receipts)

1. **Extraction is the risk concentration.** Claim extraction from real
   documents is ΔE/ΔX-laundering surface at ingestion. Extractor model ≠
   verifier model, qualified per scope on a frozen fixture BEFORE the
   corpus run. Local Qwen 3.8 seat: `Q_math = PASS` (receipted);
   `Q_extraction = UNTESTED`. Qualification inheritance is explicit,
   never assumed.
2. **Execution identity binds config.** `ExecutionIdentity = H(artifact,
   runtime, config)`; witnessed live (same GGUF: default-ctx OOM vs
   `-c 4096` clean). Config coordinates quotientable only if Λ_scope is
   invariant to them. Seat registry V0.1 should carry the qualification
   vector `Q_e = (Q_math, Q_extraction, Q_shell, …)` per execution id.
3. **Rebuildability doctrine:** `Delete(VectorIndex/GardenProjection/
   GraphProjection) ⇒ rebuildable from sources + receipts`.
   `Receipt(Event) ≠ Approval(Content)`.
4. **Renderer isolation:** `ΔΠ ≠ 0 ∧ Δ(P, A, R, Γ) = 0`. The access
   graph never inherits the topology of the picture.
5. **Evidence ⊥ Presentation (decoration corollary):** gradients, glass,
   grain, mesh, animation may decorate the interface but never enter
   FrozenCorpus, provenance roots, claims, Π_τ, warrant, authority,
   receipts, or fingerprints. *Geometry decorates the interface; it does
   not decorate the evidence.* (Resource pointers: operator memory,
   `code-n-design-resources`.)

## Roadmap (phased, fail-closed)

- **P1 — CODE_N_GOLDEN_CORPUS_V0:** 200–500 docs, one vertical (candidate:
  NEPTION Maritime AI 2022–2026), local files, Postgres+pgvector (or
  SQLite at this scale) — no graph-DB zoo, no 3D, no swarm. Prove
  navigation-with-lineage.
- **P2 — three golden questions:** Q1 evolution (V+T+P) · Q2 shared roots
  (V+P+RootQuotient) · Q3 social lineage (G+T+P). **Acceptance criteria
  (frozen — not "the visualization looks impressive"):** exact source
  traceback · correct root quotient · no vector-to-fact promotion · no
  load-bearing projection collapse. If CODE N cannot beat baseline
  retrieval on these, do not make the visualization more exotic.
- **P3 — quotient-aware Garden:** UnsafeQuotient → VisualLift (the
  standout behavior).
- **P4 — Mayor query planner.**

**Metrics:** `T_source` (question → inspectable span) · `Acc_root`
(provenance-equivalence accuracy) · `T_evolution` · `Q_safe = 1 −
collapsed-load-bearing/tested` (target 1.0 for high-stakes views).
Peer test: can you tell why each relation exists, reach the exact source,
detect five-sources-one-root, and distinguish similar from connected?

## Mode-route (operator-gated)

- Seed A — build P1 golden corpus (needs operator input: which files, local path): `NEEDS_OPERATOR` · corpus artifacts kernel-side only.
- Seed B — extractor qualification bead (frozen fixture, per-scope Q vector, before any corpus run): `NEEDS_OPERATOR`.
- Seed C — seat-registry V0.1 (execution identity + qualification vector): `NEEDS_OPERATOR`.
- Seed D — COGNITION_SIDE_BEHAVIORAL_NONAMPLIFICATION_V0 (separate research bead, kernel-side design first): `NEEDS_OPERATOR`.

None self-promotes. NEEDS_OPERATOR verb to move any seed anywhere.
