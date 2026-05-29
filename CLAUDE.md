# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

HELEN OS is a five-layer constitutional AI companion with an append-only governance kernel. The system is built on a single invariant: **NO RECEIPT = NO CLAIM**.

## Architecture Layers

### Layer 1: Constitutional Membrane
- `helen_os/governance/` — schema registry, validators, ledger validator, LEGORACLE gate, skill promotion reducer
- `oracle_town/kernel/` — daemon (Unix socket), gates A/B/C, mayor, ledger
- Sovereign: only this layer emits verdicts (SHIP/NO_SHIP/BLOCK/PASS)

### Layer 2: Append-Only Ledger
- `town/ledger_v1.ndjson` — hash-chained, cum_hash integrity
- `tools/helen_say.py` — canonical writer (payload_hash = sha256(canon(payload)))
- `tools/ndjson_writer.py` — kernel boundary writer
- **Admissibility**: `helen_say.py` → `ndjson_writer.py` is the only admitted path. Direct appends to `town/ledger_v1.ndjson` are forbidden and rejected by `tools/kernel_guard.sh`.

### Layer 3: Execution + Autonomy
- `helen_os/executor/` — bounded executor (non-sovereign: runs tasks, emits envelopes, no verdicts)
- `helen_os/autonomy/` — autoresearch step/batch, skill discovery
- `helen_os/evolution/` — failure bridge (typed failures only)

### Layer 4: Skills + Tools
- `oracle_town/skills/` — map generator, meteo, claim workflow, conquest integration, ledger reader
- `oracle_town/skills/feynman/` — peer_review, intent_action_audit, session_notes (fused 2026-04-16)
- `oracle_town/skills/voice/gemini_tts/` — Zephyr voice, Gemini 2.5 Flash TTS (LIVE)
- `oracle_town/skills/video/hyperframes/` — HyperFrames video renderer (DECLARED)
- `tools/helen_telegram.py` — two-way Telegram bot with voice
- `tools/helen_simple_ui.py` — web UI at localhost:5001 with voice

### Layer 5: TEMPLE Exploration
- Non-sovereign generative layer
- `helen_dialog/` — dialog engine, HER/AL moment detection

## Governance Artifacts

### `GOVERNANCE/CLOSURES/`
- Contains `CLOSURE_RECEIPT_V1` only — strict format
- Each closure requires: per-claim artifact SHA verification, proposer ≠ validator, missing artifact binding forces BLOCK
- Ghost closure detector validates these

### `GOVERNANCE/TRANCHE_RECEIPTS/`
- Contains `TRANCHE_SUB_RECEIPT_V1` — one hypothesis per epoch
- AUTORESEARCH tranche receipts live here

## Gates

| Gate | File | What it checks |
|---|---|---|
| K8 Non-Determinism Boundary | `scripts/helen_k8_lint.py` (v1.2) | mu_NDWRAP (AST scope), mu_NDARTIFACT (provenance sidecars), mu_NDLEDGER (hash integrity) |
| K-tau Coherence | `scripts/helen_k_tau_lint.py` | mu_BOUNDARY, mu_IO, mu_DETERMINISM, mu_ALLOWLIST, mu_SCHEMA |
| K-rho | `scripts/helen_rho_lint.py` | Numeric consistency of rho traces |
| K-wul | `scripts/helen_wul_lint.py` | Canonical WUL compile+validate (oracle_town compiler) |
| LEGORACLE | `helen_os/governance/legoracle_gate_poc.py` | Obligation checking, deterministic SHIP/NO_SHIP, replay-gated (E12) |
| Kernel Guard | `tools/kernel_guard.sh` | Only allowed writers may touch ledger |
| Doctrine Admission (DRAFT) | `DOCTRINE_ADMISSION_PROTOCOL_V1` + fixtures | §4 gate for doctrine-class artifacts; fixtures landed, gate not yet active |

## PULL-Mode Tranche Discipline

