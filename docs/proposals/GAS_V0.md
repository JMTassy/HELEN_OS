---
schema: HELEN_PROPOSAL_V1
title: Governed Admissibility Systems — V0 (Transport Program, Volume III)
authority: false
sovereign: false
canon: false
ledger_effect: none
claim_status: NO_CLAIM
final: HOLD_FOR_OPERATOR
git_stage: yes  # operator commit mark 2026-07-06
origin: JM Tassy synthesis + external mathematical review rounds 1–5, 2026-07-06; drafted by FABLE (presenter role — presents, never admits); rounds 3–5 disposition in §10
---

# Governed Admissibility Systems — V0
## Transport Theory, Volume III: Governed Dynamics

🟣 CLAIM · NON_SOVEREIGN · PROPOSAL · NO_CLAIM · HOLD_FOR_OPERATOR

This is a standalone mathematical program. HELEN is one concrete instance
(§7). The theory is intended to stand independently of the software that
motivated it.

---

## 0. Position in the Transport Program

| Volume | Object | Status |
|---|---|---|
| I | Observation maps `R : S → L`, fibers, quotients, Fundamental Factorization `R = R̄ ∘ q_R` | landed (`transport/`, `docs/proposals/TRANSPORT_THEOREM_V0.md`, 89 tests) |
| II | Information geometry on observation — earned tier-by-tier (bundles/curvature not assumed) | landed (LaTeX Vol II) |
| **III (this document)** | **Governed dynamics**: which transitions of `S` are *admitted*, and why governance is invariant | 🟣 draft |

The structural analogy is precise at the level of diagram shape — and, per
review round 5, is presented as a *candidate common abstraction*, not an
instantiation of one theory in the other. Volume I proves that every
observation factors through its observational quotient:

```
R : S ──q_R──▶ S/~_R ──R̄──▶ L
```

Volume III studies the same factorization shape one level up, applied to
*state change* rather than *state reading*:

```
𝒯 : 𝒲 ──(evidence)──▶ E ──(reduction)──▶ 𝒞
```

Where Volume I says "you cannot observe past the fiber," Volume III says
"you cannot transition past the evidence." Both concern maps being forced
through a quotient-like middle object — but in Volume I this is a proven
theorem, while in Volume III the exclusion is (for now) Axiom 2.5. The
shapes rhyme; no equivalence is claimed.

**Merge criterion (the "Volume III" label is provisional).** Similar
diagrams are not identity of mathematical objects. GAS earns the Volume III
label only when Research Goal 5.2 is resolved: a common abstraction (shared
category, quotient construction, or universal property) from which the
Vol I factorization and the governed factorization both arise as instances.
Until then, GAS is a *companion theory shelved with* the Transport program —
organizationally adjacent, mathematically unmerged. Claiming the merge from
diagram similarity alone would be shape-matching, not mathematics.

---

## 1. Layer Discipline (rule of this document)

Every statement in this document belongs to exactly one layer, and is marked.

- **Layer I — Mathematics.** Definitions, theorems, proofs. No system names.
- **Layer II — Implementation.** File paths, hashes, tests. One realization
  of Layer I, never an assumption of it.
- **Layer III — Interpretation.** Why it matters ("lawful transmutation",
  "generation ≠ authority"). Confined to §8. Layer III language inside a
  theorem statement is the prose form of admission-language laundering and
  is treated as a defect.

---

## 2. Definitions (Layer I)

**Definition 2.1 (Governed Admissibility System).**
A *GAS* is a tuple `(𝒲, 𝒞, Θ, V_Θ)` where

- `𝒲` is a set (the *configuration space*; informally: proposals, drafts,
  latent states, narratives),
- `Θ` is a finite rule set,
- `V_Θ : 𝒲 → {0,1}` is a total computable *verifier*,
- `𝒞 = V_Θ⁻¹(1) ⊆ 𝒲` is the *admissible subspace*.

**Definition 2.2 (Certification operator).**
`𝒯 : 𝒲 → 𝒞 ∪ {⊥}` is defined by `𝒯(x) = x` if `V_Θ(x) = 1`, else `⊥`.

**Remark 2.3 (Projection algebra — bookkeeping, not depth).**
Extending `𝒯(⊥) = ⊥`, we have `𝒯² = 𝒯`, `𝒞 = Fix(𝒯) ∖ {⊥} = Im(𝒯) ∖ {⊥}`.
These identities are *immediate from Definition 2.2*. They are stated for
notation, and this document does not present them as results (§3).

