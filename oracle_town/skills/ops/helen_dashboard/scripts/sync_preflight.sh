#!/usr/bin/env bash
# HELEN OS — multi-device sync preflight.
# Run before starting work on any device.
# Warns if not in sync with origin, shows memory state.
set -euo pipefail

SOT="$(git -C "$(dirname "$0")" rev-parse --show-toplevel)"
cd "$SOT"

BOLD="\033[1m"
AMBER="\033[33m"
GREEN="\033[32m"
RED="\033[31m"
RESET="\033[0m"

echo ""
echo -e "${BOLD}HELEN OS — sync preflight${RESET}"
echo "SOT: $SOT"
echo ""

# ── Branch ────────────────────────────────────────────────────────────────
BRANCH="$(git rev-parse --abbrev-ref HEAD)"
HEAD="$(git rev-parse --short HEAD)"
echo -e "  branch   ${BOLD}${BRANCH}${RESET}  ${HEAD}"

# ── Working tree ──────────────────────────────────────────────────────────
STATUS="$(git status --short 2>/dev/null)"
if [ -z "$STATUS" ]; then
  echo -e "  tree     ${GREEN}clean${RESET}"
else
  echo -e "  tree     ${AMBER}DIRTY${RESET}"
  echo "$STATUS" | head -10 | sed 's/^/             /'
fi

# ── Origin drift ──────────────────────────────────────────────────────────
git fetch --quiet origin 2>/dev/null || true
AHEAD="$(git rev-list --count origin/${BRANCH}..HEAD 2>/dev/null || echo '?')"
BEHIND="$(git rev-list --count HEAD..origin/${BRANCH} 2>/dev/null || echo '?')"

if [ "$BEHIND" != "0" ] && [ "$BEHIND" != "?" ]; then
  echo -e "  origin   ${RED}BEHIND by ${BEHIND} commit(s)${RESET}"
  echo -e "           ${AMBER}→ Run: git pull --rebase${RESET}"
elif [ "$AHEAD" != "0" ]; then
  echo -e "  origin   ${AMBER}ahead by ${AHEAD} commit(s) (push when ready)${RESET}"
else
  echo -e "  origin   ${GREEN}in sync${RESET}"
fi

# ── Memory ────────────────────────────────────────────────────────────────
MEMORY_PATH="$SOT/oracle_town/memory"
echo ""
if [ -L "$MEMORY_PATH" ]; then
  TARGET="$(readlink "$MEMORY_PATH")"
  echo -e "  memory   ${GREEN}SYMLINK${RESET} → $TARGET"
  if [ -d "$TARGET" ]; then
    echo -e "           ${GREEN}target exists — shared memory active${RESET}"
  else
    echo -e "           ${RED}target MISSING — memory not accessible${RESET}"
  fi
elif [ -d "$MEMORY_PATH" ]; then
  echo -e "  memory   ${AMBER}LOCAL directory${RESET} (not shared across devices)"
  echo -e "           → To share: run scripts/setup_memory_symlink.sh"
else
  echo -e "  memory   ${RED}MISSING${RESET}"
  echo -e "           → To init: see oracle_town/memory_template/README.md"
fi

# ── Recommendation ────────────────────────────────────────────────────────
echo ""
if [ "$BEHIND" != "0" ] && [ "$BEHIND" != "?" ]; then
  echo -e "${RED}  ACTION REQUIRED: pull before working${RESET}"
  echo -e "  git pull --rebase"
elif [ -n "$STATUS" ]; then
  echo -e "${AMBER}  Working tree dirty — commit or stash before switching devices${RESET}"
else
  echo -e "${GREEN}  Ready to work.${RESET}"
fi
echo ""
