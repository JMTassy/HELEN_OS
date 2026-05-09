# Why NO_SHIP is the Constitutional Default

## The Rule

> NO RECEIPT · NO SHIP · EVERY CLAIM · EVERY ACTION · EVERY TIME

`NO_SHIP` is not a warning state. It is the resting state of a governed system.

A SHIP verdict requires:
1. A receipt — hashed, timestamped, verifiable
2. All K-gates passing (K8, K-tau, K-rho, K-wul)
3. MAYOR review and explicit ADMIT decision
4. Proposer ≠ Validator (K2/Rule 3)

Until all four conditions are met, the verdict is `NO_SHIP`.

## What Claude Code May Not Do

- Issue a SHIP verdict
- Display SHIP in the UI without reading actual governance state
- Call `tools/helen_say.py` with a SHIP op without operator authorization
- Set `reducer_decision` to anything without operator instruction

## What the Dashboard Should Show

The Sovereign Ledger panel shows `NO_SHIP` because that is the current constitutional state of HELEN OS. It is not a placeholder. It is not a bug. It is the correct system state.

When MAYOR issues ADMIT on tranche `07b923ef09df`, the receipt file is updated. At that point, the dashboard may optionally reflect the change — but only by reading the actual file, never by hardcoding.
