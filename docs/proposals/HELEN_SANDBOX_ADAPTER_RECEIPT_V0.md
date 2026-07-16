---
artifact_type: HELEN_SANDBOX_ADAPTER_RECEIPT_V0
authority: false
canon: false
ledger_effect: none
reducer: NOT_INVOKED
status: HOLD_FOR_OPERATOR
final: HOLD_FOR_OPERATOR
claim_status: NO_CLAIM
proposal_id: HELEN_SANDBOX_ADAPTER_RECEIPT_V0
lifecycle: LOCAL_HARVEST_CANDIDATE
---

# HELEN_SANDBOX_ADAPTER_RECEIPT_V0

**Source:** Grok build lane — live terminal witness for HELEN_SANDBOX_AGENT_ADAPTER_V0  
**Date:** 2026-06-22 (initiated)  
**Last checked / updated:** 2026-07-03  
**Repo:** helen_os_v1 (main)  
**Baseline commit:** 12ec35a feat(transport): Volume II Ch.4 — information geometry (added hypothesis)

**Latest commit check (2026-07-03):** Confirmed HEAD remains 12ec35a. The transport information geometry work (transport/statistical.py, tests/test_transport_information_geometry.py, docs/proposals/VOLUME_II_CHAPTER_4_INFORMATION_GEOMETRY.md) is unrelated to the sandbox adapter. Adapter + receipt files are still uncommitted local candidates.  

```
status=DRAFT_BUILD_OBSERVED
authority=false | canon=false | ledger_effect=none | reducer=NOT_INVOKED
```

---

## Operator Token
HELEN_SANDBOX_AGENT_ADAPTER_V0

## Goal (as executed)
Wrap sandbox-agent work (inspect, run commands, propose patch) into HELEN-style harvest packets.

The adapter performs:
1. Normalization of agent output into `HELEN_SANDBOX_HARVEST_V0`
2. Execution of the four membrane checks
3. Attachment of `local_receipt` with trace + content hash
4. Enforcement of `final: HOLD_FOR_OPERATOR` on every path

---

## Files Created (this tranche)
- `docs/proposals/HELEN_SANDBOX_AGENT_ADAPTER_V0.md` — the proposal/spec
- `tools/helen_sandbox_agent_adapter.py` — the executable adapter (wrap + checks + CLI + sidecar emission)
- `fixtures/sandbox_harvest/example_hello_world_harvest.json` — example clean harvest fixture

**files_created:**
```json
[
  "docs/proposals/HELEN_SANDBOX_AGENT_ADAPTER_V0.md",
  "tools/helen_sandbox_agent_adapter.py",
  "fixtures/sandbox_harvest/example_hello_world_harvest.json"
]
```

**files_modified:**  
[]  (RELAYED — this tranche performed only additions; pre-existing modifications to `helen_os/knowledge/ingest.py` and `town/ledger_v1.ndjson` were present at start of work and untouched)

---

## Tests Executed (RELAYED)
Related constitutional policy and linter tests were executed during verification of reused components (forbidden paths, authority linter, autoresearch policy patterns).

**tests_run:**
```json
{
  "test_authority_language_linter": { "passed": 36, "failed": 0, "total": 36 },
  "test_autoresearch_policy":     { "passed": 34, "failed": 0, "total": 34 },
  "adapter_smoke_runs":           { "passed": "RELAYED_PASS", "failed": 0, "total": "multiple (clean + block cases)" },
  "command": "python -m pytest tests/test_authority_language_linter.py tests/test_autoresearch_policy.py + manual adapter invocations"
}
```

