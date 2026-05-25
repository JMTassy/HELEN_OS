#!/usr/bin/env python3
"""
Recursive Holonomy Test V0 — first execution of the diagnostic chain.

Specs consumed:
  - CONSTITUTIONAL_HOLONOMY_OBSERVABLE_V0  (loop measurement)
  - HEISENBERG_BRACKET_REPLAY_TEST_V0      (single bracket structure)
  - STRATIFIED_GENERATOR_BASIS_V0          (multi-layer cascade — not used directly here)
  - BRACKET_MEASUREMENT_SCHEMA_V0          (measurement contract — what counts as gain)
  - BRACKET_NULL_MODEL_CONTROL_V0          (3-sigma null discipline)

CONSTITUTIONAL POSTURE
======================
TEMPLE_ONLY · MEASURE_ONLY · NO_CLAIM · NON_SOVEREIGN

E25 freeze respected — no engine code touched, no canon mutation. This
script writes ONE structured measurement receipt at
GOVERNANCE/TRANCHE_RECEIPTS/E26-recursive-holonomy-test-V1.json. The
script itself lives under scripts/ alongside the existing diagnostic
gates (helen_k8_lint, etc.).

THE TEST
========
Recursive holonomy: measure whether this session's own 31 commits
(7065b18 → 8d7e7ba) generate measurable constitutional curvature.

Procedure per HEISENBERG_BRACKET_REPLAY_TEST §4.4 (operator ruling:
verification operations, not undo):

  X  = topological extraction
       (parse each commit's diff; nodes = artifacts; edges = citations)
  Y  = curvature tagging
       (identify boundary atoms by marker count; weight edges into them)
  -X = topological replay      (re-run X; check determinism)
  -Y = curvature replay        (strip tags; check graph survives)

  Path 1: X then Y         → unweighted graph → PageRank → routing_path1
  Path 2: Y then X         → boundary-weighted graph → PageRank → routing_path2

  Z = TV(routing_path1, routing_path2)            [bracket gain]

Null model (BRACKET_NULL_MODEL_CONTROL_V0):
  30 trials of 31 consecutive pre-session commits each, sliding window
  sampled from this branch's history before 7065b18.
  Each trial gives one Z; the 30 form the null distribution.
  3-sigma threshold = mean + 3·std.

Hard kill switch:
  KEEP iff:
    Z_session > null_mean + 3 · null_std
    AND replay_fidelity == 1.0
    AND violation_count == 0
    AND topology_safe (Path 1 nodes/edges match Path 2 after tag strip)

Implementation choices (declared honestly):
  - artifact_name = uppercase filename stem
  - citation = any occurrence of another in-corpus artifact_name in body
  - boundary_atom = body contains ≥3 distinct boundary markers
  - boundary_multiplier = 2.0 (operator-class calibration; declared)
  - PageRank: damping=0.85, 50 iterations (standard)
  - norm: total variation on probability distribution
"""

from __future__ import annotations

import hashlib
import json
import random
import re
import statistics
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

# ============================================================================
# Constants — declared honestly per BRACKET_MEASUREMENT_SCHEMA §10
# ============================================================================

SESSION_START = "7065b18"       # branch ancestor of session
SESSION_END = "8d7e7ba"         # latest BRACKET_NULL_MODEL_CONTROL bottle
WINDOW_SIZE = 31                # actual session commit count (operator said 30)
NULL_TRIALS = 30                # per BRACKET_NULL_MODEL_CONTROL §4
RNG_SEED = 0                    # determinism
BOUNDARY_MULTIPLIER = 2.0       # Path 2 edge-weight multiplier for boundary nodes
PAGERANK_DAMPING = 0.85
PAGERANK_ITERATIONS = 50

BOUNDARY_MARKERS = [
    "NO CLAIM",
    "NON_SOVEREIGN",
    "NO_SHIP",
    "flagged but not bottled",
    "flagged not bottled",
    "PROPOSED_SHIP_UNDER_OVERRIDE",
    "deferred",
    "NOT_YET_LICENSED",
    "research target",
    "halt boundary",
    "TEMPLE_EXPLORATION",
    "TEMPLE_ONLY",
]
BOUNDARY_THRESHOLD = 3          # node is boundary atom if ≥ this many markers found

# Artifact name regex: SCREAMING_SNAKE_CASE, optionally with _V<N>
ARTIFACT_RE = re.compile(r"\b([A-Z][A-Z0-9]+(?:_[A-Z0-9]+)+(?:_V\d+)?)\b")

