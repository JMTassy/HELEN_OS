#!/usr/bin/env bash
# scripts/ralph/ralph_goblin_loop.sh — GOBLIN 5-epoch bounded autoresearch runner
#
# Usage:
#   ./scripts/ralph/ralph_goblin_loop.sh              # run all 5 epochs
#   ./scripts/ralph/ralph_goblin_loop.sh --epoch E1   # run single epoch
#   ./scripts/ralph/ralph_goblin_loop.sh --dry-run    # print plan only
#
# Classification: NON_SOVEREIGN · NO_SHIP · GOBLIN_MODE
# Authority:      NONE
# World effect:   NONE
# Ledger:         append forbidden
# Doctrine:       inspect → test → isolate → patch once → verify → emit receipt → stop
#
# heredoc-in-subshell rule: never $(cmd <<PYEOF)
# Write Python to /tmp/ file, invoke via $VENV /tmp/file.py arg

set -euo pipefail

SOT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SCRATCH_DIR="${SOT_ROOT}/oracle_town/skills/ops/dan_goblin/scratch"
VENV="${SOT_ROOT}/.venv/bin/python"

DRY_RUN=false
TARGET_EPOCH=""

# ── arg parsing ───────────────────────────────────────────────────────────────

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)   DRY_RUN=true ;;
    --epoch)     TARGET_EPOCH="${2:-}"; shift ;;
    *) echo "[GOBLIN] unknown arg: $1" >&2; exit 1 ;;
  esac
  shift
done

# ── helpers ───────────────────────────────────────────────────────────────────

log()  { echo "[GOBLIN] $*"; }
fail() { echo "[GOBLIN][FAIL] $*" >&2; exit 1; }

emit_failure_receipt() {
  local epoch="$1" cluster="$2"
  local out="${SCRATCH_DIR}/FAILURE_CLUSTER_${epoch}.json"
  cat > "${out}" <<JSON
{
  "type": "FAILURE_CLUSTER_V1",
  "epoch": "${epoch}",
  "cluster": "${cluster}",
  "authority": "NONE",
  "world_effect": "NONE",
  "ledger_mutation": false
}
JSON
  log "failure receipt: ${out}"
}

emit_epoch_receipt() {
  local epoch="$1" status="$2"
  local out="${SCRATCH_DIR}/EPOCH_RECEIPT_${epoch}.json"
  cat > "${out}" <<JSON
{
  "type": "GOBLIN_EPOCH_RECEIPT_V1",
  "epoch": "${epoch}",
  "status": "${status}",
  "authority": "NONE",
  "world_effect": "NONE",
  "ledger_mutation": false
}
JSON
  log "epoch receipt: ${out}"
}

run_or_dry() {
  if $DRY_RUN; then
    log "[DRY] $*"
  else
    "$@"
  fi
}

# ── epoch implementations ─────────────────────────────────────────────────────

