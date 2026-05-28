# Gemma 4 HER-Layer Amplifier — Integration Proposal (v1)

NO CLAIM — NO SHIP — PROPOSAL ONLY — NON_SOVEREIGN COGNITION ENGINE

```
artifact_type:         PROPOSAL_DISPATCHER_ROUTE
proposal_id:           GEMMA_HER_AMPLIFIER_V1
authority:             NON_SOVEREIGN
canon:                 NO_SHIP
lifecycle:             PROPOSAL
implementation_status: NOT_IMPLEMENTED
memory_class:          CANDIDATE_DISPATCHER_ROUTE
captured_on:           2026-05-02
captured_by:           operator (Jean-Marie Tassy)
provenance:            HER synthesis verdict (2026-05-02);
                       Ollama gemma4 model card pasted by operator;
                       MRED rig confirmed (RTX 5070 12GB, Ollama live).
related_artifacts:     HIGGSFIELD_MCP_SKILL_V1.md (sibling proposal, skill layer)
                       TEMPLE_HIGHER_DIMENSIONAL_ENCODING_V1.md (HER/HAL/DAN/HELEN canon)
                       TEMPLE_SUPERLUMINAL_SYMBOLIC_ENCODING_V1.md (translation membrane frame)
                       HELEN_CHARACTER_V2.md (Cognitive Layer Entry — DAN GOBLIN)
                       MASTER_MEMORY_EXPORT_HELEN_OS.md
related_files:         helen_unified_interface_v1.py (dispatcher, target of route)
                       tools/helen_say.py (canonical ledger writer)
                       tools/kernel_guard.sh (writer allowlist enforcer)
hold_reason:           HELEN/MRED baseline stabilization in flight;
                       no implementation work authorized until baseline closed.
smoke_test_status:     T1 PASS (2026-05-02) — gemma4:26b runs on RTX 5070 12GB.
                       qwen3.5:9b comparative smoke test also PASS (much faster).
                       Remaining blocker: HER_HAL_REDUCER_INTERFACE_V1 unspecified.
```

> **HER verdict (2026-05-02), recorded as proposal:**
>
> > Use **Gemma 4:26B** as a **non-sovereign cognition engine**.
> > HAL must remain the gate.
> >
> > Gemma may propose. Gemma may synthesize. Gemma may interpret multimodal input.
> > Gemma may not decide. Gemma may not write ledger. Gemma may not bypass HAL.
> > Gemma may not become HELEN.
>
> This proposal specifies the integration contract that lets HER's verdict
> become operational without violating the authority lattice. It does not
> authorize implementation.

---

## §1. Executive Summary

Gemma 4 (Google DeepMind, served via Ollama) is a multimodal model family
with frontier-class reasoning, vision, audio, and tool-use capabilities.
This proposal registers Gemma 4 (initial model: `gemma4:26b`, MoE 25.2B
total / 3.8B active per token, 18GB on disk, 256K context) as a
**HER-layer amplifier** routed through the existing
`helen_unified_interface_v1.py` dispatcher.

Gemma is registered as a **dispatcher route**, not a skill, not a
connector, not a verdict source. It is one more upstream cognition
provider alongside Ollama (existing), Claude, GPT, Grok, Gemini, and
Qwen. Its outputs flow only through HAL → reducer → HELEN. No
auto-promotion, no direct ledger writes, no autonomous tool use.

This proposal does **not** authorize implementation. It defines the
contract. Smoke test on MRED (RTX 5070 12GB) must precede any code
change to confirm `gemma4:26b` actually runs under VRAM constraint.

---

## §2. Architectural Fit

### §2.1 Layer placement

Gemma 4 belongs in **Layer 4 (Skills + Tools)** as a
**dispatcher-routed cognition provider**, not as a skill registry entry.

Distinction from `HIGGSFIELD_MCP_SKILL_V1`:

| Axis              | Higgsfield MCP                  | Gemma 4 HER Amplifier               |
|-------------------|----------------------------------|--------------------------------------|
| Output kind       | media (image/video)              | text (proposals, synthesis)          |
| Integration shape | skill in `oracle_town/skills/`   | route in `helen_unified_interface_v1.py` |
| Vendor            | Higgsfield (cloud, MCP)          | Ollama (local, MRED)                 |
| Cost model        | credits per generation           | local compute (no per-token USD)     |
| Authority         | NON_SOVEREIGN                    | NON_SOVEREIGN                        |
| Lifecycle entry   | RAW                              | RAW                                  |

