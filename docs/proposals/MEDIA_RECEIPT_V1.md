# MEDIA_RECEIPT_V1

**authority:** NON_SOVEREIGN
**canon:** NO_SHIP
**lifecycle:** SCHEMA_DRAFT
**implementation_status:** TESTED_AGAINST_VALIDATOR (10/10 green)
**status:** Schema specification, proposal only
**parent_gate:** `docs/proposals/HELEN_IDENTITY_GATE_V1.md`
**wraps:** `docs/proposals/IDENTITY_GATE_RECEIPT_V1.md` + `docs/proposals/IDENTITY_GATE_RECEIPT_V1_SEQUENCE.md`
**parent_theory:** `docs/theory/CONSTITUTIONAL_MANIFOLD_RENDERING_V0.md`

---

## §1. Purpose

The Media Receipt is the **parent envelope** for any HELEN-generated media
artifact (image, frame, or sequence). It binds together:

- the **asset chain** — source → storyboard → director packet → composition → render
- the **gate chain** — identity sequence receipt + style gate + artifact gate

into one auditable, hash-chained record.

**Hard scope boundary (HAL):**

> **MEDIA_RECEIPT may bind:**
>   source → storyboard → director_packet → composition → render → gates
>
> **MEDIA_RECEIPT may not admit:**
>   canon, sovereign state, publication, identity truth, or final release.

A Media Receipt **proves the chain exists**. It does **not** prove the
media is admitted. Admission is reducer-only.

---

## §2. Required laws

| # | Law                                                    | Enforcement                                            |
| - | ------------------------------------------------------ | ------------------------------------------------------ |
| 1 | `authority` must be `false`                            | `AUTHORITY_VIOLATION` if true                          |
| 2 | `admissible` must be `false`                           | `ADMISSIBILITY_VIOLATION` if true                      |
| 3 | Media receipt does not imply canon                     | doctrinal, propagated via §5                           |
| 4 | Identity sequence verdict must be PASS for ELIGIBLE    | non-PASS → CANDIDATE_ONLY or BLOCKED                   |
| 5 | REJECT blocks media receipt validity                   | `BLOCKED_BY_REJECT` violation                          |
| 6 | REWORK blocks final admissibility but may be candidate | receipt is valid, `admissibility_status = CANDIDATE_ONLY` |
| 7 | All referenced receipt hashes must exist               | `MISSING_*_RECEIPT` violations                         |

---

## §3. Schema

```json
{
  "type": "MEDIA_RECEIPT_V1",
  "media_receipt_id": "string (unique)",
  "project_id":       "string",
  "timestamp":        "ISO 8601 datetime",

  "asset_chain": {
    "source_refs_hash":     "sha256:... (required)",
    "storyboard_hash":      "sha256:... (required)",
    "director_packet_hash": "sha256:... (required)",
    "composition_hash":     "sha256:... (required)",
    "render_hash":          "sha256:... (required)"
  },

  "gate_chain": {
    "identity_gate_sequence_receipt_hash": "sha256:... (required)",
    "style_gate_receipt_hash":             "sha256:... (optional)",
    "artifact_gate_receipt_hash":          "sha256:... (optional)"
  },

  "identity_sequence_verdict": "PASS | REWORK | REJECT (read from referenced sequence receipt)",

  "candidacy": {
    "admissibility_status": "ELIGIBLE | CANDIDATE_ONLY | BLOCKED",
    "blocking_reasons":     ["string array"]
  },

  "context": {
    "render_backend": "string (e.g. Seedance, HeyGen, internal)",
    "operator":       "string (custodian node)"
  },

  "authority":  false,
  "admissible": false,
  "claim":      "NO_CLAIM",

  "previous_receipts": ["array of sha256 hashes"],
  "cumulative_hash":   "sha256:..."
}
```

---

## §4. Required fields

These fields must be present and non-empty. Missing any one of them is a
hard validation failure:

- `type` (must equal `MEDIA_RECEIPT_V1`)
- `media_receipt_id`
- `project_id`
- `asset_chain.source_refs_hash`
- `asset_chain.render_hash`
- `gate_chain.identity_gate_sequence_receipt_hash`
- `authority` (must be `false`)
- `admissible` (must be `false`)
- `claim` (must equal `NO_CLAIM`)

Other `asset_chain.*` and `gate_chain.*` fields are **strongly
recommended** but the strict-minimum set above is what blocks validity
when missing. (Style and artifact gates are optional in V1 because not
every render produces them; they may be required in V2.)

---

## §5. Admissibility status logic

The validator computes one of three states from the referenced identity
sequence receipt:

