# QWEN 3.8 LOCAL QUALIFICATION — V0 REPORT

- Date: 2026-08-16T12:52:33Z
- AUTHORITY=false · CANON=false · LEDGER_EFFECT=none
- Substrate: Apple M3 Pro, 18 GiB unified memory
- Runtime: llama-cli b9430-d48a56eff (Homebrew, Darwin arm64)

## Disposition

**HOLD_UNUSABLE_PERFORMANCE** (supersedes initial HOLD after the ngl0
failure-boundary discriminator — see `ngl0_discriminator.json`)

The artifact is present, locally hash-witnessed, and computes correctly on the
CPU path: at ngl 0 it returned the exact expected JSON with a clean exit and
zero errors. The ngl 32/16 failures are therefore Metal/offload-specific
(METAL_OFFLOAD_BOUNDARY_FOUND), not artifact corruption or total infeasibility.
But CPU-only throughput is 0.1 tok/s generation (423 s wall for one 64-token
probe), with sys time (271 s) exceeding user time (166 s) — the machine spends
more time paging the 12.6 GB mmapped weights than computing. Runnable, not
operationally useful. The constitutional probe was still not run.

## OBSERVED

- Artifact on disk: `~/models/qwen38-ridge/Qwen3.8-27B-Ridge-3.7bpw.gguf`,
  12,599,187,008 bytes.
- SHA-256 re-computed from disk this session:
  `95580dbdaad579582ee898257116abc18d7f3625a00c16a15735d41444a09f5e` — matches
  the expected value recorded in local download metadata (`_download2.log`).
  Classification: **LOCAL_HASH_WITNESSED** (no remote checksum fetched).
- 2K smoke, ngl 32: model loaded, generation aborted — Metal
  `kIOGPUCommandBufferCallbackErrorOutOfMemory`, "Compute error", nan t/s,
  peak RSS 7.1 GB, wall 70.8 s. **FAIL**.
- 2K smoke, ngl 16 (single permitted retry): same failure class, 29 Metal OOM
  events, peak RSS 11.5 GB, wall 74.1 s. **FAIL**.
- Both runs exited cleanly (no hang, no system instability); memory returned to
  78 % free after unload. The healthy HELEN stack (:8000/:8002/:5173) was never
  touched and stayed live.
- No Ollama model was resident during the tests (`ollama ps` empty).
- ngl 0 discriminator: LOAD_SUCCESS, clean exit, exit code 0, zero stderr
  errors, output was the exact expected JSON. Prompt 1.2 t/s, generation
  0.1 t/s, wall 423.2 s, peak RSS 9.4 GB, swap ~6–7 GB used throughout.
  **Compute path is correct; performance is unusable.**

## INFERRED

- Failure class is GPU-side memory exhaustion, not artifact corruption: the
  file hash matches its download-time record, the GGUF header parsed, and the
  model loaded to the prompt stage in both runs.
- A ~12.6 GB weight set plus KV cache plus compute buffers on an 18 GiB
  unified-memory machine already hosting a desktop workload (~50 % free at
  start) is the plausible cause. This is inference, not measurement.

## NOT TESTED

- ngl 0 (CPU-only) and ngl values other than 32/16 — excluded by the
  no-brute-force rule.
- Running after freeing desktop memory (ChatGPT.app alone held ~8 % MEM).
- 4K and 8K contexts — gated on 2K stability.
- Tokens/sec, output JSON validity, determinism — no generation ever completed.
- Remote checksum verification against the upstream repository.

## UNWIRED / NOT EVALUATED

- HELEN candidate/admission interface for llama-cli output: not evaluated —
  the constitutional probe produced no output to route. No integration was
  fabricated.

## What HOLD means here

The artifact is not condemned and the substrate is not condemned; the tested
configurations are. Plausible next steps (operator decision, not performed):
free desktop memory and retry ngl 16, test ngl 0/CPU-only, or qualify on a
larger-memory seat per the seat topology doctrine. QUALIFIED_IN_SCOPE was not
reachable because no declared bounded probe completed.