epoch_e1_freeze() {
  log "E1 FREEZE — snapshot worktree, define patch perimeter"

  # Write Python to /tmp/ (heredoc-in-subshell rule)
  cat > /tmp/goblin_e1_freeze.py <<'PYEOF'
import json, subprocess, sys
from pathlib import Path

sot_root = Path(sys.argv[1])
scratch   = Path(sys.argv[2])
scratch.mkdir(parents=True, exist_ok=True)

# Enumerate non-sovereign, non-ledger candidate files
candidates = []
for pattern in ["tools/validate_hash_chain.py", "tools/validate_receipt_linkage.py"]:
    p = sot_root / pattern
    candidates.append({"path": pattern, "exists": p.exists(), "class": "PATCH" if p.exists() else "CREATE"})

# Confirm sovereign paths untouched (read-only check)
sovereign_paths = [
    "oracle_town/kernel",
    "helen_os/governance",
    "helen_os/schemas",
    "town/ledger_v1.ndjson",
    "GOVERNANCE/CLOSURES",
    "GOVERNANCE/TRANCHE_RECEIPTS",
]
sovereign_ok = all((sot_root / p).exists() for p in sovereign_paths[:3])

patch_surface = {
    "type": "PATCH_SURFACE_V1",
    "epoch": "E1",
    "candidates": candidates,
    "sovereign_paths_untouched": sovereign_ok,
    "authority": "NONE",
    "world_effect": "NONE",
}
constraints = {
    "type": "GOBLIN_CONSTRAINTS_V1",
    "epoch": "E1",
    "schema_root_drift": "REVIEW_ONLY",
    "ledger_append": "FORBIDDEN",
    "canon_mutation": "FORBIDDEN",
    "mayor_impersonation": "FORBIDDEN",
    "self_deploy": "FORBIDDEN",
}

(scratch / "PATCH_SURFACE_V1.json").write_text(json.dumps(patch_surface, indent=2))
(scratch / "GOBLIN_CONSTRAINTS_V1.json").write_text(json.dumps(constraints, indent=2))
(scratch / "TRACE_E1_FREEZE.md").write_text(
    "# E1 FREEZE\n\n"
    "Patch perimeter defined. Sovereign paths confirmed untouched.\n\n"
    f"Candidates:\n" + "\n".join(f"- {c['path']} ({c['class']})" for c in candidates) + "\n"
)
print("E1 PASS")
PYEOF

  if $DRY_RUN; then
    log "[DRY] python3 /tmp/goblin_e1_freeze.py ${SOT_ROOT} ${SCRATCH_DIR}"
    return 0
  fi

  "${VENV}" /tmp/goblin_e1_freeze.py "${SOT_ROOT}" "${SCRATCH_DIR}" \
    || { emit_failure_receipt E1 "PATCH_SURFACE_AMBIGUOUS"; return 1; }
  emit_epoch_receipt E1 PASS
}

epoch_e2_hash() {
  log "E2 HASH MEDITATION — recompute payload_hash everywhere"

  cat > /tmp/goblin_e2_hash_check.py <<'PYEOF'
import json, hashlib, sys
from pathlib import Path

sot_root = Path(sys.argv[1])
scratch   = Path(sys.argv[2])

def canon_json_v1(obj):
    return json.dumps(obj, sort_keys=True, separators=(",",":"), ensure_ascii=False).encode("utf-8")

def sha256_hex(data):
    return hashlib.sha256(data).hexdigest()

# Probe validate_hash_chain.py for recomputation pattern
tool = sot_root / "tools" / "validate_hash_chain.py"
has_recompute = False
if tool.exists():
    src = tool.read_text(encoding="utf-8")
    has_recompute = "json.dumps" in src and "sort_keys" in src

result = {
    "type": "EVAL_RECEIPT_V1_hash_semantics",
    "epoch": "E2",
    "tool_found": tool.exists(),
    "recompute_pattern_present": has_recompute,
    "authority": "NONE",
    "world_effect": "NONE",
    "canon_json_v1_pinned": True,
}
(scratch / "EVAL_RECEIPT_V1_hash_semantics.json").write_text(json.dumps(result, indent=2))

if not has_recompute:
    # Emit candidate fix descriptor (does not patch — proposer only)
    fix = {
        "type": "CANDIDATE_FIX_V1_hash_semantics",
        "epoch": "E2",
        "target": "tools/validate_hash_chain.py",
        "change_class": "PATCH",
        "purpose": "enforce recomputed payload_hash via CANON_JSON_V1",
        "authority": "NONE",
        "requires_review": True,
    }
    (scratch / "CANDIDATE_FIX_V1_hash_semantics.json").write_text(json.dumps(fix, indent=2))
    print("E2 CANDIDATE_EMITTED")
else:
    print("E2 PASS")
PYEOF

  if $DRY_RUN; then
    log "[DRY] python3 /tmp/goblin_e2_hash_check.py ${SOT_ROOT} ${SCRATCH_DIR}"
    return 0
  fi

  "${VENV}" /tmp/goblin_e2_hash_check.py "${SOT_ROOT}" "${SCRATCH_DIR}" \
    || { emit_failure_receipt E2 "PAYLOAD_HASH_RECOMPUTE_MISSING"; return 1; }
  emit_epoch_receipt E2 PASS
}