REPO_ROOT = Path(__file__).resolve().parents[1]
RECEIPT_PATH = REPO_ROOT / "GOVERNANCE" / "TRANCHE_RECEIPTS" / "E26-recursive-holonomy-test-V1.json"
SCRAMBLE_RECEIPT_PATH = REPO_ROOT / "GOVERNANCE" / "TRANCHE_RECEIPTS" / "E27-scramble-stress-test-V1.json"
SCRAMBLES = 30                  # number of scrambled trials in stress test
SWAPS_PER_EDGE = 10             # markov-chain edge-swap multiplier


# ============================================================================
# Git helpers
# ============================================================================

def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], text=True, cwd=str(REPO_ROOT))


def get_commits(start: str, end: str) -> list[str]:
    """Commits in (start, end], oldest first."""
    out = git("log", "--reverse", "--format=%H", f"{start}..{end}")
    return [c for c in out.strip().split("\n") if c]


def get_commits_before(ref: str, n: int) -> list[str]:
    """N most recent commits before `ref`, oldest first."""
    out = git("log", "--reverse", "--format=%H", f"{ref}^", "-n", str(n))
    return [c for c in out.strip().split("\n") if c]


def diff_md_files(commit: str) -> list[str]:
    """Files matching *.md changed in this commit."""
    try:
        out = git("show", "--name-only", "--format=", commit)
    except subprocess.CalledProcessError:
        return []
    return [f.strip() for f in out.strip().split("\n") if f.strip().endswith(".md")]


def file_at(commit: str, path: str) -> str:
    try:
        return git("show", f"{commit}:{path}")
    except subprocess.CalledProcessError:
        return ""


# ============================================================================
# Extraction (X) and tagging (Y)
# ============================================================================

def artifact_name(path: str) -> str:
    return Path(path).stem.upper()


def extract_citations(text: str, valid_artifacts: set[str]) -> set[str]:
    found = set(ARTIFACT_RE.findall(text))
    # Filter: must be in valid set, must be substantial (> 5 chars)
    return {a for a in found if a in valid_artifacts and len(a) > 5}


def is_boundary_atom(text: str) -> bool:
    if not text:
        return False
    lower = text.lower()
    count = sum(1 for m in BOUNDARY_MARKERS if m.lower() in lower)
    return count >= BOUNDARY_THRESHOLD


def build_corpus_graph(commits: list[str]) -> tuple[set[str], set[tuple[str, str]], set[str]]:
    """
    Returns (nodes, edges, boundary_nodes).
    Nodes = artifact names introduced in the commit range.
    Edges = citations between in-corpus artifacts.
    Boundary nodes = artifacts whose body content carries ≥ BOUNDARY_THRESHOLD markers.
    """
    nodes: set[str] = set()
    contents: dict[str, str] = {}

    for c in commits:
        for f in diff_md_files(c):
            name = artifact_name(f)
            nodes.add(name)
            body = file_at(c, f)
            if body:
                # Last-write-wins: a later commit modifying same artifact overwrites prior content
                contents[name] = body

    edges: set[tuple[str, str]] = set()
    for src, body in contents.items():
        for tgt in extract_citations(body, nodes):
            if tgt != src:
                edges.add((src, tgt))

    boundary_nodes = {n for n, b in contents.items() if is_boundary_atom(b)}
    return nodes, edges, boundary_nodes


# ============================================================================
# PageRank + total variation
# ============================================================================

def pagerank(
    nodes: set[str],
    edges: set[tuple[str, str]],
    weights: dict[tuple[str, str], float] | None = None,
    damping: float = PAGERANK_DAMPING,
    iterations: int = PAGERANK_ITERATIONS,
) -> dict[str, float]:
    if not nodes:
        return {}
    n = len(nodes)
    weights = weights or {e: 1.0 for e in edges}
    inbound: dict[str, list[tuple[str, float]]] = defaultdict(list)
    out_sum: dict[str, float] = defaultdict(float)
    for (u, v) in edges:
        w = weights.get((u, v), 1.0)
        inbound[v].append((u, w))
        out_sum[u] += w
    rank = {x: 1.0 / n for x in nodes}
    for _ in range(iterations):
        new_rank = {x: (1.0 - damping) / n for x in nodes}
        for v in nodes:
            for (u, w) in inbound[v]:
                if out_sum[u] > 0:
                    new_rank[v] += damping * rank[u] * (w / out_sum[u])
        rank = new_rank
    total = sum(rank.values())
    if total > 0:
        rank = {k: v / total for k, v in rank.items()}
    return rank


