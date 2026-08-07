"""J1_MEETING_BRIEF_V0 — day-minus-one meeting brief as a governed projection.

Pipeline: Calendar J+1 -> external participants -> person resolution ->
latest Gmail exchanges -> linked Drive documents -> open questions ->
contradictions -> sourced brief (max 15 lines).

Mandatory laws (violations raise, they never degrade silently):
  - no factual statement without a source_ref
  - no unresolved name presented as certain (person_id or AMBIGUOUS/UNKNOWN)
  - no event absent from Calendar presented as confirmed
  - no draft presented as sent; no external action of any kind
  - every retrieved trace disposed (reuses governed_context_packet.reconcile)
  - deterministic: same inputs -> same brief_hash

Posture: authority=false, canon=false, ledger_effect=none,
claim_status=LOCAL_OBSERVATION. The brief is a private JM draft — never an
admitted memory, never an auto-shared document.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))

from governed_context_packet import (  # noqa: E402
    canonical_json, reconcile, resolve_entity,
)

BRIEF_TYPE = "J1_MEETING_BRIEF_V0"
QUESTION_STATUS = {"OPEN", "UNCERTAIN"}
MAX_LINES = 15


class BriefError(Exception):
    """Raised when a brief law is violated at build or render time."""


def _require_sourced(item: Dict[str, Any], what: str) -> None:
    if not item.get("source_ref") and not item.get("source_refs"):
        raise BriefError(f"unsourced factual statement in {what}: {item}")


def resolve_participants(participants: List[Dict[str, Any]],
                         registry: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Every participant ends CONFIRMED (with person_id), AMBIGUOUS
    (candidates listed) or UNKNOWN — never a silent guess."""
    out = []
    for p in participants:
        _require_sourced(p, "participant")
        trace = {"sender": p.get("email", ""),
                 "names_mentioned": p.get("names", [])}
        binding = resolve_entity(trace, registry)
        out.append({
            "display": p.get("display") or p.get("email") or "?",
            "person_id": binding.get("entity_id"),
            "resolution_status": binding["status"],
            "candidates": binding.get("candidates", []),
            "source_ref": p["source_ref"],
        })
    return out


def build_j1_brief(event: Dict[str, Any],
                   participants: List[Dict[str, Any]],
                   registry: List[Dict[str, Any]],
                   scanned_ids: List[str],
                   dispositions: List[Dict[str, Any]],
                   latest_exchanges: Optional[List[Dict[str, Any]]] = None,
                   unresolved_questions: Optional[List[Dict[str, Any]]] = None,
                   documents_to_review: Optional[List[Dict[str, Any]]] = None,
                   contradictions: Optional[List[Dict[str, Any]]] = None,
                   unknowns: Optional[List[str]] = None) -> Dict[str, Any]:
    """Assemble and validate a J1_MEETING_BRIEF_V0. Read-only by
    construction: the brief has no action field at all."""
    latest_exchanges = latest_exchanges or []
    unresolved_questions = unresolved_questions or []
    documents_to_review = documents_to_review or []
    contradictions = contradictions or []
    unknowns = unknowns or []

    # law: event observed vs reported is an explicit, sourced axis
    if "observed_in_calendar" not in event:
        raise BriefError("event must declare observed_in_calendar")
    _require_sourced(event, "event")

    # law: every retrieved trace received exactly one disposition
    recon = reconcile(scanned_ids, dispositions)
    if not recon["balanced"]:
        raise BriefError(
            f"disposition reconciliation failed: "
            f"undisposed={recon['undisposed_ids']} errors={recon['errors']}")

    # law: everything factual carries its source
    for x in latest_exchanges:
        _require_sourced(x, "latest_exchanges")
    for q in unresolved_questions:
        _require_sourced(q, "unresolved_questions")
        if q.get("status") not in QUESTION_STATUS:
            raise BriefError(f"invalid question status: {q.get('status')}")
    for d in documents_to_review:
        if not d.get("drive_ref"):
            raise BriefError(f"document without drive_ref: {d}")
    for c in contradictions:
        _require_sourced(c, "contradictions")

    resolved = resolve_participants(participants, registry)

    brief: Dict[str, Any] = {
        "type": BRIEF_TYPE,
        "event": {
            "title": event["title"],
            "start": event.get("start"),
            "observed_in_calendar": event["observed_in_calendar"],
            "source_ref": event["source_ref"],
            "epistemic_status": ("OBSERVED" if event["observed_in_calendar"]
                                 else "REPORTED"),
        },
        "participants": resolved,
        "latest_exchanges": latest_exchanges,
        "unresolved_questions": unresolved_questions,
        "documents_to_review": documents_to_review,
        "contradictions": contradictions,
        "unknowns": unknowns,
        "scan_reconciliation": {k: recon[k] for k in
                                ("scanned", "retained", "dismissed",
                                 "deferred", "duplicate", "undisposed",
                                 "balanced")},
        "authority": False,
        "canon": False,
        "ledger_effect": "none",
        "claim_status": "LOCAL_OBSERVATION",
        "distribution": "JM_PRIVATE_DRAFT",
    }
    brief["brief_hash"] = "sha256:" + hashlib.sha256(
        canonical_json(brief).encode("utf-8")).hexdigest()
    return brief


def _participant_tag(p: Dict[str, Any]) -> str:
    if p["resolution_status"] == "CONFIRMED":
        return f"{p['display']} [{p['person_id']}]"
    if p["resolution_status"] == "AMBIGUOUS":
        return f"{p['display']} [AMBIGUOUS: {'/'.join(p['candidates'])}]"
    return f"{p['display']} [UNKNOWN]"


def render_brief(brief: Dict[str, Any]) -> str:
    """Max 15 lines, every factual line cites its source. Raises rather
    than trimming: hiding a contradiction to fit the budget is forbidden."""
    e = brief["event"]
    lines: List[str] = []
    if e["observed_in_calendar"]:
        lines.append(f"RDV {e['title']} — {e['start']} "
                     f"[OBSERVÉ Calendar: {e['source_ref']}]")
    else:
        lines.append(f"RDV {e['title']} — {e['start']} "
                     f"[RAPPORTÉ ({e['source_ref']}) — aucun événement "
                     f"observé dans Calendar]")
    lines.append("Participants: " + "; ".join(
        _participant_tag(p) for p in brief["participants"]))

    for x in brief["latest_exchanges"]:
        lines.append(f"Échange {x['date']} — {x['summary']} ({x['source_ref']})")
    for q in brief["unresolved_questions"]:
        lines.append(f"Question [{q['status']}]: {q['question']} "
                     f"({q['source_ref']})")
    for d in brief["documents_to_review"]:
        lines.append(f"Doc: {d['title']} ({d['drive_ref']}; "
                     f"{d.get('relevance_basis', 'lié')})")
    for c in brief["contradictions"]:
        refs = ",".join(c.get("source_refs", []) or [c.get("source_ref")])
        lines.append(f"CONTRADICTION: {c['statement_a']} ≠ {c['statement_b']} "
                     f"({refs})")
    if brief["unknowns"]:
        lines.append("Inconnues: " + ", ".join(brief["unknowns"]))

    r = brief["scan_reconciliation"]
    lines.append(f"[{brief['brief_hash'][:19]}… · scanned={r['scanned']} "
                 f"retained={r['retained']} balanced={r['balanced']} · "
                 f"privé JM · aucune action]")

    if len(lines) > MAX_LINES:
        raise BriefError(
            f"brief is {len(lines)} lines > {MAX_LINES}: reduce inputs — "
            f"trimming would silently hide sourced facts")
    return "\n".join(lines)
