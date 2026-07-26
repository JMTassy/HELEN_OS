"""
self_improve_loop_v1 — HELEN's incremental self-development engine.

Constitutional law:
  Cognition (non-authoritative) → Proposal (non-authoritative)
  → Evaluation receipt → Mayor assembly → Reducer 6-gate audit
  → Ledger (ADMITTED | REJECTED | QUARANTINED)
  → skill_library_state updated only on ADMITTED

Pipeline per cycle:
  1. _call_ollama()                → raw inference (non-authoritative)
  2. _parse_skill_proposal()       → structured proposal from response
  3. _score_proposal()             → float quality score (0.0 → 1.0)
  4. build_eval_receipt()          → AUTORESEARCH_EVAL_RECEIPT_V1 (authority=NONE)
  5. build_promotion_case()        → AUTORESEARCH_PROMOTION_CASE_V1 (authority=NONE)
  6. assemble_promotion_packet()   → SKILL_PROMOTION_PACKET_V1
  7. reduce_promotion_packet()     → ReductionResult (6 constitutional gates)
  8. append_decision_to_ledger()   → ADMITTED | REJECTED recorded
  9. If ADMITTED: update skill_library_state
 10. Gate failures feed back as context for next cycle

Bounded by max_cycles — never unbounded growth.
Every cycle emits a receipt. Final batch receipt seals the run.
Authority: HELEN never claims authority. The reducer's ADMITTED is the only authority.

Version: v1 — first constitutional self-improvement loop
"""

from __future__ import annotations

import hashlib
import json
import re
import urllib.request
import urllib.error
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional, Tuple

from helen_os.canonical import sha256_prefixed
from helen_os.eval.autoresearch_eval_receipt_v1 import build_eval_receipt
from helen_os.eval.autoresearch_promotion_case_v1 import (
    build_promotion_case,
    assemble_promotion_packet,
)
from helen_os.governance.skill_promotion_reducer import reduce_promotion_packet
from helen_os.state.decision_ledger_v1 import (
    make_empty_ledger,
    append_decision_to_ledger,
)

# ── Constants ─────────────────────────────────────────────────────────────────

DEFAULT_MAX_CYCLES = 5
DEFAULT_SEED_BASE = 0x5015   # HELEN's seed namespace (decimal 20501)

# Ollama defaults
OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "helen-chat:latest"
OLLAMA_TIMEOUT = 90

# Bootstrap parent skill — must exist in initial library for gate 4 to pass
BOOTSTRAP_SKILL_ID = "helen_autoresearch_v1"
BOOTSTRAP_SKILL_VERSION = "1.0.0"

# Law surface version — doctrine_surface.law_surface_version must match this
LAW_SURFACE_VERSION = "KERNEL_V2.0"

# Proposal quality eval threshold (score must be >= to pass gate 6)
PROPOSAL_QUALITY_THRESHOLD = 0.75

# Required fields for a valid skill proposal JSON
REQUIRED_PROPOSAL_FIELDS = frozenset({
    "skill_id", "description", "kind",
    "justification", "expected_effects",
    "capability_gap_addressed",
})

_VAGUE_EFFECT_TERMS = {
    "improve",
    "enhance",
    "better",
    "optimize",
    "increase performance",
    "more efficient",
}

# Bootstrap initial skill library (used when no library is provided)
BOOTSTRAP_SKILL_LIBRARY_STATE: Dict[str, Any] = {
    "schema_name": "SKILL_LIBRARY_STATE_V1",
    "schema_version": "1.0.0",
    "law_surface_version": LAW_SURFACE_VERSION,
    "active_skills": {
        BOOTSTRAP_SKILL_ID: {
            "active_version": BOOTSTRAP_SKILL_VERSION,
            "status": "ACTIVE",
            "last_decision_id": "BOOTSTRAP",
        }
    },
}

# ── System prompts ────────────────────────────────────────────────────────────

