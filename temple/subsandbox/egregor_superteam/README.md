# EGREGOR SUPERTEAM — CLI Subscription Bridge

**Status**: EXPERIMENTAL / NON_SOVEREIGN / TEMPLE LAYER

Brings your three subscription CLIs into HELEN OS as a collective witness layer (egregore) on top of local Gemma4 (aura-gemma4 or your finetune).

## Architecture

```
                    ┌─────────────────────────────┐
                    │   GEMMA4 FINETUNE (HER)     │  local, cheap, fast
                    │   temple/subsandbox/...     │  proposes, imagines
                    └──────────────┬──────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │     EGREGOR SUPERTEAM       │
                    │   (CLAUDE + CODEX + GROK)   │  your subscriptions
                    │   via CLI, no API keys      │  witness / critique / verify
                    └──────────────┬──────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │   HAL GATE (local)          │  forbidden patterns, syntax
                    └──────────────┬──────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │  RECEIPT (sidecar only)     │  authority=false
                    │  runs/*.json                │  never ledger
                    └─────────────────────────────┘
```

## CLI Roles (suggested mapping)

| CLI     | Role in Egregore          | Strength                     |
|---------|---------------------------|------------------------------|
| GROK    | Lateral Witness           | irreverence, edge cases      |
| CLAUDE  | Structural Reasoner       | critique, architecture, care |
| CODEX   | Execution Verifier        | code sanity, implementation  |

Gemma4 is the **proposer** (cheap imagination). The three CLIs are the **collective witness**.

## Current State

- `cli_adapters.py` — headless wrappers (grok works reliably)
- grok: ✅ `grok --single "..." --no-plan`
- claude: ❌ 401 (subscription vs headless print auth)
- codex: ❌ config.toml `service_tier` error

## Next

1. Stabilize codex config
2. Find reliable claude headless pattern (or agent mode)
3. Build `egregor_orchestrator.py` that fans out + aggregates
4. Wire into existing `gemma_director` or `codex_pilot` shape
5. Produce `EGREGOR_WITNESS_V0` receipts

All outputs are TEMPLE/sandbox. Never sovereign.
