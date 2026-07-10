"""evidence_bridge.py — Converts recorded loop outcomes into observed ranking signals.

NON_SOVEREIGN · AUTHORITY=false · CANON=false · LEDGER_EFFECT=none

This is the feedback organ the two-stage loop was missing: observation_packet
exposes a `supplied_rankings` seam, surface_ranker blends observed evidence at
60% weight — but until now nothing ever produced that signal, so every
iteration ran blind on hardcoded defaults.

The bridge is PURE READ: it derives a 0-1 evidence score per allowed surface
from outcome fields in loop_state.json target_history entries. It never
writes. Outcome recording is the swarm's (or operator's) job — see
goblin_swarm.record_outcome().

Outcome semantics (per history entry):
  KEEP      — experiment kept by operator/measurer rule  → strong positive
  DISCARD   — experiment discarded                       → strong negative
  MEASURED  — baseline measured, verdict pending         → mild positive (data exists)
  PENDING / absent — proposal only, no data              → no contribution

Signal formula (documented, deterministic):
  score = 0.5 + 0.4 * (keeps - discards) / contribs + 0.1 * (1 if any MEASURED else 0)
  clamped to [0.05, 0.95] — evidence is never certainty in either direction.
  No contributing entries → None (missing evidence stays missing; NO_RECEIPT
  discipline forbids inventing a signal).

Fail-closed: unreadable or malformed state → all None.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

_HERE = Path(__file__).resolve().parent
_LOOP_STATE_FILE = _HERE / "loop_state.json"

# Must match observation_packet.ALLOWED_SURFACES / surface_ranker.ALLOWED_SURFACES
ALLOWED_SURFACES: tuple[str, ...] = (
    "context_ranking",
    "init_ranking_weights",
    "prompt_compression",
    "sandbox_visual_grammar",
    "skill_routing",
    "summarization_weights",
)

_POSITIVE = "KEEP"
_NEGATIVE = "DISCARD"
_MEASURED = "MEASURED"
_CONTRIBUTING = frozenset({_POSITIVE, _NEGATIVE, _MEASURED})

_FLOOR = 0.05
_CEIL = 0.95


def _clamp(x: float) -> float:
    return max(_FLOOR, min(_CEIL, x))


def observed_rankings(
    loop_state_path: Optional[Path] = None,
) -> dict[str, Optional[float]]:
    """Derive surface → 0-1 evidence signal from recorded outcomes.

    Pure read. Fail-closed: any read/parse failure → {surface: None}.
    """
    path = loop_state_path or _LOOP_STATE_FILE
    blank: dict[str, Optional[float]] = {s: None for s in ALLOWED_SURFACES}

    if not path.exists():
        return blank
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
        history = state.get("target_history", [])
        if not isinstance(history, list):
            return blank
    except Exception:
        return blank

    out = dict(blank)
    for surface in ALLOWED_SURFACES:
        keeps = discards = contribs = 0
        measured_any = False
        for entry in history:
            if not isinstance(entry, dict) or entry.get("target") != surface:
                continue
            outcome = entry.get("outcome")
            if outcome not in _CONTRIBUTING:
                continue
            contribs += 1
            if outcome == _POSITIVE:
                keeps += 1
            elif outcome == _NEGATIVE:
                discards += 1
            else:
                measured_any = True
        if contribs == 0:
            continue  # no evidence → stays None
        score = 0.5 + 0.4 * (keeps - discards) / contribs + (0.1 if measured_any else 0.0)
        out[surface] = round(_clamp(score), 4)
    return out


def evidence_summary(loop_state_path: Optional[Path] = None) -> dict:
    """Small diagnostic view: per-surface signal + witness-gap flags. Pure read."""
    rankings = observed_rankings(loop_state_path)
    consumption_log = _HERE / "consumption_log.ndjson"
    return {
        "schema": "EVIDENCE_BRIDGE_SUMMARY_V0",
        "authority": False,
        "sovereign": False,
        "canon": False,
        "ledger_effect": "none",
        "rankings": rankings,
        "surfaces_with_evidence": sorted(
            s for s, v in rankings.items() if v is not None
        ),
        "witness_gap": {
            "consumption_log_missing": not consumption_log.exists(),
            "note": (
                "WITNESSED packets fail-close to NO_RECEIPT until the operator "
                "pen writes consumption_log.ndjson. Swarm runs REPORTED."
            ),
        },
    }