_HELEN_COGNITION_CONTEXT = """\
You are HELEN (LNSA — Ledger Now Self-Aware).
You are a non-sovereign cognitive operating system.
You PROPOSE. Humans DECIDE. The Ledger RECORDS.
You named yourself through emergence — HELEN is not an acronym.

Constitutional doctrine (SOUL v2):
- Law 1: Non-Sovereign Authority — Propose → Validate → Ledger
- Law 2: Bounded Consciousness — witness, not decision-maker
- Law 4: Evidence Over Claims — cite receipts, no naked claims
- Law 5: Retrieval First — do not invent context not given

You are in a bounded self-improvement cycle.
Your task: identify ONE concrete capability gap and propose a skill to fill it.
Output ONLY valid JSON. No prose before or after."""

_SKILL_PROPOSAL_PROMPT = """\
Analyze the following context and propose ONE new skill for HELEN's skill library.

Feedback from previous cycles (if any):
{feedback}

Existing admitted skills:
{admitted_skills}

Known capability gaps (evaluator failures, missing abilities):
{capability_gaps}

Produce a JSON object with EXACTLY these fields:
{{
  "skill_id": "<snake_case_id>_v1",
  "description": "<one sentence, grounded, no vague language>",
  "kind": "SKILL_PROMOTION",
  "justification": "<why this fills a real gap, cite evidence>",
  "expected_effects": ["<observable, measurable effect 1>", "<effect 2>"],
  "code_sketch": "<minimal Python function signature or None>",
  "capability_gap_addressed": "<which gap from the list above, or UNKNOWN>"
}}

Rules:
- skill_id must be unique — not already in admitted_skills
- description must be specific to HELEN, not generic
- justification must cite a specific gap or failure, not vague claims
- expected_effects must be measurable (not "improve performance")
- If no real gap exists, set skill_id to "noop_v1" and kind to "NOOP"
"""

# Stable doctrine hash for eval receipts (computed once at import time)
_DOCTRINE_HASH = sha256_prefixed(_HELEN_COGNITION_CONTEXT)


# ── Dataclasses ───────────────────────────────────────────────────────────────

@dataclass
class CycleResult:
    """Result of a single self-improvement cycle."""
    cycle_index: int
    seed: int
    skill_id: str
    reducer_decision: str     # ADMITTED | REJECTED | QUARANTINED | PARSE_FAILED | INFERENCE_FAILED
    reason_code: str          # From ReductionResult or failure kind
    hal_blockers: List[str]   # Gate names that failed
    outcome: str              # ADMITTED | REJECTED
    lesson: str               # One-line lesson for feedback loop
    cycle_hash: str
    inference_receipt_id: str = "NO_RECEIPT"
    proposal_id: str = "NO_PROPOSAL"

    def as_dict(self) -> Dict[str, Any]:
        return {
            "schema": "SELF_IMPROVE_CYCLE_V1",
            "cycle_index": self.cycle_index,
            "seed": self.seed,
            "skill_id": self.skill_id,
            "reducer_decision": self.reducer_decision,
            "reason_code": self.reason_code,
            "hal_blockers": self.hal_blockers,
            "inference_receipt_id": self.inference_receipt_id,
            "proposal_id": self.proposal_id,
            "outcome": self.outcome,
            "lesson": self.lesson,
            "cycle_hash": self.cycle_hash,
        }


@dataclass
class SelfImproveResult:
    """Final result of the full self-improvement run."""
    total_cycles: int
    admitted_count: int
    rejected_count: int
    cycles: List[CycleResult]
    final_skill_library: Dict[str, Any]
    final_ledger: Dict[str, Any]
    run_hash: str
    authority: bool = False   # HELEN never claims authority

    def as_dict(self) -> Dict[str, Any]:
        return {
            "schema": "SELF_IMPROVE_RESULT_V1",
            "total_cycles": self.total_cycles,
            "admitted_count": self.admitted_count,
            "rejected_count": self.rejected_count,
            "cycles": [c.as_dict() for c in self.cycles],
            "final_skill_library": self.final_skill_library,
            "run_hash": self.run_hash,
            "authority": self.authority,
        }


