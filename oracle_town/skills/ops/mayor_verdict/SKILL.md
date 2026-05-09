---
name: helen-mayor-verdict
description: load when the user asks about MAYOR verdict state, NO_SHIP governance, sovereign verdict ladder, admission decisions, reducer_decision fields in GOBLIN/terminal receipts, or what it means for a claim to be admitted vs blocked.
authority: NON_SOVEREIGN
canon: NO_SHIP
---

# HELEN MAYOR Verdict Skill

## Purpose

MAYOR is the sovereign verdict authority in HELEN OS. Claude Code is not MAYOR. Claude Code may not issue, simulate, or override MAYOR verdicts.

Current state: `NO_SHIP` — canonical across all surfaces, dashboards, and receipts.

## Verdict Ladder

```
NO_SHIP          Default. Nothing exits until MAYOR clears it.
PARTIAL_ADMIT    MAYOR admits specific artifacts, not the whole tranche.
ADMIT            MAYOR admits the tranche; opens next tranche window.
SHIP             Sovereign release. Requires: ADMIT + all K-gates PASS.
ABORT            Hard stop. Tranche sealed, batch cancelled.
```

## How Verdicts Work

1. Proposer submits work (Claude Code, GOBLIN, terminal action)
2. Receipt is emitted with `reducer_decision: null`
3. MAYOR reads the receipt and top-epoch artifacts
4. MAYOR sets `reducer_decision` in the receipt JSON to: `ADMIT / PARTIAL_ADMIT / REJECT / ABORT`
5. Only after ADMIT does the next tranche open

`reducer_decision: null` = waiting for MAYOR. This is not an error.

## GOBLIN Tranche State (current)

| Tranche | Batch ID | Epochs | HAL PASS | Top Score | reducer_decision |
|---|---|---|---|---|---|
| T000 | `07b923ef09df` | 287 | 269 (93.7%) | 0.765 | `null` (MAYOR pending) |

File: `oracle_town/skills/ops/dan_goblin/receipts/BATCH_07b923ef09df_T000.json`

## Dashboard Representation

In the Sovereign Ledger panel, MAYOR verdict is displayed at top as:

```
MAYOR VERDICT
NO_SHIP
```

This must never be changed to `SHIP` in the UI without actual MAYOR governance decision. The UI reads state; it does not set it.

## Gotchas

- `reducer_decision: null` in GOBLIN receipt means MAYOR has not ruled yet. The tranche is in RALPH-WAIT state. This is correct and expected.
- `reducer_decision` in GOBLIN_BATCH_TRANCHE_V1 is always present (null until set). In GOBLIN_EPOCH_V1 the key is ABSENT entirely (not null).
- Claude Code may not call `tools/helen_say.py` with a SHIP op without operator authorization.
- The dashboard displays `NO_SHIP` because that is the current constitutional state — not a bug, not a placeholder.
- Never hardcode `SHIP` in any UI element. Always read from governance state.

## References

- `references/no_ship_governance.md` — why NO_SHIP is the constitutional default
- `references/verdict_ladder.md` — full ladder with gate requirements per rung
