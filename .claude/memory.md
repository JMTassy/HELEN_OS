# HELEN OS — Claude Memory

Auto-updated context that persists across sessions. Every major context update from the operator gets recorded here.

## Operator

- **Name**: Jean-Marie Tassy
- **Email**: jeanmarie.tassy@uzik.com
- **Role**: HELEN OS creator, sole operator, architect
- **Style**: Fast-moving, visual thinker, speaks in compressed directives. Uses WULmoji. Prefers action over discussion. Will paste large context dumps — mine them, don't ask for clarification.

## Project State (last updated: 2026-07-01)

### Architecture
- Five-layer constitutional AI with append-only governance kernel
- Two Python trees: `helen_os/` (sovereign) and `helen_os_scaffold/` (CLI/chat)
- Core invariant: NO RECEIPT = NO CLAIM
- 10 operator surfaces in `apps/helen-surface/` (HTML cockpits)
- Transport theory library in `transport/` (observation maps, fibers, drift algebra)
- Temple exploration layer: gardens, autoresearch, aura, goblin mode

### Active Branch
- `claude/code-review-optimizations-hx26jn` — 10 commits, clean
- Work: code review fixes, drift algebra, WULMOJI palette, math garden, skills

### Model Routing (amended 2026-07-01)
- **Planning (10%)**: Fable 5 — decompose, dispatch plans, stop_conditions
- **Gruntwork (80%)**: LOCAL via Ollama — zero marginal cost:
  - helen-gemma4-12b-32k/-64k (operator preferred default miner)
  - ORNITH ornith-helen:overlay-v3 → voice/doctrine/mining (v4 PASS, unpromoted)
  - GEMMA gemma4:latest/e2b/e4b → general gruntwork
  - DEEPSEEK deepseek-r1:14b → local reasoning (strip thinking blocks)
- **Verification (10%)**: Fable 5 — metal-check against spec before reporting
- **Cloud fallback**: Sonnet 5 only when local fails 2x or needs repo tools (Read/Grep/Bash)
- **Law**: Local default. 2 strikes → escalate. Generation-shaped → local first.

### Persona Model Map (metal-verified 2026-07-01)

| Persona | Primary Model | Fallback | Locus |
|---|---|---|---|
| HER (proposer) | qwen3.5:9b-ud-q4 | qwen3.5:9b → gemma4:latest | her_coder.py:33 |
| HAL (LLM reviewer) | gemma4:e2b | gemma4:e4b | hal_reviewer.py:40 |
| GOBLIN (mutator) | gemma4:latest | gemma4:e2b | goblin_mutator.py:39 |
| HELEN (narrator) | ornith-helen:v1 | gemma4:latest → template | helen_narrator.py:26 |
| JESTER | gemma4:e4b | — | jester.py:61 |
| CLAW (skills) | openclaw | + local ONNX TTS | claw.py:11 |
| KERNEL (C-layer) | qwen3.5:9b-ud-q4 | qwen3:14b → gemma4 chain | kernel_api.py:118 |
| CLI default | gemma4:latest | — | CLAUDE.md |

Model-LESS governance spine: HAL-gate (deterministic rules), MAYOR-gate (sig), REDUCER (only admission path), WITNESS, LEDGER, REPLAY, OPERATOR (sole sovereign).

### Key Findings This Session
- Anti-Goodhart: scanner risk_flags are orthogonal to what survives review pressure
- Zero-pressure baseline: without review pressure, variance collapses to 6-value categorical
- Survival law (corrected): among PROPOSED-lifecycle artifacts, structural survival tracks load-bearing dependency formation — self-declared canon bypasses this mechanism
- K-tau needle contradiction: `"datetime.now("` matches doc-mandated `datetime.now(timezone.utc)` — permanent Δ>0, operator-gated fix

### Visual Design Language
- Source Atlas doctrine: layered source field, not flat dashboard
- Palette: ⚫🔵🟣🟠🟢🟡⚪🔴 (8 colors, strict one-meaning-per-color)
- 7 locked visual motifs (6 original + 1 candidate mandala ring)
- Two surface aesthetics: dark CRT cockpit (home_v1) and warm sand/gold (helen2027, scored 9.2/10)
- Sacred geometry basis: Talmudic page + Dante vertical cosmology + cybernetic HUD

### Local GPU Training
- ornith-helen:v4 training converged (loss 2.5→0.897)
- In GGUF export/registration/eval-gate endgame
- Relay architecture: cloud writes prompts, local dispatches to GPU

## Operator Preferences

- Always use WULmoji in verdicts and summaries
- Never green-light non-admitted artifacts (WULMOJI rendering rule)
- Prefers receipts over explanations
- Sacred geometry resonates — Indian temple / pyramid temple aesthetic
- Cost-conscious: minimize API calls, maximize local GPU usage
- Two-agent separation: HELEN=architect/gate, HERMES=executor (anti-K2)

## Session Decisions Log

| Date | Decision | Context |
|---|---|---|
| 2026-07-01 | Skills system created | 7 slash commands + 3 agent defs for Fable loop engineering |
| 2026-07-01 | Compost egregor complete | CONFIRMED_WITH_CORRECTION, 4 repairs open |
| 2026-07-01 | Math garden 80 epochs | PROPOSED, NON_SOVEREIGN, deterministic hashes |
| 2026-07-01 | Kernel guard reconciled | 3 entries with dual-tier authorization citations |
| 2026-07-01 | Drift algebra shipped | AR-DRIFT-001, D1-D4 exhaustively witnessed |
| 2026-07-01 | WULMOJI palette locked | 3 namespaces, 14 disjointness tests |
| 2026-07-01 | Barbell amended: middle 80% fully local (helen-gemma4-12b preferred, ORNITH/GEMMA/DEEPSEEK) | Operator directive |
| 2026-07-01 | ornith-helen:v4 gate PASS, registered, unpromoted | Eval gate complete |
