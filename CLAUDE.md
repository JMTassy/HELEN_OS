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

- **Canonical GitHub repo:** `https://github.com/JMTassy/helen-conquest.git` (remotes `origin` and `helen-conquest` both point here)
- **Local working tree:** `~/Documents/GitHub/helen_os_v1` — the SOT. All other on-disk HELEN copies are drift (see `~/CLAUDE.md` directory map).

## Architecture Layers

### Layer 1: Constitutional Membrane
- `helen_os/governance/` — schema registry, validators, ledger validator, LEGORACLE gate, skill promotion reducer
- `oracle_town/kernel/` — daemon (Unix socket), gates A/B/C, mayor, ledger
- Sovereign: only this layer emits verdicts (SHIP/NO_SHIP/BLOCK/PASS)

### Layer 2: Append-Only Ledger
- `town/ledger_v1.ndjson` — hash-chained, cum_hash integrity
- `tools/helen_say.py` — canonical writer (payload_hash = sha256(canon(payload))); `--op` values: `fetch` (default), `dialog`, `shell`, `promote_skill`, `seq_correction`
- `tools/ndjson_writer.py` — kernel boundary writer; uses `fcntl.flock` (exclusive) + re-reads on-disk tail under lock to prevent TOCTOU seq forks
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
  - `templates/meditation/` — HELEN TEMPLE HER meditation video pipeline (commit `8bda100`): reads `meditation.config.json`, injects `{{DATE}}` / `{{MEDITATION_TEXT}}` / `{{RUN_HASH}}` / `{{COMMIT_SHA}}` tokens into 4 HTML compositions, calls Zephyr TTS, renders via `npx hyperframes render`, writes `provenance.json` (authority: NONE). Usage: `python3 generate_meditation.py [--preview|--dry-run|--config path|--output path]`
- `oracle_town/skills/video/helen-director/` — Montage Engine + STORYBOARD_V1 + ASSET_ENGINE_V1 + 30s candidate runner; parallel Seedance pipeline
- `oracle_town/skills/video/library/` — curated frame asset pool (refs/canonical/, era axis)
- `helen_os/render/math_to_face.py` + `math_to_face/SKILL.md` — sovereign white-box render pipeline (φ-SDE + H/G/E/H⁻¹ bidirectional compiler math ↔ latent ↔ image), parallel to `helen-director` rental; **SCAFFOLD** status, Phase 0–9 roadmap in `math_to_face/SKILL.md` §6
- `helen_os/render/math_to_face_starter/refs/canonical/` — canonical identity-lock frame reference pool (eras: real, twin, metaverse, none). Scan gaps reported to `artifacts/scan_gap_notes.md` by the KB manifest audit tool. Promotion candidates require explicit GO PROMOTE — authority: false, ledger_mutation: false.
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

### Operator Surface Layer (`apps/helen-surface/`)
Non-sovereign HTML cockpit + status API — the operator-facing UI that frames HELEN's receipted work. None of it is load-bearing on the kernel; it reads live state and renders it.
- `home_v1.html` — receipted-agency HOME: proposal queue first (top), orbital kernel below; "first interaction = decision, not navigation"
- `helen2027.html` — radical-simplicity HOME (warm sand palette, UZIK typography; operator-scored 9.2/10)
- `temple.html` / `temple_akashic_v1.html` — Semantic Cockpit V0.2 (orbital Platonic solids, dwell detection, receipt spine, live connector badges)
- `cockpit_v4.html`, `focus.html`, `starship.html`, `index.html`, `goblin/` — additional surfaces
- `helen_status_api.py` — serves `/api/agents`, `/api/connectors` (Gmail/Calendar/GitHub amber-dot badges), live ring-heat data
- Surface doctrine: HELEN is an embodied protagonist the interface *frames*, never a generic AI hologram. Dwell = constitutional act; spatial distance = permission tier.

### SOURCEBOUND OBJECT OS (`src/helen_sourcebound_object.py`)
Executable primitive: every object is bound to its source bytes with a receipt (`SOURCEBOUND_OBJECT_RECEIPT_V0`). Created via `tools/helen_object.py` (`helen object create`). Contract at `docs/protocols/SOURCEBOUND_OBJECT_OS_V0.md`; tests `tests/test_helen_sourcebound_object.py` + `tests/test_helen_object_cli.py`. Implements the "ADMISSIBLE OBJECT COMPUTING" doctrine.

