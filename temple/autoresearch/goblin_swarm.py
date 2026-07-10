#!/usr/bin/env python3
"""goblin_swarm.py — Bounded goblin swarm over the two-stage autoresearch loop.

NON_SOVEREIGN · AUTHORITY=false · CANON=false · LEDGER_EFFECT=none
UNDERWARREN_SAFE · THE HEAP MAY SPEAK, THE LEDGER MUST VERIFY

Roles (operator-ruled anatomy, extended):
  goblins          = hands-in-the-heap: one bounded loop iteration each,
                     observe → rank → propose → MEASURE baseline → record
  FABLE            = validation gate: every goblin report passes
                     fable_validate() or the swarm halts (fail-closed)
  evidence_bridge  = eye: recorded outcomes → next goblin's ranking signal
  operator (JM)    = the only KEEP/DISCARD authority (mark_outcome CLI)

What makes this iterative growth rather than a blind loop:
  goblin N records an outcome → evidence_bridge converts it to an observed
  ranking → goblin N+1's ranking is evidence-blended (60% observed) → targets
  rotate and scores drift with data, not with hardcoded defaults.

Hard laws:
  - Swarm runs REPORTED packets only. WITNESSED collection fail-closes to
    NO_RECEIPT until the operator pen establishes consumption_log.ndjson;
    the swarm surfaces that witness gap, it never bypasses it.
  - Goblins never KEEP/DISCARD. Measurers record baselines (MEASURED);
    verdicts are operator-only.
  - Any fable_validate failure halts the whole swarm (fail-closed).
  - Bounded: MAX_GOBLINS = 7. Sentinel targets (HOLD_FOR_OPERATOR,
    DIRTY_STATE_DECISION_PACKET) stop the swarm immediately.
  - NO HASH = NO VOICE: every goblin report is sha256-hashed into the
    swarm receipt (trace_only/goblin_swarm_receipts.jsonl, garden-local).

Usage:
  python3 goblin_swarm.py --goblins 3 --write-state --verbose
  python3 goblin_swarm.py --mark-outcome prompt_compression KEEP   # operator pen
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))

import evidence_bridge  # noqa: E402
import observation_packet as op_mod  # noqa: E402
import surface_ranker as sr_mod  # noqa: E402
import two_stage_loop as tsl  # noqa: E402

_TRACE_DIR = _HERE / "trace_only"
_SWARM_RECEIPTS = _TRACE_DIR / "goblin_swarm_receipts.jsonl"
_LOOP_STATE_FILE = _HERE / "loop_state.json"
_TRACE_FILE = _TRACE_DIR / "two_stage_loop_trace.jsonl"

MAX_GOBLINS = 7
SENTINEL_TARGETS = frozenset({"HOLD_FOR_OPERATOR", "DIRTY_STATE_DECISION_PACKET"})
VALID_OUTCOMES = ("KEEP", "DISCARD", "MEASURED", "PENDING")


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _sha256_canon(obj: dict) -> str:
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, ensure_ascii=False).encode("utf-8")
    ).hexdigest()


# ---------------------------------------------------------------------------
# FABLE validation gate — fail-closed
# ---------------------------------------------------------------------------

class FableVerdict:
    def __init__(self, ok: bool, reasons: list[str]):
        self.ok = ok
        self.reasons = reasons


def fable_validate(report: dict) -> FableVerdict:
    """Hard-law gate over a single goblin report. Fail-closed on any doubt."""
    reasons: list[str] = []
    try:
        if report.get("authority") is not False:
            reasons.append("authority must be False")
        if report.get("sovereign") is not False:
            reasons.append("sovereign must be False")
        if report.get("canon") is not False:
            reasons.append("canon must be False")
        if report.get("ledger_effect") != "none":
            reasons.append("ledger_effect must be 'none'")
        if report.get("reducer_required") is not True:
            reasons.append("reducer_required must be True")

        target = report.get("TARGET", "")
        if target in SENTINEL_TARGETS:
            pass  # lawful halts validate clean
        elif target in sr_mod.ALLOWED_SURFACES:
            sr_mod.assert_not_forbidden(target)
        else:
            reasons.append(f"TARGET {target!r} not an allowed surface or sentinel")

        if not str(report.get("TWEAK", "")).strip():
            reasons.append("TWEAK must be non-empty (reversibility must be stated)")
        if not str(report.get("RULE", "")).strip():
            reasons.append("RULE must be non-empty (keep/discard rule required)")
    except Exception as exc:  # fail-closed: validation error = invalid
        reasons.append(f"validation exception: {exc}")
    return FableVerdict(ok=not reasons, reasons=reasons)


# ---------------------------------------------------------------------------
# Measurers — deterministic, read-only baseline instruments.
# A measurer produces a number; it NEVER produces a verdict.
# ---------------------------------------------------------------------------

def _measure_prompt_compression() -> float:
    """Whitespace-token estimate of the loop's CORE_PROMPT."""
    return float(len(tsl.CORE_PROMPT.split()))