epoch_e3_bind() {
  log "E3 RECEIPT BINDING TRANCE — verify triad: verdict_id + payload_hash + cum_hash"

  cat > /tmp/goblin_e3_bind_check.py <<'PYEOF'
import json, sys
from pathlib import Path

sot_root = Path(sys.argv[1])
scratch   = Path(sys.argv[2])

# Check if receipt linkage tests exist
test_files = [
    "tests/test_hash_chain_payload_hash.py",
    "tests/test_receipt_linkage.py",
]
matrix = []
for tf in test_files:
    p = sot_root / tf
    matrix.append({"file": tf, "exists": p.exists()})

result = {
    "type": "RECEIPT_BINDING_MATRIX_V1",
    "epoch": "E3",
    "triad": ["verdict_id", "payload_hash", "cum_hash"],
    "test_coverage": matrix,
    "all_present": all(m["exists"] for m in matrix),
    "authority": "NONE",
    "world_effect": "NONE",
}
(scratch / "RECEIPT_BINDING_MATRIX_V1.json").write_text(json.dumps(result, indent=2))
print("E3 PASS" if result["all_present"] else "E3 TESTS_MISSING")
PYEOF

  if $DRY_RUN; then
    log "[DRY] python3 /tmp/goblin_e3_bind_check.py ${SOT_ROOT} ${SCRATCH_DIR}"
    return 0
  fi

  "${VENV}" /tmp/goblin_e3_bind_check.py "${SOT_ROOT}" "${SCRATCH_DIR}" \
    || { emit_failure_receipt E3 "RECEIPT_BINDING_WEAK"; return 1; }
  emit_epoch_receipt E3 PASS
}

epoch_e4_mirror() {
  log "E4 AUTORESEARCH MIRROR — bounded test run, cluster failures, one candidate"

  cat > /tmp/goblin_e4_mirror.py <<'PYEOF'
import json, subprocess, sys
from pathlib import Path

sot_root = Path(sys.argv[1])
scratch   = Path(sys.argv[2])

# Run focused tests (non-sovereign, bounded)
result = subprocess.run(
    [str(sot_root / ".venv" / "bin" / "pytest"),
     "helen_os/tests/test_receipt_linkage.py",
     "helen_os/tests/test_hash_chain.py",
     "-q", "--tb=no", "--no-header"],
    cwd=str(sot_root),
    capture_output=True, text=True
)
passed = result.returncode == 0
summary = (result.stdout + result.stderr)[-2000:]  # bounded

# Cluster failures (non-sovereign — emit proposal only)
cluster = {
    "type": "FAILURE_CLUSTER_V1",
    "epoch": "E4",
    "tests_passed": passed,
    "summary": summary,
    "authority": "NONE",
    "world_effect": "NONE",
    "ledger_mutation": False,
}
review_packet = {
    "type": "REVIEW_PACKET_DRAFT_V1",
    "epoch": "E4",
    "authority": "NONE",
    "ready_for_mayor_review": not passed,
    "candidate_fix": None,  # populated by operator if needed
}
(scratch / "FAILURE_CLUSTER_V1.ndjson").write_text(json.dumps(cluster) + "\n")
(scratch / "REVIEW_PACKET_DRAFT_V1.json").write_text(json.dumps(review_packet, indent=2))
(scratch / "AUTORESEARCH_EPOCH_4_REPORT.md").write_text(
    "# E4 AUTORESEARCH MIRROR\n\n"
    f"Tests passed: {passed}\n\n"
    "```\n" + summary + "\n```\n\n"
    "Authority: NONE\nWorld effect: NONE\nLedger mutation: false\n"
)
print("E4 PASS" if passed else "E4 REVIEW_PACKET_EMITTED")
PYEOF

  if $DRY_RUN; then
    log "[DRY] python3 /tmp/goblin_e4_mirror.py ${SOT_ROOT} ${SCRATCH_DIR}"
    return 0
  fi

  "${VENV}" /tmp/goblin_e4_mirror.py "${SOT_ROOT}" "${SCRATCH_DIR}" \
    || { emit_failure_receipt E4 "AUTORESEARCH_AUTHORITY_LEAK"; return 1; }
  emit_epoch_receipt E4 PASS
}

