# WUL_CLAIM_SCHEMA_V1

```
AUTHORITY      = false
CANON          = false
STATE_MUTATION = none
STATUS         = spec / proposal
VERSION        = 1.0
SUPERSEDES     = docs/specs/wul_claim_schema_v0.json (field-compatible; renames claim_class → claim_type)
```

---

## 0. The locked frontier

The WUL boundary is **not symbolic — it is epistemic and institutional.**

A symbol that expresses a belief is decoration. A symbol that carries a **typed,
truth-tagged, auditable claim** is admissible material. V1 is the line between the two.

```
Observation   ≠ Hypothèse
Hypothèse     ≠ Admission
Symbole       ≠ Preuve
Narration     ≠ Ledger
```

Central law:

```
🌊❓🧠  ≠  🌊✅🧠      — until the reducer has ruled
```

A claim may *feel* warm, dense, or beautiful. None of that promotes it. Only the reducer
path, against evidence, moves `truth_status` upward.

---

## 1. Pipeline position

```
Narrative → Graph → Typed Claim → Truth Status → Reducer → Admitted JSON → Verification
                    └──────────── WUL_CLAIM_SCHEMA_V1 governs this object ───────────┘
```

A WUL Claim is the **typed object** produced when narrative/symbolic material is compiled
into something the reducer can act on. It is the unit of admission, not the unit of
expression.

---

## 2. Field set (canonical)

| Field | Type | Required | Purpose |
|---|---|---|---|
| `claim_id` | string (non-empty) | ✓ | Stable identifier, unique within a batch |
| `symbolic_form` | string (non-empty) | ✓ | WUL/WULmoji surface form (e.g. `🌊 ⊗ 💾`) |
| `natural_text` | string (non-empty) | ✓ | Plain-language statement of the same claim |
| `claim_type` | enum | ✓ | Epistemic class of the claim (see §3) |
| `truth_status` | enum | ✓ | Current epistemic standing (see §4) |
| `evidence` | array\<string\> | ✓ | Evidence references; `[]` is legal but caps promotion |
| `evidence_hash` | string \| null | ✓ | sha256 of canonicalized evidence; null caps at `SUPPORTED` |
| `admission_state` | enum | ✓ | Position in the reducer pipeline (see §5) |
| `max_admission_state` | enum | ✓ | Reducer-enforced ceiling for this claim |
| `replayable` | boolean | ✓ | Whether an admitted claim is replay-reconstructible |
| `terminal` | boolean | ✓ | True iff `admission_state` ∈ {REJECTED, SUPERSEDED} |
| `rejection_reason` | string \| null | ✓ | Non-null iff `terminal = true` |

> **Naming note:** V0 used `claim_class`. V1 renames it to `claim_type` (operator-canonical).
> A V0 object is upgraded by renaming the key; the enum values are unchanged. Consumers
> that still read `claim_class` should treat it as an alias of `claim_type`.

---

## 3. `claim_type` — closed taxonomy

| Value | Meaning | Typical max truth_status without new evidence |
|---|---|---|
| `OBSERVED` | Directly attested signal (a thing seen, measured, catalogued) | `SUPPORTED` |
| `INFERRED` | Derived from observations by stated reasoning | `REVIEWED` |
| `STRUCTURAL` | Property of the system's own structure (schema, gate, chain) | `REVIEWED` |
| `FORMAL` | Provable within a stated formal system | `REVIEWED` |
| `SPECULATIVE` | Conjecture, hypothesis, garden-fiction candidate | **`PENDING_REVIEW` (hard ceiling)** |

Closed set. An unknown `claim_type` is a schema error, not a forward-compatible warning —
admission must fail closed on unknown epistemic class.

---

## 4. `truth_status` — closed taxonomy (monotone ladder + terminal branches)

```
UNVERIFIED → SUPPORTED → REVIEWED → ADMITTED → SEALED → REPLAYABLE
                                   ╲
                                    ╲→ REJECTED      (terminal)
                                    ╲→ SUPERSEDED    (terminal)
```

| Value | Meaning |
|---|---|
| `UNVERIFIED` | Typed but unbacked; default for any fresh claim |
| `SUPPORTED` | Evidence present and hash-bound, not yet reviewed |
| `REVIEWED` | Passed peer-review (proposer ≠ validator, K2/Rule 3) |
| `ADMITTED` | Reducer admitted; ledger entry exists |
| `SEALED` | Admitted and frozen; no further mutation |
| `REPLAYABLE` | Sealed and reconstructible from replay |
| `REJECTED` | Reducer refused; terminal negative branch |
| `SUPERSEDED` | Replaced by a successor claim; terminal succession branch |

