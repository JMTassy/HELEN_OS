#!/usr/bin/env python3
"""two_stage_loop.py — Two-stage observe-then-experiment autoresearch loop.

NON_SOVEREIGN · AUTHORITY=false · CANON=false · LEDGER_EFFECT=none

Stage 1: OBSERVE  — collect read-only observation packet (git reads only)
Stage 2: DECIDE   — classify dirty state, rank surfaces, plan experiment

Decision flow:
  OBSERVE → CLASSIFY → CHECK_DIRTY_DOMINATES → IF YES: DIRTY_STATE_DECISION_PACKET
                                              → ELSE: RANK ALLOWED SURFACES
                                                      → SELECT ONE
                                                      → CHECK ANTI_LOOP
                                                      → PLAN ONE REVERSIBLE TWEAK
                                                      → REPORT → STOP

Hard laws:
  No loop may target the same surface twice without new evidence.
  No loop may touch kernel truth, identity, ledger, replay, sovereign memory, or the evaluator.
  REPORTED packets never trigger dirty-state verdicts.
  Missing evidence → NO_RECEIPT; HOLD_FOR_OPERATOR.

Output format (exactly):
  TARGET: <surface>
  HYPOTHESIS: <one sentence>
  TWEAK: <one reversible variable change>
  METRIC: <baseline vs threshold>
  RULE: <keep/discard rule>
  NEXT: <next action>
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# Garden-local paths
_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parent.parent
_LOOP_STATE_FILE = _HERE / "loop_state.json"
_TRACE_DIR = _HERE / "trace_only"
_TRACE_FILE = _TRACE_DIR / "two_stage_loop_trace.jsonl"

# ---------------------------------------------------------------------------
# Core prompt — exact text supplied by operator. Do not paraphrase.
# ---------------------------------------------------------------------------

CORE_PROMPT = """\
Read the supplied observation packet first.
Do not infer dirty state from absent evidence.
Set DIRTY_DOMINATES only if evidence shows:
- replay mismatch,
- unauthorized sovereign-path modification,
- unknown provenance touching sovereign paths.
If evidence is incomplete: NO_RECEIPT; HOLD_FOR_OPERATOR
Otherwise rank only:
- /init ranking weights
- context ranking
- prompt compression
- skill routing
- summarization weights
- sandbox visual grammar
Use: score = leverage × evidence × reversibility / (cost + blast_radius)
Choose exactly one target.
Change exactly one reversible variable.
Measure baseline against result.
Do not repeat a target twice without new evidence.
Output exactly: TARGET; HYPOTHESIS; TWEAK; METRIC; RULE; NEXT"""

# Allowed surfaces (must match observation_packet.ALLOWED_SURFACES)
ALLOWED_SURFACES = (
    "init_ranking_weights",
    "context_ranking",
    "prompt_compression",
    "skill_routing",
    "summarization_weights",
    "sandbox_visual_grammar",
)

# Anti-loop: how many recent identical targets trigger HOLD_FOR_OPERATOR
ANTI_LOOP_THRESHOLD = 2

# ---------------------------------------------------------------------------
# Experiment templates per surface
# ---------------------------------------------------------------------------

_EXPERIMENT_TEMPLATES: dict[str, dict] = {
    "init_ranking_weights": {
        "hypothesis": "Adjusting init ranking weights improves salience of non-sovereign surfaces without altering kernel truth.",
        "tweak": "Increase weight of 'context_ranking' by 0.05 in init_ranking_weights config.",
        "metric": "baseline: current salience score; success_threshold: salience increases ≥0.03 on next observe cycle",
        "rule": "KEEP if salience improves and no sovereign diff; DISCARD if ranking diverges or dirty_paths increase",
        "next": "MEASURE baseline → apply tweak → re-observe → compare",
    },
    "context_ranking": {
        "hypothesis": "Tightening context ranking reduces authority-shaped output in non-sovereign layers.",
        "tweak": "Add MAYBE_CANDIDATE prefix to routed proposals in context_ranking output.",
        "metric": "baseline: count authority-shaped verbs in last 3 outputs; success_threshold: ≤2 authority verbs",
        "rule": "KEEP if authority verb count drops; DISCARD if operator-facing outputs degrade",
        "next": "MEASURE baseline → apply prefix tweak → re-run scan → count authority verbs",
    },
    "sandbox_visual_grammar": {
        "hypothesis": "One visual grammar rule change measurably reduces sovereign-color false positives.",
        "tweak": "Remove 🟢 from non-admitted sandbox renders; replace with 🔵 OBSERVED.",
        "metric": "baseline: count misused 🟢 in last 10 sandbox renders; success_threshold: 0 misuse",
        "rule": "KEEP if misuse drops to 0; DISCARD if visual regression reported",
        "next": "MEASURE baseline misuse → apply grammar rule → re-render → count",
    },
    "prompt_compression": {
        "hypothesis": "Compressing the CORE_PROMPT header reduces token overhead without losing invariant coverage.",
        "tweak": "Remove one redundant 'Read the supplied...' clause from CORE_PROMPT header.",
        "metric": "baseline: token count of CORE_PROMPT; success_threshold: ≥10% reduction, 0 invariant loss",
        "rule": "KEEP if token count drops and all invariants remain detectable; DISCARD if any invariant is dropped",
        "next": "MEASURE baseline token count → apply compression → verify invariant coverage → compare",
    },
    "skill_routing": {
        "hypothesis": "Routing proposals through a single classifier reduces false ADMIT signals.",
        "tweak": "Add one-line PROPOSAL_GATE check before skill_routing emits any ADMIT candidate.",
        "metric": "baseline: count ADMIT signals in last 5 routing outputs; success_threshold: 0 false ADMITs",
        "rule": "KEEP if false ADMIT count drops; DISCARD if valid routing is blocked",
        "next": "MEASURE false ADMITs baseline → add gate → re-route test set → compare",
    },
    "summarization_weights": {
        "hypothesis": "Reweighting summarization toward evidence-density improves recall of receipt references.",
        "tweak": "Increase receipt_reference weight by 0.1 in summarization_weights.",
        "metric": "baseline: receipt references in last 3 summaries; success_threshold: ≥1 receipt per summary",
        "rule": "KEEP if receipt density improves; DISCARD if summary length increases >20%",
        "next": "MEASURE receipt density baseline → adjust weight → re-summarize → compare",
    },
}


# ---------------------------------------------------------------------------
# Loop state I/O
# ---------------------------------------------------------------------------

def _load_loop_state() -> dict:
    if _LOOP_STATE_FILE.exists():
        try:
            return json.loads(_LOOP_STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"schema": "TWO_STAGE_LOOP_STATE_V0", "target_history": []}


def _save_loop_state(state: dict) -> None:
    tmp = _LOOP_STATE_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(_LOOP_STATE_FILE)


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# Anti-loop guard
# ---------------------------------------------------------------------------

def _count_recent_same_target(target: str, state: dict) -> int:
    """Count how many consecutive recent runs targeted the same surface."""
    hist = state.get("target_history", [])
    count = 0
    for entry in reversed(hist[-ANTI_LOOP_THRESHOLD:]):
        if entry.get("target") == target:
            count += 1
        else:
            break
    return count


def _has_new_evidence(target: str, current_rankings: dict, state: dict) -> bool:
    """True if the packet's observed ranking for this target differs from last run."""
    hist = state.get("target_history", [])
    for entry in reversed(hist):
        if entry.get("target") == target:
            prev_ranking = entry.get("observed_ranking")
            current = current_rankings.get(target)
            if prev_ranking is None and current is None:
                return False
            if prev_ranking != current:
                return True
            return False
    return True  # no prior run for this target → treat as new


