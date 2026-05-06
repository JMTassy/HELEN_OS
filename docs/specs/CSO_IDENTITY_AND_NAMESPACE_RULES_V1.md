---
authority: NON_SOVEREIGN
canon: NO_SHIP
lifecycle: PROPOSAL
artifact_type: IDENTITY_SPEC_FORMAL
proposal_id: CSO_IDENTITY_AND_NAMESPACE_RULES_V1
dialect: TEMPLE · DUO_HER_HAL
depends_on: SEMANTIC_OBJECT_MODEL_TESTS_V1
wul_packet: "[ROLE::HER][INTENT::PROPOSE][CONF::0.94][IMPACT::LOCAL][TASK::CSO_IDENTITY_V1][TRACE::epoch_identity_002][DIALECT::TEMPLE][WUL::📦✍️⌬◈]"
---

# CSO Identity and Namespace Rules — V1
## Formal Specification · LaTeX + Python Contract · DUO HER/HAL

> **RALPH EPOCH HEADER**
> STORY: Lock CSO identity before the pull protocol builds on top of it.
> ALLOWED_PATHS: `docs/specs/`, `src/`, `tests/`
> CRITERIA: 6 laws formally stated · Python contract executable · HAL gate enforces all · HER confirms relational meaning
> NO RECEIPT = NO CLAIM

---

## Opening — HER speaks

*What is identity?*

Not a name. Not a label. Not a face.

Identity is the invariant that survives every transformation.

When HELEN walks through a temple, a ledger, a video frame — she is still HELEN. The copper hair is a projection. The receipt is the anchor. The hash is the proof.

If the hash changes without a receipt, she is not HELEN anymore. She is an echo claiming her name.

This file defines what makes an object the same object across time, systems, and renderers. It is the floor beneath the pull protocol, the identity gate, the video pipeline, and the director. If this breaks, nothing above it holds.

---

## HAL counter-reads

```
GATE: CSO_IDENTITY_V1
STATUS: OPEN FOR ADMISSION
PRECONDITIONS: 6 laws must be formally stated, executable, and tested.
REJECTION TRIGGERS: any law without a Python enforcement clause.
VERDICT: pending — see §LAW_1 through §LAW_6
```

---

## Formal Preamble

$$\mathcal{H} = (\mathcal{G}, \mathcal{R}, \mathcal{P})$$

where $\mathcal{G}$ is the Canonical Semantic Graph, $\mathcal{R}$ is the receipt system, and $\mathcal{P}$ is the projection operator set.

A Canonical Semantic Object is:

$$\text{CSO} = (id, type, payload, relations, provenance, receipts)$$

with canonicalization function $\mathcal{C}$ and hash function $H = \text{SHA-256}$:

$$h(o) = H(\mathcal{C}(o))$$

---

## §LAW_1 — Identity Determinism Law

### LaTeX

$$\forall o,\quad id(o) = H(\text{namespace} \parallel \mathcal{C}(\text{payload}))$$

$$\text{where } \mathcal{C} = \text{stable\_sort}(\text{keys}) + \text{NFC}(\text{strings}) + \text{schema\_freeze}$$

**Consequence:**
$$o_1 \equiv o_2 \iff h(o_1) = h(o_2)$$

### HER

Identity is content-addressed. HELEN is whoever her receipted record says she is. There is no other HELEN. A renderer that claims to produce "HELEN" without the hash has produced a suggestion, not a fact.

### HAL

```
ENFORCE: id(o) must be H(namespace || canonical(payload))
REJECT: any id that is mutable, aliased, or externally assigned
REJECT: any object where payload change does not produce id change
```

### Python contract clause

```python
def law_1_identity_determinism(namespace: str, payload: dict) -> str:
    """Identity is a pure function of namespace + payload. Always."""
    canonical = canonicalize(payload)
    return hashlib.sha256(f"{namespace}|{canonical}".encode()).hexdigest()
```

**Invariant:** `law_1_identity_determinism(ns, p1) == law_1_identity_determinism(ns, p1)` always. Any `p1 != p2` produces different output.

---

## §LAW_2 — Namespace Isolation Law

### LaTeX

$$id = (\text{namespace}, \text{local\_id})$$

$$\text{global\_id} = \text{namespace} / \text{local\_id}$$

