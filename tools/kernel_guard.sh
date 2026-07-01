#!/usr/bin/env bash
# tools/kernel_guard.sh
#
# CI enforcement: the ledger may only be written by kernel_cli.ml
# (or its Python shim: tools/ndjson_writer.py).
#
# This script fails if ANY other file opens a .ndjson or ledger path
# for appending or writing.
#
# Rules enforced:
#   RULE 1: Only ALLOWED_WRITERS may call open(..., "a") or open(..., "w")
#            on NDJSON/ledger files.
#   RULE 2: No file may import NDJSONWriter except ALLOWED_WRITERS.
#   RULE 3: No file may directly write json.dumps(...) + "\n" to a
#            file path matching *ledger*, *events* or *.ndjson*.
#
# Allowed writers (single source of truth):
#   tools/ndjson_writer.py    — Python kernel boundary
#   kernel/kernel_cli.ml      — OCaml kernel boundary
#   tools/end_session.py      — Session seal writer (uses NDJSONWriter)
#
# CONSUMER_ALLOWLIST entries (RULE 2) require an inline citation to the
# authorization document(s) that license the NDJSONWriter import. Two
# tiers:
#   DOCTRINE/AUDIT tier — production import; cites a protocol/spec/audit
#     doc that names the importing file and the handler(s) it backs.
#   CONTRACT-TEST tier  — test import; cites tmp_path-only isolation.
#     Test-tier entries confer NO production-writer authority; a test
#     file allowlisted here still may not open real ledger paths (see
#     RULE 1) or bypass CI schema checks.
# See: KERNEL_GUARD_ALLOWLIST_RECONCILE_V1 (proposal, authority=false).
#
# Usage:
#   bash tools/kernel_guard.sh           # exits 0 if clean, 1 if violation
#   bash tools/kernel_guard.sh --verbose # prints all checked files
#
# CI integration (.github/workflows/kernel_guard.yml):
#   - name: Kernel guard
#     run: bash tools/kernel_guard.sh

set -euo pipefail

REPO_ROOT="$(git -C "$(dirname "$0")" rev-parse --show-toplevel 2>/dev/null \
              || echo "$(dirname "$(dirname "$(realpath "$0")")")")"

VERBOSE=0
[[ "${1:-}" == "--verbose" ]] && VERBOSE=1

# -----------------------------------------------------------------------
# Allowed writers: files that are PERMITTED to write to the ledger.
# All other files are checked for violations.
# -----------------------------------------------------------------------
ALLOWED_WRITERS=(
  "tools/ndjson_writer.py"
  "kernel/kernel_cli.ml"
  "tools/end_session.py"
  "tools/helen_add_lesson.py"
  "tools/accept_payload_meta.sh"
)

VIOLATIONS=0
CHECKED=0

log() { [[ $VERBOSE -eq 1 ]] && echo "  [CHECK] $1" || true; }

# -----------------------------------------------------------------------
# Build the allowed-writer pattern for grep exclusion
# -----------------------------------------------------------------------
EXCLUDE_PATTERN=""
for writer in "${ALLOWED_WRITERS[@]}"; do
  EXCLUDE_PATTERN="${EXCLUDE_PATTERN}${REPO_ROOT}/${writer}"$'\n'
done

# -----------------------------------------------------------------------
# RULE 1: No direct open(..., "a") or open(..., "w") on ledger paths
#         in any Python file outside allowed writers.
# -----------------------------------------------------------------------
echo "RULE 1: Checking for direct ledger open() calls..."

while IFS= read -r -d '' pyfile; do
  # Skip allowed writers
  IS_ALLOWED=0
  for writer in "${ALLOWED_WRITERS[@]}"; do
    if [[ "$pyfile" == "${REPO_ROOT}/${writer}" ]]; then
      IS_ALLOWED=1; break
    fi
  done
  [[ $IS_ALLOWED -eq 1 ]] && log "ALLOWED: ${pyfile#$REPO_ROOT/}" && continue

  log "${pyfile#$REPO_ROOT/}"
  CHECKED=$((CHECKED + 1))

  # Check for direct open() with append/write mode on .ndjson files only.
  # .json files are configuration; .ndjson is the append-only ledger format.
  # Narrows to ledger-related path names to avoid false positives.
  if grep -n 'open(' "$pyfile" 2>/dev/null | \
     grep -iE '\.ndjson' | \
     grep -E '"a"|"w"|"a\+"|"w\+"' | \
     grep -qiE '(ledger|events|wisdom|dialogue|town)'; then
    echo "  [VIOLATION] RULE 1: ${pyfile#$REPO_ROOT/}"
    grep -n 'open(' "$pyfile" 2>/dev/null | \
      grep -iE '\.ndjson' | \
      grep -E '"a"|"w"|"a\+"|"w\+"' | \
      grep -iE '(ledger|events|wisdom|dialogue|town)' | \
      while IFS= read -r line; do echo "    $line"; done
    VIOLATIONS=$((VIOLATIONS + 1))
  fi
