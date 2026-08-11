"""design-memory -> WVIS -> SVG. The loop closed, once, end to end.

NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none.

    Composition (lineage-closed)          design_memory
        -> chiddush()  CANDIDATE_PROPOSED    lineage closure enforced
        -> WULVisualIR projection         wul_visual (a NOT representable)
        -> projection fidelity receipt    phi survives the crossing
        -> original SVG                   perception

The SVG is a RENDER. It carries no authority, and there is no path from
it back to the composition. Editing it green changes nothing upstream.

IP-SAFE, by construction. The ATF specimens contributed OPERATORS
(fill open/tint, scale, repeat, corner_resolve, tile_enclose) — cited,
witnessed in-frame. The FORM below is original: every path is computed
from parameters here, nothing is traced, sampled, or reproduced. This is
the difference the module exists to enforce:

    constrained recombination  !=  stylistic imitation

Deterministic: pure geometry from fixed parameters, no randomness.
"""
from __future__ import annotations

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
sys.path.insert(0, str(_HERE.parent / "wul_visual"))

import design_memory as dm                      # noqa: E402
import wul_visual_ir as wv                      # noqa: E402
from design_memory import (                     # noqa: E402
    Composition, Corpus, Operator, Primitive, apply_transform, chiddush,
)

INK = "#16130e"
CREAM = "#f4efe3"

# ── the witnessed operator set (cited to specimens delivered in-frame) ──
W_FILL = Operator("fill", (("mode", "open|tint"),),
                  source_ref="ATF specimen page: '18 POINT No 3 OPEN' vs "
                             "'18 POINT No 3 TINT' — one motif, two fills")
W_SCALE = Operator("scale", (("ratio", 1.5),),
                   source_ref="ATF: paired 18/24 POINT settings of one motif")
W_REPEAT = Operator("repeat", (("axis", "linear"), ("pitch", "even")),
                    source_ref="ATF: every border is an even linear repeat")
W_CORNER = Operator("corner_resolve", (("style", "L_tile"),),
                    source_ref="ATF: each border ships a matching L corner")
W_TILE = Operator("tile_enclose", (("shape", "square"),),
                  source_ref="ATF 'No 2405': starburst enclosed in square tile")

CORPUS = Corpus("ATF_border_specimens_in_frame", dm.AVAILABLE,
                operators=frozenset({"fill", "scale", "repeat",
                                     "corner_resolve", "tile_enclose"}),
                primitives=frozenset({"seed"}))


def build_composition() -> Composition:
    """The ORIGINAL artifact: a 'warren seed' primitive (mine) put through
    five WITNESSED operators (theirs). Novelty is the recombination."""
    seed = Primitive("warren-seed-v0", "seed")   # original form, not a specimen
    return Composition(
        artifact_id="helen-seed-border-v0",
        parts=(apply_transform(seed, W_FILL),
               apply_transform(seed, W_SCALE),
               apply_transform(seed, W_REPEAT),
               apply_transform(seed, W_CORNER),
               apply_transform(seed, W_TILE)),
        layout="rectangular_frame", spacing="even", color="mono",
        ornament="corner_L_tile")


# ── WVIS projection: provenance into IR that cannot carry authority ────

def project(comp: Composition) -> tuple:
    """Each part becomes a typed node. The PRIMITIVE is mine (HYPOTHESIS —
    original, unwitnessed); each OPERATOR is cited (OBSERVED); the
    COMPOSITION is a candidate (HYPOTHESIS). Edges from a cited operator
    are WITNESSED; the edge from my original primitive is CLAIMED —
    so the path to the artifact is honestly DISCONTINUOUS."""
    g = wv.VisualGraph("HELEN · Seed Border · lineage",
                       "operators witnessed · form original · A=0")
    g.add_node(wv.VisualNode("primitive", "SEED", "HYPOTHESIS",
                             "warren-seed-v0 (original form)", chi="root",
                             provenance_ref="composed in-frame"))
    for t in comp.parts:
        oid = f"op_{t.operator.op_id}"
        g.add_node(wv.VisualNode(oid, "WITNESS", "OBSERVED",
                                 t.operator.op_id, chi="throat",
                                 provenance_ref=t.operator.source_ref))
    g.add_node(wv.VisualNode("artifact", "CANDIDATE", "HYPOTHESIS",
                             comp.artifact_id, chi="heart",
                             provenance_ref="lineage-closed candidate"))
    g.add_edge("primitive", "artifact", "CLAIMED", "original form")
    for t in comp.parts:
        g.add_edge(f"op_{t.operator.op_id}", "artifact", "WITNESSED", "cited")
    return g, [(n, wv.projection_fidelity(node))
               for n, node in sorted(g.nodes.items())]


