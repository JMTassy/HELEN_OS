# WARREN_SOVEREIGNTY_CONSTITUTION_V0

```yaml
schema: WARREN_SOVEREIGNTY_CONSTITUTION_V0
status: 🟣 CLAIM — proposed as doctrine, not admitted
authority: false
claim_status: NO_CLAIM
final: HOLD_FOR_OPERATOR
git_stage: no
source: operator meditation 2026-07-17 (Warren ≠ generic swarm)
binding: each law audited against the doctrine triad —
         LOCATED ∧ ENFORCED ∧ REPLAYED. Unlocated laws are
         listed as prose, not gates. No location → no doctrine.
```

---

## 0. Definition

The Warren is **the bounded interior where unfinished cognition is
permitted to exist without acquiring authority**.

```
Warren activity ≠ system truth
```

The Warren generates candidate transformations. The sovereignty
boundary determines which transformations may leave it. Its purpose is
not consensus; it is **productive disagreement under containment**.

```
multiplicity ⊬ validation
```

Ten goblins repeating the same unsupported conclusion still produce
one unsupported conclusion.

---

## 1. The goblin — a typed operation, not an employee

A goblin is a narrowly typed cognitive operation:

```
gᵢ : Xᵢ → Yᵢ          gᵢ(x) = (cᵢ, eᵢ, τᵢ, σᵢ)
```

| Field | Meaning |
|---|---|
| `c` | candidate claim |
| `e` | evidence refs |
| `τ` | claim type |
| `σ` | epistemic status |

**Claim-type vocabulary (τ):** `hypothesis · observation · derivation ·
test_result · proposal · failure`

The status stays explicit forever. A goblin does not "know" — it emits
a typed claim with provenance.

Admissible goblin operations (examples): detect an unsupported
authority claim · search for a counterexample · compare a proposal
with an existing invariant · construct a falsification test · locate
an unresolved semantic promotion · produce a patch candidate ·
challenge the provenance of a receipt.

---

## 2. The Warren — composition environment

```
𝒲 = (G, Γ, Λ, B, A)
```

| Symbol | Component | Current location |
|---|---|---|
| `G` | goblin operator set | swarm agents; `temple/gardens/goblin_garden_conquest/warren_loop.py`; day1 sim agents (game altitude) |
| `Γ` | typed dependency graph | ❌ NOT LOCATED as explicit edge-type declarations (see §4) |
| `Λ` | append-only internal ledger | `temple/autoresearch/` outbox + consumption log, operator_pen hash chain |
| `B` | sovereignty boundary | sovereign-path firewall (`~/.claude/CLAUDE.md`) + `tools/kernel_guard.sh` |
| `A` | admission interface | operator stamps (ADMIT/DENY/COMPOST) via `operator_pen.py`; kernel `helen_say.py` for admitted writes |

---

## 3. The real threat — semantic promotion, not escape

The primary danger is not that a goblin escapes. It is that an
internal object **silently changes type while moving**:

```
default → classification → routing decision → proposal → admitted state
```

The Warren polices **morphisms, not merely agents**. A perfectly
bounded goblin can still participate in an unsafe pipeline if its
output is consumed under a stronger interpretation than the one it
produced.

---

## 4. Forbidden morphisms — enforcement audit

Every edge in Γ should declare `source type → permitted target type`.
The following promotions are forbidden. Audit as of `97bec2d`:

| # | Forbidden morphism | Status | Enforcement location |
|---|---|---|---|
| M1 | generated receipt → verified receipt | ✅ ENFORCED | `tests/test_doctrine_replay.py` — chain verify, tamper localization at exact position |
| M2 | internal agreement → governance approval | ✅ ENFORCED (seams) | `src/separation_gate.py` σ₃ proposer≠validator, σ₄ hal≠builder; FABLE_PASS ⊬ admission |
| M3 | candidate patch → implemented change | ✅ ENFORCED (seam) | σ₅ dreamt≠claimed (`authority:false` on all consumption entries); triage⊬consumed pytest invariant |
| M4 | parser fallback → semantic classification | 🟡 PARTIAL | `src/wul_packet_validator.py` — unknown tokens → warning, never classification; warning-tier not blocking |
| M5 | passing syntax → validated behavior | 🟡 PARTIAL | K-tau/K8 gates exist; no gate blocks a syntax-pass being *reported* as behavior-pass |
| M6 | absence of error → evidence of correctness | ❌ NOT LOCATED | "launcher green ⊬ game good" is prose; no gate requires positive artifact binding for PASS claims |
| M7 | repeated claim → corroborated claim | ❌ NOT LOCATED | adversarial-verify is methodology; nothing detects N same-provenance restatements posing as N witnesses |

**Buildable gap (unstamped):** σ₇ *absence⊬evidence* — every PASS claim
must bind a positive artifact hash, not a no-error exit. σ₈
*repetition⊬corroboration* — claims sharing a provenance digest count
as one witness. Both fit the `separation_gate.py` predicate pattern.

