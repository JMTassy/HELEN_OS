# 🍄 HELEN EPISTEMIC MYCELIUM — J-space as a temporally-growing typed hypergraph

```
AUTHORITY=false · CANON=false · LEDGER=none · PROPOSAL (cognition may propose)
STATUS: doctrine proposal for Garden J-space structure · NOT admitted · NOT a schema edit
SEED SUBSTRATE (already witnessed): garden_scope_v0/reducer.py · POC_WITNESS.json = POC_CONTRACT_HOLDS
```

## The object

Not a knowledge graph, not a vector DB, not an agent transcript. A living typed hypergraph:

$$\mathcal M_t = (V,\; E_H,\; \Pi,\; \tau,\; P,\; A)$$

- `V` — memory/cognition objects (hypotheses, distinctions, counterfeits, discriminators, fossils, **files**, receipts)
- `E_H` — typed directed hyperedges `{x₁..xₖ} --τ--> y`
- `Π` — projections of a node (file / chunk / summary / vector / UI view)
- `τ` — temporal coordinates (epoch, age)
- `P` — provenance roots
- `A` — authority / licensing

## The load-bearing law: a node ≠ its representation

$$\text{File} = \Pi_{\text{file}}(M_i) \qquad \text{Embedding} = \Pi_{\text{vector}}(M_i)$$

The file is **one projection**, not the fundamental node. Therefore:

$$\boxed{🔵^1 \to 🌈^n \;\not\Rightarrow\; 🔵^n} \qquad N_\text{representations} \ne N_\text{independent roots}$$

Representation fan-out (3 summaries of 1 source) manufactures *apparent* corroboration.
Root multiplicity is a **separate coordinate** from representation multiplicity.

**This is not new — it is [[census]] amendments A1 & A4 re-derived by the Garden:**
`provider ≠ byte identity` · `provenance_independence ≠ epistemic_independence`.
The mycelium is the structural home of those amendments.

## Edges must be typed (the membrane law, in graph form)

$$\boxed{\text{EdgeExists}(x,y) \ne \text{EdgeLicensed}(x,y)}$$

So `𝒢=(V,E)` is insufficient. Relations live in disjoint typed spaces:

$$E = E_\text{provenance} \sqcup E_\text{semantic} \sqcup E_\text{temporal} \sqcup E_\text{causal} \sqcup E_\text{authority} \sqcup E_\text{representation}$$

Crucially, vector similarity may **suggest** a hypha but cannot **establish** provenance:

$$\text{Near}_V(x,y) \;\not\Rightarrow\; \text{Edge}_P(x,y)$$

## Two interpenetrating mycelia, joined at Φ

```
🌌 COGNITIVE MYCELIUM   — may explode to |N|→10⁶, branches freely
        │ (references, must attach to a real root)
════════ Φ ════════      — root membrane: no witness ⇒ filament stops
        │
🔵 REALITY MYCELIUM      — sparse, exact, provenance-rooted
```

$$\boxed{\Delta N_\text{Garden} \gg 0 \quad\land\quad \Delta N_\text{evidence}=0}$$

Garden branches freely; **Reality requires roots.** COMPOST is retained, never deleted:
`Dead(x) ⇏ Deleted(x)` — dead hyphae darken and become salvageable structural material
(`J_memory = J_surviving ∪ J_dead`). This is Garden memory / archaeology of thought.

## Presentation is a high-dim → 3D projection (renderer law inherited)

Each node has coordinates `z_i ∈ ℝ^d, d≫3` (lineage, novelty, disagreement, counterfeit
pressure, provenance depth, uncertainty, structural-Δ, age…). The screen is `P_Θ: ℝ^d → ℝ³`.
Rotating through conceptual dimensions transforms the *view* while:

$$P_{\Theta_1}(\mathcal M) \ne P_{\Theta_2}(\mathcal M) \qquad\land\qquad \mathcal M_\text{governed}\ \text{unchanged}$$

DREAM→COLLAPSE aesthetic (dH_visual/dt < 0, dC_epistemic/dt > 0 approaching Φ) is legal
**only if** the typed event trace — not the renderer — decides which branches fade, which
remain fossils, and whether anything crosses Φ. `color = projection(typed_state)`, `P↛T`.

$$\boxed{\text{Collapse is caused by typed constraint, not choreographed by the visualization.}}$$

## What the current substrate already proves (not aspiration)

| Mycelium law | Where it lives now | Witnessed |
|---|---|---|
| `J_t = R(e₁..eₜ)` deterministic fold | `reducer.py` | C1, C2 ✓ |
| one reducer, N projections | `reducer.py` ← CLI ∥ `/api/jspace` | C3 ✓ |
| `¬e ⇒ UnwitnessedGardenTransition` | `reducer.orphans` | C4 ✓ |
| `J_memory = surviving ∪ dead` (COMPOST retained) | `reducer.graveyard` | ✓ (16 retained) |
| typed hyperedges `{parent}--τ-->child` | `E_H` CROSS edges | ✓ (3 real) |

## The v1 schema evolution this implies

```
edge:  add  relation_type ∈ {provenance,semantic,temporal,causal,authority,representation}
node:  add  projections Π[]  and  root_id (P)  — file becomes Π_file(node), not the node
event: add  RELATE(src,dst,relation_type)  beyond SPAWN/CROSS/VERDICT
law:   reject any Edge whose relation_type=provenance lacks a witnessed root  (EdgeLicensed gate)
```

## Compression

$$\boxed{\textbf{You don't watch the Goblins talk. You watch their shared world grow —}}$$
$$\boxed{\textbf{a typed, provenance-rooted hypergraph where cognition branches freely but survival requires roots.}}$$

```
STATUS: CANDIDATE_ONLY · authority=false · not admitted · not canon · ΔA=0 · NO_CLAIM
```