# ══ original geometry — every path computed, nothing traced ════════════

def seed_d(cx: float, cy: float, w: float, h: float) -> str:
    """A lens body with a punched eye (evenodd). Original construction:
    two quadratic arcs plus a circular counter."""
    top, bot = cy - h / 2, cy + h / 2
    # control offset is w (not w/2): a quadratic reaches HALF its control
    # offset at the midpoint, so the drawn lens is exactly w wide.
    lens = (f"M {cx:.2f},{top:.2f} "
            f"Q {cx + w:.2f},{cy:.2f} {cx:.2f},{bot:.2f} "
            f"Q {cx - w:.2f},{cy:.2f} {cx:.2f},{top:.2f} Z")
    r = w * 0.17
    ey = cy + h * 0.16
    eye = (f"M {cx - r:.2f},{ey:.2f} a {r:.2f},{r:.2f} 0 1,0 {2 * r:.2f},0 "
           f"a {r:.2f},{r:.2f} 0 1,0 {-2 * r:.2f},0 Z")
    return lens + " " + eye


def motif(cx, cy, w, h, rot, tint: bool) -> str:
    style = (f'fill="{INK}" fill-rule="evenodd"' if tint
             else f'fill="none" stroke="{INK}" stroke-width="1.5"')
    return (f'<g transform="rotate({rot} {cx:.2f} {cy:.2f})">'
            f'<path d="{seed_d(cx, cy, w, h)}" {style}/></g>')


def corner_tile(cx, cy, b, tint: bool) -> str:
    """corner_resolve + tile_enclose: motif at 45 deg inside a square rule."""
    half = b / 2 - 3
    sq = (f'<rect x="{cx - half:.2f}" y="{cy - half:.2f}" '
          f'width="{2 * half:.2f}" height="{2 * half:.2f}" fill="none" '
          f'stroke="{INK}" stroke-width="1.5"/>')
    return sq + motif(cx, cy, b * 0.30, b * 0.46, 45, tint)


def border(x, y, W, H, band, tint: bool) -> str:
    """repeat (even linear pitch) on four edges + corner_resolve tiles.
    Counts are DERIVED from the motif's along-edge extent so the repeat
    reads as a continuous band, the way a cast border does."""
    out = []
    mw, mh = band * 0.42, band * 0.64
    pitch = mw * 1.30                     # near-touching, like set type
    x0, x1 = x + band, x + W - band
    y0, y1 = y + band, y + H - band
    n_h = max(2, round((x1 - x0) / pitch))
    n_v = max(2, round((y1 - y0) / pitch))   # rotated: y-extent = mw
    for i in range(n_h):
        cx = x0 + (x1 - x0) * (i + 0.5) / n_h
        out.append(motif(cx, y + band / 2, mw, mh, 0, tint))
        out.append(motif(cx, y + H - band / 2, mw, mh, 180, tint))
    for j in range(n_v):
        cy = y0 + (y1 - y0) * (j + 0.5) / n_v
        out.append(motif(x + band / 2, cy, mw, mh, 90, tint))
        out.append(motif(x + W - band / 2, cy, mw, mh, -90, tint))
    for cx, cy in ((x + band / 2, y + band / 2), (x + W - band / 2, y + band / 2),
                   (x + band / 2, y + H - band / 2),
                   (x + W - band / 2, y + H - band / 2)):
        out.append(corner_tile(cx, cy, band, tint))
    return "".join(out)


