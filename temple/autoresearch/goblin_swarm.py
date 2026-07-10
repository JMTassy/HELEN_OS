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
  - PREFLIGHT: a WITNESSED dirty-state check runs before any goblin; a
    DIRTY_DOMINATES verdict halts the swarm with zero goblins dispatched.
    Goblin iterations then run as REPORTED packets (WITNESSED collection
    fail-closes to NO_RECEIPT until the operator pen establishes
    consumption_log.ndjson — the swarm surfaces that witness gap).
  - Goblins never KEEP/DISCARD. Measurers record baselines (MEASURED);
    verdicts are operator-only, and the evidence bridge refuses verdicts
    not stamped outcome_actor='operator'.
  - Measurers read git-tracked content only — never runtime traces.
  - Any fable_validate failure halts the whole swarm (fail-closed).
  - Bounded: MAX_GOBLINS = 7; dry_run previews exactly one goblin.
    Sentinel targets (HOLD_FOR_OPERATOR, DIRTY_STATE_DECISION_PACKET)
    stop the swarm immediately.
  - NO HASH = NO VOICE: every goblin report is content-hashed (wall-clock
    fields excluded, so replay can reproduce the hash) into the swarm
    receipt (trace_only/goblin_swarm_receipts.jsonl, garden-local).

Known residual gaps (declared, not hidden): loop_state.json is unchained
garden JSON, so operator verdicts are trust-on-write until this pen is
wired to the hash-chained operator_pen; two_stage_loop's own state save
does not take the flock this module uses.

Usage:
  python3 goblin_swarm.py --goblins 3 --write-state --verbose
  python3 goblin_swarm.py --mark-outcome prompt_compression KEEP --note "why"
"""
from __future__ import annotations

import fcntl
import hashlib
import json
import sys
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))

import dirty_state as ds_mod  # noqa: E402
import evidence_bridge  # noqa: E402
import observation_packet as op_mod  # noqa: E402
import surface_ranker as sr_mod  # noqa: E402
import two_stage_loop as tsl  # noqa: E402

_REPO = _HERE.parent.parent
_TRACE_DIR = _HERE / "trace_only"
_SWARM_RECEIPTS = _TRACE_DIR / "goblin_swarm_receipts.jsonl"
_LOOP_STATE_FILE = _HERE / "loop_state.json"
_OUTBOX = _HERE / "outbox"

MAX_GOBLINS = 7
SENTINEL_TARGETS = frozenset({"HOLD_FOR_OPERATOR", "DIRTY_STATE_DECISION_PACKET"})
VALID_OUTCOMES = ("KEEP", "DISCARD", "MEASURED", "PENDING")


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# Wall-clock fields are excluded from hashed content: a hash that changes
# with the clock can never be reproduced by replay, so it would witness
# nothing (goblin review). Content hashes must be pure functions of the
# run's decisions and inputs.
_VOLATILE_KEYS = frozenset({
    "observed_at", "swarm_started", "swarm_finished", "run_at", "outcome_at",
})


def _sha256_canon(obj: dict) -> str:
    stable = {k: v for k, v in obj.items() if k not in _VOLATILE_KEYS}
    return hashlib.sha256(
        json.dumps(stable, sort_keys=True, ensure_ascii=False).encode("utf-8")
    ).hexdigest()


@contextmanager
def _state_lock(state_path: Path):
    """fcntl.flock guard for loop-state read-modify-write.

    Same TOCTOU class the sovereign ledger already paid for at seq=287:
    two unlocked writers doing load → mutate → replace silently erase each
    other's outcomes. Lock file sits beside the state file.
    """
    lock_path = state_path.with_suffix(".lock")
    with lock_path.open("w") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(fh, fcntl.LOCK_UN)


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


def _measure_init_ranking_weights() -> float:
    """Default-salience ceiling: top score of an evidence-free ranking."""
    return float(sr_mod.rank({}).selected_score)


def _measure_context_ranking() -> float:
    """Authority-shaped token count across the loop's experiment templates."""
    tokens = ("ADMITTED", "SHIP", "PROMOTE", "SEALED")
    text = json.dumps(tsl._EXPERIMENT_TEMPLATES, sort_keys=True)
    return float(sum(text.count(t) for t in tokens))


def _outbox_packets() -> list[dict]:
    """Read tracked AR-*.json outbox packets in sorted order; skip malformed."""
    packets = []
    if _OUTBOX.exists():
        for f in sorted(_OUTBOX.glob("AR-*.json")):
            try:
                packets.append(json.loads(f.read_text(encoding="utf-8")))
            except Exception:
                continue
    return packets


def _measure_skill_routing() -> float:
    """Operator-routing pressure: packets routed to operator review."""
    return float(sum(
        1 for p in _outbox_packets()
        if p.get("recommended_action") == "ROUTE_TO_OPERATOR_FOR_REVIEW"
    ))


def _measure_summarization_weights() -> float:
    """Receipt-reference density across outbox packet summaries (0-1)."""
    packets = _outbox_packets()
    if not packets:
        return 0.0
    hits = sum(1 for p in packets if "receipt" in str(p.get("summary", "")).lower())
    return round(hits / len(packets), 4)


def _measure_sandbox_visual_grammar() -> float:
    """Raw green-glyph count across tracked operator surfaces (misuse proxy)."""
    surface_dir = _REPO / "apps" / "helen-surface"
    total = 0
    if surface_dir.exists():
        for f in sorted(surface_dir.glob("*.html")):
            try:
                total += f.read_text(encoding="utf-8").count("\U0001f7e2")
            except Exception:
                continue
    return float(total)