**Definition 2.4 (Reduction vs. certification — the F/𝒯 split).**
A *reduction operator* `F : 𝒲 → 𝒲` is a (possibly non-idempotent) step
function. The *canonical candidate* of `x`, when it exists, is
`x* = lfp(F)(x)` (the limit of iteration from `x`). Certification applies
after convergence: the *completed certifier* is `𝒯 ∘ lfp(F)`.
`F` and `𝒯` are different operators with different roles; only the second
is a projection. Conflating them is the central technical error this
document exists to avoid.

**Axiom 2.5 (Evidence Separation — model axiom, not theorem).**
Fix three objects: `D` (dialogue/generation), `E` (typed evidence),
`L` (ledger). The *governed transition model* admits exactly two morphism
families:

```
α : D → 𝒫(E)        (generation proposes evidence candidates)
β : L × 𝒫(E) × Θ → L (reduction decides, appending admitted events)
```

and **no morphism `D → L`**. In V0 this exclusion is an *axiom of the
model*; the corresponding theorem is about conformance of an
implementation to the model (Theorem 4.1). A universal property
("every sovereign transition factors *uniquely* through an evidence
object") is a research goal (§5), not a result: `β`'s domain is not yet
an object in a defined category, and uniqueness is unearned.

**Definition 2.6 (Ledger).**
`L ∈ Σ*` for an event alphabet `Σ`: the free monoid, with append
`L_{n+1} = L_n ⊕ e_{n+1}` as the only constructor. State is derived, never
stored: `state_n = fold(ρ, s₀, L_n)` for a total deterministic reducer `ρ`.

**Structural axioms (named per review round 3; Axiom 2.5 is A1).**
The model assumes, as axioms rather than theorems:

- **(A1) Evidence separation** — Axiom 2.5: no morphism `D → L`.
- **(A2) Append-only ledger** — `⊕` is the only constructor of `L`
  (Def. 2.6); no in-place mutation, no deletion.
- **(A3) Deterministic total reducer** — `ρ` is a function of
  `(state, event)` only: no wall clock, no randomness, no ambient IO.
- **(A4) Replay semantics** — the meaning of `L` is `fold(ρ, s₀, L)`;
  there is no other reading of state.

The §4 theorems consume these as hypotheses (4.3 rests on A2–A4; 4.1 on
A1 via H2). They are design commitments of the model; §7 shows one
implementation discharging them.

**Definition 2.7 (Ledger admissibility — the level bridge).**
`Σ` and `𝒲` are different levels: `L_n` is a monoid element, `𝒞 ⊆ 𝒲` is a
configuration subspace. Fix a payload projection `π : Σ → 𝒲` (each event
carries the configuration it admits). An event `e` is *admissible* iff
`π(e) ∈ 𝒞`. Define the **admissible ledger space**

```
𝒞_ledger = { L ∈ Σ* : π(e) ∈ 𝒞 for every event e of L }
```

and write `Inv_Θ(L)` for a predicate on ledgers (chain well-formedness,
`seq` monotonicity, schema conformance of every event). Statements about
"ledgers staying governed" are statements about `𝒞_ledger` and `Inv_Θ`,
never about `L ∈ 𝒞` — the latter is a type error.

---

## 3. Register of Trivialities (what is *not* claimed as a theorem)

External review proposed "Fail-Closed Admissibility" (`V_Θ(x)=0 ⟹ 𝒯(x)=⊥`)
and "Admissibility Preservation" (under hypothesis `𝒯(𝒞) ⊆ 𝒞`) as theorems.
Both are **definitional corollaries** — the first restates Definition 2.2,
the second is induction over a hypothesis that assumes the conclusion's
mechanism. This document registers them as such. Presenting them as
theorems would invite a one-line referee strike and would violate the
program's own discipline (nothing is "earned" by renaming a definition).

The slogan *No receipt → no ship* is the Layer III reading of
Definition 2.2. It is a design commitment, not a discovery.

---

## 4. Theorems with content (Layer I statements, Layer II witnesses)

Each entry: statement → proof obligation → implementation witness → status.

**Theorem 4.1 (Adversarial-proposer soundness).** *Main theorem.*
Let `(𝒲, 𝒞, Θ, V_Θ)` be a GAS with ledger `L` as in Def. 2.6, satisfying:

- **(H1) Verifier soundness & totality.** `V_Θ` is total on `𝒲` and sound:
  `V_Θ(x) = 1 ⟹ x ∈ 𝒞`, and appending an event `e` with `V_Θ(π(e)) = 1`
  preserves `Inv_Θ` (Def. 2.7).
- **(H2) Evidence separation.** Axiom 2.5 holds: the only morphisms into
  `L` are `β`-appends; no morphism `D → L` exists (no unguarded append path).
- **(H3) Reducer fail-closed totality & preservation.**
  `β : 𝒞_ledger × 𝒫(E) × Θ → 𝒞_ledger` is **total**: for every evidence set
  `Ê ∈ 𝒫(E)` (passing or not), `β(L, Ê, Θ) = L ⊕ s` where the suffix `s`
  contains only events `e` with `V_Θ(π(e)) = 1`; `s` may be empty —
  rejection is the identity append, never an error state and never an
  unvetted append. *(Repaired during proof drafting: the earlier form
  constrained `β` only on passing evidence, leaving adversarial evidence
  unspecified — see GAS_V0_PROOFS.md §1.)*

Then for **every** dialogue stream `D` — including adversarial / Byzantine
streams — every reachable ledger satisfies `L_n ∈ 𝒞_ledger` and `Inv_Θ(L_n)`.
*Flavor:* non-interference / preservation, in the sense of
programming-language semantics: soundness must hold against a hostile
wild space, not merely a well-behaved one.
*Honesty note:* without (H1)–(H3) stated as hypotheses, "hostile dialogue
cannot corrupt the ledger" is an engineering claim, not a theorem. (H2) is
where the axiom must be *established for the implementation*
(Proposition 7.1), not assumed of it.
*Proof:* GAS_V0_PROOFS.md §2 (induction on appends from (H1)–(H3);
hypothesis-necessity counterexamples in §3).
*Witness (Layer II):* `tools/kernel_guard.sh` (writer allowlist);
`src/wul_packet_validator.py` unconditional `PERM::WRITE_SOVEREIGN` reject;
root constitutional suite `tests/test_1_…test_9_*.py`.
*Status:* **PROVED** (paper proof; mechanized components exist in
`formal/` — full mechanization is the goal recorded in GAS_V0_PROOFS.md §4).

**Theorem 4.2 (Concurrent-append preservation).**
The chain invariant (strictly incrementing `seq`, well-formed `cum_hash`
links) is preserved under concurrent writers **iff** append is linearized:
each writer acquires an exclusive lock and re-reads the on-disk tail under
the lock before constructing its event. Without the re-read, preservation
fails (a TOCTOU interleaving forks `seq`).
*Proof obligation:* standard linearizability argument; the "only if"
direction is witnessed empirically (§6).
*Witness (Layer II):* `fcntl.flock` + tail re-read in
`tools/ndjson_writer.py`; `helen_os/tests/test_ndjson_writer_atomic.py`
(`test_concurrent_appends_produce_unique_seqs`,
`test_wrong_constructor_seq_is_overridden_by_on_disk_tail`,
`test_duplicate_seq_detector_flags_forked_ledger`).
*Status:* PROOF_SKETCH, with a real-world falsification-and-repair exhibit (§6).

**Theorem 4.3 (Replay determinism / unique reconstruction).**
If the reducer `ρ` is total and deterministic, then
`state_n = fold(ρ, s₀, L_n)` is well-defined and unique: any two replays of
the same ledger prefix yield equal states. Consequently the ledger *is* the
state, up to the (deterministic) fold.
*Proof obligation:* structural induction over the free monoid; the entire
weight rests on establishing determinism of `ρ` (no wall clock, no
randomness, no ambient IO in the fold path).
*Witness (Layer II):* `oracle_town.core.replay`; CI 200-iteration replay
determinism check (`ci_run_checks.py`); LEGORACLE replay gate (E12);
K-tau `mu_DETERMINISM` lint.
*Status:* PROOF_SKETCH; empirically exercised on every push.

**Theorem 4.4 (Conditional integrity).**
Define `h_{n+1} = SHA256("HELEN_CUM_V1" ‖ h_n ‖ payloadhash_{n+1})`. Under
the collision-resistance assumption for SHA-256, the map `L ↦ h_{|L|}` is
computationally injective: producing `L ≠ L'` with equal cumulative hash
implies a collision. **This theorem is conditional on a cryptographic
assumption and must always be stated as such** — unconditionally it is
false (pigeonhole), and stating it unconditionally would not be
mathematics.
*Witness (Layer II):* ledger validator; K8 `mu_NDLEDGER` (hash integrity).
*Status:* standard reduction; write-up routine.

---

## 5. Research goals (explicitly not results)

1. **Universal property of evidence factorization.** Define the ambient
   category (objects `D`, `E`, `L`; a monoidal or Kleisli structure to
   accommodate `β : L × 𝒫(E) × Θ → L`), then prove: every morphism into `L`
   factors through `E`, uniquely up to iso. Until the category is defined,
   "uniquely factors" stays out of all statements.
2. **Volume I ↔ Volume III common abstraction (the merge criterion, §0).**
   Make precise the analogy `q_R : S → S/~_R` (cannot observe past the
   fiber) vs. `α : D → 𝒫(E)` (cannot transition past the evidence) —
   candidate: both as (co)reflections onto subcategories, or both as
   instances of one factorization system. Resolving this goal is what
   *earns* the Volume III label; failing it demotes GAS to a companion
   theory published separately.
3. **Quantitative admissibility.** `V_Θ` as a graded verifier (cf. WUL
   `CONF` thresholds) — does the projection algebra survive grading?
4. **"Drift Algebra".** Referenced in external review ("guards as
   projections") but **not located in the SOT** (repo-wide grep, 2026-07-06:
   zero hits). Per the doctrine triad — no location → no doctrine — it is
   excluded from this program until it lands as an artifact that can be
   cited by path.

---

## 6. Empirical exhibit: the seq=287 fork (falsification and lawful repair)

Formal-methods papers rarely have field data. This program does.

- **Event:** a TOCTOU interleaving between construct-time `seq` reads
  produced a forked ledger `seq` — precisely the failure mode Theorem 4.2
  predicts when the linearization hypothesis is dropped.
- **Detection & post-mortem:**
  `oracle_town/audits/SOVEREIGN_PROMOTION_AUDIT_REFERENCE_DRIFT_WITNESS_V1.md`.
- **Repair:** operator-authorized `LEDGER_SEQ_CORRECTION_V1` packet via the
  admissible path (`oracle_town/protocols/SOVEREIGN_LEDGER_SEQ_REPAIR_PROTOCOL_V1.md`);
  artifact anchored at seq=295; chain returned to PASS.
- **Hardening:** the lock + tail re-read of Theorem 4.2's hypothesis was
  installed in `tools/ndjson_writer.py` and regression-locked by
  `test_ndjson_writer_atomic.py`.

Reading: the theory's assumption was violated in production, the predicted
breach occurred, and the invariant was restored through the model's own
admissible path — not by out-of-band mutation. This is the strongest
evidence in the program that the abstractions carve the system at its
joints.

---

## 7. HELEN as instantiation (Layer II)

**Proposition 7.1 (Axiom conformance).** The HELEN kernel satisfies
Axiom 2.5: every write to `town/ledger_v1.ndjson` factors through the
`NDJSONWriter` kernel boundary (realized by the gate's five-writer
allowlist — `ndjson_writer.py`, `kernel_cli.ml`, `end_session.py`,
`helen_add_lesson.py`, `accept_payload_meta.sh`, all β-family), and no
dialogue surface holds a direct write capability. This is a *meaningful
result about the implementation* (per review round 2), distinct from the
axiom itself: the model excludes `D → L` by fiat; the implementation must
be *shown* to.
*Proof & live verdicts:* GAS_V0_PROOFS.md §5. Split: **7.1(a)**
architectural conformance — SUPPORTED (guard RULE 1 + RULE 3 pass
repo-wide, 22 boundary/atomicity tests pass, 36 constitutional tests pass;
no `D → L` arrow found). **7.1(b)** self-certification — **FALSE at
`dace8b02`**: the designated gate (`kernel_guard.sh` RULE 2) returns FAIL
on 3 stale consumer-allowlist entries, and its CI job is red on `main`.
*Status:* **OPEN — fail-closed.** Not proved while its own verifier is
red; blocked on the operator ruling in the GAS_V0_PROOFS.md §5
remediation packet.

| Abstract (Layer I) | HELEN realization |
|---|---|
| `𝒲` wild space | dialogue, TEMPLE/garden output, autoresearch packets, drafts |
| `E` typed evidence | receipts, `AUTORESEARCH_PACKET_V1`, `CHIDDUSH_RECEIPT_V0`, attestations |
| `Θ` rule set | schemas (`helen_os/schemas/`), K-gates, WUL tiers, policy |
| `V_Θ` verifier | validators + gates (fail-closed), `helen_os/governance/` |
| `F` reduction steps | reducer pipeline, MAYOR ratification stages |
| `𝒯 ∘ lfp(F)` completed certifier | 6-gate `_handle_promote_skill()` path ending in admitted write |
| `L` free monoid | `town/ledger_v1.ndjson`, append-only, `cum_hash` chained |
| `fold(ρ, s₀, L)` | `oracle_town.core.replay` |
| `D ↛ L` exclusion | `kernel_guard.sh` + sole-writer discipline (`helen_say.py` → `ndjson_writer.py`) |
| Garden-level miniature | Warren feed: per-packet `admission: FORBIDDEN`, surface has no stamp control (`apps/goblin-warren/`) |

Non-claims (to be stated verbatim in any paper): no novelty is claimed for
event sourcing, append-only logs, hash chains, replay, fixed-point theory,
or substructural logic individually. The claimed contribution is the
**composition**: a factorization constraint separating generation from
authority, with invariant preservation proven against adversarial
generation, instantiated and field-tested.

---

## 8. Interpretation (Layer III — quarantined)

Within this framework — and only within it — `𝒞 = Im(𝒯)` is the state the
system treats as authoritative. The design commitment this encodes has
session names: *lawful transmutation*, *generation ≠ authority*,
*admissibility-governed intelligence*, *sparse sovereignty*. None of these
phrases carries mathematical weight, and none appears in §2–§7 statements.
They explain why one would build a GAS; they do not prove anything about
one.

---

## 9. Self-audit against the doctrine triad

| Triad | This document |
|---|---|
| Located | ✅ every Layer II witness cited by path; Drift Algebra excluded for failing this test |
| Tested | ◐ Thm 4.1 PROVED (GAS_V0_PROOFS.md §2) with mechanized components (`formal/`, 0 Admitted); Prop 7.1 OPEN — its designated gate is RED at `dace8b02`; Thms 4.2–4.4 remain PROOF_SKETCH |
| Replay | ✅ Theorem 4.3's witness runs 200× per push; this document changes no behavior |

Status honesty: this is a **proposal for a paper**, not a paper. Remaining
work: Thm 4.2–4.4 write-ups, the §5.1 category, the §5.2 merge criterion,
GAS mechanization in Coq, and closing Prop 7.1(b) after the operator rules
on the guard allowlist. Until then, `GAS_V0 ⊬ publishable` — by this
document's own law. The Prop 7.1 episode (gate red, unnoticed, while the
architecture held) is recorded in GAS_V0_PROOFS.md §6 as the paper's second
field exhibit alongside seq=287.

