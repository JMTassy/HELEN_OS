# Obsidian Mirror — Autoresearch Role

The Obsidian Mirror is the memory chamber of autoresearch.

Primary document: `docs/temple/obsidian_mirror.md`
This file describes the Mirror's specific role in the autoresearch loop.

## What the Mirror Does in Autoresearch

Across 200 epochs, the Mirror aggregates per-epoch receipts into an attractor map:

```
epoch_1_receipt  (concept=REPLAY, probe=frequency_in_docs, CONFIRMED)
epoch_2_receipt  (concept=REPLAY, probe=coupling_with_ledger, CONFIRMED)
...
epoch_20_receipt (concept=REPLAY, probe=frequency_in_proposals, CONFIRMED)
  => lineage_pressure(REPLAY) = 0.95
```

High lineage pressure = the concept keeps reappearing in admissible evidence.

## What the Mirror Does NOT Do

- It does not decide which attractors are "true"
- It does not promote attractors to doctrine
- It does not generate new hypotheses autonomously
- It does not claim that frequency equals importance

## The Mirror's Question

Not: "What did the model say?"
But: "What keeps recurring across admissible history?"

## Attractor Map Output Format

```json
{
  "type": "OBSIDIAN_MIRROR_ATTRACTOR_MAP_V1",
  "epochs_run": 200,
  "head_sha": "...",
  "attractors": [
    {
      "concept": "REPLAY",
      "probe_angles_run": 20,
      "confirmed": 19,
      "weak": 1,
      "absent": 0,
      "lineage_pressure": 0.95,
      "top_sources": ["docs/", "helen_os/", "scripts/"]
    }
  ],
  "authority": "NONE",
  "non_sovereign": true
}
```

## Routing After 200 Epochs

The attractor map is a candidate input for doctrine delta.
It does not become doctrine automatically.

Required path:

    Mirror emits attractor_map
      -> Operator reviews
      -> Routes to MAYOR
      -> MAYOR issues verdict
      -> Doctrine_new = Diff(candidate, SOT)
      -> Receipt written to ledger

## Anti-Inflation Guard

The Mirror's output must satisfy AURA anti-inflation laws:
1. Frequency is not truth
2. Recurrence is not proof
3. High lineage_pressure is not authority
4. Attractor candidate is not doctrine
5. Mirror output is not self-admitting

The receipt decides. The MAYOR rules. The ledger preserves.
