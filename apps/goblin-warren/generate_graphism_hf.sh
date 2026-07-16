#!/usr/bin/env bash
# generate_graphism_hf.sh — remix operator concept plates via Higgsfield
# authority=false · NON_SOVEREIGN · garden surface art only
set -euo pipefail
export PATH="${HOME}/.hermes/node/bin:${PATH}"
ROOT="$(cd "$(dirname "$0")" && pwd)"
OUT="$ROOT/assets/generated"
mkdir -p "$OUT"
REF="$ROOT/assets/districts"

if ! higgsfield account status >/dev/null 2>&1; then
  echo "Higgsfield not authenticated."
  echo "Run:  higgsfield auth login"
  echo "Then re-run this script."
  exit 2
fi

# Model: nano_banana_2 for character-faithful style transfer; gpt_image_2 for UI plates
run_plate() {
  local name="$1" image="$2" prompt="$3"
  echo "=== generating $name ==="
  higgsfield generate create nano_banana_2 \
    --prompt "$prompt" \
    --image "$image" \
    --aspect_ratio 16:9 \
    --wait --json | tee "$OUT/${name}.job.json"
}

COMMON="Goblin Warren game art, HELEN OS garden surface, painterly isometric fantasy UI, bioluminescent purple mushrooms, warm lantern gold, dark wood HUD, green goblin engineers with brass goggles, NON_SOVEREIGN aesthetic, no photoreal humans, cinematic game screenshot quality, consistent art direction"

run_plate sparkfall_depot_clean \
  "$REF/01_sparkfall_depot.png" \
  "$COMMON. Clean playable Sparkfall Depot district interior: tool bench, signal relay, power core, parts stockpile, dispatch board, goblin Ritchie bottom-left, flow integrity meter, no real brand logos."

run_plate warren_map_clean \
  "$REF/03_warren_map_clean.png" \
  "$COMMON. Clean world map with 8 districts on glowing stone path through night forest: Rootglow Grove, Sparkfall Depot, Mossbound Archive, Glowcap Market, Truth Foundry, Obsidian Observatory, Council Hall, Beyond the Bramble. Locked padlocks on later nodes. Readable English labels."

run_plate compost_garden_clean \
  "$REF/04_compost_garden.png" \
  "$COMMON. Compost Garden: discarded ideas become growth. Debunked theories, failed experiments, bad prompts piles, compost cycle center, extracts panel, goblin Lulu guide. Town trust meter."

run_plate eastern_blackout_clean \
  "$REF/05_eastern_quarter_blackout.png" \
  "$COMMON. Investigation scene Eastern Quarter Blackout: three goblins Ritchie Mica Puck argue at broken power core, rainy night market, investigation paths UI."

echo "Done. Inspect $OUT and promote chosen plates into assets/districts/."
