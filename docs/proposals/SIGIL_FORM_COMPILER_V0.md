# SIGIL FORM COMPILER V0 — A Sigil Is a Portable Structure, Not an Image

```
type:           PROPOSAL
authority:      false
canon:          false
ledger_effect:  none
claim_status:   NO_CLAIM
parent:         TEMPLE_CONSERVED_FORM_V0.md · HELEN_SIGIL_REGISTRY_MERGE_V0.md
final:          HOLD_FOR_OPERATOR
date:           2026-08-04
origin:         operator-relayed upstream synthesis, verbed WRITE PROPOSAL
                2026-08-04; the "universal sigil grammar" is a research
                hypothesis, not an established historical fact
```

HELEN OS — created by JM Tassy.

---

## 0. Redefinition

A sigil is no longer defined as an image. It is:

```
a symbolic structure portable across several media
```

i.e. the representation of a deterministic traversal that can be translated
from one medium to another (graphic, sonic, gestural, numeric) without
losing its identity.

## 1. Canonical object

```
S = (M, N, C, G, R, P)
```

| Component | Meaning |
|---|---|
| M | source message (verbatim, hashed) |
| N | normalized symbol sequence (mapping version pinned) |
| C | coordinate sequence (alphabet → grid) |
| G | traversal graph (nodes = occupied cells, edges = consecutive steps) |
| R | rhythmic realization (derived, not composed) |
| P | provenance and policy (source class, mapping id, ambiguity log) |

Compilation pipeline:

```
phrase → normalized symbols → numbers → coordinates → graph
       → rhythm → animation → haptic → code
```

Everything downstream of G is a **renderer**. Renderers currently foreseen:
`visual · audio · temporal · haptic · voxel · computational`.

## 2. The conservation property

The property the compiler guarantees — and the only one:

```
same source + same rules = same intermediate structure
```

NOT:

```
same appearance
```

Two renderings may look nothing alike; they are equivalent iff they derive
from the same (N, C, G) under declared mappings. Equivalence is checked by
fingerprint: sha256 over canonical JSON of each intermediate. NO HASH = NO
VOICE applies — an unfingerprinted projection has no standing in a
comparison.

Divergence semantics: the first index at which two compilations differ
localizes the defective transformation. This is the debugging value of the
multi-projection design (see TEMPLE_CONSERVED_FORM_V0 §1).

## 3. Historical grammar (hypothesis, attested components)

Across the surveyed corpora the recurring architecture is:

```
Name → Alphabet → Grid → Path → Figure → Ritual
```

The compiler is a modern formalization of that scheme. What is attested is
the recurrence of components (letter/number squares, wheels, hexagrams,
name lists, paths); what is hypothesis is any claim that a single grammar
underlies them historically. The compiler makes the hypothesis *testable*:
if distinct traditions' artifacts compile to structurally similar (C, G)
under declared mappings, that is a measurable formal resemblance — and
still not a proof of transmission.

Corpus data (divine/angelic name tables, abbreviation formulae such as
AGLA / ARARITA / ANA BEKOACH, square inventories) is ingested only via
`helen_os/knowledge/symbolic_sources/` under T4/T6 provenance floors, each
item tagged with source class and attestation status. This document stays
data-free by design.

## 4. Determinism constraints

- Mapping tables are versioned artifacts (`MAPPING_V1`, …); a compilation
  pins its mapping id in P.
- Normalization ambiguities (dropped characters, merged letters, dialect
  choices) are **logged in P, never silent**.
- No wall-clock, no randomness anywhere in the pipeline (K-tau
  mu_DETERMINISM); identical inputs must produce byte-identical packets.
- Compiler output is a TEMPLE replay packet (see TEMPLE_CONSERVED_FORM_V0
  §2) — `authority: false`, `ledger_effect: none`.

## 5. Relation to existing lanes

- **HELEN_SIGIL_REGISTRY_MERGE_V0** governs glyph *meaning* (one glyph =
  one primary meaning). This compiler governs form *conservation*. The
  registry is the semantic membrane; the compiler is the structural engine.
  They compose; neither subsumes the other.
- **WUL**: compiled packets are candidate WUL attachments — bounded
  structure, hashed artifacts, no free text in the decision layer.
- First executable instance: `BEAD-TEMPLE-CONSERVED-FORM-001`
  (`temple/subsandbox/conserved_form/`).

## 6. Non-claims

This document is a proposal. It admits nothing, promotes nothing, claims no
historical fact beyond attested component recurrence, and must not be cited
as HELEN doctrine unless admitted through HELEN's own machinery.
