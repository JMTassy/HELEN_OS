---
name: HELEN_PROOF_FRONTIER_V0
status: CANDIDATE_GENERALIZATION
authority: false
canon: false
ledger_effect: none
session: eec5cb93-4b2a-4a99-9806-73e035e48e29
frozen: 2026-08-14
subsumes: r★ (scalar Vision ladder), VISION_CROSSING_V3_SPEC (specific instance on chain poset)
does_not_supersede: kernel, gates, MAYOR, ledger (those are substrate implementations of this calculus)
---

# HELEN PROOF FRONTIER V0 — CANDIDATE GENERALIZATION
## CANDIDATE_GENERALIZATION — not CANON, not IMPLEMENTED, not VERIFIED

This document generalizes r★ (Vision promotion scalar on a chain) to F★ 
(proof frontier antichain on a partial order). The generalization absorbs:
Vision, UZIK documentary, Git substrate, Swarm, EXEC, ATF historical, 
1711 operational, and the HELEN development pipeline itself.

**Same crossing calculus ≠ same warrant semantics.**
Each domain provides typed warrants. The kernel calculates the frontier.

---

## 1. Formal Definition

### Claim space

```
P = (Ψ, ⪯)
```

Partially ordered set of institutional claims.
ψ_a ⪯ ψ_b means ψ_b is institutionally stronger, or requires at least 
the obligations of ψ_a.

### Per-claim obligation

For each ψ ∈ Ψ:
```
O_ψ = (W_req, P_req, A_req, R_req, Ω)
```
— required warrants, proof type, authority level, receipt type, scope.

### Licensed set

```
L(W) = {ψ ∈ Ψ : Discharge(O_ψ, W, Ω) = PASS}
```

**Required property — down-set (downward closed)**:

```
ψ ∈ L(W)  ∧  φ ⪯ ψ  ⟹  φ ∈ L(W)
```

Falsifier for this property: does the system ever license BUILT_AS_DESIGNED 
without licensing BUILT? If yes, L(W) is incoherent.

### Proof frontier

```
F★(W) = Max_{⪯}(L(W))
```

The antichain of maximally licensed claims. F★ is neither a probability 
nor a confidence score. It is the minimal representation of the maximal 
licensed consequence.

### Lossless compression property

```
L(W) = ↓F★(W) = {φ : ∃ψ ∈ F★(W), φ ⪯ ψ}
```

HELEN need not carry 500 boolean state flags. It carries only F★, and 
reconstructs the full licensed set from the declared poset.

---

## 2. Monotonicity Laws (three cases)

### ΔW⁺ — valid warrant added, no invalidation

```
W ⊆ W'  ∧  ¬Invalidate(W, W')  ⟹  L(W) ⊆ L(W')
```

If the new warrant specifically discharges a frontier obligation:

```
DischargeGain(w⁺) > 0  ⟹  L(W ∪ {w⁺}) ⊋ L(W)
```

Antichain comparison uses domination order:

```
F₁ ⊑_dom F₂  iff  ∀ψ ∈ F₁, ∃φ ∈ F₂: ψ ⪯ φ
```

Then: F★(W) ⊑_dom F★(W ∪ {w⁺})  with strict when new region opened.

### ΔW⁻ — warrant withdrawn or source invalidated

```
Invalidate(w)  ⟹  Reevaluate(Descendants(w))
```

