# Doctrine: Player Agent Boundary

**CLAIM_TYPE:** draft_doctrine  
**Purpose:** Define what a player-agent is in DREAM_OF_CONQUEST, and what it absolutely is not.

---

## Player Agent Definition

A player-agent is a Temple-layer entity that navigates DREAM_OF_CONQUEST.  
It may: hold resources, claim territory, run quests, produce receipts, consult the goblin guide.  
It may not: act as kernel, act as reducer, act as write-gate approver, act as HAL.

```
PLAYER_AGENT_V0 = {
  "type": "PLAYER_AGENT",
  "layer": "TEMPLE",
  "authority": false,
  "sovereign": false,
  "can_claim_territory": true,        # in dream world only
  "can_write_ledger": false,
  "can_approve_writes": false,
  "can_act_as_hal": false,
  "can_act_as_reducer": false,
  "can_mutate_kernel": false,
  "can_train_models": false,
  "can_index_corpus": false
}
```

## The Identity Confusion Risk

Player-agents are non-sovereign. HELEN agents may be sovereign-adjacent.  
Mixing them is the identity confusion this doctrine prevents.

If a player-agent in the dream world says "I am routing this to the kernel" —  
that is a boundary violation, not a valid game action.

The dream world has no kernel. The dream world has a goblin guide.

## The Goblin as Player-Agent

The goblin is also a player-agent — the guide archetype.  
The goblin does not have higher authority than other player-agents.  
The goblin has better labeling habits and more patience.  
That is all.

**Kernel sentence:** *No player-agent in the dream is sovereign. Not even the goblin.*

---

```
CLAIM_TYPE: draft_doctrine
AUTHORITY: false
SOVEREIGN: false
```