The ladder is **monotone**: no transition may lower `truth_status` except into the two
terminal branches (`REJECTED`, `SUPERSEDED`).

---

## 5. `admission_state` — pipeline position

| Value | Meaning |
|---|---|
| `PENDING_REDUCER` | Compiled, queued, not yet seen by reducer (canonical entry state) |
| `PENDING_REVIEW` | Awaiting peer-review before reducer can admit |
| `REJECTED` | Reducer refused (terminal) |
| `ADMITTED` | Reducer admitted; ledger append occurred |
| `SEALED` | Admitted and frozen (terminal-positive for mutation) |
| `REPLAYABLE` | Sealed and replay-reconstructible |
| `SUPERSEDED` | Replaced (terminal) |

> **V0 mapping:** V0's `PENDING` ≡ V1 `PENDING_REDUCER`. All other values are unchanged.

---

## 6. Passage law (reducer-enforced, NOT schema-enforced)

The JSON schema accepts shapes; it cannot enforce transitions. These rules belong to
`WUL_REDUCER_RULES_V1` and are restated here as invariants:

```
P1  truth_status > SUPPORTED          ⟹ evidence_hash ≠ null
P2  claim_type = SPECULATIVE          ⟹ max_admission_state ≤ PENDING_REVIEW
                                         (may never reach ADMITTED/SEALED/REPLAYABLE)
P3  admission_state ≤ max_admission_state    at every transition
P4  admission_state ∈ {REJECTED, SUPERSEDED} ⟺ terminal = true
P5  terminal = true                   ⟹ rejection_reason ≠ null
P6  REJECTED and SUPERSEDED are terminal       — no outgoing transitions
P7  symbolic_form and natural_text must denote the same claim (HAL-checkable)
```

---

## 7. Canonical minimal form

```json
{
  "claim_id": "CLAIM_001",
  "symbolic_form": "🌊 ⊗ 💾",
  "natural_text": "Tidal/flow process is coupled to persisted memory.",
  "claim_type": "INFERRED",
  "truth_status": "UNVERIFIED",
  "evidence": [],
  "evidence_hash": null,
  "admission_state": "PENDING_REDUCER",
  "max_admission_state": "REVIEWED",
  "replayable": false,
  "terminal": false,
  "rejection_reason": null
}
```

---

## 8. Worked example — the Shigir Idol (OBSERVED)

A claim about a real, catalogued artifact carries evidence and may sit at `SUPPORTED`,
queued for review:

```json
{
  "claim_id": "CLAIM_002",
  "symbolic_form": "🗿 ⊗ 🔺",
  "natural_text": "The Shigir Idol bears carved geometric (triangular) markings.",
  "claim_type": "OBSERVED",
  "truth_status": "SUPPORTED",
  "evidence": ["photo_ref", "museum_catalog_ref"],
  "evidence_hash": "sha256:…",
  "admission_state": "PENDING_REVIEW",
  "max_admission_state": "ADMITTED",
  "replayable": true,
  "terminal": false,
  "rejection_reason": null
}
```

Note: even with evidence, it is `SUPPORTED` + `PENDING_REVIEW` — **not** admitted. The
photo and catalogue support the claim; only the reducer admits it.

---

## 9. The sentence to keep

> **WUL becomes rigorous when symbols stop expressing beliefs and start carrying typed,
> truth-tagged, auditable claims.**

---

## 10. Admission path (when ready)

This is a spec/proposal artifact. To advance from spec to enforced schema:

1. Peer-review (proposer ≠ validator — K2/Rule 3)
2. Reconcile field names with `helen_os/schemas/` canonical registry (MAYOR-routed)
3. Implement `WUL_REDUCER_RULES_V1` as executable reducer logic
4. MAYOR routing via `tools/helen_say.py`; ledger admission if ratified

Until then: `AUTHORITY = false`, `CANON = false`, `STATE_MUTATION = none`,
`PROMOTION = FORBIDDEN_WITHOUT_PEER_REVIEW_AND_REDUCER`.

```
🌊❓🧠 ≠ 🌊✅🧠
📜 → 🔣 → 🧾(typed) → ⚖️(reducer) → ✅(admitted) → 🔁(replay)
🏁
```