# ---------------------------------------------------------------------------
# Trace writer
# ---------------------------------------------------------------------------

def _write_trace(record: dict) -> None:
    _TRACE_DIR.mkdir(parents=True, exist_ok=True)
    with _TRACE_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")


# ---------------------------------------------------------------------------
# Report builder
# ---------------------------------------------------------------------------

def _build_report(
    *,
    target: str,
    template: dict,
    dirty_verdict_summary: str,
    packet_head: str,
    packet_status: str,
    selected_score: float,
    ranked_surfaces: list[str],
    anti_loop_fired: bool,
    no_receipt: bool,
    observed_at: str,
) -> dict:
    """Build the structured experiment report."""
    return {
        "schema": "TWO_STAGE_LOOP_REPORT_V0",
        "authority": False,
        "sovereign": False,
        "canon": False,
        "ledger_effect": "none",
        "reducer_required": True,
        "observed_at": observed_at,
        "packet_head": packet_head,
        "packet_status": packet_status,
        "dirty_verdict": dirty_verdict_summary,
        "anti_loop_fired": anti_loop_fired,
        "no_receipt": no_receipt,
        "selected_surface": target,
        "selected_score": selected_score,
        "ranked_surfaces": ranked_surfaces,
        "TARGET": target,
        "HYPOTHESIS": template.get("hypothesis", ""),
        "TWEAK": template.get("tweak", ""),
        "METRIC": template.get("metric", ""),
        "RULE": template.get("rule", ""),
        "NEXT": template.get("next", "HOLD_FOR_OPERATOR"),
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def run(
    *,
    packet=None,
    packet_data: Optional[dict] = None,
    dry_run: bool = True,
    verbose: bool = False,
) -> dict:
    """Execute the two-stage loop.

    Parameters
    ----------
    packet:
        Pre-built ObservationPacket (takes precedence over packet_data).
        If None, collect() is called for a WITNESSED packet.
    packet_data:
        Raw dict for building a REPORTED packet (used when caller supplies
        externally-collected observations, e.g. from a CI harness).
    dry_run:
        If True, do not persist loop_state.json updates. Trace is always written.
    verbose:
        Print status lines to stdout.

    Returns
    -------
    The structured report dict.
    """
    import observation_packet as op_mod
    import dirty_state as ds_mod
    import surface_ranker as sr_mod

    # ---- STAGE 1: OBSERVE ------------------------------------------------

    if packet is not None:
        pkt = packet
    elif packet_data is not None:
        pkt = op_mod.from_reported(packet_data)
    else:
        pkt = op_mod.collect()

    if verbose:
        print(f"[OBSERVE] head={pkt.head} status={pkt.packet_status} "
              f"outbox={pkt.outbox_unconsumed} replay={pkt.replay_status}")

    # ---- CLASSIFY: dirty-state predicate ---------------------------------

    dirty_verdict = ds_mod.evaluate(pkt)
    dirty_summary = ds_mod.summarize(dirty_verdict)

    if verbose:
        print(f"[CLASSIFY] {dirty_summary}")

    # ---- CHECK DIRTY_DOMINATES -------------------------------------------

    if dirty_verdict.dominates:
        report = {
            "schema": "TWO_STAGE_LOOP_REPORT_V0",
            "authority": False,
            "sovereign": False,
            "canon": False,
            "ledger_effect": "none",
            "reducer_required": True,
            "observed_at": pkt.observed_at,
            "packet_head": pkt.head,
            "packet_status": pkt.packet_status,
            "dirty_verdict": dirty_summary,
            "anti_loop_fired": False,
            "no_receipt": dirty_verdict.no_receipt,
            "selected_surface": "DIRTY_STATE_DECISION_PACKET",
            "selected_score": 0.0,
            "ranked_surfaces": [],
            "TARGET": "DIRTY_STATE_DECISION_PACKET",
            "HYPOTHESIS": "Stale dirt may masquerade as active risk.",
            "TWEAK": "Add last-observed timestamp per dirty item.",
            "METRIC": "Replay-risk ranking changes only with evidence.",
            "RULE": "NO_RECEIPT; timestamps grant zero authority.",
            "NEXT": "HOLD_FOR_OPERATOR",
        }
        _write_trace({**report, "stage": "dirty_halt", "run_at": _utc_now()})
        _print_report(report, verbose=True)
        return report

    if dirty_verdict.no_receipt:
        report = {
            "schema": "TWO_STAGE_LOOP_REPORT_V0",
            "authority": False,
            "sovereign": False,
            "canon": False,
            "ledger_effect": "none",
            "reducer_required": True,
            "observed_at": pkt.observed_at,
            "packet_head": pkt.head,
            "packet_status": pkt.packet_status,
            "dirty_verdict": dirty_summary,
            "anti_loop_fired": False,
            "no_receipt": True,
            "selected_surface": "HOLD_FOR_OPERATOR",
            "selected_score": 0.0,
            "ranked_surfaces": [],
            "TARGET": "HOLD_FOR_OPERATOR",
            "HYPOTHESIS": "Evidence is absent; loop cannot rank without a witnessed baseline.",
            "TWEAK": "None — operator must supply or collect a WITNESSED packet.",
            "METRIC": "N/A",
            "RULE": "NO_RECEIPT — no action until evidence is present.",
            "NEXT": "HOLD_FOR_OPERATOR",
        }
        _write_trace({**report, "stage": "no_receipt_halt", "run_at": _utc_now()})
        _print_report(report, verbose=True)
        return report

    # ---- RANK ALLOWED SURFACES -------------------------------------------

    state = _load_loop_state()
    recent_targets = [h.get("target", "") for h in state.get("target_history", [])[-3:]]
    recent_targets.reverse()

    ranking = sr_mod.rank(
        pkt.rankings,
        anti_loop_targets=recent_targets,
    )
    selected = ranking.selected
    ranked_names = [s.surface for s in ranking.ranked]

    if verbose:
        print(f"[RANK] top={selected} score={ranking.selected_score:.3f} "
              f"all={ranked_names}")

    # ---- CHECK ANTI-LOOP -------------------------------------------------

    same_count = _count_recent_same_target(selected, state)
    new_ev = _has_new_evidence(selected, pkt.rankings, state)

    anti_loop_fired = same_count >= ANTI_LOOP_THRESHOLD and not new_ev

    if anti_loop_fired:
        report = {
            "schema": "TWO_STAGE_LOOP_REPORT_V0",
            "authority": False,
            "sovereign": False,
            "canon": False,
            "ledger_effect": "none",
            "reducer_required": True,
            "observed_at": pkt.observed_at,
            "packet_head": pkt.head,
            "packet_status": pkt.packet_status,
            "dirty_verdict": dirty_summary,
            "anti_loop_fired": True,
            "no_receipt": False,
            "selected_surface": "HOLD_FOR_OPERATOR",
            "selected_score": ranking.selected_score,
            "ranked_surfaces": ranked_names,
            "TARGET": "HOLD_FOR_OPERATOR",
            "HYPOTHESIS": (
                f"Loop repeated '{selected}' {same_count}x without new evidence — "
                "anti-loop guard triggered."
            ),
            "TWEAK": "None — new evidence required before next run.",
            "METRIC": "N/A",
            "RULE": f"same_target_count={same_count} >= {ANTI_LOOP_THRESHOLD} and not new_evidence.",
            "NEXT": "HOLD_FOR_OPERATOR",
        }
        _write_trace({**report, "stage": "anti_loop_halt", "run_at": _utc_now()})
        _print_report(report, verbose=True)
        return report

    # ---- PLAN ONE REVERSIBLE TWEAK ---------------------------------------

    template = _EXPERIMENT_TEMPLATES.get(selected, {
        "hypothesis": f"Tweak {selected} to improve salience in non-sovereign layer.",
        "tweak": f"Make exactly one small, reversible change to {selected}.",
        "metric": "baseline: current output quality score; success_threshold: measurable improvement",
        "rule": "KEEP if metric improves; DISCARD if any sovereign path is touched",
        "next": "MEASURE baseline → apply tweak → re-observe → compare",
    })

    report = _build_report(
        target=selected,
        template=template,
        dirty_verdict_summary=dirty_summary,
        packet_head=pkt.head,
        packet_status=pkt.packet_status,
        selected_score=ranking.selected_score,
        ranked_surfaces=ranked_names,
        anti_loop_fired=False,
        no_receipt=False,
        observed_at=pkt.observed_at,
    )

    # ---- PERSIST STATE (unless dry_run) ----------------------------------

    if not dry_run:
        state.setdefault("target_history", []).append({
            "target": selected,
            "score": ranking.selected_score,
            "observed_ranking": pkt.rankings.get(selected),
            "run_at": _utc_now(),
        })
        _save_loop_state(state)

    # ---- WRITE TRACE (always) --------------------------------------------

    _write_trace({**report, "stage": "experiment_planned", "run_at": _utc_now()})

    # ---- REPORT ----------------------------------------------------------

    _print_report(report, verbose=True)
    return report


def _print_report(report: dict, *, verbose: bool) -> None:
    """Print the six-line operator output."""
    print()
    print(f"TARGET: {report['TARGET']}")
    print(f"HYPOTHESIS: {report['HYPOTHESIS']}")
    print(f"TWEAK: {report['TWEAK']}")
    print(f"METRIC: {report['METRIC']}")
    print(f"RULE: {report['RULE']}")
    print(f"NEXT: {report['NEXT']}")
    if verbose and report.get("dirty_verdict"):
        print(f"\n[dirty_verdict] {report['dirty_verdict']}")
    print()
    print("authority=false · ledger_effect=none · reducer_required=true")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(
        description="Two-stage observe-then-experiment autoresearch loop (NON_SOVEREIGN)"
    )
    ap.add_argument(
        "--reported",
        type=Path,
        help="Path to a JSON file containing a pre-collected observation packet "
             "(builds REPORTED packet; bypasses local git reads)",
    )
    ap.add_argument(
        "--write-state",
        action="store_true",
        default=False,
        help="Persist loop_state.json after a successful experiment plan "
             "(default: dry-run, state not written)",
    )
    ap.add_argument("--verbose", action="store_true", default=False)
    a = ap.parse_args()

    packet_data = None
    if a.reported:
        try:
            packet_data = json.loads(Path(a.reported).read_text(encoding="utf-8"))
        except Exception as exc:
            print(f"ERROR: cannot read reported packet: {exc}", file=sys.stderr)
            return 1

    run(
        packet_data=packet_data,
        dry_run=not a.write_state,
        verbose=a.verbose,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
