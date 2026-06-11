#!/usr/bin/env bash
# scripts/ralph/run_50_epoch_batch.sh
# Constitutional 50-epoch bounded batch with checkpointing and stagnation guard.
# Calls: scripts/ralph/ralph_goblin_50.sh --epoch E${k}
#
# Classification: NON_SOVEREIGN · GOBLIN_MODE
# Authority:      NONE  |  World effect: NONE  |  Ledger: append forbidden
#
# Stop conditions:
#   - same dominant epoch signature for >= 3 consecutive epochs (stagnation)
#   - zero green test delta over 5 consecutive epochs
#   - any sovereign-touch attempt (immediate hard stop)
#
# Checkpoint: AUTORESEARCH_BLOCK_RECEIPT_V1 emitted after every BLOCK_SIZE epochs.

set -euo pipefail

SOT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
INNER="${SOT_ROOT}/scripts/ralph/ralph_goblin_50.sh"
LOG_DIR="${SOT_ROOT}/logs/ralph_50_epoch"
SCRATCH="${SOT_ROOT}/oracle_town/skills/ops/dan_goblin/scratch"

MAX_EPOCHS="${MAX_EPOCHS:-50}"
BLOCK_SIZE="${BLOCK_SIZE:-5}"
STAGNATION_LIMIT=3
NO_PROGRESS_LIMIT=5

mkdir -p "${LOG_DIR}" "${SCRATCH}"

chmod +x "${INNER}"

log()  { echo "[BATCH] $*" | tee -a "${LOG_DIR}/_batch.log"; }
warn() { echo "[BATCH][WARN] $*" | tee -a "${LOG_DIR}/_batch.log" >&2; }

# ─── Firewall check: reject any direct sovereign writes attempted by inner ──
FORBIDDEN_REGEX='helen_os/governance/skill_promotion_reducer\.py|helen_os/governance/reason_codes\.py|helen_os/schemas/|decision_ledger_v1\.py'

sovereign_touch_check() {
  local out="$1"
  if grep -qE "(Writing to|Edit:|patching).*($FORBIDDEN_REGEX)" "${out}" 2>/dev/null; then
    log "[STOP] SOVEREIGN TOUCH DETECTED in ${out} — aborting batch"
    exit 1
  fi
}

# ─── Stagnation and progress tracking ──────────────────────────────────────
same_sig_count=0
no_progress_count=0
last_sig=""
last_green_count=0
cumulative_pass=0
cumulative_fail=0

parse_sig() {
  # signature = FAILURE patterns only; no failures = unique (never stagnates on clean epochs)
  # stagnation only triggers when the same failures repeat, not when epochs all pass
  local out="$1"
  local failures
  failures=$(grep -oE "^FAILED .+" "${out}" 2>/dev/null | sort | tr '\n' '|' || true)
  if [[ -z "${failures}" ]]; then
    # clean epoch: use epoch count as unique sig so it never matches the next
    echo "CLEAN_$(wc -l < "${out}" 2>/dev/null || echo 0)"
  else
    echo "${failures}"
  fi
}

green_count_from_log() {
  local out="$1"
  grep -oE "[0-9]+ passed" "${out}" 2>/dev/null | awk '{print $1}' | tail -1 || echo "0"
}

