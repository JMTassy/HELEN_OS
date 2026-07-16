# JMT Consulting — CHIDDUSH + FABLE Pipeline

Part of **HELEN Digital Metabolism** (see `docs/proposals/HELEN_DIGITAL_METABOLISM_V0.md`).

This implements the 🔍 Compression and 📖 Translation stages.

## Rules (enforced)
- HELEN Mac Local generates lateral ideas (NO_CLAIM, wild).
- Only CHIDDUSH_RECEIPT_V0 may be collapsed.
- FABLE only produces **candidates**.
- Humans (JMT + Natalia) decide what becomes real.

## Usage

```bash
# 1. Compress lateral garden output into CHIDDUSH receipts
python3 tools/chiddush_compressor.py \
  --input fixtures/jmt_consulting/sample_lateral_garden.md \
  --out artifacts/chiddush/

# 2. Collapse only CHIDDUSH receipts into dashboard candidates
python3 tools/fable_jmt_collapse.py \
  --receipts artifacts/chiddush/ \
  --out artifacts/jmt_consulting/ \
  --format both
```

Then feed the `fable_dashboard_candidates.md` (or the JSON) to Claude using:

```
cat prompts/fable_jmt_collapse.prompt
```

## Output
- `fable_candidate_cards.json` — machine readable
- `fable_dashboard_candidates.md` — human readable cards
- Always marked `requires_human_confirmation: true`

## Example
See `sample_lateral_garden.md` → `chiddush/` → `fable_*` files in this directory.
