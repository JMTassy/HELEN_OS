#!/usr/bin/env bash
# Run the HELEN OS dashboard — kills port 7000 first, then starts Flask.
set -euo pipefail

SOT="$(git -C "$(dirname "$0")" rev-parse --show-toplevel)"
PORT=7000
VENV="$SOT/.venv/bin/python"
SERVER="$SOT/oracle_town/skills/ops/helen_dashboard/server.py"

# Kill anything on port
lsof -ti:$PORT | xargs kill -9 2>/dev/null || true
sleep 0.5

echo "HELEN OS Dashboard → http://localhost:$PORT"
echo "SOT: $SOT"
exec "$VENV" "$SERVER"