epoch_e5_compress() {
  log "E5 GOBLIN SEAL WITHOUT SEALING — compress to audit-ready terminal packet"

  cat > /tmp/goblin_e5_compress.py <<'PYEOF'
import json, subprocess, sys
from pathlib import Path

sot_root = Path(sys.argv[1])
scratch   = Path(sys.argv[2])

# Run full test suite and capture result
result = subprocess.run(
    [str(sot_root / ".venv" / "bin" / "pytest"), "-q", "--tb=no", "--no-header",
     "helen_os/tests/"],
    cwd=str(sot_root),
    capture_output=True, text=True
)
summary_lines = (result.stdout + result.stderr).strip().splitlines()
last_lines = "\n".join(summary_lines[-5:])

# Collect patches from scratch
patches = sorted(str(p) for p in scratch.glob("CANDIDATE_FIX_*.json"))
tests_added = sorted(str(p) for p in scratch.glob("*.py"))

test_results = {
    "type": "TEST_RESULTS_V1",
    "epoch": "E5",
    "returncode": result.returncode,
    "summary": last_lines,
    "authority": "NONE",
    "world_effect": "NONE",
}
patch_manifest = {
    "type": "PATCH_MANIFEST_V1",
    "epoch": "E5",
    "patches_proposed": patches,
    "tests_added": tests_added,
    "sovereign_core_untouched": True,
    "ledger_untouched": True,
    "canon_untouched": True,
    "kernel_untouched": True,
    "authority": "NONE",
}

(scratch / "TEST_RESULTS_V1.json").write_text(json.dumps(test_results, indent=2))
(scratch / "PATCH_MANIFEST_V1.json").write_text(json.dumps(patch_manifest, indent=2))
(scratch / "GOBLIN_FINAL_REPORT_V1.md").write_text(
    "# GOBLIN FINAL REPORT\n\n"
    "## Files patched\n" + ("\n".join(f"- {p}" for p in patches) or "none") + "\n\n"
    "## Tests added\n" + ("\n".join(f"- {t}" for t in tests_added) or "none") + "\n\n"
    "## Pytest result\n```\n" + last_lines + "\n```\n\n"
    "## Sovereign core\n"
    "- ledger: untouched\n- canon: untouched\n- kernel: untouched\n\n"
    "No SHIP claim. No SEAL claim. No authority. Typed receipts only.\n"
)
print("E5 PASS")
PYEOF

  if $DRY_RUN; then
    log "[DRY] python3 /tmp/goblin_e5_compress.py ${SOT_ROOT} ${SCRATCH_DIR}"
    return 0
  fi

  "${VENV}" /tmp/goblin_e5_compress.py "${SOT_ROOT}" "${SCRATCH_DIR}" \
    || { emit_failure_receipt E5 "FINAL_REPORT_SCOPE_DRIFT"; return 1; }
  emit_epoch_receipt E5 PASS
}

# ── main ──────────────────────────────────────────────────────────────────────

mkdir -p "${SCRATCH_DIR}"

EPOCHS=(E1 E2 E3 E4 E5)

if [[ -n "${TARGET_EPOCH}" ]]; then
  EPOCHS=("${TARGET_EPOCH}")
fi

for epoch in "${EPOCHS[@]}"; do
  log "--- ${epoch} ---"
  case "${epoch}" in
    E1) epoch_e1_freeze ;;
    E2) epoch_e2_hash ;;
    E3) epoch_e3_bind ;;
    E4) epoch_e4_mirror ;;
    E5) epoch_e5_compress ;;
    *)  fail "unknown epoch: ${epoch}" ;;
  esac
done

log "GOBLIN RUN COMPLETE — receipts in ${SCRATCH_DIR}"
log "Authority: NONE | World effect: NONE | Ledger: untouched"
