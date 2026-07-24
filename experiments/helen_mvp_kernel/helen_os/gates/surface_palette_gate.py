"""
Surface Palette Gate — Gate Layer 4.

Detects CSS governance-color leakage in HTML surface files that declare
authority=false. Wires check_leakage → score_runs into a single
GateVerdict compatible with composite_admissibility.

What this catches:
  - CSS rules using #00ff88 / --green / --grn for semantic UI states
    (live, done, committed, shipped, …) inside authority=false files
  - Source Atlas one-meaning-per-color violation (WULMOJI secondary gap)

What this does NOT catch:
  - Emoji 🟢/🟡/⚪ violations (addressed by E12 fix, commit e9ae8f9)
  - Sovereign files (not scanned — no writes to sovereign layer)

NON_SOVEREIGN · authority=false · NO_CLAIM · ledger_effect=none

Caller usage:
    from helen_os.gates.surface_palette_gate import surface_palette_gate
    verdict = surface_palette_gate("apps/helen-surface/**/*.html", repo_root=".")
    if verdict["verdict"] == "BLOCK":
        ...
"""
from __future__ import annotations

import datetime
import hashlib
import json
from pathlib import Path
from typing import Any

from helen_os.skills.surface_grammar.check_leakage import scan_glob
from helen_os.skills.surface_grammar.score_runs import score as score_run


def _now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")


def surface_palette_gate(
    path_glob: str = "apps/helen-surface/**/*.html",
    repo_root: str | Path = ".",
    pass_threshold: int = 0,
) -> dict[str, Any]:
    """
    Run the surface palette gate.

    Returns a gate receipt dict:
      verdict          PASS | BLOCK
      violation_count  int
      score            float  (1.0 = clean)
      violations       list of leakage events
      gate_hash        sha256 of the violations payload (deterministic)
      ts               ISO timestamp (UTC)
    """
    violations = scan_glob(path_glob, repo_root)

    trace = {
        "skill_id": "surface_grammar_v1",
        "gate": "check_leakage",
        "authority": False,
        "claim_status": "NO_CLAIM",
        "scanned_glob": path_glob,
        "violation_count": len(violations),
        "violations": violations,
    }

    scored = score_run(trace, pass_threshold=pass_threshold)

    payload_bytes = json.dumps(violations, sort_keys=True, ensure_ascii=False).encode()
    gate_hash = hashlib.sha256(payload_bytes).hexdigest()

    return {
        "gate": "surface_palette_gate",
        "authority": False,
        "claim_status": "NO_CLAIM",
        "ledger_effect": "none",
        "verdict": scored["verdict"],
        "score": scored["score"],
        "violation_count": len(violations),
        "pass_threshold": pass_threshold,
        "violations": violations,
        "gate_hash": gate_hash,
        "ts": _now_iso(),
    }


if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Surface Palette Gate")
    parser.add_argument("--glob", default="apps/helen-surface/**/*.html")
    parser.add_argument("--root", default=".")
    parser.add_argument("--threshold", type=int, default=0)
    args = parser.parse_args()

    result = surface_palette_gate(
        path_glob=args.glob,
        repo_root=args.root,
        pass_threshold=args.threshold,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if result["verdict"] == "PASS" else 1)