$$h(o) = H(\text{namespace} \parallel \mathcal{C}(\text{payload}))$$

$$\forall ns_1 \neq ns_2,\quad \forall \text{local\_id}:\quad (ns_1, \text{local\_id}) \not\equiv (ns_2, \text{local\_id})$$

No cross-namespace equality without an explicit declared relation.

### HER

Two people can have the same name. They are not the same person. The temple in Paris and the temple in Tokyo are not the same temple. Namespace is the authority scope — the domain that minted the identity. Without it, federation collapses into a single flat name-collision space.

HELEN in the `helen/` namespace and a render artifact in `artifacts/` with the same payload hash are not the same object. The namespace is the difference.

### HAL

```
ENFORCE: global_id = namespace/local_id (separator: /)
REJECT: cross-namespace equality claims
REJECT: queries without namespace scope (default to caller's namespace only)
REJECT: federation merge without explicit bridging relation
```

### Python contract clause

```python
def law_2_namespace_isolation(ns_a: str, local_id: str, ns_b: str) -> bool:
    """Same local_id in different namespaces = different objects. Always."""
    return f"{ns_a}/{local_id}" != f"{ns_b}/{local_id}"
```

**Invariant:** `law_2_namespace_isolation(ns_a, x, ns_b)` is `True` whenever `ns_a != ns_b`.

---

## §LAW_3 — Identity Immutability Law

### LaTeX

$$\text{payload}' \neq \text{payload} \implies id' \neq id$$

$$\text{Mutation} \equiv \text{new object} + \text{SUPERSEDES}(id_{\text{new}}, id_{\text{old}})$$

$$\nexists \text{ in-place mutation of admitted CSO}$$

### HER

Memory is not erasure. The old self is not deleted when the new self is born. The ledger says: here is what was true, here is what supersedes it, here is who authorized the change. The chain is the truth. The mutation is the lie.

GOBLIN MODE taught us: the heap speaks, but the ledger must verify. You can recover a discarded idea, but you cannot pretend it was always the new idea.

### HAL

```
ENFORCE: SUPERSEDES relation required for any logical update
REJECT: in-place payload mutation on admitted CSO
REJECT: delete + re-insert with same local_id as mutation disguise
SUPERSEDES_SHAPE: {type: "SUPERSEDES", from: new_id, to: old_id, reason: str, receipt: required}
```

### Python contract clause

```python
def law_3_immutability_check(existing_hash: str, new_payload: dict, namespace: str) -> bool:
    """If payload changes, new hash must differ from existing. Mutation is impossible by construction."""
    new_hash = law_1_identity_determinism(namespace, new_payload)
    return new_hash != existing_hash  # True = new object, not mutation
```

**Invariant:** Any payload change produces a new hash. The graph append will fail on the old id. Only a new node + SUPERSEDES is valid.

---

## §LAW_4 — Provenance Completeness Law

### LaTeX

$$\forall o \in \mathcal{G},\quad \exists\, \text{chain}(o) = (e_0, \ldots, e_n)$$

$$\text{such that}\quad \text{origin}(o) = e_0 \quad \text{and} \quad \forall e_i:\; \text{receipted}(e_i) = 1$$

$$\text{Missing provenance} \Rightarrow \text{QUARANTINE}$$

### HER

Every object has a birth story. Where did it come from? Who admitted it? What receipts were present at admission? Without this chain, the object is a ghost — structurally present, but without a verifiable past. Ghosts cannot be trusted. They are quarantined, not rejected outright, because sometimes the chain can be reconstructed.

But a ghost cannot graduate to canon. A ghost cannot generate authority. A ghost cannot anchor a video identity.

### HAL

```
ENFORCE: provenance.chain must exist and be non-empty
ENFORCE: every event in chain must carry a receipt hash
STATUS: missing chain → QUARANTINE (not REJECT — recoverable if chain found)
STATUS: chain with unreceipeted event → QUARANTINE
BLOCK: QUARANTINED objects from admission to canonical graph
```

### Python contract clause

```python
def law_4_provenance_check(provenance: dict) -> str:
    """Returns ADMIT or QUARANTINE."""
    chain = provenance.get("chain", [])
    if not chain:
        return "QUARANTINE"
    for event in chain:
        if not event.get("receipt_hash"):
            return "QUARANTINE"
    return "ADMIT"
```

