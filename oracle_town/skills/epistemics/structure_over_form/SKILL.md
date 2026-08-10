---
name: epistemics/structure_over_form
description: Enforce the priority of combinatorial structure over isolated visual form when analyzing any system of discrete signs (scripts, glyphs, symbol palettes, motifs, tokens). Three-layer architecture — FORM (weak) / STRUCTURE (empirical) / FORMAL CONCEPT LAYER (formal relative to declared context). Structure can falsify strongly but usually confirms only weakly. First application: WULmoji structural fingerprint.
helen_faculty: EPISTEMICS
helen_status: PROPOSAL (drafted 2026-08-07; not doctrine, not invariant)
authority: false
claim_status: NO_CLAIM
banner_max: "🔵 OBSERVED"
---

# STRUCTURE OVER FORM — Combinatorial-Structure-First Discipline

**Class**: Non-sovereign epistemic skill. No kernel authority. No ledger write.
Every output of this skill is a proposal or an observation, never a verdict.

**One-line law**:

> Individual sign forms are weak and freely interpretable. The structure that
> assembles them is stronger and less freely interpretable. Any link between
> form and value must be justified by structure — never the reverse.

---

## 1. Three-layer architecture

```
L0  FORM
    resemblance / iconography / shape
    epistemic force : WEAK
    output class    : hypothesis only (Garden)

L1  STRUCTURE
    counts / unordered pair co-occurrence / adjacency / position /
    entropy / mutual information / transition constraints
    epistemic force : EMPIRICAL
    output class    : measured observation (replayable)

L2  FORMAL CONCEPT LAYER
    declared formal context (G, M, I) — objects × attributes × incidence
    derivation operators  A′ = {m ∈ M : ∀g ∈ A, gIm}
                          B′ = {g ∈ G : ∀m ∈ B, gIm}
    closures A ↦ A″, B ↦ B″ · concepts · implications
    epistemic force : FORMAL_RELATIVE_TO_DATA_MODEL

L3  EMPIRICAL CLAIM
    external evidence · independent test · world-facing interpretation
    epistemic status : TESTED | CONTRADICTED | UNRESOLVED
```

**Non-derivability seams** (each crossing is an explicit act, never
automatic): `L0 ⊬ L1 · L1 ⊬ L2 · L2 ⊬ L3`. In particular L1 may serve to
*construct* K, but only after explicit declaration of the context and the
incidence rule: `STRUCTURE → possible construction of K, but STRUCTURE ⊬
FORMAL_CONTEXT automatically`. And the model/world boundary:
`K ⊨ X→Y` means only that in the declared context every object with X has
Y — it never yields `World ⊨ X→Y` by itself.

The L2 qualifier is load-bearing: an FCA conclusion is formal **relative to
the chosen context**. It certifies nothing about whether the attributes were
well chosen. Rigor over a representation is not truth of the representation:

```
┌─────────────────────────────────────────────────────┐
│ Formal rigor over a chosen representation           │
│              ≠                                      │
│ truth of the representation                         │
└─────────────────────────────────────────────────────┘
```

This is what prevents FCA from becoming sophisticated gematria.

## 2. Invariants

1. **Justification order.** `FORM → STRUCTURE` is forbidden as a proof
   direction. Structure may justify a form-value link; form may never
   justify a structural claim.
2. **Attribute-choice independence.**
   `ATTRIBUTE_CHOICE ↚ TARGET_CORRESPONDENCE` — structural attributes must
   be defined independently of the correspondence under test, or at minimum
   their provenance must be declared before results are seen. A lattice
   built from attributes chosen after seeing the desired match encodes the
   bias, not the data.
3. **Asymmetric force.** Structure **falsifies strongly** (a required
   transition with observed frequency ≈ 0 heavily weakens the hypothesis)
   but **confirms weakly** (high structural similarity can come from
   universal constraints, frequency effects, alphabet size, or independent
   convergence). Hence:
   `STRUCTURAL_COUNTEREVIDENCE > FORM_RESEMBLANCE`
   but never `STRUCTURAL_SIMILARITY = IDENTITY`.
4. **Type separation.** `VISUAL ≠ STRUCTURAL ≠ FUNCTIONAL ≠ HISTORICAL`.
   A hypothesis may not silently change type. Schema:

   ```yaml
   correspondence:
     visual:     OBSERVED
     structural: SUPPORTED | CONTRADICTED | UNKNOWN
     functional: HYPOTHESIZED | TESTED
     phonetic:   HYPOTHESIZED | TESTED
     historical: UNESTABLISHED | DOCUMENTED
   ```

   `LOOKS_LIKE ↛ SAME_ROLE ↛ SAME_SOUND ↛ SAME_ORIGIN` is a schema
   constraint, not merely a doctrine sentence.
5. **Form-motivated claims stay weak.** Any phonetic, semantic, functional,
   or historical correspondence initially motivated by form remains a weak
   hypothesis until supported by evidence independent of that form.
   Structural compatibility may raise plausibility or eliminate
   incompatible candidates; it cannot by itself establish phonetic value,
   functional identity, historical descent, or common origin.
