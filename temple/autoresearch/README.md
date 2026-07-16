# Autoresearch — Consumption Organ (Garden Layer)

This directory now contains the full generation → validation → **consumption** loop.

## The Trio (property ③ closed in garden)

- `outbox_triage.py` — lens on unconsumed packets. Groups by emergent theme. Emits TRIAGE_RECEIPT_V0.
- `outbox_consume.py` — pen. Routes triage to bounded actions. Emits CONSUME_RECEIPT_V0.
- `ci_outbox_guard.py` — gate. Fails CI (exit 1) if unconsumed > threshold.

All output is garden-only (`triage/`, `triage/consumed/`). `authority=false`, `ledger_effect=none`, `reducer_required=true`.

## Usage (local + CI)

```bash
# 1. Lens
python temple/autoresearch/outbox_triage.py --emit

# 2. Pen
python temple/autoresearch/outbox_consume.py

# 3. Gate (in CI or pre-push)
python temple/autoresearch/ci_outbox_guard.py --max-unconsumed 5
```

See HELEN_DIGITAL_METABOLISM_V0.md §"Consumption Organ" for the law.

" A pipeline that only produces is a graveyard with receipts." — now has a consumer.

## TRACE_ONLY AUTORESEARCH LOOP (doctrine refinement)

`trace_only_autoresearch_loop.py` implements the recursive doctrine-compression loop:

- Starts from jurisdiction-before-cognition seed.
- 8 steps per epoch: Current Doctrine, Mutate, Attack, Locate, Extract, Compress, Verify, Convergence Check.
- TRACE ONLY: authority=false, no sovereign writes, proposal candidates only.
- Stops on 3-epoch stability or max epochs.
- Produces the smallest replayable, operational, verifiable invariant.

Example:
python temple/autoresearch/trace_only_autoresearch_loop.py --epochs 8 --seed "The metabolism itself is the invariant: Model ⊬ Organ ..."

Output candidates can be fed as proposals into the consumption organ.

All output is candidate doctrine only. NO CLAIM.