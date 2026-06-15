# WUL_COMPILER_V0_SPEC

**Classification:** NON_SOVEREIGN / NO_SHIP / SPEC
**Status:** DRAFT
**Version:** 0.1

---

## 1. Purpose

WUL (Wordless Universal Language) is a computable symbolic governance language, not a poetic lexicon.

This spec defines the grammar, type system, operator semantics, modal truth-status rules, admission model, execution pipeline, and ledger event format for WUL v0.1.

A WUL sentence must either:
- fail parsing,
- fail type-checking,
- remain pending, or
- compile into a deterministic ledger event.

No other outcome is valid. There is no decoration mode in the compiler.

---

## 2. Minimal Grammar

```
sentence     := optional_modal expr
optional_modal := modal | ε
expr         := atom | expr operator expr
atom         := emoji_atom | math_symbol | typed_entity
operator     := → | ∩ | ∪ | ≡ | ×
modal        := Ⓢ | Ⓞ | Ⓟ | Ⓐ
typed_entity := atom LABEL
               (e.g., 📜RH001, 🧾EXPERIMENT)
```

`→` is left-associative. `expr operator expr` is parsed as a left-to-right chain.

A sentence with no modal is treated as untagged. Untagged sentences may parse and type-check but cannot produce an ADMITTED ledger event without an explicit `Ⓐ` tag.

---

## 3. Token Table

### Ontology (L1)
| Token | Type | Meaning |
|---|---|---|
| 💡 | INFORMATION | Information / data / idea |
| 🧬 | STRUCTURE | Pattern / schema / structure |
| 🌊 | FLOW | Flux / dynamic / stream |
| 🔄 | RECURSION | Loop / iteration / feedback |
| 🔀 | TRANSFORMATION | Mutation / evolution / change |

### Governance (L0)
| Token | Type | Meaning |
|---|---|---|
| 📜 | CLAIM | A proposition requiring admission |
| 🧾 | EVIDENCE | Artifact supporting a claim |
| 🔐 | RECEIPT | Cryptographic/hash-bound record |
| ⚖️ | REVIEW | Evaluation / gate pass |
| 🧱 | GATE | Admission boundary |
| ✅ | ADMISSION | Successful gate passage |
| ❌ | REJECTION | Gate failure |
| ⚰️ | SEAL | Immutable closure |
| 🔁 | REPLAY | Verifiable replay state |
| ⏳ | PENDING | Awaiting resolution |
| ⚠️ | RISK | Flagged hazard |
| 🚫 | PREVENTED | Blocked — no further progress |

### Mathematical Operators (L2)
| Token | Role | Meaning |
|---|---|---|
| → | binary operator | PRODUCES |
| ∩ | binary operator | INTERSECTS |
| ∪ | binary operator | UNIONS |
| ≡ | binary operator | EQUIVALENT |
| × | binary operator | COMPOSES |
| ∫ | unary aggregator | AGGREGATE |
| ∇ | unary | OPTIMIZE |
| Σ | unary aggregator | SUM |
| Π | unary aggregator | COMPOSE-PRODUCT |
| ∀ | quantifier | FOR ALL |
| ∃ | quantifier | EXISTS |

### Modal Status Tags (L0)
| Token | Type | Meaning |
|---|---|---|
| Ⓢ | SPECULATIVE | Hypothesis — cannot write ledger |
| Ⓞ | OBSERVED | Empirically grounded — may produce claim |
| Ⓟ | PROVEN | Formally verified — requires evidence chain |
| Ⓐ | ADMITTED | Passed full admission chain |

---

## 4. Type System

Each atom has exactly one type. Types are non-overlapping.

```
💡  → INFORMATION
🧬  → STRUCTURE
🌊  → FLOW
🔄  → RECURSION
🔀  → TRANSFORMATION
📜  → CLAIM
🧾  → EVIDENCE
🔐  → RECEIPT
⚖️  → REVIEW
🧱  → GATE
✅  → ADMISSION
❌  → REJECTION
⚰️  → SEAL
🔁  → REPLAY
⏳  → PENDING
⚠️  → RISK
🚫  → PREVENTED
Ⓢ  → SPECULATIVE
Ⓞ  → OBSERVED
Ⓟ  → PROVEN
Ⓐ  → ADMITTED
```

Any symbol not in this table is a parse error. The kernel does not accept unknown tokens.

---

## 5. Operator Semantics

### `→` PRODUCES

The canonical execution operator. It has exactly one meaning:

> **A → B** means: A produces B.

Forbidden interpretations of `→`:
- causes
- implies
- suggests
- points to
- is followed by
- leads to

