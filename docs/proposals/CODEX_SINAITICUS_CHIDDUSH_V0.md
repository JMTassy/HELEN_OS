<!-- authority=false · claim=NO_CLAIM · a reading, not a ruling -->
# CODEX SINAITICUS — CHIDDUSH V0

🔵 OBSERVED · NON_SOVEREIGN · authority=false · canon=FALSE · TEMPLE-class historical corpus.
Provenance chain: **S** (the manuscript / the Lake facsimile) → **G** (its transmission structure) → **H** (chiddush). H never collapses into S.

**Corpus status (honest):**
- **WITNESSED** (archive.org metadata): *"Codex Sinaiticus. The Old Testament,"* creator **Helen and Kirsopp Lake**, 1921 facsimile (Oxford); digitized from IA1879501-12; page `n210`.
- **NOT_IN_SESSION** (manuscript text): photographic facsimile of 4th-century Greek majuscule — **no usable OCR**. The Greek content is not read here.
- **REPORTED** (from textual-critical scholarship, not extracted): Sinaiticus's scribes (A/B/D), its layers of **correctors** (א*, אᵃ, אᵇ, אᶜ across centuries), its variant readings, and the discipline of **collation** the Lakes performed.

EPISTEMIC_SYNTAX class: **MYTHIC_SIGNAL / historical artifact**, read for *transmission structure*, never theology, never canon.

## The chiddush — textual criticism IS claim-local provenance quotienting

The deep finding: **Codex Sinaiticus is the physical archetype of the very architecture this repo shipped tonight.** Textual criticism has, for centuries, done by hand what `epistemic_roots.py` and `graph_ir.py` now do mechanically. The manuscript is not evidence *for* HELEN's paradigm — it is the paradigm's 1600-year empirical precedent.

The one-line convergence:
```
Westcott–Hort, 1881:  "manuscripts are to be WEIGHED, not COUNTED."
epistemic_roots, 2026: N_representations ⊬ N_epi  (count roots)  AND  N_epi ⊬ W  (weigh quality).
```
"Weighed, not counted" is *exactly* the two-part law committed in `3ca3a6d`: ignore representation-count (`Λ_proxy`), collapse copies to independent roots (`N_epi`), then evaluate quality (`warrant_supported`). Textual criticism split *count* from *weight* long before HELEN typed it.

## Term-by-term map (manuscript structure → committed invariants)

| Codex / textual criticism | HELEN invariant (committed) |
|---|---|
| A manuscript **witness** (a copy) | a `Representation` |
| 500 copies descending from one lost archetype | `N_epi = 1`, `Λ_proxy = 500` — **amplification, not corroboration** (`epistemic_roots`) |
| **Shared error → shared ancestry** (stemmatics reconstructs the archetype) | `test_hidden_common_dependency` — different-id roots sharing an upstream **collapse under ~dep** (fixture 4) |
| A late, corrupt-but-genuinely-independent manuscript | `warrant_supported`: `N_epi=10 ⊬ W` — independent yet weak witnesses don't warrant (`fixture 5`) |
| A **corrector** (אᵃ…אᶜ) changing a reading centuries later | temporal supersession — `graph_ir I₄` (a reading at t₁ ⊬ the reading at t₂ without a witnessed correction event) |
| A superseded reading left "open" with no recorded correction | `graph_ir I₇` banishment — an unrevoked state; the apparatus must record the teardown, not silently drop it |
| A scribal error copied into a whole family | `Λ_proxy` high — representational fan-out with zero new root |
| The **critical apparatus** (per-variant witness list) | the `ClaimProvenancePacket` — claim-local root accounting, one packet per reading |
| **Collation** (what the Lakes did to Sinaiticus) | building the derivation graph `G_c` by hand — the manual form of `epistemic_roots` |

## The genuinely new insight
HELEN did not invent non-amplification governance; it **mechanized a discipline that already governs the most consequential text-transmission problem in history.** A biblical variant cannot be admitted because many manuscripts carry it — the manuscripts might all copy one corrupt exemplar. The critic reconstructs the *stemma* (lineage graph), collapses copies to independent witnesses, weighs each, and only then judges the reading. That is `representations → G_c → roots → N_epi → warrant` — the exact pipeline in `3ca3a6d`.

So the corpus does two things for HELEN:
1. **Validates the paradigm empirically** — `citations ⊬ witnesses` is not a novel guess; it's the load-bearing law of a 200-year-old evidential science.
2. **Names the missing layer** — textual criticism also has *conjectural emendation* (a reading with **zero** manuscript support, admitted on internal grounds). That is the epistemic dual HELEN doesn't yet type: warrant from *coherence/derivation* when `N_epi = 0`. Candidate future primitive; not built.

(The editor's given name — **Helen** Lake — is a resonance, not a warrant. Noted, not load-bearing.)

## Laws carried over (not re-derived)
- `N_repr ⊬ N_epi ⊬ W` (epistemic_roots, `3ca3a6d`) = "weighed, not counted."
- hidden-common-ancestor collapse (`~dep`) = stemmatic shared-error reasoning.
- `UNRESOLVED ≠ INDEPENDENT` = a manuscript of unknown filiation is not counted as a fresh witness.

## Mode-route (operator-gated)
None self-promotes. `authority=false`. Sinaiticus stays a TEMPLE-class structural specimen, never a truth/canon claim.
- `BUILD CONJECTURAL_EMENDATION` → type the `N_epi=0`, coherence-warranted case (the one layer this corpus reveals is missing).
- `COMMIT` → this doc is untracked (NO_COMMIT default).

*authority=false · canon=false · corpus WITNESSED (metadata) / NOT_IN_SESSION (text) / REPORTED (transmission) · a reading, not a ruling.*
