# Fine-tune HELEN-Gemma — the SIA weight lever, governed

Bake HELEN's voice + governance reflexes into Gemma 4 weights, so HELEN is HELEN
even with no system prompt. This is the **weight lever** from the SIA paper; HELEN
adds what SIA's own Limitations section lacks — the adapter is a **receipted,
separately-validated claim**, not a self-approved verdict.

## Hard reality: where this runs
- **Training → the 5070 only.** Unsloth needs CUDA/NVIDIA. Mac/MLX training is not
  shipped yet. The Mac (M3 Pro) *runs* models; it does not *train* them.

## Two model tracks (same dataset, different base)
HELEN's current brain (`helen-core`/`helen-ship`) is **Qwen3.5** — so the *faithful*
HELEN tune is Qwen, in her own lineage. Gemma is the multimodal/AIRI track.

| Track | Script | Base (fits 5070 ~12 GB) | For |
|---|---|---|---|
| **Qwen3.5 (faithful core)** | `train_helen_qwen35.py` | **Qwen3.5-4B bf16 LoRA (~10 GB)** — 9B (22 GB) won't fit; QLoRA not recommended for Qwen3.5 | HELEN's identity/governance in her own model family |
| **Gemma 4 (multimodal)** | `train_helen_gemma.py` | **Gemma 4 E2B 4-bit LoRA (8–10 GB)** — E4B (17 GB) won't fit | vision/audio HELEN for AIRI |

Both consume the **same** dataset (persona + plugins + doctrine).
Start with Qwen3.5-2B (5 GB) if you want a fast first pass before the 4B run.

### Big models (9B / 12B) → cloud, not the 5070
The 5070 (~12 GB) is a **~4B-class trainer**. Qwen3.5-9B (22 GB bf16 LoRA) and Gemma 4
12B (~16–24 GB) **won't fit** — fine-tuning holds the full model's activations, not just
the LoRA adapter. For those, use **`HELEN_bigmodel_colab_A100.ipynb`** on a free Colab
A100 (40 GB): flip `MODEL_CHOICE`, upload the 3 jsonl, train, download the GGUF.

## Files
- `helen_persona_sft.jsonl` — starter HELEN dataset (14 examples: authority=false,
  no-receipt-no-claim, proposer≠validator, the `HELEN_ACTION` protocol, her voice).
  **This is a seed — expand it** from real receipted sessions before a serious run.
- `train_helen_gemma.py` — Unsloth E2B LoRA recipe (gemma-4 non-thinking template,
  `train_on_responses_only`, GGUF export).

## Run it on the 5070
```bash
# 1. install Unsloth (Linux/WSL)
curl -fsSL https://unsloth.ai/install.sh | sh
# 2. copy this folder over, then:
python train_helen_gemma.py
# 3. load the result into Ollama as a HELEN model (Modelfiles included)
ollama create helen-gemma-tuned -f Modelfile.helen-gemma   # Gemma track
ollama create helen-qwen-tuned  -f Modelfile.helen-qwen    # Qwen track
#    (confirm the GGUF filename in the FROM line first: ls helen_*_gguf/)
```
Then on the Mac: `HELEN_MODEL=helen-gemma-tuned OLLAMA_HOST=http://<5070-ip>:11434 helen start`.

## Governance — why this is a *claim*, not a checkpoint
A LoRA adapter trained by HELEN is exactly the failure SIA names ("coupled
co-evolutionary Goodhart": an optimiser that games its own grader). HELEN's answer:
1. **Receipt** — the run emits a `WEIGHT_UPDATE` record: dataset SHA, base model,
   LoRA config, step count, eval result, output GGUF SHA. No receipt → not real.
2. **Proposer ≠ validator** — the session that trained it cannot promote it. A
   fresh context (or you) must evaluate the adapter against held-out HELEN behaviour
   before it becomes a runnable model.
3. **Replayable** — same dataset + same seed (3407) → same adapter. If it doesn't
   reproduce, it doesn't ship.
4. **Human gate** — you authorize promotion to `helen-gemma-tuned`. The verifier is
   not sovereign; you are.

## Two tracks (SIA framing)
- **SFT (this folder)** — persona/governance. Makes Gemma *be* HELEN.
- **GRPO RL (next)** — task skill on a verifier (the SIA weight lever proper). Fits
  E2B on 9 GB; reward = a deterministic HELEN gate. This is where domain intuition
  that no prompt can instil gets built.

> SIA is the engine. HELEN is the governance that makes the engine admissible.
