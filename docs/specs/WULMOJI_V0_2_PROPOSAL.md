---
authority: NON_SOVEREIGN
canon: NO_SHIP
status: PROPOSAL
lifecycle: PENDING_MAYOR_RECEIPT
version: "0.2"
supersedes: null
relates_to:
  - formal/wulmoji_spec_v1.txt          # SYSTEM_A: PROCESS layer (canonical)
  - docs/specs/WULMOJI_V1_RECONCILIATION.md  # SYSTEM_A ⊥ SYSTEM_B audit
  - docs/specs/WULMOJI_SCATTER_MAP.md   # Authority invariant + scatter
  - docs/specs/WUL_PACKET_SPEC_V0_1.md  # Inter-agent WUL packets (DISTINCT)
date: 2026-06-15
---

# WULMOJI V0.2 — RENDER LAYER SPEC (PROPOSAL)

**Mission in one line:**
WULmoji must become a receipt protocol, not a mystical language.

---

## Scope Boundary

This spec governs WULmoji as a **visual render layer** — signal, status, risk, receipt.

It does NOT govern:
- WUL inter-agent packets → see `docs/specs/WUL_PACKET_SPEC_V0_1.md`
- WUL process primitives → see `formal/wulmoji_spec_v1.txt` (SYSTEM_A, canonical)
- Deployment status headers → see SYSTEM_B (WULMOJI_V1_RECONCILIATION)

Those three remain authoritative in their own lanes. This spec adds a fourth lane: **bounded render grammar**.

---

## Zone Architecture

```
ZONE        SYMBOL    PURPOSE
─────────────────────────────────────────────────────
GARDEN      🌿        Symbolic play, aesthetic, runes, myths, inspiration
TEMPLE      🎭        Lateral modes, DAN personas, GOBLIN sessions
KERNEL      🛡️        Gates, firewall, receipt verification, enforcement
DOCTRINE    🧾        Audited, receipt-backed, bounded principles only
```

### Zone Routing Rule

```
🌿 → 🎭 → 🛡️ → 🧾

Myth may inspire Garden.
Garden may inform Temple.
Temple outputs route through KERNEL verification.
Only KERNEL-verified artifacts reach DOCTRINE.
No shortcut from 🌿 to 🧾.
```

**The critical invariant:** zone symbols are routing labels, not authority claims. A `🌿` prefix means GARDEN content. It does not grant GARDEN content KERNEL authority.

---

## Lexicon (Minimal)

```
SYMBOL   ROLE         MEANING
────────────────────────────────────────────────────
📜       PROPOSAL     Artifact under consideration
🕯️       RECEIPT      Proof of action (hash-chained)
🧾       PROOF        Verified evidence
👁️       VERIFY       Verification action
✅       ADMITTED     Passed gate, admitted
❌       REJECTED     Not admitted
⏳       PENDING      Awaiting proof or gate
⚠️       RISK         Flagged for review
🚫       BLOCKED      Hard block — gate or firewall
🛡️       PROTECTED    Under firewall / guarded
🔒       LOCKED       Sealed, immutable
🏁       END          Terminal state marker (mandatory)
🌿       GARDEN       Symbolic / non-sovereign zone
🧺       COMPOST      Discarded material, no extract value
🎭       TEMPLE       Lateral / exploratory session mode
```

No other symbols are canonical. Additions require a MAYOR receipt.

---

## Math Connectors (Logic/Proof Layer)

A minimal logic vocabulary for expressing proofs, conditions, and set membership inside WULmoji grammar. These symbols are operators, not emojis — they compose with WULmoji tokens to build verifiable assertions.

```
SYMBOL   ROLE              MEANING
────────────────────────────────────────────────────
=        EQUIV             équivaut à / définition
≠        NEQ               différent — interdit de confondre
⇒        IMPLIES           implique (one-directional)
⇔        IFF               équivalence (bidirectional)
∧        AND               et
∨        OR                ou
¬        NOT               non
∀        FORALL            pour tout
∃        EXISTS            il existe
∴        THEREFORE         donc (conclusion)
∵        BECAUSE           parce que (premise)
⊂        SUBSET            inclus dans
∈        MEMBER            appartient à
∉        NOT_MEMBER        n'appartient pas
≈        APPROX            approximativement
≤        ATMOST            au plus / borne haute
≥        ATLEAST           au moins / seuil
Δ        DELTA             changement / variation
Σ        SIGMA             somme / système total
⊥        CONTRADICTION     contradiction — claim fails
```

### Math Grammar (with WULmoji)

Canonical sentence with math layer:

```
[ZONE] [OBJECT] ⇒ [PROOF] ⇒ [STATUS] 🏁
```

### Math Examples

```
🛡️ 📜 ∧ 🧾 ⇒ ✅ 🏁
= KERNEL: proposal AND proof present → admitted.

📜 ∧ ¬🧾 ⇒ ⏳ 🏁
= proposal WITHOUT proof → pending.

🌿 ∈ GARDEN ∧ 🌿 ∉ KERNEL 🏁
= mythic content belongs to Garden, not Kernel.

🧾 = 0 ⇒ ✅ = 0 🏁
= proof absent → acceptance impossible. (GOLDEN RULE, math form)

⚠️ ≥ τ ⇒ 🚫 🏁
= if risk exceeds threshold τ → blocked.

🧾❌ ⇒ ¬✅ ∧ ⏳ 🏁
= no proof → not admitted AND pending.
```