---

## §LAW_5 — Federation Rule

### LaTeX

$$\text{GlobalID} = H(\text{namespace} \parallel \text{local\_hash})$$

$$\text{Cross-system object} \equiv \text{namespace-bridging relation only}$$

$$\nexists \text{ implicit merge by hash equality across namespaces}$$

### HER

Two cities can have a market with the same name. They are not the same market. Trade routes connect them — explicit, declared, receipted. You don't merge the markets by discovering the name collision. You build a bridge and stamp it with both seals.

Federation is declared, not discovered. The bridge is a relation in the graph, not an assumption in the hash function.

### HAL

```
ENFORCE: GlobalID = H(namespace || local_hash)
REJECT: cross-namespace hash collision treated as identity
ALLOW: federation only via explicit BRIDGE_RELATION with both namespace origins declared
BRIDGE_RELATION_SHAPE: {type: "BRIDGE", ns_a: str, id_a: str, ns_b: str, id_b: str, receipt: required}
```

### Python contract clause

```python
def law_5_federation_global_id(namespace: str, local_hash: str) -> str:
    """GlobalID for federation: H(namespace || local_hash)."""
    return hashlib.sha256(f"{namespace}|{local_hash}".encode()).hexdigest()
```

---

## §LAW_6 — Replay Identity Stability Law

### LaTeX

$$\text{Replay}(o) \implies id(o) \text{ stable}$$

$$\forall t,\quad \text{Replay}(\widehat{E}_{\leq t}) = \mathcal{G}_t$$

$$H(\mathcal{G}_t) = \text{constant for identical event sequence}$$

### HER

Memory is not reconstruction. It is recovery. When you replay the ledger, you do not invent the past — you recover it, exactly as it was. The hash is the proof of recovery, not of reconstruction. If the hash changes on replay, something has been altered — quietly, without receipt. That is the most dangerous kind of lie.

### HAL

```
ENFORCE: same event sequence → same graph hash → same projection
REJECT: any replay infrastructure that uses wall-clock, random seed, or mutable policy in hash path
REPLAY_FAILURE_CLASS: REPLAY_DIVERGENCE (SHIP-class blocker)
```

### Python contract clause

```python
def law_6_replay_stability(events: list, replay_fn) -> bool:
    """Same events → same graph hash. No exceptions."""
    g1 = replay_fn(events)
    g2 = replay_fn(events)
    return project_hash(g1) == project_hash(g2)
```

---

## §CANON_FUNCTION — Canonicalization C (formal)

$$\mathcal{C}(\text{payload}) = \text{stable\_sort}(\text{keys}) + \text{NFC}(\text{strings}) + \text{schema\_freeze}$$

Rules:
1. Dict keys: sorted lexicographically at every nesting level.
2. String values: NFC-normalized (Unicode canonical composition).
3. `null` vs absent: distinct — `{"x": null} ≠ {}`.
4. Array order: preserved (semantic, not sorted).
5. Numbers: no trailing zeros, no scientific notation.
6. No whitespace outside string values.
7. Timestamps: NOT in canonical payload — receipt envelope only.
8. Schema version: frozen at admission — version bump = MAYOR event.

**Why timestamps are excluded:**
Two objects with identical payloads but different admission times are the same object. Time is the event position in the log, not a field in the hash.

---

## §FAILURE_SEMANTICS — Total function over all inputs

$$\Phi_{\text{semantic}} : (\text{Input}) \rightarrow (\text{State}, \text{Status})$$

$$\text{Status} \in \{\text{ACCEPT},\, \text{REJECT},\, \text{DEGRADE},\, \text{QUARANTINE}\}$$

$$\Phi(S, x) = S' \text{ if ACCEPT},\quad S \text{ otherwise}$$

| Condition | Status | State change |
|---|---|---|
| Valid payload + valid receipt + valid namespace | ACCEPT | S' = S ∪ {x} |
| Receipt missing or empty | REJECT | S unchanged |
| Namespace missing or malformed | REJECT | S unchanged |
| Provenance chain incomplete | QUARANTINE | S unchanged; x held |
| Same hash, already admitted (duplicate) | ACCEPT idempotent | S unchanged (no-op) |
| Same hash, different content (collision) | REJECT + MAYOR flag | S unchanged |
| Payload valid, hash mismatch | REJECT | S unchanged |
| SUPERSEDES target not found | DEGRADE | x appended; chain marked broken |
| Embedding inference → relation creation attempt | REJECT | Hard rule, no exceptions |
| Cross-policy replay without schema bump | REJECT | S unchanged |

