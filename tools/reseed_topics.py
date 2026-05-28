#!/usr/bin/env python3
"""
reseed_topics.py

Read-only governance-failure miner. Reads the unified queue (GEMMA +
RALPH proposals), extracts repeated HAL concerns and missing-evidence
patterns, and emits next-topic CANDIDATES the operator can choose to
feed into the next autoresearch run.

The system does NOT auto-seed. This tool only surfaces patterns. The
operator decides which candidates become live research topics.

Inputs (read-only):
  - GOVERNANCE/GEMMA_PROPOSALS/*.json
  - GOVERNANCE/RALPH_PROPOSALS/*.json
  - Optional: filter to a queue category (default: all sources, all categories)

Output (default):
  Human-readable ranked candidate list.

Output (--json):
  JSON array of:
    {
      "topic":          str   - normalized 10-word seed phrase
      "reason":         str   - one-line explanation of the signal
      "evidence_count": int   - number of distinct receipts containing the signature
      "source_mix":     [str] - subset of ["GEMMA","RALPH"]
      "signal":         str   - "hal_question" | "missing_receipt"
      "priority":       str   - "HIGH" | "MEDIUM" | "LOW"
      "blocked_count":  int   - how many of those receipts are HAL BLOCKED
      "example_paths":  [str] - up to 3 receipt filenames as provenance
    }

Hard constraints:
  - READ ONLY across all sources.
  - NEVER writes to receipt files.
  - NEVER writes to town/ledger_v1.ndjson.
  - NEVER mutates lifecycle_entry or auto_promotion_ceiling.
  - NEVER seeds gemma_autonomous_loop.py automatically. This tool emits
    candidates to stdout / a JSON file. Operator action is required.
  - NEVER calls a model. No generation. No synthesis beyond truncation
    + lowercase normalization of phrases that already exist in the
    corpus. The topic strings are quotes, not inventions.

Usage:
  python tools/reseed_topics.py                                # ranked list, all sources
  python tools/reseed_topics.py --source ralph                 # only RALPH corpus
  python tools/reseed_topics.py --queue blocked                # only BLOCKED receipts
  python tools/reseed_topics.py --min-evidence 3               # raise threshold
  python tools/reseed_topics.py --json > reports/next_topics.json
  python tools/reseed_topics.py --top 10                       # limit output

Priority heuristic:
  HIGH     evidence_count >= 3, OR multi-source AND evidence_count >= 2,
           OR any contributing receipt is HAL BLOCKED
  MEDIUM   evidence_count >= 2 (single-source, not blocked)
  LOW      evidence_count == --min-evidence (when min < 2)
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hal_receipt_analyzer import (  # noqa: E402
    normalize_item,
    split_numbered_items,
)
from review_queue import (  # noqa: E402
    _load_tagged,
    classify,
)
# Cockpit owns the queue-name -> category mapping; reuse it for arg parity.
from review_cockpit import QUEUE_TO_CATEGORY  # noqa: E402

SIGNAL_FIELDS = (
    # (receipt field, human-readable signal name, reason template)
    ("hal_questions", "hal_question",
     "{n} repeated HAL concern(s): \"{sig}\""),
    ("required_receipts", "missing_receipt",
     "{n} receipt(s) flagged missing evidence: \"{sig}\""),
)


def _gather_signatures(
    tagged_receipts: list[tuple[Path, dict, str]],
    field: str,
) -> dict[str, list[tuple[Path, dict, str]]]:
    """For each normalized signature in `field`, list contributing receipts."""
    bucket: dict[str, list[tuple[Path, dict, str]]] = defaultdict(list)
    for path, receipt, src in tagged_receipts:
        seen_in_this_receipt: set[str] = set()
        for item in split_numbered_items(receipt.get(field)):
            sig = normalize_item(item)
            if not sig or sig in seen_in_this_receipt:
                continue
            seen_in_this_receipt.add(sig)
            bucket[sig].append((path, receipt, src))
    return bucket


def _classify_priority(
    evidence_count: int,
    source_mix: set[str],
    blocked_count: int,
    min_evidence: int,
) -> str:
    if blocked_count > 0:
        return "HIGH"
    if evidence_count >= 3:
        return "HIGH"
    if evidence_count >= 2 and len(source_mix) >= 2:
        return "HIGH"
    if evidence_count >= 2:
        return "MEDIUM"
    if evidence_count >= min_evidence:
        return "LOW"
    return "LOW"


def build_candidates(
    tagged_receipts: list[tuple[Path, dict, str]],
    min_evidence: int,
) -> list[dict]:
    candidates: list[dict] = []
    for field, signal_name, reason_tmpl in SIGNAL_FIELDS:
        bucket = _gather_signatures(tagged_receipts, field)
        for sig, contributors in bucket.items():
            if len(contributors) < min_evidence:
                continue
            source_mix = sorted({src for _, _, src in contributors})
            blocked_count = sum(
                1 for _, r, _ in contributors if "BLOCKED" in classify(r)
            )
            priority = _classify_priority(
                evidence_count=len(contributors),
                source_mix=set(source_mix),
                blocked_count=blocked_count,
                min_evidence=min_evidence,
            )
            example_paths = [p.name for p, _, _ in contributors[:3]]
            reason = reason_tmpl.format(n=len(contributors), sig=sig)
            if blocked_count:
                reason += f" ({blocked_count} currently BLOCKED)"
            candidates.append({
                "topic": sig,
                "reason": reason,
                "evidence_count": len(contributors),
                "source_mix": source_mix,
                "signal": signal_name,
                "priority": priority,
                "blocked_count": blocked_count,
                "example_paths": example_paths,
            })

    priority_rank = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    candidates.sort(
        key=lambda c: (
            priority_rank.get(c["priority"], 9),
            -c["evidence_count"],
            -c["blocked_count"],
            c["topic"],
        )
    )
    return candidates


def render_text(candidates: list[dict], scope: str) -> str:
    bar = "=" * 72
    lines = [bar, f"NEXT RESEARCH CANDIDATES  ({scope})", bar, ""]
    if not candidates:
        lines.append("(no repeated governance signals at current threshold)")
        return "\n".join(lines)
    for i, c in enumerate(candidates, 1):
        lines.append(
            f"[{i:>2}] {c['priority']:<6} "
            f"ev={c['evidence_count']} blocked={c['blocked_count']} "
            f"src={'+'.join(c['source_mix'])} "
            f"signal={c['signal']}"
        )
        lines.append(f"     topic:  {c['topic']}")
        lines.append(f"     reason: {c['reason']}")
        lines.append(f"     from:   {', '.join(c['example_paths'])}")
        lines.append("")
    lines.append(bar)
    lines.append("OPERATOR ACTION REQUIRED: these are candidates, not commitments.")
    lines.append("Topic strings are quoted from the corpus, not synthesized.")
    lines.append("Choose which (if any) to feed into the next autoresearch run.")
    lines.append(bar)
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        choices=["gemma", "ralph", "all"],
        default="all",
        help="receipt source corpus (default: all)",
    )
    parser.add_argument(
        "--queue",
        choices=list(QUEUE_TO_CATEGORY.keys()),
        default=None,
        help="restrict to a queue category (uses review_queue.classify)",
    )
    parser.add_argument(
        "--min-evidence",
        type=int,
        default=2,
        help="minimum number of distinct receipts containing a signature (default: 2)",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=None,
        help="emit only the top N candidates",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="emit candidates as a JSON array on stdout (no banner, no operator note)",
    )
    args = parser.parse_args()

    tagged = _load_tagged(args.source)
    if args.queue is not None:
        required_cat = QUEUE_TO_CATEGORY[args.queue]
        tagged = [t for t in tagged if required_cat in classify(t[1])]

    scope_parts = [f"source={args.source}"]
    if args.queue:
        scope_parts.append(f"queue={args.queue}")
    scope_parts.append(f"min_evidence={args.min_evidence}")
    scope_parts.append(f"corpus_size={len(tagged)}")
    scope = "  ".join(scope_parts)

    if not tagged:
        msg = f"[reseed] no receipts in scope ({scope})."
        if args.json:
            print("[]")
        else:
            print(msg)
        return 0

    candidates = build_candidates(tagged, args.min_evidence)
    if args.top is not None:
        candidates = candidates[: args.top]

    if args.json:
        print(json.dumps(candidates, indent=2, ensure_ascii=False))
    else:
        print(render_text(candidates, scope))
    return 0


if __name__ == "__main__":
    sys.exit(main())
