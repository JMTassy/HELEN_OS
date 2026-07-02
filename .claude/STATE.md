# HELEN Session State — Compounding Memory

The 5-stage progression written down (Continual Learning Bench):
FAIL → INVESTIGATE → VERIFY → DISTILL → CONSULT.

**Write before walking away. Read at session start.** Without the write,
the next session restarts from zero.

---

## Verified facts (stage 3 — stop guessing about these)

- Branch `claude/code-review-optimizations-hx26jn` is the active work branch. Never push elsewhere without explicit permission.
- Sovereign firewall is absolute: `helen_os/governance/`, `helen_os/schemas/`, `oracle_town/kernel/`, `town/ledger_v1.ndjson` are read-only. Verified via CLAUDE.md + repeated enforcement.
- Garden zone (`temple/gardens/`) is NO_CLAIM by GARDEN_NO_CLAIM_RULE_V0. Wildest material permitted; only CROSSING refused. Safety is LOCATIONAL, not LEXICAL.
- Skills live in `.claude/commands/` as slash commands. Registered automatically by the harness on write. Verified: 11 skills registered this session.
- K-tau `datetime.utcnow()` is a mu_DETERMINISM violation — use `datetime.now(timezone.utc)`. Most common recurring lint failure.
- After any CLAUDE.md edit: `python3 scratchpad/generate_claude_index.py` before commit, or CI fails.
- ornith-helen:v4 gate PASSED, registered, unpromoted (operator must repoint .env).

## General rules (stage 4 — consult before re-deriving)

- **Maker ≠ grader.** The agent that produces an artifact never verifies it. Spawn an independent verifier sub-agent (no exposure to the maker's reasoning). Confirmed by Anthropic Parameter Golf; matches HELEN's K2 anti-violation (proposer ≠ validator).
- **Barbell routing.** Fable plans (10%) → local models grunt (80%, helen-gemma4-12b/ORNITH/GEMMA/DEEPSEEK, free) → Fable verifies (10%). Cloud only for repo-navigation tools or 2x local failure.
- **Bounded retry is an axiom.** 2 strikes → escalate. Never open-ended. TERMINATION IS SACRED.
- **Format before content.** Cheapest rejection goes first: schema/format gate, then semantic gate. WUL Packet Validator tier-1 before tier-2.
- **Compost method.** External corpus → extract structural topology only → discard framing → map to existing HELEN mechanism → stay NO_CLAIM. The source is a witness, not an authority.
- **NO_CLAIM discipline.** Garden artifacts carry `authority=false · canon=false · admission_status=NOT_ADMITTED`. Never render 🟢🟡⚪ on them.

## Open failures (stage 1 → 2, investigate next session)

- **ktau_needle_fix**: the K-tau linter needle `"datetime.now("` matches the doc-mandated `datetime.now(timezone.utc)`. Proven on metal (permanent Δ>0 in tests/test_transport_drift.py). Fix is operator-gated. Acceptance test already exists.
- **GOBLIN-RELAY-1**: dual-miner dispatch (ORNITH overlay-v3 vs helen-gemma4-12b) staged, awaiting local GPU dispatch after v4 eval gate. Output → CHIDDUSH+HAL gate.
- **6 report-only review findings**: executor burn-on-failure, fire-and-forget ledger bridge, linter document-global pardon, twin-sim economics, LoRA masking, batch-runner reruns. All need operator decision.

## Lessons learned (stage 4 distillations)

- Fable's safety classifier can silently downgrade to Opus on requests that look like cyber/bio/chem OR that ask the model to "show its reasoning." Never put "explain your reasoning" in a system prompt. Architect for the fallback.
- Vision-verify is underused: screenshot → verifier reads it against goal + design tokens + previous screenshot. Applies to HELEN's 10 operator surfaces (`/vision-audit`, `/surface-iterate`).
- A skill that never gets written to is wasted scaffolding. After any non-trivial failure, write the lesson into the skill itself, not just here.
- Convergence evidence is the strongest chiddush: when an independent external system arrives at the same structure HELEN already has, the external system is a witness, not a source. (Faust protocol ↔ gate ordering; Hekspakat 4-mode ↔ FOCUS/WITNESS/ORACLE/TEMPLE.)

## Last session (stage 5 — resume, don't restart)

2026-07-02 · Built the HELEN skill system (11 skills, 5 agents), amended barbell to local-model middle, created memory/instructions/ROUTING/STATE files, mined 3 grimoire corpora into garden compost (Faust, Sacred Names, Radionics), built WULMOJI_ESOTERIC_TEMPLE_V0.
Next: dispatch GOBLIN-RELAY-1 when local GPU frees; triage the 6 report-only findings; consider ktau_needle_fix if operator gives GO.
