#!/usr/bin/env python3
"""
helen_prettymaps — bounded wrapper for the external PrettyMaps library. CANDIDATE · authority=false.
NON-SOVEREIGN. Enforces the LICENSE GATE from SKILL.md: every figure is stamped with the mandatory
PrettyMaps + OpenStreetMap credit, and publish_status defaults to NO_PUBLISH (HELEN cannot credit yet).

NOT auto-run. Requires operator-gated `pip install prettymaps` (osmnx/matplotlib/shapely/vsketch).
The wrapper REFUSES to emit an un-stamped figure — the attribution is not optional.
"""
from __future__ import annotations
import json, os, sys, datetime

ATTRIBUTION = ("Map data (c) OpenStreetMap contributors - openstreetmap.org/copyright\n"
               "Rendered with PrettyMaps (c) marceloprates, AGPL-3.0")

def _slug(s: str) -> str:
    return "".join(c if c.isalnum() else "_" for c in s.lower())[:60]

def render(location, preset="minimal", out_dir="artifacts/maps", radius=1100):
    """Render one stylized map. Always stamps attribution. Always NO_PUBLISH. Returns the receipt dict."""
    try:
        import prettymaps            # external AGPL-3.0 tool; operator-installed only
        import matplotlib.pyplot as plt
    except ImportError:
        return {"error": "prettymaps not installed",
                "hint": "operator-gated: pip install prettymaps (heavy deps; AGPL-3.0). NOT auto-installed.",
                "publish_status": "NO_PUBLISH"}
    os.makedirs(out_dir, exist_ok=True)
    slug = _slug(str(location))
    plot = prettymaps.plot(location, preset=preset, radius=radius)   # osmnx network read
    ax = plot.ax
    # MANDATORY attribution stamp — never omitted (license gate). fail-closed if it cannot be drawn.
    ax.annotate(ATTRIBUTION, xy=(0.5, 0.005), xycoords="figure fraction",
                ha="center", va="bottom", fontsize=6, color="#444")
    png = os.path.join(out_dir, slug + ".png")
    plot.fig.savefig(png, dpi=200, bbox_inches="tight")
    plt.close(plot.fig)
    receipt = {"source_lib": "prettymaps", "source_license": "AGPL-3.0",
               "attribution_text": ATTRIBUTION, "attribution_present": True, "osm_credit": True,
               "publish_status": "NO_PUBLISH",           # HELEN cannot credit publicly yet (operator directive)
               "publish_allowed": False, "location": str(location), "preset": preset,
               "artifact": png, "generated_local_only": True, "authority": False,
               "stamped_at": datetime.datetime.now(datetime.timezone.utc).isoformat()}
    with open(os.path.join(out_dir, slug + ".receipt.json"), "w") as f:
        json.dump(receipt, f, indent=2)
    return receipt

if __name__ == "__main__":
    loc = sys.argv[1] if len(sys.argv) > 1 else "Calvi, France"
    r = render(loc, preset=sys.argv[2] if len(sys.argv) > 2 else "minimal")
    print(json.dumps(r, indent=2))
    print("\nLICENSE GATE: publish_status=NO_PUBLISH · attribution stamped · AGPL-3.0 · authority=false")
    print("A PrettyMaps/OSM-derived figure MUST carry the credit and stay LOCAL until HELEN's credit pipeline is wired.")
