#!/usr/bin/env bash
# scripts/ralph/ralph.sh — HELEN_DAN_RALPH_V0 epoch runner
#
# Usage:
#   ./scripts/ralph/ralph.sh                      # auto-select highest-priority todo
#   ./scripts/ralph/ralph.sh --story HD-001       # run specific story
#   ./scripts/ralph/ralph.sh --dry-run            # print plan only
#   ./scripts/ralph/ralph.sh --close HD-001 GREEN # close epoch after DAN work
#   ./scripts/ralph/ralph.sh --close HD-001 FAILED TEST_FAILURE
#
# Classification: NON_SOVEREIGN · NO_SHIP · PROPOSAL
# Receipt path:   oracle_town/skills/ops/dan_goblin/receipts/
#
# Doctrine:
#   Temple explores. Mayor specifies. Ralph cadences.
#   DAN implements. HAL verifies. Reducer decides. Ledger remembers.
#   One epoch = one story. No receipt = no claim.

set -euo pipefail

SOT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DAN_ROOT="${SOT_ROOT}/oracle_town/skills/ops/dan_goblin"
PRD_FILE="${DAN_ROOT}/prd.json"
RECEIPTS_DIR="${DAN_ROOT}/receipts"
SCRATCH_DIR="${DAN_ROOT}/scratch"
PROGRESS_FILE="${SCRATCH_DIR}/progress.txt"
VENV="${SOT_ROOT}/.venv/bin/python"

DRY_RUN=false
STORY_ID=""
CLOSE_MODE=false
CLOSE_OUTCOME=""
CLOSE_FAILURE_TYPE="null"