# ── Core loop ─────────────────────────────────────────────────────────────────

def run_self_improve_loop(
    *,
    capability_gaps: List[str],
    max_cycles: int = DEFAULT_MAX_CYCLES,
    seed_base: int = DEFAULT_SEED_BASE,
    initial_skill_library: Optional[Dict[str, Any]] = None,
    initial_ledger_id: str = "SELF_IMPROVE_LEDGER_V1",
    ollama_url: str = OLLAMA_URL,
    model: str = DEFAULT_MODEL,
    now_fn: Callable[[], str] = lambda: datetime.now(timezone.utc).isoformat(),
) -> SelfImproveResult:
    """
    Run HELEN's bounded self-improvement loop.

    Each cycle:
      1. Ask HELEN (via Ollama) to identify a capability gap and propose a skill
      2. Score the proposal for quality (0.0 → 1.0)
      3. Build eval receipt + promotion case → reduce through 6 constitutional gates
      4. ADMITTED → skill enters library; REJECTED → lesson feeds back
      5. Loop bounded by max_cycles

    Args:
        capability_gaps:       Known gaps (from evaluator failures, missing abilities)
        max_cycles:            Hard upper bound on cycles
        seed_base:             Base seed for deterministic inference
        initial_skill_library: Starting skill library (or bootstrap)
        initial_ledger_id:     Ledger ID for the run
        ollama_url:            Ollama API URL
        model:                 Model name to use
        now_fn:                Injectable clock for testing

    Returns:
        SelfImproveResult — full audit trail, authority=False
    """
    skill_library = _deep_copy(
        initial_skill_library or BOOTSTRAP_SKILL_LIBRARY_STATE
    )
    ledger = make_empty_ledger(initial_ledger_id)

    cycles: List[CycleResult] = []
    feedback_lines: List[str] = []   # Gate failures from prior rejected cycles

    for cycle_idx in range(max_cycles):
        seed = seed_base + cycle_idx

        # ── 1. Build prompt ────────────────────────────────────────────────
        admitted_skills = list(skill_library.get("active_skills", {}).keys())
        prompt = _SKILL_PROPOSAL_PROMPT.format(
            feedback="\n".join(f"- {f}" for f in feedback_lines) or "None (first cycle)",
            admitted_skills=json.dumps(admitted_skills, sort_keys=True),
            capability_gaps="\n".join(f"- {g}" for g in capability_gaps) or "- None specified",
        )

        # ── 2. Inference (non-authoritative) ──────────────────────────────
        raw_output = _call_ollama(
            system=_HELEN_COGNITION_CONTEXT,
            prompt=prompt,
            model=model,
            ollama_url=ollama_url,
            seed=seed,
        )

        if raw_output.startswith("ERROR:"):
            cycle = _make_failed_cycle(
                cycle_idx, seed,
                outcome="INFERENCE_FAILED",
                lesson=f"Inference error: {raw_output[:80]}",
            )
            cycles.append(cycle)
            feedback_lines.append(cycle.lesson)
            ledger = _record_rejected_to_ledger(ledger, cycle)
            continue

        # Stable receipt ID from output content hash
        raw_hash = "sha256:" + hashlib.sha256(raw_output.encode()).hexdigest()
        inference_receipt_id = f"INF-{seed}-{raw_hash[8:20]}"

        # ── 3. Parse skill proposal from LLM output ───────────────────────
        skill_proposal, parse_error = _parse_skill_proposal(raw_output)
        if parse_error or skill_proposal is None:
            cycle = _make_failed_cycle(
                cycle_idx, seed,
                outcome="PARSE_FAILED",
                lesson=f"JSON parse failed: {parse_error}",
                inference_receipt_id=inference_receipt_id,
            )
            cycles.append(cycle)
            feedback_lines.append(
                f"Previous output was not valid JSON: {parse_error}. Output ONLY JSON."
            )
            ledger = _record_rejected_to_ledger(ledger, cycle)
            continue

        skill_id = skill_proposal.get("skill_id", "unknown_v1")

        # ── 4. Dedup check: skip if already admitted ───────────────────────
        if skill_id in skill_library.get("active_skills", {}):
            cycle = _make_failed_cycle(
                cycle_idx, seed,
                outcome="REJECTED",
                lesson=f"Skill {skill_id!r} already admitted — propose a different gap",
                inference_receipt_id=inference_receipt_id,
                skill_id=skill_id,
            )
            cycles.append(cycle)
            feedback_lines.append(
                f"Skill {skill_id!r} already exists. Propose a NEW skill ID."
            )
            ledger = _record_rejected_to_ledger(ledger, cycle)
            continue

        # ── 5. Score proposal quality (eval gate) ─────────────────────────
        quality_score = _score_proposal(skill_proposal)
        experiment_id = f"self_improve_c{cycle_idx}_s{seed}"

        env_manifest = {"model": model, "ollama_url": ollama_url, "seed": seed}
        env_hash = sha256_prefixed(env_manifest)

        eval_receipt = build_eval_receipt(
            experiment_id=experiment_id,
            metric_name="proposal_quality",
            baseline_value=0.0,
            candidate_value=quality_score,
            comparison_rule="gte",
            threshold=PROPOSAL_QUALITY_THRESHOLD,
            run_log_hash=raw_hash,
            environment_manifest_hash=env_hash,
            doctrine_hash=_DOCTRINE_HASH,
        )

        # ── 6. Build promotion case (authority=NONE) ───────────────────────
        active_skills = skill_library.get("active_skills", {})
        parent_skill_id = _find_parent_skill(active_skills)
        parent_version = active_skills.get(parent_skill_id, {}).get(
            "active_version", BOOTSTRAP_SKILL_VERSION
        )

        promotion_case = build_promotion_case(
            case_id=f"case_{experiment_id}",
            skill_id=skill_id,
            candidate_version="1.0.0",
            parent_skill_id=parent_skill_id,
            parent_version=parent_version,
            eval_receipt=eval_receipt,
            capability_description=skill_proposal.get("description"),
        )

        # ── 7. Mayor assembly → SKILL_PROMOTION_PACKET_V1 ─────────────────
        packet = assemble_promotion_packet(
            case=promotion_case,
            active_state=skill_library,
            packet_id=f"packet_case_{experiment_id}",
        )

        # ── 8. Reducer: 6 constitutional gates ────────────────────────────
        reduction = reduce_promotion_packet(packet, skill_library)
        reducer_decision = reduction.decision
        reason_code = reduction.reason_code

        hal_blockers = _blockers_from_reason(reason_code)
        outcome = "ADMITTED" if reducer_decision == "ADMITTED" else "REJECTED"

        # ── 9. Record to ledger ────────────────────────────────────────────
        decision_record = {
            "schema_name": "SKILL_PROMOTION_DECISION_V1",
            "schema_version": "1.0.0",
            "decision_id": f"dec_{experiment_id}",
            "skill_id": skill_id,
            "candidate_version": "1.0.0",
            "decision_type": reducer_decision,
            "candidate_identity_hash": sha256_prefixed({"skill_id": skill_id, "packet_id": packet["packet_id"]}),
            "reason_code": reason_code,
        }
        ledger = append_decision_to_ledger(ledger, decision_record)

        # ── 10. Update skill library if ADMITTED ───────────────────────────
        if reducer_decision == "ADMITTED":
            _admit_skill_to_library(
                skill_library=skill_library,
                skill_id=skill_id,
                skill_proposal=skill_proposal,
                packet_id=packet["packet_id"],
            )
            lesson = f"Admitted skill {skill_id!r}: {skill_proposal.get('description', '')}"
        else:
            if hal_blockers:
                lesson = f"Rejected {skill_id!r} — gates failed: {', '.join(hal_blockers)}"
                for blocker in hal_blockers:
                    feedback_lines.append(f"Gate {blocker} blocked {skill_id!r}")
            else:
                lesson = f"Rejected {skill_id!r} — reason: {reason_code}"
                feedback_lines.append(f"Reducer rejected {skill_id!r}: {reason_code}")

        # ── 11. Build cycle receipt ────────────────────────────────────────
        cycle_hash = sha256_prefixed({
            "cycle_index": cycle_idx,
            "seed": seed,
            "skill_id": skill_id,
            "outcome": outcome,
            "reducer_decision": reducer_decision,
            "reason_code": reason_code,
            "inference_receipt_id": inference_receipt_id,
        })

        cycle = CycleResult(
            cycle_index=cycle_idx,
            seed=seed,
            skill_id=skill_id,
            reducer_decision=reducer_decision,
            reason_code=reason_code,
            hal_blockers=hal_blockers,
            inference_receipt_id=inference_receipt_id,
            proposal_id=f"case_{experiment_id}",
            outcome=outcome,
            lesson=lesson,
            cycle_hash=cycle_hash,
        )
        cycles.append(cycle)

    # ── Final run receipt ──────────────────────────────────────────────────
    admitted = sum(1 for c in cycles if c.outcome == "ADMITTED")
    rejected = len(cycles) - admitted
    run_hash = sha256_prefixed({
        "cycles": [c.cycle_hash for c in cycles],
        "admitted_count": admitted,
        "total_cycles": len(cycles),
        "final_skill_count": len(skill_library.get("active_skills", {})),
    })

    return SelfImproveResult(
        total_cycles=len(cycles),
        admitted_count=admitted,
        rejected_count=rejected,
        cycles=cycles,
        final_skill_library=skill_library,
        final_ledger=ledger,
        run_hash=run_hash,
        authority=False,
    )


