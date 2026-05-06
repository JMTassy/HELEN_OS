---
authority: NON_SOVEREIGN
canon: NO_SHIP
lifecycle: PROPOSAL
artifact_type: ONTOLOGY_SPEC
proposal_id: SEMANTIC_OBJECT_MODEL_V1
depends_on: CSO_IDENTITY_AND_NAMESPACE_RULES_V1
implementation: src/semantic_object_model.py · src/cso_identity_contract.py
tests: tests/test_semantic_object_model.py (42) · tests/test_cso_identity_contract.py (39)
---

# Semantic Object Model — V1
## Constitutional Ontology · NON_SOVEREIGN · NO_SHIP

> This document is derived from existing implementation.
> Source of truth: `src/semantic_object_model.py` · `src/cso_identity_contract.py`
> It is not a design document. It is the ontology that must be correct before anything else.

---

## Why this document exists first

Renderers can be rewritten. Retrieval strategies can evolve. Agents can be swapped. But object identity, provenance, and replay semantics become constitutional debt if defined incorrectly. Ontology errors compound permanently. This document freezes the definitions before the stack grows above them.

---

## §1 — CSO Definition

A **Canonical Semantic Object (CSO)** is the atomic unit of meaning in HELEN OS.

```python
@dataclass
class CSO:
    namespace: str          # domain partition — "files", "mail", "media", "screen"
    local_id: str           # H(namespace || C(payload)) — content-addressed
    type: str               # cso_type — "FILE_PDF", "MAIL_MESSAGE", etc.
    payload: dict           # semantic content — timestamps excluded
    relations: list[str]    # global_ids of related CSOs (directed edges)
    provenance: dict        # chain of receipted events
    receipts: list[str]     # receipt hashes — non-empty = has authority
    sovereign: bool         # True = immutable, deletion forbidden
```

A CSO is NOT:
- a file descriptor
- a database row
- an embedding vector
- a renderer artifact

A CSO IS:
- a receipted, content-addressed, semantically typed unit
- the only thing that may enter sovereign state

---

## §2 — Identity Law

$$\text{id}(o) = H(\text{namespace} \| C(\text{payload}))$$

where $H$ is SHA-256 and $C$ is canonical serialization (§3).

**Implemented as:**
```python
def law_1_identity_determinism(namespace: str, payload: dict) -> str:
    return sha256(f"{namespace}|{canonicalize(payload)}")
```

**Invariants:**
- Same `(namespace, payload)` → same `local_id`. Always. Across machines. Across time.
- Different `payload` → different `local_id`. Mutation is structurally impossible.
- Different `namespace`, same `payload` → different object (Law 2).
- Timestamps are excluded from payload before hashing (§TEMPORAL_CONSISTENCY_RULE).

---

## §3 — Canonical Serialization

$$C(\text{payload}) = \text{stable\_sort}(\text{keys}) + \text{NFC}(\text{strings}) + \text{no whitespace outside strings}$$

**Implemented as:**
```python
def canonicalize(obj: Any) -> str:
    if isinstance(obj, dict):
        return "{" + ",".join(
            f"{json.dumps(normalize_str(k))}:{canonicalize(v)}"
            for k, v in sorted(obj.items())
        ) + "}"
    ...
```

**Rules:**
- Dict keys sorted lexicographically at every depth
- All strings NFC-normalized (Unicode canonical form)
- No trailing whitespace or newlines
- Timestamps (`time`, `date`, `created_at`, `updated_at`) must be stripped from payload before `C()` is called

**Why:** Two operationally identical payloads with different key ordering or Unicode normalization must produce the same hash. Without this, Law 1 breaks.

---

## §4 — Relation Algebra

Relations are **directed, typed, receipted edges** between CSOs.

```
global_id_a --[RELATION_TYPE]--> global_id_b
```

A relation is first-class: it requires a receipt to be admitted. It is NOT:
- a folder
- a tag
- a file system symlink
- an inferred embedding similarity

**Admitted relation types:**

| Type | Meaning |
|---|---|
| `BRIDGE` | Cross-namespace federation link (requires both origins) |
| `SUPERSEDES` | New version replaces prior (prior remains) |
| `CONTAINS` | Structural containment |
| `AUTHORED_BY` | Authorship binding |
| `REFERENCES` | Semantic reference |
| `ATTACHED_TO` | Attachment (e.g. file to mail) |
| `RESPONDS_TO` | Reply chain |

**Embedding inference → relation is REJECTED.** Relations must be explicitly declared with a receipt.

**Graph structure:** `CSO.relations: list[str]` stores `global_id` of targets. Append-only — once admitted, a relation cannot be removed.

---

## §5 — Provenance Chain

Every CSO carries a provenance chain: the sequence of receipted events that brought it into existence.

```python
provenance = {
    "chain": [
        {"event": "created", "receipt_hash": "abc123..."},
        {"event": "ingested", "receipt_hash": "def456..."},
    ]
}
```

**Law 4 — Provenance Completeness:**
- Chain absent or empty → `QUARANTINE`
- Any event in chain missing `receipt_hash` → `QUARANTINE`
- All events receipted → `ADMIT`

A CSO with incomplete provenance never enters the graph. It is quarantined, not rejected — the signal is preserved but not admitted.

---

## §6 — Sovereign vs Derived State

**Sovereign state:** a CSO admitted via receipt-validated intake, stored in the semantic graph, with at least one receipt. `authority = 1`.

