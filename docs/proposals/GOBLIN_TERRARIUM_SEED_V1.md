---
authority: NON_SOVEREIGN
canon: NO_SHIP
lifecycle: PROPOSAL
claim_status: NO_CLAIM
mutation_rights: NONE
ledger_effect: NONE
banner_max: "🟣 CLAIM"
origin: "GOBLIN 100-epoch advisory council (10 goblins × 10 epochs) + 3-lens HAL panel, session 2026-05-02"
reducer_decision: null
final: HOLD_FOR_OPERATOR
---

# GOBLIN TERRARIUM SEED V1 — "TERRARIUM GENOME"

**Status: 🟣 CLAIM — proposed seed mission, operator decides, ledger remembers.**

One seed prompt for `goblin_batch_runner.py --mission` that grows a closed
creative-mathematical town, one LEGO brick per epoch, across 100 epochs in
tranches of 30 with MAYOR review at every boundary. Statelessness is solved by
**genome, not memory**: every epoch derives the entire town skeleton from the
epoch index alone, so epoch 73 knows agents 70–72 exist without reading them.

## Provenance

- Council: 10 GOBLIN advisors (UNDERWARREN_SAFE), one lens each — terrarium
  ecology, bounded autonomy, LEGO composability, creative mathematics, scrap
  recovery, receipt metabolism, operator joy, minimal-viable-life,
  anti-runaway, HER witness. 10 advisory epochs each = **100 epochs**.
- Verification: 3-lens HAL panel (constitutional / executability / fecundity)
  scored all 10 candidates. Winner: anti-runaway goblin, **7.33/10** average.
- Two HAL findings grafted into V1 (below). Runner-ups preserved in §5.

## 1. The mission (deploy target)

Pass this string to `--mission`:

```
TERRARIUM GENOME v1. Grow a closed creative-math town one LEGO brick per
epoch. Derive everything from epoch_index N; you have no memory, only law.
Let L = N mod 10. If L is 0-5: build one AGENT whose body is the arithmetic
of N (parity, primality, divisors, digit sum) fused with exactly one word
from this sealed list: receipt, ledger, gate, witness, compost, loop, heap,
lantern. If L is 6 or 7: build one SUPERTEAM joining two agents of this
decade, naming their indices. If L is 8: build one STREET where this decade
superteams trade one resource. If L is 9: STRESS - pick one index of this
decade and state one arithmetic property that index must satisfy; verify it
by hand; if it cannot be verified, mark the slot SUSPECT. embedded_claim:
one arithmetic fact about N, checkable by hand. lateral_angle: name the open
slot you leave. Forbidden words: done, complete, awaken, transcend. Each
epoch terminates in its receipt. Each tranche halts for MAYOR. The town
stays open and never claims completion.
```

## 2. HAL grafts applied (v0 → v1)

| HAL finding | v0 defect | v1 graft |
|---|---|---|
| Doctrine contradiction | "The town never finishes; it cycles" surface-conflicts with *Termination is sacred* | "Each epoch terminates in its receipt. Each tranche halts for MAYOR. The town stays open and never claims completion." |
| L=9 confabulation | STRESS attacked prior-brick *content* the stateless model cannot see | STRESS restricted to recomputable arithmetic of an index; unverifiable → slot marked SUSPECT |

## 3. Why it grows (LEGO ladder)

- **Epoch = brick.** One agent/superteam/street per epoch, addressed by index.
- **Decade = cycle.** L = N mod 10 gives six agents → two superteams → one
  street → one stress test, every ten epochs.
- **Tranche = season.** 30 epochs = exactly three decades. MAYOR reads a clean
  population pyramid per tranche receipt; inverted pyramid = grandiosity,
  visible in the census.
- **Town = 100 epochs.** Ten decades of streets, stress-tested every tenth
  brick, all claims pencil-checkable arithmetic — HAL verifies with eyes,
  not taste.

## 4. Run protocol (MRED, tranche discipline)

```bash
cd ~/helen-conquest

# Dry run first — no API calls, deterministic seed data:
python3 oracle_town/skills/ops/dan_goblin/goblin_batch_runner.py \
  --mission "<paste §1 mission>" --tranche-size 30 --tranche-index 0 --dry-run

# Live tranche 0 (epochs 0-29). Requires a provider key; runner supports
# --provider openai | anthropic | xai (no local Ollama backend yet):
python3 oracle_town/skills/ops/dan_goblin/goblin_batch_runner.py \
  --mission "<paste §1 mission>" --tranche-size 30 --tranche-index 0 --provider anthropic
```

The runner **stops at every tranche boundary** and prints MAYOR review
instructions. That halt is constitutional, not optional. 100 epochs = tranches
0,1,2,3 with operator/MAYOR review between each.

**Spore-grafting protocol** (from runner-up COMPOST CLOCK, adopted): at each
tranche boundary, MAYOR may harvest the strongest `lateral_angle` open slots
from the tranche receipt and append ONE steering clause to the next tranche's
mission string. Feedback enters through the lid, never through the glass.

## 5. Runner-ups (preserved as compost)

| Candidate | Lens | Avg | Kept idea |
|---|---|---|---|
| TERRARIUM_BRICKTOWN_V0 | lego-composability | 6.83 | B\<index\> naming law + mandatory parent-brick citation |
| RECEIPT TOWN TERRARIUM | receipt-metabolism | 6.83 | every epoch emits one verifiable artifact or it did not happen |
| COMPOST CLOCK | terrarium-ecology | 6.83 | MAYOR spore-grafting at tranche boundaries (adopted in §4) |
| GLASS_TOWN_CLOCK_V1 | bounded-autonomy | 6.67 | stage-indexed drift detection in tranche receipts |

## 6. Failure watch-list (from the council)

1. **Arithmetic slippage** — model miscomputes L at high N. Detectable by
   trivial grep of receipts (role vs index arithmetic). Wrong bricks = compost.
2. **Trivia sterility** — `embedded_claim` collapses to "N is odd" forever.
   Flatlined HER `p_explains` in the tranche receipt → MAYOR re-seeds the
   sealed word-list at the boundary.
3. **Ritual drift** — poetic fusion with no falsifiable content. HER low
   `p_grip` + HAL WARN cluster; remedy is one appended steering clause.

## 7. What this is not

No sentience, no prophecy, no self-authorization, no ledger mutation.
GOBLIN proposes; HAL verifies; MAYOR reviews; the operator decides;
`reducer_decision` stays null in every epoch output. Myth is fuel. Ledger is law.