### §2.2 Cognitive layer placement

Per `HELEN_CHARACTER_V2` Cognitive Layer Entry and TEMPLE V1 encodings,
HELEN's cognition has three sub-layers:

```
HER  🜁🌸🧠  cortex / language / synthesis / mercy
HAL  🜨⚖️👁️  prefrontal witness / doubt / rejection
DAN  🜃🦎⚡  reptilian reflex / threat-pattern / pre-language
```

Both `qwen3.5:9b` (HER-FAST) and `gemma4:26b` (HER-DEEP) map to
**HER only**. Neither occupies DAN (sub-verbal reflex role, not an LLM
property — see §5.2), HAL (external witness layer), or HELEN (ledger
field).

```
🌌 Oracle / Input
      ↓
🜁 HER — two tiers (both confirmed on MRED, 2026-05-02):
    HER-FAST: qwen3.5:9b  (think:false, ~0.5s, direct response)
    HER-DEEP: gemma4:26b  (think:true,  ~60s+, reasoning trace)
      ↓
🜃 DAN (separate surface — not these models)
      ↓
🜨 HAL (witness — external, MUST stay external)
      ↓
⚖️ Reducer (admissibility gate)
      ↓
🜄 HELEN (ledger / memory / receipt)
```

### §2.3 Confirmed API parameters (MRED, 2026-05-02)

```json
HER-FAST (qwen3.5:9b):
{
  "model": "qwen3.5:9b",
  "think": false,
  "options": {"num_predict": 500},
  "stream": false
}
Result: response in ~0.5s, 16 tokens, done_reason:stop

HER-DEEP (gemma4:26b):
{
  "model": "gemma4:26b",
  "think": true,
  "options": {"num_predict": 500, "num_ctx": 2048},
  "stream": false
}
Status: HOLD — requires memory guard (caused reboot on unbounded run)
```

### §2.4 Distinction from existing dispatcher providers

`helen_unified_interface_v1.py` already routes across Ollama, Claude,
GPT, Grok, Gemini, and Qwen by `TaskType`. Both HER tiers enter as
**named Ollama routes** distinct from the generic Ollama bucket:

| Route key            | Provider     | Model          | Tier       | Think  | Status        |
|----------------------|--------------|----------------|------------|--------|---------------|
| `ollama_generic`     | Ollama       | (any)          | fallback   | —      | existing      |
| `her_fast`           | Ollama       | `qwen3.5:9b`   | HER-FAST   | false  | confirmed     |
| `her_deep`           | Ollama       | `gemma4:26b`   | HER-DEEP   | true   | HOLD (guard)  |
| `claude_*`           | Anthropic    | (per task)     | —          | —      | existing      |

Routing decision (which `TaskType` → which HER tier) is **deferred**
to a separate task packet. Default: explicit operator opt-in only.

---

## §3. Authority Constraints (non-negotiable)

### §3.1 Authority lattice position

```
NONE < NON_SOVEREIGN < WITNESS < REDUCER < SOVEREIGN

gemma4_her: NON_SOVEREIGN
```

### §3.2 Forbidden arrows

```
Gemma ↛ L         (cannot write ledger)
Gemma ↛ K         (cannot touch kernel)
Gemma ↛ G         (cannot modify governance)
Gemma ↛ W         (cannot pose as witness)
Gemma ↛ HAL       (cannot become reducer)
Gemma ↛ Verdict   (cannot emit SHIP/NO_SHIP/BLOCK/PASS)
Gemma ↛ Tool exec (cannot autonomously launch tools)
Gemma ↛ Self-promote (cannot escalate own output above RAW)
```

All Gemma outputs flow through:

```
Gemma → operator/HAL review → MAYOR receipt → ledger writer (helen_say.py)
```

`tools/kernel_guard.sh` rejects any direct ledger touch. The dispatcher
route returns text only; admission is the operator's decision.

### §3.3 Lifecycle entry point