AUTORESEARCH operates under PULL-mode:
- **One hypothesis per epoch** — observable signals only, no speculative ideas
- **Non-sovereign layers only** — kernel, memory, identity, ledger, replay are NOT mutation targets
- **Bounded tranches** — HAL gate + tranche sub-receipt + MAYOR re-rank between tranches
- **7-field receipt per epoch**: carry-forward state, hypothesis, experiment, metric, failure mode, keep/reject rule, upgrade path
- **Halt discipline** — tranche seals before next opens

## Schema Authority

- **Canonical**: `helen_os/governance/schema_registry.py` → `helen_os/schemas/` (66 files as of 2026-05-23; all parse as valid JSON per E23 SE4)
- **Legacy (deprecated, 0 consumers)**: `helen_os/schema_registry.py`, `helen_os/validators.py`
- **Governance audit tools**: `helen_os/governance/schema_index_audit.py` (dual-recognizer), `helen_os/governance/root_schemas_consumer_audit.py` (runtime/doc/orphan classifier)
- Root `schemas/` does **not exist in this branch's git history** (verified E21, 2026-05-23). The earlier "19 ORPHAN_ZERO_REF files" claim was a cross-session reference to `~/Documents/GitHub/helen_os_v1/` (the parallel session at cum_hash `b3415eb3edfb`); see Cross-Session Contamination below.

## Key Invariants

- `NO RECEIPT = NO CLAIM` — every action produces a hash-chained ledger entry
- `NO HASH = NO VOICE` — K8 corollary: ND output never enters spine unhashed
- `additionalProperties: false` on all constitutional schemas — forbidden fields rejected at schema level
- Proposer ≠ Validator — peer_review enforces K2/Rule 3
- Termination is sacred — SHIP or ABORT only, no open-ended pauses
- **Governance edit rule** — direct edits to `helen_os/governance/**` and `helen_os/schemas/**` require a prior proposal in `docs/proposals/` with operator authorization. Gate additions count as governance contract changes. (`docs/proposals/HUMAN_SEAL_OVERRIDE_GATES_V1.md` retroactively satisfies this rule for commit `284b347`.)

## Test Suite

There are **two test trees** with different scopes:

- `helen_os/tests/` — autoresearch, ledger validator, LEGORACLE replay gate, bounded executor, etc. This is what `make test` runs.
- `tests/` (repo root) — numbered constitutional invariants (`test_1_mayor_only_writes_decisions.py` … `test_9_mayor_io_allowlist.py`) plus `governance_regression/`. **Not covered by `make test`** — invoke explicitly, e.g. `.venv/bin/pytest tests/ -q`.

Commands:

- `make test` — authoritative for `helen_os/tests/` only. Do not rely on stale test counts pinned here — run the suite.
- `make membrane-test` — ledger validator + autoresearch bounded/deterministic + no-local-replay-shadowing
- `make anti-regression` — replay divergence check (single-test-file, verbose)
- Single test: `.venv/bin/pytest helen_os/tests/test_foo.py::test_bar -v`
- K8 target: PASS (k8=+1.000)
- LEGORACLE replay gate: fixture integrity + determinism + frozen output + mutation detection

**Caveats** (verified E23 SE3 / SE13 / SE15, 2026-05-23):
- `Makefile:5` hardcodes `PYTHONPATH` to an operator-specific Mac path (`/Users/jean-marietassy/Desktop/JMT CONSULTING - Releve 24`). Tests fail to import modules on any other host until this is replaced.
- **18 collection errors** in `helen_os/tests/` if pytest's Python lacks `jsonschema`. On systems using `uv`-managed pytest (e.g. `/root/.local/bin/pytest` backed by `/root/.local/share/uv/tools/pytest/bin/python`), install into THAT Python: `<uv-pytest-python> -m pip install jsonschema`.
- **7 deterministic failures** in `test_init_determinism_against_chaos` share root cause `helen_os/api/init_helen_wedge.py:229 ModuleNotFoundError`. Open carrier issue.
- **`tools/helen_say.py` SyntaxError at line 256** (f-string unmatched paren in a macOS dialog code path) — **REPAIRED in this tree** (`claude/launch-helen-os-0xZXH`), verified 2026-05-29: `py_compile` and `import` both pass; fix extracts the escape into `escaped_msg` (lines 254–260). May still be broken in the parallel `helen-os-jmtc` tree; cross-tree status not verified.