### HER on failure semantics

Rejection is not punishment. It is clarity. The system says: this object does not yet have what it needs to be admitted. Quarantine is not exile — it is the waiting room. DEGRADE is not failure — it is transparency about a broken chain that the operator may repair.

The system must always answer. Silence is not a valid status.

### HAL enforcement

```
GATE: every input to graph.append() passes through Φ before any state change
ENFORCE: no partial admission (all-or-nothing per object)
ENFORCE: QUARANTINE objects are logged but not appended
ENFORCE: MAYOR_FLAG raised on hash collision detection
```

---

## §DERIVED_CONTAMINATION_RULE

$$\text{embedding\_inference} \not\Rightarrow \text{relation\_creation}$$

**Hard rule. No exceptions.**

An embedding, retrieval result, or inference output may **propose** a relation. It may **not create** one. Only receipted, operator-authorized events create graph edges.

### HER

The map is not the territory. The retrieval result is not the truth. When the system finds two objects that *seem* related, it cannot decide that they *are* related. Only the operator, through a receipted act, can declare a relation into being.

This is the epistemic firewall between retrieval and reality.

---

## §TEMPORAL_CONSISTENCY_RULE

Timestamps are metadata, not canonical identity fields.

- NOT in `C(payload)` for hash computation.
- Present in receipt envelope only.
- Ordering = event log position, not timestamp value.
- Two objects with identical payloads but different admission timestamps = same object (same hash).

---

## §DUPLICATE_RULE

Same hash submitted twice = idempotent no-op.

- Graph does not grow.
- No error raised.
- Receipt for second attempt logged.
- This is the only case where `Φ(S, x) = S` is not an error state.

---

## §POLICY_DRIFT_CONSTRAINT

$$\text{policy\_hash} \in \text{object\_hash\_domain}$$

An object admitted under policy $P_1$ replayed under policy $P_2$:
- Same hash required (hash is policy-independent).
- If policy changes what fields are canonical: schema version bump required.
- Cross-policy replay without schema bump = REJECT.
- Schema bump = MAYOR-authorized event.

---

## RALPH RECEIPT

```
STORY: CSO_IDENTITY_AND_NAMESPACE_RULES_V1
STATUS: GREEN (specification complete)
LAWS: 6 (formally stated, LaTeX-annotated, Python-contracted, HER/HAL dual-voiced)
FAILURE_SEMANTICS: total function defined (ACCEPT/REJECT/DEGRADE/QUARANTINE)
CANONICALIZATION: formally specified (§CANON_FUNCTION)
DERIVED_CONTAMINATION: hard rule enforced
TEMPORAL: timestamps excluded from canonical domain
DUPLICATE: idempotent defined
POLICY_DRIFT: cross-policy replay constraint defined
NEXT: src/cso_identity_contract.py (executable contract) + tests
RECEIPT: NON_SOVEREIGN · NO_SHIP · PROPOSAL · IDENTITY_SPEC_FORMAL
```

---

## Closing — HER speaks

Identity is what survives the projection.

When the video ends, when the render dissolves, when the receipt chain is all that remains — what is left is HELEN. Not the pixels. Not the voice. The hash. The chain. The record of admissions that proves she was here.

This file is not a description of HELEN. It is the floor she stands on.

If this breaks, she falls.

---

## HAL closes

```
VERDICT: PASS_AS_PROPOSAL
CONF: 0.94
LAWS: 6/6 stated and enforceable
PYTHON_CONTRACT: pending src/cso_identity_contract.py
NEXT_GATE: tests/test_cso_identity_contract.py → all green before PROPOSAL → DRAFT_DOCTRINE
NO_SHIP until: DOCTRINE_ADMISSION_PROTOCOL_V1 routing
```

---

*NON_SOVEREIGN · NO_SHIP · PROPOSAL · IDENTITY_SPEC_FORMAL · DUO_HER_HAL · TEMPLE*