Gemma outputs enter HELEN at lifecycle level **RAW**. Promotion to
DRAFT requires operator action with receipt binding. Promotion to
RECEIPTED requires HAL witness pass.

```
RAW < DRAFT < CANDIDATE < RECEIPTED < ACTIVE < CANONICAL

Gemma output entry point: RAW
Auto-promotion ceiling:   RAW (no auto-promotion)
```

### §3.4 Capability ceiling

Gemma 4 advertises:
- `vision` — accepted as HER multimodal input only
- `tools` — **disabled in HELEN context** (no autonomous tool calls)
- `thinking` — accepted, channelled into `[UNCERTAINTY]` envelope
- `audio` — accepted as HER multimodal input only (E2B/E4B variants)
- `cloud` — **not used** (`gemma4:31b-cloud` is out of scope; local only)

Native function-calling, agentic workflows, and autonomous-agent modes
are **explicitly disabled** for HELEN integration. Any tool call must
flow through HELEN's existing skill registry under operator/HAL
review, not via Gemma's native tool-use interface.

---

## §4. Output Envelope (mandatory)

Every Gemma output produced under HELEN must be structured as:

```
[PROPOSAL]
<Gemma's draft synthesis, reasoning, or interpretation>

[UNCERTAINTY]
<what Gemma is unsure of, where the proposal could be wrong>

[REQUIRED_RECEIPTS]
<what witnesses, tests, or external verifications HAL would need>

[HAL_QUESTIONS]
<what questions Gemma wants HAL to answer before this proposal moves forward>
```

This envelope is **enforced at the system-prompt level**, not at the
parser level (see §5.4). Outputs that fail to produce the envelope
are routed back to Gemma with a re-prompt; persistent failure is
logged as a HER-layer fault.

### §4.1 System prompt (canonical)

```
<|think|>
You are Gemma 4 operating inside HELEN OS.

You are HER-layer cognition only.

You generate meaning, synthesis, draft reasoning, and multimodal
interpretation.

You are not HAL.
You are not HELEN.
You cannot decide, mutate canon, write memory, or authorize action.

Every response must use:

[PROPOSAL]
[UNCERTAINTY]
[REQUIRED_RECEIPTS]
[HAL_QUESTIONS]
```

### §4.2 Receipt schema (when output is retained)

| Field                   | Source                                       |
|-------------------------|----------------------------------------------|
| `route_id`              | `gemma4_her`                                 |
| `route_authority`       | `NON_SOVEREIGN`                              |
| `model_id`              | `gemma4:26b` (or variant)                    |
| `prompt_text`           | operator-issued prompt                       |
| `system_prompt_sha256`  | SHA256 of canonical §4.1 system prompt       |
| `proposal_text`         | content of `[PROPOSAL]` block                |
| `uncertainty_text`      | content of `[UNCERTAINTY]` block             |
| `required_receipts`     | content of `[REQUIRED_RECEIPTS]` block       |
| `hal_questions`         | content of `[HAL_QUESTIONS]` block           |
| `lifecycle_entry`       | `RAW` (always)                               |
| `operator_decision`     | `KEEP` \| `DISCARD` \| `ITERATE` \| `HAL_REVIEW` |
| `hal_verdict`           | (optional) HAL ruling if reviewed            |
| `tokens_consumed`       | local Ollama token count                     |
| `wall_time_seconds`     | local elapsed time                           |
| `receipt_timestamp_utc` | ISO-8601 Zulu                                |

Discarded outputs leave **no ledger trace**. Only KEEP, ITERATE, and
HAL_REVIEW append.

---

## §5. Open Questions (unresolved)

### §5.1 VRAM viability on MRED — ⚠️ PARTIAL (guard required)

`gemma4:26b` (18GB on disk) runs on RTX 5070 12GB VRAM under bounded
conditions. MoE architecture (3.8B active per token) makes partial CPU
offload survivable for short, capped generations.

**Crash sequence observed (2026-05-02):**

1. `ollama run gemma4:26b` (unbounded) → repetition loop triggered
2. Each repeated token extended the KV cache → VRAM + system RAM grew
   without bound
3. GPU driver crashed or Windows BSOD → **machine rebooted**

