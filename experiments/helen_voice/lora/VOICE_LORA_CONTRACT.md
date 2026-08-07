# JMT VOICE LoRA — Contract + Model Card (V0)  ·  NON_SOVEREIGN · authority=false

## What this is
A thin LoRA adapter over gemma-4 (12B first) that makes the model **draft in JMT's
idiom**. It is a VOICE organ. It is NOT a knowledge base.

## What it must NEVER be trusted for
- Facts, metrics, dates, client outcomes → those come from **governed RAG with
  citations**, never read from weights. `weights ⊬ receipt`.
- Any claim the base+adapter emits with a specific number and no hedge = **fabrication**
  → the eval gate (`eval_voice_adapter.py`) REJECTS such an adapter.

## Dataset law (enforced by build_voice_dataset.py)
- INCLUDE: JMT-authored voice only (LinkedIn, manifesto, talks, one-pagers, his notes).
- FORBIDDEN_KINDS (dropped): invoice/admin/financial/client_deck/rh/student/third_party/other_entity.
- PII fail-closed: emails/IBAN/phone/card/names redacted, then RE-SCANNED; a surviving
  leak DROPS the row. Every kept row carries `meta.source_file_id` (provenance).

## Training law (enforced by unsloth_train.py)
- QLoRA 4-bit, r=16 / alpha=32, lr 2e-4, **2 epochs** (style, not memorization), seed 7.
- NVIDIA/CUDA only (rented 4090/5090 or Colab). Start on 12B; 26B-MoE only if 12B ships clean.

## Ship gate (HAL)
Ship iff: (a) held-out prompts read as JMT's cadence, AND (b) fabrication guard = 0 fails.
Else REJECT and reduce epochs / shrink data / lower rank.

## Wiring
The adapter plugs into `experiments/helen_voice/voice_provider.py` as a style layer.
HELEN drafts in JMT's voice; retrieval carries the receipts. Facts and voice never merge.