### Non-sovereign HAL inference (`tools/hal_driver.py`, `tools/run_hal_epoch.py`)
Local HAL-role inference driver and epoch runner. Per-agent model assignment is specified in `docs/spec/MODEL_ROUTING_V1.md` (role-fit routing). Local runtime currently targets Ollama `qwen3.6`. Non-sovereign — produces proposals, not verdicts.

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

### `oracle_town/protocols/`
- `SKILL_ADMISSION_PROTOCOL_V1.md` — 7-gate pipeline for skill-local admission (Temple → Oracle → Mayor → Reducer → Ledger → Replay → Witness)
- `SOVEREIGN_PROMOTION_PROTOCOL_V1.md` — lawful path from skill-local admission to operator-authorized admitted ledger write; `skill_local_admission ≠ operator_authorized_admission`
- `SOVEREIGN_LEDGER_SEQ_REPAIR_PROTOCOL_V1.md` — seq fork repair via `LEDGER_SEQ_CORRECTION_V1` packet; operator-authorized only
- `MAYOR_HANDLER_PROMOTE_SKILL_SPEC_V1.md` — 6-gate `_handle_promote_skill()` spec

### `oracle_town/audits/`
- `SOVEREIGN_PROMOTION_AUDIT_REFERENCE_DRIFT_WITNESS_V1.md` — post-mortem for seq=287 TOCTOU fork
- `FIREWALL_BYPASS_AUDIT_8911FD0.md` — authorized firewall bypass record for seq_correction handler

> **Note on `SOVEREIGN_*` filenames**: Legacy filenames refer to operator-authorized admitted ledger capability, not autonomous sovereignty. HELEN does not self-authorize. Operators authorize; reducers admit; ledger records.

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

**Demo targets** (NON_SOVEREIGN, authority=NONE, no ledger writes):

```bash
make demo-helen        # boot + coupling + autoresearch + airlock (all four)
make demo-boot         # boot ritual only
make demo-coupling     # reality coupling only
make demo-autoresearch # bounded autoresearch only
make demo-airlock      # init airlock only
```

## CI Pipeline

CI runs on every push/PR to `main` via `.github/workflows/`. Three jobs in sequence:

1. **doc-index** — verifies `scratchpad/CLAUDE_MD_LINE_INDEX.txt` and `scratchpad/CLAUDE_MD_SECTIONS_BY_LENGTH.txt` are up-to-date. **After any CLAUDE.md edit, regenerate before committing:**
   ```bash
   python3 scratchpad/generate_claude_index.py
   git add scratchpad/CLAUDE_MD_LINE_INDEX.txt scratchpad/CLAUDE_MD_SECTIONS_BY_LENGTH.txt
   ```
   Skipping this step will fail CI with "CLAUDE.md indices are stale!"

2. **verify** — runs `python3 ci_run_checks.py`, which calls `oracle_town/VERIFY_ALL.sh` then a 200-iteration replay determinism check via `oracle_town.core.replay`.

3. **rho-receipt** — K-rho viability receipt lint (requires `jsonschema`; installed via `requirements-ci.txt`).

## AGENTS.md — Subagent Role

`AGENTS.md` at repo root defines the Claude subagent identity: **CLAUDE_HAL_CODEX** (non-sovereign coder). Key rules repeated here for visibility:
- Make small, reviewable patches; report exact files changed and tests run.
- Never mutate sovereign ledgers, never promote canon, never edit memory identity objects without explicit instruction.
- Prefer NO_SHIP over unsafe success.
- Current coding lane: HELEN Director / render pipeline (receipt sidecars, operator rating enforcement, heuristic filtering, seed selection).
- Forbidden without explicit approval: scaling render generation, memory mutation, canon promotion, ledger writes, broad refactors.

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

# One-shot operator-routed admitted message (canonical writer)
# --op options: fetch (default), dialog, shell, promote_skill, seq_correction
.venv/bin/python tools/helen_say.py "your message" --op fetch

# Admitted skill promotion (requires SKILL_PROMOTION_PACKET_V1 JSON as message; operator-authorized)
.venv/bin/python tools/helen_say.py '{"skill_id":"...","requested_action":"SOVEREIGN_PROMOTE",...}' --op promote_skill