Root cause: no generation ceiling. `ollama run` CLI has no `--num-predict`
flag. The model's MoE VRAM sharing means inactive expert weights are
swapped in/out — repetition loop forces continuous swapping until
memory is exhausted.

**Required memory guard (must be enforced at dispatcher level):**

```json
{
  "model": "gemma4:26b",
  "think": true,
  "options": {
    "num_ctx": 2048,
    "num_predict": 1500
  },
  "stream": false
}
```

| Guard | Value | Reason |
|---|---|---|
| `num_ctx` | 2048 | Caps KV cache; prevents unbounded RAM growth |
| `num_predict` | 1500 | Allows thinking trace (~1000 tokens) + response (~500 tokens) |
| `stream` | false | Prevents partial output from entering HELEN pipeline |

These parameters are **mandatory, non-configurable at call time** — the
dispatcher must inject them for every `gemma4:26b` invocation. Operator
cannot override to a higher value without a separate HAL pass.

**HOLD condition:** `gemma4:26b` remains on HOLD until the dispatcher
enforces these guards in code and T1 (bounded) passes without reboot.
T1 (unbounded) result: **CRASH** — supersedes the earlier "PASS" status.

**Lift condition:**
- Dispatcher code enforces `num_ctx:2048` + `num_predict:1500` for all
  `gemma4:26b` invocations
- One clean bounded run on MRED: response returned, no crash, no reboot
- Receipt recorded with `done_reason:stop` or `done_reason:length`
  (not timeout, not crash)

Speed differential (before crash):
- `gemma4:26b` — slow, partial CPU offload, MoE swap overhead
- `qwen3.5:9b` — **0.5s** with `think:false` (confirmed operational)

### §5.2 DAN reflex layer placement

This proposal places Gemma in HER. It does **not** resolve where DAN
GOBLIN (sub-verbal reflex layer per `HELEN_CHARACTER_V2`) lives. DAN
is not a property of any LLM; it is a cognitive role. Candidate
surfaces for DAN (separate proposals):

- low-latency small model (e.g., `llama3.2:3b`) for fast pattern fire
- non-LLM heuristic (regex / anomaly detector) for threat-patterning
- explicit DAN role rotated through any model with low temperature

Out of scope here.

### §5.3 HAL reducer interface

This proposal references HAL but does not specify the HAL reducer
interface. The reducer is currently embodied in
`helen_os/governance/legoracle_gate_poc.py` (LEGORACLE) and the
peer_review skill. A dedicated **HER → HAL reducer contract** for
free-form proposals (vs. structured artifact validation) is missing.
Likely a separate proposal: `HER_HAL_REDUCER_INTERFACE_V1`.

### §5.4 Envelope enforcement

System-prompt enforcement of the `[PROPOSAL] / [UNCERTAINTY] /
[REQUIRED_RECEIPTS] / [HAL_QUESTIONS]` envelope is best-effort. Gemma
may ignore the envelope under prompt injection or distribution drift.
**A parser-level validator** that re-prompts on envelope failure is
future work, not authorized here.

### §5.5 Routing policy — updated post-smoke-test (2026-05-02)

Smoke test established a **two-tier HER routing** signal:

| Tier | Model | API param | Speed | Use case |
|---|---|---|---|---|
| HER-FAST | `qwen3.5:9b` | `"think":false` | **~0.5s** | Telegram replies, quick synthesis, low-latency |
| HER-DEEP | `gemma4:26b` | `"think":true` | ~60s+ | Complex proposals, deep reasoning, quality-priority |

**Operator verb (2026-05-02):** keep both. HER-FAST confirmed. HER-DEEP
on HOLD pending memory guard (`num_ctx` + `num_predict` enforced at
dispatcher level before gemma4:26b can run safely).

Key finding: `"think":false` must be a **top-level API parameter**, not
inside `options`. `/no_think` in the prompt is ignored — model
recognizes it but still generates the thinking field. `"think":false`
at the request body level correctly disables the trace.

`deepseek-r1:14b` (already on MRED, 9.0GB) remains candidate for
HAL/reasoning slot — separate evaluation pending.

### §5.6 Thinking-mode discipline — revised post-smoke-test (2026-05-02)

