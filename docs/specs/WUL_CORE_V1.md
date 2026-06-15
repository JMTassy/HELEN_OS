---
authority: OPERATOR_BOUND
canon: NO_SHIP
lifecycle: SPEC
version: 1.0
parent_compiler: docs/specs/WUL_COMPILER_V0_SPEC.md
---

# WUL_CORE_V1

Canonical token authority for WUL (WULmoji).
This file is the single source of truth for what symbols exist in the WUL kernel and which domain they belong to.

The compiler spec (`WUL_COMPILER_V0_SPEC.md`) defines pipeline and type rules.
This spec defines the token registry.

---

## Token Registry

```
DOMAIN=A  ONTOLOGY     💡 🧬 🌊 🔄 🔀 ∞
DOMAIN=B  MATHEMATICS  ∫ ∇ Σ Π ∩ ∪ → ≡
DOMAIN=C  GOVERNANCE   📜 🧾 🔐 ⚖️ 🧱 ✅ ❌ ⏳ ⚠️ ⚰️ 🔁
DOMAIN=D  SPECULATION  🔮 🌌 🧠∞ ψ
```

---

## Domain Rules

### DOMAIN=A — Ontology

Grounded. Safe for computation and modeling. May appear in canonical chains as inputs.

| Token | Name | Type |
|---|---|---|
| 💡 | Information | INFORMATION |
| 🧬 | Structure | STRUCTURE |
| 🌊 | Flow | FLOW |
| 🔄 | Recursion | RECURSION |
| 🔀 | Transformation | TRANSFORMATION |
| ∞ | Unbounded | UNBOUNDED |

### DOMAIN=B — Mathematics

Operators only. Each has exactly one semantic. Never decorative.

| Token | Name | Semantic |
|---|---|---|
| → | Produces | A produces B — no other meaning |
| ∩ | Intersects | Common elements |
| ∪ | Unions | Combined set |
| ≡ | Equivalent | Definitional identity |
| ∫ | Aggregate | Collect over domain |
| ∇ | Optimize | Gradient / minimize obstruction |
| Σ | Sum | Total over elements |
| Π | Compose | Sequential composition |

### DOMAIN=C — Governance

Epistemic weight. These are the admission chain. Truth status lives here.

| Token | Name | Type |
|---|---|---|
| 📜 | Claim | CLAIM |
| 🧾 | Evidence | EVIDENCE |
| 🔐 | Receipt | RECEIPT |
| ⚖️ | Review | REVIEW |
| 🧱 | Gate | GATE |
| ✅ | Admitted | ADMISSION |
| ❌ | Rejected | REJECTION |
| ⏳ | Pending | PENDING |
| ⚠️ | Risk | RISK |
| ⚰️ | Sealed | SEAL |
| 🔁 | Replayable | REPLAY |

### DOMAIN=D — Speculation

Recognized and typed. The compiler knows these tokens and assigns them type `SPECULATIVE`.
They survive the lexer. They are rejected by admission, not by lexing.
Untagged Domain D use (missing `Ⓢ`) is a modal/type error at the modal validation stage.

| Token | Name | Type |
|---|---|---|
| 🔮 | Hypothesis | SPECULATIVE |
| 🌌 | Cosmology | SPECULATIVE |
| 🧠∞ | Consciousness Theory | SPECULATIVE |
| ψ | Quantum Analogy | SPECULATIVE |

**Domain D rules (compiler-enforced):**

1. Every Domain D symbol is assigned type `SPECULATIVE`
2. All `SPECULATIVE` tokens require modal tag `Ⓢ` — untagged speculative tokens are a type error
3. `SPECULATIVE → ADMISSION` is a type error — always
4. `SPECULATIVE → SEAL` is a type error — always
5. `SPECULATIVE → REPLAY` is a type error — always
6. `SPECULATIVE` may produce `CLAIM` — but that claim remains `⏳ PENDING`

**The only valid speculative chain:**

```
Ⓢ 🔮 → 📜 → ⏳
```

Domain D can inspire claims. It cannot produce admitted state.

---

### MODAL STATUS

Modal tags are lexer-known tokens. They prefix a sentence and bind to the entire expression.
They are mandatory for sentences that make truth claims.

| Token | Name | Type |
|---|---|---|
| Ⓢ | Speculative | SPECULATIVE_STATUS |
| Ⓞ | Observed | OBSERVED_STATUS |
| Ⓟ | Proven | PROVEN_STATUS |
| Ⓐ | Admitted | ADMITTED_STATUS |

**Modal rules (compiler-enforced):**

1. A sentence with Domain D tokens and no `Ⓢ` tag is a type error
2. `Ⓢ` sentences cannot produce ADMISSION, SEAL, or REPLAY
3. `Ⓐ` sentences require the full governance chain: `📜 → 🧾 → ⚖️ → 🧱 → ✅`
4. A sentence with no modal tag is structurally valid but epistemically inert — it describes, does not claim

---

## The Law

```
A symbol without truth status is poetry.
A symbol with truth status can enter governance.
```

Truth status is carried by DOMAIN=C tokens and the modal tags `Ⓢ Ⓞ Ⓟ Ⓐ`.
A WUL sentence containing only DOMAIN=A or DOMAIN=B symbols is structurally valid but epistemically inert.
It describes. It does not claim. It does not admit.

---

## Admission Chain (Reference)

```
📜 → 🧾 → 🔐 → ⚖️ → 🧱 → ✅ → ⚰️ → 🔁
```

Every admitted fact traces to this chain.

## Prime Knowledge Chain (Reference)

```
💡 → 🧬 → 📜 → 🧾 → 🔐 → ⚖️ → 🧱 → ✅ → ⚰️ → 🔁
```

## Hard Firewall

```
Ⓢ ↛ ✅
Ⓢ ↛ ⚰️
Ⓢ ↛ 🔁
```

Speculation cannot become admitted state directly.
The path from `Ⓢ` to `✅` requires the full chain — and a human operator at the admission gate.

---

## Delta from WUL_COMPILER_V0_SPEC.md

Two additions relative to the compiler spec token table:

1. `∞ (UNBOUNDED)` added to DOMAIN=A — was missing from compiler spec; it is now lexer-known
2. `DOMAIN=D` (🔮 🌌 🧠∞ ψ) added as recognized-and-typed layer — tokens are lexer-known and typed SPECULATIVE; they fail admission, not lexing; unrecognized decorative tokens (🌱 🌈 ρ Δx etc.) still fail the lexer
3. `⏳ (PENDING)` added to DOMAIN=C — required for valid speculative chain `Ⓢ 🔮 → 📜 → ⏳`
4. `MODAL STATUS` section added — `Ⓢ Ⓞ Ⓟ Ⓐ` are now lexer-registered tokens with typed semantics

The compiler spec §3 token table should be updated to reflect this registry on next revision.

---

## Status

OPERATOR_BOUND / NO_SHIP
Pending: operator countersignature → commit decision
