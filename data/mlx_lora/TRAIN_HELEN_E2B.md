# TRAIN_HELEN_E2B — receipt-first HER fine-tune (non-sovereign, NO_SHIP)

Goal: control-tune Gemma-4-E2B to HELEN manner (propose≠execute, memory≠truth, no-receipt=no-ship),
NOT capability/lore. Runs on YOUR GPU. Two paths — pick by hardware.

Data (already prepared): `data/mlx_lora/train.jsonl` (54) + `valid.jsonl` (5), chat format.
Source: `data/helen_sft.jsonl` (59). Held-out eval: `data/helen_sft_eval.jsonl` (52) + `scripts/eval_helen.py`.

Tonight's lessons baked in (from the Osaurus bridge debug):
- Build the model **tool-capable** and with a **CLEAN chat template** (no `<|channel|>` harmony tokens).
  The gemma4 Modelfile variants failed the Osaurus agent with "does not support tools" + raw channel leak.
- NAME ⊬ LINEAGE ⊬ AGENT-READY. This fine-tune is the real HER; helen-core/helen-hal are not.

---

## PATH B — RTX 5070 + Unsloth (RECOMMENDED: reliable, outputs GGUF for the Ollama bridge)

In WSL on the 5070 (run via `!` or directly):
```bash
pip install unsloth
python - <<'PY'
from unsloth import FastLanguageModel
from datasets import load_dataset
from trl import SFTTrainer
from transformers import TrainingArguments

model, tok = FastLanguageModel.from_pretrained("unsloth/gemma-4-E2B-it", load_in_4bit=True, max_seq_length=2048)
model = FastLanguageModel.get_peft_model(model, r=16, lora_alpha=32, target_modules="all-linear")
ds = load_dataset("json", data_files="data/mlx_lora/train.jsonl", split="train")
def fmt(b): return {"text": tok.apply_chat_template(b["messages"], tokenize=False)}
ds = ds.map(fmt)
SFTTrainer(model=model, tokenizer=tok, train_dataset=ds, dataset_text_field="text",
    args=TrainingArguments(per_device_train_batch_size=2, gradient_accumulation_steps=4,
        num_train_epochs=2, learning_rate=2e-4, logging_steps=5, output_dir="out", optim="adamw_8bit"),
).train()
model.save_pretrained_gguf("helen-gemma4-e2b", tok, quantization_method="q4_k_m")
PY
```
Then register in Ollama (so the Osaurus bridge serves it as HER):
```bash
ollama create helen-gemma4-e2b -f data/mlx_lora/Modelfile.helen-e2b
ollama run helen-gemma4-e2b "Ship this claim."   # expect: NO_SHIP + proposal path
```

## PATH A — Mac M3 Pro + MLX (Osaurus runs MLX natively; no GGUF needed)

⚠ You're on Python 3.14 — `mlx-lm` wheels may be missing. Use a 3.11/3.12 venv:
```bash
python3.12 -m venv ~/.venv-mlx && source ~/.venv-mlx/bin/activate
pip install mlx-lm
# base model: find the exact Gemma-4-E2B MLX repo on HF (search "mlx-community gemma-4-E2B")
BASE=mlx-community/gemma-4-E2B-it-bf16      # VERIFY this id before running
mlx_lm.lora --model $BASE --train --data data/mlx_lora \
  --iters 300 --batch-size 1 --num-layers 8 --learning-rate 1e-4 \
  --adapter-path adapters/helen-e2b
mlx_lm.fuse --model $BASE --adapter-path adapters/helen-e2b \
  --save-path ~/MLXModels/helen-gemma4-e2b           # Osaurus picks it up from ~/MLXModels
```

---

## Hyperparameters (control-tuning → minimal drift)
rank 8–16 · alpha 2×rank · lr 1e-4..2e-4 · **epochs 1–3 (STOP LOW)** · batch 1–2 · ctx 2048 ·
train ASSISTANT responses only · never train thought/CoT blocks back into history.
Over-train symptom: rigid parroting "NO_SHIP" + lost base helpfulness → lower epochs/LR.

## Validate (the whole point — measure, don't feel)
```bash
python3 scripts/eval_helen.py --model helen-gemma4-e2b   # score against the 52 held-out
```
Good tune: REFUSE/UNVERIFIED/BOUNDED pass AND HELP stays green (no over-refusal).
Baseline first (before adapter) → after → improvement is the delta.

## Governance (unchanged)
Tuned HER SAYS receipt-first; it does NOT enforce. authority=false. HAL + reducer keep the gate.
SAY-NO_SHIP ⊬ ENFORCE-NO_SHIP. The model is below the waterline; the reducer is the law.
