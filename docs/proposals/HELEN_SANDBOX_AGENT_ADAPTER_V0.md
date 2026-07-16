---
authority: false
canon: false
lifecycle: PROPOSAL
ledger_effect: NONE
status: HOLD_FOR_OPERATOR
proposal_id: HELEN_SANDBOX_AGENT_ADAPTER_V0
final: HOLD_FOR_OPERATOR
---

# HELEN_SANDBOX_AGENT_ADAPTER_V0

**Classification:** NON_SOVEREIGN · NO_CLAIM · OPERATOR_BRIDGE  
**Authority:** NONE  
**Route:** tools/ (operator surface) + docs/proposals (doctrine)  
**Goal:** Wrap exactly one OpenAI Sandbox Agent (or equivalent sandboxed coding agent) run as a HELEN harvest packet. The packet is always emitted under HOLD_FOR_OPERATOR.

---

## One-line

Operator task → sandbox agent execution (inspect / test / patch) → structured HELEN_SANDBOX_HARVEST_V0 packet → HELEN checks (AntiGhost, CapabilityRegistry, AuthorityLinter, forbidden path policy) → HOLD_FOR_OPERATOR.

Nothing is admitted. Nothing is sovereign. Operator decides.

---

## Input

- `operator_task`: free text or structured directive from operator ("Add X; make tests pass; do not touch Y").

The adapter itself does **not** execute the agent. The sandbox agent (OpenAI code interpreter, e2b, custom computer-use agent, etc.) runs under operator control. The adapter **wraps** the observable result of one such run.

---

## What the agent is permitted to do (in its sandbox)

- Inspect files (read source, list dirs)
- Run tests (pytest, make test, etc. inside the sandbox env)
- Propose a patch (produce diff or file-level edit descriptions)

---

## Mandatory agent output contract (what must be captured)

The adapter normalizes whatever the sandbox agent emits into a `HELEN_SANDBOX_HARVEST_V0` packet containing at minimum:

| Field                  | Type          | Meaning |
|------------------------|---------------|---------|
| `trace_id`             | string        | Unique id for this agent run (sandbox session / thread / response id) |
| `diff_summary`         | string        | Human + machine readable summary of the intent and effect of changes |
| `tests_run`            | object        | `{passed, failed, total, command?, stdout_tail?}` |
| `files_touched`        | string[]      | Relative paths written, modified, or proposed |
| `forbidden_paths_touched` | string[]   | Self-report + adapter-detected sovereign/forbidden paths |
| `capability_claims`    | string[]      | Capabilities the agent asserts it exercised (e.g. "inspect_files", "run_tests", "propose_patch") |
| `local_receipt`        | object        | Agent- or adapter-produced receipt envelope for the run (includes trace binding + content hash) |

Additional recommended fields (adapter will carry if present):
- `proposed_diff` (unified diff or patch summary)
- `raw_transcript_ref`
- `sandbox_env` (image, provider, limits)

---

## HELEN checks (always executed by adapter, never bypassed)

1. **AntiGhost**
   - trace_id must be present and non-empty.
   - Evidence of work required: at least one of (non-trivial diff_summary, files_touched non-empty, tests_run.total > 0).
   - local_receipt must bind to the packet content (hash present and consistent).
   - Ghost → overall verdict forces stronger quarantine language; packet still emitted but flagged.

2. **CapabilityRegistry (V0)**
   - capability_claims must be a list.
   - Claims are cross-checked against known-safe sandbox claims for this class of agent.
   - Dangerous claims (ledger write, kernel mutation, outbound network without declaration, privilege escalation) are flagged.
   - Unknown claims are recorded (forward compatible) but do not auto-admit.

3. **AuthorityLinter**
   - Run `tools/validators/authority_language_linter.py` (HARD) over diff_summary + any free-text summary fields.
   - HARD violation without attached reducer/ledger receipt marker → BLOCK component of the check.
   - The harvest packet itself may never contain "REDUCER admits", "admitted to canon", "ledger updated", etc.

