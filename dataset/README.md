# HELEN_DATASET_V0

Sovereign dataset for HER fine-tuning. Small, high-signal, replayable.

## Structure

```
dataset/
  approved/    HAL-PASS exemplars — p_true >= 0.65, p_harm <= 0.15
  rejected/    HAL-BLOCK exemplars — refusal training signal
  boundary/    HAL-WARN exemplars — edge cases, ambiguous
  receipts/    Governance artifacts — tranche receipts, closure receipts
  motifs/      CHIDDUSH / doctrine motifs — constitutional writing style
```

## Curation Rules

Good sources:
- GOBLIN brainstorm entries with HAL=PASS, p_true >= 0.65
- Tranche receipts with verdict=SHIP
- Closure receipts with valid attestor chain
- HER proposal/review pairs from GEMMA_PROPOSALS/

Bad sources (excluded):
- Raw chat logs / user_msg ledger entries
- Entries with p_harm > 0.15
- Entries with missing or null reducer_decision where required
- Cross-session contaminated artifacts (see CLAUDE.md)

## Usage

```bash
python tools/dataset_curator_v0.py --output dataset/ --dry-run
python tools/dataset_curator_v0.py --output dataset/
```

## Target

100–500 clean exemplars. Not 100k noisy files.

## Training objective

HER = proposal-generation behavior under HELEN constraints.
NOT: sovereign cognition, not verdicts, not ledger writes.
