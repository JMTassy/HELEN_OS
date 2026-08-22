<!-- authority=false · claim=NO_CLAIM · a reading, not a ruling -->
# MILITARY & SEA DICTIONARY (1711) — CHIDDUSH V0

🔵 OBSERVED · NON_SOVEREIGN · authority=false · canon=FALSE · not admitted · no ledger effect
Provenance chain: **S** (1711 dictionary) → **G** (extracted structure) → **H** (chiddush). H never collapses into S.

## 0. Corpus status — honest

| artifact | status | detail |
|---|---|---|
| `ocr.txt` (archive.org `_djvu.txt` OCR layer) | **DOWNLOADED** | sha256 `2274a7f58683549f14b35b4dd17a4f5cb8c190bf85e39c0355c730a752a70861` · 19,607 lines · 428 KB |
| `source.pdf` (image scan) | **WITNESSED-PARTIAL** | fetch timed out at 15 MB / 139 MB; `file` confirms *PDF v1.5, 330 pages*. Body not fully on disk. |
| `_djvu.xml` · `_hocr.html` · `_chocr.html.gz` · `_scandata.xml` (word-coordinate layers) | **NOT_IN_SESSION** | present in the item manifest, identified, **not** downloaded. Load-bearing for the extraction answer below. |

EPISTEMIC_SYNTAX class of the corpus: **COMMUNICATION_ACT** (a normative reference register), read here as a candidate **LOCAL_OBSERVATION** about coordination language — never CANONICAL_CLAIM.

Full title (WITNESSED, l.44–52): *"A Military and Sea Dictionary … Explaining … Difficult Terms in Martial Discipline, Fortification, and Gunnery, and all Terms of Navigation … The Fourth Edition, Improv'd."*

## 1. What is WITNESSED (grepped, quoted, line-referenced)

All counts are over `ocr.txt`; every figure is reproducible with the greps in §5.

| structural signal | count | witnessed example (line) |
|---|---|---|
| `Vide X` explicit cross-reference edges | **217** | `Ambligon. Vide Triangle` (l.449) · `Army. Vide Camp` (l.689) |
| `To <verb>` action-primitive definitions | **96** | `Advance. To advance, is to move forwards.` (l.392) |
| role / authority terms (Officer, Colonel, Admiral…) | **209** | `Aid de Camp. An Officer always…` (l.382) |
| state/relation copulas (`is a`, `made by`, `us'd by/to`, `serves to`) | **411** | `Carabine. A small Fire Arm … us'd by all the Horse.` |
| column-gutter rule mis-OCR'd as `\|` | **673 lines** | `Horse-Guards. Captain aux Gardes, or \|` (l. body) |

**The load-bearing find is the `Vide` graph.** The dictionary is not a flat list; it prints **217 explicit typed pointer edges** between its own entries (`Angle. Vide Triangle`). The source *self-describes as a reference network* — a K-graph with explicit edges, authored in 1711.

## 2. The deeper chiddush (H) — beyond `m*` and the WUL packet

The relay established the packet `m_ij = (ENTITY, STATE, RELATION, DIRECTION, ACTION, AUTHORITY, PROVENANCE)` and the bottleneck objective `m* = argmin L(m) s.t. ΔS=ΔS*, ΔA≤0, ΔΓ≤ΔΓ_licensed`. The witnessed corpus adds a layer the packet formulation hides:

### I* — invariant across lenses
> **Operational language does not compress the message. It externalizes shared structure into a common reference graph, and the message is short *because the index is shared and authority-neutral*.**

Formally, the object to minimize is not `L(m)` but the **conditional** length:
```
m* = argmin_m  L(m | K_shared)      s.t.  ΔS_j = ΔS*  ∧  ΔA_j ≤ 0  ∧  ΔΓ_j ≤ ΔΓ_licensed
```
`"Vide Guard"` is maximally compressed **only** because sender and receiver hold the *same indexed graph* `K_shared`. The 1711 dictionary **is** that shared `K` — the artifact that makes two-word orders sufficient between officers who never share context. This relocates the optimization: **coordination bandwidth is lowered by growing shared reference structure, not by shortening individual messages.** A short order presupposes a large, identical, pre-loaded index on both ends.

### Two corollaries, each witnessed in S

**C1 — The dictionary is a pure K-graph with `A_E = 0` on every node.**
Knowing the entry for *Admiral* confers no admiralty; the definition is `A_K` (knowledge), the office is `A_E` (authority). The book is a witnessed instance of the session's membrane `A_K ⇏ A_E`: 646… 209 role terms defined, zero authority minted. Reading `emit_admission()`'s definition grants no admission — the 1711 lexicon is the historical proof that **a name is not a grant**.

**C2 — `Vide` is an authority-neutral pointer.**
`Vide Guard` transmits *where to look*, never the referent's power. It moves attention, not authority — exactly the WUL `PROVENANCE`/pointer field carrying `A = 0`. The Latin cross-reference is the 1711 ancestor of a receipt pointer: it licenses navigation, not action.

## 3. The extraction answer (concrete, grounded in the witnessed OCR)

**The question — "what cues isolate headword+definition and prevent cross-column bleed?" — has a geometry answer and a text answer, and the order matters.**