**Remaining proof order (review round 5's ladder, adapted to current
state — Thm 4.1 already has a write-up in GAS_V0_PROOFS.md):**

1. **Theorem 4.3 (Replay determinism)** — shortest, standard induction,
   immediately recognizable to referees; foundations first.
2. **Proposition 7.1(b)** — blocked on the operator's guard-allowlist
   ruling; conformance must be re-established, not asserted.
3. **Theorem 4.2 (Concurrent preservation)** — linearizability argument
   plus the §6 exhibit.
4. **Theorem 4.4 (Conditional integrity)** — routine reduction,
   explicitly conditional on cryptographic assumptions.

---

## 10. External review disposition (rounds 3–5)

| Review point | Disposition |
|---|---|
| R3: definitions are not theorems | already enforced — §3 Register of Trivialities |
| R3: F/𝒯 split essential | already enforced — Definition 2.4 |
| R3: theorem candidates need explicit mathematical hypotheses | already enforced — Theorem 4.1 (H1)–(H3) |
| R3: evidence factorization as axiom + implementation conformance; uniqueness unearned | already enforced — Axiom 2.5 + Proposition 7.1 + §5.1 |
| R3: Vol III label requires common abstraction, not diagram similarity | already enforced — §0 merge criterion + §5.2 |
| R3: name the structural axioms as a distinct layer | **adopted** — (A1)–(A4) block after Def. 2.6 |
| R4: `L_n ∈ 𝒞` mixes levels; define ledger admissibility explicitly | **adopted** — Definition 2.7 (`𝒞_ledger`, `Inv_Θ`); Thm 4.1 restated over `𝒞_ledger` |
| R4: keep model theorem (4.1) separate from implementation proposition (7.1) | already enforced — the split is stated in both statements |
| R4: remaining gap is proofs + formal objects, not structure | agreed — §9 status honesty; the four PROOF_SKETCHes and §5.1 category are the work |
| R5: Transport↔GAS must read "candidate common abstraction", never "instantiation" | **adopted** — §0 softened ("structural continuity is exact" removed; shapes rhyme, no equivalence claimed) |
| R5: proof priority ladder (4.3 → 7.1 → 4.1 → 4.2 → 4.4) | **adopted** — recorded in §9 |
| R5: level-bridge repair (Def. 2.7) is correct, not cosmetic | confirmed — no further action |

No review round has surfaced a structural defect since the level bridge
(Def. 2.7); the document is at referee-shape. What remains is Layer I labor.

---

*proposal ⊬ admission · math ⊬ authority · 🟣 CLAIM · 📜 ledger sleeps*
