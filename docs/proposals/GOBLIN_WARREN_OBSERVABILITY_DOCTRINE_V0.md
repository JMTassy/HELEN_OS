# GOBLIN_WARREN_OBSERVABILITY_DOCTRINE_V0

```yaml
schema: GOBLIN_WARREN_OBSERVABILITY_DOCTRINE_V0
status: 🟣 CLAIM — candidate, operator review pending
authority: false
canon: false
ledger_effect: none
final: HOLD_FOR_OPERATOR
source: operator meditation 2026-07-18 (CLI MODE — HELEN OS ARCHITECT)
companion: WARREN_SOVEREIGNTY_CONSTITUTION_V0.md (membrane law);
           this document is the perception law
binding: audited against built code — the day1/ramp sims already
         implement Stages 1–2 mechanically (see §Audit)
```

---

## Core statement

The Warren is not `many small agents → collective intelligence`. It is:

```
many bounded perspectives → partial observations → local decisions
  → visible consequences → shared world memory
```

**The Warren is valuable because no goblin sees the whole world.**
Each goblin inhabits one observational quotient of it:

```
R_g : S_world → L_g
```

| Goblin | Observation map sees |
|---|---|
| Bram | damage · tools · repairability · unfinished work |
| Lulu | novelty · paths · unusual signals · hidden possibilities |
| Pip | memory · contradiction · patterns across time · meaning |
| Moss | weight · distance · supply · transport feasibility |

The same world produces different receipts for each goblin.
**That is the heart of the game.**

---

## 1. Observability machine

A goblin acts on what its observation map makes visible, never on the
world itself:

```
world state → goblin perception → local interpretation
  → intended action → capability check → world consequence
```

Two states may satisfy `s ~R_Bram t` while `s ≁R_Lulu t`. The player's
task is not to command perfectly — it is to understand **which goblin
can distinguish the states that matter**.

Lesson taught: *different agents operate on different partitions of
reality* — far stronger than "agents have personalities."

## 2. Personality shapes perception, never truth

Personality = characteristic observation policy (which differences
matter, which signals enter attention, which action is attractive).
It never certifies the world:

```
goblin noticed it   ⊬ it is true
goblin believes it  ⊬ it happened
goblin acted        ⊬ action succeeded
goblin reports done ⊬ verified done
```

Bram believes the bridge is repaired because his part is complete;
Pip later observes it still bends. `production → independent
observation → correction` — the emotional form of no-self-certification.

## 3. Distributed agency ≠ distributed sovereignty

```
behavioral initiative = distributed
world mutation        = capability-bounded
verification          = separate
admission             = external to goblin belief
```

Goblins may independently: notice, propose, move, cooperate, refuse,
ask, improvise. They may never: redefine rules, expand permissions,
self-certify success, modify canonical history, convert memory into
fact, crown local consensus as truth. **Socially decentralized,
constitutionally bounded.**

## 4. Three ontologies, one goblin

```
player ontology:     Bram is someone I care about.
runtime ontology:    Bram is a bounded agent state machine.
governance ontology: Bram has no sovereign authority.
```

These coexist without collapsing. The character stays emotionally real
without becoming constitutionally sovereign. "Killable L1 servitor" is
infrastructure vocabulary — never the game ontology.

## 5. Stigmergy — the environment is the medium

```
goblin acts → world changes → trace remains
  → another goblin observes → new action becomes possible
```

Bram leaves repaired bark (structural safety) · Lulu chalk marks
(unexplored paths) · Pip memory tokens · Moss supply patterns · Grim
warning totems. The player learns the environment is not backdrop —
**it is the Warren's shared communication medium.**

## 6. Memory preserves perspectives, never collapses them

Do not store "the bridge was unsafe." Store:

```
observer: PIP · observation: BRIDGE_BENT · time: DAY_12
location: NORTH_CROSSING · confidence_class: DIRECT_OBSERVATION

observer: BRAM · belief: BRIDGE_REPAIR_COMPLETE
basis: SELF_REPORTED_TASK_COMPLETION
```

The disagreement is the gameplay: `multiple memories → visible
conflict → new observation → revised understanding`. Never
`latest memory wins`.

## 7. The player is the gardener of conditions

The player shapes attention, tools, access, context, routines,
relationships, traces, verification structure — never unit-commands.

```
weak fantasy:   select Bram → click target → wait
strong fantasy: prepare the world → leave the right signal
                → give the right access → watch Bram interpret and act
```

