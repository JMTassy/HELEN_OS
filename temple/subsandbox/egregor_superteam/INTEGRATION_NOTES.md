# EGREGOR SUPERTEAM — Integration Notes

## Current Status (2026-07-20)

| CLI     | Headless Pattern                    | Status     | Notes |
|---------|-------------------------------------|------------|-------|
| grok    | `grok --single "..." --no-plan`     | ✅ LIVE    | Reliable JSON output |
| claude  | `claude -p "..." --dangerously-skip-permissions` | ❌ BLOCKED | 401 or hangs in non-interactive |
| codex   | `codex exec "..."`                  | ⚠️ DEGRADED | service_tier fixed, but often no clean JSON stdout |

## How to use right now

```bash
cd ~/Documents/GitHub/helen_os_v1

# Direct (grok will dominate until claude/codex are fixed)
python3 temple/subsandbox/egregor_superteam/orchestrator.py \
  "Your intent here. The egregor will witness."

# Or from Gemma director later:
# 1. Gemma proposes (cheap local)
# 2. Call run_egregor(intent) as witness layer
# 3. HAL gate inside orchestrator
# 4. Write EGREGOR_WITNESS_V0 sidecar
```

## Fixing the other two CLIs (operator action)

### Codex
Already edited `~/.codex/config.toml` → `service_tier = "fast"`

If still noisy, try:
```bash
codex exec -c 'service_tier="fast"' 'Return ONLY: {"role":"codex","ok":true}'
```

### Claude
Claude Code CLI is primarily interactive/TUI. Headless `-p` often requires:
- Being logged in via the TUI first (`claude` then exit)
- Or the `ANTHROPIC_API_KEY` env (but you said "not API yet")
- Or `--bare` + specific agent

Test manually:
```bash
claude -p 'Return ONLY JSON: {"test":true}' --bare --dangerously-skip-permissions
```

If it keeps 401/timeout, we may need to run claude via a different invocation (e.g. inside an existing session or different flag set). This is outside the current scope.

## Architecture fit inside HELEN OS

```
temple/subsandbox/
├── gemma_director/          # HER (local Gemma4 finetune) — proposer
├── codex_pilot/             # HER→HAL→CODEX (local only)
└── egregor_superteam/       # NEW: Grok+Claude+Codex via subscription CLIs — witness
    ├── cli_adapters.py
    ├── orchestrator.py      # produces EGREGOR_WITNESS_V0
    └── runs/EGREGOR__*.json # sidecars only
```

Gemma = cheap imagination (proposer)
Egregor = your three paid subscriptions (collective witness / critique)

This matches the "Gemma4 finetune + egregor superteam" request.

## Next concrete steps (small patches only)

1. Make orchestrator more tolerant of non-JSON responses (grok sometimes adds prose)
2. Add explicit role prompts so each CLI knows its egregor job
3. Wire a simple "Gemma proposes → Egregor witnesses" demo script
4. (Later, when claude/codex stabilize) expose via tools/ or a skill

All of this stays in TEMPLE/subsandbox. Never auto-promoted.