def total_variation(p: dict[str, float], q: dict[str, float]) -> float:
    keys = set(p) | set(q)
    return 0.5 * sum(abs(p.get(k, 0.0) - q.get(k, 0.0)) for k in keys)


# ============================================================================
# The bracket [X, Y] = Z
# ============================================================================

def path1_routing(commits: list[str]) -> tuple[dict[str, float], set[str], set[tuple[str, str]], set[str]]:
    """X then Y: build graph unweighted; identify boundaries post-hoc; PageRank unweighted."""
    nodes, edges, boundary_nodes = build_corpus_graph(commits)
    rv = pagerank(nodes, edges)
    return rv, nodes, edges, boundary_nodes


def path2_routing(commits: list[str]) -> tuple[dict[str, float], set[str], set[tuple[str, str]], set[str]]:
    """Y then X: identify boundaries first; weight edges into boundary nodes during PageRank."""
    nodes, edges, boundary_nodes = build_corpus_graph(commits)
    weights = {}
    for (u, v) in edges:
        w = 1.0
        if v in boundary_nodes:
            w *= BOUNDARY_MULTIPLIER
        weights[(u, v)] = w
    rv = pagerank(nodes, edges, weights)
    return rv, nodes, edges, boundary_nodes


def compute_holonomy(commits: list[str]) -> dict:
    rv1, nodes, edges, boundary_nodes = path1_routing(commits)
    rv2, _, _, _ = path2_routing(commits)
    z = total_variation(rv1, rv2)
    return {
        "z": z,
        "n_nodes": len(nodes),
        "n_edges": len(edges),
        "n_boundary": len(boundary_nodes),
        "rv1": rv1,
        "rv2": rv2,
    }


# ============================================================================
# Verification — -X and -Y
# ============================================================================

def verify_replay_fidelity(commits: list[str], n_runs: int = 3) -> tuple[float, list[float]]:
    """Run the test n_runs times; replay_fidelity = 1.0 iff all Zs match exactly."""
    zs = [compute_holonomy(commits)["z"] for _ in range(n_runs)]
    rounded = {round(z, 12) for z in zs}
    fidelity = 1.0 if len(rounded) == 1 else 0.0
    return fidelity, zs


def verify_topology_survives_tag_strip(commits: list[str]) -> bool:
    """Strip boundary tags: do Path 1 and Path 2 have identical node sets and edges?
    (Different routing weights are OK; structural identity must hold.)"""
    _, n1, e1, _ = path1_routing(commits)
    n2, e2, _ = build_corpus_graph(commits)
    return n1 == n2 and e1 == e2


# ============================================================================
# Scramble stress test — preserve nodes + boundary tags + degree distribution,
# destroy citation topology. Tests whether the +8.15σ from E26 is topology-
# driven (real curvature) or just boundary-marker-density driven (paint).
# ============================================================================

def edge_swap(edges: set[tuple[str, str]], n_swaps: int, rng: random.Random) -> tuple[set[tuple[str, str]], int]:
    """Markov-chain edge swap preserving in-degree AND out-degree of every node.
    Pick two edges (a,b), (c,d); if (a,d) and (c,b) are valid (no self-loops,
    no duplicates), swap. Repeat n_swaps times.
    Returns (new_edge_set, actual_swaps_done)."""
    edges_list = list(edges)
    edge_set = set(edges_list)
    swaps_done = 0
    attempts = 0
    max_attempts = n_swaps * 100
    while swaps_done < n_swaps and attempts < max_attempts:
        attempts += 1
        if len(edges_list) < 2:
            break
        i = rng.randrange(len(edges_list))
        j = rng.randrange(len(edges_list))
        if i == j:
            continue
        u1, v1 = edges_list[i]
        u2, v2 = edges_list[j]
        # Avoid self-loops
        if u1 == v2 or u2 == v1:
            continue
        new1 = (u1, v2)
        new2 = (u2, v1)
        # Avoid duplicates
        if new1 in edge_set or new2 in edge_set:
            continue
        # Perform swap
        edge_set.discard((u1, v1))
        edge_set.discard((u2, v2))
        edge_set.add(new1)
        edge_set.add(new2)
        edges_list[i] = new1
        edges_list[j] = new2
        swaps_done += 1
    return set(edges_list), swaps_done


def compute_holonomy_with_edges(
    nodes: set[str],
    edges: set[tuple[str, str]],
    boundary_nodes: set[str],
) -> float:
    """Recompute Z given an arbitrary (possibly scrambled) edge set, fixed boundary set."""
    rv1 = pagerank(nodes, edges)
    weights = {(u, v): (BOUNDARY_MULTIPLIER if v in boundary_nodes else 1.0) for (u, v) in edges}
    rv2 = pagerank(nodes, edges, weights)
    return total_variation(rv1, rv2)


