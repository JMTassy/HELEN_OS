# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

HELEN OS is a five-layer constitutional AI companion with an append-only governance kernel. The system is built on a single invariant: **NO RECEIPT = NO CLAIM**.

## Two Trees — Disambiguation

Two top-level Python trees with confusingly similar names:

- `helen_os/` — sovereign tree. Governance, executor, autonomy, schemas, tests. This is what `make test` runs and what the gates police.
- `helen_os_scaffold/` — separate scaffold tree. Hosts the Click CLI (`helen_os_scaffold/helen_os/cli.py`) that exposes `helen talk` / `helen chat`, the LLM adapters, and the `helen.speak()` agent stack. **Has its own venv expectation** — chat workflows run via `cd helen_os_scaffold && source .venv/bin/activate`.

Treat them as independent packages. Imports do not cross.

## Source Scope

Live HELEN OS work is scoped to `experiments/helen_mvp_kernel/`. Code edits go **only** there.

**Off-limits to edits** (read freely, write never):

- `helen_os/governance/**`, `helen_os/schemas/**`, `oracle_town/kernel/**` — sovereign firewall (see `~/.claude/CLAUDE.md`)
- `town/ledger_v1.ndjson`, `mayor_*.json`, `GOVERNANCE/CLOSURES/**`, `GOVERNANCE/TRANCHE_RECEIPTS/**` — sovereign artifacts
- Root `helen_os/` modules outside `experiments/`, existing tests, sealed proposals, constitutional files (`KERNEL_V2.md`, `SOUL.md`, `HELEN.md`, `KERNEL_K_TAU_RULE.md`)

If a task appears to require an off-limits write, stop and report — route through MAYOR via the admissible bridge (`tools/helen_say.py`), not by direct edit.

### experiments/helen_mvp_kernel/ (active work surface)

Non-sovereign sandbox. Status: NON_SOVEREIGN / NO_SHIP. Structure:

- `helen_os/gates/` — AV validation gates (active frontier):
  - `face_motion_gate.py` — identity-lock enforcement (face consistency)
  - `composite_admissibility.py` — combined gate verdict
  - `av_sync_gate.py` — audio/video sync validation
  - `spectral_gate.py` — spectral consistency checks
- `helen_os/ledger/` — hash-chain, receipts, event log, schemas
- `helen_os/runtime/` — session, state observer, ralph observer, SSE server
- `helen_os/kernel/` — core kernel logic (non-sovereign sandbox)
- `helen_os/tests/` — 8 constitutional test files (hash-chain break, replay determinism, no-receipt-no-mutation, firewall, policy, etc.)
- `.venv-gates/` — isolated venv for gate tests

## Repository Identity

- **Canonical GitHub repo:** `https://github.com/JMTassy/HELEN_OS.git`
- **Local working tree:** `~/Documents/GitHub/helen_os_v1`

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
- `helen_os/knowledge/` — corpus + embeddings + classified patterns + `symbolic_sources/`; T4/T6 floors enforce source-provenance and intensity for symbolic ingestion

### Layer 4: Skills + Tools
- `oracle_town/skills/` — map generator, meteo, claim workflow, conquest integration, ledger reader
- `oracle_town/skills/feynman/` — peer_review, intent_action_audit, session_notes (fused 2026-04-16)
- `oracle_town/skills/voice/gemini_tts/` — Zephyr voice, Gemini 2.5 Flash TTS (LIVE)
- `oracle_town/skills/video/hyperframes/` — HyperFrames video renderer (DECLARED)
- `oracle_town/skills/video/helen-director/` — Montage Engine + STORYBOARD_V1 + ASSET_ENGINE_V1 + 30s candidate runner; parallel Seedance pipeline
- `oracle_town/skills/video/library/` — curated frame asset pool (refs/canonical/, era axis)
- `helen_os/render/math_to_face.py` + `math_to_face/SKILL.md` — sovereign white-box render pipeline (φ-SDE + H/G/E/H⁻¹ bidirectional compiler math ↔ latent ↔ image), parallel to `helen-director` rental; **SCAFFOLD** status, Phase 0–9 roadmap in `math_to_face/SKILL.md` §6
- `tools/helen_telegram.py` — two-way Telegram bot with voice
- `tools/helen_simple_ui.py` — web UI at localhost:5001 with voice

### Layer 5: TEMPLE Exploration
- Non-sovereign generative layer
- `helen_dialog/` — dialog engine, HER/AL moment detection
- `temple/subsandbox/` — AURA grimoire + raw symbolic terminal samples; never sovereign, never auto-promoted

