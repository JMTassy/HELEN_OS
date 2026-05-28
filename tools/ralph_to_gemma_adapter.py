#!/usr/bin/env python3
"""
ralph_to_gemma_adapter.py

Projection layer (NOT migration). Reads AUTORESEARCH / RALPH_W NDJSON
receipts and projects each row into GEMMA_PROPOSAL_RAW_V1 shape so that
the existing helen-conquest governance tools (review_cockpit,
hal_receipt_analyzer, receipt_graph, review_queue) can render them
unchanged.

Contract:
  - Input:  --ralph-ndjson PATH (default: helensh/.state/goblin_ar/results.ndjson)
  - Output: --out-dir PATH      (default: GOVERNANCE/RALPH_PROPOSALS/)
  - READ-ONLY on the NDJSON. Source file is never mutated.
  - WRITE-ONLY to the quarantine directory.
  - NEVER writes to town/ledger_v1.ndjson.
  - NEVER mutates lifecycle_entry / auto_promotion_ceiling.
  - Idempotent: same NDJSON row -> same output filename + same content.

Projection (NDJSON field -> GEMMA_PROPOSAL_RAW_V1 field):

  hypothesis              -> proposal_text          (the A stage abstraction)
  mechanism               -> uncertainty_text       (the L stage prototype, still uncertain)
  surviving_mechanism     -> required_receipts      (what HAL filtered as needing evidence)
  sovereignty_violations  -> hal_questions          (HAL's open concerns, numbered)
  verdict/confidence/...  -> ralph_witness (NEW)    (kept separate from hal_verdict
                                                     so RALPH H != governance HAL)
  epoch/receipt_hash/...  -> provenance + prompt_text

Critical design choice (per operator directive):
  RALPH 'H' stage is NOT mapped directly into canonical hal_verdict.
  hal_verdict stays null on every projected receipt. The cockpit HAL lane
  remains an independent governance decision. The ralph_witness field
  preserves the autoresearch HAL output for inspection without
  collapsing the two semantics.

Set on every projected receipt:
  route_id               = "ralph_w_adapter"
  route_authority        = "NON_SOVEREIGN"
  lifecycle_entry        = "RAW"
  auto_promotion_ceiling = "RAW"
  authority              = False
  envelope_complete      = (hypothesis non-empty)
  operator_decision      = null   (untouched -- operator action via cockpit)
  hal_verdict            = null   (untouched -- HAL action via cockpit)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT_DIR = REPO_ROOT / "GOVERNANCE" / "RALPH_PROPOSALS"

SCHEMA_NAME = "GEMMA_PROPOSAL_RAW_V1"
SCHEMA_VERSION = "1.0.0"
ROUTE_ID = "ralph_w_adapter"

TOPIC_MAX = 80


def _short_topic(hypothesis: str) -> str:
    """Derive a stable Topic: line from the hypothesis."""
    if not hypothesis:
        return "(no hypothesis)"
    first_sentence = hypothesis.split(".")[0].strip()
    if len(first_sentence) > TOPIC_MAX:
        first_sentence = first_sentence[:TOPIC_MAX].rstrip() + "..."
    return first_sentence or "(no hypothesis)"


def _numbered_list(items) -> str:
    if not items:
        return ""
    lines = []
    for i, item in enumerate(items, 1):
        text = item if isinstance(item, str) else json.dumps(item, ensure_ascii=False)
        lines.append(f"{i}. {text}")
    return "\n".join(lines)


def _hypothesis_to_prompt(row: dict, source_name: str) -> str:
    return (
        "AUTORESEARCH RALPH_W projection (not original prompt).\n"
        f"Topic: {_short_topic(row.get('hypothesis', ''))}\n"
        f"Source: {source_name}\n"
        f"Epoch: {row.get('epoch', '?')}\n"
        f"Source receipt_hash: {row.get('receipt_hash', '?')[:16]}"
    )


def _project_row(row: dict, source_name: str) -> dict:
    """Project one RALPH NDJSON row into GEMMA_PROPOSAL_RAW_V1 + ralph_witness."""
    hypothesis = row.get("hypothesis", "") or ""
    mechanism = row.get("mechanism", "") or ""
    surviving = row.get("surviving_mechanism", "") or ""
    violations = row.get("sovereignty_violations", []) or []

    envelope_complete = bool(hypothesis.strip())

    ralph_witness = {
        "verdict": row.get("verdict"),
        "confidence": row.get("confidence"),
        "self_verdict": row.get("self_verdict"),
        "rationale": row.get("rationale"),
        "sovereignty_violations": violations,
        "breakthrough": row.get("breakthrough"),
        "surviving_mechanism": surviving,
        "her_time_s": row.get("her_time_s"),
        "hal_time_s": row.get("hal_time_s"),
        "source_epoch": row.get("epoch"),
        "source_receipt_hash": row.get("receipt_hash"),
        "source_previous_hash": row.get("previous_hash"),
        "source_timestamp": row.get("timestamp"),
        "source_file": source_name,
    }

    projected = {
        "schema_name": SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "route_id": ROUTE_ID,
        "route_authority": "NON_SOVEREIGN",
        "lifecycle_entry": "RAW",
        "auto_promotion_ceiling": "RAW",
        "model_id": "autoresearch",
        "system_prompt_sha256": None,
        "prompt_text": _hypothesis_to_prompt(row, source_name),
        "envelope_complete": envelope_complete,
        "proposal_text": hypothesis,
        "uncertainty_text": mechanism,
        "required_receipts": surviving,
        "hal_questions": _numbered_list(violations),
        "raw_response_text": None if envelope_complete else json.dumps(row, ensure_ascii=False),
        "memory_guards": None,
        "tokens_consumed": None,
        "wall_time_seconds": (row.get("her_time_s") or 0) + (row.get("hal_time_s") or 0) or None,
        "done_reason": "ralph_w_projection",
        "receipt_timestamp_utc": row.get("timestamp"),
        "iteration_index": row.get("epoch"),
        "constitutional_breach_notation": None,
        "operator_decision": None,
        "hal_verdict": None,
        "ralph_witness": ralph_witness,
        "authority": False,
    }
    return projected


def _filename_for(row: dict, fallback_index: int) -> str:
    """Deterministic filename: same input row -> same output file."""
    epoch = row.get("epoch")
    rh = row.get("receipt_hash") or ""
    if epoch is not None and rh:
        return f"ralph_epoch{int(epoch):06d}_{rh[:12]}.json"
    if rh:
        return f"ralph_unkep_{rh[:12]}.json"
    # last resort: hash the row content itself so re-runs stay deterministic
    h = hashlib.sha256(json.dumps(row, sort_keys=True).encode("utf-8")).hexdigest()
    return f"ralph_anon_{fallback_index:06d}_{h[:12]}.json"


def adapt(ndjson_path: Path, out_dir: Path, limit: int | None = None) -> tuple[int, int, int]:
    """Project the NDJSON into the quarantine dir. Returns (read, written, skipped)."""
    if not ndjson_path.exists():
        print(f"[adapter] NDJSON not found: {ndjson_path}", file=sys.stderr)
        return (0, 0, 0)

    out_dir.mkdir(parents=True, exist_ok=True)
    source_name = ndjson_path.name

    read = 0
    written = 0
    skipped = 0

    with ndjson_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            read += 1
            if limit is not None and read > limit:
                break
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                print(f"[adapter] skip line {read}: {exc}", file=sys.stderr)
                skipped += 1
                continue
            projected = _project_row(row, source_name)
            out_path = out_dir / _filename_for(row, read)
            out_path.write_text(
                json.dumps(projected, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            written += 1

    return (read, written, skipped)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--ralph-ndjson",
        required=True,
        help="Path to the RALPH / AUTORESEARCH results.ndjson source file",
    )
    parser.add_argument(
        "--out-dir",
        default=str(DEFAULT_OUT_DIR),
        help="Quarantine output directory for projected receipts",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Maximum number of rows to project (default: all)",
    )
    args = parser.parse_args()

    ndjson_path = Path(args.ralph_ndjson)
    out_dir = Path(args.out_dir)

    read, written, skipped = adapt(ndjson_path, out_dir, args.limit)
    print(
        f"[adapter] read={read} written={written} skipped={skipped} "
        f"source={ndjson_path} out={out_dir}"
    )
    print("[adapter] mode: PROJECTION (source NDJSON untouched; quarantine write-only)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
