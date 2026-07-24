# HELEN OS — ZONE ARCHITECTURE + GARDEN SWARM V1

```
authority: NONE · claim_status: NO_CLAIM · status: 🟣 CLAIM
source: Fable_helen vision · executed: claude-sonnet-4-6
grounded_on: GARDEN_NO_CLAIM_RULE_V0.md · NEVER_ENDING_GARDEN_ZONE_V0.md · DREAMT ≠ CLAIMED law
```

---

## 1. Zone Map

| Zone | Name | Who lives there | Can happen | Cannot happen |
|---|---|---|---|---|
| **Z1** | KERNEL (castle tower) | JM + reducer only | Receipted admission, replay, seal | Any agent write. Ever. |
| **Z2** | GARDEN (quantum bloom) | GOBLIN-*, HER, HAL, MAYOR-SHADOW, all NPCs | Continuous generation, merging, decay — 24/7, JM absent | Claims, receipts, kernel reads, ledger writes, self-promotion |
| **Z3** | TEMPLE (bridge) | Collapsed candidates only, frozen | Proposal storage, MAYOR validation, operator review | Mutation after entry; entry without a collapse receipt |

**Membrane law:** Z2→Z3 requires JM's collapse act. Z3→Z1 requires the existing 7-gate admission pipeline. Z2 never sees Z1. The blindness protocol extends spatially: **zones are blind upward**.

---

## 2. Garden NPC Roster (always running)

| NPC | Ingests | Emits per cycle | Directory |
|---|---|---|---|
| GOBLIN-ARXIV | daily arxiv RSS (allowlisted cats) | 1–3 DreamSeeds | `swarm/goblin_arxiv/` |
| GOBLIN-AGORA | X/Twitter saved posts export | 1–3 DreamSeeds (chiddush-tagged) | `swarm/goblin_agora/` |
| GOBLIN-POSTMASTER | JM's email digest (read-only, redacted) | 1–2 pattern DreamSeeds | `swarm/goblin_postmaster/` |
| GOBLIN-COMPOST | decayed blooms (hashes only) | 0–1 mutation DreamSeed | `swarm/goblin_compost/` |
| HER | live DreamSeed pool | InsightCandidates (5-blocks) | `swarm/her/` |
| HAL | InsightCandidate pool | ClaimCandidates (10-blocks), evidence-bound | `swarm/hal/` |
| MAYOR-SHADOW | ClaimCandidate pool | ranked shortlist + objection notes — **advisory only, never a verdict** | `swarm/mayor_shadow/` |

Each NPC writes NDJSON to its directory. Artifacts are hashed but unchained (not ledger-linked).

---

## 3. Lego Block Taxonomy

```
1-piece  =  DreamSeed          one NPC, one signal, one source hash. NO_CLAIM.
5-piece  =  InsightCandidate   HER fuses 3–5 seeds sharing a motif. parent hashes required. NO_CLAIM.
10-piece =  ClaimCandidate     HAL binds 2+ Insights to verifiable evidence. Blindness holds.
────────────────────────────────────────────────────────────────────────────────────────
Temple Proposal  =  ClaimCandidate frozen by JM's collapse act. Hashed. MAYOR-validated.
Kernel Receipt   =  Existing 7-gate admission pipeline. Unchanged.
```

**Recursion:** composted and surviving blocks re-enter the seed pool as raw material. The tower is built only from blocks whose parent hashes trace to sources. Rejected ClaimCandidates and HOLD verdicts re-enter GOBLIN-COMPOST as mutation seeds — the swarm learns from what was rejected.

---

## 4. The Daily Garden Cycle (JM away)

Every 24h, `garden_tick` runs:

```
1. GOBLINs ingest → new DreamSeeds registered in garden_state.json
2. HER fusion pass → fuse 3–5 seeds sharing motifs → InsightCandidates
3. HAL binding pass → bind 2+ insights to evidence → ClaimCandidates
4. MAYOR-SHADOW re-rank → advisory shortlist, objection notes
5. GOBLIN-COMPOST pass → decayed block hashes → mutation DreamSeeds
6. Compost sweep → artifacts at cycle_age >= 7 → composted (content withdrawn, hash retained)
7. Emit GARDEN_DAWN_REPORT → one markdown page
```

JM returns to **one page**: N seeds bloomed, M insights fused, K claims candidate, shortlist top-5, compost obituary.

---

## 5. The Collapse Moment

JM reads the Dawn Report and runs:

```bash
python temple/gardens/swarm/garden_collapse.py <block_hash>
```

This:
1. Freezes the block and its full ancestry chain in `garden_state.json`
2. Emits a `COLLAPSE_RECEIPT_V1` (authority=false — this is non-sovereign)
3. Copies the frozen block to `temple/proposals/`
4. JM manually runs `helen_say` to produce the actual ledger entry (JM's act, not the garden's)

All sibling possibilities remain in superposition — uncollapsed, decaying, recombinable. **Collapse selects; it never deletes.**

---

## 6. The New Invariant (absent from all prior HELEN OS docs)

> **EVERY BLOOM DECAYS: a garden artifact not collapsed within 7 cycles is composted — content withdrawn from agent view, hash retained forever — so the garden selects by survival, never by accumulation.**

Without decay, the bloom space becomes a landfill and the swarm optimizes for volume.  
With decay, only ideas strong enough to be re-dreamt, re-fused, or collapsed persist.  
The ledger remembers everything; the garden forgets almost everything.  
That asymmetry is the wall between castle and field.

---

## Relationship to Existing Docs

| Doc | Status | Relationship |
|---|---|---|
| `GARDEN_NO_CLAIM_RULE_V0.md` | Active | Zone Z2 safety law — unchanged, extended here |
| `NEVER_ENDING_GARDEN_ZONE_V0.md` | Active | Growth engine foundation — the swarm is its implementation |
| DREAMT ≠ CLAIMED | Active | Garden law — COLLAPSE is the collapse of quantum state |
| Superteam Egregor MVP V0 | Active | Schemas (DreamSeed/InsightCandidate/ClaimCandidate) used here |
| Sovereign promotion pipeline | Unchanged | Z3→Z1 path, not touched by garden |