`→` describes a production relationship only. If a different relationship is intended, a different operator must be used. If no operator exists for that relationship, the sentence is not expressible in WUL v0.1.

### `∩` INTERSECTS
The set of elements common to both operands.

### `∪` UNIONS
The combined set of both operands.

### `≡` EQUIVALENT
Definitional or functional equivalence. Both sides must share a type-compatible domain.

### `×` COMPOSES
Sequential composition. `A × B` means A then B as a composed unit.

---

## 6. Type Rules

### Valid production chains
```
INFORMATION  → STRUCTURE
INFORMATION  → CLAIM
STRUCTURE    → CLAIM
CLAIM        → EVIDENCE
EVIDENCE     → RECEIPT
EVIDENCE     → REVIEW
RECEIPT      → REVIEW
REVIEW       → GATE
GATE         → ADMISSION
GATE         → REJECTION
ADMISSION    → SEAL
SEAL         → REPLAY
CLAIM        → PENDING          (when evidence absent)
CLAIM        → RISK             (when flagged)
RISK         → PREVENTED
```

### Invalid (type errors)
```
CLAIM        → ADMISSION        # skips evidence/review/gate
SPECULATIVE  → ADMISSION        # modal violation
EVIDENCE     → <undefined>      # unknown token
SEAL         → CLAIM            # reverse chain forbidden
```

### Double-operator error
```
🧬 → → 💡    # parse error: consecutive operators
```

### Unknown symbol error
```
🧾 → 🌈      # type error: 🌈 not in kernel token table
```

---

## 7. Modal Truth-Status Rules

Modal tags prefix a sentence and bind to the entire expression.

| Modal | Rule |
|---|---|
| Ⓢ SPECULATIVE | Cannot produce ADMISSION or SEAL. Output is always PENDING. Cannot write ledger. |
| Ⓞ OBSERVED | May produce CLAIM. Cannot skip evidence chain. |
| Ⓟ PROVEN | Requires full evidence chain. May produce ADMISSION if chain is complete. |
| Ⓐ ADMITTED | Requires complete chain: `📜 → 🧾 → ⚖️ → 🧱 → ✅`. May produce SEAL and REPLAY. |

**Modal override rule:** A lower-privilege modal cannot override a higher-privilege requirement. `Ⓢ` can never produce `✅`. `Ⓞ` cannot skip `🧾`.

**Untagged sentences:** May parse and type-check. Cannot produce ADMITTED events. Compiler emits `status: "untagged"` in output.

---

## 8. Admission Model

A WUL sentence compiles to `status: "accepted"` only if it satisfies all of:

1. Modal tag is `Ⓐ`
2. Chain contains, in order: `CLAIM → EVIDENCE → REVIEW → GATE → ADMISSION`
3. All type rules pass
4. No unknown tokens

Optional downstream stages (do not affect admission):
- `ADMISSION → SEAL`
- `SEAL → REPLAY`

If any required stage is missing, the compiler emits `status: "incomplete_chain"` with the first missing stage identified.

---

## 9. Execution Model

```
WUL sentence
    ↓
Lexer
    — tokenizes emoji, symbols, labels, modals
    — rejects unknown tokens immediately
    ↓
Parser
    — builds AST from grammar
    — rejects double-operator, empty expr, malformed modal
    ↓
AST
    ↓
Type Checker
    — validates each production rule
    — rejects type violations
    ↓
Modal Validator
    — checks modal tag against output type
    — Ⓢ → cannot produce ADMISSION
    ↓
Admission Validator
    — checks full chain presence for Ⓐ sentences
    — emits missing_stage if incomplete
    ↓
Ledger Event JSON
```

The compiler is **fail-closed**: any stage failure returns an error event, never a partial success.

---

## 10. Ledger Event Examples

### Pending speculative claim
**Input:** `Ⓢ 🧠∞ → 📜 → ⏳`

**Output:**
```json
{
  "event": "wul_compile",
  "modal": "SPECULATIVE",
  "chain": ["CONSCIOUSNESS_THEORY", "CLAIM", "PENDING"],
  "status": "pending",
  "reason": "speculative_modal_cannot_admit"
}
```

### Rejected malformed sentence
**Input:** `🧬 → → 💡`

**Output:**
```json
{
  "event": "wul_compile",
  "modal": null,
  "chain": null,
  "status": "parse_error",
  "reason": "consecutive_operators_at_position_2"
}
```

### Admitted governance sentence
**Input:** `Ⓐ 📜RH001 → 🧾EXPERIMENT → ⚖️ → 🧱 → ✅`

