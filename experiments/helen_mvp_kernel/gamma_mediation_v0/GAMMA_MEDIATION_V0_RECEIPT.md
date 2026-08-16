# ΓE MEDIATION V0 — K_TAU GUARD WIRED INTO EXECUTOR EFFECT PATHS

- Date: 2026-08-16
- AUTHORITY=false · CANON=false · LEDGER_EFFECT=none · NOT COMMITTED, NOT PUSHED
- Operator authorization: explicit ("Choose 1. Yes.") for exactly two root
  `helen_os/` executor files. Firewalled paths untouched.
- Proposer ≠ Validator: independent peer-review sub-agent PASS 6/6
  (fresh context, criteria re-verified literally, adversarial spot-checks of
  its own devising).

## OBSERVED (witnessed this session)

- `helen_os/helen_executor.py` — `pre_dispatch_guard` called in
  `run_executor_manifest` after schema check, before mkdir/subprocess/any
  effect; block raises `ExecutorViolation("K_TAU_BLOCKED:...")`. Fail-closed
  import (guard unloadable ⇒ module unloadable; no silent bypass).
- `helen_os/executor/bounded_executor_v1.py` — guard at top of
  `BoundedExecutor.execute`, before handler resolution and registry writes;
  block ⇒ REJECT decision + FAILURE result, `failure_code=jurisdiction_blocked`
  (new code; schema allows string, sovereign schemas not modified), no
  artifact, no registry mutation (proved by non-duplicate re-execution test).
- `tests/test_effect_path_mediation.py` (NEW) — 13/13 PASS: forged claim types
  (VERDICT/CANON), authority-shaped string, unknown operation class, missing
  claim type, empty dispatch, unhashable claim type (fail-closed crash before
  effect), terminality (no mkdir / no file / no registry write on block),
  positive controls (RECEIPT/AUDIT admitted, effect + receipts emitted).
- Regression: boundary+gate suites 37/37; bounded executor 52/52;
  `make test` 742 passed / 5 skipped / 1 failed.
- Peer-review adversarial extras: lowercase "receipt" blocked; family/op
  injection via request keys inert (executors pin operation class internally);
  explicit claim_type=None blocked (default undefeatable to None).

## EFFECT-SURFACE ENUMERATION (step 2 of the falsification plan)

| Path | Mediation status |
|---|---|
| `run_executor_manifest` (subprocess+fs) | WIRED this tranche |
| `BoundedExecutor.execute` (fs writes) | WIRED this tranche |
| `tools/run_hal_epoch.py` (cognition) | already wired (pre-existing) |
| `tools/helen_say.py` → `ndjson_writer` (ledger) | kernel-gated (sovereign bridge, out of scope) |
| direct handler `.execute()` internal API | OUT OF SCOPE — documented in test docstring; equivalent to raw file I/O; process-boundary job (kernel_guard/hooks) |
| ad-hoc `subprocess`/file writes in scripts/tools | NOT MEDIATED — pre-existing surface, unchanged this tranche |

## NOT DONE / NOT CLAIMED

- `make test` warren failure (`test_real_feed_on_disk_replays_if_present`) is
  PRE-EXISTING: on-disk staleness assertion, stdlib-only imports, causally
  disjoint (peer-review verified independently).
- Witness verification (w_A), ΓE authority checks, replay-of-effect
  verification: NOT in this tranche. This gate enforces claim-type
  jurisdiction only. Non-amplification holds under the TESTED entry points,
  not universally.
- No commit, no push, no CLAUDE.md edits, no sovereign writes.

## DRIFT SIGNAL

During peer review an unrelated untracked dir appeared:
`experiments/helen_mvp_kernel/goblin_substitutability_v0/` — not created by
this session. Reported per mirror/drift discipline.