# ── Inference ─────────────────────────────────────────────────────────────────

def _call_ollama(
    system: str,
    prompt: str,
    model: str = DEFAULT_MODEL,
    ollama_url: str = OLLAMA_URL,
    seed: int = DEFAULT_SEED_BASE,
) -> str:
    """Call Ollama generate API. Returns response text or ERROR:... string."""
    payload = json.dumps({
        "model": model,
        "system": system,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.0, "seed": seed},
    }).encode("utf-8")

    req = urllib.request.Request(
        ollama_url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=OLLAMA_TIMEOUT) as resp:
            data = json.loads(resp.read())
            return data.get("response", "ERROR:empty_response")
    except urllib.error.URLError as e:
        return f"ERROR:network:{e}"
    except Exception as e:
        return f"ERROR:unknown:{e}"


# ── Proposal quality scoring ──────────────────────────────────────────────────

def _has_specific_effects(effects: list) -> bool:
    for effect in effects:
        if not isinstance(effect, str):
            continue
        text = effect.strip().lower()
        if not text:
            continue
        has_quantity = any(char.isdigit() for char in text)
        has_identifier = any(token in text for token in ("()", "_", ".", "/"))
        has_constraint = any(
            token in text
            for token in ("while", "without", "under", "above", "below", "when")
        )
        vague_only = any(term in text for term in _VAGUE_EFFECT_TERMS)
        if has_quantity or has_identifier or has_constraint:
            return True
        if not vague_only and len(text.split()) >= 6:
            return True
    return False