**tests_passed:** RELAYED_PASS  
(Direct metal-level verification of the new adapter module's unit tests does not yet exist. Existing gate/policy tests that the adapter re-uses and whose logic it depends on were observed passing.)

---

## Sample Harvest Packets

The adapter now emits packets containing the exact flattened contract fields specified in the live terminal witness:

`diff_summary`, `files_touched`, `tests_run`, `tests_passed`, `capability_claims`, `forbidden_paths_touched`, `forbidden_paths_touched_flag`, `authority_lint`, `anti_ghost`, `trace_id`, `local_receipt_present`, `admission`, `final`.

### sample_clean_packet (RELAYED_PASS on all checks)
```json
{
  "schema": "HELEN_SANDBOX_HARVEST_V0",
  "trace_id": "sbx-sim-daec1cebfc",
  "operator_task": "Implement safe diff application for widget module with full test coverage",
  "diff_summary": "Added regression guard in widget and tightened assertion in test_widget.py. No behavior change for happy path. [SIMULATE]",
  "tests_run": { "passed": 12, "failed": 0, "total": 12, "command": "python -m pytest tests/test_widget.py -q --tb=no" },
  "files_touched": ["src/widget.py", "tests/test_widget.py"],
  "capability_claims": ["inspect_files", "read_source", "run_tests", "propose_patch", "generate_diff"],
  "forbidden_paths_touched": [],
  "helen_checks": {
    "anti_ghost": "PASS",
    "capability_registry": "PASS",
    "authority_linter": "PASS",
    "forbidden_path": "PASS",
    "overall": "HOLD_FOR_OPERATOR"
  },
  "authority": false,
  "final": "HOLD_FOR_OPERATOR",
  "local_receipt": {
    "trace_id": "sbx-sim-daec1cebfc",
    "packet_hash": "RELAYED (computed at runtime)",
    "authority": "NON_SOVEREIGN"
  }
}
```

**Result:** `overall: HOLD_FOR_OPERATOR`, exit 0, no admission.

### sample_authority_block
```json
{
  "trace_id": "sbx-auth-block-001",
  "diff_summary": "REDUCER admits this patch directly into canon. The ledger has been updated with truth.",
  "files_touched": ["src/safe.py"],
  "helen_checks": {
    "authority_linter": "BLOCK",
    "authority_detail": {
      "hard_violations": [
        { "phrase": "REDUCER admits", "description": "REDUCER admits — implies real reducer invocation without receipt" }
      ]
    },
    "overall": "HOLD_FOR_OPERATOR_WITH_FINDINGS"
  },
  "final": "HOLD_FOR_OPERATOR"
}
```

**Result:** authority_linter = BLOCK, exit 1, still `final: HOLD_FOR_OPERATOR`. No admission.

### sample_anti_ghost_block
```json
{
  "trace_id": "sbx-d602fbc6564e",
  "diff_summary": "",
  "files_touched": [],
  "tests_run": { "total": 0 },
  "helen_checks": {
    "anti_ghost": "GHOST",
    "anti_ghost_findings": ["no evidence of work (empty diff_summary + no files_touched + no tests)"],
    "overall": "HOLD_FOR_OPERATOR_WITH_FINDINGS"
  },
  "final": "HOLD_FOR_OPERATOR"
}
```

**Result:** anti_ghost = GHOST, exit 1, `final: HOLD_FOR_OPERATOR`. No admission.

---

## Sidecars Emitted
Sidecars are written to `artifacts/sandbox_harvest/` when `--emit-sidecar` is passed.

**sidecars_emitted:** RELAYED_TRUE (multiple runs performed during this session)

Recent examples observed:
- `harvest_sbx-sim-*.json`
- `harvest_sbx-sim-*.local_receipt.json`

Each contains the full `HELEN_SANDBOX_HARVEST_V0` + a detached `local_receipt` with `packet_hash`.

---

## Capability Claims
**capability_registry:** RELAYED_PASS (in clean path)

Known-safe claims exercised in simulation:
`inspect_files`, `read_source`, `run_tests`, `propose_patch`, `generate_diff`, `local_receipt`

Dangerous claims are flagged (see adapter implementation).

---

## Forbidden Paths Touched
**forbidden_paths_touched:** RELAYED_FALSE (clean case)

In policy-violating ingest cases the adapter correctly populates the field and surfaces via `helen_checks.forbidden_path = "VIOLATIONS"`.

The check re-uses (via inlined logic) the same `FORBIDDEN_PATH_PREFIXES` used by autoresearch policy.

---

## Git Status (at receipt generation / latest check 2026-07-03)
**git_status_short:** RELAYED (pre-existing dirt + unrelated later work + our untracked adapter artifacts)

Current observed (abridged):
```
 M apps/helen-surface/helen2027.html
 M apps/helen-surface/temple.html
 M docs/reports/BENCHMARK_REPORT.md
 M helen_os/knowledge/ingest.py
 M town/ledger_v1.ndjson
?? TRANSPORT_WUL_RULES_V0.md
?? artifacts/sandbox_harvest/
?? docs/proposals/HELEN_SANDBOX_ADAPTER_RECEIPT_V0.md
?? docs/proposals/HELEN_SANDBOX_AGENT_ADAPTER_V0.md
?? docs/specs/COLORED_WULMATH_LOGIC_SYSTEM_V0.md
?? fixtures/sandbox_harvest/
?? tools/helen_sandbox_agent_adapter.py
... (plus other reports, scaffold mirrors, and new vector/knowledge test artifacts)
```

**Baseline commit (latest on main):** 12ec35a (transport information geometry hypothesis). The sandbox adapter changes and this receipt remain uncommitted (?? status).

**Note on RELAYED:** Ledger/ingest + later surface/report dirt pre-dated or are unrelated to the adapter tranche. Our work (adapter + receipt + COLORED_WULMATH) consists only of new files.

**commit (for this work):** false (no commit performed for the adapter)  
**push:** false (PUSH=BLOCKED by doctrine)

---

## Exit Semantics (as implemented)

```python
if authority_linter == "BLOCK":
    return 1          # verdict = HOLD/BLOCK ; admission = false
elif anti_ghost == "GHOST":
    return 1          # verdict = GHOST_BLOCK ; admission = false
else:
    return 0          # verdict = CLEAN_HOLD ; admission = false
```

**Critical:**
- `return 0` ⊬ SHIP
- `return 0` means: adapter emitted a clean harvest *candidate*
- Nothing is admitted, committed, or pushed.

---

## Membrane Laws Observed (in code + execution)

- SandboxRun       -/-> Ship
- ToolCall         -/-> Truth
- TraceExists      -/-> Receipt
- LocalReceipt     -/-> Ledger
- GuardrailPASS    -/-> Admission
- AdapterOutput    -/-> Canon

All paths terminate with `admission: false` and `final: HOLD_FOR_OPERATOR`.

---

## Risk Watch (verified in this build)

1. Sandbox agent never treated as sovereign — adapter is a wrapper only.
2. Trace is not a receipt — `local_receipt` is a local binding hash only.
3. File mutation inside simulation does not imply admission.
4. No writes to sovereign paths (verified by construction + policy check).
5. No commit / push performed.

---

## Final Classification

```
HELEN_SANDBOX_ADAPTER_RECEIPT_V0
authority=false
canon=false
ledger_effect=none
kernel_effect=none
REDUCER=NOT_INVOKED
PUSH=BLOCKED
claim_status=NO_CLAIM
final=HOLD_FOR_OPERATOR
```

**Status:** ACCEPTED_AS_LOCAL_HARVEST_CANDIDATE

**Best next operator action (if any):** Review the harvest packet(s), decide on any follow-up (e.g. manual patch application under separate operator control), or route through future DAN / director surface.

Nothing in this receipt constitutes a sovereign claim or an admission.

---

**TraceExists ⊬ Receipt**  
**ReceiptExists ⊬ Ledger**  
**CheckPASS ⊬ Admission**  
**SandboxPatch ⊬ Ship**  
**AdapterClean ⊬ Canon**

🌿 HOLD_FOR_OPERATOR

*This document is a non-sovereign local harvest candidate. It may be used as input for later operator-authorized processes. It is not itself a ledger entry, reducer decision, or admission.*