def _measure_summarization_weights() -> float:
    """Receipt-reference density over the last 20 trace lines (0-1)."""
    if not _TRACE_FILE.exists():
        return 0.0
    lines = [
        l for l in _TRACE_FILE.read_text(encoding="utf-8").splitlines() if l.strip()
    ][-20:]
    if not lines:
        return 0.0
    hits = sum(1 for l in lines if "receipt" in l.lower())
    return round(hits / len(lines), 4)


def _measure_sandbox_visual_grammar() -> float:
    """Count of 🟢 glyphs in garden trace output (misuse proxy; target 0)."""
    if not _TRACE_FILE.exists():
        return 0.0
    return float(_TRACE_FILE.read_text(encoding="utf-8").count("\U0001f7e2"))


MEASURERS: dict[str, Callable[[], float]] = {
    "prompt_compression": _measure_prompt_compression,
    "summarization_weights": _measure_summarization_weights,
    "sandbox_visual_grammar": _measure_sandbox_visual_grammar,
}


# ---------------------------------------------------------------------------
# Outcome recording — the only writer, and it only writes garden state
# ---------------------------------------------------------------------------

def record_outcome(
    target: str,
    outcome: str,
    measured: Optional[float] = None,
    *,
    loop_state_path: Optional[Path] = None,
    actor: str = "goblin_swarm",
) -> bool:
    """Attach an outcome to the most recent outcome-less history entry for target.

    Goblins may record MEASURED/PENDING only. KEEP/DISCARD is operator-only
    (actor='operator'); a goblin attempting a verdict is refused (fail-closed).
    Returns True if an entry was updated.
    """
    if outcome not in VALID_OUTCOMES:
        raise ValueError(f"invalid outcome {outcome!r}; allowed: {VALID_OUTCOMES}")
    if outcome in ("KEEP", "DISCARD") and actor != "operator":
        raise PermissionError(
            "KEEP/DISCARD is an operator verdict. Goblins measure; JM decides."
        )

    path = loop_state_path or _LOOP_STATE_FILE
    if not path.exists():
        return False
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return False

    history = state.get("target_history", [])
    for entry in reversed(history):
        if entry.get("target") == target and "outcome" not in entry:
            entry["outcome"] = outcome
            if measured is not None:
                entry["measured"] = measured
            entry["outcome_at"] = _utc_now()
            entry["outcome_actor"] = actor
            tmp = path.with_suffix(".tmp")
            tmp.write_text(
                json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8"
            )
            tmp.replace(path)
            return True
    return False


# ---------------------------------------------------------------------------
# Swarm runner
# ---------------------------------------------------------------------------

