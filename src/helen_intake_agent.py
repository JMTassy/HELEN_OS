"""
helen_intake_agent.py — Local-first semantic intake bridge for HELEN PULL
NON_SOVEREIGN · NO_SHIP · PROPOSAL
authority: NONE · mutation_rights: NONE · ledger_effect: NONE

Converts raw OS signals (file, mail, media, screen) into admitted CSOs.
Three public functions:

    intake_signal(raw)                  → CSOCandidate
    admit_intake(candidate, receipt)    → AdmissionResult
    project_context(graph, intent)      → CoherenceSlice

Law invariants enforced:
  Law 1 — id = H(namespace || C(payload))         [via cso_identity_contract]
  Law 2 — namespace isolation                      [namespace per signal type]
  Law 3 — immutability via existing_graph check    [via admit_cso]
  Law 4 — provenance chain at intake               [stub chain, receipt required]
  Law 6 — projection is deterministic              [via semantic_object_model]

Timestamps are NOT in canonical payload (Law §TEMPORAL_CONSISTENCY_RULE).
No disk writes. No network calls. No Computer Use dependency.
"""

import hashlib
import mimetypes
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from src.cso_identity_contract import (
    admit_cso,
    law_1_identity_determinism,
    AdmissionResult,
    ADMIT, REJECT, QUARANTINE,
)
from src.semantic_object_model import (
    CSO, SemanticGraph,
    project, RetrievalPolicy,
)


# ── Signal types ──────────────────────────────────────────────────────────────

SIGNAL_FILE   = "FILE"
SIGNAL_MAIL   = "MAIL"
SIGNAL_MEDIA  = "MEDIA"
SIGNAL_SCREEN = "SCREEN"

NAMESPACE_FILE   = "files"
NAMESPACE_MAIL   = "mail"
NAMESPACE_MEDIA  = "media"
NAMESPACE_SCREEN = "screen"

_TYPE_TO_NAMESPACE = {
    SIGNAL_FILE:   NAMESPACE_FILE,
    SIGNAL_MAIL:   NAMESPACE_MAIL,
    SIGNAL_MEDIA:  NAMESPACE_MEDIA,
    SIGNAL_SCREEN: NAMESPACE_SCREEN,
}

# Extensions → SIGNAL type
_MEDIA_EXTENSIONS = {
    ".mp4", ".mov", ".avi", ".mkv", ".webm",
    ".mp3", ".wav", ".flac", ".aac", ".ogg",
    ".jpg", ".jpeg", ".png", ".gif", ".webp", ".tiff",
}
_MAIL_EXTENSIONS = {".eml", ".msg"}


# ── CSOCandidate (pre-admission, no receipt yet) ──────────────────────────────

@dataclass
class CSOCandidate:
    signal_type: str      # FILE | MAIL | MEDIA | SCREEN
    namespace: str
    local_id: str         # content-addressed: H(namespace || C(payload))
    cso_type: str         # fine-grained: FILE_PDF, MAIL_THREAD, MEDIA_VIDEO, …
    payload: dict         # canonical fields only, NO timestamps
    provenance_stub: dict = field(default_factory=dict)
    raw_hint: str = ""    # non-canonical metadata for operator display only

    @property
    def global_id(self) -> str:
        return f"{self.namespace}/{self.local_id}"


@dataclass
class CoherenceSlice:
    """Minimum sufficient state for a query intent."""
    intent: dict
    node_count: int
    nodes: dict           # global_id → {type, hash, relations, authority}
    graph_hash: str
    namespace_filter: Optional[str]
    depth_bound: int


# ── Classifiers ───────────────────────────────────────────────────────────────

def _classify_file(path_str: str) -> tuple[str, dict]:
    """Returns (cso_type, payload) for a file path. No disk read required."""
    p = Path(path_str)
    ext = p.suffix.lower()
    name = p.name

    if ext in _MEDIA_EXTENSIONS:
        mime, _ = mimetypes.guess_type(path_str)
        cso_type = "MEDIA_IMAGE" if ext in {".jpg", ".jpeg", ".png", ".gif", ".webp", ".tiff"} \
                   else "MEDIA_AUDIO" if ext in {".mp3", ".wav", ".flac", ".aac", ".ogg"} \
                   else "MEDIA_VIDEO"
        payload = {
            "name": name,
            "extension": ext,
            "mime_type": mime or "application/octet-stream",
            "signal": SIGNAL_MEDIA,
        }
        return cso_type, payload

    if ext in _MAIL_EXTENSIONS:
        payload = {"name": name, "extension": ext, "signal": SIGNAL_MAIL}
        return "MAIL_FILE", payload

    mime, _ = mimetypes.guess_type(path_str)
    cso_type = (
        "FILE_PDF"      if ext == ".pdf"  else
        "FILE_TEXT"     if ext in {".txt", ".md", ".rst"} else
        "FILE_CODE"     if ext in {".py", ".js", ".ts", ".go", ".rs"} else
        "FILE_DOCUMENT" if ext in {".docx", ".doc", ".odt"} else
        "FILE_GENERIC"
    )
    payload = {
        "name": name,
        "extension": ext,
        "mime_type": mime or "application/octet-stream",
        "signal": SIGNAL_FILE,
    }
    return cso_type, payload