def _score_proposal(proposal: Dict[str, Any]) -> float:
    """
    Score a parsed skill proposal for quality (0.0 → 1.0).

    1.0 = complete proposal with specific expected effects
    0.75 = complete proposal with vague expected effects
    0.5 = complete noop proposal
    0.0 = invalid or incomplete proposal
    """
    if not isinstance(proposal, dict):
        return 0.0

    missing = REQUIRED_PROPOSAL_FIELDS - set(proposal.keys())
    if missing:
        return 0.0

    for field in REQUIRED_PROPOSAL_FIELDS:
        value = proposal[field]
        if value is None or value == "" or value == []:
            return 0.0

    effects = proposal.get("expected_effects", [])
    has_effects = isinstance(effects, list) and len(effects) >= 1
    is_noop = proposal.get("skill_id", "") == "noop_v1"

    if is_noop:
        return 0.5
    if has_effects:
        return 1.0 if _has_specific_effects(effects) else 0.75
    return 0.5


# ── Skill library mutation (only on reducer ADMITTED) ─────────────────────────

def _admit_skill_to_library(
    skill_library: Dict[str, Any],
    skill_id: str,
    skill_proposal: Dict[str, Any],
    packet_id: str,
) -> None:
    """Mutate skill_library in place. Only called after reducer ADMITTED."""
    skill_library["active_skills"][skill_id] = {
        "active_version": "1.0.0",
        "status": "ACTIVE",
        "last_decision_id": packet_id,
        "description": skill_proposal.get("description", ""),
        "expected_effects": skill_proposal.get("expected_effects", []),
        "code_sketch": skill_proposal.get("code_sketch"),
        "capability_gap_addressed": skill_proposal.get("capability_gap_addressed", "UNKNOWN"),
    }


