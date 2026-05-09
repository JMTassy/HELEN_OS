# HELEN OS — Verdict Ladder

| Verdict | Who Sets It | What It Unlocks |
|---|---|---|
| `NO_SHIP` | Default / MAYOR | Nothing. Resting state. |
| `PARTIAL_ADMIT` | MAYOR | Specific artifacts admitted; others blocked |
| `ADMIT` | MAYOR | Full tranche admitted; next tranche may open |
| `SHIP` | MAYOR (after all gates) | Sovereign release — requires K8 + K-tau + K-rho + K-wul all PASS |
| `ABORT` | MAYOR | Hard stop. Tranche sealed. Batch dead. |
| `REJECT` | MAYOR | Tranche-level rejection; no partial credit |

## Gate Requirements for SHIP

All gates must PASS before MAYOR may issue SHIP:

| Gate | Script |
|---|---|
| K8 Non-Determinism Boundary | `scripts/helen_k8_lint.py` |
| K-tau Coherence | `scripts/helen_k_tau_lint.py` |
| K-rho Numeric Consistency | `scripts/helen_rho_lint.py` |
| K-wul WUL Compile+Validate | `scripts/helen_wul_lint.py` |

## Current Tranche State

```
Batch:     07b923ef09df
Tranche:   T000
Epochs:    287 / 300
HAL:       PASS=269  WARN=16  BLOCK=2
Receipt:   oracle_town/skills/ops/dan_goblin/receipts/BATCH_07b923ef09df_T000.json
Decision:  null  (MAYOR pending)
```

RALPH is waiting. Next tranche cannot open until `reducer_decision` is set.
