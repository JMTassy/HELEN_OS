---
authority: NON_SOVEREIGN
canon: NO_SHIP
lifecycle: PROPOSAL
artifact_type: TEST_SPEC
proposal_id: SEMANTIC_OBJECT_MODEL_TESTS_V1
source: HELEN_SEMANTIC_PULL_ARCHITECTURE (LaTeX formalization)
---

# SEMANTIC OBJECT MODEL — Test Spec V1

Formal adversarial test suite for the HELEN Canonical Semantic Object (CSO) model.

Implementation: `src/semantic_object_model.py`
Test runner: `tests/test_semantic_object_model.py`

---

## Foundational definitions under test

```
H = (G, R, P)
  G = Canonical Semantic Graph
  R = Receipt system
  P = Projection operators

CSO = (id, type, payload, relations, provenance, receipts)
h(o) = SHA256(canonical_serialization(o))
```

---

## Property 1 — Canonicalization determinism

**Claim:** Same CSO content → same hash, always.

**Tests:**
- P1.1: Two CSOs with identical fields produce identical h(o)
- P1.2: Field order in payload does not change h(o)
- P1.3: Whitespace variation in payload does not change h(o)
- P1.4: Two CSOs with any field difference produce different h(o)

**Adversarial:**
- P1.A: Unicode normalization attack — same string, different byte representations → must produce same hash
- P1.B: Null vs missing field → must produce different hash (strict canonicalization)

---

## Property 2 — Truth Closure Law (Emergent Property 1)

**Claim:** G_{t+1} = G_t ∪ E_t if validated, else G_t unchanged.

**Tests:**
- P2.1: Validated event appended → graph grows by exactly 1
- P2.2: Unvalidated event rejected → graph unchanged
- P2.3: Receipt-missing event rejected → graph unchanged
- P2.4: Sequential events accumulate correctly: G_t = union of G_0..E_{t-1}

**Adversarial:**
- P2.A: Attempt to mutate existing node → rejected; graph unchanged
- P2.B: Attempt to delete a node → rejected (append-only)
- P2.C: Event with invalid receipt hash → rejected

---

## Property 3 — Replay Determinism (Emergent Property 2)

**Claim:** Replay(G, t) = G_t for all t.

**Tests:**
- P3.1: Replay from genesis with same events produces same graph
- P3.2: Replay is independent of wall-clock time
- P3.3: Replay of empty event log produces empty graph
- P3.4: Replay to intermediate t produces correct partial graph

**Adversarial:**
- P3.A: Replay with shuffled events that share no dependencies → must detect ordering violation
- P3.B: Partial replay (first k events) + re-append remaining → same as full replay

---

## Property 4 — Projection determinism (Emergent Property 3)

**Claim:** S_t = P(G_{<=t}) — same graph → same projected state.

**Tests:**
- P4.1: Same graph produces same projection output
- P4.2: Different graph (even 1 node different) produces different projection
- P4.3: Projection of empty graph is well-defined (not error)

**Adversarial:**
- P4.A: Projection called twice on same graph → identical output (no hidden state)

---

## Property 5 — Bounded retrieval (Emergent Property 4)

**Claim:** |T(Q)| ≤ B_d × B_w (depth × branching factor).

**Tests:**
- P5.1: Retrieval on deep graph respects depth bound B_d
- P5.2: Retrieval on wide graph respects branching bound B_w
- P5.3: Retrieval with B_d=1 returns only direct neighbors
- P5.4: Retrieval with B_d=0 returns only the query root node

**Adversarial:**
- P5.A: Circular graph (A→B→A) — retrieval must terminate within bounds
- P5.B: Graph with B_w > policy bound — branching is clipped, not error

---

## Property 6 — Namespace identity isolation (Emergent Property 5)

**Claim:** id = namespace || local_id; h(o) = H(namespace || payload). No cross-namespace collision.

**Tests:**
- P6.1: Same local_id in different namespaces → different global id
- P6.2: Same namespace + same local_id → same global id (stable)
- P6.3: CSO from namespace A cannot be retrieved via namespace B query
- P6.4: Hash includes namespace — payload collision across namespaces is impossible

**Adversarial:**
- P6.A: Attempt to insert CSO with id that crosses namespace boundary → rejected
- P6.B: Query without namespace → rejected or scoped to default namespace only

---

## Property 7 — Sovereign vs derived state (Emergent Property 6)

**Claim:** Loss of derived state is recoverable. Loss of sovereign state = system failure.

**Tests:**
- P7.1: Derived node can be recomputed from sovereign graph
- P7.2: Sovereign node marked; deletion attempt raises SovereignViolation
- P7.3: Derived node deletion is allowed (recoverable)
- P7.4: Full graph replay reconstructs all derived state

**Adversarial:**
- P7.A: Mark a node as sovereign, then attempt mutation → SovereignViolation
- P7.B: Derived node computed incorrectly → re-projection from sovereign graph corrects it

---

## Property 8 — Kernel authority law

**Claim:** Authority(x) = 1 only if x ∈ CSO and validated. Renderers and embeddings have Authority = 0.

**Tests:**
- P8.1: Validated CSO has Authority = 1
- P8.2: Renderer output (non-CSO) has Authority = 0
- P8.3: Embedding vector has Authority = 0
- P8.4: Unvalidated CSO candidate has Authority = 0

**Adversarial:**
- P8.A: Renderer claims Authority = 1 → rejected at gate
- P8.B: Embedding claims canonical status → rejected

---

## Property 9 — Ontological closure (Global Theorem)

**Claim:** If all transitions are receipted + all objects canonicalized + all projections deterministic → H is a closed semantic system: G_t is uniquely reconstructible.

**Tests:**
- P9.1: Full system with receipted events + canonical objects → replay produces identical G_t
- P9.2: System with one unreceipted event → replay fails closed (incomplete state flagged)
- P9.3: System with one non-canonical object → hash mismatch detected

**Adversarial:**
- P9.A: Inject non-deterministic projection (random seed) → system detects replay divergence
- P9.B: Introduce hash collision (crafted payload) → collision resistance holds (SHA-256 property)

---

## Pass/fail contract

All 29 tests must pass. Any failure is a SHIP-class blocker.

Failure modes:
- `CANONICALIZATION_DRIFT` — same content, different hash
- `MUTATION_ADMITTED` — append-only violated
- `REPLAY_DIVERGENCE` — same events, different state
- `BOUND_EXCEEDED` — retrieval exceeded B_d × B_w
- `NAMESPACE_COLLISION` — cross-namespace identity leak
- `SOVEREIGN_VIOLATION` — sovereign node mutated or deleted
- `AUTHORITY_LEAK` — renderer/embedding claimed authority
- `CLOSURE_BROKEN` — system not fully reconstructible

---

*NON_SOVEREIGN · NO_SHIP · PROPOSAL · TEST_SPEC*