| Identity sequence verdict | `admissibility_status` | Meaning                                          |
| ------------------------- | ---------------------- | ------------------------------------------------ |
| `PASS`                    | **ELIGIBLE**           | Eligible for MAYOR to sign for canon            |
| `REWORK`                  | **CANDIDATE_ONLY**     | Receipt is valid; admissibility blocked         |
| `REJECT`                  | **BLOCKED**            | Receipt itself is invalid; cannot proceed       |

The Media Receipt **never** writes `admissibility_status = ELIGIBLE`
implies canon. ELIGIBLE only means "MAYOR may now look at this."
Admission is downstream and reducer-only.

---

## §6. The wrapper / re-implementation boundary

Critical constraint:

> **MEDIA_RECEIPT_V1 wraps the identity gate sequence receipt.
> It does not re-implement identity logic.**

The Media Receipt reads `identity_sequence_verdict` from the referenced
sequence receipt and propagates it. It does **not**:

- recompute `d_cycle`
- re-evaluate trajectory shape
- re-validate frame receipts
- adjust tolerance bands
- override the sequence verdict

If you want to question the identity verdict, you produce a new sequence
receipt. The Media Receipt only carries what the gates already decided.

---

## §7. Storage

Media receipts are written append-only to:

```
ledgers/media_receipt_v1.ndjson
```

This is a third sub-ledger, distinct from:

```
ledgers/identity_gate_v1.ndjson           ← per-frame
ledgers/identity_gate_v1_sequence.ndjson  ← per-sequence
```

Separation keeps each layer's replay clean.

---

## §8. Validator contract

The validator is at:

```
helen_os/governance/media_receipt_validator.py
```

Signature:

```python
def validate_media_receipt(
    receipt: dict,
    *,
    identity_sequence_store: dict[str, dict] | None = None,  # hash -> sequence receipt
    style_gate_store: dict[str, bool] | None = None,         # hash -> exists
    artifact_gate_store: dict[str, bool] | None = None,      # hash -> exists
) -> dict
```

Returns:

```python
{
    "valid": bool,
    "violations": list[str],           # violation codes
    "admissibility_status": str,       # "ELIGIBLE" | "CANDIDATE_ONLY" | "BLOCKED"
    "details": list[str],
}
```

The validator is **pure**: it never writes to any ledger, never mutates
the input receipt, never opens files. Validation is idempotent (same
input → same output, every time).

---

## §9. Test coverage (10 cases)

Bound to `tests/test_media_receipt_v1.py`:

| # | Test                                                         | Asserts                              |
| - | ------------------------------------------------------------ | ------------------------------------ |
| 1 | Valid receipt with PASS identity sequence                    | valid + ELIGIBLE                     |
| 2 | Missing identity_gate_sequence_receipt_hash                  | invalid + `MISSING_IDENTITY_SEQUENCE`|
| 3 | Identity sequence verdict is REJECT                          | invalid + BLOCKED                    |
| 4 | Identity sequence verdict is REWORK                          | valid + CANDIDATE_ONLY               |
| 5 | Missing render_hash                                          | invalid + `MISSING_RENDER_HASH`      |
| 6 | Missing source_refs_hash                                     | invalid + `MISSING_SOURCE_REFS_HASH` |
| 7 | `authority` is `true`                                        | invalid + `AUTHORITY_VIOLATION`      |
| 8 | `admissible` is `true`                                       | invalid + `ADMISSIBILITY_VIOLATION`  |
| 9 | Referenced style gate hash not in store                      | invalid + `REFERENCED_GATE_MISSING`  |
| 10 | Validator does not mutate the input or write any ledger     | idempotency + purity                 |

---

## §10. What the Media Receipt does NOT do

To prevent authority creep:

- It does not sign the ledger (only MAYOR signs).
- It does not declare admission (only the Reducer admits).
- It does not re-run identity gates (only references them).
- It does not store assets (only references them by hash).
- It does not validate render quality (that's the renderer's pre-gate).
- It does not modify any other receipt.

---

## §11. Admission sidecar

When/if REDUCER admits this schema:

```
sha256: <pending>
test_pointer: tests/test_media_receipt_v1.py
validator_pointer: helen_os/governance/media_receipt_validator.py
parent_gate: HELEN_IDENTITY_GATE_V1
parent_theory: CONSTITUTIONAL_MANIFOLD_RENDERING_V0
wraps:
  - IDENTITY_GATE_RECEIPT_V1
  - IDENTITY_GATE_RECEIPT_V1_SEQUENCE
proposer: HER
attestor: REDUCER (pending)
ledger_receipt: <pending>
```

Until then: SCHEMA_DRAFT, NO_SHIP, APPEND_ONLY proposal.

---

## §12. The single line

> **The Media Receipt proves the chain. It does not admit the media.
> Admissibility is still reducer-only.**