6. **Execution receipts are not evidence.** Referee-safe form (engraved):
   *under a fixed formal context and unchanged evidence, reapplying the
   same closure operator does not modify the obtained closure and provides
   no new independent empirical evidence.* A second run may produce new
   execution metadata (logs, run receipts) — never a new element of X″.
   `NEW_EXECUTION_RECEIPT ⊬ NEW_EVIDENCE ·
   EXECUTION_RECEIPT ⊬ EMPIRICAL_CORROBORATION`.

## 3. Pipeline (causal order)

```
FORM        → candidate hypothesis (explicitly separate object)
                    │
STRUCTURE   → compatibility test (pair frequencies, positions, entropy)
                    │
FCA (L2)    → concept-membership / closure / implication test
              over a DECLARED context (G, M, I)
                    │
EXTERNAL    → independent phonetic / historical / semantic adjudication
```

FCA does not have to *produce* candidates; its role is chiefly to *test*
them. Form-derived candidates enter the pipeline as labeled hypotheses, not
as outputs of the formal layer.

Note: `pair frequencies ≢ Galois connection`. A co-occurrence matrix is L1
empirics. The Galois connection exists only once a formal context (G, M, I)
is declared. Do not launder L1 statistics in L2 vocabulary.

## 4. Triggers

- Comparative analysis of writing systems or symbol sets
- "Same letter / same power" claims based on visual resemblance
- Assigning meaning or sound to isolated glyphs
- Decipherment attempts; historical alphabet tables; iconographic corpora
- Auditing HELEN's own sign systems (WULmoji, WUL packets, seals)
- Anyone reversing the justification order (form → structure)

## 5. Procedure

1. Ignore isolated form first. Do not start from resemblance.
2. Declare the corpus and the attribute set, with provenance, **before**
   computing (Invariant 2).
3. Measure structure: unordered pair frequencies / co-occurrence within a
   declared window (line, block, document — state which and why).
4. Only then examine whether visual similarities are supported by shared
   combinatorial behaviour.
5. Report the two layers separately:
   - form observations → weak claim, Garden
   - structure observations → empirical, replayable
6. If L2 is used, declare (G, M, I) explicitly and carry the
   `FORMAL_RELATIVE_TO_DATA_MODEL` qualifier on every conclusion.
7. Never let a form-based argument override a structural counter-argument.

## 6. HELEN envelope

```
reads    : declared sign corpus only (paths listed in the artifact)
writes   : non-sovereign artifacts only (this skill's artifacts/ dir,
           docs/proposals/) — never firewall paths
artifact : two-layer report (form vs structure) + co-occurrence matrix JSON
receipt  : sha256 of every corpus file embedded in the artifact — the
           analysis is replayable or it is nothing. The output receipt
           MUST additionally declare: which formal context K was used,
           which operations (′/″) were applied, and which validity
           boundary remains (what the result does NOT establish).
           NO_RECEIPT → NOT_ADMISSIBLE as skill output. The receipt
           certifies the execution, never the truth of interpretation.
HAL flag : every form→value correspondence emitted as AURA_PROPOSED_*,
           never as claim; structural counterevidence emitted as
           OBSERVED with the probe that produced it
```

## 7. First application — WULmoji structural fingerprint

`fingerprint.py` (this directory) computes, deterministically:

- symbol counts for the locked 14-symbol palette
  (`oracle_town/skills/ops/wulmoji_enhancer/SKILL.md` §2)
- unordered pair co-occurrence at three declared windows:
  line (doctrine says max 1/line → in-line pairs are *violation signal*,
  not structure), block (blank-line delimited — the real structural unit
  for seals), and document
- per-file sha256 receipts, corpus manifest, palette given as explicit
  NFC codepoint sequences — identity by codepoint, never by visual form
  (lesson B5: symbol filters that trust looks leak through invisible
  joiners and homoglyphs)

Output: `artifacts/wulmoji_fingerprint_v0.json`. Companion doctrine
proposal: `docs/proposals/WULMOJI_STRUCTURE_UPGRADE_V0.md`.

## 8. Seal

```
BEAUTY ⊬ EVIDENCE
FORM ⊬ FUNCTION
STRUCTURE ⊬ ORIGIN
COMPATIBILITY ⊬ IDENTITY
CLOSURE ⊬ HISTORY
CONVERGENCE ⊬ PROOF
IMPLICATION ⊬ CAUSATION
CLOSURE ⊬ EXTERNAL_VALIDATION
REPETITION ⊬ NEW_EVIDENCE
EXECUTION_RECEIPT ⊬ NEW_EVIDENCE
[K fixed ∧ evidence unchanged] ⇒ C(C(X)) = C(X) ⇒ ⚖️⚖️ ↛ 🧾NEW_PROOF

FORM      → HYPOTHESIS
STRUCTURE → CONSTRAINT
FCA       → FORMAL RELATIONSHIP RELATIVE TO DECLARED CONTEXT (K ⊨ ≠ World ⊨)
EMPIRICAL CLAIM (L3) → INDEPENDENT ADJUDICATION: TESTED | CONTRADICTED | UNRESOLVED
```

authority = false. This skill instructs decisions; it never makes them.

HELEN OS — created by JM Tassy.
