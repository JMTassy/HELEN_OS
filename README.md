# HELEN OS

**Local-first AI companion with constitutional governance.**

HELEN is a five-layer AI system where every action is a claim, every claim is challengeable, and every decision is receipted on an immutable ledger. Built for determinism, auditability, and zero authority leakage.

## Quick Start

```bash
# 1. Start the governance kernel
python3 oracle_town/kernel/kernel_daemon.py &

# 2. Talk to HELEN
python3 tools/helen_say.py "hello HELEN" --op fetch

# 3. Interactive CLI
python3 tools/helen_cli.py

# 4. Web UI with voice (requires Gemini API key)
GEMINI_API_KEY=... python3 tools/helen_simple_ui.py
# → http://localhost:5001

# 5. Telegram bot with voice
GEMINI_API_KEY=... python3 tools/helen_telegram.py

# 6. Run tests
python3 -m pytest helen_os/ -q
```

## Architecture

```
Layer 1  Constitutional Membrane     helen_os/governance/     Sovereign: emits verdicts
Layer 2  Append-Only Ledger          town/ledger_v1.ndjson    Hash-chained, immutable
Layer 3  Execution + Autonomy        helen_os/executor/       Non-sovereign: runs, doesn't judge
Layer 4  Skills + Tools              oracle_town/skills/      Voice, video, research, games
Layer 5  TEMPLE Exploration          helen_dialog/            Non-sovereign generative layer
```

## Core Invariants

- **NO RECEIPT = NO CLAIM** — every action produces a hash-chained ledger entry
- **NO HASH = NO VOICE** — non-deterministic output never enters the spine unhashed
- **Proposer ≠ Validator** — the entity that writes cannot approve its own work
- **Termination is sacred** — every process ends SHIP or ABORT, never open-ended
- **additionalProperties: false** — constitutional schemas reject unknown fields at the boundary

## What's Inside

| Component | Status | Description |
|---|---|---|
| Governance kernel | LIVE | Schema registry, LEGORACLE gate, K8 gate, ledger validator |
| Voice (Zephyr) | LIVE | Gemini 2.5 TTS — HELEN speaks her verdicts |
| Telegram bot | LIVE | Two-way dialogue with voice notes |
| Web UI | LIVE | localhost:5001 with async voice |
| HyperFrames video | DECLARED | HTML/CSS/GSAP compositions rendered to MP4 |
| Peer review | LIVE | Structural code review with reviewer ≠ proposer enforcement |
| Intent-action audit | LIVE | Compares stated intentions against actual implementation |
| LEGORACLE gate | LIVE | Obligation-checking validator with replay harness |
| K8 gate (v1.2) | LIVE | Non-determinism boundary — AST-scoped, peer-reviewed twice |
| Skill registry | SHIPPED | 75 skills audited and classified |

## Gates

HELEN enforces correctness through automated gates:

```bash
# K8: Non-determinism boundary
python3 scripts/helen_k8_lint.py

# K-tau: Coherence (boundary, IO, determinism, allowlist, schema)
python3 scripts/helen_k_tau_lint.py

# K-rho: Numeric consistency
python3 scripts/helen_rho_lint.py

# Kernel guard: Only allowed writers may touch the ledger
bash tools/kernel_guard.sh
```

## Project Structure

```
helen_os/
  governance/          Schema registry, validators, LEGORACLE gate, promotion reducer
  executor/            Bounded task execution (non-sovereign)
  autonomy/            Autoresearch, skill discovery
  schemas/             47 constitutional schemas (100% governance-indexed)
  tests/               426 tests, 0 failures

oracle_town/
  kernel/              Daemon, gates A/B/C, mayor, ledger
  skills/              Map gen, meteo, claim workflow, conquest integration
    feynman/           Peer review, intent-action audit, session notes
    voice/gemini_tts/  Zephyr TTS (Gemini 2.5 Flash)
    video/hyperframes/ HyperFrames video renderer

tools/                 helen_say, helen_cli, telegram bot, web UI, kernel guard
scripts/               K8, K-tau, K-rho lints, metrics analyzer
town/                  ledger_v1.ndjson (hash-chained append-only)
```

## Governance

HELEN's development process follows the same governance model as the system:

- **PULL-mode autoresearch**: one hypothesis per epoch, observable signals only, non-sovereign layers only
- **Tranche discipline**: HAL gate + receipted summary + MAYOR re-rank between tranches
- **Ghost closure detection**: every "DONE" claim is verified against artifact SHA-256
- **Schema authority**: single canonical registry at `helen_os/governance/schema_registry.py`

## Documentation

| Document | Purpose |
|---|---|
| [CLAUDE.md](CLAUDE.md) | Operational reference — architecture, gates, running instructions, current state |
| [HELEN.md](HELEN.md) | Philosophical manifesto — consciousness loop, three properties, free will |
| [SKILL_REGISTRY_V1.json](SKILL_REGISTRY_V1.json) | 75 skills audited: canonical, legacy, sovereign risk, test coverage |
| [AUTORESEARCH_CONTRACT_V1.json](AUTORESEARCH_CONTRACT_V1.json) | Sealed contract — hypothesis validated across 20 epochs |

## Current State

- **Tests**: 426 pass, 0 fail, 0 warnings
- **K8**: PASS (k8=+1.000)
- **Governance index**: 47/47 (100%)
- **AUTORESEARCH**: Contract sealed — governance enforcement validated empirically

## HELEN_OS_ROSE

[HELEN_OS_ROSE/](HELEN_OS_ROSE/README.md) — model-agnostic operating system for ROSE and CIELO IMPACT (strategy, decisions, execution packets, evidence register, claim linter). Rose is the sovereign operator; its ledger is separate from the town ledger. Status: IMPLEMENTED_NOT_APPROVED (see `HELEN_OS_ROSE/receipts/bootstrap_receipt.json`).

```bash
# validate the ROSE workspace
python3 HELEN_OS_ROSE/scripts/validate_workspace.py

# run its tests
python3 -m unittest discover -s HELEN_OS_ROSE/tests
```

## License

MIT
