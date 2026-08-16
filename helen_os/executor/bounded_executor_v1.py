"""Bounded executor: handler-based, deterministic, receipted.

Implements Stage B.1 scaffolding:
- WRITE, EDIT, ANALYZE, ROUTE handlers
- Execution identity
- Failure registry
- Receipt separation (decision, result, artifact)
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import fcntl
import json
import uuid

from helen_os.governance.canonical import sha256_prefixed, assert_prefixed_sha256, canonical_json_bytes
from helen_os.governance.validators import validate_schema
from helen_kernel.gates.claim_type_policy import pre_dispatch_guard


SCHEMA_VERSION = "1.0.0"
EMPTY_STATE_HASH = "sha256:" + "0" * 64

FAILURE_CODES = {
    "invalid_target",
    "bounds_violation",
    "precondition_failed",
    "conflicting_pre_state",
    "duplicate_execution",
    "unsupported_handler",
    "artifact_write_failed",
    "receipt_emission_failed",
    "jurisdiction_blocked",
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def assert_failure_code(code: str) -> None:
    if code not in FAILURE_CODES:
        raise ValueError(f"Unknown failure code: {code}")


def compute_execution_identity(
    *,
    tool_type: str,
    normalized_target: str,
    normalized_payload: Dict[str, Any],
    pre_state_hash: str,
    policy_version: str,
) -> str:
    assert_prefixed_sha256(pre_state_hash)
    payload = {
        "tool_type": tool_type,
        "normalized_target": normalized_target,
        "normalized_payload": normalized_payload,
        "pre_state_hash": pre_state_hash,
        "policy_version": policy_version,
    }
    return sha256_prefixed(payload)


def compute_payload_hash(payload: Dict[str, Any]) -> str:
    return sha256_prefixed(payload)


def compute_file_hash(path: Path) -> str:
    data = path.read_bytes()
    return sha256_prefixed(data)


def normalize_target(base_dir: Path, target: str) -> Tuple[Optional[str], Optional[str]]:
    if not isinstance(target, str) or not target.strip():
        return None, "invalid_target"
    if Path(target).is_absolute():
        return None, "bounds_violation"
    if ".." in Path(target).parts:
        return None, "bounds_violation"
    normalized = Path(target).as_posix().lstrip("/")
    resolved = (base_dir / normalized).resolve()
    try:
        resolved.relative_to(base_dir.resolve())
    except Exception:
        return None, "bounds_violation"
    return normalized, None


@dataclass(frozen=True)
class ExecutionDecisionReceipt:
    schema_name: str
    schema_version: str
    decision_id: str
    created_at: str
    tool_type: str
    normalized_target: str
    normalized_payload_sha256: str
    pre_state_hash: str
    policy_version: str
    execution_identity: str
    decision: str
    failure_code: Optional[str]
    notes: Optional[str]


@dataclass(frozen=True)
class ExecutionResultReceipt:
    schema_name: str
    schema_version: str
    execution_id: str
    created_at: str
    decision_id_ref: str
    tool_type: str
    status: str
    failure_code: Optional[str]
    pre_state_hash: str
    post_state_hash: Optional[str]
    output_sha256: str
    execution_identity: str
    artifact_refs: List[str]
    notes: Optional[str]


@dataclass(frozen=True)
class ArtifactWriteReceipt:
    schema_name: str
    schema_version: str
    artifact_id: str
    created_at: str
    target_path: str
    sha256: str
    bytes: int
    execution_id_ref: str


class HandlerBase:
    tool_type: str

    def normalize_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

    def validate_target(self, base_dir: Path, normalized_target: str, payload: Dict[str, Any]) -> Optional[str]:
        return None

    def execute(
        self,
        base_dir: Path,
        normalized_target: str,
        payload: Dict[str, Any],
        pre_state_hash: str,
    ) -> Tuple[Optional[ArtifactWriteReceipt], Dict[str, Any], Optional[str], Optional[str]]:
        raise NotImplementedError


class WriteHandler(HandlerBase):
    tool_type = "WRITE"

    def normalize_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        content = payload.get("content")
        if not isinstance(content, str):
            raise ValueError("content must be string")
        return {"content": content}

    def validate_target(self, base_dir: Path, normalized_target: str, payload: Dict[str, Any]) -> Optional[str]:
        path = base_dir / normalized_target
        if path.exists():
            return "bounds_violation"
        return None

    def execute(
        self,
        base_dir: Path,
        normalized_target: str,
        payload: Dict[str, Any],
        pre_state_hash: str,
    ) -> Tuple[Optional[ArtifactWriteReceipt], Dict[str, Any], Optional[str], Optional[str]]:
        path = base_dir / normalized_target
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            data = payload["content"].encode("utf-8")
            path.write_bytes(data)
        except Exception:
            return None, {"status": "failure"}, "artifact_write_failed", None

        post_state_hash = sha256_prefixed(data)
        artifact = ArtifactWriteReceipt(
            schema_name="ARTIFACT_WRITE_V1",
            schema_version=SCHEMA_VERSION,
            artifact_id=f"artifact_{uuid.uuid4().hex}",
            created_at=utc_now_iso(),
            target_path=normalized_target,
            sha256=post_state_hash,
            bytes=len(data),
            execution_id_ref="",
        )
        output = {"status": "success", "bytes_written": len(data), "path": normalized_target}
        return artifact, output, None, post_state_hash


class EditHandler(HandlerBase):
    tool_type = "EDIT"

    def normalize_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        content = payload.get("content")
        if not isinstance(content, str):
            raise ValueError("content must be string")
        return {"content": content}

    def validate_target(self, base_dir: Path, normalized_target: str, payload: Dict[str, Any]) -> Optional[str]:
        path = base_dir / normalized_target
        if not path.exists():
            return "invalid_target"
        return None

    def execute(
        self,
        base_dir: Path,
        normalized_target: str,
        payload: Dict[str, Any],
        pre_state_hash: str,
    ) -> Tuple[Optional[ArtifactWriteReceipt], Dict[str, Any], Optional[str], Optional[str]]:
        path = base_dir / normalized_target
        try:
            data = payload["content"].encode("utf-8")
            path.write_bytes(data)
        except Exception:
            return None, {"status": "failure"}, "artifact_write_failed", None

        post_state_hash = sha256_prefixed(data)
        artifact = ArtifactWriteReceipt(
            schema_name="ARTIFACT_WRITE_V1",
            schema_version=SCHEMA_VERSION,
            artifact_id=f"artifact_{uuid.uuid4().hex}",
            created_at=utc_now_iso(),
            target_path=normalized_target,
            sha256=post_state_hash,
            bytes=len(data),
            execution_id_ref="",
        )
        output = {"status": "success", "bytes_written": len(data), "path": normalized_target}
        return artifact, output, None, post_state_hash


class AnalyzeHandler(HandlerBase):
    tool_type = "ANALYZE"

    def normalize_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        query = payload.get("query")
        if not isinstance(query, str):
            raise ValueError("query must be string")
        return {"query": query}

    def execute(
        self,
        base_dir: Path,
        normalized_target: str,
        payload: Dict[str, Any],
        pre_state_hash: str,
    ) -> Tuple[Optional[ArtifactWriteReceipt], Dict[str, Any], Optional[str], Optional[str]]:
        output = {"status": "success", "analysis": f"ANALYZE:{payload['query']}"}
        return None, output, None, None


class RouteHandler(HandlerBase):
    tool_type = "ROUTE"

    def normalize_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        route = payload.get("route")
        if not isinstance(route, str):
            raise ValueError("route must be string")
        return {"route": route}

    def execute(
        self,
        base_dir: Path,
        normalized_target: str,
        payload: Dict[str, Any],
        pre_state_hash: str,
    ) -> Tuple[Optional[ArtifactWriteReceipt], Dict[str, Any], Optional[str], Optional[str]]:
        output = {"status": "success", "route": payload["route"]}
        return None, output, None, None


HANDLERS = {
    "WRITE": WriteHandler(),
    "EDIT": EditHandler(),
    "ANALYZE": AnalyzeHandler(),
    "ROUTE": RouteHandler(),
}


class ExecutionRegistry:
    def __init__(self, persist_path: Optional[Path] = None) -> None:
        self._seen: set[str] = set()
        self._persist_path = persist_path
        if persist_path is not None and persist_path.exists():
            for line in persist_path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    eid = entry.get("execution_identity", "")
                    if eid:
                        self._seen.add(eid)
                except Exception:
                    pass  # corrupt line — skip without crashing

    def register(self, execution_identity: str) -> bool:
        if execution_identity in self._seen:
            return False
        self._seen.add(execution_identity)
        if self._persist_path is not None:
            self._persist_path.parent.mkdir(parents=True, exist_ok=True)
            entry = json.dumps({"execution_identity": execution_identity, "registered_at": utc_now_iso()}) + "\n"
            with open(self._persist_path, "a", encoding="utf-8") as f:
                fcntl.flock(f, fcntl.LOCK_EX)
                try:
                    f.write(entry)
                    f.flush()
                finally:
                    fcntl.flock(f, fcntl.LOCK_UN)
        return True


class BoundedExecutor:
    def __init__(self, *, base_dir: Path, policy_version: str, registry_path: Optional[Path] = None) -> None:
        self.base_dir = base_dir
        self.policy_version = policy_version
        self.registry = ExecutionRegistry(persist_path=registry_path)

    def execute(self, request: Dict[str, Any]) -> Tuple[ExecutionDecisionReceipt, ExecutionResultReceipt, Optional[ArtifactWriteReceipt]]:
        tool_type = request.get("tool_type")

        # Jurisdiction before effect: this REJECT is terminal for the attempted
        # effect — no handler resolution, no registry write, no mutation.
        block = pre_dispatch_guard(
            {
                "family": "executor",
                "op": "task",
                "claim_type": request.get("claim_type", "RECEIPT"),
            }
        )
        if block is not None:
            decision = self._reject_decision("jurisdiction_blocked", tool_type or "UNKNOWN")
            result = self._failure_result(decision, "jurisdiction_blocked", pre_state_hash=EMPTY_STATE_HASH)
            return decision, result, None

        if tool_type not in HANDLERS:
            decision = self._reject_decision("unsupported_handler", tool_type or "UNKNOWN")
            result = self._failure_result(decision, "unsupported_handler", pre_state_hash=EMPTY_STATE_HASH)
            return decision, result, None

        handler = HANDLERS[tool_type]
        target = request.get("target")
        normalized_target, err = normalize_target(self.base_dir, target)
        if err:
            decision = self._reject_decision(err, tool_type)
            result = self._failure_result(decision, err, pre_state_hash=EMPTY_STATE_HASH)
            return decision, result, None

        try:
            normalized_payload = handler.normalize_payload(request.get("payload", {}))
        except Exception:
            decision = self._reject_decision("precondition_failed", tool_type, normalized_target)
            result = self._failure_result(decision, "precondition_failed", pre_state_hash=EMPTY_STATE_HASH)
            return decision, result, None

        target_err = handler.validate_target(self.base_dir, normalized_target, normalized_payload)
        if target_err:
            decision = self._reject_decision(target_err, tool_type, normalized_target, normalized_payload)
            result = self._failure_result(decision, target_err, pre_state_hash=self._compute_pre_state_hash(tool_type, normalized_target))
            return decision, result, None

        pre_state_hash, pre_state_err = self._determine_pre_state_hash(request, tool_type, normalized_target)
        if pre_state_err:
            decision = self._reject_decision(pre_state_err, tool_type, normalized_target, normalized_payload)
            result = self._failure_result(decision, pre_state_err, pre_state_hash=EMPTY_STATE_HASH)
            return decision, result, None

        execution_identity = compute_execution_identity(
            tool_type=tool_type,
            normalized_target=normalized_target,
            normalized_payload=normalized_payload,
            pre_state_hash=pre_state_hash,
            policy_version=self.policy_version,
        )
        if not self.registry.register(execution_identity):
            decision = self._reject_decision("duplicate_execution", tool_type, normalized_target, normalized_payload, pre_state_hash, execution_identity)
            result = self._failure_result(decision, "duplicate_execution", pre_state_hash=pre_state_hash)
            return decision, result, None

        decision = self._allow_decision(tool_type, normalized_target, normalized_payload, pre_state_hash, execution_identity)

        artifact, output, failure_code, post_state_hash = handler.execute(
            self.base_dir,
            normalized_target,
            normalized_payload,
            pre_state_hash,
        )

        if artifact:
            artifact = ArtifactWriteReceipt(
                schema_name=artifact.schema_name,
                schema_version=artifact.schema_version,
                artifact_id=artifact.artifact_id,
                created_at=artifact.created_at,
                target_path=artifact.target_path,
                sha256=artifact.sha256,
                bytes=artifact.bytes,
                execution_id_ref="",
            )

        if failure_code:
            assert_failure_code(failure_code)
            result = self._failure_result(decision, failure_code, pre_state_hash=pre_state_hash)
            return decision, result, None

        output_sha256 = sha256_prefixed(output)
        result = ExecutionResultReceipt(
            schema_name="EXECUTION_RESULT_V1",
            schema_version=SCHEMA_VERSION,
            execution_id=f"exec_{uuid.uuid4().hex}",
            created_at=utc_now_iso(),
            decision_id_ref=decision.decision_id,
            tool_type=tool_type,
            status="SUCCESS",
            failure_code=None,
            pre_state_hash=pre_state_hash,
            post_state_hash=post_state_hash,
            output_sha256=output_sha256,
            execution_identity=decision.execution_identity,
            artifact_refs=[artifact.artifact_id] if artifact else [],
            notes=None,
        )

        if artifact:
            artifact = ArtifactWriteReceipt(
                schema_name=artifact.schema_name,
                schema_version=artifact.schema_version,
                artifact_id=artifact.artifact_id,
                created_at=artifact.created_at,
                target_path=artifact.target_path,
                sha256=artifact.sha256,
                bytes=artifact.bytes,
                execution_id_ref=result.execution_id,
            )

        self._validate_receipts(decision, result, artifact)
        return decision, result, artifact

    def _compute_pre_state_hash(self, tool_type: str, normalized_target: str) -> str:
        path = self.base_dir / normalized_target
        if tool_type in {"WRITE", "EDIT"}:
            if path.exists():
                return compute_file_hash(path)
            return EMPTY_STATE_HASH
        return EMPTY_STATE_HASH

    def _determine_pre_state_hash(self, request: Dict[str, Any], tool_type: str, normalized_target: str) -> Tuple[Optional[str], Optional[str]]:
        if tool_type == "EDIT":
            supplied = request.get("pre_state_hash")
            if not isinstance(supplied, str):
                return None, "precondition_failed"
            try:
                assert_prefixed_sha256(supplied)
            except Exception:
                return None, "precondition_failed"
            actual = self._compute_pre_state_hash(tool_type, normalized_target)
            if supplied != actual:
                return None, "conflicting_pre_state"
            return supplied, None
        if tool_type == "WRITE":
            return EMPTY_STATE_HASH, None
        return EMPTY_STATE_HASH, None

    def _allow_decision(
        self,
        tool_type: str,
        normalized_target: str,
        normalized_payload: Dict[str, Any],
        pre_state_hash: str,
        execution_identity: str,
    ) -> ExecutionDecisionReceipt:
        receipt = ExecutionDecisionReceipt(
            schema_name="EXECUTION_DECISION_V1",
            schema_version=SCHEMA_VERSION,
            decision_id=f"dec_{uuid.uuid4().hex}",
            created_at=utc_now_iso(),
            tool_type=tool_type,
            normalized_target=normalized_target,
            normalized_payload_sha256=compute_payload_hash(normalized_payload),
            pre_state_hash=pre_state_hash,
            policy_version=self.policy_version,
            execution_identity=execution_identity,
            decision="ALLOW",
            failure_code=None,
            notes=None,
        )
        return receipt

    def _reject_decision(
        self,
        failure_code: str,
        tool_type: str,
        normalized_target: Optional[str] = "",
        normalized_payload: Optional[Dict[str, Any]] = None,
        pre_state_hash: Optional[str] = None,
        execution_identity: Optional[str] = None,
    ) -> ExecutionDecisionReceipt:
        assert_failure_code(failure_code)
        normalized_payload = normalized_payload or {}
        pre_state_hash = pre_state_hash or EMPTY_STATE_HASH
        execution_identity = execution_identity or compute_execution_identity(
            tool_type=tool_type,
            normalized_target=normalized_target or "",
            normalized_payload=normalized_payload,
            pre_state_hash=pre_state_hash,
            policy_version=self.policy_version,
        )
        receipt = ExecutionDecisionReceipt(
            schema_name="EXECUTION_DECISION_V1",
            schema_version=SCHEMA_VERSION,
            decision_id=f"dec_{uuid.uuid4().hex}",
            created_at=utc_now_iso(),
            tool_type=tool_type,
            normalized_target=normalized_target or "",
            normalized_payload_sha256=compute_payload_hash(normalized_payload),
            pre_state_hash=pre_state_hash,
            policy_version=self.policy_version,
            execution_identity=execution_identity,
            decision="REJECT",
            failure_code=failure_code,
            notes=None,
        )
        return receipt

    def _failure_result(self, decision: ExecutionDecisionReceipt, failure_code: str, pre_state_hash: str) -> ExecutionResultReceipt:
        assert_failure_code(failure_code)
        output_sha256 = sha256_prefixed({"status": "failure", "code": failure_code})
        result = ExecutionResultReceipt(
            schema_name="EXECUTION_RESULT_V1",
            schema_version=SCHEMA_VERSION,
            execution_id=f"exec_{uuid.uuid4().hex}",
            created_at=utc_now_iso(),
            decision_id_ref=decision.decision_id,
            tool_type=decision.tool_type,
            status="FAILURE",
            failure_code=failure_code,
            pre_state_hash=pre_state_hash,
            post_state_hash=None,
            output_sha256=output_sha256,
            execution_identity=decision.execution_identity,
            artifact_refs=[],
            notes=None,
        )
        self._validate_receipts(decision, result, None)
        return result

    def _validate_receipts(
        self,
        decision: ExecutionDecisionReceipt,
        result: ExecutionResultReceipt,
        artifact: Optional[ArtifactWriteReceipt],
    ) -> None:
        ok, err = validate_schema("EXECUTION_DECISION_V1", SCHEMA_VERSION, decision.__dict__)
        if not ok:
            raise RuntimeError(f"decision receipt invalid: {err}")
        ok, err = validate_schema("EXECUTION_RESULT_V1", SCHEMA_VERSION, result.__dict__)
        if not ok:
            raise RuntimeError(f"result receipt invalid: {err}")
        if artifact:
            ok, err = validate_schema("ARTIFACT_WRITE_V1", SCHEMA_VERSION, artifact.__dict__)
            if not ok:
                raise RuntimeError(f"artifact receipt invalid: {err}")