def label(cx, y, text, size=13, weight="normal", op=1.0) -> str:
    return (f'<text x="{cx:.1f}" y="{y:.1f}" text-anchor="middle" '
            f'font-family="Georgia,serif" font-size="{size}" '
            f'font-weight="{weight}" fill="{INK}" opacity="{op}" '
            f'letter-spacing="1.6">{text}</text>')


def build_svg(comp: Composition, verdict: dict, fidelity: list) -> str:
    W, H = 1140, 700
    pw, ph, band = 450, 286, 46
    ax, bx, py = 60, 630, 122
    faithful = all(f["faithful"] for _n, f in fidelity)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}">',
        f'<title>HELEN seed border — original composition, witnessed operators</title>',
        f'<desc>Lineage-closed chiddush. Operators cited to ATF border '
        f'specimens observed in-frame; all geometry computed here. '
        f'authority=0, canon=false, ledger_effect=none.</desc>',
        f'<rect width="{W}" height="{H}" fill="{CREAM}"/>',
        label(W / 2, 56, "THE WARREN SEED BORDER", 22, "bold"),
        label(W / 2, 82, "one primitive · five witnessed operators · "
                         "two fills", 13, "normal", 0.75),
        f'<line x1="{W/2-150}" y1="96" x2="{W/2+150}" y2="96" '
        f'stroke="{INK}" stroke-width="0.8" opacity="0.5"/>',
    ]
    # the flagship witness, side by side: ONE motif, TWO fills
    parts.append(border(ax, py, pw, ph, band, tint=False))
    parts.append(border(bx, py, pw, ph, band, tint=True))
    parts.append(label(ax + pw / 2, py + ph + 34, "OPEN", 15, "bold"))
    parts.append(label(bx + pw / 2, py + ph + 34, "TINT", 15, "bold"))
    parts.append(label(ax + pw / 2, py + ph + 54,
                       "fill(mode=open) · scale · repeat · corner_resolve",
                       10.5, "normal", 0.65))
    parts.append(label(bx + pw / 2, py + ph + 54,
                       "fill(mode=tint) · scale · repeat · corner_resolve",
                       10.5, "normal", 0.65))
    # lineage receipt — provenance travels with the render
    ry = py + ph + 96
    parts.append(f'<line x1="60" y1="{ry-22}" x2="{W-60}" y2="{ry-22}" '
                 f'stroke="{INK}" stroke-width="0.8" opacity="0.45"/>')
    parts.append(label(W / 2, ry, "LINEAGE RECEIPT", 11.5, "bold", 0.8))
    rows = [
        f"verdict {verdict['verdict']} · lineage_closed "
        f"{verdict['artifact'].lineage_closed} · novelty "
        f"{verdict['artifact'].novelty_source}",
        "operators (witnessed, cited): fill · scale · repeat · "
        "corner_resolve · tile_enclose",
        "primitive: warren-seed-v0 — original form, composed in-frame, "
        "not a specimen",
        f"projection fidelity: {'phi preserved on every node' if faithful else 'BROKEN'}"
        f" · authority not representable in the IR",
    ]
    for i, row in enumerate(rows):
        parts.append(label(W / 2, ry + 22 + i * 17, row, 10.5, "normal", 0.72))
    parts.append(label(W / 2, H - 40,
                       "A = 0   ·   CANON = FALSE   ·   LEDGER_EFFECT = NONE"
                       "   ·   render carries no authority", 11, "bold", 0.85))
    parts.append("</svg>")
    return "".join(parts)


def main() -> int:
    comp = build_composition()
    verdict = chiddush(CORPUS, comp)          # lineage closure enforced first
    if verdict["verdict"] != "CANDIDATE_PROPOSED":
        print("REFUSED:", verdict)
        return 1
    graph, fidelity = project(comp)
    svg = build_svg(comp, verdict, fidelity)
    out = _HERE / "seed_border_v0.svg"
    out.write_text(svg, encoding="utf-8")

    print("chiddush      :", verdict["verdict"],
          "· lineage_closed:", verdict["artifact"].lineage_closed)
    print("fidelity      :", "all faithful" if all(f["faithful"] for _n, f in fidelity)
          else "BROKEN")
    print("path verdict  :", graph.path_verdict(["primitive", "artifact"]))
    print("svg           :", out, out.stat().st_size, "bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