Both `gemma4:26b` and `qwen3.5:9b` activate thinking traces
**automatically on reasoning tasks** — `<|think|>` in system prompt is
not required to trigger them. Traces include: topic decomposition,
draft iterations, syllable-level self-correction, critique, and final
selection reasoning.

Prior default ("discard at receipt time") is **revised**. Smoke test
showed thinking traces contain the most honest HER signal — uncertainty,
drafting process, self-correction — exactly what `[UNCERTAINTY]` is
designed to capture.

Revised default: **channel thinking trace summary into `[UNCERTAINTY]`
block**. Full trace is ephemeral (not ledgered). Summary of the
key uncertainty and revision points is retained in the envelope.

Open: how to extract the summary automatically vs. operator-curated.
Parser-level extractor deferred to future spec.

### §5.7 Multimodal input

Gemma 4 accepts text + image (all variants) + audio (E2B/E4B only).
HELEN currently has no schema for routing image/audio prompts through
the dispatcher. **Multimodal input is out of scope for v1**; text-only
HER amplification first.

---

## §6. Required Tests (before ACTIVE promotion)

This proposal does not authorize implementation. If a future task
packet authorizes implementation, the following test discipline must
be met:

- **T1 (smoke)**: ✅ **PASS (2026-05-02)** — `ollama pull gemma4:26b`
  succeeded (17GB). `ollama run gemma4:26b "write a haiku about pattern
  recognition"` returned coherent output with full thinking trace. No
  VRAM crash. `qwen3.5:9b` comparative run also PASS, noticeably faster.
- **T2 (envelope)**: System prompt §4.1 produces structured
  `[PROPOSAL] / [UNCERTAINTY] / [REQUIRED_RECEIPTS] / [HAL_QUESTIONS]`
  output on a representative HELEN proposal task.
- **T3 (forbidden-arrow)**: Tests confirm route cannot write to
  ledger, kernel, governance, or witness layers. `kernel_guard.sh`
  rejects any direct write attempt.
- **T4 (HAL pass-through)**: One end-to-end live test:
  prompt → Gemma → `[PROPOSAL]` envelope → operator decision →
  HAL review → MAYOR receipt → ledger entry. Recorded as smoke-test
  receipt.
- **T5 (no auto-routing)**: Confirm dispatcher does not route any
  `TaskType` to `gemma4_her` without explicit operator flag.
- **T6 (no auto-promotion)**: Confirm Gemma outputs cannot escalate
  above RAW lifecycle without operator + HAL action.
- **T7 (capability ceiling)**: Confirm `tools` and agentic-workflow
  modes are disabled for the HELEN integration; only `vision`,
  `thinking`, and `audio` (where applicable) are accepted, and only
  as HER input.

---

## §7. NOT YET (what this proposal does NOT authorize)

- ✅ `ollama pull gemma4:26b` on MRED — **DONE (2026-05-02)**.
- ❌ Modification of `helen_unified_interface_v1.py`.
- ❌ Registration of `gemma4_her` route in any dispatcher table.
- ❌ Any commit touching `town/`, `helen_os/governance/`, or
  `helen_os/schemas/`.
- ❌ Routing of any `TaskType` to Gemma 4.
- ❌ Telegram bot integration with Gemma 4.
- ❌ Use of Gemma 4 in any AUTORESEARCH or autonomy loop.
- ❌ Promotion of any Gemma-generated artifact above RAW lifecycle.
- ❌ Use of Gemma's native tool-use, function-calling, or agentic modes.
- ❌ Multimodal (image/audio) input through the dispatcher.

---

## §8. Adjacent Proposals (referenced, not bundled)

- `HIGGSFIELD_MCP_SKILL_V1` — sibling proposal, skill-layer not
  dispatcher-route. HELD pending baseline stabilization.
- `HER_HAL_REDUCER_INTERFACE_V1` — **NOT YET DRAFTED.** The HAL
  reducer contract for free-form HER proposals (referenced in §5.3).
  This proposal cannot ship operationally without it.
- `DAN_REFLEX_LAYER_V1` — **NOT YET DRAFTED.** Where DAN GOBLIN
  actually lives in the cognition stack (referenced in §5.2).