# Full coverage: every allowed surface has a deterministic baseline
# instrument. Measurers read GIT-TRACKED content only (CORE_PROMPT,
# experiment templates, outbox packets, operator surfaces) — never the
# untracked runtime traces, which mutate under the measurer's feet and
# vanish on a fresh clone (goblin review: fabricated/constant baselines).
# A measurer is therefore a pure function of the commit, and a baseline
# can only move when the measured content actually changes.
MEASURERS: dict[str, Callable[[], float]] = {
    "context_ranking": _measure_context_ranking,
    "init_ranking_weights": _measure_init_ranking_weights,
    "prompt_compression": _measure_prompt_compression,
    "sandbox_visual_grammar": _measure_sandbox_visual_grammar,
    "skill_routing": _measure_skill_routing,
    "summarization_weights": _measure_summarization_weights,
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
    note: Optional[str] = None,
) -> bool:
    """Attach an outcome to the most recent eligible history entry for target.

    Goblins may record MEASURED/PENDING only, and only on entries that have
    no outcome yet (the fresh entry the loop just appended). The operator
    may additionally upgrade PENDING/MEASURED entries to a KEEP/DISCARD
    verdict — that is the whole point of those states. KEEP/DISCARD entries
    are final and never rewritten. Returns True if an entry was updated.
    """
    if outcome not in VALID_OUTCOMES:
        raise ValueError(f"invalid outcome {outcome!r}; allowed: {VALID_OUTCOMES}")
    if outcome in ("KEEP", "DISCARD") and actor != "operator":
        raise PermissionError(
            "KEEP/DISCARD is an operator verdict. Goblins measure; JM decides."
        )
    upgradeable = (None, "PENDING", "MEASURED") if actor == "operator" else (None,)

    path = loop_state_path or _LOOP_STATE_FILE
    if not path.exists():
        return False
    with _state_lock(path):
        try:
            state = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return False

        history = state.get("target_history", [])
        for entry in reversed(history):
            if not isinstance(entry, dict):
                continue
            if entry.get("target") == target and entry.get("outcome") in upgradeable:
                entry["outcome"] = outcome
                if measured is not None:
                    entry["measured"] = measured
                entry["outcome_at"] = _utc_now()
                entry["outcome_actor"] = actor
                if note:
                    entry["outcome_note"] = note
                # distinct tmp suffix: two_stage_loop._save_loop_state uses
                # .tmp; sharing it lets concurrent writers clobber each other
                tmp = path.with_suffix(".pen.tmp")
                tmp.write_text(
                    json.dumps(state, indent=2, ensure_ascii=False),
                    encoding="utf-8",
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

    Preflight: before any goblin runs, a WITNESSED packet is collected and
    dirty-state-evaluated. REPORTED packets are structurally exempt from
    DIRTY_DOMINATES, so without this check the swarm would run blind past a
    live sovereign-path violation (goblin review). DIRTY halts the swarm;
    NO_RECEIPT alone does not — that is the documented witness gap.

    dry_run previews exactly ONE goblin: without persisted state every
    iteration sees identical evidence and repeats the same report, so a
    multi-goblin dry run records N copies of one decision. Growth requires
    --write-state.
    """
    goblins = max(1, min(int(goblins), MAX_GOBLINS))
    if dry_run:
        goblins = 1
    swarm_started = _utc_now()
    goblin_receipts: list[dict] = []
    halt_reason: Optional[str] = None

    witnessed = op_mod.collect()
    preflight = ds_mod.evaluate(witnessed)
    if preflight.dominates:
        halt_reason = f"PREFLIGHT_DIRTY: {'; '.join(preflight.reasons)}"
        goblins = 0

    for i in range(goblins):
        rankings = evidence_bridge.observed_rankings()
        state = tsl._load_loop_state()
        recent = [
            h.get("target", "")
            for h in state.get("target_history", [])[-3:]
            if isinstance(h, dict)
        ]
        recent.reverse()

        pkt = op_mod.from_reported({
            "head": witnessed.head,  # real commit provenance, not a label
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
                    help="operator pen: record KEEP/DISCARD for a target "
                         "(requires --note; see LAW OF THE PEN)")
    ap.add_argument("--note", default="",
                    help="operator justification recorded with --mark-outcome")
    a = ap.parse_args()

    if a.mark_outcome:
        target, outcome = a.mark_outcome
        outcome = outcome.upper()
        # LAW OF THE PEN: this CLI cannot authenticate who is typing. A note
        # is mandatory so every verdict carries a recorded justification, and
        # agents are FORBIDDEN from invoking it — loop_state.json is unchained
        # garden state, so verdicts here are trust-on-write until the swarm
        # is wired to the hash-chained operator_pen (declared NEXT step).
        if outcome in ("KEEP", "DISCARD") and not a.note.strip():
            print("REFUSED: KEEP/DISCARD requires --note with the operator's "
                  "justification. Goblins measure; JM decides.")
            return 1
        try:
            ok = record_outcome(target, outcome, actor="operator",
                                note=a.note.strip() or None)
        except (ValueError, PermissionError) as exc:
            print(f"REFUSED: {exc}")
            return 1
        print(f"mark_outcome {target} {outcome}: "
              f"{'recorded' if ok else 'NO eligible entry (already final or never targeted)'}")
        return 0 if ok else 1

    run_swarm(a.goblins, dry_run=not a.write_state, verbose=a.verbose)
    return 0


if __name__ == "__main__":
    sys.exit(main())
