<!-- authority=false · claim=NO_CLAIM · a reading, not a ruling -->
# CODEX BEZAE CANTABRIGIENSIS — CHIDDUSH V0

🔵 OBSERVED · NON_SOVEREIGN · authority=false · canon=FALSE · TEMPLE-class historical corpus.
Provenance chain: **S** (Codex Bezae / Scrivener's 1864 edition) → **G** (its transmission structure) → **H** (chiddush).

**Corpus status (honest):**
- **DOWNLOADED** — `ocr.txt` of Scrivener, *Bezae Codex Cantabrigiensis* (Cambridge, 1864), 68,849 lines, sha256 `ed855a25…`. Scrivener's **English prolegomena are WITNESSED** (quoted below, line-referenced); the Greek/Latin uncial transcription is present but noisy.
- **REPORTED** (scholarship): Bezae = **D/05**, bilingual Greek-Latin, 5th c., chief witness of the **"Western" text** (longer, paraphrastic; Western Acts ~8% longer).

EPISTEMIC_SYNTAX class: **historical artifact**, read for *transmission structure*, never theology, never canon.

## The chiddush — Bezae marks the MATERIAL/CONJECTURE boundary and `N_epi=1 ⊬ warrant`

> **Correction to a first, wrong intuition** (caught by peer-review, honored here): an interpolation
> *written in Bezae is materially WITNESSED* — `N_epi(r_D) ≥ 1`. Calling it an "interpolation" is a
> *genealogical hypothesis about an EARLIER state*, NOT a claim that its root count is zero.
> `Interpolated ⊬ N_epi=0` · `SingularReading ⊬ Conjectural`. So Bezae is **not** "a conjecture that
> became witnessed"; it is the archetype of a *materially real* reading that is *weak evidence for the
> original text* — exactly `N_epi ⊬ W`.

**Witnessed, in Scrivener's own words** (l.543–550):
> *"the many **singular readings and arbitrary additions to the sacred text, known to exist in no copy
> save Beza's** … Some of them are of considerable length … such large **interpolations** as follow
> Matth. xx. 28, and the wide variations that abound in Luke iii. …; John vii. 53–viii. 11."*

These additions are **WITNESSED** (Bezae physically has them). What is *conjectural* is the reconstruction
of the earlier archetype they diverge from. And Scrivener's editorial *practice* is the real fence: he
**recorded every stroke he could trace but refused to restore letters merely because they could be
conjectured** — precisely the `WITNESSED / RECONSTRUCTED_TRACE / CONJECTURE` boundary, with `D(r) ⊬ M(r)`.

**And Beza himself stated the law, in the 1580s** (l.868–870):
> *"to avoid giving offence through its **extensive deviations from all other documents, however old**,
> it was more fit to be **stored up than published**."*

That is `N_epi = 1 ⊬ warrant` **and** `age ⊬ authority`, four centuries early: a singular ancient witness
is `HOLD`, not `ADMIT`. Exactly `warrant_supported` (independence count ⊬ warrant) + `graph_ir` non-amplification.

## Term-by-term map (Bezae → committed invariants)

| Bezae / Scrivener | HELEN invariant |
|---|---|
| "arbitrary addition known to exist in **no copy save Beza's**" | the reading is `WITNESSED` (materially in Bezae, `N_epi≥1`); its being an *interpolation* is a genealogical hypothesis about the earlier state — `Interpolated ⊬ N_epi=0` |
| Scrivener records recoverable strokes, refuses to restore conjecturable letters | the `WITNESSED / RECONSTRUCTED_TRACE / CONJECTURE` boundary — `D(r) ⊬ M(r)` (`conjectural_emendation`, MATERIAL_WITNESS_BOUNDARY) |
| a visible original-scribe correction | `WITNESSED_CORRECTION`, never `CONJECTURE` — a temporal layer (W0→W1), both materially witnessed |
| singular reading (Bezae alone) | `N_epi = 1` — one witness, however old, is one root; weak evidence for the original (`N_epi ⊬ W`) |
| Beza: "deviations from all other documents, however old → store up, don't publish" | `age ⊬ authority`, `N_epi=1 ⇒ HOLD` (non-amplification) |
| "a **gloss from Matth. xiii. 12**" imported into Luke (harmonization) | contamination between parallel passages → `~dep` dependency, not a fresh witness (`test_hidden_common_dependency`) |
| bilingual **Greek + Latin** columns (each can be corrected toward the other) | two representations sharing one root — the Latin is not independent of the Greek → `~dep` collapse, `N_epi=1` not 2 |
| the whole **"Western" text-type** | a dependency *family*, not a crowd of independent witnesses — `N_repr ≫ N_epi` |

## The genuinely new insight — the two manuscripts are a matched pair
- **Sinaiticus** = the discipline: careful collation, correctors recorded, copies collapsed to roots. The *positive* control — how governance should look.
- **Bezae** = the disease: singular arbitrary additions inscribed as text, one text-type mistaken for many witnesses. The *negative* control — what governance must catch.

Together they are the empirical `assert` pair for the boundary primitives. Sinaiticus shows the disciplined
`MATERIAL / TRACE / CONJECTURE` boundary in practice; Bezae shows a *materially real* text whose singular,
expansive readings are **witnessed yet weak evidence for the original** — the reason Beza said "store it up."
The corrected law: **status follows the warrant actually consumed (material vs trace vs derivation), and
weight follows independent-root count — neither is set by the plausibility, antiquity, or length of the
reading.** `D ⊬ M` · `N_epi ⊬ W` · `Interpolated ⊬ N_epi=0`.

## Laws carried over (not re-derived)
- `CONJECTURE ⊬ WITNESSED` (`conjectural_emendation`, built tonight) = the anti-interpolation fence.
- `N_epi=1 ⊬ warrant` · `age ⊬ authority` (`epistemic_roots` + non-amplification) = Beza's own "store it up."
- `~dep` collapse = harmonization/contamination and the diglot Greek↔Latin dependency.

## Mode-route (operator-gated)
None self-promotes. `authority=false`. Bezae stays a TEMPLE-class structural specimen, never a truth/canon claim.
- `BUILD INTERPOLATION_DETECTOR` → type a reading as `INTERPOLATION` when it is singular (`N_epi≤1`) AND inscribed-as-text (claims WITNESSED type) — the executable form of "demote the arbitrary addition."
- `COMMIT` → this doc is untracked (NO_COMMIT default).

*authority=false · canon=false · corpus DOWNLOADED (Scrivener OCR, English witnessed) / REPORTED (transmission) · a reading, not a ruling.*