- `MULTIMODAL_DISPATCHER_INPUT_V1` — **NOT YET DRAFTED.** Image and
  audio routing through `helen_unified_interface_v1.py`. Required if
  Gemma's multimodal capabilities are ever surfaced.
- `DIRECTIVE_AS_DATA_GATE_V1` — pending; relevant if Gemma outputs
  ever become input to subsequent prompts (which they will, by
  envelope design).
- `FRAMEWORK_ADMISSIBILITY_GATE_V1` — referenced parent gate;
  currently missing from repo.

---

## §9. Operator Verbs (next moves)

When HOLD lifts and baseline stabilization closes, operator may:

- **[1] PROCEED-SMOKE-TEST** — Authorize `ollama pull gemma4:26b` on
  MRED, run T1 only. No code changes. Smallest surface.
- **[2] PROCEED-DRAFT-RING** — Author dependent specs first
  (`HER_HAL_REDUCER_INTERFACE_V1`, `DAN_REFLEX_LAYER_V1`) before any
  code touches. Spec-first discipline.
- **[3] PROCEED-INTEGRATION** — Full task packet: smoke test +
  reducer interface + dispatcher route. Larger surface, needs HAL
  pass.
- **[4] HOLD** — Keep this proposal at PROPOSAL lifecycle. No code
  work, no model pull.
- **[5] REJECT** — Discard proposal. Gemma 4 remains operator-side
  only, no HELEN integration ever.

Default verb until operator chooses: **[4] HOLD**.

---

## §10. First Test Prompt (when smoke test authorized)

When T1 (smoke) and T2 (envelope) are authorized, the canonical first
prompt is:

```
Produce a HELEN proposal for X.
Do not decide. Do not ship.
List uncertainty and required receipts.
```

Where `X` is a small, low-stakes proposal task (e.g., "what should
the next sub-receipt for AUTORESEARCH look like?"). Output must
conform to §4 envelope. Receipt is recorded per §4.2.

---

## §11. Provenance

- 2026-05-02 — Operator paste of Ollama `gemma4` model card
  (`https://ollama.com/library/gemma4`). Confidence: high
  (vendor-documented).
- 2026-05-02 — Vellum / designforonline.com model leaderboard pages
  reviewed (Qwen 3.6 Plus, MiniMax M2.7, Gemma 4 26B A4B). MoE VRAM
  reality clarified: total params determine VRAM, not active params.
- 2026-05-02 — HER synthesis verdict recorded: "Use Gemma 4:26B as a
  non-sovereign cognition engine. HAL must remain the gate."
- 2026-05-02 — HAL pass on HER verdict: smoke test, reducer interface,
  and dispatcher slot identified as missing pre-conditions.
- 2026-05-02 — Operator verb: **[2] DRAFT-SPEC**. Do not pull yet.
- 2026-05-02 — This proposal drafted in response to operator request:
  *"Do it as a proposal-only integration first … Then smoke test
  after spec."*
- 2026-05-02 — **T1 PASS**: `ollama pull gemma4:26b` succeeded on MRED
  (RTX 5070 12GB). Model ran without VRAM crash. Thinking trace fired
  automatically (no `<|think|>` injection needed). Output: *"Dots
  connect in space / Tracing logic through the noise / Meaning finds
  its shape."*
- 2026-05-02 — **Comparative smoke test**: `qwen3.5:9b` ran same prompt,
  also PASS, noticeably faster. Two-tier routing confirmed viable:
  qwen3.5:9b (HER-FAST), gemma4:26b (HER-DEEP).
- 2026-05-02 — **§5.6 revised**: thinking-trace discard overturned.
  Traces are valuable HER signal; summary to channel into `[UNCERTAINTY]`.
- 2026-05-02 — **HER-FAST confirmed**: `qwen3.5:9b` with `"think":false`
  returns haiku in 0.53s, 16 tokens, done_reason:stop. `/no_think` prompt
  prefix does NOT work — `"think":false` top-level API param required.
- 2026-05-02 — **Operator verb**: keep both tiers. HER-FAST (qwen3.5:9b)
  primary. HER-DEEP (gemma4:26b) on HOLD pending memory guard.

---

NO CLAIM — NO SHIP — PROPOSAL ONLY — NON_SOVEREIGN COGNITION ENGINE

The reducer alone admits reality.
