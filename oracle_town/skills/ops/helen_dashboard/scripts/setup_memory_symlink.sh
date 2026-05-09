#!/usr/bin/env bash
# HELEN OS — set up oracle_town/memory as a symlink to a shared folder.
# Usage:
#   bash setup_memory_symlink.sh "/path/to/shared/HELEN/memory"
#
# Example (iCloud):
#   bash setup_memory_symlink.sh \
#     "$HOME/Library/Mobile Documents/com~apple~CloudDocs/HELEN/memory"
set -euo pipefail

SOT="$(git -C "$(dirname "$0")" rev-parse --show-toplevel)"
TARGET="${1:-}"

if [ -z "$TARGET" ]; then
  echo "Usage: $0 <shared-memory-folder-path>"
  echo ""
  echo "Examples:"
  echo "  iCloud:    $0 \"\$HOME/Library/Mobile Documents/com~apple~CloudDocs/HELEN/memory\""
  echo "  Syncthing: $0 \"\$HOME/Sync/HELEN/memory\""
  exit 1
fi

LINK="$SOT/oracle_town/memory"

echo ""
echo "HELEN OS — setup memory symlink"
echo "  target: $TARGET"
echo "  link:   $LINK"
echo ""

# ── Create target if missing ──────────────────────────────────────────────
if [ ! -d "$TARGET" ]; then
  echo "  Creating target folder…"
  mkdir -p "$TARGET"
  # Seed from template if template exists
  TMPL="$SOT/oracle_town/memory_template"
  if [ -d "$TMPL" ]; then
    cp "$TMPL/helen_identity.md"  "$TARGET/" 2>/dev/null || true
    cp "$TMPL/active_context.md"  "$TARGET/" 2>/dev/null || true
    touch "$TARGET/long_term_memory.jsonl"
    touch "$TARGET/sovereign_ledger.jsonl"
    echo "  Seeded from memory_template/"
  fi
fi

# ── Backup existing memory dir if not a symlink ───────────────────────────
if [ -d "$LINK" ] && [ ! -L "$LINK" ]; then
  BACKUP="${LINK}_backup_$(date +%Y%m%d_%H%M%S)"
  echo "  Backing up existing memory dir → $BACKUP"
  mv "$LINK" "$BACKUP"
fi

# ── Remove stale symlink ──────────────────────────────────────────────────
[ -L "$LINK" ] && rm "$LINK"

# ── Create symlink ────────────────────────────────────────────────────────
ln -s "$TARGET" "$LINK"

echo "  ✓ Symlink created: oracle_town/memory → $TARGET"
echo ""
ls -la "$LINK"/ 2>/dev/null | head -12 || true
echo ""
echo "  Done. HELEN memory is now shared from: $TARGET"
echo "  Run this script on every Mac to use the same memory."
echo ""
