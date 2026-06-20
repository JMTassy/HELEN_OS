from __future__ import annotations

import json
import re
import threading
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from helen_os.governance.canonical import canonical_json_bytes, sha256_prefixed, assert_prefixed_sha256

SESSION_ID_RE = re.compile(r"^[A-Za-z0-9_]{1,256}$")
ALLOWED_MODES = {"deterministic", "bounded", "open"}
RECENT_RECEIPTS_LIMIT = 50
ALLOWED_POLICY_DIRECTIVES = {"DEFER", "REJECT"}

# Structural audit policy — epoch-based, not text-based
HARD_REJECT_EPOCH = 1000  # absolute ceiling: reject any session that has run this many times


class DoNextError(Exception):
    def __init__(self, status_code: int, message: str) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.message = message


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def make_receipt(*, event_type: str, session_id: str, parent_receipt_id: Optional[str], **fields: Any) -> Dict[str, Any]:
    receipt = {
        "event_type": event_type,
        "receipt_id": str(uuid.uuid4()),
        "session_id": session_id,
        "created_at": utc_now_iso(),
        "parent_receipt_id": parent_receipt_id,
    }
    receipt.update(fields)
    return receipt


@dataclass
class DoNextResult:
    status_code: int
    response: Dict[str, Any]
    trace: List[str]
    receipts: List[Dict[str, Any]]
    session_state: Dict[str, Any]


class SessionStore:
    def __init__(self, base_dir: Path) -> None:
        self._base_dir = base_dir
        self._base_dir.mkdir(parents=True, exist_ok=True)
        self._locks: Dict[str, threading.Lock] = {}
        self._locks_lock = threading.Lock()

    def _lock_for(self, session_id: str) -> threading.Lock:
        with self._locks_lock:
            lock = self._locks.get(session_id)
            if lock is None:
                lock = threading.Lock()
                self._locks[session_id] = lock
            return lock

    def _path_for(self, session_id: str) -> Path:
        return self._base_dir / f"{session_id}.json"

    def load(self, session_id: str) -> Optional[Dict[str, Any]]:
        path = self._path_for(session_id)
        if not path.exists():
            return None
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise DoNextError(500, "SESSION_STATE_CORRUPTED")
        if not verify_state_hash(data):
            raise DoNextError(500, "SESSION_STATE_CORRUPTED")
        return data

    def save(self, session: Dict[str, Any]) -> None:
        session_id = session.get("session_id")
        if not isinstance(session_id, str) or not session_id:
            raise DoNextError(500, "SESSION_STATE_CORRUPTED")
        path = self._path_for(session_id)
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(session, sort_keys=True, separators=(",", ":"), ensure_ascii=False), encoding="utf-8")
        tmp.replace(path)

    def lock(self, session_id: str) -> threading.Lock:
        return self._lock_for(session_id)