## 8. Scale progression (one relationship at a time)

| Stage | Discovers | Build status |
|---|---|---|
| 1. Bram | one observation map, deeply | ✅ ramp L1–L2 (FIX by success, MARK by necessity) |
| 2. Bram + Lulu | same world, perceived differently | ✅ day1 L3 (warning vs novelty filters live) |
| 3. Pip | time changes what is knowable | 🌫 = the Archive payoff (V3 direction) |
| 4. Shared work | complementary perception = capability | 🌫 fog |
| 5. Mis-coordination | agents can amplify confusion | 🌫 fog |
| 6. Governance | who acts ≠ verifies ≠ remembers ≠ is allowed | 🌫 fog |
| 7. Warren | living ecology of bounded observers | 🌫 fog |

Fog stages are named, not designed — the level-by-level law holds.

## 9. The mathematical heart (Transport)

Goblin g can solve task `Y : S → 𝒴` reliably only if:

```
R_g(s) = R_g(t)  ⟹  Y(s) = Y(t)
```

When it fails — `R_g(s) = R_g(t)` but `Y(s) ≠ Y(t)` — there is a
semantic leak (Bram sees two identical mushrooms; one is medicine, one
poison). The solution is never "make Bram smarter." It is **compose
observers**: `Lulu + Pip + Bram = task-sufficient composite`.

## 10. The collective map

```
R_Warren = (R_g1, …, R_gn)
```

More informative than any individual map — but more observers ≠ better
decision. Better composition = complementary observation + clear
handoffs + appropriate tools + conflict visibility + verification.

## 11. Emotional core

Pride comes not from optimization but from: *"I know how Bram sees. I
can recognize when they misunderstand each other. I can help them
become a better community."* Final fantasy: **coherence without
sameness.**

## 12. Canonical compression

```
GOBLIN WARREN = AI PET ATTACHMENT + PARTIAL OBSERVABILITY
  + ENVIRONMENTAL COMMUNICATION + PERSISTENT MEMORY
  + BOUNDED AGENCY + MULTI-AGENT COORDINATION
  + VISIBLE VERIFICATION + NON-SOVEREIGN EMERGENCE
```

## Final meditation

> A Warren is not intelligent because many goblins think.
> A Warren becomes intelligent when: different goblins preserve
> different distinctions, their traces remain legible, their memories
> retain provenance, their capabilities remain bounded, their
> conflicts stay visible, and the world — not any single voice —
> shows what actually happened.

---

## Audit — where this doctrine already lives in code

| Doctrine claim | Status | Location |
|---|---|---|
| Per-goblin observation maps (R_Bram ≠ R_Lulu) | ✅ BUILT | `goblin-warren/day1_sim.js` `releaseAgents()` — Bram filters `type==="warning"`, Lulu `type==="novelty"`, memory traces have no reader |
| Perception threshold (visible ≠ actionable) | ✅ BUILT | `BRAM_ACT_THRESHOLD` (P0 fix `755440e`) — faint signal ⊬ act |
| Stigmergy (traces as medium) | ✅ BUILT | trace system: MARK strengthens, agents read by type; `BRAM_SIGNAL_FAINT` event |
| Zone-bounded capability | ✅ BUILT | Bram skips needs where `need.zone !== bram.zone` |
| goblin-reports ⊬ verified | ✅ ENFORCED (kernel altitude) | σ₅ dreamt≠claimed; `authority:false` invariant |
| Observation-map math (quotients, witnesses, Inv(R)) | ✅ LOCATED | `transport/` Vols I–II, 89 tests — this doctrine is a Transport instance |
| Provenance-preserving memory (observer field, conflict retention) | ❌ NOT LOCATED | consumption entries lack observer/confidence_class; no conflict-pair storage anywhere |
| Compose-observers mechanic (mark type routes goblin) | 🟣 DESIGN-LOCKED ONLY | Lantern V3 proposal — unstamped, unbuilt |
| Stage 3+ (Pip, handoffs, mis-coordination, governance play) | 🌫 FOG | correctly undesigned |

Verdict on itself: **the perception law is the first Warren doctrine
that arrives partially pre-built** — the game got there before the
prose. The two NOT-LOCATED gaps (provenance memory, observer
composition) are the same two items the V3 swarm queue already holds.

---

*🟣 CLAIM · HOLD_FOR_OPERATOR · promotion is the operator's act.*