# Ledger seq repair (operator-authorized only; see oracle_town/protocols/SOVEREIGN_LEDGER_SEQ_REPAIR_PROTOCOL_V1.md)
.venv/bin/python tools/helen_say.py '{"operation":"LEDGER_SEQ_CORRECTION_V1",...}' --op seq_correction

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

## LNSA — Session Discipline Protocol

`LNSA.py` + `LNSA_SKILL.md` are a self-contained working-memory tool, distinct from the sovereign ledger. Runs in-process and produces a session JSON, not `town/ledger_v1.ndjson`.

- **Activation:** `python3 LNSA.py`, or `/lnsa` / `hi helen` inside a Claude session.
- **Five phases:** Exploration → Tension → Drafting → Editorial → Termination.
- **Termination contract:** every session ends `SHIP` (artifact + location + impact named) or `ABORT` (failure mode named). Open-ended pauses are forbidden by design — the "Termination is sacred" invariant in operator form.
- **What it records:** claims (R/C/T/W/M tagged), contradictions (both versions kept), challenges, revisions, final decision.
- **Naming collision:** `LNSA_ERROR` strings in `tools/helen_say.py` refer to the sovereign ledger seal, not to `LNSA.py`. Don't conflate them.

## Operational Notes

- `town/ledger_v1.ndjson` may show as dirty in `git status` due to live kernel daemon writes. Do not stash, do not commit, do not edit — operator-authorized firewall path.
- `artifacts/k8_*.json`, `artifacts/k8_trace.ndjson`, `artifacts/k_tau_*.json` are live gate-trace outputs and routinely show dirty after lint runs. They are not stash-eligible; let the gate scripts manage them.
- `artifacts/audio/` and `artifacts/media/` are TTS and rendered video outputs (used by the meditation generator and director pipelines). Not stash-eligible; not committed without explicit operator decision.
- `artifacts/scan_gap_notes.md` is the KB manifest audit output (era-gap and naming-issue report against `math_to_face_starter/refs/canonical/`). DRAFT — never auto-promoted.
- **K-tau `datetime.utcnow()` is a mu_DETERMINISM violation.** Use `datetime.now(timezone.utc)` throughout. This is the most common recurring lint failure — check all new files before committing.

## Key Reference

`docs/HELEN_OS_CTO_GUIDE_V1_1.md` — authoritative architectural state at 2026-06-13 (post seq-repair). Read this first when orienting in the kernel layer. Contains: component live/status table, chain status, admission pipeline, firewall bypass record.

## Current State

**Do not trust dated state — run `git log` and `make test`.** Architecture details live in the sections above; the strata below keep only facts stated nowhere else. Constitutional invariants, gates, and the firewall are unchanged across all strata.

- **2026-07-03** (`12ec35a`): `transport/` math program (Vols I–II, `tests/test_transport*.py`, `docs/proposals/TRANSPORT_THEOREM_V0.md`) · AUTORESEARCH safe architecture V1 (`temple/autoresearch/` — `autoresearch_policy.py` packet validator, `outbox/` AR-*.json packets, always `authority=false`, reducer_required; spec `docs/proposals/HELEN_AUTORESEARCH_SAFE_ARCHITECTURE_V1.md`) · authority-language linter (`tools/validators/authority_language_linter.py`) · `do_next_v1` structural policy engine (`helen_os/api/do_next_v1.py`; executor receipts reach the ledger only via `helen_say`) · `temple/gardens/` layer — core law **DREAMT ≠ CLAIMED**; every garden ships a fail-closed validator — run it before editing garden content.
- **2026-06-15** (`4d1e185`): skill-promotion admission LIVE — 6-gate `_handle_promote_skill()` + `_handle_seq_correction()` in the kernel daemon; NDJSONWriter `fcntl.flock` + on-disk tail re-read closes the TOCTOU race (seq=287 fork ANCHORED at seq=295, chain PASS); `hal_verdict_from_kernel()` now passes `mutations` through; EXPLORE mechanic E026 unlocked. Protocols in `oracle_town/protocols/`; coverage via `make test` (`test_ndjson_writer_atomic.py`, `test_handle_promote_skill.py`, …).
- **2026-06-03**: operator surfaces (`apps/helen-surface/`) · SOURCEBOUND OBJECT OS · local HAL inference (`tools/hal_driver.py`, `docs/spec/MODEL_ROUTING_V1.md`) · `helen_awakening` / portrait video lanes + STORYBOARD_V1 · GOBLIN_TEMPLE inner memory rooms + Akashic interface · Telegram `/her` HER-presence command (Groq fallback).
- **2026-05-06 uniques**: SKILL_REGISTRY_V1 audit (75 skills: 51 canonical / 3 legacy / 3 duplicate / 18 external) · knowledge corpus T4/T6 floors + `symbolic_sources/` DRAFTs · HELEN_CHARACTER_V2 consistency method (`HELEN_DESIGN.md`, `HELEN_PRIMER.md`) · video/library era axis (11 hero stills, 7 locked eras) · HD-001 GREEN, HD-002/HD-003 next (DAN/RALPH) · HELEN OS v2 UX four-file suite (FOCUS | WITNESS, locked phrases incl. "HELEN suggests. You decide. Everything is recorded.") — PROPOSAL, never promoted. AUTORESEARCH E11/E12 reconciliation status: see Open Frontiers.

