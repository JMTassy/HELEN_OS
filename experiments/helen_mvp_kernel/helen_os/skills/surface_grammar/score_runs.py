"""
score_runs.py — Surface Grammar run scorer.

Reads a check_leakage JSON or YAML trace and returns:
  score   0.0–1.0   (1.0 = clean, 0.0 = every candidate violated)
  verdict PASS | BLOCK

Scoring formula:
  If violations == 0 → score = 1.0, verdict = PASS
  Otherwise          → score = 0.0, verdict = BLOCK
  (binary gate: any leakage blocks; no partial credit)

The pass_threshold param lets operators relax the gate during migration
(e.g. --threshold 2 allows up to 2 violations before BLOCK).

NON_SOVEREIGN · authority=false · NO_CLAIM · ledger_effect=none

Usage:
    python score_runs.py trace.json [--threshold 0] [--format json|yaml]
    python score_runs.py trace.yaml [--threshold 0] [--format json|yaml]
    cat trace.json | python score_runs.py - [--threshold 0]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


# ── Loaders ───────────────────────────────────────────────────────────────────


def _load(source: str) -> dict[str, Any]:
    """Load JSON or YAML from a file path or '-' for stdin."""
    if source == "-":
        raw = sys.stdin.read()
    else:
        raw = Path(source).read_text(encoding="utf-8")

    # Try JSON first (no dependency); fall back to YAML
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    try:
        import yaml  # type: ignore[import]
        return yaml.safe_load(raw)
    except ImportError:
        raise SystemExit(
            "error: input is not valid JSON and pyyaml is not installed."
        ) from None


# ── Scoring ───────────────────────────────────────────────────────────────────


def score(trace: dict[str, Any], pass_threshold: int = 0) -> dict[str, Any]:
    """
    Compute score + verdict from a check_leakage trace dict.

    Returns a result dict with keys: score, verdict, violation_count,
    pass_threshold, violations_summary.
    """
    violations = trace.get("violations", [])
    n = len(violations)

    passed = n <= pass_threshold
    result: dict[str, Any] = {
        "skill_id": trace.get("skill_id", "surface_grammar_v1"),
        "gate": "score_runs",
        "authority": False,
        "claim_status": "NO_CLAIM",
        "pass_threshold": pass_threshold,
        "violation_count": n,
        "score": 1.0 if passed else 0.0,
        "verdict": "PASS" if passed else "BLOCK",
        "violations_summary": [
            {
                "file": v.get("file", "?"),
                "line": v.get("line", 0),
                "selector": v.get("selector", "?"),
                "token": v.get("token", "?"),
                "semantic_meaning": v.get("semantic_meaning", "?"),
            }
            for v in violations
        ],
    }
    return result


# ── Serialisation ─────────────────────────────────────────────────────────────


def _emit(data: dict, fmt: str) -> str:
    if fmt == "yaml":
        try:
            import yaml  # type: ignore[import]
            return yaml.dump(data, sort_keys=False, allow_unicode=True)
        except ImportError:
            print("warning: pyyaml not available — falling back to JSON", file=sys.stderr)
    return json.dumps(data, indent=2, ensure_ascii=False)


# ── CLI ───────────────────────────────────────────────────────────────────────


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Surface Grammar run scorer")
    parser.add_argument(
        "trace",
        nargs="?",
        default="-",
        help="check_leakage output file (JSON or YAML) or '-' for stdin",
    )
    parser.add_argument(
        "--threshold",
        type=int,
        default=0,
        help="Max violations allowed before BLOCK (default: 0)",
    )
    parser.add_argument("--format", choices=["json", "yaml"], default="json")
    args = parser.parse_args()

    trace = _load(args.trace)
    result = score(trace, pass_threshold=args.threshold)
    print(_emit(result, args.format))

    sys.exit(0 if result["verdict"] == "PASS" else 1)