## Running HELEN

Prefer `.venv/bin/python` for runtime commands so imports resolve consistently with `make test`. If `.venv` is absent (some environments do not provision it), use the system `python` with `PYTHONPATH=.` and a separately-installed `pytest` (e.g. `/root/.local/bin/pytest`). Substitute accordingly in the examples below.

```bash
# Start kernel daemon (background)
.venv/bin/python oracle_town/kernel/kernel_daemon.py &

# Interactive CLI
.venv/bin/python tools/helen_cli.py

# Web UI with voice
GEMINI_API_KEY=... .venv/bin/python tools/helen_simple_ui.py
# → http://localhost:5001

# Telegram bot (two-way voice dialogue)
GEMINI_API_KEY=... .venv/bin/python tools/helen_telegram.py

# One-shot sovereign-routed message (canonical writer)
.venv/bin/python tools/helen_say.py "your message" --op fetch

# TTS (Zephyr, Gemini 2.5 Flash)
GEMINI_API_KEY=... .venv/bin/python oracle_town/skills/voice/gemini_tts/helen_tts.py "text"

# K8 lint
.venv/bin/python scripts/helen_k8_lint.py --mode all_nd

# K-wul lint (canonical WUL compile+validate)
.venv/bin/python scripts/helen_wul_lint.py /path/to/slab.json

# Full test suite
make test

# Ledger writer guard (run before any suspected direct-ledger write)
bash tools/kernel_guard.sh
```

### Packaging note
`pyproject.toml` declares the project as `oracle-town` v1.0.0 with `dependencies = []` — it is not the dependency source of truth. Use `requirements.txt` / `requirements-ci.txt` when installing.

## Roles

HELEN's cognition operates as named roles, not personal identities. Each role has a defined authority surface; crossing the surface is a constitutional breach.