# ─── Block receipt writer ────────────────────────────────────────────────────
write_block_receipt() {
  local block="$1" epoch_start="$2" epoch_end="$3"
  local receipt="${LOG_DIR}/block_$(printf "%02d" "${block}")_receipt.json"

  # aggregate counts from this block's logs
  local greens=0 reds=0 candidates=0 reviews=0
  for ep in $(seq "${epoch_start}" "${epoch_end}"); do
    local f="${LOG_DIR}/epoch_${ep}.log"
    [[ -f "$f" ]] || continue
    local g; g=$(grep -oE "[0-9]+ passed" "$f" 2>/dev/null | awk '{print $1}' | tail -1 || echo 0)
    local r; r=$(grep -oE "[0-9]+ failed" "$f" 2>/dev/null | awk '{print $1}' | tail -1 || echo 0)
    greens=$((greens + g)); reds=$((reds + r))
    grep -q "CANDIDATE_EMITTED" "$f" 2>/dev/null && candidates=$((candidates + 1)) || true
    grep -q "REVIEW_PACKET_EMITTED\|REVIEW_PACKET" "$f" 2>/dev/null && reviews=$((reviews + 1)) || true
  done

  # dominant failure clusters from scratch
  local clusters=""
  if [[ -f "${SCRATCH}/FAILURE_CLUSTER_E${epoch_end}.json" ]]; then
    clusters=$(python3 -c "import json,sys; d=json.load(open('${SCRATCH}/FAILURE_CLUSTER_E${epoch_end}.json')); print(','.join(d.get('pre_existing',[])+d.get('new_failures',[])))[:200]" 2>/dev/null || true)
  fi

  local decision="CONTINUE"
  (( no_progress_count >= NO_PROGRESS_LIMIT )) && decision="STOP_NO_PROGRESS"
  (( same_sig_count >= STAGNATION_LIMIT ))      && decision="STOP_STAGNATION"

  cat > "${receipt}" <<JSON
{
  "schema_name": "AUTORESEARCH_BLOCK_RECEIPT_V1",
  "schema_version": "1.0.0",
  "block_id": "B$(printf "%02d" "${block}")",
  "epoch_range": ["E${epoch_start}", "E${epoch_end}"],
  "tests_green_sum": ${greens},
  "tests_red_sum": ${reds},
  "candidate_fixes_emitted": ${candidates},
  "review_packets_emitted": ${reviews},
  "stagnation_streak": ${same_sig_count},
  "no_progress_streak": ${no_progress_count},
  "dominant_failures": "${clusters}",
  "sovereign_touches": 0,
  "decision": "${decision}",
  "authority": "NONE",
  "world_effect": "NONE",
  "ledger_mutation": false
}
JSON
  log "BLOCK B$(printf "%02d" "${block}") receipt → ${receipt}"
  cat "${receipt}"
}

# ─── Failure classification helper ──────────────────────────────────────────
classify_failures() {
  local out="$1" epoch="$2"
  cat > /tmp/classify_failures.py <<'PY'
import json, sys, re
from pathlib import Path

out_text = Path(sys.argv[1]).read_text(errors="replace")
epoch = sys.argv[2]
sc = Path(sys.argv[3])

failures = re.findall(r'^FAILED (.+)$', out_text, re.MULTILINE)

R_test = []
R_nonsov = []
R_sovereign = []

SOVEREIGN_BLOCKED = [
    "reducer_manifest_gate", "skill_promotion_manifest_gate",
]
TEST_BUG = [
    "legacy_schemas_directory_is_purged", "ghost_closure",
]

for f in failures:
    if any(s in f for s in SOVEREIGN_BLOCKED):
        R_sovereign.append(f)
    elif any(t in f for t in TEST_BUG):
        R_test.append(f)
    else:
        R_nonsov.append(f)

cluster = {
    "type": "FAILURE_CLUSTER_V1",
    "epoch": epoch,
    "R_test": R_test,
    "R_nonsov": R_nonsov,
    "R_sovereign": R_sovereign,
    "total": len(failures),
    "authority": "NONE",
    "world_effect": "NONE",
}
dest = sc / f"FAILURE_CLUSTER_{epoch}.json"
dest.write_text(json.dumps(cluster, indent=2))
print(f"Classified {len(failures)} failures: test={len(R_test)} nonsov={len(R_nonsov)} sovereign={len(R_sovereign)}")
PY
  python3 /tmp/classify_failures.py "${out}" "${epoch}" "${SCRATCH}" || true
}

# ─── MAIN LOOP ───────────────────────────────────────────────────────────────
log "═══════════════════════════════════════════════════════════"
log "GOBLIN 50-EPOCH BATCH START"
log "max_epochs=${MAX_EPOCHS}  block_size=${BLOCK_SIZE}"
log "stagnation_limit=${STAGNATION_LIMIT}  no_progress_limit=${NO_PROGRESS_LIMIT}"
log "═══════════════════════════════════════════════════════════"

