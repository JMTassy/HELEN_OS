#!/usr/bin/env python3
"""
train_helen_e2b.py — control-tune Gemma-4-E2B → receipt-first HER (NON-SOVEREIGN, NO_SHIP).
Run on a CUDA GPU (RTX 5070 / WSL).  Outputs a q4_k_m GGUF for `ollama create`.

  pip install unsloth
  python train_helen_e2b.py
  ollama create helen-gemma4-e2b -f Modelfile.helen-e2b
  python3 ../../scripts/eval_helen.py --model helen-gemma4-e2b   # score vs held-out

Trains assistant turns only. Keep epochs low (control-tuning = minimal drift). authority=false.
"""
import os
from unsloth import FastLanguageModel
from datasets import load_dataset
from trl import SFTTrainer
from transformers import TrainingArguments

HERE = os.path.dirname(os.path.abspath(__file__))
TRAIN = os.path.join(HERE, "train.jsonl")          # 54 examples, chat format
OUT_GGUF = os.path.join(HERE, "helen-gemma4-e2b")  # GGUF dir for the Modelfile

model, tok = FastLanguageModel.from_pretrained(
    "unsloth/gemma-4-E2B-it",        # verify the exact tag if it errors
    load_in_4bit=True,
    max_seq_length=2048,
)
model = FastLanguageModel.get_peft_model(
    model, r=16, lora_alpha=32, lora_dropout=0,
    target_modules="all-linear", use_gradient_checkpointing="unsloth",
)

ds = load_dataset("json", data_files=TRAIN, split="train")
ds = ds.map(lambda b: {"text": tok.apply_chat_template(b["messages"], tokenize=False)})

trainer = SFTTrainer(
    model=model, tokenizer=tok, train_dataset=ds,
    dataset_text_field="text", max_seq_length=2048,
    args=TrainingArguments(
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,
        num_train_epochs=2,            # STOP LOW — 1-3. raise only if undertrained
        learning_rate=2e-4,
        warmup_steps=5,
        logging_steps=5,
        optim="adamw_8bit",
        weight_decay=0.01,
        lr_scheduler_type="linear",
        seed=0,
        output_dir=os.path.join(HERE, "out"),
    ),
)
trainer.train()

# Export GGUF (q4_k_m) for Ollama → the Osaurus bridge will then serve it as HER.
model.save_pretrained_gguf(OUT_GGUF, tok, quantization_method="q4_k_m")
print(f"\nDONE → {OUT_GGUF}\nNext: ollama create helen-gemma4-e2b -f {os.path.join(HERE,'Modelfile.helen-e2b')}")