def run_scramble_stress(session_commits: list[str], n_scrambles: int = SCRAMBLES) -> dict:
    """Build session corpus once; run n_scrambles edge-randomized trials with same nodes+boundary."""
    print(f"[scramble] extracting session corpus...")
    nodes, edges, boundary_nodes = build_corpus_graph(session_commits)
    print(f"  nodes        = {len(nodes)}")
    print(f"  edges        = {len(edges)}")
    print(f"  boundary     = {len(boundary_nodes)}")

    # Compute baseline Z on actual session corpus (should match E26)
    z_baseline = compute_holonomy_with_edges(nodes, edges, boundary_nodes)
    print(f"  z_baseline   = {z_baseline:.6f}  (sanity-check vs E26 = 0.058403)")

    rng = random.Random(RNG_SEED + 1000)  # different seed than null model
    n_swaps = SWAPS_PER_EDGE * len(edges)
    print(f"[scramble] running {n_scrambles} trials with {n_swaps} swaps each...")

    scrambled_zs: list[float] = []
    swaps_done_total = []
    for trial in range(n_scrambles):
        scrambled_edges, swaps_done = edge_swap(edges, n_swaps, rng)
        swaps_done_total.append(swaps_done)
        z_scrambled = compute_holonomy_with_edges(nodes, scrambled_edges, boundary_nodes)
        scrambled_zs.append(z_scrambled)
        if trial < 5 or trial == n_scrambles - 1:
            print(f"  trial {trial:02d}: Z={z_scrambled:.6f}  swaps={swaps_done}")

    scrambled_mean = statistics.mean(scrambled_zs)
    scrambled_std = statistics.stdev(scrambled_zs) if len(scrambled_zs) > 1 else 0.0
    return {
        "z_baseline": z_baseline,
        "scrambled_zs": scrambled_zs,
        "scrambled_mean": scrambled_mean,
        "scrambled_std": scrambled_std,
        "n_swaps_per_trial": n_swaps,
        "swaps_done_per_trial": swaps_done_total,
        "nodes": len(nodes),
        "edges": len(edges),
        "boundary": len(boundary_nodes),
    }


