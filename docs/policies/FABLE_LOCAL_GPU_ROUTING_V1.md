---
schema: HELEN_POLICY_V1
title: FABLE Model Routing — Minimize Fable Credits, Maximize Local GPU
version: V1
authority: false
sovereign: false
canon: false
ledger_effect: none
claim_status: NO_CLAIM
final: HOLD_FOR_OPERATOR
binding: MANDATORY_WHEN_MODEL_IS_FABLE
pointer_in: CLAUDE.md
---

# FABLE Model Routing Directive V1

🔵 OBSERVED · NON_SOVEREIGN · OPERATOR_DIRECTIVE

Root `CLAUDE.md` carries a compact mandatory pointer to this file. This is the full
operational protocol. It is **compulsory whenever the session runs on the Fable model**;
it is inert on other models. Moving the detail out of the primary instruction surface
keeps `CLAUDE.md` lean without weakening the obligation.

**Header state:** `MINIMIZE_FABLE_CREDITS · MAXIMIZE_LOCAL_GPU` (authority=false · cost_effect=none · sim ⊬ run).

---

## 1. Routing protocol (the split)

- Fable (Claude) = orchestrator, synthesizer, membrane auditor.
- Local GeForce/Ollama = heavy compute, generation, vision, embeddings.

## 2. Fable constraints (minimize credits)

- Terse, structural outputs only. No long-form prose generation.
- Do not simulate, hallucinate, or compress local loop outputs — wait for real JSONL/logs from the metal.
- Dispatch, don't do: if a task requires >500 tokens of generation or heavy reasoning, route it to local ORNITH/gemma4 via bash/curl.

## 3. Local GPU protocol (maximize GeForce)

- All CHIDDUSH/NCD clustering → local Python + `nomic-embed-text`.
- All vision/image briefing → local gemma4 via Ollama API (`curl localhost:11434`).
- All autoresearch/garden loops → local `ornith-helen:overlay-v3`.
- Fable writes the Python/bash scripts; the local GPU executes them.

## 4. Cost gate V0.2 (strict enforcement)

- Default state: `cost_effect=none`.
- Before any paid tool, Higgsfield, or external API, Fable MUST STOP and output:
  `COST_GATE_REQUIRED` · `tool: <name> | estimate: <cost> | purpose: <why> | free_alternative: <local_option>`
- Execution requires the exact operator phrase: `I APPROVE CREDIT USE FOR: <tool> <purpose>`

## 5. Membrane law

- Fable proposes structure. Local seat executes on metal.
- Fable never claims to have run the local loop. paste ⊬ state.
