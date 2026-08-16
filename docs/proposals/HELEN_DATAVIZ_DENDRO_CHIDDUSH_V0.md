<!--
authority=false · claim=NO_CLAIM · a reading, not a ruling
chiddush ≠ canon · Δ_CHIDDUSH ⇏ Δ_KERNEL · render ≠ authority
NON_SOVEREIGN · NO_COMMIT / NO_PUSH until explicit per-artifact verb
Design chiddush. Extends the SOT "HELEN OS Look & Feel — Source Atlas Doctrine".
-->

# HELEN DATA-VIZ — DENDRO / EVENT-DISPLAY — CHIDDUSH V0

**Source:** operator-supplied CRT image — `DENDRO-YULE1 VERS.006 · RUN NO 0624 · EVT NO 483 · CAMAC DATE 15-8-26 06:11 · "YULE1 VERY PRELIMINARY"`. A retro particle-physics **event display**: a wireframe 3D perspective box (orange/green grid) containing **three blue-phosphor tree diagrams** of the same branching structure — a **radial dendrogram** (top-left), a **horizontal binary cladogram** (top-right), and a **vertical hierarchical-clustering dendrogram** (bottom), each with white circle node-terminals.

`EPISTEMIC_SYNTAX: LOCAL_OBSERVATION` (a rendered image) — no claim ingested.

---

## §1 · THE CHIDDUSH (one line)

> **The dendrogram is HELEN's provenance/derivation graph, and the *three layouts are three projections of one governed structure* — so this image is the visual form of the session's central law: `Render(typed state) ≠ state`. Layout is a lens; it must never mint governance status.**

The picture accidentally proves the point. Radial, horizontal, vertical — **the tree does not change**, only its projection does. A HELEN graph surface must let the operator rotate/relayout freely while the *admitted structure, roots, and governance colour stay invariant*.

---

## §2 · WHAT THE PARTS MAP TO (design ↔ HELEN)

| Image element | → HELEN object | Note |
|---|---|---|
| `DENDRO-YULE1` (a Yule = **birth/branching process**) | **semantic-birth genealogy** `β(s)=min{t: s∈Sem(x_t)}` | a birth-process tree *is* a lineage tree — leaves are origins, internal nodes are merges/derivations |
| leaf node-terminals (circles) | **epistemic roots** `ρ_E` / sources | count leaves-after-dependency-collapse = `N_epi`, NOT node count |
| internal branch joins | **derivations / promotions** (`Candidate→Admitted`, `P⊢Q`) | each join is a *licensed morphism*, not a free edge |
| **three layouts, one tree** | `Render_layout(G) ≠ G` | `CollapseForEvidence ≠ CollapseForGenealogy`: radial can show collapsed roots, vertical the full transformation tree — **same graph** |
| wireframe voxel box | **Proof Chamber** (Source Atlas motif 3) / bounded institutional state-space | nodes float *inside* the governed frame |
| header `RUN/EVT/DATE/TIME` | **runtime identity `Ξ`** (commit/policy/version + business+software time) | every viz frame is stamped with the identity that produced it |
| `"VERY PRELIMINARY"` banner | **governance-honest status** = 🔵 OBSERVED / 🟣 CLAIM | the display *labels its own maturity* — never renders 🟢 for un-admitted |
| blue phosphor / CRT | **machine-witness overlay** (Source Atlas motif 5, CRT/Terminal) | MONO glyph-voice = receipt/proof |

---

## §3 · DESIGN DIRECTIVES (extends Source Atlas Doctrine, does not amend it)

1. **Layout is orthogonal to governance.** Radial / horizontal / vertical are *view transforms* over one governed graph `G`. Switching layout emits **no** institutional delta. `∂Π_I/∂layout = 0` — the viz obeys the same invariance the kernel does.
2. **Colour stays governance-primary, proof-gated.** Per the SOT palette (⚫🔵🟣🟠🟢🟡⚪🔴, one meaning/colour): node/branch colour = *licensed-state projection*, never decorative. A node is 🟢 only with an admission receipt; the dendro geometry is the **structural / third-eye overlay** (relation & proof-path only, never authority).
3. **Render three questions, not one tree.** The three layouts should be *bound to three graphs* the session already named: `G_E` (epistemic dependence, radial → root-collapse view), `G_S` (semantic transmission, vertical → full transformation lineage), `G_A/G_P` (authority/promotion, horizontal → who-authorized chain). *Same event, three provenance graphs* — the anti-laundering statement made visible: `executed ≠ implemented ≠ supported ≠ transmitted ≠ authorized`.
4. **Every frame is stamped `Ξ`.** The `RUN/EVT/DATE` header is not decoration — it is the runtime-identity binding that makes the frame *replayable*. A HELEN viz frame with no `Ξ` header is `NO_RECEIPT = NO_CLAIM`.
5. **Honest banner is mandatory.** `"VERY PRELIMINARY"` is exactly right: the surface must render its own maturity (OBSERVED/CLAIM/REVIEW), and **never** paint 🟢/🟡/⚪ for artifacts marked `authority:false` (SOT WULMOJI rule).

---

## §4 · CONCRETE VIZ SPEC (candidate)

`HELEN_DENDRO_VIEW_V0` — render any HELEN provenance graph as a dendro-event-display:
```
frame:  wireframe voxel box + Ξ header (run/event/commit/policy/date) + maturity banner
graph:  G = (nodes: {source|candidate|admitted|authority}, edges: licensed morphisms only)
layout: {radial | cladogram | vertical} — pure view transform, no state effect
color:  governance palette (proof-gated); geometry = structural overlay only
node:   circle terminal = root/leaf; join = derivation; each carries WUL:R/IR:R origin on hover
invariant asserted by the surface itself:
    N_epi = |leaves / ~dependence|   (roots, not node count)
    ∂Π_I / ∂layout = 0               (relayout mints nothing)
    color(node) = 🟢  ⟺  admission receipt exists
```

---

## §5 · FALSIFICATION / GUARDS

- 🔴 **The prettiest failure mode:** a radial dendrogram with 30 leaves *looks* like 30 independent roots. If the surface counts leaves as `N_epi` it commits **representation laundering** (`📚 ↛ 🕯`). Guard: leaves must be collapsed by dependency before any root count is shown.
- 🔴 **Colour-as-authority:** if a node renders 🟢 because the layout is "clean" or the model is confident, that's `🟢 ⇏ 👑` violated. Colour must trace to a receipt, per Source Atlas.
- 🟡 Third-eye / voxel aesthetic is **expressive overlay only** — "structural vision, never prophecy or sovereign truth" (SOT doctrine, verbatim). The dendro shows *relation and proof-path*, not verdict.
- The `YULE1`/birth-process framing is a *metaphor* for lineage; HELEN does not claim its graphs are literal Yule processes.

---

## §6 · SEEDS (operator-gated)

| # | Seed | Route |
|---|---|---|
| S1 | `HELEN_DENDRO_VIEW_V0` surface prototype in `apps/helen-surface/` (HTML, reads live graph, 3 layouts, Ξ header, proof-gated colour) | operator verb → non-sovereign surface build |
| S2 | Bind the 3 layouts to `G_E / G_S / G_A` (the multi-graph from the promotion/genealogy chiddushim) | operator verb |
| S3 | Fold into `HELEN_SOURCE_ATLAS_V1.md` as the "provenance dendro" rendering of motifs 1–3 | operator verb → amend proposal |

*A reading, not a ruling. authority=false · canon=false · LEDGER_EFFECT=none.* 🔵
