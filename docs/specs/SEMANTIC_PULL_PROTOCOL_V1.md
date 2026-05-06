---
authority: NON_SOVEREIGN
canon: NO_SHIP
lifecycle: PROPOSAL
artifact_type: PROTOCOL_SPEC
proposal_id: SEMANTIC_PULL_PROTOCOL_V1
depends_on: CSO_IDENTITY_AND_NAMESPACE_RULES_V1 · HELEN_PULL_INTAKE_BRIDGE_V1 · HELEN_COMPUTER_USE_API_V1
implementation: src/helen_intake_agent.py (cd757b9, 30/30 green)
---

# Semantic Pull Protocol — V1
## Documentation of Existing Implementation · NON_SOVEREIGN · NO_SHIP

> This document describes code that already exists and passes tests.
> It is not a design document. It is a specification derived from implementation.
> Source of truth: `src/helen_intake_agent.py` + `src/helen_computer_use_api.py`

---

## Protocol Definition

The Semantic Pull Protocol is a three-step pipeline that converts raw OS signals into minimum-sufficient semantic state. It is the execution mechanism of `helen.open()` — the replacement for navigation, search, and app-state.

$$\text{Pull}(\text{raw}, r, I) = \text{project\_context}(\text{admit\_intake}(\text{intake\_signal}(\text{raw}), r), I)$$

where $r$ is an operator receipt and $I$ is a query intent.

---

## Step 1 — Classify: `intake_signal(raw) → CSOCandidate`

**What it does:** Converts any raw OS signal into a typed, content-addressed candidate. No receipt yet. No graph write.

**Input forms:**
- `str` → treated as file path
- `{"signal": "FILE", "path": "..."}` → file
- `{"signal": "MAIL", "from_addr": "...", "message_id": "...", ...}` → mail
- `{"signal": "MEDIA", "title": "...", "codec": "...", ...}` → media
- `{"signal": "SCREEN", "ocr_text": "...", ...}` → screen region

**Output:** `CSOCandidate(signal_type, namespace, local_id, cso_type, payload, provenance_stub)`

**Key invariants:**
- `local_id = H(namespace || C(payload))` — content-addressed, Law 1
- Timestamps excluded from payload — §TEMPORAL_CONSISTENCY_RULE
- Unknown signal type → `namespace="quarantine"` (never admitted)
- Never raises — fails to quarantine candidate on exception

**Namespace assignment:**

| Signal | Namespace |
|---|---|
| FILE | `files` |
| MAIL | `mail` |
| MEDIA | `media` |
| SCREEN | `screen` |
| UNKNOWN/ERROR | `quarantine` |

---

## Step 2 — Gate: `admit_intake(candidate, receipt) → AdmissionResult`

**What it does:** Applies the CSO identity law total function Φ(S, x) to the candidate. Returns ACCEPT, REJECT, or QUARANTINE. Never raises.

**Receipt requirement:** `operator_receipt` must be non-empty. Empty receipt → REJECT immediately. `NO RECEIPT = NO CLAIM`.

**Quarantine namespace short-circuit:** If `candidate.namespace == "quarantine"` → QUARANTINE immediately (no further checks).

**Φ gate sequence:**
1. Receipt present? → else REJECT
2. Quarantine namespace? → QUARANTINE
3. `law_4_provenance_check(provenance)` → chain non-empty, all events receipted? → else QUARANTINE
4. Compute `h = law_1_identity_determinism(namespace, payload)`
5. Already in graph with same hash? → ACCEPT (idempotent no-op)
6. Already in graph with different hash? → REJECT (mutation attempt)
7. New object → ACCEPT

**Graph write:** `admit_intake_to_graph(candidate, receipt, graph)` — convenience wrapper that appends admitted CSO to a `SemanticGraph` if ACCEPT.

---

## Step 3 — Project: `project_context(graph, intent) → CoherenceSlice`

**What it does:** Returns the minimum sufficient state for an intent. Pure function of graph state. Deterministic.

**Intent fields:**

| Field | Type | Effect |
|---|---|---|
| `namespace_filter` | `str \| None` | restrict to one namespace |
| `type_filter` | `str \| None` | restrict to one CSO type |
| `max_depth` | `int` (default 3) | traversal depth bound |
| `max_branching` | `int` (default 10) | branching factor bound |

**Output:** `CoherenceSlice(intent, node_count, nodes, graph_hash, namespace_filter, depth_bound)`

**Complexity:** O(V + E) bounded by `max_depth × max_branching` — not a scan.

**Determinism:** Same graph + same intent → same `graph_hash` → same `nodes`. Law 6 holds.

---

## Full pipeline example

```python
from src.helen_intake_agent import intake_signal, admit_intake_to_graph, project_context
from src.semantic_object_model import SemanticGraph

graph = SemanticGraph()

# Step 1: classify
candidate = intake_signal("/docs/contract.pdf")
# → CSOCandidate(cso_type="FILE_PDF", namespace="files", local_id="a3f...")

# Step 2: gate
result = admit_intake_to_graph(candidate, "user:open:2026-05-06", graph)
# → AdmissionResult(status=ACCEPT, global_id="files/a3f...")

# Step 3: project
slice_ = project_context(graph, {"namespace_filter": "files", "type_filter": "FILE_PDF"})
# → CoherenceSlice(node_count=1, nodes={"files/a3f...": {...}}, graph_hash="...")
```

---

## Protocol invariants (all enforced in tests)

| Invariant | Source |
|---|---|
| Same raw signal → same local_id (determinism) | Law 1 |
| Different namespace → different object | Law 2 |
| Payload change → new object, not mutation | Law 3 |
| Empty provenance chain → QUARANTINE | Law 4 |
| Same events → same graph_hash | Law 6 |
| No receipt → REJECT at gate | §FAILURE_SEMANTICS |
| Unknown signal → QUARANTINE, never ACCEPT | §FAILURE_SEMANTICS |
| Duplicate → ACCEPT idempotent, graph unchanged | §DUPLICATE_RULE |
| Projection is pure — no hidden state | §CANON_FUNCTION |

---

## Test coverage

```
tests/test_helen_intake_agent.py    30/30 green  (cd757b9)
tests/test_helen_computer_use_api.py  32/32 green  (8479dd5)
tests/test_cso_identity_contract.py  39/39 green  (dd09eb0)
tests/test_semantic_object_model.py  42/42 green  (d0cbed2)
```

Total: **143 tests, all green.** No new tests required by this document — it documents existing coverage.

---

## What this protocol does NOT define (deferred)

- Cross-device session reconciliation (receipt-chain merge)
- Relation inference proposals (embedding → PROPOSE only, never create)
- Computer Use bridge (screen observation → CSO, requires Anthropic CU API)
- SEMANTIC_PULL_PROTOCOL_V2 (tensor-compressed traversal, deferred pending MAYOR gate)

---

## Receipt status

```
CLAIM: SEMANTIC_PULL_PROTOCOL_V1 (documentation)
IMPLEMENTATION: SHIPPED — cd757b9 + 8479dd5
TESTS: 143/143 green
RECEIPT: pending route via helen_say
```

---

*NON_SOVEREIGN · NO_SHIP · PROPOSAL · PROTOCOL_SPEC*