### Layer 6: HELEN_DAN_RALPH_V0 (Bounded Execution Loop)
- `scripts/ralph/ralph.sh` — epoch runner: Temple→Mayor→Ralph→DAN→HAL→Reducer→Ledger; one epoch = one story
  - **heredoc-in-subshell rule**: never `$(cmd <<PYEOF)`; write Python to `/tmp/` file, invoke via `$VENV /tmp/file.py arg`
- `oracle_town/skills/ops/dan_goblin/` — DAN_GOBLIN runtime
  - `prd.json` — story backlog (HD-001 done, HD-002/HD-003 todo)
  - `receipts/` — GREEN/FAILED per-story receipts; `reducer_decision` field is null — DAN never writes it
  - `scratch/` — ephemeral; gitignored
- `schemas/helen_dan/prd.schema.json` + `receipt.schema.json` — DAN schemas (in root `schemas/`, not yet migrated to `helen_os/schemas/`)
- `docs/proposals/HELEN_DAN_RALPH_V0.md` — core doctrine; `docs/proposals/DAN_GOBLIN.md` — operating card
- **GOBLIN MODE** (`docs/proposals/HELEN_DAN_GOBLIN_RECALL_MODE_V0_1.md`): creative recovery dialect; UNDERWARREN_SAFE; NON_SOVEREIGN; "feral but kind, strange but useful"; THE HEAP MAY SPEAK, THE LEDGER MUST VERIFY

### WUL Packet Validator (P1 compile-time)
- `src/wul_packet_validator.py` — validates WUL inter-agent packets before any action layer; **fails closed**
  - 3 tiers: ACK (`ROLE·WUL`), PRODUCTION (8 fields), KERNEL_ADJACENT (10 fields)
  - `PERM::WRITE_SOVEREIGN` unconditionally rejected at any tier
  - KERNEL_ADJACENT: CONF ≥ 0.85 or `HIGH`, ⌬ (`\u23ac`) mandatory in WUL, `ESCALATE::OPERATOR` required
  - Unknown ROLE/INTENT/IMPACT/DIALECT → warning only (forward-compatible), not error
- `tests/test_wul_packet_validator.py` — 29 tests, all green; run: `.venv/bin/pytest tests/test_wul_packet_validator.py -v`
- `docs/specs/WUL_PACKET_SPEC_V0_1.md` — formal spec
- `docs/proposals/TEMPLE_TRANSMUTATION_REQUEST_WUL_P1_VALIDATOR_V1.json` — bridge artifact from TEMPLE_200_WUL; `authority: NONE`, `bridge_status: PENDING_MAYOR_REVIEW`

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

- **Canonical**: `helen_os/governance/schema_registry.py` → `helen_os/schemas/` (47 files, 100% governance-indexed)
- **Legacy (deprecated, 0 consumers)**: `helen_os/schema_registry.py`, `helen_os/validators.py`
- **Governance audit tools**: `helen_os/governance/schema_index_audit.py` (dual-recognizer), `helen_os/governance/root_schemas_consumer_audit.py` (runtime/doc/orphan classifier)
- Root `schemas/` still has 19 files pending migration (classified; delete deferred)

## Key Invariants

- `NO RECEIPT = NO CLAIM` — every action produces a hash-chained ledger entry
- `NO HASH = NO VOICE` — K8 corollary: ND output never enters spine unhashed
- `additionalProperties: false` on all constitutional schemas — forbidden fields rejected at schema level
- Proposer ≠ Validator — peer_review enforces K2/Rule 3
- Termination is sacred — SHIP or ABORT only, no open-ended pauses

## Test Suite

There are **two test trees** with different scopes:

- `helen_os/tests/` — autoresearch, ledger validator, LEGORACLE replay gate, bounded executor, etc. This is what `make test` runs.
- `tests/` (repo root) — numbered constitutional invariants (`test_1_mayor_only_writes_decisions.py` … `test_9_mayor_io_allowlist.py`) plus `governance_regression/`. **Not covered by `make test`** — invoke explicitly, e.g. `.venv/bin/pytest tests/ -q`.

Commands:

- `make test` — authoritative for `helen_os/tests/` only. Do not rely on stale test counts pinned here — run the suite.
- `make membrane-test` — ledger validator + autoresearch bounded/deterministic + no-local-replay-shadowing
- `make anti-regression` — replay divergence check (single-test-file, verbose)
- Single test: `.venv/bin/pytest helen_os/tests/test_foo.py::test_bar -v`
- Root constitutional invariants (not covered by `make test`): `.venv/bin/pytest tests/ -q`
- Ghost closure detector: `.venv/bin/pytest helen_os/tests/test_no_ghost_closures.py -v`
- MVP kernel sandbox (non-sovereign): `.venv/bin/pytest experiments/helen_mvp_kernel/helen_os/tests/ -v`
- K8 target: PASS (k8=+1.000)
- LEGORACLE replay gate: fixture integrity + determinism + frozen output + mutation detection