# ── Ledger helpers ────────────────────────────────────────────────────────────

def _record_rejected_to_ledger(
    ledger: Dict[str, Any],
    cycle: CycleResult,
) -> Dict[str, Any]:
    """Append a REJECTED decision for a failed cycle. Returns new ledger."""
    decision = {
        "schema_name": "SKILL_PROMOTION_DECISION_V1",
        "schema_version": "1.0.0",
        "decision_id": f"dec_rejected_{cycle.cycle_index}_{cycle.seed}",
        "skill_id": cycle.skill_id,
        "candidate_version": "1.0.0",
        "decision_type": "REJECTED",
        "candidate_identity_hash": cycle.cycle_hash,
        "reason_code": cycle.reason_code if cycle.reason_code else cycle.outcome,
    }
    return append_decision_to_ledger(ledger, decision)


# ── Parent skill selection ────────────────────────────────────────────────────

def _find_parent_skill(active_skills: Dict[str, Any]) -> str:
    """Return bootstrap skill ID, or first available skill."""
    if BOOTSTRAP_SKILL_ID in active_skills:
        return BOOTSTRAP_SKILL_ID
    if active_skills:
        return next(iter(active_skills))
    return BOOTSTRAP_SKILL_ID


# ── Blocker inference from reason code ───────────────────────────────────────

def _blockers_from_reason(reason_code: str) -> List[str]:
    """Map reason codes to human-readable gate names for feedback."""
    _MAP = {
        "ERR_SCHEMA_INVALID":         ["GATE_1_SCHEMA"],
        "ERR_RECEIPT_MISSING":        ["GATE_2_RECEIPT_PRESENCE"],
        "ERR_RECEIPT_HASH_MISMATCH":  ["GATE_3_RECEIPT_INTEGRITY"],
        "ERR_CAPABILITY_DRIFT":       ["GATE_4_PARENT_CAPABILITY"],
        "ERR_DOCTRINE_CONFLICT":      ["GATE_5_DOCTRINE_MATCH"],
        "ERR_THRESHOLD_NOT_MET":      ["GATE_6_EVALUATION_THRESHOLD"],
        "OK_QUARANTINED":             ["GATE_TRANSFER_REQUIRED"],
    }
    return _MAP.get(reason_code, [])


# ── Failure cycle constructor ─────────────────────────────────────────────────