---

## 5. Sovereignty boundary — one-way membrane

Not a validator after the Warren finishes; a **one-way membrane with a
narrow export language**. Internally: rich, contradictory, provisional.
Externally: only objects satisfying the admission schema.

```
A(z) = ADMIT(z)   if all required proofs are present
       HOLD(z)    if evidence is incomplete
       REJECT(z)  if an invariant is violated
```

Admission depends on receipts generated **outside the candidate's own
semantic loop**. A proposer must not manufacture the evidence that
certifies its proposal:

```
proposal producer ≠ proof producer ≠ admission authority
```

Three non-collapsible **roles**, not necessarily three models.
Current instantiation: goblins/HER propose → gates/replay prove →
operator + reducer admit. Enforced at: σ₃ (builder cannot import the
gate), σ₄ (builder cannot run it), sovereign firewall (the execution
shell cannot write the ledger at all).

---

## 6. The ledger — append-only epistemic history

Shared **mutable** memory would let the Warren rewrite its own
epistemic history. Canonical form:

```
λₖ = (id, parent_ids, operator, input_hash, output_hash,
      claim_type, status, evidence_refs)
```

A goblin may append a contradiction or a superseding claim. It may
never erase a previous claim. The Warren remembers not only what it
currently believes but **how each candidate acquired its status**.

Located: `operator_pen.py` hash chain (GENESIS-anchored,
`entry_hash = sha256(canon(body))`), replay-tested in
`tests/test_doctrine_replay.py`. Gap: current entries lack
`parent_ids` / `claim_type` fields — chain integrity is enforced,
claim-genealogy is not.

---

## 7. The quotient relationship — witnesses over verdicts

Given a receipt map `R : 𝒮 → ℒ`, the Warren searches for states the
current observer fails to distinguish. A goblin's most valuable output
is often a **witness**:

```
s ≠ t   but   R(s) = R(t)
```

That witness proves the receipt regime is incomplete at the required
resolution. The Warren's first duty is to expose the collapse — not to
choose which of `s`, `t` is "true." The sovereignty layer decides
whether and how `R` must be refined.

(Proved instance: Garden T1+T2 — structural ceiling 0.6667 on semantic
cases; Π(x) ≠ Truth. The reducer/human is the only semantic admission
path.)

---

## 8. The five laws

| Law | Statement | LOCATED | ENFORCED | REPLAYED |
|---|---|---|---|---|
| **1. No self-promotion** | An output cannot strengthen its own epistemic status | ✅ σ₅/σ₆ | ✅ authority:false invariant; render⊬state | ✅ `test_sigma_gate.py` |
| **2. No untyped transport** | Every inter-goblin edge preserves or explicitly transforms claim type | 🟡 WUL tiers only | 🟡 packets, not general Γ edges | 🟡 `test_wul_packet_validator.py` (29) |
| **3. No consensus authority** | Agreement changes neither evidence nor admission status | ❌ prose | ❌ (= M7 gap) | ❌ |
| **4. No mutable history** | Claims appended, contradicted, superseded — never rewritten | ✅ operator_pen chain | ✅ tamper breaks hash | ✅ `test_doctrine_replay.py` (10) |
| **5. No sovereign execution** | The Warren constructs candidates and tests; never admits canonical state or executes irreversible effects | ✅ firewall paths | ✅ kernel_guard + admissible bridge (`helen_say.py` only) | 🟡 guard script, no replay fixture |

Verdict on itself: **3 of 5 laws are living gates; Law 2 is partial;
Law 3 is prose awaiting σ₈.** This constitution is admissible as a
map, not yet as a wall.

---

## 9. Mythic reading

The Goblin is the creature allowed to touch dirt, ambiguity, discarded
fragments, false starts, and embarrassing contradictions. The Town
cannot work in that material without contaminating its authoritative
surface. The Warren protects sovereignty by **giving disorder a
legitimate habitat**.

Its shadow appears when the habitat becomes a kingdom — when goblins
mistake prolific internal activity for jurisdiction.

> The Warren may discover what the Town cannot yet see.
> It may not decide what the Town must believe.

> Myth is fuel; ledger is law.
> The Warren is the furnace, not the throne.

---

## 10. Two altitudes, one discipline

The same morphism law runs at kernel altitude and at game altitude:

| Kernel | Game (day1/ramp, goblin-warren repo) |
|---|---|
| proposal ⊬ admission | MARK ⊬ resolution (influence is not action) |
| trace presence ⊬ verdict | faint signal ⊬ Bram acts (BRAM_ACT_THRESHOLD) |
| attention ⊬ authority | Lulu watches ⊬ Lulu fixes |
| typed packet routing | mark *type* decides which goblin comes (V3 direction) |

The child who says "I didn't lift the rock — I made Bram notice it"
has learned Law 5 without vocabulary.

---

*This document is a 🟣 CLAIM. Promotion to 🟠 REVIEW is the operator's
act. Green means admitted, never "successfully written."*
