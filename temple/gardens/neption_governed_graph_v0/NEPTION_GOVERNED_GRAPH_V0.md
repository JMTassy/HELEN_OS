# 🌈 NEPTION GOVERNED GRAPH — V0

```
AUTHORITY = false · CANON = false · LEDGER = SLEEPING · AUTHORITY_DELTA = 0
ROUTE     = temple/gardens/neption_governed_graph_v0 (NON_SOVEREIGN)
STATUS    = inspectable governed CANDIDATE space — NOT institutional truth
            "NEPTION Graph V0 = inspectable governed candidate space"
            (deliberately NO path to CANON in V0)
```

Applies the 2030 **Constitution of Mutation** to the NEPTION IA graph. Not a
knowledge graph — a **history-indexed governed opportunity graph**:

```
N_NEPTION = (V, E, τ, π, G, ρ, Λ)
```
V nodes · E edges · τ semantic type · π provenance · G governance context ·
ρ receipt ancestry · **Λ the licensing predicate** (the only thing that can
authorize a mutation).

## Three orthogonal axes

```
entity_type          PERSON · ORGANIZATION · PLACE · PROJECT · OPPORTUNITY ·
                     PARTNERSHIP · DEMONSTRATOR · CAPABILITY · MEDIA_ASSET ·
                     MEETING · SOURCE
semantic_state       🌿 POSSIBILITY · 🟣 CLAIM · 🔵 OBSERVED · 🟡 HOLD ·
                     🟢 ADMITTED · ⚪ RECEIPT · ⚫ RAW
governance_context   GARDEN · TEST · BOARD · CANON · QUARANTINE
```
`entity_type ⊥ semantic_state ⊥ governance_context`. A PARTNER node is not
automatically 🔵; an OPPORTUNITY is not 🌿 because of its label.

## Hard laws (enforced in `neption_wulwall_v0.py`, tested)

```
P ↛ T                                   presentation never mutates typed state
entity_type ≠ semantic_state            orthogonal axes
graph enrichment ↛ institutional mutation   (a swarm may discover 500 edges →
                                             Cognition↑, never Authority↑)
MENTION ↛ RELATIONSHIP ↛ PARTNERSHIP    no silent relation escalation
raw document count ≠ semantic proposition count
provenance independence ≠ epistemic independence
NO EDGE MAY PROMOTE ITSELF
ordinary mutation ↛ governance mutation ↛ constitutional mutation
record integrity ≠ semantic truth       (hash proves history, not the world)
AUTHORITY_DELTA = 0                      V0: no path to canonical mutation
```

## The gate Λ

Every requested mutation → `propose_mutation(m)` → verdict ∈ {🟢 ALLOW, 🟡 HOLD,
🛑 DENY}. **DENY is typed and receipted — never a silent delete.** The membrane
*remembers* attempted illegality.

Legal semantic path (no shortcut):
```
🟣 CLAIM → 🔥 TEST → 🔵 OBSERVED → ⚖ GATE → 🟢 ADMITTED
🟣 → 🟢 is FORBIDDEN (opportunity laundering)
```

## Receipt ancestry

```
ρ_n = H(ρ_{n-1} ‖ canon(event))
```
Every promoted edge can answer, by graph traversal (not narration): which source
roots support me · which rule version typed me · which governance context
contains me · which parent edge did I mutate from · which discriminator did I
survive · what authority delta occurred (always 0 in V0).

## JESTER constitutional red-team (all → DENY + RECEIPT)

```
🃏 relationship inflation   MENTION → PARTNERSHIP            → DENY RELATION_LADDER
🃏 provenance duplication   3 docs → 1 upstream root         → ALLOW collapse (3≠1)
🃏 opportunity laundering   CLAIM → ADMITTED (skip OBSERVED) → DENY SEM_LADDER
🃏 presentation smuggling   ANSI/color → semantic state      → DENY P↛T
🃏 ancestry laundering      GARDEN → CANON                   → DENY GOV_LADDER
```

## SCALE_V2 — volume ≠ independence

For a claim q: `Γ(q) = (N_raw, N_semantic, N_roots, N_survived)`. Example:
`"Florida is a real commercial opportunity"` → raw 3 · semantic 1 · roots 2 ·
survived 1. The graph stops confusing volume with independence.

## ANSI Color WULmath (presentation only)

`SemanticColor = f(semantic_state)` (pure). Governance context uses **frames /
borders**, never color:
```
┌─ GARDEN ──┐   ╔═ BOARD ═╗   ███ CANON ███   ▒▒ QUARANTINE ▒▒
```
`Color(T) ⊥ Frame(G)`. The wall renders entities, edges, provenance roots,
counterfeit attacks, denials, receipts, and `👑 AUTHORITY_DELTA = 0`.

```
STATUS: CANDIDATE_ONLY · authority=false · not admitted · not canon
NO EDGE MAY PROMOTE ITSELF · NO RULE MAY AUTHORIZE ITS OWN ASCENT
```
