# Quest Model

**CLAIM_TYPE:** world_model  
**Purpose:** Define quest structure in DREAM_OF_CONQUEST. Quests as epistemic challenges.

---

## Quest Schema

```
QUEST_V0 = {
  "id": "QUEST_XXX",
  "claim_type": "quest",
  "authority": false,
  "sovereign": false,
  "status": "PROPOSED",
  "title": "...",
  "domain": "...",              # knowledge domain to master
  "difficulty": 1-5,
  "knowledge_reward": N,        # KNOWLEDGE_UNITS on completion
  "receipt_required": true,     # always true
  "min_receipt_chain": 2,       # minimum verified claims
  "validation_gate": "...",     # which local gate validates completion
  "faction_alignment": "...",   # which faction benefits (or NEUTRAL)
  "forbidden_in_quest": [
    "unreceipted_assertions",
    "sovereignty_claims",
    "ledger_references"
  ]
}
```

## Quest Types

| Type | Description |
|---|---|
| KNOWLEDGE_ACQUISITION | Understand a domain deeply enough to hold receipted claims about it |
| CLAIM_CHAIN | Build a receipt chain of N verified claims in a domain |
| DISPUTE_RESOLUTION | Resolve a territory dispute using better receipts than the challenger |
| HEAP_AUDIT | Correctly label N heap items (honest labeling quest) |
| BOUNDARY_TEST | Prove you understand a constraint by refusing a forbidden action |

## Completion Protocol

A quest completes when:
1. The required receipt chain is produced
2. The local validation gate passes
3. A QUEST_RECEIPT is written with `authority=false`
4. Resources are credited in simulation state

Quests cannot be completed by assertion. The receipt is the proof.  
The goblin guide verifies the receipts, not the confidence of the claim.

---

```
CLAIM_TYPE: world_model
AUTHORITY: false
SOVEREIGN: false
SIMULATION_ONLY: true
```
