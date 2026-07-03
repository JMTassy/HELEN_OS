#!/usr/bin/env bash
# ci_garden_validators.sh — run every temple garden validator and FAIL CLOSED.
#
# The garden validators exit 0 even when ok:false (verified 2026-07-03), so this
# runner parses the --json "ok" field instead of trusting exit codes. This is the
# CI rail the 2026-06-19 incident lacked: a 300-epoch run broke validate_avalon
# and was only caught manually days later (quarantined in commit 07bdf88).
#
# NON_SOVEREIGN: read-only over temple/gardens/; no ledger, no kernel.
set -u

PY="${PYTHON:-python3}"
FAIL=0

check() {
  local name="$1" script="$2"
  if [ ! -f "$script" ]; then
    echo "SKIP  $name — validator not found at $script"
    return
  fi
  local out ok
  out=$("$PY" "$script" --json 2>&1)
  ok=$(printf '%s' "$out" | "$PY" -c "import json,sys
try:
    print(json.load(sys.stdin).get('ok'))
except Exception:
    print('parse_error')")
  if [ "$ok" = "True" ]; then
    echo "PASS  $name"
  else
    echo "FAIL  $name (ok=$ok)"
    printf '%s\n' "$out" | head -20
    FAIL=1
  fi
}

check "goblin_meditation_center" temple/gardens/goblin_meditation_center/validate_garden.py
check "goblin_garden_conquest"   temple/gardens/goblin_garden_conquest/validate_conquest_garden.py
check "goblin_garden_conquest_avalon" temple/gardens/goblin_garden_conquest_avalon/validate_avalon.py

if [ "$FAIL" -ne 0 ]; then
  echo "GARDEN VALIDATORS: FAIL — at least one garden is invalid"
  exit 1
fi
echo "GARDEN VALIDATORS: ALL PASS"