def _classify_mail(envelope: dict) -> tuple[str, dict]:
    """
    envelope keys: subject, from_addr, to_addrs (list), message_id, body_snippet.
    Timestamps are NOT in the payload — they are receipt-envelope only.
    """
    payload = {
        "subject":       str(envelope.get("subject", "")),
        "from_addr":     str(envelope.get("from_addr", "")),
        "to_addrs":      sorted([str(a) for a in envelope.get("to_addrs", [])]),
        "message_id":    str(envelope.get("message_id", "")),
        "body_snippet":  str(envelope.get("body_snippet", ""))[:512],
        "signal":        SIGNAL_MAIL,
    }
    cso_type = "MAIL_THREAD" if envelope.get("thread_id") else "MAIL_MESSAGE"
    return cso_type, payload


def _classify_media(meta: dict) -> tuple[str, dict]:
    """
    meta keys: title, duration_seconds, codec, width, height, channels, mime_type.
    No creation date — excluded per §TEMPORAL_CONSISTENCY_RULE.
    """
    has_video = "width" in meta and "height" in meta
    has_audio = "channels" in meta
    cso_type = (
        "MEDIA_VIDEO" if has_video else
        "MEDIA_AUDIO" if has_audio else
        "MEDIA_GENERIC"
    )
    payload = {
        "title":            str(meta.get("title", "")),
        "codec":            str(meta.get("codec", "")),
        "mime_type":        str(meta.get("mime_type", "")),
        "signal":           SIGNAL_MEDIA,
    }
    if has_video:
        payload["width"]  = int(meta["width"])
        payload["height"] = int(meta["height"])
    if has_audio:
        payload["channels"] = int(meta["channels"])
    if "duration_seconds" in meta:
        payload["duration_seconds"] = float(meta["duration_seconds"])
    return cso_type, payload


def _classify_screen(region: dict) -> tuple[str, dict]:
    """
    region keys: ocr_text, app_hint, region_label.
    Screen captures are content-addressed on their OCR text.
    """
    payload = {
        "ocr_text":     str(region.get("ocr_text", ""))[:2048],
        "app_hint":     str(region.get("app_hint", "")),
        "region_label": str(region.get("region_label", "")),
        "signal":       SIGNAL_SCREEN,
    }
    return "SCREEN_REGION", payload


# ── intake_signal ─────────────────────────────────────────────────────────────

def intake_signal(raw: Any) -> CSOCandidate:
    """
    Convert a raw OS signal into a CSOCandidate.

    Accepted raw input forms:
      str                     → treated as file path
      {"signal": "FILE",  …}  → file path dict
      {"signal": "MAIL",  …}  → IMAP envelope dict
      {"signal": "MEDIA", …}  → media metadata dict
      {"signal": "SCREEN",…}  → screen region dict

    Returns CSOCandidate. Never raises (fails to QUARANTINE on unknown input).
    """
    try:
        if isinstance(raw, str):
            raw = {"signal": SIGNAL_FILE, "path": raw}

        signal = raw.get("signal", "").upper()

        if signal == SIGNAL_FILE or "path" in raw:
            path = str(raw.get("path", ""))
            cso_type, payload = _classify_file(path)
            namespace = _TYPE_TO_NAMESPACE.get(
                SIGNAL_MEDIA if cso_type.startswith("MEDIA") else SIGNAL_FILE,
                NAMESPACE_FILE,
            )
            raw_hint = path

        elif signal == SIGNAL_MAIL:
            cso_type, payload = _classify_mail(raw)
            namespace = NAMESPACE_MAIL
            raw_hint = raw.get("message_id", "")

        elif signal == SIGNAL_MEDIA:
            cso_type, payload = _classify_media(raw)
            namespace = NAMESPACE_MEDIA
            raw_hint = raw.get("title", "")

        elif signal == SIGNAL_SCREEN:
            cso_type, payload = _classify_screen(raw)
            namespace = NAMESPACE_SCREEN
            raw_hint = raw.get("app_hint", "")

        else:
            # Unknown signal type — produce QUARANTINE-eligible candidate
            cso_type = "UNKNOWN"
            payload = {"raw_repr": repr(raw)[:256], "signal": signal or "UNKNOWN"}
            namespace = "quarantine"
            raw_hint = ""

        local_id = law_1_identity_determinism(namespace, payload)

        provenance_stub = {
            "chain": []  # empty — intake is pre-receipt; admit_intake adds the receipt event
        }

        return CSOCandidate(
            signal_type=signal or "UNKNOWN",
            namespace=namespace,
            local_id=local_id,
            cso_type=cso_type,
            payload=payload,
            provenance_stub=provenance_stub,
            raw_hint=raw_hint,
        )

    except Exception as exc:
        return CSOCandidate(
            signal_type="ERROR",
            namespace="quarantine",
            local_id=hashlib.sha256(repr(raw).encode()).hexdigest(),
            cso_type="INTAKE_ERROR",
            payload={"error": str(exc)[:256], "signal": "ERROR"},
            provenance_stub={"chain": []},
            raw_hint="",
        )