**Output:**
```json
{
  "event": "wul_compile",
  "modal": "ADMITTED",
  "claim": "RH001",
  "evidence": "EXPERIMENT",
  "chain": ["CLAIM", "EVIDENCE", "REVIEW", "GATE", "ADMISSION"],
  "status": "accepted"
}
```

### Sealed replayable event
**Input:** `Ⓐ 📜RH001 → 🧾EXPERIMENT → ⚖️ → 🧱 → ✅ → ⚰️ → 🔁`

**Output:**
```json
{
  "event": "wul_compile",
  "modal": "ADMITTED",
  "claim": "RH001",
  "evidence": "EXPERIMENT",
  "chain": ["CLAIM", "EVIDENCE", "REVIEW", "GATE", "ADMISSION", "SEAL", "REPLAY"],
  "status": "sealed",
  "replayable": true
}
```

### Type error
**Input:** `📜 → ✅`

**Output:**
```json
{
  "event": "wul_compile",
  "modal": null,
  "chain": ["CLAIM", "ADMISSION"],
  "status": "type_error",
  "reason": "CLAIM cannot produce ADMISSION directly; missing EVIDENCE, REVIEW, GATE"
}
```

---

## 11. Test Vectors

### Valid sentences

| # | WUL | Expected status |
|---|---|---|
| V01 | `💡 → 🧬` | `type_valid` |
| V02 | `📜 → 🧾 → ⚖️ → 🧱 → ✅` | `incomplete_chain` (no Ⓐ modal) |
| V03 | `Ⓐ 📜RH001 → 🧾EXPERIMENT → ⚖️ → 🧱 → ✅` | `accepted` |
| V04 | `Ⓐ 📜RH001 → 🧾EXPERIMENT → ⚖️ → 🧱 → ✅ → ⚰️ → 🔁` | `sealed` |
| V05 | `Ⓢ 🔮 → 📜 → ⏳` | `pending` |
| V06 | `Ⓞ 💡 → 📜 → 🧾 → ⏳` | `pending` (evidence present but unreviewed) |
| V07 | `📜 → ⚠️ → 🚫` | `prevented` |
| V08 | `💡 → 🧬 → 📜 → 🧾 → ⚖️ → 🧱 → ❌` | `rejected` |
| V09 | `∀ 📜 : 📜 → 🧾 ∪ ⏳` | `type_valid` (quantified rule) |
| V10 | `Ⓟ 🧾BENCHMARK → ⚖️ → 🧱 → ✅` | `accepted` (proven evidence chain) |

### Invalid sentences

| # | WUL | Expected error |
|---|---|---|
| I01 | `🧬 → → 💡` | `parse_error: consecutive_operators` |
| I02 | `🧾 → 🌈` | `type_error: unknown_token 🌈` |
| I03 | `Ⓢ 🧠∞ → ✅` | `modal_error: SPECULATIVE cannot produce ADMISSION` |
| I04 | `📜 → ✅` | `type_error: CLAIM cannot produce ADMISSION directly` |
| I05 | `Ⓐ 📜 → ✅` | `incomplete_chain: missing EVIDENCE, REVIEW, GATE` |
| I06 | `⚰️ → 📜` | `type_error: SEAL cannot produce CLAIM (reverse chain)` |
| I07 | `→ 🧬` | `parse_error: operator without left operand` |
| I08 | `Ⓐ Ⓢ 📜 → 🧾 → ⚖️ → 🧱 → ✅` | `parse_error: multiple modal tags` |
| I09 | `🧾 → 🧱` | `type_error: EVIDENCE cannot produce GATE directly; missing REVIEW` |
| I10 | (empty) | `parse_error: empty sentence` |

---

## 12. Non-Goals

This spec explicitly excludes:

- New symbols beyond the token table in §3
- Mythology, cosmology, or metaphysical claims
- Consciousness theory in the kernel
- Free-text execution
- Ledger mutation by the compiler itself
- Agent authority claims
- Ambiguous or polysemous operator definitions
- Automatic promotion of speculative sentences

The compiler is a **validator and event emitter**, not a decision-maker. The admission decision belongs to HELEN's reducer. The compiler determines only whether a WUL sentence is syntactically and type-theoretically valid, and whether its chain is complete.

---

## Canonical Chains (Reference)

**Governance chain:**
`📜 → 🧾 → 🔐 → ⚖️ → 🧱 → ✅ → ⚰️ → 🔁`

**Prime chain (full knowledge-to-ledger):**
`💡 → 🧬 → 📜 → 🧾 → 🔐 → ⚖️ → 🧱 → ✅ → ⚰️ → 🔁`

**The rule:**
> Every WUL line must carry a truth-status marker. Without one, it is decorative. Decoration does not compile.