class DoNextService:
    def __init__(self, *, storage_dir: Path) -> None:
        self._store = SessionStore(storage_dir)

    def handle_http(self, body: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
        try:
            result = self.execute(body)
            return result.status_code, result.response
        except DoNextError as exc:
            return exc.status_code, {"error": exc.message}
        except Exception as exc:
            return 500, {"error": str(exc)}

    def execute(self, body: Dict[str, Any]) -> DoNextResult:
        trace: List[str] = []
        call_receipts: List[Dict[str, Any]] = []

        trace.append("REQUEST_VALIDATION")
        req = validate_request(body)

        session_id = req["session_id"]
        with self._store.lock(session_id):
            trace.append("SESSION_LOAD")
            session, resumption_receipt = self._load_or_create_session(session_id)
            if resumption_receipt:
                call_receipts.append(resumption_receipt)

            trace.append("KNOWLEDGE_AUDIT")
            audit, audit_receipt = self._audit(session=session, request=req, parent_receipt_id=resumption_receipt["receipt_id"] if resumption_receipt else None)
            call_receipts.append(audit_receipt)

            trace.append("DISPATCH_DECISION")
            dispatch_decision, dispatch_receipt = self._dispatch(session_id=session_id, routing_consequence=audit["routing_consequence"], parent_receipt_id=audit_receipt["receipt_id"], epoch=session["epoch"])
            if dispatch_receipt:
                call_receipts.append(dispatch_receipt)

            trace.append("CONSEQUENCE_OR_BLOCK")
            consequence: Dict[str, Any]
            leaf_receipt: Optional[Dict[str, Any]] = None

            if dispatch_decision == "KERNEL":
                reply, context_items = self._infer(req)
                leaf_receipt = make_receipt(
                    event_type="INFERENCE_EXECUTION",
                    session_id=session_id,
                    parent_receipt_id=dispatch_receipt["receipt_id"] if dispatch_receipt else None,
                    reply_length=len(reply),
                    context_count=len(context_items),
                )
                call_receipts.append(leaf_receipt)
                consequence = {"type": "KERNEL", "reply": reply, "context_items_used": context_items}
            elif dispatch_decision == "DEFER":
                deferred_marker = {
                    "deferred_at": utc_now_iso(),
                    "scheduled_for": None,
                    "queue_position": 1,
                }
                leaf_receipt = make_receipt(
                    event_type="DEFERRED_EXECUTION",
                    session_id=session_id,
                    parent_receipt_id=dispatch_receipt["receipt_id"] if dispatch_receipt else None,
                    queue_position=deferred_marker["queue_position"],
                )
                call_receipts.append(leaf_receipt)
                consequence = {"type": "DEFER", "deferred": deferred_marker, "context_items_used": []}
            else:
                consequence = {"type": "REJECT", "error": "AUDIT_BLOCK"}

            trace.append("CONSOLIDATION")
            session_update = self._consolidate(
                session=session,
                request=req,
                audit=audit,
                dispatch_decision=dispatch_decision,
                consequence=consequence,
                leaf_receipt=leaf_receipt,
            )

            conclusion_receipt: Optional[Dict[str, Any]] = None
            if dispatch_decision != "REJECT" and leaf_receipt is not None:
                chain_hash = sha256_prefixed(json.loads(json.dumps(call_receipts)))
                conclusion_receipt = make_receipt(
                    event_type="CONCLUSION",
                    session_id=session_id,
                    parent_receipt_id=leaf_receipt["receipt_id"],
                    call_outcome="KERNEL_EXECUTED" if dispatch_decision == "KERNEL" else "DEFERRED",
                    receipt_chain_hash=chain_hash,
                )
                call_receipts.append(conclusion_receipt)

            trace.append("PERSISTENCE_RESPONSE")
            response_status, response_body, session_commit_receipt = self._persist_and_respond(
                session=session_update,
                req=req,
                dispatch_decision=dispatch_decision,
                consequence=consequence,
                conclusion_receipt=conclusion_receipt,
                call_receipts=call_receipts,
            )
            if session_commit_receipt:
                call_receipts.append(session_commit_receipt)

            return DoNextResult(
                status_code=response_status,
                response=response_body,
                trace=trace,
                receipts=call_receipts,
                session_state=session_update,
            )

    def _load_or_create_session(self, session_id: str) -> Tuple[Dict[str, Any], Optional[Dict[str, Any]]]:
        session = self._store.load(session_id)
        if session is None:
            now = utc_now_iso()
            session = {
                "schema": "helen_session_state_v1",
                "session_id": session_id,
                "created_at": now,
                "updated_at": now,
                "epoch": 0,
                "run_count": 0,
                "continuity_score": 1.0,
                "memory": [],
                "receipts": [],
                "recent_receipts": [],
                "state_hash": "",
            }
            return session, None

        receipt = make_receipt(
            event_type="SESSION_RESUMPTION",
            session_id=session_id,
            parent_receipt_id=None,
            prior_run_count=session.get("run_count", 0),
            prior_epoch=session.get("epoch", 0),
        )
        return session, receipt

    def _audit(self, *, session: Dict[str, Any], request: Dict[str, Any], parent_receipt_id: Optional[str]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        findings: List[Dict[str, Any]] = []
        routing = "ANNOTATE"

        # Structural policy check 1: epoch hard ceiling
        epoch = int(session.get("epoch", 0))
        if epoch >= HARD_REJECT_EPOCH:
            findings.append({"code": "AUDIT_BLOCK", "severity": "CRITICAL", "routing_effect": "REJECT"})
            routing = "REJECT"

        # Structural policy check 2: explicit policy_directive in request
        elif request.get("policy_directive") == "REJECT":
            findings.append({"code": "AUDIT_BLOCK", "severity": "CRITICAL", "routing_effect": "REJECT"})
            routing = "REJECT"
        elif request.get("policy_directive") == "DEFER":
            findings.append({"code": "AUDIT_DEFER", "severity": "HIGH", "routing_effect": "DEFER"})
            routing = "DEFER"

        audit = {
            "session_id": session["session_id"],
            "findings": findings,
            "routing_consequence": routing,
            "registry_version": "1.0.0",
            "audit_timestamp": utc_now_iso(),
        }
        receipt = make_receipt(
            event_type="KNOWLEDGE_AUDIT",
            session_id=session["session_id"],
            parent_receipt_id=parent_receipt_id,
            finding_count=len(findings),
            routing_consequence=routing,
            registry_version="1.0.0",
        )
        return audit, receipt

    def _dispatch(self, *, session_id: str, routing_consequence: str, parent_receipt_id: str, epoch: int) -> Tuple[str, Optional[Dict[str, Any]]]:
        if routing_consequence == "REJECT":
            return "REJECT", None
        decision = "DEFER" if routing_consequence == "DEFER" else "KERNEL"
        receipt = make_receipt(
            event_type="DISPATCH_DECISION",
            session_id=session_id,
            parent_receipt_id=parent_receipt_id,
            routing_decision=decision,
            epoch=epoch,
        )
        return decision, receipt

    def _infer(self, request: Dict[str, Any]) -> Tuple[str, List[str]]:
        user_input = str(request.get("user_input") or "").strip()
        reply = user_input
        return reply, []

    def _consolidate(
        self,
        *,
        session: Dict[str, Any],
        request: Dict[str, Any],
        audit: Dict[str, Any],
        dispatch_decision: str,
        consequence: Dict[str, Any],
        leaf_receipt: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        session = dict(session)
        now = utc_now_iso()

        memory_entry = {
            "ts": now,
            "user_input": request.get("user_input"),
            "mode": request.get("mode"),
            "model": request.get("model"),
            "routing_consequence": audit.get("routing_consequence"),
            "dispatch_decision": dispatch_decision,
            "authorized_receipt_id": leaf_receipt["receipt_id"] if leaf_receipt else None,
            "audit_findings": audit.get("findings", []),
        }
        if consequence.get("type") == "KERNEL":
            memory_entry["reply"] = consequence.get("reply")
        elif consequence.get("type") == "DEFER":
            memory_entry["deferred"] = consequence.get("deferred")
        else:
            memory_entry["error"] = consequence.get("error")

        memory = list(session.get("memory") or [])
        memory.append(memory_entry)
        session["memory"] = memory
        session["updated_at"] = now
        return session

    def _persist_and_respond(
        self,
        *,
        session: Dict[str, Any],
        req: Dict[str, Any],
        dispatch_decision: str,
        consequence: Dict[str, Any],
        conclusion_receipt: Optional[Dict[str, Any]],
        call_receipts: List[Dict[str, Any]],
    ) -> Tuple[int, Dict[str, Any], Optional[Dict[str, Any]]]:
        session = dict(session)
        accepted = dispatch_decision != "REJECT"
        if accepted:
            session["run_count"] = int(session.get("run_count", 0)) + 1
            session["epoch"] = int(session.get("epoch", 0)) + 1

        receipts = list(session.get("receipts") or [])
        receipts.extend(call_receipts)
        session_commit_receipt = make_receipt(
            event_type="SESSION_COMMIT",
            session_id=session["session_id"],
            parent_receipt_id=conclusion_receipt["receipt_id"] if conclusion_receipt else None,
            state_hash="",
            run_count=session.get("run_count", 0),
        )
        receipts.append(session_commit_receipt)
        session["receipts"] = receipts
        session["recent_receipts"] = receipts[-RECENT_RECEIPTS_LIMIT:]

        state_hash = compute_state_hash(session)
        session["state_hash"] = state_hash
        session_commit_receipt["state_hash"] = state_hash

        try:
            self._store.save(session)
        except Exception as exc:
            raise DoNextError(500, "PERSISTENCE_FAILURE") from exc

        reply: Optional[str]
        context_items = []
        if dispatch_decision == "KERNEL":
            reply = consequence.get("reply")
            context_items = consequence.get("context_items_used", [])
        else:
            reply = None

        response_body = {
            "session_id": session["session_id"],
            "mode": req["mode"],
            "model": req["model"],
            "reply": reply,
            "receipt_id": conclusion_receipt["receipt_id"] if conclusion_receipt else None,
            "run_id": session.get("run_count", 0),
            "context_items_used": context_items,
            "epoch": session.get("epoch", 0),
            "continuity": session.get("continuity_score", 1.0),
        }

        status_code = 200 if accepted else 400
        return status_code, response_body, session_commit_receipt


def validate_request(body: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(body, dict):
        raise DoNextError(400, "invalid request body")

    allowed = {
        "session_id",
        "user_input",
        "mode",
        "model",
        "project",
        "max_context_messages",
        "include_reasoning",
        "temperature",
        "top_p",
        "seed",
        "policy_directive",
    }
    unknown = set(body.keys()) - allowed
    if unknown:
        raise DoNextError(400, f"unknown fields: {sorted(unknown)}")

    required = ["session_id", "user_input", "mode", "model"]
    for key in required:
        if key not in body or body[key] is None:
            raise DoNextError(400, f"missing required field: {key}")

    session_id = body.get("session_id")
    if not isinstance(session_id, str) or not session_id.strip():
        raise DoNextError(400, "session_id required")
    if not SESSION_ID_RE.match(session_id):
        raise DoNextError(400, "session_id invalid")

    user_input = body.get("user_input")
    if not isinstance(user_input, str) or not user_input.strip():
        raise DoNextError(400, "user_input required")
    if len(user_input) > 10000:
        raise DoNextError(400, "user_input too long")

    mode = body.get("mode")
    if mode not in ALLOWED_MODES:
        raise DoNextError(400, "mode invalid")

    model = body.get("model")
    if not isinstance(model, str) or not model.strip():
        raise DoNextError(400, "model invalid")

    project = body.get("project")
    if project is not None and not isinstance(project, str):
        raise DoNextError(400, "project invalid")

    max_context_messages = body.get("max_context_messages")
    if max_context_messages is not None:
        if not isinstance(max_context_messages, int) or max_context_messages < 1:
            raise DoNextError(400, "max_context_messages invalid")

    include_reasoning = body.get("include_reasoning")
    if include_reasoning is not None and not isinstance(include_reasoning, bool):
        raise DoNextError(400, "include_reasoning invalid")

    temperature = body.get("temperature")
    if temperature is not None:
        if not isinstance(temperature, (int, float)) or temperature < 0.0 or temperature > 2.0:
            raise DoNextError(400, "temperature invalid")

    top_p = body.get("top_p")
    if top_p is not None:
        if not isinstance(top_p, (int, float)) or top_p < 0.0 or top_p > 1.0:
            raise DoNextError(400, "top_p invalid")

    seed = body.get("seed")
    if seed is not None:
        if not isinstance(seed, int) or seed < 0:
            raise DoNextError(400, "seed invalid")

    policy_directive = body.get("policy_directive")
    if policy_directive is not None and policy_directive not in ALLOWED_POLICY_DIRECTIVES:
        raise DoNextError(400, "policy_directive invalid")

    return {
        "session_id": session_id,
        "user_input": user_input,
        "mode": mode,
        "model": model,
        "project": project,
        "max_context_messages": max_context_messages,
        "include_reasoning": include_reasoning,
        "temperature": temperature,
        "top_p": top_p,
        "seed": seed,
        "policy_directive": policy_directive,
    }


def compute_state_hash(state: Dict[str, Any]) -> str:
    data = sanitize_state_for_hash(state)
    return sha256_prefixed(canonical_json_bytes(data))


def sanitize_state_for_hash(state: Dict[str, Any]) -> Dict[str, Any]:
    data = json.loads(json.dumps(state))
    data.pop("state_hash", None)
    for key in ("receipts", "recent_receipts"):
        receipts = data.get(key)
        if isinstance(receipts, list):
            for receipt in receipts:
                if isinstance(receipt, dict) and receipt.get("event_type") == "SESSION_COMMIT":
                    receipt["state_hash"] = ""
    return data


def verify_state_hash(state: Dict[str, Any]) -> bool:
    expected = state.get("state_hash")
    if not isinstance(expected, str) or not expected:
        return False
    try:
        assert_prefixed_sha256(expected)
    except Exception:
        return False
    actual = compute_state_hash(state)
    return actual == expected