done < <(find "$REPO_ROOT" -name "*.py" -not -path "*/\.*" \
              -not -path "*/__pycache__/*" -print0)

echo "  Checked $CHECKED Python files, RULE 1 done."

# -----------------------------------------------------------------------
# RULE 2: NDJSONWriter import only from allowed consumers
# -----------------------------------------------------------------------
echo ""
echo "RULE 2: Checking NDJSONWriter import origins..."

CONSUMER_ALLOWLIST=(
  "tools/ndjson_writer.py"            # DOCTRINE: the writer itself
  "tools/end_session.py"              # DOCTRINE: session seal writer
  "tools/helen_add_lesson.py"         # DOCTRINE: lesson writer
  "tools/test_kernel_properties.py"   # CONTRACT-TEST: tmp_path only
  "tools/test_meta_invariance.py"     # CONTRACT-TEST: tmp_path only
  "tools/accept_payload_meta.sh"      # DOCTRINE: payload-meta acceptor
  "tools/validate_hash_chain.py"      # DOCTRINE: hash-chain validator
  "tools/validate_turn_schema.py"     # DOCTRINE: turn-schema validator
  # DOCTRINE: promote_skill path per MAYOR_HANDLER_PROMOTE_SKILL_SPEC_V1.md
  #   (oracle_town/protocols/, "The NDJSONWriter must be imported", §10
  #   "This is the only path that writes to town/ledger_v1.ndjson") and
  #   SOVEREIGN_PROMOTION_PROTOCOL_V1.md ("One writer only ... called by
  #   the kernel daemon on behalf of MAYOR"); ALSO covers seq_correction
  #   path per FIREWALL_BYPASS_AUDIT_8911FD0.md (oracle_town/audits/).
  #   Any additional _handle_* writer path added to that file requires
  #   its own fresh authorization citation appended here — file-level
  #   allowlisting does not auto-extend to new handlers.
  "oracle_town/kernel/kernel_daemon.py"
  # CONTRACT-TEST: verified tmp_path-only, no real-ledger contact.
  # Allowlisting here does NOT authorize production writes.
  "helen_os/tests/test_ndjson_writer_atomic.py"
  "helen_os/tests/test_duplicate_seq_detector.py"
)

while IFS= read -r -d '' pyfile; do
  IS_ALLOWED=0
  for writer in "${CONSUMER_ALLOWLIST[@]}"; do
    if [[ "$pyfile" == "${REPO_ROOT}/${writer}" ]]; then
      IS_ALLOWED=1; break
    fi
  done
  [[ $IS_ALLOWED -eq 1 ]] && continue

  if grep -qE 'from tools\.ndjson_writer import|import ndjson_writer' \
       "$pyfile" 2>/dev/null; then
    echo "  [VIOLATION] RULE 2: Unapproved NDJSONWriter import: ${pyfile#$REPO_ROOT/}"
    VIOLATIONS=$((VIOLATIONS + 1))
  fi
done < <(find "$REPO_ROOT" -name "*.py" -not -path "*/\.*" \
              -not -path "*/__pycache__/*" -print0)

echo "  RULE 2 done."

# -----------------------------------------------------------------------
# RULE 3: No shell scripts writing raw JSON to ledger paths
#         (except allowed writers)
# -----------------------------------------------------------------------
echo ""
echo "RULE 3: Checking shell scripts for raw ledger writes..."

while IFS= read -r -d '' shfile; do
  IS_ALLOWED=0
  for writer in "${ALLOWED_WRITERS[@]}"; do
    if [[ "$shfile" == "${REPO_ROOT}/${writer}" ]]; then
      IS_ALLOWED=1; break
    fi
  done
  [[ $IS_ALLOWED -eq 1 ]] && continue

  # Check for echo/printf >> *.ndjson patterns
  if grep -nE '(echo|printf).+>>.+\.(ndjson|jsonl)' "$shfile" 2>/dev/null | \
     grep -qiE '(ledger|events|wisdom|dialogue)'; then
    echo "  [VIOLATION] RULE 3: ${shfile#$REPO_ROOT/}"
    VIOLATIONS=$((VIOLATIONS + 1))
  fi
done < <(find "$REPO_ROOT" -name "*.sh" -not -path "*/\.*" -print0)

echo "  RULE 3 done."

# -----------------------------------------------------------------------
# Summary
# -----------------------------------------------------------------------
echo ""
echo "============================================================"
if [[ $VIOLATIONS -eq 0 ]]; then
  echo "  [PASS] kernel_guard: $VIOLATIONS violations found."
  echo "  All ledger writes route through the kernel boundary."
else
  echo "  [FAIL] kernel_guard: $VIOLATIONS violation(s) found."
  echo "  Direct ledger writes bypass the kernel. Fix before merge."
fi
echo "============================================================"

exit $([[ $VIOLATIONS -eq 0 ]] && echo 0 || echo 1)