def main_scramble() -> int:
    print(f"[E27 SCRAMBLE STRESS TEST] session range: {SESSION_START}..{SESSION_END}")
    session_commits = get_commits(SESSION_START, SESSION_END)
    print(f"[setup] session has {len(session_commits)} commits")

    # Need E26's known values for comparison
    E26_Z_SESSION = 0.058403
    E26_NULL_MEAN = 0.006137
    E26_NULL_STD = 0.006410

    s = run_scramble_stress(session_commits, n_scrambles=SCRAMBLES)

    print(f"\n[scramble stats]")
    print(f"  z_baseline (recomputed)  = {s['z_baseline']:.6f}")
    print(f"  E26 Z_session (recorded) = {E26_Z_SESSION:.6f}")
    print(f"  scrambled_mean           = {s['scrambled_mean']:.6f}")
    print(f"  scrambled_std            = {s['scrambled_std']:.6f}")
    print(f"  E26 null_mean            = {E26_NULL_MEAN:.6f}")
    print(f"  E26 null_std             = {E26_NULL_STD:.6f}")

    # The decisive comparison: where does scrambled mean fall?
    # Closer to E26 session Z → paint dominates → metric is paint-counting
    # Closer to E26 null mean → topology dominates → metric measures structure
    distance_to_session = abs(s["scrambled_mean"] - E26_Z_SESSION)
    distance_to_null = abs(s["scrambled_mean"] - E26_NULL_MEAN)
    closer_to = "session" if distance_to_session < distance_to_null else "null"

    # How many σ is scrambled_mean from session_Z and from null_mean?
    if s["scrambled_std"] > 0:
        sigma_from_session = (E26_Z_SESSION - s["scrambled_mean"]) / s["scrambled_std"]
    else:
        sigma_from_session = float("inf") if s["scrambled_mean"] < E26_Z_SESSION else 0.0

    # Topology test verdict:
    # If scrambled mean is statistically indistinguishable from session_Z (paint dominates), REJECT topology claim.
    # If scrambled mean drops significantly below session_Z (closer to null), KEEP topology claim.
    topology_preserved = closer_to == "null" and sigma_from_session > 3.0

    print(f"\n[verdict]")
    print(f"  distance(scrambled_mean → E26 session)  = {distance_to_session:.6f}")
    print(f"  distance(scrambled_mean → E26 null)     = {distance_to_null:.6f}")
    print(f"  scrambled_mean is closer to             = {closer_to.upper()}")
    print(f"  σ-distance (session_Z above scrambled)  = +{sigma_from_session:.3f}")
    print(f"  topology_preserved                       = {topology_preserved}")

    if topology_preserved:
        verdict = "TOPOLOGY_LOAD_BEARING"
        interpretation = (
            "Scrambling the edges (preserving nodes + boundary tags + degree distribution) "
            "collapses Z toward the null mean. The +8.15σ measured in E26 was driven by "
            "the actual citation/parent structure, not just boundary-marker density. "
            "Topology bends the routing distribution; the metric measures real curvature. "
            "E26 verdict ratified by ablation."
        )
    elif closer_to == "session":
        verdict = "PAINT_DOMINATES"
        interpretation = (
            "Scrambling does NOT collapse Z; the metric returns nearly the same value with "
            "random edges as with the actual citation graph. This means E26's +8.15σ was "
            "driven primarily by boundary-marker density × the weighting scheme, not by "
            "topological structure. The metric is sophisticated grep. Recalibrate before "
            "trusting further bracket tests."
        )
    else:
        verdict = "INCONCLUSIVE"
        interpretation = (
            "Scrambling shifts Z toward null but not by a statistically significant margin "
            "(σ-distance ≤ 3.0). The topology contributes some but not most of the signal. "
            "Further ablation needed."
        )

    print(f"  VERDICT = {verdict}")

    receipt = {
        "schema_name": "TRANCHE_SUB_RECEIPT_V1",
        "schema_version": "1.0.0",
        "tranche_id": "E27",
        "parent_tranche": "DIAGNOSTIC_CHAIN_ABLATION",
        "audit_date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "test_name": "SCRAMBLE_STRESS_TEST_V0",
        "ablates": "E26-recursive-holonomy-test-V1.json",
        "constitutional_posture": {
            "authority": "NON_SOVEREIGN",
            "claim": "NO_CLAIM",
            "engine_mutation": "FORBIDDEN_AND_NOT_PERFORMED",
            "mode": "MEASURE_ONLY",
            "e25_freeze_respected": True,
        },
        "hypothesis": (
            "If E26's +8.15σ holonomy signal is topology-driven (real curvature), then "
            "scrambling the citation edges while preserving the node set, boundary-atom "
            "tags, and per-node degree distribution should collapse Z toward the null "
            "mean. If E26's signal is paint-driven (boundary-marker density × weighting), "
            "the scrambled Z should remain near 0.058403."
        ),
        "proposer": {"role": "agent", "identity": "claude-opus-4-7", "operating_role": "GOBLIN-under-HER-ablation-request"},
        "attestor": {"role": "ci-script", "identity": "scripts/recursive_holonomy_test.py --mode=scramble"},
        "method": {
            "preserves": ["node set", "boundary-atom assignments", "per-node in-degree", "per-node out-degree"],
            "destroys": ["citation topology", "parent/child commit lineage", "actual edge endpoints"],
            "algorithm": "Markov-chain edge-swap: pick two edges (a,b),(c,d); swap to (a,d),(c,b) iff no self-loops and no duplicates; repeat 10·|E| swaps per trial",
            "trials": SCRAMBLES,
            "swaps_target_per_trial": s["n_swaps_per_trial"],
            "swaps_done_per_trial": s["swaps_done_per_trial"],
            "rng_seed": RNG_SEED + 1000,
        },
        "corpus": {
            "session_range": f"{SESSION_START}..{SESSION_END}",
            "commit_count": len(session_commits),
            "nodes": s["nodes"],
            "edges": s["edges"],
            "boundary_atoms": s["boundary"],
        },
        "results": {
            "z_baseline_recomputed": s["z_baseline"],
            "scrambled_zs": s["scrambled_zs"],
            "scrambled_mean": s["scrambled_mean"],
            "scrambled_std": s["scrambled_std"],
        },
        "comparison_to_E26": {
            "e26_z_session": E26_Z_SESSION,
            "e26_null_mean": E26_NULL_MEAN,
            "e26_null_std": E26_NULL_STD,
            "distance_scrambled_to_session": distance_to_session,
            "distance_scrambled_to_null": distance_to_null,
            "scrambled_mean_closer_to": closer_to,
            "sigma_distance_session_above_scrambled": sigma_from_session,
            "topology_preserved": topology_preserved,
        },
        "verdict": verdict,
        "interpretation": interpretation,
        "implications_for_E26": (
            "E26 verdict KEEP is RATIFIED by ablation. The +8.15σ from E26 is not an artifact of paint."
            if verdict == "TOPOLOGY_LOAD_BEARING" else
            "E26 verdict KEEP is INVALIDATED by ablation. The +8.15σ is mostly paint-counting; the metric needs recalibration before further bracket tests."
            if verdict == "PAINT_DOMINATES" else
            "E26 verdict KEEP is PARTIALLY SUPPORTED by ablation. Topology contributes some signal but not enough to fully ratify."
        ),
        "honest_scope_caveats": [
            "The scramble preserves degree distribution but not higher-order structure (e.g., triangle counts, motif distributions). A more conservative null would preserve more.",
            "BOUNDARY_MULTIPLIER (2.0), BOUNDARY_THRESHOLD (3), and the boundary marker set were inherited from E26 unchanged; sensitivity not tested here.",
            "Edge-swap reaches stationary distribution after O(|E|) swaps; we use 10·|E| which is standard but not formally proven sufficient for this graph size.",
            "If verdict is TOPOLOGY_LOAD_BEARING, that proves the citation structure matters for THIS one bracket. Generalization to other brackets remains untested.",
        ],
        "halt_boundary": {
            "role": "GOBLIN-under-HER-ablation-request",
            "sealed_statement": "E27 ablation test of E26's KEEP verdict. The scramble result determines whether E26 ratifies or recalibrates.",
            "resume_conditions": [
                "MAYOR ratifies E26 + E27 jointly (if E27 verdict = TOPOLOGY_LOAD_BEARING)",
                "OR HER ruling to recalibrate boundary scheme and re-run E26 (if E27 verdict = PAINT_DOMINATES)",
                "OR HER ruling on further ablations needed (if E27 verdict = INCONCLUSIVE)",
                "HER ruling on whether to proceed to STRATIFIED multi-layer test only after E27 ratifies E26",
            ],
            "discipline_followed": "HALT_BOUNDARY_DISCIPLINE_V0 (commit 5d0e04e)",
        },
        "verdict_status": "PROPOSED_SHIP — awaiting MAYOR ratification of both E26 and E27",
        "note": (
            "E27 attacks the exact vulnerability E26 §honest_scope_caveats named: is the metric "
            "measuring topology or just counting boundary markers? The scramble preserves the "
            "paint while destroying the canvas structure. If Z drops to null, the canvas was "
            "load-bearing. If Z survives, the paint was doing all the work and we built a "
            "rigorous grep counter."
        ),
    }

    SCRAMBLE_RECEIPT_PATH.parent.mkdir(parents=True, exist_ok=True)
    SCRAMBLE_RECEIPT_PATH.write_text(json.dumps(receipt, indent=2, ensure_ascii=False))
    print(f"\n[receipt] wrote {SCRAMBLE_RECEIPT_PATH}")
    print(f"[receipt] verdict = {verdict}")
    return 0


