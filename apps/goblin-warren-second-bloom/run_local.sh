#!/usr/bin/env bash
# Goblin Warren: Second Bloom — local run (ES modules need an http server).
cd "$(dirname "$0")"
echo "Goblin Warren: Second Bloom — Level 1: The Dying Fire"
echo "→ open http://localhost:8321"
echo "  (backtick \` toggles the dev inspector; ✨ button = reduced sensory mode)"
python3 -m http.server 8321