# ── admit_intake ──────────────────────────────────────────────────────────────

def admit_intake(
    candidate: CSOCandidate,
    operator_receipt: str,
    existing_graph: Optional[dict] = None,
) -> AdmissionResult:
    """
    Admit a CSOCandidate into the graph with an operator receipt.

    operator_receipt: any non-empty string identifying the admission event
                      (e.g. "user:open:2026-05-06T14:30", "agent:fetch:mail:inbox")
    existing_graph:   dict of {global_id: hash} for mutation/duplicate detection

    Returns AdmissionResult: ACCEPT | REJECT | QUARANTINE
    """
    if not operator_receipt:
        return AdmissionResult(
            REJECT,
            candidate.global_id,
            "NO RECEIPT = NO CLAIM. operator_receipt is required.",
        )

    # Unknown/error signals land in "quarantine" namespace — always QUARANTINE
    if candidate.namespace == "quarantine":
        return AdmissionResult(
            QUARANTINE,
            candidate.global_id,
            "Unknown or error signal type — quarantine namespace.",
        )

    provenance = {
        "chain": [
            {"event": "intake", "receipt_hash": operator_receipt}
        ]
    }

    return admit_cso(
        namespace=candidate.namespace,
        local_id=candidate.local_id,
        payload=candidate.payload,
        receipts=[operator_receipt],
        provenance=provenance,
        existing_graph=existing_graph,
    )


def admit_intake_to_graph(
    candidate: CSOCandidate,
    operator_receipt: str,
    graph: SemanticGraph,
) -> AdmissionResult:
    """
    Convenience wrapper: admits candidate and appends to SemanticGraph if ACCEPT.
    Returns AdmissionResult. Never raises.
    """
    from src.cso_identity_contract import law_1_identity_determinism as _lid
    existing = {
        gid: _lid(node.namespace, node.payload)
        for gid, node in graph._nodes.items()
    }
    result = admit_intake(candidate, operator_receipt, existing_graph=existing)

    if result.status == ADMIT:
        if candidate.global_id not in graph._nodes:
            try:
                cso = CSO(
                    namespace=candidate.namespace,
                    local_id=candidate.local_id,
                    type=candidate.cso_type,
                    payload=candidate.payload,
                    receipts=[operator_receipt],
                    provenance={"chain": [{"event": "intake", "receipt_hash": operator_receipt}]},
                )
                graph.append(cso)
            except Exception as exc:
                return AdmissionResult(REJECT, candidate.global_id, f"graph.append failed: {exc}")

    return result


# ── project_context ───────────────────────────────────────────────────────────

def project_context(
    graph: SemanticGraph,
    intent: dict,
) -> CoherenceSlice:
    """
    Compute the minimum sufficient state for a query intent.

    intent keys:
      namespace_filter  str | None   — restrict to one namespace (e.g. "mail")
      type_filter       str | None   — restrict to one CSO type (e.g. "MAIL_THREAD")
      max_depth         int          — traversal depth (default 3)
      max_branching     int          — branching factor (default 10)

    Returns CoherenceSlice. Pure function of graph state. Deterministic.
    """
    namespace_filter = intent.get("namespace_filter")
    type_filter = intent.get("type_filter")
    max_depth = int(intent.get("max_depth", 3))
    max_branching = int(intent.get("max_branching", 10))

    proj = project(graph, namespace=namespace_filter)

    nodes = proj["nodes"]
    if type_filter:
        nodes = {
            gid: info for gid, info in nodes.items()
            if info.get("type") == type_filter
        }

    return CoherenceSlice(
        intent=intent,
        node_count=len(nodes),
        nodes=nodes,
        graph_hash=proj["graph_hash"],
        namespace_filter=namespace_filter,
        depth_bound=max_depth,
    )