def run_swarm(
    goblins: int = 3,
    *,
    dry_run: bool = True,
    verbose: bool = False,
) -> dict:
    """Run up to `goblins` bounded loop iterations with evidence feedback.

    Each goblin: evidence_bridge → REPORTED packet → two_stage_loop.run →
    fable_validate → measure baseline → record MEASURED/PENDING outcome.
    Halts early on sentinel targets or any FABLE validation failure.
    """
    goblins = max(1, min(int(goblins), MAX_GOBLINS))
    swarm_started = _utc_now()
    goblin_receipts: list[dict] = []
    halt_reason: Optional[str] = None

    for i in range(goblins):
        rankings = evidence_bridge.observed_rankings()
        state = tsl._load_loop_state()
        recent = [h.get("target", "") for h in state.get("target_history", [])[-3:]]
        recent.reverse()

        pkt = op_mod.from_reported({
            "head": "GOBLIN_SWARM_REPORTED",
            "rankings": rankings,
            "recent_targets": recent,
        })
        report = tsl.run(packet=pkt, dry_run=dry_run, verbose=verbose)

        verdict = fable_validate(report)
        target = report.get("TARGET", "")

        measured: Optional[float] = None
        outcome_recorded = False
        if verdict.ok and target not in SENTINEL_TARGETS and not dry_run:
            measurer = MEASURERS.get(target)
            if measurer is not None:
                try:
                    measured = measurer()
                except Exception:
                    measured = None  # measurement failure ≠ verdict; stays PENDING
            outcome_recorded = record_outcome(
                target,
                "MEASURED" if measured is not None else "PENDING",
                measured,
            )

        goblin_receipts.append({
            "goblin": i + 1,
            "target": target,
            "score": report.get("selected_score", 0.0),
            "evidence_in": {k: v for k, v in rankings.items() if v is not None},
            "fable_ok": verdict.ok,
            "fable_reasons": verdict.reasons,
            "measured": measured,
            "outcome_recorded": outcome_recorded,
            "report_hash": _sha256_canon(report),
        })

        if not verdict.ok:
            halt_reason = f"FABLE_BLOCK: goblin {i + 1} failed validation"
            break
        if target in SENTINEL_TARGETS:
            halt_reason = f"SENTINEL: goblin {i + 1} hit {target}"
            break

    receipt = {
        "schema": "GOBLIN_SWARM_RECEIPT_V0",
        "authority": False,
        "sovereign": False,
        "canon": False,
        "ledger_effect": "none",
        "reducer_required": True,
        "dry_run": dry_run,
        "swarm_started": swarm_started,
        "swarm_finished": _utc_now(),
        "goblins_requested": goblins,
        "goblins_ran": len(goblin_receipts),
        "halt_reason": halt_reason,
        "witness_gap": evidence_bridge.evidence_summary()["witness_gap"],
        "goblins": goblin_receipts,
    }
    receipt["receipt_hash"] = _sha256_canon(
        {k: v for k, v in receipt.items() if k != "receipt_hash"}
    )

    _TRACE_DIR.mkdir(parents=True, exist_ok=True)
    with _SWARM_RECEIPTS.open("a", encoding="utf-8") as f:
        f.write(json.dumps(receipt, ensure_ascii=False) + "\n")

    if verbose:
        print(f"\n[SWARM] ran={receipt['goblins_ran']}/{goblins} "
              f"halt={halt_reason or 'completed'} "
              f"receipt_hash={receipt['receipt_hash'][:12]}")
    return receipt


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(
        description="Bounded goblin swarm over the two-stage loop (NON_SOVEREIGN)"
    )
    ap.add_argument("--goblins", type=int, default=3,
                    help=f"goblin count, 1-{MAX_GOBLINS} (default 3)")
    ap.add_argument("--write-state", action="store_true", default=False,
                    help="persist loop_state.json outcomes (default: dry-run)")
    ap.add_argument("--verbose", action="store_true", default=False)
    ap.add_argument("--mark-outcome", nargs=2, metavar=("TARGET", "OUTCOME"),
                    help="operator pen: record KEEP/DISCARD for a target")
    a = ap.parse_args()

    if a.mark_outcome:
        target, outcome = a.mark_outcome
        ok = record_outcome(target, outcome.upper(), actor="operator")
        print(f"mark_outcome {target} {outcome.upper()}: "
              f"{'recorded' if ok else 'NO matching pending entry'}")
        return 0 if ok else 1

    run_swarm(a.goblins, dry_run=not a.write_state, verbose=a.verbose)
    return 0


if __name__ == "__main__":
    sys.exit(main())
