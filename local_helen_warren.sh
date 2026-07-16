#!/bin/bash
# local_helen_warren.sh
# Start the Goblin Warren (LIVE-NPC) fully offline using local models.
# Assumes you have Ollama running with gemma2 or similar.

echo "=== HELEN LOCAL WARREN LAUNCHER ==="
echo "Make sure Ollama is running and you have pulled a model (e.g. ollama pull gemma2:9b)"

# 1. Start a tiny local API shim if you want (optional)
# For now we just serve the static game and tell you the Ollama endpoint.

echo ""
echo "Serving warren-town.html locally..."
echo "Open http://localhost:8123/warren-town.html in your browser"
echo ""
echo "In the game code, replace any cloud LLM calls with:"
echo "  http://localhost:11434/api/generate   (Ollama)"
echo "  model: gemma2:9b   (or your local Gemma4 equivalent)"
echo ""
echo "Press Ctrl+C to stop."

cd temple/gardens/goblin_garden_conquest
python3 -m http.server 8123
