"""BEAD-TEMPLE-CONSERVED-FORM-001 — conserved-form compiler.

Compiles a source phrase into the canonical object S = (M, N, C, G, R, P)
and three projections (2D trace, minimal voxel, rhythm), each fingerprinted.

Constitutional posture: NON_SOVEREIGN sandbox. Output is a TEMPLE replay
packet, not a kernel receipt. authority=false, ledger_effect=none,
claim_status=LOCAL_OBSERVATION.

Determinism (K-tau mu_DETERMINISM): no wall-clock, no randomness, no
environment reads. Same input + same mapping = byte-identical packet.
"""

import hashlib
import json

BEAD_ID = "BEAD-TEMPLE-CONSERVED-FORM-001"

# MAPPING_V1 — declared modern interpretation, not a historical claim.
# 25-letter grid, J merged into I (classical Polybius-style merge).
MAPPING_ID = "MAPPING_V1"
ALPHABET = "ABCDEFGHIKLMNOPQRSTUVWXYZ"
GRID_SIZE = 5
ZERO_STEP_INTERVAL = 1  # repeated letter: declared interval, not silence


def canon(obj):
    """Canonical JSON bytes — the only admissible hashing surface."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256(obj):
    return hashlib.sha256(canon(obj)).hexdigest()


def normalize(message):
    """M -> N. Every lossy step is logged as an ambiguity, never silent."""
    symbols = []
    ambiguities = []
    for i, ch in enumerate(message):
        up = ch.upper()
        if up == "J":
            ambiguities.append({"index": i, "char": ch, "rule": "J_MERGED_TO_I"})
            up = "I"
        if up in ALPHABET:
            symbols.append(up)
        else:
            ambiguities.append({"index": i, "char": ch, "rule": "DROPPED_NON_ALPHABET"})
    return symbols, ambiguities


def coordinates(symbols):
    """N -> C. Letter -> (row, col) on the 5x5 grid."""
    coords = []
    for s in symbols:
        idx = ALPHABET.index(s)
        coords.append([idx // GRID_SIZE, idx % GRID_SIZE])
    return coords


def build_graph(symbols, coords):
    """C -> G. Nodes = occupied cells; edges = consecutive steps in order."""
    nodes = {}
    for s, (row, col) in zip(symbols, coords):
        nodes[s] = [row, col]
    path_edges = []
    for i in range(1, len(symbols)):
        path_edges.append([symbols[i - 1], symbols[i]])
    return {
        "nodes": [{"symbol": s, "cell": nodes[s]} for s in sorted(nodes)],
        "path": path_edges,
    }


def trace2d(coords):
    """Visual projection: the traversal as an ordered polyline of points."""
    return {"points": [[c[1], c[0]] for c in coords]}  # [x, y] drawing order


def ascii_trace(symbols, coords):
    """Operator-readable render of the trace: visit order per cell."""
    grid = [["." for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    for order, (row, col) in enumerate(coords):
        mark = symbols[order]
        grid[row][col] = mark if grid[row][col] == "." else grid[row][col]
    return "\n".join(" ".join(row) for row in grid)


def voxels(coords):
    """Voxel projection: [col, row, layer]; revisited cells stack upward.

    The voxel is a spatial debugger — a revisit is visible as height, so a
    divergence in traversal order shows as a displaced layer.
    """
    visits = {}
    out = []
    for row, col in coords:
        key = (row, col)
        layer = visits.get(key, 0)
        visits[key] = layer + 1
        out.append([col, row, layer])
    return out


def rhythm(coords):
    """Rhythmic projection: a humanly reproducible checksum.

    Interval between onsets = Chebyshev distance of the grid step (a longer
    jump takes longer). Accent marks a row change. Zero-distance steps
    (repeated letter) get the declared ZERO_STEP_INTERVAL.
    """
    events = []
    onset = 0
    for i, (row, col) in enumerate(coords):
        if i == 0:
            interval = 0
            accent = True
        else:
            prev_row, prev_col = coords[i - 1]
            dist = max(abs(row - prev_row), abs(col - prev_col))
            interval = dist if dist > 0 else ZERO_STEP_INTERVAL
            accent = row != prev_row
        onset += interval
        events.append({"index": i, "onset": onset, "interval": interval, "accent": accent})
    return events


def cross_links(symbols, coords, voxs, rhythm_events):
    """One record per symbol occurrence, binding all three projections.

    A click on symbol i must light exactly these targets.
    """
    links = []
    for i, s in enumerate(symbols):
        links.append(
            {
                "index": i,
                "symbol": s,
                "point": [coords[i][1], coords[i][0]],
                "voxel": voxs[i],
                "rhythm_onset": rhythm_events[i]["onset"],
            }
        )
    return links


def compile_bead(message, bead_id=BEAD_ID):
    """Full pipeline: source -> replay packet (dict, deterministic)."""
    symbols, ambiguities = normalize(message)
    coords = coordinates(symbols)
    graph = build_graph(symbols, coords)
    trace = trace2d(coords)
    voxs = voxels(coords)
    rhythm_events = rhythm(coords)
    links = cross_links(symbols, coords, voxs, rhythm_events)

    projections = {
        "normalized": symbols,
        "coordinates": coords,
        "graph": graph,
        "trace2d": trace,
        "voxel": voxs,
        "rhythm": rhythm_events,
        "cross_links": links,
    }
    fingerprints = {name: sha256(value) for name, value in projections.items()}

    packet = {
        "packet_type": "TEMPLE_REPLAY_PACKET_V0",
        "bead_id": bead_id,
        "mapping": {
            "id": MAPPING_ID,
            "alphabet": ALPHABET,
            "grid_size": GRID_SIZE,
            "zero_step_interval": ZERO_STEP_INTERVAL,
            "declared_as": "modern interpretation, not historical claim",
        },
        "source": {"text": message, "sha256": hashlib.sha256(message.encode("utf-8")).hexdigest()},
        "ambiguities": ambiguities,
        "projections": projections,
        "ascii_trace": ascii_trace(symbols, coords),
        "fingerprints": fingerprints,
        "authority": False,
        "canon": False,
        "ledger_effect": "none",
        "claim_status": "LOCAL_OBSERVATION",
    }
    packet["packet_hash"] = sha256(packet)
    return packet


def first_divergence(seq_a, seq_b):
    """Index of the first differing element, or None if one is a prefix."""
    for i, (a, b) in enumerate(zip(seq_a, seq_b)):
        if a != b:
            return i
    return None if len(seq_a) == len(seq_b) else min(len(seq_a), len(seq_b))


if __name__ == "__main__":
    import os
    import sys

    source = sys.argv[1] if len(sys.argv) > 1 else "SHAPE IS SOUND"
    result = compile_bead(source)
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "renders")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, result["bead_id"] + ".replay.json")
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, sort_keys=True)
        fh.write("\n")
    print("packet:", out_path)
    print("packet_hash:", result["packet_hash"])
    print(result["ascii_trace"])
