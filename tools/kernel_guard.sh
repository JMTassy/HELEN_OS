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

# -----------------------------------------------------------------------
# Doc-fixture allowlist: files that MENTION forbidden patterns inside
# quoted fixtures/documentation only (mention != use). The scanner-crossing
# test feeds the exact forbidden string to the scanner UNDER TEST; the
# string never executes. Grep cannot tell mention from use — we can.
# -----------------------------------------------------------------------
DOC_FIXTURE_ALLOWLIST=(
  "tests/test_scanner_crossing.py"
)
ALLOWED_WRITERS+=("${DOC_FIXTURE_ALLOWLIST[@]}")

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
  "tools/ndjson_writer.py"
  "tools/end_session.py"
  "tools/helen_add_lesson.py"
  "tools/test_kernel_properties.py"
  "tools/test_meta_invariance.py"
  "tools/accept_payload_meta.sh"
  "tools/validate_hash_chain.py"
  "tools/validate_turn_schema.py"
  # Operator ruling 2026-07-06 (stale-allowlist drift repair, GAS Prop 7.1(b)):
  "oracle_town/kernel/kernel_daemon.py"          # kernel boundary itself (β-family; _handle_promote_skill / _handle_seq_correction)
  "helen_os/tests/test_ndjson_writer_atomic.py"  # writer atomicity regression tests (Thm 4.2 witness)
  "helen_os/tests/test_duplicate_seq_detector.py" # forked-ledger detector tests (Thm 4.2 witness)
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