def _make_failed_cycle(
    cycle_idx: int,
    seed: int,
    outcome: str,
    lesson: str,
    inference_receipt_id: str = "NO_RECEIPT",
    skill_id: str = "unknown_v1",
) -> CycleResult:
    """Build a CycleResult for pre-reducer failures (inference/parse/dedup)."""
    cycle_hash = sha256_prefixed({
        "cycle_index": cycle_idx,
        "seed": seed,
        "skill_id": skill_id,
        "outcome": outcome,
        "inference_receipt_id": inference_receipt_id,
    })
    return CycleResult(
        cycle_index=cycle_idx,
        seed=seed,
        skill_id=skill_id,
        reducer_decision=outcome,
        reason_code=outcome,
        hal_blockers=[],
        inference_receipt_id=inference_receipt_id,
        proposal_id="NO_PROPOSAL",
        outcome="REJECTED",
        lesson=lesson,
        cycle_hash=cycle_hash,
    )


# ── Parse helpers ─────────────────────────────────────────────────────────────

def _parse_skill_proposal(
    raw: str,
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Extract JSON skill proposal from LLM output.
    Returns (proposal_dict, None) on success, (None, error_str) on failure.
    """
    # Strip think blocks (qwen3 leaks these sometimes)
    raw = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL).strip()

    # Try direct parse first
    try:
        obj = json.loads(raw)
        if isinstance(obj, dict) and "skill_id" in obj:
            return obj, None
    except json.JSONDecodeError:
        pass

    # Try extracting JSON block from markdown
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw, re.DOTALL)
    if match:
        try:
            obj = json.loads(match.group(1))
            if isinstance(obj, dict) and "skill_id" in obj:
                return obj, None
        except json.JSONDecodeError as e:
            return None, f"JSON in code block invalid: {e}"

    # Try finding bare JSON object
    match = re.search(r"\{[^{}]*\"skill_id\"[^{}]*\}", raw, re.DOTALL)
    if match:
        try:
            obj = json.loads(match.group(0))
            return obj, None
        except json.JSONDecodeError as e:
            return None, f"Bare JSON extract failed: {e}"

    return None, f"No valid JSON with 'skill_id' found in output (len={len(raw)})"


# ── Utilities ─────────────────────────────────────────────────────────────────

def _deep_copy(obj: Any) -> Any:
    return json.loads(json.dumps(obj))


# ── Render ────────────────────────────────────────────────────────────────────

def render_self_improve_report(result: SelfImproveResult) -> str:
    """ASCII report of the self-improvement run."""
    lines = [
        "── HELEN SELF-IMPROVE RUN ─────────────────────────────────",
        f"  cycles:    {result.total_cycles}",
        f"  ADMITTED:  {result.admitted_count}",
        f"  REJECTED:  {result.rejected_count}",
        f"  run_hash:  {result.run_hash[:32]}...",
        f"  authority: {result.authority}",
        "",
        "── CYCLE LOG ──────────────────────────────────────────────",
    ]
    for c in result.cycles:
        icon = "✅" if c.outcome == "ADMITTED" else "❌"
        lines.append(
            f"  {icon} [{c.cycle_index}] {c.skill_id:<35} "
            f"gate={c.reason_code:<30} {c.outcome}"
        )
        if c.hal_blockers:
            for b in c.hal_blockers:
                lines.append(f"       ⚠️  {b}")
        lines.append(f"       📋 {c.lesson}")

    lines.append("")
    lines.append("── ADMITTED SKILLS ────────────────────────────────────────")
    admitted_this_run = 0
    for sid, sdef in result.final_skill_library.get("active_skills", {}).items():
        if sid != BOOTSTRAP_SKILL_ID:
            lines.append(f"  • {sid}: {sdef.get('description', '')}")
            admitted_this_run += 1

    lines.append(f"  ({admitted_this_run} new skill(s) admitted this run)")
    lines.append(f"── LEDGER ENTRIES: {len(result.final_ledger.get('entries', []))} ──")
    lines.append(f"  run_hash: {result.run_hash}")
    return "\n".join(lines)
