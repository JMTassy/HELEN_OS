# FABLE — non-sovereign goblin swarm (data plane)

```yaml
authority: false
canon: false
implementation: BLOCKED beyond listed phases
core_invariant: "50 logical goblins ≠ 50 resident models"
```

Doctrine: `docs/proposals/FABLE_50_GOBLIN_ARCHITECTURE_V0.md`  
Selection math: `docs/proposals/SELECTIVE_ADMISSIBILITY_DYNAMICS_V0.md`

## P0 (landed) — registry + schemas, no runtime

| Path | Content |
|---|---|
| `registry/guilds.yaml` + `.json` | 10 guilds |
| `registry/goblins.yaml` + `.json` | **50** role packets |
| `schemas/goblin_proposal.schema.json` | GoblinProposalV1 |
| `schemas/epoch.schema.json` | FableEpochV1 |
| `schemas/compost.schema.json` | CompostRecordV1 |
| `schemas/goblin_registry_entry.schema.json` | registry entry (P0 helper) |
| `tests/test_p0_registry_schemas.py` | gate: count 50 + schemas validate |

```bash
.venv/bin/pytest fable/tests/test_p0_registry_schemas.py -v
```

## Not in P0

- `runtime/*` scheduler, dispatcher, selector, reducer, verifier  
- model calls, fine-tunes, concurrent loads  
- ledger writes, admission  

Next phases (each needs its own operator GO): P1 selector → P2 dispatcher → …
