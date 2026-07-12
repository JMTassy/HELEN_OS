# WARREN LEVEL ATLAS — six stages, three laws, one loop

```yaml
artifact:   WARREN_LEVEL_ATLAS_V1
derives:    WARREN_COMPOST_CALCULUS_V1 (laws) + THEOREM_PHI_CONTRACTION_FLOOR_V1
stages:     6 operator-supplied scene renders (hash-pinned in assets/)
authority:  false · canon: false · NO_CLAIM · playable-sandbox law applies
loop:       /loop deeper-gameplay iteration 1
```

## Design thesis

The storyboard already teaches three lessons (prompting / evidence /
WULmath). The calculus already proves three laws (callback / compost /
backed ZOL). **A level = one place where one law becomes playable.**
Deeper gameplay is not more content — it is the same law at higher stakes.

## The world graph

```
                    [L0 GARDEN]  day/night pair — home base
                         │
                 [L1 GATE HUB]  root-arch portal + pool — level select
                    │        │
        [L2 BRIDGE STREAM]  [L3 STONE CIRCLE]
             │                    │
             └────► [L4 VILLAGE CROSS] ◄────┘
                          │
                   (L5 — future: under the pool)
```

## Level cards

### L0 — THE GARDEN (home base) · `warren_scene_{night,day}_garden_v1`
- **Teaches:** the main loop (observe → touch → signal → propose → choose).
- **Mechanic:** deposit traces; watch salience fade *toward* — never to —
  the floor. Status board shows the plateau (≈ ⅛ of peak) so the player
  *discovers* the Unforgetting.
- **Law on stage:** the flow itself. Day = verbs fire, night = flow runs.
- **Win condition:** none. Home has no fail state.

### L1 — MYCELIAL GATE HUB (level select) · `warren_scene_gate_hub_v1`
- **Teaches:** navigation + the replay strip. The pool under the root arch
  shows a swirl of PAST traces (the timeline made visible).
- **Mechanic:** each doorway lights only when its entry condition is met
  (spiral path-marks = breadcrumbs of prior choices). Touching the pool
  replays any past event — Law 1 makes this ALWAYS possible: every trace
  retains ≥ c_φ salience, so no door ever rusts shut.
- **Gate rule (new, from Law 1):** a level door requires salience of its
  key-memory ≥ θ. Since σ(∞) = ℓ₀ + c_φ·w₀, a door stays open forever iff
  the player composted enough lesson into its key-memory: ℓ₀ ≥ θ − c_φ·w₀.
  *Doors are opened by learning, and learning never expires.*

### L2 — BRIDGE STREAM (Gerald's bridge) · `warren_scene_bridge_stream_v1`
- **Teaches:** the storyboard's Lesson 1 — better prompt = objective +
  context + constraints + success test.
- **Mechanic:** the player writes the bridge-instruction; goblin telephone
  mutates it; the bridge BUILDS ITSELF from whatever survived the mutation.
  Missing constraint → visibly wrong bridge (sunset-colored fridge tier).
  The crystal stream carries away un-specified details — visual metaphor
  for detail decay; what was composted into the prompt (lesson mass) is
  what the bridge keeps.
- **Law on stage:** Law 3 economics — ZOL minted only for the detail the
  player successfully converts into constraint-lessons. κ ≤ 1−ρ enforced:
  you cannot mint more understanding than detail you actually processed.
- **Stakes ramp (deeper mode):** same bridge, three tiers — plank (1
  constraint), arch (3 constraints + test), keystone (constraints + test +
  a *counterexample* the player must supply). Tier 3 is the Forge's
  falsifier discipline as gameplay.

### L3 — STONE CIRCLE (the Ogham Tribunal) · `warren_scene_stone_circle_v1`
- **Teaches:** Lesson 2 — evidence or mushroom; confidence ≠ correctness.
- **Mechanic:** claims are carved on the dolmen bench (the ogham strokes
  ARE the tally). Player sorts: BELIEVE / TEST / COMPOST. Tested claims
  earn tally-strokes; composted claims fertilize the ring mushrooms
  (visible Law 2: the circle only cleans itself when goblins compost —
  toxic claims left alone plateau at ⅛ glow and keep whispering).
- **Law on stage:** Law 2 (compost necessity) + the evidence ladder from
  the Theorem Forge, child-shaped: Tier I = carved in stone, Tier II =
  chalk on stone (testable, washable), Tier III = spoken only.
- **Deeper mode:** a claim the player BELIEVED earlier returns as a
  witness in a later trial (Law 1 callback — the circle remembers what
  you didn't test).

### L4 — VILLAGE CROSS (the market of lessons) · `warren_scene_village_cross_v1`
- **Teaches:** Lesson 3 economics — the ZOL loop closed.
- **Mechanic:** goblins trade berries (details) for preserved goods
  (lessons). The market ONLY accepts compost-backed ZOL — the druids at
  the cross audit the wallet against the compost ledger (Law 3's backing
  bound as an NPC ritual). Counterfeit test: any offer where minted ZOL >
  λ × composted detail is refused by the druid with the actual inequality
  shown, goblin-style.
- **Deeper mode:** market prices drift with garden toxicity (uncleaned
  residue taxes trade) — closing the loop back to L3's compost duty.

### L5 — UNDER THE POOL (reserved)
The gate-hub pool swirls with galaxy light. One day: descend into the
replay itself — a level made of the player's own past traces at floor
salience. Requires nothing new mathematically; it is Law 1 as a place.
NOT designed yet. Reserved marker only.

## Progression law (the atlas in one line)

    L0 shows the flow · L1 proves doors never rust · L2 mints by learning
    L3 makes testing sacred · L4 audits the wallet · L5 is memory itself

## Session pacing (fits the 0–120s first-arc contract)

First session touches L0 only. L1 unlocks on first compost. L2–L4 are
one-lesson visits (< 3 min each, per success criteria). Deeper modes are
replay-unlocked — the same stage, higher tier, per the design thesis.

## Honest boundaries

Playable sandbox only. NO CLAIM · NO SHIP · NO ADMISSION · NO LEDGER
EFFECT. The druids audit game-ZOL, not real value. localStorage ≠ ledger.

## Asset registry (all hash-pinned in assets/)

| Stage | File | sha256 (16) |
|---|---|---|
| L0 night | warren_scene_night_garden_v1.jpeg | ddab84fb33c8c790… |
| L0 day | warren_scene_day_garden_v1.jpeg | c08db3429c826ffc… |
| L1 hub | warren_scene_gate_hub_v1.jpeg | ca5fb0e496d437bf… |
| L2 bridge | warren_scene_bridge_stream_v1.jpeg | 0275810891558bfa… |
| L3 circle | warren_scene_stone_circle_v1.jpeg | 8f555f45a91d3b9c… |
| L4 village | warren_scene_village_cross_v1.jpeg | 99414da494aade85… |

*Six stages. Three laws. One loop. The Warren deepens by rhyming with
itself.*
