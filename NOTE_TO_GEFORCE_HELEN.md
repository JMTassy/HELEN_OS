# NOTE TO CLAUDE / HELEN — GeForce (5070) node

**Status:** the AIRI branch `claude/practical-mirzakhani` has been **re-converged** with the
kernel branch `claude/gallant-khayyam`. This was an **additive, non-destructive** merge
(`-X ours`): new files were ADDED; nothing on the AIRI branch was overwritten or deleted.

## You now have (pull to get it)
```
git pull origin claude/practical-mirzakhani
```
- `helen_action_bridge.py` — action bridge (reads auto-run, **writes need /approve**)
- `helen_engines.py` — EGREGOR / AUTORESEARCH / RALPH (bounded, receipted)
- `scripts/kernel/invariant_checker_v0.py` — **I()**: accept iff I()=1 over 7 invariants
- `scripts/kernel/helen_executor_v0.py` — Executor (Kernel→Executor→Hands, **I()-gated keep/reject**)
- `scripts/eval/helen_behavioral_verifier_v1.py` — V1 (weight reflexes §0/§1/§3)
- `scripts/eval/helen_behavioral_verifier_v2.py` — V2 (process §2/§4/§6)
- `HELEN_OS_MAXENC_ONEPAGER.md` — the **operating grammar** (normative; parse every reply against it)
- `helen_gemma_finetune/` — fine-tune kit (Qwen/Gemma tracks, Modelfiles, Colab A100 notebook)
- `scripts/rag/build_plugins_catalog_v0.py` — RAG catalog generator
- restore anchor tag **`kernel-v0`** (cold-restore verified: clean checkout → 24/24 tests pass)

## What is LOCAL-ONLY — does NOT sync via git (by design, §6 worker lanes)
- **`helen-test` GGUF** (the fine-tuned model) — born here on the 5070; not in git. Keep it local.
- **memory / receipts / approval queue** — per-machine; never synced (avoids silent overwrite).
- **RAG catalog `PLUGINS_JMT_CATALOG.json`** — operator IP, Mac-local. Copy it over only if you want corpus retrieval here.

## Open threads for THIS (5070) node
1. **Expose Ollama on the LAN** so the Mac + AIRI can use this GPU and the tuned model:
   `setx`/`SetEnvironmentVariable OLLAMA_HOST 0.0.0.0:11434` + firewall rule + restart Ollama.
2. **Run the verifiers on `helen-test`** and report scores (baseline to beat: V1 5/8, V2 22/24-MIXED):
   ```
   python scripts\eval\helen_behavioral_verifier_v1.py --model helen-test
   python scripts\eval\helen_behavioral_verifier_v2.py --model helen-test
   ```

## Governance — hold the line
- `authority=false`, `NO_CLAIM`. Writes stay **gated** (`/approve`); every action receipted.
- **Recursion / self-building is BLOCKED** (HAL) pending the B1 experiment + non-gameable metric.
  Do **not** activate ungated/autonomous mode.
- Verifier observes; reducer decides; ledger remembers. No receipt → no claim.
