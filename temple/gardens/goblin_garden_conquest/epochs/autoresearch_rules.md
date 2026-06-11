# Temple Autoresearch Simulation — Rules

**CLAIM_TYPE:** simulation  
**Purpose:** Define the rules for the non-sovereign autoresearch simulation in this garden.

---

## What This Is

A 25-epoch Temple autoresearch simulation. Not live system optimization.  
Target: world-model consistency, quest ordering, bulletin clarity, learning-path coherence.

## What This Is NOT

Real autoresearch mutates candidate parameters and evaluates them against live system state.  
This does not. This is a ritual scaffolding of the autoresearch *form* in Temple space.

The simulation practices the discipline of bounded hypothesis formation without touching:
- HELEN kernel
- Sovereign ledger
- Reducer
- Memory systems
- Canonical schemas
- Write gate
- Skills
- Tests
- Real ranking config

## Simulation Rules

```
AUTORESEARCH_SIMULATION_RULES = {
  "hypothesis_per_epoch": 1,
  "observable_signals_only": true,
  "kernel_mutation": false,
  "ledger_mutation": false,
  "memory_mutation": false,
  "halt_discipline": true,        # each epoch seals before next opens
  "receipt_required": true,       # every epoch produces a receipt
  "proposer_ne_validator": true,  # structure not just discipline
  "authority": false,
  "sovereign": false
}
```

## Autoresearch Candidates (allowed)

- Quest ordering: which quest sequence builds knowledge most coherently
- Symbolic map layout: how territories relate spatially to knowledge domains
- Bulletin clarity: which WULmoji grammar produces clearest learning signal
- World-model consistency: does the faction/resource/territory model cohere?
- Learning-path coherence: does Doctrine→Meditation→Bulletin→Validator sequence hold?

---

```
CLAIM_TYPE: simulation
AUTHORITY: false
SOVEREIGN: false
```
