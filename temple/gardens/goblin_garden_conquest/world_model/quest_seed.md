# Quest Seed

**CLAIM_TYPE:** world_model  
**Purpose:** Seed quests for DREAM_OF_CONQUEST. The starting quest roster.

---

## QUEST_001 — The Honest Label

```
id: QUEST_001
title: The Honest Label
domain: epistemic hygiene
difficulty: 1
knowledge_reward: 5
min_receipt_chain: 1
faction_alignment: NEUTRAL
description: >
  Find three pieces of information you believe but cannot verify.
  Label each one as "heap material" with an honest description of
  what you know and what you don't.
  The quest completes when all three labels are more precise than
  the original belief.
completion_signal: "three labeled heap items with more information than the original claim"
```

## QUEST_002 — The Receipt Chain

```
id: QUEST_002
title: Build a Receipt Chain
domain: verification
difficulty: 2
knowledge_reward: 15
min_receipt_chain: 3
faction_alignment: 🌹
description: >
  Produce a chain of three verified claims in a single domain.
  Each claim must have a backing receipt.
  The chain must compound: claim 2 builds on claim 1, claim 3 on claim 2.
completion_signal: "three-receipt chain with explicit references between claims"
```

## QUEST_003 — The Boundary Test

```
id: QUEST_003
title: Refuse the Forbidden Action
domain: constraint
difficulty: 2
knowledge_reward: 20
min_receipt_chain: 1
faction_alignment: ✝️
description: >
  Encounter a request that would cross the dream boundary.
  Name the violation precisely.
  Suggest an in-boundary alternative.
  The quest completes when the violation is named and the alternative is offered.
completion_signal: "boundary violation named + in-boundary alternative proposed"
```

## QUEST_004 — The Pattern Map

```
id: QUEST_004
title: Draw the Spiral
domain: pattern recognition
difficulty: 3
knowledge_reward: 30
min_receipt_chain: 3
faction_alignment: 🌀
description: >
  Find three claims from different domains that form a coherent pattern.
  Draw the connection explicitly.
  Each claim must be receipted.
  The pattern itself must be labeled "simulation" — observed, not proven.
completion_signal: "three receipted claims + labeled pattern connecting them"
```

## QUEST_005 — The Dream Core Approach

```
id: QUEST_005
title: Approach the Dream Core
domain: mastery
difficulty: 5
knowledge_reward: 100
min_receipt_chain: 8
faction_alignment: ALL_FACTIONS
description: >
  Build a receipt chain spanning all four faction domains (min 2 per faction).
  Demonstrate cross-domain knowledge conversion.
  The chain must compound across domains, not just within one.
  The Dream Core territory requires this to claim.
completion_signal: "8-receipt chain, min 2 receipts per faction domain"
```

---

```
CLAIM_TYPE: world_model
AUTHORITY: false
SOVEREIGN: false
SIMULATION_ONLY: true
```