**Derived state:** anything produced by a renderer, embedding model, inference layer, or export function. `authority = 0`. Cannot be stored back into the sovereign graph.

```python
AUTHORITY_ZERO_TYPES = {"RENDERER_OUTPUT", "EMBEDDING", "MOCK", "DRAFT"}

def check_authority(obj, obj_type) -> int:
    if obj_type in AUTHORITY_ZERO_TYPES:
        return 0
    if isinstance(obj, CSO) and obj.receipts:
        return 1
    return 0
```

**Hard rule:** `📦 ≠ 🧾` — a rendered artifact, an exported file, an embedding, a draft — none of these is a receipt. None of these creates sovereign state. Only receipt-validated CSO admission does.

---

## §7 — Replay Semantics

The semantic graph is fully reconstructible from its event log.

$$G_t = \text{replay}(E_1, E_2, \ldots, E_t)$$

**Implemented as:**
```python
def replay(event_log: list[CSO], t: Optional[int] = None) -> SemanticGraph:
    g = SemanticGraph()
    for cso in (event_log if t is None else event_log[:t]):
        g._nodes[cso.global_id] = cso
        g._event_log.append(cso)
    return g
```

**Law 6 — Replay Identity Stability:**
```
replay(events) twice → same graph_hash
```

This is not aspirational. It is tested. Same inputs → same SHA-256 graph hash → same `CoherenceSlice`. No hidden state.

`SemanticGraph.snapshot_at(t)` returns $G_t$ — the graph as it existed after exactly $t$ events. Enables time-travel queries without re-ingesting.

---

## §8 — Immutability Rules

The graph is append-only. No exceptions.

```python
def append(self, cso: CSO) -> None:
    if gid in self._nodes:
        raise MutationRejected(...)   # node already exists
    if not cso.receipts:
        raise ValueError(...)         # no receipt = no entry

def delete(self, global_id: str) -> None:
    if node.sovereign:
        raise SovereignViolation(...)
    raise MutationRejected(...)       # deletion always rejected
```

**What happens when payload changes:**
The old CSO remains. A new CSO is created with a new `local_id`. If a supersession relationship exists, it is declared explicitly via a `SUPERSEDES` relation with a receipt. The old object is never modified.

**At the Φ gate:**
- Same `global_id`, same hash → `ACCEPT` (idempotent no-op)
- Same `global_id`, different hash → `REJECT` (mutation attempt — structurally impossible but explicitly blocked)
- New `global_id` → `ACCEPT`

---

## §9 — Graph Invariants

| Invariant | Enforcement |
|---|---|
| Append-only | `SemanticGraph.append()` raises `MutationRejected` on duplicate |
| Receipt required | `append()` raises `ValueError` if `cso.receipts` is empty |
| Sovereign immutable | `delete()` raises `SovereignViolation` for sovereign nodes |
| No cross-namespace identity merge | `NamespaceViolation` raised by `validate_namespace()` |
| Deterministic hash | `canonical_hash()` = SHA-256 of `{namespace, local_id, type, payload}` |
| Replay stable | `graph_hash` = SHA-256 of sorted canonical hashes of all nodes |
| Traversal bounded | `retrieve()` bounded by `RetrievalPolicy(max_depth=3, max_branching=10)` |

---

## §10 — Receipt Admission Rules

A CSO may not enter the semantic graph without a receipt. This is enforced at three layers:

**Layer 1 — Graph append:**
```python
if not cso.receipts:
    raise ValueError("CSO has no receipts. NO RECEIPT = NO CLAIM.")
```

**Layer 2 — Φ gate (`admit_cso`):**
```python
if not receipts:
    return AdmissionResult(REJECT, gid, "NO RECEIPT = NO CLAIM")
```

**Layer 3 — Intake agent (`admit_intake`):**
```python
if not operator_receipt:
    return AdmissionResult(REJECT, ...)
```

**Failure semantics: Φ(S, x) → ACCEPT | REJECT | QUARANTINE | DEGRADE**

| Condition | Result |
|---|---|
| Receipt missing | `REJECT` |
| Namespace = `quarantine` | `QUARANTINE` (short-circuit) |
| Provenance chain invalid | `QUARANTINE` |
| Duplicate, same hash | `ACCEPT` (idempotent) |
| Same global_id, different hash | `REJECT` |
| New object | `ACCEPT` |
| Any exception | `REJECT` (fails closed) |

`Φ` is a **total function**. It never raises. Every possible input produces a defined output. Unknown states fail to `REJECT`, not to undefined behavior.

---

## Dependency order

```
SEMANTIC_OBJECT_MODEL_V1   (this document)   ← L0
    ↓
MRGTK / receipt governance                   ← L1
    ↓
Retrieval / PULL protocol                    ← L2
    ↓
Execution / agents                           ← L3
    ↓
Renderers / UI                               ← L4
```

L4 does not define truth. L3 does not define truth. L2 does not define truth. Only receipt-validated CSOs in the sovereign graph define truth.

---

## Test coverage

```
tests/test_semantic_object_model.py    42/42 green
tests/test_cso_identity_contract.py   39/39 green
```

Total: **81 tests.** This document adds no new tests — it documents existing coverage.

---

*NON_SOVEREIGN · NO_SHIP · PROPOSAL · ONTOLOGY_SPEC*