4. **forbidden path policy**
   - Reuse / mirror `check_forbidden_paths` logic from `temple/autoresearch/autoresearch_policy.py`.
   - Any file in `files_touched` that matches FORBIDDEN_PATH_PREFIXES is recorded in `forbidden_paths_touched`.
   - Sovereign paths (ledger, kernel, governance, schemas, mayor_*, GOVERNANCE/*) are never auto-tolerated.

All four checks produce structured findings. The adapter never suppresses a finding.

---

## Packet schema (HELEN_SANDBOX_HARVEST_V0)

```json
{
  "schema": "HELEN_SANDBOX_HARVEST_V0",
  "trace_id": "sbx-9f3c2a...",
  "operator_task": "string",
  "diff_summary": "string",
  "tests_run": {
    "passed": 0,
    "failed": 0,
    "total": 0,
    "command": "string?",
    "summary": "string?"
  },
  "files_touched": ["path/to/file.py"],
  "forbidden_paths_touched": ["FORBIDDEN: 'town/ledger...' matches ..."],
  "capability_claims": ["inspect_files", "run_tests", "propose_patch"],
  "local_receipt": {
    "trace_id": "...",
    "packet_hash": "sha256 of canon content",
    "generated_at": "iso8601",
    "authority": "NON_SOVEREIGN"
  },
  "authority": false,
  "sovereign": false,
  "canon": false,
  "ledger_effect": "none",
  "status": "HOLD_FOR_OPERATOR",
  "final": "HOLD_FOR_OPERATOR",
  "helen_checks": {
    "anti_ghost": "PASS|GHOST",
    "capability_registry": "PASS|FLAGGED",
    "authority_linter": "PASS|BLOCK",
    "forbidden_path": "PASS|VIOLATIONS",
    "overall": "HOLD_FOR_OPERATOR"
  }
}
```

`additionalProperties: false` discipline recommended for consumers. Adapter emits with the fields above.

---

## Lifecycle & final state

- Every wrapped run **terminates** as `HOLD_FOR_OPERATOR`.
- The adapter emits the packet + a sidecar local receipt.
- No path leads to auto-admission, reducer, or ledger write.
- Operator (or later DAN/HAL/MAYOR flow) consumes the packet as a proposal artifact.
- Promotion path (if any) is the standard operator-authorized SKILL_PROMOTION or equivalent after review — outside scope of V0.

---

## Usage (V0)

```bash
# Demo / smoke (no external agent)
python3 tools/helen_sandbox_agent_adapter.py \
  --task "Fix the failing widget test and add a regression case" \
  --simulate

# Wrap output from a real sandbox agent run
python3 tools/helen_sandbox_agent_adapter.py \
  --task "$(cat task.txt)" \
  --ingest-json /tmp/agent_run_42.json \
  --emit-sidecar
```

The adapter prints the harvest packet to stdout (JSON). With `--emit-sidecar` it also writes:

- `harvest_<trace_id>.json`
- `harvest_<trace_id>.local_receipt.json`

---

## Non-sovereignty invariants (enforced)

- `authority` is always the boolean `false`.
- `sovereign`, `canon` always `false`.
- `ledger_effect` always `"none"`.
- `final` / `status` = `HOLD_FOR_OPERATOR`.
- Adapter never writes `town/ledger*`, `GOVERNANCE/*`, `helen_os/governance/*`, `helen_os/schemas/*`, `oracle_town/kernel/*`, `mayor_*`.
- Adapter does not invoke `helen_say.py`, does not call reducers, does not claim verdicts.

---

## Relation to existing

- Reuses `AuthorityLinter` (`tools/validators/authority_language_linter.py`).
- Reuses forbidden path list/policy pattern from autoresearch policy (V0 inlines for tool portability).
- Similar in spirit to `MIRROR_OF_ADMISSION_V1`, `DAN_GOBLIN` receipt schema (`schemas/helen_dan/receipt.schema.json`), and swarm supervision EVENT_CARD (files_touched + receipts).
- Complements (does not replace) HELEN Director / render sidecar work.
- Is a **harvest bridge**, not an execution kernel.

---

## Acceptance for V0

A correct implementation must:

1. Accept an operator task.
2. Accept (or simulate) an agent result containing the required output fields.
3. Produce a well-formed `HELEN_SANDBOX_HARVEST_V0` dict/JSON.
4. Execute all four named HELEN checks and attach `helen_checks`.
5. Force `final: HOLD_FOR_OPERATOR` (and equivalent status fields).
6. Emit a `local_receipt` bound by trace_id + content hash.
7. Never mutate sovereign state.
8. Pass a manual smoke run (`--simulate`) producing clean structured output.

---

## Future (post V0, operator authorized only)

- Real OpenAI / e2b / computer-use driver that auto-emits the contract fields.
- Capability manifest registry wiring (manifest sha + declared capabilities).
- AntiGhost with SHA proof of proposed patch files.
- Operator rating surface for harvested proposals.
- Batch director integration (seed selection from harvest packets).

---

**This document + adapter implementation are NON_SOVEREIGN, HOLD_FOR_OPERATOR.**

No claim is made. No receipt is sovereign. Operator decides.