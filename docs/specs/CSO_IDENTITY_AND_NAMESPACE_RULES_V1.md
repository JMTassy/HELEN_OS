---
authority: NON_SOVEREIGN
canon: NO_SHIP
lifecycle: PROPOSAL
artifact_type: IDENTITY_SPEC
proposal_id: CSO_IDENTITY_AND_NAMESPACE_RULES_V1
depends_on: SEMANTIC_OBJECT_MODEL_TESTS_V1
---

# CSO Identity and Namespace Rules — V1

If identity is wrong, everything above it becomes unrecoverable.
This file locks identity before the pull protocol builds on top of it.

---

## Law 1 — Identity Determinism Law

```
∀o,  id(o) = H(namespace ∥ C(payload))
```

- Identity is content-addressed.
- No mutable identity. No aliasing without explicit SUPERSEDES relation.
- `C` = canonical serialization (stable sort + NFC normalization + schema freeze).
- `H` = SHA-256.

**Consequence:** Two objects with the same namespace and payload are the same object. Two objects with any difference in either are different objects. There is no third case.

---

## Law 2 — Namespace Isolation Law

```
object_id = (namespace, local_id)
global_id = namespace/local_id
object_hash = H(namespace ∥ C(payload))
```

- No cross-namespace equality without an explicit declared relation.
- Same `local_id` in different namespaces = different objects. Always.
- Namespaces are domain/authority scopes: `helen`, `oracle_town`, `mayor`, `dan_goblin`, etc.

**Consequence:** Federation is possible. Collisions are impossible. Identity is stable across systems.

---

## Law 3 — Identity Immutability Law

```
payload' ≠ payload  ⟹  id' ≠ id
```

- Payloads are immutable once an object is admitted.
- Mutation is represented only as a new object with a `SUPERSEDES` relation pointing to the old one.
- Deleting an admitted object is forbidden (graph is append-only).

**SUPERSEDES relation shape:**
```json
{
  "type": "SUPERSEDES",
  "from": "<new_global_id>",
  "to": "<old_global_id>",
  "reason": "<operator-authored string>"
}
```

---

## Law 4 — Provenance Completeness Law

```
∀o ∈ G,  ∃ chain(o) = (e₀, ..., eₙ)
such that origin(o) = e₀  and  ∀eᵢ, receipted(eᵢ)
```

- No orphan objects.
- Every admitted object must have a receipt chain traceable to a genesis event.
- Missing provenance = QUARANTINE status, not admission.

---

## Law 5 — Federation Rule

```
GlobalID = H(namespace ∥ local_hash)
```

- Cross-system federation is achieved by namespace scoping only.
- Two systems may share objects only through explicit namespace-bridging relations.
- No implicit merge by hash collision (impossible by construction if namespaces differ).

---

## Law 6 — Replay Identity Stability Law

```
Replay(o) ⟹ id(o) stable
```

- Replaying an event log must produce objects with identical hashes.
- If replay produces a different hash for the same logical object, the canonicalization function is broken.
- Hash stability is a SHIP-class invariant.

---

## Canonicalization function C (formal)

```
C(payload) = stable_sort(keys) + NFC_normalize(strings) + schema_freeze
```

Rules:
1. Dict keys sorted lexicographically at all levels.
2. All string values NFC-normalized (Unicode canonical composition).
3. `null` and absent fields are distinct — `{"x": null}` ≠ `{}`.
4. Arrays preserve order (not sorted — order is semantic).
5. Numbers: no trailing zeros, no scientific notation.
6. No whitespace outside of string values.

The canonicalization function is frozen at schema version. A schema version change triggers a re-hash pass and is a MAYOR-authorized event.

---

## Failure semantics (§15 — total function over invalid inputs)

Every CSO input maps to exactly one status. No undefined behavior.

```
Status ∈ { ACCEPT, REJECT, DEGRADE, QUARANTINE }
```

| Condition | Status | Action |
|---|---|---|
| Valid payload + valid receipt + valid namespace | ACCEPT | Append to graph |
| Receipt missing | REJECT | Not appended; log rejection |
| Namespace missing or malformed | REJECT | Not appended |
| Provenance chain incomplete | QUARANTINE | Held; operator routing required |
| Hash collision (same hash, different content) | REJECT | System error; flag for MAYOR |
| SUPERSEDES target not found | DEGRADE | Append but mark chain broken |
| Payload valid, hash mismatch | REJECT | Tamper indicator |
| Duplicate (same hash, already admitted) | ACCEPT (idempotent) | No-op; not an error |

State evolution rule:
```
Φ(S, x) = S'  if ACCEPT
Φ(S, x) = S   otherwise
```

---

## Identity collision impossibility

SHA-256 collision resistance: for any two inputs `a ≠ b`, `H(a) = H(b)` with probability 2⁻²⁵⁶. Namespace prefixing ensures that even payloads that happen to be identical across domains are distinguishable by their global hash.

This is not a probabilistic guarantee in the system design sense — it is treated as a structural invariant. If a collision is ever observed, it is treated as a system failure requiring MAYOR intervention.

---

## Duplicate object handling

Same hash admitted twice = idempotent no-op. The graph does not grow. No error is raised. The receipt for the second attempt is logged but does not create a new node.

This is the only case where `Φ(S, x) = S` is not an error.

---

## Temporal consistency rule

Timestamps are metadata, not canonical identity fields.

- Timestamps are NOT included in `C(payload)` for hash computation.
- Timestamps are included in the receipt envelope only.
- Two objects with identical payloads but different timestamps are the same object (same hash).
- Ordering is determined by the event log position, not by timestamp value.

**Why:** Timestamps introduce non-determinism into canonicalization if included. The event log is the authoritative ordering.

---

## Policy drift constraint

```
policy_hash ∈ object_hash domain
```

An object admitted under policy `P₁` that is replayed under policy `P₂` must produce the same hash (hash is policy-independent). If the policy changes what fields are canonical, a schema version bump is required and all affected objects must be re-admitted under the new schema.

Cross-policy replay without schema bump = REJECT.

---

## Derived contamination rule

```
embedding_inference  ⟹̸  relation_creation
```

Hard rule. No exceptions.

An embedding or retrieval output may PROPOSE a relation. It may not CREATE one. Only receipted, operator-authorized events create relations in the graph.

---

## Next artifacts that depend on this file

- `SEMANTIC_PULL_PROTOCOL_V1.md` — pull retrieval uses namespace-scoped traversal
- `MRGTK_RECEIPT_V0` — receipt envelope uses `object_hash = H(namespace ∥ payload)`
- Video identity gate — character CSO uses namespace `helen/characters/helen_canonical`

---

*NON_SOVEREIGN · NO_SHIP · PROPOSAL · IDENTITY_SPEC*