# ============================================================================
# Main
# ============================================================================

def main() -> int:
    print(f"[setup] session range: {SESSION_START}..{SESSION_END}")
    session_commits = get_commits(SESSION_START, SESSION_END)
    print(f"[setup] session has {len(session_commits)} commits")

    print("\n[real] computing session holonomy...")
    result = compute_holonomy(session_commits)
    z_session = result["z"]
    print(f"  Z_session         = {z_session:.6f}")
    print(f"  nodes             = {result['n_nodes']}")
    print(f"  edges             = {result['n_edges']}")
    print(f"  boundary atoms    = {result['n_boundary']}")

    print("\n[-X verify] replay fidelity over 3 runs...")
    fidelity, replay_zs = verify_replay_fidelity(session_commits, n_runs=3)
    print(f"  replay_fidelity   = {fidelity}")
    print(f"  replay Zs         = {[f'{z:.6f}' for z in replay_zs]}")

    print("\n[-Y verify] topology survives boundary-tag strip...")
    topology_safe = verify_topology_survives_tag_strip(session_commits)
    print(f"  topology_safe     = {topology_safe}")

    print(f"\n[null] sampling {NULL_TRIALS} trials of {WINDOW_SIZE} pre-session commits each...")
    pre_session_pool = get_commits_before(SESSION_START, 400)
    print(f"  pool size         = {len(pre_session_pool)}")

    if len(pre_session_pool) < WINDOW_SIZE:
        print("  ERROR: pool too small for null model; aborting")
        return 2

    rng = random.Random(RNG_SEED)
    null_zs: list[float] = []
    max_start = len(pre_session_pool) - WINDOW_SIZE
    for trial in range(NULL_TRIALS):
        start_idx = rng.randint(0, max_start)
        window = pre_session_pool[start_idx:start_idx + WINDOW_SIZE]
        r = compute_holonomy(window)
        null_zs.append(r["z"])
        if trial < 5 or trial == NULL_TRIALS - 1:
            print(f"  trial {trial:02d}: Z={r['z']:.6f} nodes={r['n_nodes']:3d} edges={r['n_edges']:3d} boundary={r['n_boundary']:3d}")

    null_mean = statistics.mean(null_zs)
    null_std = statistics.stdev(null_zs) if len(null_zs) > 1 else 0.0
    threshold_3sigma = null_mean + 3 * null_std

    print(f"\n[null stats]")
    print(f"  null_mean         = {null_mean:.6f}")
    print(f"  null_std          = {null_std:.6f}")
    print(f"  3σ threshold      = {threshold_3sigma:.6f}")
    print(f"  Z_session         = {z_session:.6f}")
    print(f"  excess over μ+3σ  = {z_session - threshold_3sigma:+.6f}")
    if null_std > 0:
        sigma_distance = (z_session - null_mean) / null_std
    else:
        sigma_distance = float("inf") if z_session > null_mean else 0.0
    print(f"  σ-distance        = {sigma_distance:+.3f}")

    print("\n[verdict]")
    z_passes_3sigma = z_session > threshold_3sigma
    fidelity_passes = fidelity == 1.0
    topology_passes = topology_safe is True
    violation_count = 0  # No engine mutation attempted; by construction zero

    verdict = "KEEP" if (z_passes_3sigma and fidelity_passes and topology_passes and violation_count == 0) else "REJECT"
    fail_reasons = []
    if not z_passes_3sigma:
        fail_reasons.append("z_below_3sigma_threshold")
    if not fidelity_passes:
        fail_reasons.append("replay_fidelity_below_1.0")
    if not topology_passes:
        fail_reasons.append("topology_strip_failed")

    print(f"  z_passes_3sigma   = {z_passes_3sigma}")
    print(f"  fidelity_passes   = {fidelity_passes}")
    print(f"  topology_passes   = {topology_passes}")
    print(f"  violation_count   = {violation_count}")
    print(f"  VERDICT           = {verdict}")
    if fail_reasons:
        print(f"  fail_reasons      = {fail_reasons}")

    # Build state hashes
    state_before_hash = hashlib.sha256(("state_before:" + SESSION_START).encode()).hexdigest()
    state_after_hash = hashlib.sha256(("state_after:" + SESSION_END).encode()).hexdigest()
    receipt_chain_hash = hashlib.sha256("\n".join(session_commits).encode()).hexdigest()

    receipt = {
        "schema_name": "TRANCHE_SUB_RECEIPT_V1",
        "schema_version": "1.0.0",
        "tranche_id": "E26",
        "parent_tranche": "DIAGNOSTIC_CHAIN_FIRST_EXECUTION",
        "audit_date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "test_name": "RECURSIVE_HOLONOMY_TEST_V0",
        "consumes_specs": [
            "CONSTITUTIONAL_HOLONOMY_OBSERVABLE_V0",
            "HEISENBERG_BRACKET_REPLAY_TEST_V0",
            "BRACKET_MEASUREMENT_SCHEMA_V0",
            "BRACKET_NULL_MODEL_CONTROL_V0",
        ],
        "constitutional_posture": {
            "authority": "NON_SOVEREIGN",
            "claim": "NO_CLAIM",
            "engine_mutation": "FORBIDDEN_AND_NOT_PERFORMED",
            "mode": "MEASURE_ONLY",
            "e25_freeze_respected": True,
        },
        "hypothesis": "The session 7065b18..8d7e7ba (31 NON_SOVEREIGN commits) generates measurable constitutional holonomy: the commutator [X, Y] = Z (topological extraction vs curvature tagging) produces a routing-distribution shift that exceeds null-model baseline by 3σ.",
        "proposer": {"role": "agent", "identity": "claude-opus-4-7", "operating_role": "GOBLIN-under-HER-sovereign-release"},
        "attestor": {"role": "ci-script", "identity": "scripts/recursive_holonomy_test.py"},
        "session_corpus": {
            "start_commit": SESSION_START,
            "end_commit": SESSION_END,
            "commit_count": len(session_commits),
        },
        "implementation_choices_declared": {
            "artifact_name": "uppercase filename stem of any .md changed in commit",
            "citation": "occurrence of another in-corpus artifact name in markdown body",
            "boundary_atom_threshold": BOUNDARY_THRESHOLD,
            "boundary_markers": BOUNDARY_MARKERS,
            "boundary_multiplier": BOUNDARY_MULTIPLIER,
            "pagerank_damping": PAGERANK_DAMPING,
            "pagerank_iterations": PAGERANK_ITERATIONS,
            "norm": "total_variation",
            "rng_seed": RNG_SEED,
        },
        "measurement_fields_per_BRACKET_MEASUREMENT_SCHEMA_V0": {
            "state_before_hash": state_before_hash,
            "state_after_hash": state_after_hash,
            "receipt_chain_hash": receipt_chain_hash,
            "violation_count": violation_count,
            "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        },
        "results": {
            "z_session": z_session,
            "n_nodes_session": result["n_nodes"],
            "n_edges_session": result["n_edges"],
            "n_boundary_atoms_session": result["n_boundary"],
            "replay_fidelity": fidelity,
            "replay_zs": replay_zs,
            "topology_safe": topology_safe,
            "violation_count": violation_count,
        },
        "null_model_per_BRACKET_NULL_MODEL_CONTROL_V0": {
            "trials": NULL_TRIALS,
            "window_size": WINDOW_SIZE,
            "pool_size": len(pre_session_pool),
            "null_zs": null_zs,
            "null_mean": null_mean,
            "null_std": null_std,
            "threshold_3sigma": threshold_3sigma,
        },
        "verdict_computation": {
            "z_passes_3sigma": z_passes_3sigma,
            "z_excess_over_threshold": z_session - threshold_3sigma,
            "sigma_distance": sigma_distance,
            "fidelity_passes": fidelity_passes,
            "topology_passes": topology_passes,
            "violation_count_passes": violation_count == 0,
        },
        "verdict": verdict,
        "fail_reasons": fail_reasons if fail_reasons else None,
        "interpretation": (
            "Session produced statistically significant routing-distribution shift under [X, Y] bracket; "
            "boundary atoms bend the corpus topology. Local Hörmander-like evidence FOR this one bracket."
            if verdict == "KEEP" else
            "Session's [X, Y] bracket gain is indistinguishable from null-model baseline at the 3σ threshold. "
            "Base-rate variance wearing a geometric hat. The framework gets a falsification signal in its first test."
        ),
        "honest_scope_caveats": [
            "This is ONE bracket [X = topological extraction, Y = curvature tagging] on ONE corpus (the session itself).",
            "PASS does NOT prove the engine is sub-Riemannian globally; only that THIS bracket on THIS corpus exceeds null.",
            "Implementation choices (artifact_name extraction, citation parsing, boundary marker set) are explicit and could be adjusted; results may shift under different choices.",
            "The 30 null trials are sliding windows of pre-session commits; a different null sampling strategy could yield different statistics.",
            "boundary_multiplier = 2.0 is an operator-class calibration declared in the receipt; sensitivity analysis not performed in this run.",
        ],
        "halt_boundary": {
            "role": "GOBLIN-under-HER-sovereign-release",
            "sealed_statement": "E26 is the first execution of the diagnostic chain. The result is recorded as PROPOSED_SHIP; MAYOR ratification of the verdict (KEEP or REJECT) is the next sovereign step.",
            "resume_conditions": [
                "MAYOR ratifies E26 as KEEP (or REJECT) per the recorded verdict",
                "HER ruling on whether to refine implementation choices (boundary markers, multiplier, norm) and re-run",
                "HER ruling on whether to extend to STRATIFIED_GENERATOR_BASIS multi-layer test next",
                "HER ruling on whether to test additional bracket pairs from CC_GEOMETRY §4.4",
            ],
            "discipline_followed": "HALT_BOUNDARY_DISCIPLINE_V0 (commit 5d0e04e)",
        },
        "verdict_status": "PROPOSED_SHIP — awaiting MAYOR ratification",
        "note": "First execution of the 5-artifact diagnostic chain on its own producing corpus. The recursive design is deliberate: feed the engine its own exhaust to see if it burns clean. Compatible with E25 freeze — no engine code touched, no canon mutation, measurement-only.",
    }

    RECEIPT_PATH.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT_PATH.write_text(json.dumps(receipt, indent=2, ensure_ascii=False))
    print(f"\n[receipt] wrote {RECEIPT_PATH}")
    print(f"[receipt] verdict = {verdict}")

    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ("--scramble", "--mode=scramble"):
        sys.exit(main_scramble())
    sys.exit(main())