# ── arg parsing ───────────────────────────────────────────────────────────────

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)    DRY_RUN=true ;;
    --story)      STORY_ID="${2:-}"; shift ;;
    --story=*)    STORY_ID="${1#--story=}" ;;
    --close)
      CLOSE_MODE=true
      STORY_ID="${2:-}"; shift
      CLOSE_OUTCOME="${2:-}"; shift
      CLOSE_FAILURE_TYPE="${3:-null}"; [[ $# -ge 1 ]] && shift || true
      ;;
    *) echo "Unknown arg: $1" >&2; exit 1 ;;
  esac
  [[ $# -gt 0 ]] && shift || true
done

# ── close mode ────────────────────────────────────────────────────────────────

if [[ "${CLOSE_MODE}" == "true" ]]; then

  [[ -z "${STORY_ID}" ]]    && { echo "ERROR: --close requires story_id" >&2; exit 1; }
  [[ -z "${CLOSE_OUTCOME}" ]] && { echo "ERROR: --close requires GREEN|FAILED" >&2; exit 1; }
  [[ "${CLOSE_OUTCOME}" != "GREEN" && "${CLOSE_OUTCOME}" != "FAILED" ]] && {
    echo "ERROR: outcome must be GREEN or FAILED" >&2; exit 1; }

  TIMESTAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  SESSION_SALT="ralph-close-$$-${RANDOM}"
  EPOCH_ID="$(echo -n "${STORY_ID}:${TIMESTAMP}:${SESSION_SALT}" | shasum -a 256 | cut -c1-12)"
  RECEIPT_FILE="${RECEIPTS_DIR}/${STORY_ID}_${EPOCH_ID}.json"

  mkdir -p "${RECEIPTS_DIR}" "${SCRATCH_DIR}"

  echo "=== RALPH CLOSE: ${STORY_ID} ${CLOSE_OUTCOME} ==="

  # Collect artifact manifest (write to tmp file — heredoc-in-subshell is unreliable)
  cat > /tmp/ralph_manifest.py <<'PYEOF'
import sys, json, hashlib, pathlib
dan_root = sys.argv[1]
sot_root = sys.argv[2]
artifacts = pathlib.Path(dan_root) / "artifacts"
manifest = []
if artifacts.exists():
    for p in sorted(artifacts.rglob("*")):
        if p.is_file():
            digest = hashlib.sha256(p.read_bytes()).hexdigest()
            manifest.append({"path": str(p.relative_to(sot_root)), "sha256": digest})
print(json.dumps(manifest))
PYEOF
  ARTIFACTS_JSON="$($VENV /tmp/ralph_manifest.py "${DAN_ROOT}" "${SOT_ROOT}")"

  # Read story's allowed_paths to scope the test run
  cat > /tmp/ralph_test_paths.py <<'PYEOF'
import json, sys
prd_file, story_id = sys.argv[1], sys.argv[2]
data = json.load(open(prd_file))
for s in data["userStories"]:
    if s["id"] == story_id:
        paths = [p for p in s.get("allowed_paths", [])
                 if p.startswith("experiments/") or p.startswith("helen_os/tests")]
        print(" ".join(paths) if paths else "experiments/")
        break
else:
    print("experiments/")
PYEOF
  TEST_PATHS="$($VENV /tmp/ralph_test_paths.py "${PRD_FILE}" "${STORY_ID}")"
  TEST_CMD_STR="pytest ${TEST_PATHS} -q --tb=no"

  # Run tests and capture result
  TEST_CMD="PYTHONPATH=${SOT_ROOT} ${VENV} -m ${TEST_CMD_STR} 2>&1"
  TEST_OUT="$(eval "${TEST_CMD}" | tail -5 || true)"
  PASSED="$(echo "${TEST_OUT}" | grep -oE '[0-9]+ passed' | grep -oE '[0-9]+' | head -1 || echo 0)"
  FAILED_CT="$(echo "${TEST_OUT}" | grep -oE '[0-9]+ failed' | grep -oE '[0-9]+' | head -1 || echo 0)"
  TOTAL="$(( ${PASSED:-0} + ${FAILED_CT:-0} ))"

  HAL_VERDICT="PASS"
  [[ "${CLOSE_OUTCOME}" == "FAILED" ]] && HAL_VERDICT="FAIL"

  # Failure type quoting
  FAILURE_FIELD="null"
  [[ "${CLOSE_FAILURE_TYPE}" != "null" ]] && FAILURE_FIELD="\"${CLOSE_FAILURE_TYPE}\""

  # Commit hash (if GREEN and committed)
  COMMIT_HASH="null"
  if [[ "${CLOSE_OUTCOME}" == "GREEN" ]]; then
    COMMIT_HASH="\"$(git -C "${SOT_ROOT}" rev-parse HEAD 2>/dev/null || echo 'none')\""
  fi

  # Write receipt via tmp script (avoids heredoc-in-subshell)
  cat > /tmp/ralph_write_receipt.py <<'PYEOF'
import sys, json, hashlib

story_id, epoch_id, outcome, failure_field, passed, failed_ct, total, \
    test_out, artifacts_json, commit_hash_val, receipt_file, timestamp, test_cmd_str = sys.argv[1:]

receipt = {
    "receipt_id": "",
    "story_id": story_id,
    "epoch": epoch_id,
    "actor": "DAN_GOBLIN",
    "authority": "NON_SOVEREIGN",
    "canon": "NO_SHIP",
    "status": outcome,
    "failure_type": None if failure_field == "null" else failure_field,
    "files_changed": [],
    "tests_run": {
        "passed": int(passed),
        "failed": int(failed_ct),
        "total": int(total),
        "command": test_cmd_str,
        "stdout_tail": test_out
    },
    "screenshots": [],
    "artifact_manifest": json.loads(artifacts_json),
    "commit_hash": None if commit_hash_val == "null" else commit_hash_val,
    "notes": "",
    "reducer_decision": None,
    "timestamp": timestamp
}
payload = {k: v for k, v in receipt.items() if k != "receipt_id"}
canon = json.dumps(payload, sort_keys=True, ensure_ascii=True)
receipt["receipt_id"] = hashlib.sha256(canon.encode()).hexdigest()[:16]
with open(receipt_file, "w") as f:
    json.dump(receipt, f, indent=2)
print(f"Receipt: {receipt_file}")
PYEOF
  $VENV /tmp/ralph_write_receipt.py \
    "${STORY_ID}" "${EPOCH_ID}" "${CLOSE_OUTCOME}" "${CLOSE_FAILURE_TYPE}" \
    "${PASSED:-0}" "${FAILED_CT:-0}" "${TOTAL}" \
    "${TEST_OUT}" "${ARTIFACTS_JSON}" "${COMMIT_HASH}" \
    "${RECEIPT_FILE}" "${TIMESTAMP}" "${TEST_CMD_STR}"

  # Update story status in prd.json
  NEW_STATUS="done"
  [[ "${CLOSE_OUTCOME}" == "FAILED" ]] && NEW_STATUS="todo"

  cat > /tmp/ralph_update_prd.py <<'PYEOF'
import sys, json
prd_file, story_id, new_status = sys.argv[1], sys.argv[2], sys.argv[3]
data = json.load(open(prd_file))
for s in data["userStories"]:
    if s["id"] == story_id:
        s["status"] = new_status
        s["epoch_owner"] = None
with open(prd_file, "w") as f:
    json.dump(data, f, indent=2)
print(f"Story {story_id} -> {new_status}")
PYEOF
  $VENV /tmp/ralph_update_prd.py "${PRD_FILE}" "${STORY_ID}" "${NEW_STATUS}"

  # Progress log
  echo "[${TIMESTAMP}] ${STORY_ID} ${CLOSE_OUTCOME} epoch=${EPOCH_ID} hal=${HAL_VERDICT}" \
    >> "${PROGRESS_FILE}"

  if [[ "${CLOSE_OUTCOME}" == "GREEN" ]]; then
    echo ""
    echo "GREEN — commit is authorised for allowed_paths only."
    echo "Run: git add <allowed_paths> && git commit -m 'feat(dan): ${STORY_ID} <title>'"
  else
    echo ""
    echo "FAILED — story reset to todo. No success commit."
    echo "Failure receipt: ${RECEIPT_FILE}"
    echo "Failure type: ${CLOSE_FAILURE_TYPE}"
  fi

  echo "=== RALPH CLOSE DONE ==="
  exit 0
fi

# ── preflight ─────────────────────────────────────────────────────────────────

echo "=== RALPH EPOCH START ==="
echo "SOT    : ${SOT_ROOT}"
echo "HEAD   : $(git -C "${SOT_ROOT}" rev-parse --short HEAD 2>/dev/null || echo 'none')"
echo "BRANCH : $(git -C "${SOT_ROOT}" rev-parse --abbrev-ref HEAD 2>/dev/null || echo 'none')"
echo "DIRTY  : $(git -C "${SOT_ROOT}" status --porcelain 2>/dev/null | wc -l | tr -d ' ') files"
echo "DRY    : ${DRY_RUN}"
echo ""

[[ ! -f "${PRD_FILE}" ]] && { echo "ERROR: prd.json not found at ${PRD_FILE}" >&2; exit 1; }

mkdir -p "${RECEIPTS_DIR}" "${SCRATCH_DIR}"

# ── story selection ───────────────────────────────────────────────────────────

if [[ -z "${STORY_ID}" ]]; then
  cat > /tmp/ralph_select_story.py <<'PYEOF'
import json, sys
data = json.load(open(sys.argv[1]))
todos = [s for s in data["userStories"] if s.get("status") == "todo"]
if not todos:
    print("NONE")
    sys.exit(0)
best = sorted(todos, key=lambda s: s["priority"])[0]
print(best["id"])
PYEOF
  STORY_ID="$($VENV /tmp/ralph_select_story.py "${PRD_FILE}")"
fi

if [[ "${STORY_ID}" == "NONE" || -z "${STORY_ID}" ]]; then
  echo "No todo stories in prd.json. All done or prd.json is empty."
  exit 0
fi

# Read story details
cat > /tmp/ralph_read_story.py <<'PYEOF'
import json, sys
data = json.load(open(sys.argv[1]))
for s in data["userStories"]:
    if s["id"] == sys.argv[2]:
        print(json.dumps(s, indent=2))
        break
PYEOF
STORY_JSON="$($VENV /tmp/ralph_read_story.py "${PRD_FILE}" "${STORY_ID}")"

STORY_TITLE="$(echo "${STORY_JSON}" | $VENV -c "import json,sys; print(json.load(sys.stdin)['title'])")"
ALLOWED="$(echo "${STORY_JSON}" | $VENV -c "import json,sys; print('\n  '.join(json.load(sys.stdin)['allowed_paths']))")"
CRITERIA="$(echo "${STORY_JSON}" | $VENV -c "import json,sys; d=json.load(sys.stdin); [print(f'  - {c}') for c in d['acceptanceCriteria']]")"

# ── epoch stamp ───────────────────────────────────────────────────────────────

TIMESTAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
SESSION_SALT="ralph-$$-${RANDOM}"
EPOCH_ID="$(echo -n "${STORY_ID}:${TIMESTAMP}:${SESSION_SALT}" | shasum -a 256 | cut -c1-12)"

echo "STORY  : ${STORY_ID} — ${STORY_TITLE}"
echo "EPOCH  : ${EPOCH_ID}"
echo "TIME   : ${TIMESTAMP}"
echo ""
echo "ALLOWED PATHS:"
echo "  ${ALLOWED}"
echo ""
echo "ACCEPTANCE CRITERIA:"
echo "${CRITERIA}"
echo ""

# ── mark in_progress ──────────────────────────────────────────────────────────

if [[ "${DRY_RUN}" == "false" ]]; then
  $VENV - <<PYEOF
import json
data = json.load(open("${PRD_FILE}"))
for s in data["userStories"]:
    if s["id"] == "${STORY_ID}":
        s["status"] = "in_progress"
        s["epoch_owner"] = "${EPOCH_ID}"
with open("${PRD_FILE}", "w") as f:
    json.dump(data, f, indent=2)
print(f"  marked ${STORY_ID} -> in_progress  epoch=${EPOCH_ID}")
PYEOF
fi

# ── DAN work phase ────────────────────────────────────────────────────────────

echo "=== DAN_GOBLIN WORK PHASE ==="
echo ""
echo "DAN_GOBLIN: implement story ${STORY_ID} within allowed_paths only."
echo "When done, close with:"
echo ""
echo "  ./scripts/ralph/ralph.sh --close ${STORY_ID} GREEN"
echo "  ./scripts/ralph/ralph.sh --close ${STORY_ID} FAILED <failure_type>"
echo ""
echo "Failure types: TEST_FAILURE | SCOPE_DRIFT | RECEIPT_MISSING |"
echo "               NONLOCAL_MUTATION | REPEATED_FAILURE |"
echo "               SCREENSHOT_MISSING | QUALITY_CHECK_FAILED"
echo ""
echo "=== RALPH WAITING FOR DAN ==="
