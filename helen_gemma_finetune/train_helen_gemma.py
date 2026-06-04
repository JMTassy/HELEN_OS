"""
train_helen_gemma.py — fine-tune Gemma 4 E2B into HELEN (the weight lever).

RUNS ON THE 5070 (CUDA), NOT THE MAC. Unsloth needs an NVIDIA GPU; MLX/Mac
training is not shipped yet. E2B LoRA fits the 5070's ~12 GB VRAM (8-10 GB);
E4B (17 GB) and 12B+ do not.

This is the SIA "weight lever": it bakes HELEN's voice and governance reflexes
(authority=false, no-receipt-no-claim, proposer != validator, the HELEN_ACTION
protocol) into the weights instead of only the system prompt. The resulting LoRA
adapter is a WEIGHT_UPDATE artifact — under HELEN doctrine it is a *claim*, not a
verdict: it must be receipted and validated by someone other than the proposer
before it is promoted to a runnable HELEN model.

Setup on the 5070 (Windows/Linux + CUDA):
    curl -fsSL https://unsloth.ai/install.sh | sh        # Linux/WSL
    # or on Windows PowerShell: irm https://unsloth.ai/install.ps1 | iex
    python train_helen_gemma.py

Then export to GGUF and load into Ollama as `helen-gemma-tuned` (see README).
"""

import os
from unsloth import FastModel
from unsloth.chat_templates import get_chat_template, standardize_data_formats, train_on_responses_only
from datasets import load_dataset
from trl import SFTTrainer, SFTConfig

# Default E2B (8 GB train). E4B (10 GB) is the bigger model that STILL fits a 12 GB 5070
# and Unsloth recommends it over E2B:  GEMMA_MODEL=unsloth/gemma-4-E4B-it python train_helen_gemma.py
# Do NOT set this to gemma-4-12b: fine-tuning 12B needs ~16-24 GB and will OOM on a 5070.
# (The 12B you run fast in Ollama is INFERENCE, not training.)
MODEL = os.getenv("GEMMA_MODEL", "unsloth/gemma-4-E2B-it")
MAX_SEQ = 4096
# HELEN persona/governance + the #PLUGINS slice (run build_plugins_dataset.py first).
DATA = ["helen_persona_sft.jsonl", "helen_plugins_sft.jsonl", "helen_doctrine_sft.jsonl"]

# ── 1. Load E2B in 4-bit LoRA mode ───────────────────────────────────────────
model, tokenizer = FastModel.from_pretrained(
    model_name=MODEL,
    max_seq_length=MAX_SEQ,
    load_in_4bit=True,          # ~8-10 GB on the 5070
    full_finetuning=False,
)

# E2B is non-thinking; use the plain "gemma-4" template (not "-thinking").
tokenizer = get_chat_template(tokenizer, chat_template="gemma-4")

model = FastModel.get_peft_model(
    model,
    finetune_vision_layers=False,     # text-only persona tune
    finetune_language_layers=True,
    finetune_attention_modules=True,
    finetune_mlp_modules=True,
    r=8, lora_alpha=8, lora_dropout=0, bias="none",
    random_state=3407,
)

# ── 2. HELEN persona/governance dataset ──────────────────────────────────────
dataset = load_dataset("json", data_files=DATA, split="train")
dataset = standardize_data_formats(dataset)

def fmt(ex):
    return {"text": [
        tokenizer.apply_chat_template(c, tokenize=False, add_generation_prompt=False).removeprefix("<bos>")
        for c in ex["conversations"]
    ]}
dataset = dataset.map(fmt, batched=True)

# ── 3. Train (loss ~13-15 is normal for E2B multimodal — not a bug) ──────────
trainer = SFTTrainer(
    model=model, tokenizer=tokenizer, train_dataset=dataset,
    args=SFTConfig(
        dataset_text_field="text",
        per_device_train_batch_size=1,
        gradient_accumulation_steps=4,   # Unsloth fixes the GA-loss inflation bug
        warmup_steps=5,
        num_train_epochs=3,              # small dataset — a few epochs; watch for overfit
        learning_rate=2e-4,
        logging_steps=1,
        optim="adamw_8bit",
        weight_decay=0.001,
        lr_scheduler_type="linear",
        seed=3407,
        report_to="none",
        output_dir="outputs_helen_gemma",
    ),
)
# Train only on HELEN's responses, not the user turns.
trainer = train_on_responses_only(
    trainer,
    instruction_part="<|turn>user\n",
    response_part="<|turn>model\n",
)

trainer.train()

# ── 4. Export to GGUF for Ollama (HELEN runtime) ─────────────────────────────
model.save_pretrained_gguf("helen_gemma_gguf", tokenizer, quantization_method="q4_k_m")
print("DONE. Adapter + GGUF in helen_gemma_gguf/. This is a WEIGHT_UPDATE claim —")
print("receipt it and have a non-proposer validate before promoting to a HELEN model.")
