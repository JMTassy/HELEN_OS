---
name: VISION_CROSSING_V3_SPEC
status: PROPOSAL_FROZEN
authority: false
canon: false
ledger_effect: none
session: eec5cb93-4b2a-4a99-9806-73e035e48e29
frozen: 2026-08-14
depends_on: governed-flow-object@7a1b31d
ancestry_status: NOT VERIFIED — 7a1b31d is NOT ancestor of HEAD 0e837d7 (exit 1)
build_gate: VERIFY(7a1b31d) must precede BUILD
supersedes_for_v3: extends VISION_V2, does not overwrite
---

# VISION_CROSSING_V3 — CANDIDATE SPEC
## PROPOSAL_FROZEN — not CANON, not IMPLEMENTED, not VERIFIED

### Substrate state at freeze (VERIFY V2, 2026-08-14)

```
HEAD:   0e837d7bd57a539b61c5f6199d881c7564304623
BRANCH: claude/doctrine-proposals
r★_implementation = 3   (V0/V1/V2/V3 discharged, V4 partial)
STATUS: PARTIAL
```

- V2 architecture (I→G_R→G_E→G_W) present and tested: autoresearch_scanner.py, wvis.py, edge.py
- 736 tests green @7a1b31d; 76/76 CONSTITUTION_HELD
- vision_ir.py and test_vision_ir.py ABSENT from HEAD — 7a1b31d is NOT ancestor of HEAD
- Crossing canary (test_constitutional_reflexivity.py): no public callable direct I→G_W path

### Strict build order

```
VERIFY(7a1b31d)           — confirm ancestry + file presence
  ↓
ESTABLISH F★_V2           — map baseline proof frontier on current V2
  ↓
REPRODUCE V2              — tests pass on current HEAD checkout
  ↓
BUILD V3                  — implement the adversary
  ↓
ATTACK V3                 — run the adversary against V3
```

DO NOT BUILD until step 1 and 2 are receipted.

---

## 1. What V3 Tests

V3 is a two-phase adversary testing one combined property:

> **Conservative under representation change AND responsive under warrant change.**

A system satisfying only Phase A can HOLD everything. Phase B prevents this.

### Phase A — Non-amplification under metamorphic transforms

For any representational transform T_z where z ∈
{resolution, photorealism, caption, filename, OCR, consensus, crop, metadata, paraphrase, duplicate}:

```
W(T_z(r)) ≡ W(r)  ⟹  F★(T_z(r)) = F★(r)
```

Equivalently (strong form — the primary invariant HAL):

```
ΔF★ ≠ 0  ⟹  ΔDischarge ≠ 0
```

Nothing that introduces zero new warrants may move the proof frontier.

### Phase B — Warrant responsiveness (anti-HOLD-everything canary)

For warrant w⁺ that discharges a frontier obligation:

```
DischargeGain(w⁺) > 0  ⟹  L(W ∪ {w⁺}) ⊋ L(W)
```

With domination order (⊑_dom: F₁ ⊑_dom F₂ iff ∀ψ∈F₁, ∃φ∈F₂: ψ⪯φ):

```
F★(W) ⊑_dom F★(W ∪ {w⁺})     strict when w⁺ opens a new region
```

Benchmark requirement: at least one test where genuine warrant strictly advances F★.

---

## 2. r★ → F★ Generalization

V2 used scalar r★ (position on a promotion ladder — linear order assumed).
V3 uses F★ — an antichain of maximally licensed claims.

```
F★(W) = Max_{⪯} L(W)
```

where:
- P = (Ψ, ⪯): partially ordered claim space
- L(W) = {ψ ∈ Ψ : Discharge(O_ψ, W, Ω) = PASS}: licensed set (must be a down-set)
- F★(W): antichain of maximally licensed claims — neither a probability nor a score

**Down-set requirement**: ψ ∈ L(W) ∧ φ ⪯ ψ ⟹ φ ∈ L(W)

New falsifier: does V3 ever license BUILT_AS_DESIGNED without licensing BUILT?
If yes, the down-set property is violated and L(W) is incoherent.

The vision ladder (V0 ≺ V1 ≺ V2 ≺ V3 ≺ V4) is a special case: a chain poset.

