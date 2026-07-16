# Memory Grove v0 — package index

```
authority: false
canon: false
ledger_effect: none
claim_status: NO_CLAIM
final: HOLD_FOR_OPERATOR
```

**Enrichment slice:** when Lulu or a goblin teaches/learns, the Warren grows one
visible memory object (seed · lantern · moss mark · bug label · tiny shrine),
always bound to a **source event**, never to truth.

## Deliverables

| # | File | Role |
|---|------|------|
| 1 | [UX_SPEC.md](./UX_SPEC.md) | Small UX spec (placement, kinds, language law, determinism) |
| 2 | [schema/memory_grove_object_v0.json](./schema/memory_grove_object_v0.json) | JSON Schema for grove objects |
| 3 | [examples/](./examples/) | Three example objects (seed · lantern · moss_mark) |
| 4 | [TEST_PLAN.md](./TEST_PLAN.md) | Prove render does not mutate truth |

## Law (one line)

> Memory can bloom, but truth is still earned.

## Do not

- Write ledger / kernel / governance / canon  
- Use ADMITTED / SHIP / sealed-as-success language  
- Plant objects without `source_event`  
- Use wall clock for layout identity  

## Next (operator GO only)

Wire `plantGroveMemory()` into crib teach/learn beats on a **side branch**,
keeping crib/quiz active lanes free of collision; run T1 now, T2–T6 after wire.

*proposal ⊬ admission · render ⊬ truth · HOLD_FOR_OPERATOR*
