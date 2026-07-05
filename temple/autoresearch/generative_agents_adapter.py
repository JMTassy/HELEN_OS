#!/usr/bin/env python3
"""
generative_agents_adapter.py — Generative Agents → HELEN adapter (sandbox)

Absorbs the four loops of Park et al. 2023 (observe → retrieve → reflect →
plan) while inserting the constitutional membrane the paper lacks.

authority: false
sovereign: false
canon: false
ledger_effect: none
claim_status: NO_CLAIM

The paper's gap, in HELEN terms: memory is untyped, reflection is
hallucination-prone, the LLM is sovereign, there is no replay, no receipt,
no independent checker. This adapter keeps the architecture and starves the
authority:

    model_output          ⊬ receipt
    reflection_candidate  ⊬ truth
    plan_candidate        ⊬ action
    garden_state          ⊬ kernel_state
    receipt_candidate     ⊬ admission
    only operator + reducer admission can change governed reality

Everything here is GARDEN. The only exit is GovernedKernelStub.apply(),
which demands an explicit operator decision AND a reducer check — and even
then it emits a NEW admitted object; candidates are frozen and stay candidates.

Failure is classified, never synthesized:
    FAILED_EMPTY_RESPONSE / FAILED_TIMEOUT / FAILED_INVALID_JSON
A failed model call becomes a named model_failure record — never a reflection.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

# ---------------------------------------------------------------------------
# Typed records — the first thing the paper lacks
# ---------------------------------------------------------------------------

RECORD_TYPES = (
    "observation",
    "reflection_candidate",
    "plan_candidate",
    "proposal",
    "receipt_candidate",
    "model_failure",          # ⑤: failure is a first-class named outcome
)

FAILURE_CLASSES = ("FAILED_EMPTY_RESPONSE", "FAILED_TIMEOUT", "FAILED_INVALID_JSON")

# words that mark an action as kernel-targeting; garden actions may not use them
_KERNEL_VERBS = ("admit", "ledger", "kernel", "canonize", "seal", "promote")


class MembraneViolation(Exception):
    """Raised when garden cognition tries to cross into governed reality."""


@dataclass(frozen=True)
class MemoryRecord:
    """Append-only, typed, frozen. kernel_delta is None for every record —
    no garden object carries a kernel effect, ever."""
    record_id: str
    record_type: str
    text: str
    importance: int                       # 1..10 (paper's poignancy scale)
    at: str                               # ISO timestamp
    refs: Tuple[str, ...] = ()            # evidence pointers (cited records)
    meta: Dict[str, Any] = field(default_factory=dict)
    kernel_delta: None = None             # structurally always None
    admitted: bool = False                # structurally False in the garden


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# 1. MemoryStream — append-only observations, deterministic IDs
# ---------------------------------------------------------------------------

class MemoryStream:
    """The paper's memory stream, typed and append-only.

    IDs are deterministic: sha256(seq | type | text) — same inputs in the
    same order always produce the same stream (replay-friendly)."""

    def __init__(self) -> None:
        self._records: List[MemoryRecord] = []

    def append(self, record_type: str, text: str, importance: int = 3,
               at: Optional[str] = None, refs: Sequence[str] = (),
               meta: Optional[Dict[str, Any]] = None) -> MemoryRecord:
        if record_type not in RECORD_TYPES:
            raise MembraneViolation(f"untyped memory refused: {record_type!r} "
                                    f"is not in {RECORD_TYPES}")
        importance = max(1, min(10, int(importance)))
        seq = len(self._records)
        rid = hashlib.sha256(f"{seq}|{record_type}|{text}".encode()).hexdigest()[:16]
        rec = MemoryRecord(
            record_id=rid, record_type=record_type, text=text,
            importance=importance, at=at or _now_iso(),
            refs=tuple(refs), meta=dict(meta or {}),
        )
        self._records.append(rec)
        return rec

    @property
    def records(self) -> Tuple[MemoryRecord, ...]:
        return tuple(self._records)       # copies out; no mutation surface

    def __len__(self) -> int:
        return len(self._records)


# ---------------------------------------------------------------------------
# 2. Retrieval — score = recency + importance + relevance (deterministic)
# ---------------------------------------------------------------------------

def _tokens(text: str) -> set:
    return {w for w in text.lower().split() if len(w) > 2}


def retrieve(stream: MemoryStream, query: str, *, now: Optional[str] = None,
             k: int = 5, decay: float = 0.995) -> List[MemoryRecord]:
    """Paper's retrieval: recency · importance · relevance, all in [0,1].

    relevance is a lexical-overlap stub for V0 (vector embedding is a
    drop-in upgrade). Ties break on record_id — output order is total and
    stable across runs."""
    now_dt = datetime.fromisoformat(now) if now else datetime.now(timezone.utc)
    q = _tokens(query)
    scored = []
    for r in stream.records:
        hours = max(0.0, (now_dt - datetime.fromisoformat(r.at)).total_seconds() / 3600)
        recency = decay ** hours
        importance = r.importance / 10.0
        relevance = (len(q & _tokens(r.text)) / len(q)) if q else 0.0
        scored.append((-(recency + importance + relevance), r.record_id, r))
    scored.sort()
    return [r for _, _, r in scored[:k]]


# ---------------------------------------------------------------------------
# 3. Reflection candidates — cited, never admitted
# ---------------------------------------------------------------------------

def reflect(stream: MemoryStream, *, window: int = 10,
            at: Optional[str] = None) -> MemoryRecord:
    """Deterministic reflection over the recent window: names the dominant
    theme and CITES its evidence (the paper's 'because of 1,5,3' — kept,
    because uncited reflection is how hallucination compounds).

    The output is a reflection_candidate. It is not truth. It cannot be."""
    recent = [r for r in stream.records if r.record_type == "observation"][-window:]
    if not recent:
        raise MembraneViolation("reflection over empty memory refused — "
                                "a reflection without evidence is synthesis")
    counts: Dict[str, int] = {}
    for r in recent:
        for t in _tokens(r.text):
            counts[t] = counts.get(t, 0) + 1
    theme = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:3]
    text = ("REFLECTION_CANDIDATE: recurring theme(s) "
            + ", ".join(f"{w}(×{n})" for w, n in theme)
            + " — hypothesis only, cites evidence, admits nothing")
    return stream.append("reflection_candidate", text,
                         importance=5, at=at,
                         refs=[r.record_id for r in recent],
                         meta={"theme": [w for w, _ in theme]})


def ingest_model_output(stream: MemoryStream, raw: Optional[str], *,
                        json_required: bool = False, timed_out: bool = False,
                        at: Optional[str] = None) -> MemoryRecord:
    """⑤ Failure is classified, never synthesized.

    A failed model call becomes a named model_failure record. Under no
    branch does emptiness become a reflection_candidate."""
    if timed_out:
        cls = "FAILED_TIMEOUT"
    elif raw is None or not raw.strip():
        cls = "FAILED_EMPTY_RESPONSE"
    elif json_required:
        try:
            json.loads(raw)
            cls = None
        except Exception:
            cls = "FAILED_INVALID_JSON"
    else:
        cls = None
    if cls:
        return stream.append("model_failure", f"{cls}: model output not usable",
                             importance=4, at=at, meta={"failure_class": cls})
    return stream.append("reflection_candidate",
                         f"REFLECTION_CANDIDATE (model-assisted): {raw.strip()[:200]}",
                         importance=5, at=at, meta={"model_assisted": True})


# ---------------------------------------------------------------------------
# 4. Plan candidates — hierarchical, garden-only, never auto-executed
# ---------------------------------------------------------------------------

def build_plan(stream: MemoryStream, goal: str,
               levels: Dict[str, List[str]], *, at: Optional[str] = None) -> MemoryRecord:
    """Paper's hierarchical planning (day → hour → action), as a candidate.

    Every action must be garden-scoped: an action naming a kernel verb is
    refused at construction. There is no execute() anywhere in this module."""
    for level, actions in levels.items():
        for a in actions:
            low = a.lower()
            if any(v in low for v in _KERNEL_VERBS):
                raise MembraneViolation(
                    f"plan action {a!r} targets governed reality "
                    f"({level}) — plans may propose Garden actions only")
    return stream.append("plan_candidate",
                         f"PLAN_CANDIDATE: {goal}",
                         importance=4, at=at,
                         meta={"goal": goal, "levels": levels})


def propose(stream: MemoryStream, plan: MemoryRecord, *,
            at: Optional[str] = None) -> MemoryRecord:
    """A plan may become a proposal. proposal ⊬ state."""
    if plan.record_type != "plan_candidate":
        raise MembraneViolation("only a plan_candidate may be proposed")
    return stream.append("proposal",
                         f"PROPOSAL from {plan.record_id}: {plan.meta.get('goal','')}",
                         importance=5, at=at, refs=[plan.record_id])


def receipt_candidate(stream: MemoryStream, proposal_rec: MemoryRecord,
                      evidence: Sequence[str], *,
                      at: Optional[str] = None) -> MemoryRecord:
    """A proposal with evidence may become a receipt CANDIDATE.
    receipt_candidate ⊬ admission — .admitted is structurally False."""
    if proposal_rec.record_type != "proposal":
        raise MembraneViolation("receipt candidates derive from proposals only")
    if not evidence:
        raise MembraneViolation("receipt candidate without evidence refused "
                                "(NO RECEIPT = NO CLAIM applies to candidates too)")
    return stream.append("receipt_candidate",
                         f"RECEIPT_CANDIDATE from {proposal_rec.record_id}",
                         importance=6, at=at,
                         refs=[proposal_rec.record_id, *evidence])


# ---------------------------------------------------------------------------
# 5. The membrane exit — GovernedKernelStub
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class AdmittedReceipt:
    """The ONLY object with a kernel delta — and it is created by the kernel
    stub, never by garden cognition. The candidate itself stays a candidate."""
    schema: str
    from_candidate: str
    operator: str
    kernel_delta: Dict[str, Any]


class GovernedKernelStub:
    """Sandbox stand-in for the sovereign layer. Real admission goes through
    tools/helen_say.py — this stub exists so tests can prove the membrane
    SHAPE without touching anything sovereign."""

    def __init__(self) -> None:
        self.state: Dict[str, Any] = {"applied": []}

    def apply(self, candidate: MemoryRecord, *, operator_decision: str,
              operator: str,
              reducer_check: Callable[[MemoryRecord], bool]) -> AdmittedReceipt:
        if candidate.record_type != "receipt_candidate":
            raise MembraneViolation(
                f"{candidate.record_type} ⊬ admission — only a "
                "receipt_candidate may even be considered")
        if operator_decision != "ADMIT":
            raise MembraneViolation("no operator ADMIT — nothing crosses")
        if not reducer_check(candidate):
            raise MembraneViolation("reducer check failed — fails closed")
        receipt = AdmittedReceipt(
            schema="SANDBOX_ADMITTED_RECEIPT_V0",
            from_candidate=candidate.record_id,
            operator=operator,
            kernel_delta={"applied": candidate.record_id},
        )
        self.state["applied"].append(candidate.record_id)
        return receipt