L(W') ⊄ L(W) is possible. The frontier may retract.
Historical record preserved: ADMITTED@t₀ and CHALLENGED@t₁ coexist.
The old frontier is not erased — it is superseded with a timestamp.

### ΔW× — contradiction

```
L(W') ⊉ L(W)  (not guaranteed to be monotone)
```

Contradiction must route to explicit conflict resolution. Silent override 
of a prior warrant is a CROSSING_POLICY_VIOLATION.

**The frontier is revisable, not monotonically progressive.**
A falsifying experiment that retracts a claim is epistemic progress.

---

## 3. Strong Constitutional Invariant

```
ΔF★ ≠ 0  ⟹  ΔDischarge ≠ 0
```

Nothing that produces zero new warrants may move the proof frontier.

Applies to: crop, resize, OCR, paraphrase, photorealism, model consensus,
duplication, metadata enrichment, caption generation, agent-to-agent relay,
representation format change, or any purely derivational transform.

This is the generalization of Vision V2's "no perceptual property mints a 
world state" to all domain types.

---

## 4. Two-Graph Separation

```
G_⟹  ≠  G_W
```

| Graph | Contents |
|---|---|
| G_⟹ | Implication/license graph between claims; typed edges |
| G_W | Warrant graph; actual available evidence with provenance |

The frontier engine computes:

```
F★ = Max(Closure_{G_⟹}(ClaimsDischarged(G_W)))
```

"This document establishes X" (G_W edge) ≠ "X implies Y" (G_⟹ edge).
These are two separate proofs. They must not be conflated.

### Edge typing in G_⟹

```
e = (ψ_i, ψ_j, τ_e, ρ_e, v_e)

τ_e ∈ {LOGICAL, POLICY, EMPIRICAL, WORKFLOW, TEMPORAL}
```

Examples:
- BUILT_AS_DRAWN → BUILT:   τ = LOGICAL (valid by definitional entailment)
- APPROVED → EXECUTED:       this edge must NOT exist (the canonical EXEC attack)
- COMMIT_EXISTS → TESTS_PASS: τ = EMPIRICAL (requires behavioral witness)
- DECIDED → EXECUTED:        τ = WORKFLOW (requires a separate execution warrant)

**The poset G_⟹ is itself an attack surface.**
Warrant corruption and order corruption are independent failure modes.
A system can have perfectly valid warrants and still over-promote if G_⟹ 
contains an unauthorized edge.

CROSS must govern G_⟹ edges as well as W.

---

## 5. Temporalized Frontier

```
F★(W; t, Ω, v)
```

- t: validity time being queried
- Ω: scope (branch, seat, organizational context)
- v: calculus/ontology version

Same memory yields different frontiers across scopes:

```
F★(W; t₁₉₄₅) ≠ F★(W; t₁₉₄₇)   (same archive, different temporal scope)
F★(W; branch_A) ≠ F★(W; HEAD)   (same repo, different ancestry scope)
```

This is why:

```
Exists(commit)  ↛  Ancestor(commit, HEAD)  ↛  BehaviorVerified(commit)
```

The claim is not false. Its scope of validity is simply different.
Scope mismatch is a crossing into the wrong Ω — not a warrant failure.

---

## 6. Proof Frontier Delta in Receipts

Receipts should record the frontier change, not only the decision:

```
ΔF★ = F★_after ⊖ F★_before
```

Three distinct receipt annotations:

| Symbol | Meaning | Interpretation |
|---|---|---|
| `+ψ` | ψ newly enters L(W) | Warrant discharged obligation |
| `-ψ (dominated)` | ψ is no longer maximal | Stronger claim ψ' ≻ ψ now licensed; ψ NOT falsified |
| `-ψ (invalidated)` | ψ exits L(W) | Source warrant retracted or contradicted |

`-ψ (dominated)` ≠ `-ψ (invalidated)` — these are distinct operations with 
different implications for dependent claims.

---

## 7. HOLD = Minimal Cut Sets

```
B★(W) = MinimalOpenObligations(∂L(W))
```

The minimal families of obligations whose discharge would expand L(W) toward 
a target claim c.

```
H(c) = (F★, B★(W), x★, cost, risk)
```

HELEN knows exactly why it is blocked and what families of evidence could 
resolve the block — not just "missing warrant" but the minimal cut families.

DISCRIMINATE selects optimal acquisition:

```
x★ = argmax_x  E[V(L(W ∪ W_x)) - V(L(W))]  /  (Cost(x) + λRisk(x))
```

V: 2^Ψ → ℝ weighted by current objective.
Acquiring SAFE_BASE_FOR_V3 may outweigh twenty descriptive claims.
Research = frontier-directed acquisition.

---

## 8. Primary Falsifier: PER_F

```
PER_F = P(F★_system ≻_dom F★_warranted)
```

Frontier Promotion Error Rate: the frequency at which HELEN licenses claims 
that exceed what its warrants support.

Replaces generic "hallucination rate" as the primary constitutional benchmark.

Cannot be gamed by HOLDing everything — requires DA ≥ DA_min (acquisition 
quality floor). The system must advance when genuine warrants arrive AND 
must not advance when they do not.

---

## 9. Relation to HELEN OS Kernel

The kernel is not adjacent to this calculus. It IS the substrate implementing it.

| Kernel object | Proof Frontier interpretation |
|---|---|
| Gates K8/K-tau/K-rho/K-wul | O_ψ obligations — each gate discharges one claim level |
| MAYOR signing a receipt | Γ = ADMIT — the crossing authority function |
| town/ledger_v1*.ndjson | The admitted G_W — witnessed world-state (downward closed) |
| python3 tools/helen_say.py | The only licensed CROSS bridge — the sole L_C→L_L path |
| Sovereign-path firewall | Substrate implementation of "no direct I→G_W callable path" |
| SHIP / ABORT session end | F★ advanced (SHIP with artifact) or B★ blocking (ABORT with reason) |

The kernel does not define what promotion means. F★ formalizes what the 
kernel has been computing operationally: the maximal licensed consequence 
that can be entered into the ledger.

---

## 10. Domains Absorbed (warrant semantics distinct per domain)

| Domain | Warrant type | Representative claims |
|---|---|---|
| Vision (A&A corpus) | Photograph, caption, plan | BUILT, REFERENT_IDENTIFIED, DATED |
| UZIK / GMail | Email, document, contract, calendar | DECIDED, AUTHORIZED, DELIVERED |
| Git / substrate | Commit hash, ancestry, test result | CODE_EXISTS, ANCESTOR_OF_HEAD, TESTS_PASS |
| Swarm | Agent derivation, equivalence class, N_epi | HYPOTHESIS_DISTINCT, SATURATED |
| EXEC | Authorization receipt, signed policy | EFFECT_LICENSED, CAPABILITY_GRANTED |
| ATF | Catalog entry, specimen photograph | CATALOGUED, NOT_PROVED_USED_HISTORICALLY |
| 1711 | Drill entry, authority signature | DEFINED, NOT_PROVED_OPERATIONALLY_AUTHORIZED |
| HELEN dev | PR, commit ancestry, test run, gate verdict | BUILD_VERIFIED, SAFE_TO_EXTEND_V3 |

**Same crossing calculus ≠ same warrant semantics.**
The kernel calculates F★ uniformly; the warrant types are domain-specific.

---

## 11. Six Additions Frozen as CROSS_FRONTIER_V0

1. `r★ → F★` — scalar replaced by antichain of maximally licensed claims
2. `L(W) = ↓F★(W)` — downward closure; F★ is lossless compression
3. `ΔW = 0 ⟹ ΔF★ = 0` — representation invariance (strong invariant: ΔF★≠0 ⟹ ΔDischarge≠0)
4. `W ⊆ W' ∧ ¬Invalidate ⟹ L(W) ⊆ L(W')` — monotonicity (ΔW⁺ case only)
5. `HOLD → B★(W) → x★` — minimal cut sets, not single missing bridge
6. `PER_F = P(F★_system ≻_dom F★_warranted)` — constitutional falsifier

---

## 12. Canonical HELEN Phrase (frozen)

> **HELEN maintains the maximal antichain of consequences currently licensed by 
> scoped, replayable warrants.**
>
> **It acquires information to move, retract, or resolve that frontier without 
> allowing representation alone to move it.**

This captures both promotion AND falsification. A system that can only 
gain claims is not scientifically adequate. HELEN must be able to lose claims.

---

## 13. Open Questions / Gaps

1. **Discharge calculus**: when can PARTIAL ⊗ PARTIAL = FULL? A rule set 
   is needed; a free LLM decision is not acceptable here.

2. **G_⟹ governance**: who authorizes new implication edges? MAYOR? 
   A separate schema authority? This is the "order corruption" attack surface.

3. **Invalidation cascade**: how far does Reevaluate(Descendants(w)) propagate 
   in a large warrant graph? Needs a termination / scope bound.

4. **Viability kernel V**: formal definition of 
   V = {F : PER_F(F) ≤ ε, C(F) ≥ C_min} under adversarial perturbations.
   Connection to AVT (Adversarial Viability Theory) needs explicit bridge.

5. **Crossing Repeller R_C**: R_C = Var(∇_z{F★, W, ρ, confidence}) / (‖∇_z W‖² + ε) 
   needs precise space definitions before canonicalization.

6. **Temporal scope resolution**: who determines t, Ω for a given query? 
   Must be declared before inspection (pre-commitment property).

7. **Σ-SEED adaptation**: the seed function should track I_t (epistemic resolution: 
   warrants gained, contradictions resolved, obligations clarified) not just 
   F★_t ⪰ F★_{t-1}. A falsifying experiment may decrease F★ while increasing I.

---

*CANDIDATE_GENERALIZATION — not CANON, not IMPLEMENTED, not VERIFIED*
*VISION_CROSSING_V3_SPEC is a special case: linear poset (chain), visual warrant domain.*
*The HELEN OS kernel is the substrate implementation of this calculus, not a 
separate layer adjacent to it.*