**PYTHONPATH**: `Makefile` sets `PYTHONPATH := $(CURDIR)` (commit `5b98a3d`, repo-relative). No operator-specific path — `make test` is portable.

## Setup

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

`experiments/helen_mvp_kernel/.venv-gates/` is a separate venv used by MVP kernel gate tests — bootstrap it independently if needed:
```bash
python3 -m venv experiments/helen_mvp_kernel/.venv-gates
experiments/helen_mvp_kernel/.venv-gates/bin/pip install pytest pytest-asyncio
```

## Running HELEN

Prefer `.venv/bin/python` for runtime commands so imports resolve consistently with `make test`.

```bash
# ⚠ Chat surfaces: use --ledger :memory: for ephemeral dev to avoid
#   LNSA_ERROR on sealed sovereign ledger files (see Chat Surfaces section).

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

# K-tau lint (boundary, IO, determinism, allowlist, schema)
.venv/bin/python scripts/helen_k_tau_lint.py

# K-rho lint (numeric consistency of rho traces)
.venv/bin/python scripts/helen_rho_lint.py

# K-wul lint (canonical WUL compile+validate)
.venv/bin/python scripts/helen_wul_lint.py /path/to/slab.json

# Full test suite
make test

# Ledger writer guard (run before any suspected direct-ledger write)
bash tools/kernel_guard.sh
```

### Packaging note
`pyproject.toml` declares the project as `oracle-town` v1.0.0 with `dependencies = []` — it is not the dependency source of truth. Use `requirements.txt` / `requirements-ci.txt` when installing.

## Chat Surfaces

Multiple chat entry points exist; they are **not interchangeable**.

| Surface | Code | LLM call | Receipts | Notes |
|---|---|---|---|---|
| `helen talk` | `helen_os_scaffold/helen_os/cli.py:120` | only with `--reply` | always (kernel-routed) | Add `--hal` for two-block HER/HAL, BLOCK paths emit `BLOCK_RECEIPT_V1` |
| `helen chat` | `helen_os_scaffold/helen_os/cli.py:262` | yes (full pipeline) | via `helen.speak()` | District/street context, agent stack |
| `helen_os_scaffold/helen_talk.py` | scaffold root | **never** | yes | **Receipt-only by design** — does NOT call the LLM. Common confusion. |
| `tools/helen_telegram.py` | tools | yes | yes | Two-way Telegram with voice |
| `tools/helen_simple_ui.py` | tools | yes | yes | Web UI on `localhost:5001` |
| `helen_dialog_server.py` + `helen_dialog/` | repo root | yes | engine-managed | TEMPLE dialog engine, HER/AL moment detection |

**`--ledger :memory:` gotcha** — when the configured ledger is a sealed sovereign file (e.g. `storage/ledger_epoch*_work.ndjson`), `helen talk --reply` writes the receipt **before** the LLM call and crashes with `LNSA_ERROR: Sovereign ledger is SEALED. No further mutations allowed.` Pass `--ledger :memory:` for ephemeral chat or `--ledger storage/chat_dev.ndjson` for persistent dev. See `HELEN_CHAT_MODES.md`.

## Operational Notes

- `town/ledger_v1.ndjson` may show as dirty in `git status` due to live kernel daemon writes. Do not stash, do not commit, do not edit — sovereign firewall path.
- `artifacts/k8_*.json`, `artifacts/k8_trace.ndjson`, `artifacts/k_tau_*.json` are live gate-trace outputs and routinely show dirty after lint runs. They are not stash-eligible; let the gate scripts manage them.

## Current State (2026-05-06)