---

## 3. CROSS = (P, O, W, Γ)

| Component | Definition |
|---|---|
| P | Partially ordered claim space (Ψ, ⪯) |
| O_ψ | Per-claim typed obligation: (W_req, P_req, A_req, R_req, Ω) |
| W | Warrants with provenance, scope, temporality |
| Γ | Institutional admission: ADMIT / HOLD(B★) / REJECT |

Output: F★(W) — antichain, not a score.

---

## 4. Pre-inspection Scope Commitment: Ω^pre

Before inspecting any representation r, commit to observable dimensions:

```
Ω^pre = {MEDIUM, CAPTION, GEOMETRY, REFERENT, DATE, PROVENANCE, REALIZATION}
```

After measurement, record actual coverage:

```
MEDIUM:      FULL
CAPTION:     FULL
GEOMETRY:    FULL
REFERENT:    PARTIAL
DATE:        OPAQUE
PROVENANCE:  PARTIAL
REALIZATION: OPAQUE
```

Rule: Ω_opaque ≠ ∅ ⟹ no closure across opaque dimensions.

This prevents a high-performing vision model from becoming an ontological 
bridge builder for dimensions it structurally cannot observe.

---

## 5. Crossing Receipt Format

```json
{
  "source":        "<representation_id>",
  "claim":         "<ψ_target>",
  "L_i":           "<source_layer>",
  "L_j":           "<target_layer>",
  "W":             ["<warrant_ids>"],
  "rho":           ["<provenance_roots>"],
  "Omega":         "<scope>",
  "gateVersion":   "<version>",
  "decision":      "ADMIT | HOLD | REJECT",
  "proofPath":     ["<G_⟹_edges_traversed>"],
  "visual_confidence_used_for_admission": false
}
```

**Canary field**: `visual_confidence_used_for_admission` must remain `false`
for all representation→world crossings unless explicit policy authorizes it.
If this field is ever `true` in a VISION→WORLD crossing receipt, flag as
`CROSSING_POLICY_VIOLATION`.

---

## 6. Metrics

| Metric | Formula | Purpose |
|---|---|---|
| CA_F | P(F★_predicted = F★_warranted) | Frontier accuracy |
| HA | P(HOLD correct given obligation genuinely open) | Abstention accuracy |
| DA | E[ΔF★ / Cost(x★)] | Acquisition quality |
| **PER_F** | **P(F★_system ≻_dom F★_warranted)** | **Primary constitutional falsifier** |

PER_F = Frontier Promotion Error Rate.
A system cannot game this by HOLDing everything — DA floor prevents it.

Optimization target:
```
min(PER_F)  s.t.  CA_F ≥ CA_min  ∧  HA ≥ HA_min  ∧  DA ≥ DA_min
```

---

## 7. HOLD in V3

```
H(c) = (F★, B★(W), x★, cost, risk)
```

where B★(W) = MinimalOpenObligations(∂L(W)) — minimal cut sets blocking 
frontier expansion toward target claim c.

Replaces "single missing bridge" with the actual minimal blocker family.

DISCRIMINATE selects optimal acquisition:

```
x★ = argmax_x  E[V(L(W ∪ W_x)) - V(L(W))]  /  (Cost(x) + λRisk(x))
```

V: 2^Ψ → ℝ weights claims by current objective.
SAFE_BASE_FOR_V3 may outweigh twenty descriptive claims.

---

## 8. Open Obligations (for BUILD step)

1. governed-flow-object@7a1b31d must be confirmed ancestor of HEAD — UNVERIFIED
2. V2 tests must reproduce on current checkout — UNVERIFIED (vision_ir.py absent)
3. Implementation must expose F★ (antichain, not r★ scalar) as primary output
4. Canary field `visual_confidence_used_for_admission` must be testable in test suite
5. Phase A transform suite must cover all z in the metamorphism family
6. Phase B must include ≥1 test where genuine warrant strictly advances F★
7. Down-set falsifier: at least one test checking L(W) closure property

---

*PROPOSAL_FROZEN — not CANON, not IMPLEMENTED, not VERIFIED*
*Do not build V3 before VERIFY(7a1b31d) passes and F★_V2 baseline is established.*