### Zone Membership (Math Form)

```
🌿 ∈ GARDEN
🎭 ∈ TEMPLE
🛡️ ∈ KERNEL
🧾 ∈ DOCTRINE

🌿 ∉ DOCTRINE  ∵  ¬🧾✅
∴ 🌿 → GARDEN only, until 🧾✅ gates it through 🛡️
```

### Math Central Rule

```
🧾 = 0 ⇒ ✅ = 0

Σ(proof) = 0 ⇒ Σ(admission) = 0

NO PROOF = NO CLAIM = NO ADMISSION
```

### Contradiction Detection

```
⊥ signals a logic failure in the sentence.

Example:
🌿 ∈ DOCTRINE ∧ ¬🧾✅ ⊥ 🏁
= mythic content claimed as Doctrine without proof → CONTRADICTION
```

---

## Grammar (Full)

Canonical sentence (emoji-only form):

```
[ZONE] [OBJECT] ➡️ [ACTION] ➡️ [PROOF] ➡️ [STATUS] 🏁
```

Canonical sentence (with math layer):

```
[ZONE] [OBJECT] ∧ [CONDITION] ⇒ [STATUS] 🏁
```

Every WULmoji sentence ends in `🏁`. Open sentences are malformed.

### Worked examples

```
🛡️ 📜 ➡️ 👁️ ➡️ 🧾 ➡️ ✅ 🏁
= KERNEL: proposal verified, proof present, admitted.

🌿 📜 ➡️ 🎭 ➡️ 🕯️ ➡️ ✅ 🏁
= GARDEN: symbolic content accepted into Garden layer.

🛡️ 📜 ➡️ ⚠️ ➡️ 🚫 🏁
= KERNEL: proposal flagged, blocked. No proof required to block.

🧾❌ ➡️ ⏳ 🏁
= No proof present → pending. Never admitted without proof.

🌿 🧺 ➡️ 🧺 🏁
= GARDEN: material composted. No extraction.
```

---

## Receipt Encoding

WULmoji may signal receipt status. It cannot issue receipts.

```
🕯️✅   Receipt present, admitted
🕯️❌   No receipt → no claim (NO RECEIPT = NO CLAIM)
🕯️⏳   Receipt pending
🕯️⚠️   Receipt disputed — gate review required
```

### Golden Rule

```
🧾❌ ➡️ ⏳ 🏁

NO PROOF = PENDING. NEVER ADMITTED.
```

---

## GOBLIN Filter (Render Classification)

Before WULmoji is assigned to incoming symbolic material:

```
🟢 KEEP            Safe as-is. No boundary required.
🟡 SAFE_AFTER      Safe after extraction of drift phrases.
🟠 BOUNDARY        Needs explicit authority:false + ledger_effect:NONE header.
🧺 COMPOST         Discard. No extraction value.
🚫 BLOCK           Hard block. Do not pass to any layer.
```

Classification is mandatory for GARDEN and TEMPLE material before routing forward.

---

## Forbidden Patterns

WULmoji **cannot**:

```
× Create authority
    🌿 content cannot become 🧾 without passing 🛡️ gate

× Admit truth
    🎭 output is not truth; only 🛡️-verified artifacts carry truth status

× Mutate ledger
    WULmoji is render layer only; no WULmoji sequence writes to ledger

× Override reducer decisions
    🚫 cannot be reversed by 🌿 or 🎭 sequences

× Claim sentience
    No emoji combination constitutes a consciousness claim

× Shortcut zones
    🌿 ≠ 🧾 — they are separated by 🛡️
    Any sequence skipping 🛡️ is malformed
```

---

## Authority Invariant (Restated)

```
WULmoji is a render layer.

It may signal: state · mood · risk · receipt status.

It cannot: create authority · admit truth · mutate ledger ·
           override reducer decisions · establish sovereignty.
```

Source: `docs/specs/WULMOJI_SCATTER_MAP.md §WULmoji Authority Invariant`
This spec operationalizes that invariant as grammar.

---

## Relation to Existing Systems

| System | Lane | This spec affects? |
|---|---|---|
| `formal/wulmoji_spec_v1.txt` (SYSTEM_A) | PROCESS primitives | No — orthogonal |
| Deployment status header (SYSTEM_B) | Status format | No — orthogonal |
| `WUL_PACKET_SPEC_V0_1.md` | Inter-agent packets | No — distinct protocol |
| **This spec (V0.2)** | **Visual render grammar** | Yes — adds bounded grammar |

Merge with SYSTEM_A or SYSTEM_B is explicitly REJECTED without a separate MAYOR receipt.

---

## Promotion Path

This document is PROPOSAL / NON_SOVEREIGN / NO_SHIP.

To promote to canon:
1. Operator review
2. HAL gate pass
3. MAYOR receipt via `tools/helen_say.py --op promote_skill`
4. Reducer admission
5. Ledger write (seq-anchored)

Until promotion: treat as GARDEN-tier reference.

---

```
AUTHORITY: NON_SOVEREIGN
SOVEREIGN: false
CANON: NO_SHIP
STATUS: PROPOSAL
GOBLIN_FILTER_PASSED: true
LAYER: TEMPLE / KERNEL_ADJACENT (grammar only, no enforcement)
LEDGER_EFFECT: NONE
```
