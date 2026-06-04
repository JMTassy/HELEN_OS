"""
train_helen_qwen35.py — fine-tune Qwen3.5 into HELEN (the FAITHFUL weight lever).

HELEN's current brain (helen-core / helen-ship) is Qwen3.5. So tuning Qwen3.5 keeps
HELEN in her own lineage, unlike the Gemma track (which is for multimodal/AIRI).

RUNS ON THE 5070 (CUDA), NOT THE MAC. On ~12 GB VRAM the faithful target is
Qwen3.5-4B bf16 LoRA (~10 GB). 9B needs 22 GB. QLoRA (4-bit) is NOT recommended
for Qwen3.5 (quantization error too high) — use bf16/16-bit LoRA.

Requirements: transformers v5 (Unsloth pulls it in). Same HELEN dataset as the
Gemma track — persona + the #PLUGINS slice.

The resulting LoRA adapter is a WEIGHT_UPDATE claim under HELEN doctrine: receipt
it, have a non-proposer validate it, then you authorize promotion.
"""

import os
from unsloth import FastLanguageModel
from unsloth.chat_templates import train_on_responses_only
from datasets import load_dataset
from trl import SFTTrainer, SFTConfig

# First pass = 2B (5 GB, fast). Faithful run: HELEN_QWEN=unsloth/Qwen3.5-4B python train_helen_qwen35.py
MODEL = os.getenv("HELEN_QWEN", "unsloth/Qwen3.5-2B")   # 2B/4B fit the 5070 at bf16; 9B does not
MAX_SEQ = 4096
DATA = ["helen_persona_sft.jsonl", "helen_plugins_sft.jsonl", "helen_doctrine_sft.jsonl"]

# ── 1. Load Qwen3.5-4B in bf16 LoRA mode (NOT 4-bit) ─────────────────────────
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name=MODEL,
    max_seq_length=MAX_SEQ,
    load_in_4bit=False,     # QLoRA not recommended for Qwen3.5
    load_in_16bit=True,     # bf16 LoRA
    full_finetuning=False,
)

model = FastLanguageModel.get_peft_model(
    model,
    r=16, lora_alpha=16, lora_dropout=0, bias="none",
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                    "gate_proj", "up_proj", "down_proj"],
    use_gradient_checkpointing="unsloth",   # lower VRAM + long context
    random_state=3407,
    max_seq_length=MAX_SEQ,
)

# ── 2. HELEN dataset → Qwen ChatML via the tokenizer's native template ────────
dataset = load_dataset("json", data_files=DATA, split="train")

def fmt(ex):
    return {"text": [
        tokenizer.apply_chat_template(c, tokenize=False, add_generation_prompt=False)
        for c in ex["conversations"]
    ]}
dataset = dataset.map(fmt, batched=True)

# ── 3. Train ─────────────────────────────────────────────────────────────────
trainer = SFTTrainer(
    model=model, tokenizer=tokenizer, train_dataset=dataset,
    args=SFTConfig(
        max_seq_length=MAX_SEQ,
        dataset_text_field="text",
        per_device_train_batch_size=1,
        gradient_accumulation_steps=4,
        warmup_steps=5,
        num_train_epochs=3,
        learning_rate=2e-4,
        logging_steps=1,
        optim="adamw_8bit",
        weight_decay=0.001,
        lr_scheduler_type="linear",
        seed=3407,
        report_to="none",
        output_dir="outputs_helen_qwen35",
    ),
)
# Qwen uses ChatML — train only on HELEN's assistant turns.
trainer = train_on_responses_only(
    trainer,
    instruction_part="<|im_start|>user\n",
    response_part="<|im_start|>assistant\n",
)

trainer.train()

# ── 4. Export to GGUF for Ollama (HELEN runtime) ─────────────────────────────
model.save_pretrained_gguf("helen_qwen35_gguf", tokenizer, quantization_method="q4_k_m")
print("DONE. helen_qwen35_gguf/. WEIGHT_UPDATE claim — receipt + non-proposer validation before promote.")