### 3a. Do NOT extract M_k from `_djvu.txt`. It has already lost the geometry.
Witnessed proof of bleed: the linear headword stream reads
`… Ambligon · [Inward] · Appointe · Approaches · [Sappe] · Araignet · Area · Artillery · [Stores] · [Sault] · Ball …`
The bracketed intruders are **second-column fragments** interleaved into the first column's read order by the top-to-bottom linearization. The djvu.txt cannot be de-interleaved reliably because the x-coordinates are gone.

### 3b. Fix bleed at the coordinate layer (fetch `_djvu.xml` or `_hocr.html`).
These carry per-word bounding boxes. Recipe:
1. **Find the gutter x per page:** histogram all word-box x-centres; the low-density **valley** near the page mid-line is the gutter. Cross-check against the mis-OCR'd `|` rule positions (673 witnessed).
2. **Split words into `col_L` (x < gutter)` / `col_R (x ≥ gutter)`.**
3. **Read each column top-to-bottom independently, then concatenate `col_L ++ col_R`.** This is the single step djvu.txt skips.

### 3c. Segment headwords within a clean column (text cues, all witnessed).
- **Headword anchor:** line-initial `^[A-Z][A-Za-z .'\-]+[.,]\s+[A-Z]` starts a definition (`Carabine. A small…`, `Artillery. All sorts…`).
- **Alphabetical-monotonicity VALIDATOR (the key trick):** entries are a-z ordered, so **a detected headword that breaks alphabetical order flags a residual column-bleed misread.** The failure mode and its detector are the *same signal* — no separate QA pass needed.
- **Strip page-boundary noise:** printer's signatures `^[A-Z]\s?[0-9]` (`A 2`, `B 5`, `E 1` — witnessed l.158/2015/886) and foot-of-page **catchwords** (a lone word repeated as the next page's first head).
- **Normalize long-ſ** (`ſ→s`) and the common f/s ligature confusions before regex.
- **Extract `Vide` edges** as `(headword, VIDE, target)` — a free, source-printed relation graph.

### 3d. Then compute M_k.
Per entry, code the binary vector on `{E, R, S, D, C, G, A}`: **R** from `Vide`/copula markers, **C** from `To <verb>`, **A** from role terms, **S** from state copulas. `M_k = (1/N) Σ 1[‖x_i‖₀ ≥ k]`. Report **M_3**.

## 4. Falsification plan — what is proven vs pending

- **PROVEN (WITNESSED, absolute):** the 1711 corpus contains 217 explicit relation edges, 96 action-primitive definitions, 209 role terms — it *does* encode typed transition structure, not only nouns. This is `LOCAL_OBSERVATION`, not proof of authorial intent.
- **PENDING — `INSTRUMENT_UNRESOLVED` (the comparative claim only):** the M_k thesis is *"military dictionary has significantly higher M_3 than a matched general dictionary."* The **control is not fetched.** Until the same pipeline runs on a general 1700s lexicon (e.g. Kersey 1702 / Bailey 1721), the comparison `M_3(military) > M_3(general)` is **UNKNOWN**. Absolute density ≠ relative density; do not launder one into the other (UMS: coverage↑ ⊬ claim↑).
- **Negative-evidence guard:** a low M_3 on the control is informative only if the control's OCR/sampling is matched to the military's — else the gap is an instrument artifact, not a finding.
- **`x*` (next discriminator):** run the §3 pipeline on 100 random entries from each dictionary; the discriminating measurement is ΔM_3. Suspected failure mode: the extractor over-reads ordinary copulas (`is a`) as operational relations → hallucinated R, inflating M_3 on *both* corpora and washing out the contrast. Guard: require R to be a *directional* relation (`Vide`, `commands`, `us'd to`), not the bare copula.

## 5. Reproduce
```
grep -coE '\bVide\b' ocr.txt                         # 217 relation edges
grep -coE '\bTo [a-z]+' ocr.txt                       # 96 action primitives
grep -coiE '\b(Officer|Colonel|Admiral|Captain|General|Lieutenant|Serjeant|Commander)\b' ocr.txt  # 209 roles
grep -oE '^[A-Z][A-Za-z]+[.,] +[A-Z]' ocr.txt | sed 's/[.,].*//'   # headword stream (see the a-z break intruders)
```

## Laws carried over (not re-derived here)
- `A_K ⇏ A_E` — knowledge ⊬ authority (the dictionary is the witnessed instance: definitions, zero grants).
- `descriptive ⊬ constitutive` · `possession ⊬ trust` (ν / WVIS / UMS).
- `coverage↑ ⊬ claim↑` (UMS) — absolute M_k ⊬ comparative M_k.
- `representation ≠ admission · glyph ≠ receipt · Δ_CHIDDUSH ⇏ Δ_KERNEL`.

## Mode-route (operator-gated)
None self-promotes. This is a REVIEWED_CANDIDATE at best; admission belongs to the gates.
- `NEEDS_OPERATOR` verb `FETCH CONTROL` → pull a general 1700s lexicon, run §3, resolve INSTRUMENT_UNRESOLVED.
- `NEEDS_OPERATOR` verb `BUILD EXTRACTOR` → implement §3a–d as a script under `experiments/helen_mvp_kernel/`.
- `NEEDS_OPERATOR` verb `COMMIT` → this doc is untracked (NO_COMMIT default).

*authority=false · canon=false · corpus DOWNLOADED (ocr) / WITNESSED-PARTIAL (pdf) / NOT_IN_SESSION (coord layers) · a reading, not a ruling.*