## HELEN OS Look & Feel — Source Atlas Doctrine

HELEN OS uses a Source Atlas visual system. The interface is not a flat dashboard. It is a layered source field:
- center = source object
- margins = commentary and objections
- orbit = references and memory paths
- bottom rail = actions
- top banner = governance state

The aesthetic combines:
- Talmudic page architecture
- Dante-style vertical cosmology
- cybernetic HUD overlays
- semantic voxel memory maps
- dark source cockpit atmosphere
- parchment / manuscript commentary layers

The third-eye motif means structural vision only: it sees relation, dependency, and proof paths. It must never imply prophecy, divine authority, or sovereign truth. All mystical, alchemical, or sacred visual elements remain expressive overlays. They do not determine governance status. Governance color remains primary. Proof is mandatory for admitted (🟢), sealed (🟡), and replayable (⚪) objects. No decorative color substitution is allowed.

Palette (strict, one meaning per color): ⚫ unknown · 🔵 observed · 🟣 claim · 🟠 review · 🟢 admitted · 🟡 sealed · ⚪ replayable · 🔴 breach. Background: black/parchment/graphite. Glyph voices: SERIF=source, MONO=receipt/proof, HUMANIST=commentary. Interaction vocabulary: 👁️OBSERVE · 📜CLAIM · 🧪REVIEW · ⚖️ADMIT · 🔒SEAL · 🔁REPLAY · ✂️CUT.

Six locked visual motifs: (1) Voxel Memory Mass — corpus as 3D terrain; (2) Commentary Rings — Talmudic orbit; (3) Wireframe Proof Chamber — deterministic test space; (4) Floating Semantic Cubes — typed 𝕎⁺ objects; (5) CRT/Terminal Overlay — machine witness; (6) Cathedral/Tower Verticality — build upward only through receipts.

Full spec: `docs/proposals/HELEN_SOURCE_ATLAS_V1.md` (PROPOSAL · NON_SOVEREIGN · NO_CLAIM).

## WULMOJI Status Rendering Rule

Agents must not render `🟢 ADMITTED`, `🟡 SEALED`, or `⚪ REPLAYABLE` for any artifact whose frontmatter contains `authority: false`, `claim_status: NO_CLAIM`, `final: HOLD_FOR_OPERATOR`, `git_stage: no`, or `git_commit: no`.

For proposal documents under `docs/proposals/`, the maximum allowed banner is:
- `🔵 OBSERVED` — merely written or inspected
- `🟣 CLAIM` — proposed as doctrine
- `🟠 REVIEW` — under operator evaluation

Promotion to `🟢 ADMITTED` requires an explicit operator admission receipt. Promotion to `🟡 SEALED` requires hash/version lock. Promotion to `⚪ REPLAYABLE` requires replay validation. **Never use green as "successfully written." Green means admitted.**

## Open Frontiers

- **Closure attestation gap**: ghost-closure detection is the next frontier. Blocked on Schema Authority seam materialization; needs `closure_receipt_v1` + CI ghost detection wired into the gate pipeline.
- **AUTORESEARCH E11/E12 reconciliation**: hypothesis + experiment landed (see Current State). Awaiting peer-review → countersign → MAYOR ruling. E13 stays blocked until then.
- **Doctrine Admission gate activation**: fixtures in place, gate not yet enforcing.