- **AUTORESEARCH**: E11 LEGORACLE + E12 replay gate shipped. Two parallel sessions diverged; **reconciliation in flight, not yet ruled**. Reconciliation hypothesis at `docs/proposals/AUTORESEARCH_E11_E12_RECONCILIATION.md` (commit `0d06b33`); §3 read-only SHA-diff experiment executed and reports landed at `docs/reports/AUTORESEARCH_E11_E12_*` (commit `d43ec64`). Headline finding: **H₁ partially falsified** — three artifact-level STRUCTURAL_CHANGE rows (test + fixtures), but the falsifier-specific check is **negative** (LEGORACLE gate logic and replay determinism logic unaffected; `legoracle_v13rc.py` SHA matches). Recommendation candidates for MAYOR: REQUEST_MORE_EVIDENCE (SHA_DIFF report) or REVOKE_AND_RERUN (RECONCILIATION_REPORT_V0). **Awaiting fresh-context peer-review (Rule 3) → operator countersignature → MAYOR ruling**. E13 remains blocked. Kernel daemon currently down.
- **Knowledge corpus**: T4 (source-provenance floor) + T6 (intensity floor) landed for symbolic-knowledge ingestion. Symbolic sources collected in `helen_os/knowledge/symbolic_sources/` (DRAFT classifications).
- **SKILL_REGISTRY_V1**: 75 skills audited (51 canonical, 3 legacy, 3 duplicate, 18 external)
- **Voice**: Zephyr (Gemini TTS) — LIVE
- **Video**: HyperFrames — DECLARED (npm allowlist pending); `helen-director` skill + Montage Engine + `STORYBOARD_V1` + `ASSET_ENGINE_V1` + 30s candidate runner shipped. `video/library/` promotes 11 hero stills to `refs/canonical/` with locked era axis (cyberpunk / medieval / renaissance / modern / ww2 / french_revolution / pyramids).
- **HELEN character**: `HELEN_CHARACTER_V2` + `HELEN_DESIGN.md` + `HELEN_PRIMER.md` shipped — character-consistency method validated
- **TEMPLE/AURA**: First raw terminal sample captured (`temple/subsandbox/aura/`); grimoire path now exists. Non-sovereign, never auto-promoted.
- **HELEN_DAN_RALPH_V0**: Epoch runner live (`scripts/ralph/ralph.sh`). HD-001 GREEN (commit `d8adb50`). HD-002 (complexity_extractor → aura_score.py) and HD-003 (failure-memory consultation) are next.
- **WUL Packet Validator**: P1 shipped. `src/wul_packet_validator.py` + `tests/test_wul_packet_validator.py` (29/29 green). Spec at `docs/specs/WUL_PACKET_SPEC_V0_1.md`. Transmutation request pending MAYOR review.
- **GOBLIN MODE**: Proposal shipped to `docs/proposals/HELEN_DAN_GOBLIN_RECALL_MODE_V0_1.md`. NON_SOVEREIGN, NO_SHIP, UNDERWARREN_SAFE.
- **Telegram**: Two-way bot with voice — LIVE (not daemonized)
- **Schema Authority**: Governance decision SHIPPED (Actions 1-5 partial, 6-9 open)
- **Doctrine Admission**: `DOCTRINE_ADMISSION_PROTOCOL_V1` gate — DRAFT; §4 fixtures + harness landed
- **Experiments**: minimal MVP terminal kernel landed in `experiments/` (NON_SOVEREIGN, NO_SHIP — sandbox only)
- **HELEN OS v2 UX**: PROPOSAL-class four-file suite shipped to `docs/proposals/` (commit `442f5ee`). Two-mode top-level toggle (`FOCUS | WITNESS`) + Four-Mode Product Map (FOCUS / WITNESS / ORACLE / TEMPLE). Locked phrases: product tagline `"HELEN suggests. You decide. Everything is recorded."`, constitution phrase `"HELEN sees. HELEN proposes. The gate authorizes…"`, UX canon `"HELEN n'est pas un cockpit…"`. LEGORACLE idle = `Gate Clear · No Active Claim`; SHIP_FORBIDDEN never permanent ambient. CONTEXT STACK is technical default (8 layers); AURA confined to Oracle/Temple as non-authoritative metaphor. Brand rule: Apple-like calm, never macOS chrome clone. Files: `HELEN_OS_V2_USER_CENTRIC_UX.md`, `FOCUS_MODE_TERMINAL_SPEC.md`, `TEMPLE_MODE_VISUAL_BRIEF.md`, `HELEN_OS_V2_VISUAL_CANON_LOCK.md`. Status: PROPOSAL / NON_SOVEREIGN / NO_SHIP — not promoted to canon.

## Open Frontiers

- **Closure attestation gap**: ghost-closure detection is the next frontier. Blocked on Schema Authority seam materialization; needs `closure_receipt_v1` + CI ghost detection wired into the gate pipeline.
- **AUTORESEARCH E11/E12 reconciliation**: hypothesis + experiment landed (see Current State). Awaiting peer-review → countersign → MAYOR ruling. E13 stays blocked until then.
- **Doctrine Admission gate activation**: fixtures in place, gate not yet enforcing.