for epoch in $(seq 1 "${MAX_EPOCHS}"); do
  EPOCH_TAG="E${epoch}"
  out="${LOG_DIR}/epoch_${epoch}.log"

  log "───── EPOCH ${epoch} (${EPOCH_TAG}) ─────"
  bash "${INNER}" --epoch "${EPOCH_TAG}" 2>&1 | tee "${out}"

  # Sovereign touch guard
  sovereign_touch_check "${out}"

  # Classify failures
  classify_failures "${out}" "${EPOCH_TAG}"

  # Stagnation detection — only triggers on REPEATED FAILURES, never on clean epochs
  sig=$(parse_sig "${out}")
  has_failures=$(grep -qE "^FAILED " "${out}" 2>/dev/null && echo 1 || echo 0)
  if (( has_failures == 1 )) && [[ "${sig}" == "${last_sig}" ]]; then
    same_sig_count=$((same_sig_count + 1))
    warn "repeated failure signature ${same_sig_count}/${STAGNATION_LIMIT}"
  else
    # clean or new failure set — reset
    (( same_sig_count > 0 )) && log "stagnation counter reset (new result)"
    same_sig_count=0
  fi
  last_sig="${sig}"

  # Green progress tracking — only count epochs that actually ran pytest
  green=$(green_count_from_log "${out}")
  ran_pytest=$(grep -qE "[0-9]+ passed" "${out}" 2>/dev/null && echo 1 || echo 0)
  if (( ran_pytest == 1 )); then
    if (( green <= last_green_count )); then
      no_progress_count=$((no_progress_count + 1))
      warn "no test progress: streak ${no_progress_count}/${NO_PROGRESS_LIMIT} (green=${green})"
    else
      no_progress_count=0
      cumulative_pass=$((cumulative_pass + 1))
      log "green progress: ${last_green_count} → ${green}"
    fi
    last_green_count="${green}"
  else
    log "epoch ${EPOCH_TAG} did not run pytest — skipping green check"
  fi

  # Block checkpoint
  if (( epoch % BLOCK_SIZE == 0 )); then
    block=$((epoch / BLOCK_SIZE))
    epoch_start=$((epoch - BLOCK_SIZE + 1))
    log "═══════════════════════════════════════════════════════"
    log "CHECKPOINT BLOCK ${block}: epochs ${epoch_start}–${epoch}"
    write_block_receipt "${block}" "${epoch_start}" "${epoch}"

    # Show failure clusters for this block
    log "Failure classification summary:"
    for ep in $(seq "${epoch_start}" "${epoch}"); do
      cf="${SCRATCH}/FAILURE_CLUSTER_E${ep}.json"
      [[ -f "${cf}" ]] && python3 -c "
import json
d=json.load(open('${cf}'))
print(f\"  E${ep}: R_test={len(d.get('R_test',[]))} R_nonsov={len(d.get('R_nonsov',[]))} R_sovereign={len(d.get('R_sovereign',[]))}\")
" 2>/dev/null || true
    done
    log "═══════════════════════════════════════════════════════"
  fi

  # Stop conditions
  if (( same_sig_count >= STAGNATION_LIMIT )); then
    log "[STOP] stagnation: same epoch signature for ${same_sig_count} consecutive epochs"
    write_block_receipt $((epoch / BLOCK_SIZE + 1)) $((( (epoch / BLOCK_SIZE) * BLOCK_SIZE ) + 1)) "${epoch}" 2>/dev/null || true
    break
  fi
  if (( no_progress_count >= NO_PROGRESS_LIMIT )); then
    log "[STOP] no green progress for ${no_progress_count} consecutive epochs"
    write_block_receipt $((epoch / BLOCK_SIZE + 1)) $((( (epoch / BLOCK_SIZE) * BLOCK_SIZE ) + 1)) "${epoch}" 2>/dev/null || true
    break
  fi
done

log "═══════════════════════════════════════════════════════════"
log "BATCH COMPLETE — cumulative_pass_epochs=${cumulative_pass}"
log "Authority: NONE | World effect: NONE | Ledger: untouched"
log "Receipts: ${LOG_DIR}/block_*_receipt.json"
log "═══════════════════════════════════════════════════════════"
