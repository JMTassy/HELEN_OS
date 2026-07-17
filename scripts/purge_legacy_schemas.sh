#!/usr/bin/env bash
# purge_legacy_schemas.sh — Seam 1 Schema Authority closure tool
#
# Safe-by-default: dry-run unless --execute is passed.
# Refuses to purge if bare SchemaRegistry() callers remain in helen_os/
# that would break without the legacy schemas/ directory.
#
# Usage:
#   bash scripts/purge_legacy_schemas.sh           # dry-run
#   bash scripts/purge_legacy_schemas.sh --execute # actually delete

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
LEGACY_DIR="$REPO_ROOT/schemas"
EXECUTE=false

for arg in "$@"; do
  [[ "$arg" == "--execute" ]] && EXECUTE=true
done

# Guard: check for bare SchemaRegistry() callers in helen_os/ that
# depend on the legacy path (schema_dir defaults to root schemas/).
echo "==> Checking for bare SchemaRegistry() callers in helen_os/..."
BARE_CALLERS=$(grep -rn "SchemaRegistry()" "$REPO_ROOT/helen_os/" \
  --include="*.py" \
  --exclude="*schema_registry.py" \
  --exclude="*test_schema_authority_guard.py" \
  -l 2>/dev/null || true)

if [[ -n "$BARE_CALLERS" ]]; then
  echo "BLOCKED: bare SchemaRegistry() callers found (would break without legacy schemas/):"
  echo "$BARE_CALLERS"
  echo "Fix these callers before purging."
  exit 1
fi
echo "    OK — no bare SchemaRegistry() callers found."

# List legacy JSON files
mapfile -t LEGACY_FILES < <(find "$LEGACY_DIR" -maxdepth 1 -name "*.json" 2>/dev/null)
if [[ ${#LEGACY_FILES[@]} -eq 0 ]] || [[ ! -f "${LEGACY_FILES[0]}" ]]; then
  echo "==> Legacy schemas/ is already empty. Nothing to purge."
  exit 0
fi

echo "==> Legacy JSON schemas to purge:"
for f in "${LEGACY_FILES[@]}"; do
  [[ -f "$f" ]] && echo "    $(basename "$f")"
done

if [[ "$EXECUTE" == "false" ]]; then
  echo ""
  echo "DRY-RUN complete. No files deleted."
  echo "Run with --execute to actually purge."
  exit 0
fi

echo ""
echo "==> EXECUTING purge..."
for f in "${LEGACY_FILES[@]}"; do
  if [[ -f "$f" ]]; then
    rm "$f"
    echo "    DELETED: $(basename "$f")"
  fi
done
echo "==> Done. Run make test to verify kernel gate passes."