- **GOBLIN** — non-sovereign operational persona. `GOBLIN_CLARITY = Tool + Command + Log + Receipt`. May inspect, test, write receipts. May NOT claim sovereignty, mutate canon, or emit verdicts. (Role defined operationally 2026-05-23; formal proposal `GOBLIN_ROLE_V1` is in `CHIDDUSH_BOTTLE_V0` roadmap #8.)
- **HER** — generative / visionary cognition layer. Per `GEMMA_HER_AMPLIFIER_V1`, HER may be served by local LLM (qwen3.5:9b HER-FAST, gemma4:26b HER-DEEP) under strict envelope discipline.
- **HAL** — critical / poison-detection layer. Per `HYPERSTITION_FIREWALL_V0 §2.2`, HAL_GOBLIN enumerates poison patterns (godmode_language, coercive_propagation, reality_control_claim, ai_sentience_claim, ...). HAL flags; HAL does not decide.
- **DAN** — reflex / sub-verbal pattern layer per `HELEN_CHARACTER_V2`. Not an LLM property; a cognitive role. Placement TBD (see `DAN_REFLEX_LAYER_V1` — not yet drafted).
- **MAYOR** — sovereign SHIP / NO_SHIP authority. Functional title, not personal name.
- **REDUCER** — admission gate into canon. Only REDUCER admits into the ledger.

## Halt Discipline (`HALT_BOUNDARY_DISCIPLINE_V0`, commit `5d0e04e`)

Every non-sovereign receipt that defers work to a sovereign actor MUST declare the halt explicitly in a section headed "Halt boundary" and enumerate the required inputs to resume. Implicit handoffs are not handoffs. This is now canonical across `docs/proposals/`, `GOVERNANCE/TRANCHE_RECEIPTS/`, and any new artifact GOBLIN produces. CI enforcement (a script scanning for required §) is not yet wired — paper invariant until enforcement lands.

## Cross-Session Contamination (per E22 meta-finding)

`GOVERNANCE/TRANCHE_RECEIPTS/` contains tranche receipts whose evidence was authored against a **parallel session** (`~/Documents/GitHub/helen_os_v1/`, cum_hash `b3415eb3edfb`) rather than this branch (`claude/launch-helen-os-0xZXH`). Confirmed phantom in this tree:
- `E20.open_seams.SEAM-001-C12` (audited E21, `2fa41cc`) — schemas/ never existed here
- `E20.open_seams.Knowledge_Compiler_V2_ratification` (audited E22, `a598769`) — commit `6eede55` doesn't exist on any branch

Contamination scope per E23 SE8: **≥10 files** reference parallel session by known markers; real scope likely larger. **Any future epoch sourcing hypothesis from `E20.open_seams` (or analogous fields in older receipts) without independent tree-truth verification is operating on parallel-session evidence by default.** New proposal `CROSS_SESSION_FIELD_ATTRIBUTION_V0` flagged but not yet bottled.

## Identity Gate Stack (shipped 2026-05-23)

Six-artifact constitutional layer for governed generative media:

- `docs/theory/CONSTITUTIONAL_MANIFOLD_RENDERING_V0.md` — parent theory
- `docs/proposals/HELEN_IDENTITY_GATE_V1.md` — doctrine
- `docs/proposals/IDENTITY_GATE_PSEUDOCODE_V0.md` — algorithm contract (G1→G2→G3→G4 with skipped-stage marking and Phase 2 Manual Gate reference pattern)
- `docs/proposals/IDENTITY_GATE_RECEIPT_V1.md` + `IDENTITY_GATE_RECEIPT_V1_SEQUENCE.md` — schemas (12/12 tests green)
- `docs/proposals/MEDIA_RECEIPT_V1.md` — parent envelope (10/10 tests green)

NON_SOVEREIGN, NO_SHIP. Implementation (Phase 1: `tools/hash_render_artifact.py`) not yet started. Unblocks video backends (Seedance/HeyGen/Kling) once Phase 1 lands.

## Chiddush Roadmap (`CHIDDUSH_BOTTLE_V0`)

10-item proposal roadmap synthesized from HER+HAL brainstorm. As of 2026-05-23: 1/10 bottled.

```
✅ #1  HALT_BOUNDARY_DISCIPLINE_V0     (Tier 1, parallel-safe)
□  #2  RECEIPT_EMISSION_INVARIANT_V0   (Tier 1, parallel-safe)
□  #3  DOC_DRIFT_REGISTER_V0           (Tier 2)
□  #4  DOCTRINAL_DIFF_PROTOCOL_V0      (Tier 2)
□  #5  MANUAL_GATE_PATTERN_V0          (Tier 2)
□  #6  LIFECYCLE_TAXONOMY_V0           (Tier 3, prereq for #7)
□  #7  RECONNAISSANCE_RECEIPT_V0       (Tier 3, deps on #6)
□  #8  GOBLIN_ROLE_V1                  (Tier 4)
□  #9  DOCTRINE_LINK_CHECK_V0          (Tier 5, prereq for #10)
□  #10 PSEUDOCODE_TIER_DOCTRINE_V0     (Tier 5, deps on #9)
```

Deferred: `SELF_CORRECTING_RECEIPT_PATTERN_V0` (needs termination rule).

## Gemma Integration

- `docs/proposals/GEMMA_HER_AMPLIFIER_V1.md` — full proposal at `lifecycle: PROPOSAL`, `implementation_status: NOT_IMPLEMENTED`. T1 smoke test PASSED on MRED (RTX 5070 12GB) 2026-05-02. `qwen3.5:9b` (HER-FAST) confirmed; `gemma4:26b` (HER-DEEP) on HOLD pending dispatcher-level memory guards (`num_ctx:2048`, `num_predict:1500`).
- `docs/proposals/HER_HAL_REDUCER_INTERFACE_V1.md` — missing dep spec from §5.3; landed as `SPEC_DRAFT` under override `f354bc3`.
- `tools/gemma_autonomous_loop.py` — runnable autonomous-proposal loop for operator MRED. Hardcodes memory guards. Writes to `GOVERNANCE/GEMMA_PROPOSALS/` (RAW), never to canonical ledger. Iterations capped at 50; halt-pause between iterations by default. Staged under HER override per E24.
- **Forbidden arrows** (`GEMMA_HER_AMPLIFIER_V1 §3.2`): Gemma cannot write ledger, touch kernel, modify governance, pose as witness, become reducer, emit verdicts, or autonomously launch tools.

## Current State (2026-05-23)

- **AUTORESEARCH**: E1-E20 sealed under MAYOR ship gate (2026-04-17). E21 and E22 closed as phantom-blocker audits (`2fa41cc`, `a598769`) — both `E20.open_seams` entries invalidated for this tree. E23 (`a61395e`, 19 sub-epochs in one batch) and E24 (`f354bc3`, Gemma staging) are `PROPOSED_SHIP_UNDER_OVERRIDE` — three consecutive HER overrides this session; receipts carry breach notation; future audits may invalidate.
- **SKILL_REGISTRY_V1**: 75 skills audited (51 canonical, 3 legacy, 3 duplicate, 18 external). Last audit pre-2026-05-23; verify before relying on counts.
- **Voice**: Zephyr (Gemini TTS) — LIVE
- **Video**: HyperFrames — DECLARED (npm allowlist pending); `helen-director` skill + Montage Engine + `STORYBOARD_V1` + `ASSET_ENGINE_V1` shipped. Identity Gate stack (above) unblocks governed admission.
- **HELEN character**: `HELEN_CHARACTER_V2` + `HELEN_DESIGN.md` + `HELEN_PRIMER.md` shipped — character-consistency method validated.
- **Telegram**: Two-way bot with voice — LIVE (not daemonized).
- **Schema Authority**: Governance decision SHIPPED (Actions 1-5 partial, 6-9 open). Schema count 66 (was documented as 47 — drift corrected this revision).
- **Doctrine Admission**: `DOCTRINE_ADMISSION_PROTOCOL_V1` gate — DRAFT; §4 fixtures + harness landed.
- **Carrier rehabilitation** (per `TEMPLE_MEDITATION_DEBUG_UPGRADE_V0` §7): HELEN's kernel is sound; HELEN's carrier (writer, env, docs, portability) is rotting. Debug priority is carrier fixes; upgrade priority is carrier sustainability.

## Open Frontiers

- **Closure attestation gap**: ghost-closure detection is the next frontier. Blocked on Schema Authority seam materialization; needs `closure_receipt_v1` + CI ghost detection wired into the gate pipeline.
- **Doctrine Admission gate activation**: fixtures in place, gate not yet enforcing.
- **Cross-session field attribution**: E22 meta-finding; `CROSS_SESSION_FIELD_ATTRIBUTION_V0` not yet bottled. Highest-leverage governance gap.
- **HELEN carrier rehabilitation**: `helen_say.py` SyntaxError, `jsonschema` dep in pytest's uv-python, `init_helen_wedge` import, Makefile Mac path — each is a small fix; together they restore full test suite collection. See `TEMPLE_MEDITATION_DEBUG_UPGRADE_V0` §7 and `E23.synthesis.actionable_findings`.
- **HALT_BOUNDARY_DISCIPLINE_V0 enforcement**: the doctrine is bottled; a CI gate scanning `docs/proposals/*.md` for the required §heading is not. Paper invariant until script exists.
- **Identity Gate Phase 1**: doctrine + algorithm + schemas + tests are bottled; `tools/hash_render_artifact.py` is the next implementation step.
- **Gemma integration**: `GEMMA_HER_AMPLIFIER_V1` at HOLD; `tools/gemma_autonomous_loop.py` staged under override; needs smoke test on MRED + MAYOR review before any iteration count beyond 1.
- **Override review**: E23 and E24 carry `PROPOSED_SHIP_UNDER_OVERRIDE`. HER ruling on whether to ratify or revoke the override path is pending.
