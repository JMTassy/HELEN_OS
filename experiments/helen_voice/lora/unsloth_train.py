"""STEP 3 — Unsloth QLoRA voice trainer. RUNS ON NVIDIA/CUDA ONLY (rented 4090/5090 or Colab).
NOT on a Mac. Teaches VOICE (style) only — LOW epochs on purpose. authority=false.
Setup on the GPU box:  pip install "unsloth[colab-new]" trl datasets
Run:                   python unsloth_train.py
"""
import torch
from unsloth import FastLanguageModel
from datasets import load_dataset
from trl import SFTTrainer
from transformers import TrainingArguments

MODEL = "unsloth/gemma-4-12b-it-bnb-4bit"   # HAL: start with 12B. 26B-MoE only after this works.
MAX_SEQ = 2048

model, tok = FastLanguageModel.from_pretrained(
    model_name=MODEL, max_seq_length=MAX_SEQ, load_in_4bit=True, dtype=None)

model = FastLanguageModel.get_peft_model(
    model, r=16, lora_alpha=32, lora_dropout=0, bias="none",
    target_modules=["q_proj","k_proj","v_proj","o_proj","gate_proj","up_proj","down_proj"],
    use_gradient_checkpointing="unsloth", random_state=7)

ds = load_dataset("json", data_files="voice_dataset.train.jsonl", split="train")
ds = ds.map(lambda ex: {"text": tok.apply_chat_template(ex["messages"], tokenize=False,
                                                        add_generation_prompt=False)})

trainer = SFTTrainer(
    model=model, tokenizer=tok, train_dataset=ds,
    dataset_text_field="text", max_seq_length=MAX_SEQ,
    args=TrainingArguments(
        per_device_train_batch_size=2, gradient_accumulation_steps=4, warmup_steps=5,
        num_train_epochs=2,                 # <-- HAL: 2, not 10. Style, not memorization.
        learning_rate=2e-4, logging_steps=1, optim="adamw_8bit", weight_decay=0.01,
        lr_scheduler_type="linear", seed=7, output_dir="outputs",
        bf16=torch.cuda.is_bf16_supported(), fp16=not torch.cuda.is_bf16_supported()))

trainer.train()
model.save_pretrained("jmt_voice_lora"); tok.save_pretrained("jmt_voice_lora")
print("adapter saved -> jmt_voice_lora/  (VOICE-ONLY, authority=false). Run eval_voice_adapter.py next.")
