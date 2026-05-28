#!/usr/bin/env python3
"""
receipt_graph.py

Read-only receipt graph viewer.

Reads GOVERNANCE/GEMMA_PROPOSALS/, groups receipts by topic cluster
(via hal_receipt_analyzer.tokenize + jaccard), and renders:

  default:    ASCII graph to stdout
  --dot PATH: Graphviz DOT file to PATH

Nodes: receipt (timestamp, topic short, envelope, operator, HAL)
Edges:
  - chronological chain within topic cluster
  - shared required_receipt signature
  - shared HAL question theme

Hard constraints:
  - NEVER write to receipt files
  - NEVER write to town/ledger_v1.ndjson
  - NEVER mutate lifecycle_entry
  - Only write path is --dot PATH (a derived artifact file).
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

# Sibling import: hal_receipt_analyzer.py lives next to this file.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from hal_receipt_analyzer import (  # noqa: E402
    DEFAULT_PROPOSAL_DIR,
    TOPIC_CLUSTER_JACCARD,
    extract_topic,
    get_status,
    jaccard,
    load_receipts,
    normalize_item,
    split_numbered_items,
    tokenize,
)


def short_time(ts: str | None) -> str:
    if not ts:
        return "??:??"
    try:
        return ts.split("T")[1][:5]
    except (IndexError, AttributeError):
        return "??:??"


def short_topic(topic: str, max_len: int = 14) -> str:
    if not topic:
        return "(no topic)"
    words = re.findall(r"[A-Za-z][A-Za-z0-9-]+", topic)
    if not words:
        return topic[:max_len]
    longest = max(words, key=len)
    return longest[:max_len]


def short_status(s: str) -> str:
    table = {
        "(none)": "none",
        "PENDING_REVIEW": "PENDING",
        "APPROVED_FOR_SANDBOX_ONLY": "APPR_SBX",
        "REJECTED": "REJECT",
        "NEEDS_MORE_RECEIPTS": "NEEDS_MORE",
        "PASS": "PASS",
        "FAIL": "FAIL",
    }
    return table.get(s, s)


def cluster_receipts(receipts):
    """Group receipts by topic-cluster. Returns (clusters, untyped).

    clusters: list of (keywords_set, [(path, receipt, topic), ...]) sorted by ts.
    untyped:  list of (path, receipt) with no extractable topic.
    """
    typed = []
    untyped = []
    for path, r in receipts:
        topic = extract_topic(r)
        if topic:
            typed.append((path, r, topic, tokenize(topic)))
        else:
            untyped.append((path, r))

    clusters: list[tuple[set, list[tuple[Path, dict, str]]]] = []
    for path, r, topic, toks in typed:
        for keywords, members in clusters:
            if jaccard(keywords, toks) >= TOPIC_CLUSTER_JACCARD:
                members.append((path, r, topic))
                keywords.update(toks)
                break
        else:
            clusters.append((set(toks), [(path, r, topic)]))

    for _, members in clusters:
        members.sort(key=lambda m: m[1].get("receipt_timestamp_utc", ""))
    untyped.sort(key=lambda m: m[1].get("receipt_timestamp_utc", ""))
    return clusters, untyped


def _node_line(receipt: dict, topic: str) -> str:
    t = short_time(receipt.get("receipt_timestamp_utc"))
    short = short_topic(topic)
    env = "YES" if receipt.get("envelope_complete") else "NO"
    op = short_status(get_status(receipt.get("operator_decision")))
    hal = short_status(get_status(receipt.get("hal_verdict")))
    return f"[{t} {short}] envelope={env}  op={op}  hal={hal}"


def render_ascii(receipts) -> str:
    clusters, untyped = cluster_receipts(receipts)
    lines: list[str] = []
    lines.append(
        f"=== RECEIPT GRAPH ({len(receipts)} receipt(s), "
        f"{len(clusters)} cluster(s)) ==="
    )
    lines.append("")

    for keywords, members in clusters:
        for i, (_, r, topic) in enumerate(members):
            lines.append(_node_line(r, topic))
            if i < len(members) - 1:
                lines.append("   |")
        lines.append("")

    if untyped:
        lines.append("--- untopic'd receipts ---")
        for _, r in untyped:
            lines.append(_node_line(r, ""))
        lines.append("")

    # Cross-cluster edges summary (text only -- DOT shows them visually).
    shared_req = _shared_signatures(receipts, "required_receipts")
    shared_q = _shared_signatures(receipts, "hal_questions")
    if shared_req or shared_q:
        lines.append("--- cross-cluster edges ---")
        if shared_req:
            lines.append(
                f"shared required_receipt signatures: {len(shared_req)} "
                "(visualize with --dot)"
            )
        if shared_q:
            lines.append(
                f"shared HAL question signatures: {len(shared_q)} "
                "(visualize with --dot)"
            )

    return "\n".join(lines)


def _shared_signatures(receipts, field: str) -> dict[str, list[Path]]:
    """For each normalized item signature in `field`, list the receipts that
    contain it. Returns only signatures appearing in 2+ receipts."""
    bucket: dict[str, list[Path]] = defaultdict(list)
    for path, r in receipts:
        for item in split_numbered_items(r.get(field)):
            sig = normalize_item(item)
            if sig:
                bucket[sig].append(path)
    return {sig: paths for sig, paths in bucket.items() if len(paths) >= 2}


def _dot_escape(s: str) -> str:
    return (
        s.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\n", "\\n")
    )


def _dot_node_label(receipt: dict, topic: str) -> str:
    t = short_time(receipt.get("receipt_timestamp_utc"))
    short = short_topic(topic) if topic else "(no topic)"
    env = "YES" if receipt.get("envelope_complete") else "NO"
    op = short_status(get_status(receipt.get("operator_decision")))
    hal = short_status(get_status(receipt.get("hal_verdict")))
    return _dot_escape(f"{t}  {short}\nenv={env}  op={op}\nhal={hal}")


def render_dot(receipts) -> str:
    clusters, untyped = cluster_receipts(receipts)
    node_id: dict[Path, str] = {}
    for i, (path, _) in enumerate(receipts):
        node_id[path] = f"r{i}"

    lines: list[str] = []
    lines.append("digraph receipt_graph {")
    lines.append("  rankdir=TB;")
    lines.append('  node [shape=box, fontname="monospace", style="filled,rounded"];')
    lines.append("")

    def emit_node(path: Path, receipt: dict, topic: str) -> None:
        label = _dot_node_label(receipt, topic)
        color = "lightgreen" if receipt.get("envelope_complete") else "lightcoral"
        lines.append(f'  {node_id[path]} [label="{label}", fillcolor="{color}"];')

    for ci, (keywords, members) in enumerate(clusters):
        kw_label = _dot_escape(", ".join(sorted(keywords)[:3]))
        lines.append(f"  subgraph cluster_{ci} {{")
        lines.append(f'    label="topic: {kw_label}";')
        lines.append("    style=rounded;")
        lines.append('    color="gray60";')
        for path, r, topic in members:
            emit_node(path, r, topic)
        lines.append("  }")

    if untyped:
        lines.append("  subgraph cluster_untyped {")
        lines.append('    label="(no topic)";')
        lines.append("    style=dashed;")
        for path, r in untyped:
            emit_node(path, r, "")
        lines.append("  }")

    lines.append("")
    lines.append("  // chronological chain within each topic cluster")
    for keywords, members in clusters:
        for i in range(len(members) - 1):
            a, b = members[i][0], members[i + 1][0]
            lines.append(f'  {node_id[a]} -> {node_id[b]} [label="chrono", color=black];')

    lines.append("")
    lines.append("  // shared required_receipt signatures (cross-cluster)")
    for sig, paths in _shared_signatures(receipts, "required_receipts").items():
        for i in range(len(paths) - 1):
            lines.append(
                f"  {node_id[paths[i]]} -> {node_id[paths[i + 1]]} "
                '[label="shared_req", style=dashed, color=blue, constraint=false];'
            )

    lines.append("")
    lines.append("  // shared HAL question signatures (cross-cluster)")
    for sig, paths in _shared_signatures(receipts, "hal_questions").items():
        for i in range(len(paths) - 1):
            lines.append(
                f"  {node_id[paths[i]]} -> {node_id[paths[i + 1]]} "
                '[label="shared_q", style=dotted, color=orange, constraint=false];'
            )

    lines.append("}")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dir",
        default=str(DEFAULT_PROPOSAL_DIR),
        help="proposal directory to analyze",
    )
    parser.add_argument(
        "--dot",
        metavar="PATH",
        help="Write Graphviz DOT file to PATH instead of ASCII. Creates parent dirs.",
    )
    args = parser.parse_args()
    proposal_dir = Path(args.dir)

    receipts = load_receipts(proposal_dir)
    if not receipts:
        print(f"[graph] no receipts found in {proposal_dir}.")
        return 0

    if args.dot:
        out = Path(args.dot)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(render_dot(receipts), encoding="utf-8")
        print(f"[graph] wrote DOT file ({len(receipts)} receipts) -> {out}")
        return 0

    print(render_ascii(receipts))
    return 0


if __name__ == "__main__":
    sys.exit(main())
