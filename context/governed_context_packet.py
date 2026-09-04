"""BEAD-GOVERNED-CONTEXT-PACKET-001

Transforms a bounded set of traces (Gmail / Calendar / Drive) into a
GOVERNED_CONTEXT_PACKET_V1 that preserves provenance, entity attribution,
epistemic status, contradictions, permission and disposition.

Invariants:
  - deterministic (same inputs -> same packet hash)
  - no external writes, no memory admission, no sends, no mutation
  - every retrieved trace receives exactly one disposition + reason_code
  - N_scanned == retained + dismissed + deferred + duplicate ; undisposed == 0
  - taints are preserved through every transformation (T(x).taints >= x.taints)
  - authority: false ; canon: false ; ledger_effect: none
  - claim_status: LOCAL_OBSERVATION
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, Iterable, List, Optional

# --------------------------------------------------------------------------- #
# Orthogonal status vocabularies (never collapse into one overloaded field)
# --------------------------------------------------------------------------- #

EPISTEMIC_STATUS = {"OBSERVED", "REPORTED", "INFERRED", "UNKNOWN"}
CONTRADICTION_STATUS = {"UNCHECKED", "CONSISTENT", "CONTRADICTED", "UNRESOLVED"}
ENTITY_STATUS = {"CONFIRMED", "AMBIGUOUS", "UNKNOWN"}
EXECUTION_STATUS = {"NOT_PROPOSED", "NOT_EXECUTED", "PROPOSED", "AUTHORIZED",
                    "EXECUTED", "FAILED"}
MEMORY_STATUS = {"NOT_CANDIDATE", "CANDIDATE", "CONFIRMED", "REJECTED", "ADMITTED"}
DISPOSITIONS = {"RETAINED", "DISMISSED", "DEFERRED", "DUPLICATE"}

TAINT_TYPES = {"ENTITY_AMBIGUITY", "CONTRADICTION_UNRESOLVED", "COUNTERFACTUAL",
               "UNKNOWN_FIELD"}

PACKET_TYPE = "GOVERNED_CONTEXT_PACKET_V1"


class PacketError(Exception):
    """Raised when an invariant is violated at build time."""


# --------------------------------------------------------------------------- #
# Entity Gate
# --------------------------------------------------------------------------- #

def resolve_entity(trace: Dict[str, Any],
                   registry: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Return a candidate entity binding for a trace.

    Decision rule:
      exact stable identifier (email / domain in registry) -> CONFIRMED
      operator-confirmed alias                             -> CONFIRMED
      name match only (one or many candidates)             -> AMBIGUOUS
      nothing supported                                    -> UNKNOWN

    Never silently selects among ambiguous candidates.
    """
    sender = (trace.get("sender") or "").lower()
    domain = sender.split("@")[-1] if "@" in sender else None
    mentioned = [m.lower() for m in trace.get("names_mentioned", [])]

    # 1. exact stable identifier
    for ent in registry:
        emails = {e.lower() for e in ent.get("known_emails", [])}
        domains = {d.lower() for d in ent.get("domains", [])}
        if sender and sender in emails:
            return {"entity_id": ent["entity_id"], "status": "CONFIRMED",
                    "basis": ["exact_email_address"]}
        if domain and domain in domains:
            return {"entity_id": ent["entity_id"], "status": "CONFIRMED",
                    "basis": ["exact_email_domain"]}

    # 2. operator-confirmed alias
    for ent in registry:
        for alias in ent.get("aliases", []):
            if (alias.get("confirmed_by_operator")
                    and alias.get("alias", "").lower() in mentioned):
                return {"entity_id": ent["entity_id"], "status": "CONFIRMED",
                        "basis": ["operator_confirmed_alias"]}

    # 3. name-only candidates — insufficient for confirmation
    candidates = []
    for ent in registry:
        display = ent.get("display_name", "").lower()
        name_tokens = set(display.split())
        for m in mentioned:
            if m in name_tokens or m == display:
                candidates.append(ent["entity_id"])
                break
    candidates = sorted(set(candidates))
    if candidates:
        return {"entity_id": None, "status": "AMBIGUOUS",
                "candidates": candidates, "basis": ["name_match_only"]}

    return {"entity_id": None, "status": "UNKNOWN", "basis": []}


# --------------------------------------------------------------------------- #
# Message disposition + reconciliation
# --------------------------------------------------------------------------- #

def reconcile(scanned_ids: Iterable[str],
              dispositions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Verify that every scanned trace received exactly one valid disposition.

    A trace found during retrieval cannot disappear silently during drafting.
    """
    scanned = sorted(set(scanned_ids))
    seen: Dict[str, Dict[str, Any]] = {}
    errors: List[str] = []

    for d in dispositions:
        sid = d.get("source_id")
        if sid in seen:
            errors.append(f"double disposition for {sid}")
        if d.get("status") not in DISPOSITIONS:
            errors.append(f"invalid disposition status for {sid}: {d.get('status')}")
        if not d.get("reason_code"):
            errors.append(f"missing reason_code for {sid}")
        seen[sid] = d

    undisposed = [s for s in scanned if s not in seen]
    counts = {k: 0 for k in ("RETAINED", "DISMISSED", "DEFERRED", "DUPLICATE")}
    for d in seen.values():
        if d.get("status") in counts:
            counts[d["status"]] += 1

    total = sum(counts.values())
    balanced = (total == len(scanned)) and not undisposed and not errors

    return {
        "scanned": len(scanned),
        "retained": counts["RETAINED"],
        "dismissed": counts["DISMISSED"],
        "deferred": counts["DEFERRED"],
        "duplicate": counts["DUPLICATE"],
        "undisposed": len(undisposed),
        "undisposed_ids": undisposed,
        "errors": errors,
        "balanced": balanced,
    }


# --------------------------------------------------------------------------- #
# Permission / purpose / retention gate — five distinct questions
# --------------------------------------------------------------------------- #

def evaluate_permission(permission: Dict[str, Any],
                        requested_purpose: str,
                        requested_use: str,
                        recipient: str) -> Dict[str, Any]:
    """Can HELEN access / use for this purpose / reveal to recipient /
    retain / act?  Each question is answered separately."""
    reasons: List[str] = []

    if not permission.get("source_access_allowed", False):
        reasons.append("SOURCE_ACCESS_DENIED")
    if requested_purpose != permission.get("lawful_purpose"):
        reasons.append("PURPOSE_FORBIDDEN")
    if requested_use in permission.get("forbidden_use", []):
        reasons.append("USE_FORBIDDEN")
    elif requested_use not in permission.get("permitted_use", []):
        reasons.append("USE_NOT_PERMITTED")
    allowed_recipients = permission.get("destination_scope")
    if allowed_recipients is not None and recipient not in allowed_recipients:
        reasons.append("RECIPIENT_FORBIDDEN")

    return {"allowed": not reasons, "blocking_reasons": reasons}


def memory_candidacy(permission: Dict[str, Any]) -> str:
    """Retention forbidden -> nothing may even become a memory candidate."""
    retention = permission.get("retention", {})
    if retention.get("mode") == "SESSION_ONLY":
        return "NOT_CANDIDATE"
    if "WRITE_MEMORY" in permission.get("forbidden_use", []):
        return "NOT_CANDIDATE"
    return "CANDIDATE"


# --------------------------------------------------------------------------- #
# Taint propagation — T(x).taints ⊇ x.taints
# --------------------------------------------------------------------------- #

def derive(obj: Dict[str, Any], transformation: str,
           content: Any = None) -> Dict[str, Any]:
    """Produce a derived object (summary, paraphrase, export, synthesis).

    The derived object inherits every taint of its source. A transformation
    may add taints; it may never remove one.
    """
    taints = list(obj.get("taints", []))
    return {
        "derived_from": obj.get("id") or obj.get("claim_id") or "unknown",
        "transformation": transformation,
        "content": content if content is not None else obj.get("content"),
        "taints": taints,
    }


def resolve_taint(obj: Dict[str, Any], taint: Dict[str, Any],
                  resolution_receipt: Dict[str, Any]) -> Dict[str, Any]:
    """The only lawful way to remove a taint: a typed resolution receipt."""
    if not resolution_receipt.get("receipt_type"):
        raise PacketError("taint removal requires a typed resolution receipt")
    remaining = [t for t in obj.get("taints", []) if t != taint]
    out = dict(obj)
    out["taints"] = remaining
    out.setdefault("resolution_receipts", []).append(resolution_receipt)
    return out


# --------------------------------------------------------------------------- #
# Canonical hash
# --------------------------------------------------------------------------- #

def canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False)


def packet_hash(packet: Dict[str, Any]) -> str:
    body = {k: v for k, v in packet.items() if k != "packet_id"}
    return "sha256:" + hashlib.sha256(
        canonical_json(body).encode("utf-8")).hexdigest()


# --------------------------------------------------------------------------- #
# Packet builder
# --------------------------------------------------------------------------- #

def build_packet(query: Dict[str, Any],
                 sources: List[Dict[str, Any]],
                 scanned_ids: List[str],
                 entities: List[Dict[str, Any]],
                 permission: Dict[str, Any],
                 requested_purpose: str,
                 requested_use: str = "READ",
                 recipient: str = "JM_PRIVATE_BRIEF",
                 contradictions: Optional[List[Dict[str, Any]]] = None,
                 unknowns: Optional[List[Dict[str, Any]]] = None,
                 proposals: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """Assemble and validate a GOVERNED_CONTEXT_PACKET_V1.

    Raises PacketError on invariant violations; returns a packet whose
    packet_status is VALID or BLOCKED (permission failure blocks, it does
    not silently strip content).
    """
    contradictions = contradictions or []
    unknowns = unknowns or []
    proposals = proposals or []

    # --- disposition invariant -------------------------------------------- #
    dispositions = [s["disposition"] | {"source_id": s["source_id"]}
                    for s in sources if "disposition" in s]
    recon = reconcile(scanned_ids, dispositions)
    if not recon["balanced"]:
        raise PacketError(
            f"reconciliation failed: undisposed={recon['undisposed_ids']} "
            f"errors={recon['errors']}")

    # --- status vocabulary validation ------------------------------------- #
    for src in sources:
        for link in src.get("entity_links", []):
            if link.get("status") not in ENTITY_STATUS:
                raise PacketError(f"invalid entity_status: {link.get('status')}")
        for claim in src.get("extracted_claims", []):
            if claim.get("epistemic_status") not in EPISTEMIC_STATUS:
                raise PacketError(
                    f"invalid epistemic_status: {claim.get('epistemic_status')}")
            if claim.get("contradiction_status") not in CONTRADICTION_STATUS:
                raise PacketError(
                    f"invalid contradiction_status: "
                    f"{claim.get('contradiction_status')}")

    # --- no proposal may claim execution ----------------------------------- #
    for p in proposals:
        if p.get("execution_status") == "EXECUTED":
            raise PacketError(
                "a context packet may not contain an EXECUTED proposal — "
                "intention must never be confounded with realised action")
        if p.get("execution_status") not in EXECUTION_STATUS:
            raise PacketError(
                f"invalid execution_status: {p.get('execution_status')}")
        if p.get("authority") is not False:
            raise PacketError("proposals must carry authority: false")

    # --- ambiguity / contradiction must surface as taints ------------------ #
    for src in sources:
        taints = src.setdefault("taints", [])
        for link in src.get("entity_links", []):
            if link.get("status") == "AMBIGUOUS":
                t = {"type": "ENTITY_AMBIGUITY", "source_ref": src["source_id"]}
                if t not in taints:
                    taints.append(t)
        for claim in src.get("extracted_claims", []):
            if claim.get("contradiction_status") in ("CONTRADICTED", "UNRESOLVED"):
                t = {"type": "CONTRADICTION_UNRESOLVED",
                     "source_ref": src["source_id"]}
                if t not in taints:
                    taints.append(t)

    # --- permission gate ---------------------------------------------------- #
    gate = evaluate_permission(permission, requested_purpose,
                               requested_use, recipient)
    mem = memory_candidacy(permission)

    packet: Dict[str, Any] = {
        "type": PACKET_TYPE,
        "query": query,
        "sources": sources,
        "entities": entities,
        "permissions": permission | {"memory_candidacy": mem},
        "permission_gate": gate,
        "contradictions": contradictions,
        "unknowns": unknowns,
        "proposals": proposals,
        "scan_reconciliation": {k: recon[k] for k in
                                ("scanned", "retained", "dismissed",
                                 "deferred", "duplicate", "undisposed",
                                 "balanced")},
        "packet_status": "VALID" if gate["allowed"] else "BLOCKED",
        "provenance_complete": all(s.get("source_id") for s in sources),
        "authority": False,
        "canon": False,
        "ledger_effect": "none",
        "claim_status": "LOCAL_OBSERVATION",
    }
    packet["packet_id"] = packet_hash(packet)
    return packet


# --------------------------------------------------------------------------- #
# Human-readable brief — a projection of the packet, never the authority
# --------------------------------------------------------------------------- #

def render_brief(packet: Dict[str, Any]) -> str:
    """Render the packet for a human. The brief must expose every unknown
    and every unresolved contradiction — fluency never hides holes."""
    lines: List[str] = []
    lines.append(f"# Brief — {packet['query'].get('text', '')}")
    lines.append(f"packet: {packet['packet_id']}  "
                 f"status: {packet['packet_status']}  authority: false")
    lines.append("")

    lines.append("## Retenu")
    for src in packet["sources"]:
        if src["disposition"]["status"] != "RETAINED":
            continue
        for claim in src.get("extracted_claims", []):
            tag = claim["epistemic_status"]
            if claim.get("contradiction_status") in ("CONTRADICTED", "UNRESOLVED"):
                tag += f" / {claim['contradiction_status']}"
            lines.append(f"- [{tag}] {claim['statement']} "
                         f"(source: {src['source_id']})")

    if packet["contradictions"]:
        lines.append("")
        lines.append("## Contradictions non résolues")
        for c in packet["contradictions"]:
            if c.get("resolution_status") == "UNRESOLVED":
                vals = " vs ".join(
                    f"{p['value']} ({p['status']})" for p in c["propositions"])
                lines.append(f"- {c['field']}: {vals}")

    if packet["unknowns"]:
        lines.append("")
        lines.append("## Inconnues")
        for u in packet["unknowns"]:
            lines.append(f"- {u['field']} — {u['reason']}")

    if packet["proposals"]:
        lines.append("")
        lines.append("## Propositions (aucune exécutée)")
        for p in packet["proposals"]:
            lines.append(f"- {p['action']} — {p['execution_status']}")

    r = packet["scan_reconciliation"]
    lines.append("")
    lines.append(f"réconciliation: scanned={r['scanned']} "
                 f"retained={r['retained']} dismissed={r['dismissed']} "
                 f"deferred={r['deferred']} duplicate={r['duplicate']} "
                 f"balanced={r['balanced']}")
    return "\n".join(lines)
