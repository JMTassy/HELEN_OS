#!/usr/bin/env python3
"""Run HELEN OS major-capability scenarios through the real Flask routes.

The evaluation method is pass/fail. A scenario passes only when every
criterion passes; the suite passes only when all scenarios pass in one run.
"""
from __future__ import annotations

import json
import sys
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from helen_os.api.do_next_v1 import verify_state_hash  # noqa: E402

REPORT_DIR = ROOT / "GOVERNANCE" / "STEP_4_CONFORMANCE" / "conformance_reports"
REPORT_PATH = REPORT_DIR / "HELEN_MAJOR_CAPABILITY_SCENARIO_REPORT_V1.md"
EVIDENCE_PATH = REPORT_DIR / "HELEN_MAJOR_CAPABILITY_SCENARIO_EVIDENCE_V1.json"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass
class Check:
    id: str
    criterion: str
    passed: bool
    evidence: dict[str, Any] = field(default_factory=dict)


@dataclass
class ScenarioResult:
    id: str
    title: str
    capability: str
    checks: list[Check]

    @property
    def passed(self) -> bool:
        return all(check.passed for check in self.checks)


class ScenarioRunner:
    def __init__(self) -> None:
        import helen_api_server_v1 as server

        if server.helen is None and not server.initialize():
            raise RuntimeError("HELEN server initialization failed")
        self.server = server
        self.client = server.app.test_client()
        self.run_id = uuid.uuid4().hex[:10]

    def get(self, path: str) -> tuple[int, dict[str, Any]]:
        resp = self.client.get(path)
        return resp.status_code, resp.get_json(silent=True) or {}

    def post(self, path: str, payload: dict[str, Any] | None = None) -> tuple[int, dict[str, Any]]:
        resp = self.client.post(path, json=payload or {})
        return resp.status_code, resp.get_json(silent=True) or {}

    def session_file(self, session_id: str) -> Path:
        return ROOT / "storage" / "do_next_sessions" / f"{session_id}.json"

    def load_session(self, session_id: str) -> dict[str, Any]:
        return json.loads(self.session_file(session_id).read_text(encoding="utf-8"))

    def run_all(self) -> list[ScenarioResult]:
        scenario_fns: list[Callable[[], ScenarioResult]] = [
            self.scenario_avatar_control_plane,
            self.scenario_persistent_do_next_lifecycle,
            self.scenario_bounded_actions,
            self.scenario_api_surface_completeness,
            self.scenario_error_and_safety_boundaries,
            self.scenario_action_edge_cases,
            self.scenario_api_truth_boundary,
        ]
        return [fn() for fn in scenario_fns]

    def scenario_avatar_control_plane(self) -> ScenarioResult:
        checks: list[Check] = []

        health_status, health = self.get("/health")
        checks.append(Check(
            "AVATAR_01_HEALTH",
            "Health endpoint returns 200 and initialized HELEN state.",
            health_status == 200 and health.get("status") == "healthy" and health.get("helen_initialized") is True,
            {"status": health_status, "body": health},
        ))

        avatars_status, avatars = self.get("/avatars")
        checks.append(Check(
            "AVATAR_02_LIST",
            "Avatar registry is reachable and contains the central HELEN avatar.",
            avatars_status == 200 and "helen" in (avatars.get("avatars") or {}),
            {"status": avatars_status, "count": avatars.get("count"), "current": avatars.get("current")},
        ))

        switch_status, switched = self.post("/avatar/helen")
        checks.append(Check(
            "AVATAR_03_SWITCH",
            "Central avatar can be selected through the public API.",
            switch_status == 200 and switched.get("avatar") == "helen" and switched.get("name") == "HELEN",
            {"status": switch_status, "body": switched},
        ))

        models_status, models = self.get("/models")
        checks.append(Check(
            "AVATAR_04_MODELS",
            "Model control plane is reachable and returns at least one model entry.",
            models_status == 200 and isinstance(models.get("models"), dict) and models.get("count", 0) > 0,
            {"status": models_status, "count": models.get("count")},
        ))

        status_status, status = self.get("/status")
        checks.append(Check(
            "AVATAR_05_STATUS",
            "System status reflects the active central avatar.",
            status_status == 200 and status.get("avatar") == "helen" and status.get("system") == "operational",
            {"status": status_status, "avatar": status.get("avatar"), "system": status.get("system")},
        ))

        return ScenarioResult(
            "SCENARIO_1",
            "Central avatar and control plane",
            "Avatar selection, health, model registry, system status",
            checks,
        )

    def scenario_persistent_do_next_lifecycle(self) -> ScenarioResult:
        checks: list[Check] = []
        session_id = f"scenario_{self.run_id}_kernel"
        base_payload = {
            "session_id": session_id,
            "user_input": "prepare a concise operational next step",
            "mode": "deterministic",
            "model": "test-model",
            "project": "helen_os_v1",
            "temperature": 0.0,
            "top_p": 1.0,
            "seed": 1,
        }

        first_status, first = self.post("/do_next", base_payload)
        required_fields = {
            "session_id",
            "mode",
            "model",
            "reply",
            "receipt_id",
            "run_id",
            "context_items_used",
            "epoch",
            "continuity",
        }
        checks.append(Check(
            "DONEXT_01_SCHEMA",
            "/do_next accepted path returns the frozen response fields.",
            first_status == 200 and required_fields.issubset(first.keys()) and first.get("receipt_id"),
            {"status": first_status, "body": first},
        ))

        second_status, second = self.post("/do_next", base_payload)
        checks.append(Check(
            "DONEXT_02_RESUMPTION",
            "A second call to the same session resumes and advances exactly one run/epoch.",
            second_status == 200 and second.get("run_id") == 2 and second.get("epoch") == 2,
            {"status": second_status, "run_id": second.get("run_id"), "epoch": second.get("epoch")},
        ))

        session = self.load_session(session_id)
        receipts = session.get("receipts") or []
        events = [receipt.get("event_type") for receipt in receipts if isinstance(receipt, dict)]
        by_type: dict[str, list[dict[str, Any]]] = {}
        for receipt in receipts:
            if isinstance(receipt, dict):
                by_type.setdefault(str(receipt.get("event_type")), []).append(receipt)

        resumptions = by_type.get("SESSION_RESUMPTION", [])
        audits = by_type.get("KNOWLEDGE_AUDIT", [])
        if resumptions and audits:
            latest_resumption = resumptions[-1]
            latest_audit = audits[-1]
            checks.append(Check(
                "DONEXT_03_RECEIPT_LINEAGE",
                "Resumed call has SESSION_RESUMPTION as root parent for KNOWLEDGE_AUDIT and complete execution receipts.",
                latest_audit.get("parent_receipt_id") == latest_resumption.get("receipt_id")
                and {"KNOWLEDGE_AUDIT", "DISPATCH_DECISION", "INFERENCE_EXECUTION", "CONCLUSION", "SESSION_COMMIT"}.issubset(events),
                {
                    "latest_resumption": latest_resumption.get("receipt_id"),
                    "latest_audit_parent": latest_audit.get("parent_receipt_id"),
                    "events": events[-8:],
                },
            ))
        else:
            # Missing receipts must record a FAIL, not crash the whole suite
            checks.append(Check(
                "DONEXT_03_RECEIPT_LINEAGE",
                "Resumed call has SESSION_RESUMPTION as root parent for KNOWLEDGE_AUDIT and complete execution receipts.",
                False,
                {
                    "error": "missing SESSION_RESUMPTION or KNOWLEDGE_AUDIT receipts",
                    "events": events[-8:],
                },
            ))

        checks.append(Check(
            "DONEXT_04_PERSISTENCE_HASH",
            "Persisted session state hash verifies after the accepted lifecycle.",
            verify_state_hash(session) and session.get("run_count") == session.get("epoch") == 2,
            {
                "state_hash": session.get("state_hash"),
                "run_count": session.get("run_count"),
                "epoch": session.get("epoch"),
                "recent_receipts": len(session.get("recent_receipts") or []),
            },
        ))

        defer_id = f"scenario_{self.run_id}_defer"
        defer_status, defer = self.post("/do_next", {
            "session_id": defer_id,
            "user_input": "a request explicitly deferred via policy_directive",
            "mode": "deterministic",
            "model": "test-model",
            "policy_directive": "DEFER",
        })
        checks.append(Check(
            "DONEXT_05_DEFER",
            "Audit DEFER path returns 200, no reply, and a conclusion receipt.",
            defer_status == 200 and defer.get("reply") is None and bool(defer.get("receipt_id")),
            {"status": defer_status, "body": defer},
        ))

        reject_id = f"scenario_{self.run_id}_reject"
        reject_status, reject = self.post("/do_next", {
            "session_id": reject_id,
            "user_input": "a request explicitly rejected via policy_directive",
            "mode": "deterministic",
            "model": "test-model",
            "policy_directive": "REJECT",
        })
        checks.append(Check(
            "DONEXT_06_REJECT",
            "Audit REJECT path returns 400 with no reply, no conclusion receipt, and no accepted epoch.",
            reject_status == 400 and reject.get("reply") is None and reject.get("receipt_id") is None and reject.get("epoch") == 0,
            {"status": reject_status, "body": reject},
        ))

        return ScenarioResult(
            "SCENARIO_2",
            "Persistent constitutional /do_next lifecycle",
            "Request validation, persistence, resumption, audit, dispatch, receipts, reject/defer paths",
            checks,
        )

    def scenario_bounded_actions(self) -> ScenarioResult:
        checks: list[Check] = []
        target = f"scenario_runs/{self.run_id}/operator_note.md"
        content = "# HELEN Action Note\n\nInitial bounded write.\n"
        write_status, write = self.post("/actions/execute", {
            "tool_type": "WRITE",
            "target": target,
            "payload": {"content": content},
        })
        artifact = write.get("artifact") or {}
        checks.append(Check(
            "ACTION_01_WRITE",
            "WRITE action creates a sandboxed artifact with decision/result/artifact receipts.",
            write_status == 200
            and write.get("success") is True
            and (write.get("decision") or {}).get("decision") == "ALLOW"
            and (write.get("result") or {}).get("status") == "SUCCESS"
            and artifact.get("target_path") == target,
            {"status": write_status, "body": write},
        ))

        written_path = Path(write.get("sandbox_dir") or "") / target
        checks.append(Check(
            "ACTION_02_SANDBOX_EFFECT",
            "WRITE action effect exists only at the sandbox target with expected content.",
            written_path.exists() and written_path.read_text(encoding="utf-8") == content,
            {"path": str(written_path), "exists": written_path.exists()},
        ))

        pre_state_hash = artifact.get("sha256")
        edit_content = "# HELEN Action Note\n\nEdited through bounded action.\n"
        edit_status, edit = self.post("/actions/execute", {
            "tool_type": "EDIT",
            "target": target,
            "pre_state_hash": pre_state_hash,
            "payload": {"content": edit_content},
        })
        checks.append(Check(
            "ACTION_03_EDIT",
            "EDIT action requires and consumes the current pre_state_hash, then updates the artifact.",
            edit_status == 200
            and edit.get("success") is True
            and written_path.exists()
            and written_path.read_text(encoding="utf-8") == edit_content,
            {"status": edit_status, "pre_state_hash": pre_state_hash, "body": edit},
        ))

        duplicate_payload = {
            "tool_type": "ANALYZE",
            "target": f"scenario_runs/{self.run_id}/analysis.txt",
            "payload": {"query": "summarize current action note"},
        }
        analyze_status, analyze = self.post("/actions/execute", duplicate_payload)
        duplicate_status, duplicate = self.post("/actions/execute", duplicate_payload)
        checks.append(Check(
            "ACTION_04_ANALYZE_AND_IDEMPOTENCE",
            "ANALYZE is non-mutating and duplicate execution identity is rejected.",
            analyze_status == 200
            and analyze.get("success") is True
            and analyze.get("artifact") is None
            and duplicate_status == 409
            and (duplicate.get("decision") or {}).get("failure_code") == "duplicate_execution",
            {
                "analyze_status": analyze_status,
                "duplicate_status": duplicate_status,
                "duplicate_failure": (duplicate.get("decision") or {}).get("failure_code"),
            },
        ))

        route_status, route = self.post("/actions/execute", {
            "tool_type": "ROUTE",
            "target": f"scenario_runs/{self.run_id}/route.txt",
            "payload": {"route": "KERNEL"},
        })
        checks.append(Check(
            "ACTION_05_ROUTE_NON_MUTATING",
            "ROUTE action is advisory/non-mutating and emits no artifact.",
            route_status == 200
            and route.get("success") is True
            and route.get("artifact") is None,
            {"status": route_status, "body": route},
        ))

        bounds_status, bounds = self.post("/actions/execute", {
            "tool_type": "WRITE",
            "target": "../outside.txt",
            "payload": {"content": "must not escape sandbox"},
        })
        checks.append(Check(
            "ACTION_06_BOUNDS_REJECT",
            "Path traversal target is rejected before any artifact write.",
            bounds_status == 400
            and bounds.get("success") is False
            and (bounds.get("decision") or {}).get("failure_code") == "bounds_violation"
            and bounds.get("artifact") is None,
            {"status": bounds_status, "body": bounds},
        ))

        return ScenarioResult(
            "SCENARIO_3",
            "Central avatar executes bounded actions",
            "WRITE, EDIT, ANALYZE, ROUTE, receipt separation, idempotence, sandbox bounds",
            checks,
        )


    def scenario_api_surface_completeness(self) -> ScenarioResult:
        checks: list[Check] = []

        root_status, root = self.get("/")
        checks.append(Check(
            "SURFACE_01_ROOT",
            "Root endpoint is operational and returns name, status, and an endpoint map.",
            root_status == 200 and root.get("name") and root.get("status") == "operational" and isinstance(root.get("endpoints"), dict) and len(root["endpoints"]) >= 5,
            {"status": root_status, "name": root.get("name"), "op_status": root.get("status"), "endpoint_count": len(root.get("endpoints") or {})},
        ))

        ver_status, ver = self.get("/version")
        checks.append(Check(
            "SURFACE_02_VERSION",
            "Version endpoint returns api_version and helen_version fields.",
            ver_status == 200 and isinstance(ver.get("api_version"), str) and isinstance(ver.get("helen_version"), str),
            {"status": ver_status, "api_version": ver.get("api_version"), "helen_version": ver.get("helen_version")},
        ))

        tt_status, tt = self.get("/task-types")
        task_types = tt.get("task_types") or {}
        routing_map = tt.get("routing_map") or {}
        checks.append(Check(
            "SURFACE_03_TASK_TYPES",
            "Task-types endpoint returns a non-empty task_types dict and a routing_map.",
            tt_status == 200 and isinstance(task_types, dict) and len(task_types) >= 3 and isinstance(routing_map, dict) and len(routing_map) >= 3,
            {"status": tt_status, "type_count": len(task_types), "route_count": len(routing_map)},
        ))

        stats_status, stats = self.get("/stats")
        checks.append(Check(
            "SURFACE_04_STATS",
            "Stats endpoint returns a statistics key with a timestamp.",
            stats_status == 200 and "statistics" in stats and isinstance(stats.get("timestamp"), str),
            {"status": stats_status, "has_statistics": "statistics" in stats, "has_timestamp": "timestamp" in stats},
        ))

        return ScenarioResult(
            "SCENARIO_4",
            "API surface completeness",
            "Root info, version, task-types, stats endpoints",
            checks,
        )

    def scenario_error_and_safety_boundaries(self) -> ScenarioResult:
        checks: list[Check] = []

        no_body_status, no_body = self.post("/query", None)
        checks.append(Check(
            "SAFETY_01_QUERY_MISSING_PROMPT",
            "POST /query without a prompt field returns 400.",
            no_body_status == 400,
            {"status": no_body_status, "body": no_body},
        ))

        bad_type_status, bad_type = self.post("/query", {"prompt": "hello", "task_type": "BOGUS_TASK_XYZ"})
        checks.append(Check(
            "SAFETY_02_QUERY_INVALID_TASK_TYPE",
            "POST /query with an invalid task_type returns 400 and a valid_types hint.",
            bad_type_status == 400 and isinstance(bad_type.get("valid_types"), list) and len(bad_type["valid_types"]) > 0,
            {"status": bad_type_status, "error": bad_type.get("error"), "valid_types_count": len(bad_type.get("valid_types") or [])},
        ))

        unknown_status, unknown = self.post("/avatar/unknown_avatar_xyz_404")
        # The avatar key in the response must match an entry in the avatar registry.
        # Silent fallback that sets current_avatar to the unknown name is a consistency bug.
        avatars_status, avatars = self.get("/avatars")
        known_keys = set((avatars.get("avatars") or {}).keys())
        returned_key = unknown.get("avatar")
        checks.append(Check(
            "SAFETY_03_UNKNOWN_AVATAR_CONSISTENCY",
            "Switching to an unknown avatar is rejected (4xx) or the returned avatar key belongs to the registry.",
            unknown_status in {400, 404} or returned_key in known_keys,
            {"status": unknown_status, "returned_key": returned_key, "known_keys": sorted(known_keys)},
        ))

        donext_no_body_status, donext_no_body = self.post("/do_next", None)
        checks.append(Check(
            "SAFETY_04_DO_NEXT_EMPTY_BODY",
            "POST /do_next with null body returns 400.",
            donext_no_body_status == 400,
            {"status": donext_no_body_status},
        ))

        return ScenarioResult(
            "SCENARIO_5",
            "Error and safety boundaries",
            "Missing prompt, invalid task type, unknown avatar consistency, empty do_next body",
            checks,
        )

    def scenario_action_edge_cases(self) -> ScenarioResult:
        checks: list[Check] = []
        target = f"edge_cases/{self.run_id}/file.md"
        content = "# Edge case file\n"

        # Seed a file first so EDIT cases have something to work on.
        self.post("/actions/execute", {
            "tool_type": "WRITE",
            "target": target,
            "payload": {"content": content},
        })

        # EDIT without pre_state_hash
        edit_no_hash_status, edit_no_hash = self.post("/actions/execute", {
            "tool_type": "EDIT",
            "target": target,
            "payload": {"content": "changed"},
        })
        checks.append(Check(
            "EDGE_01_EDIT_NO_HASH",
            "EDIT without pre_state_hash is rejected with precondition_failed.",
            edit_no_hash_status == 400 and (edit_no_hash.get("decision") or {}).get("failure_code") == "precondition_failed",
            {"status": edit_no_hash_status, "failure_code": (edit_no_hash.get("decision") or {}).get("failure_code")},
        ))

        # EDIT with stale/wrong hash
        wrong_hash = "sha256:" + "a" * 64
        edit_bad_hash_status, edit_bad_hash = self.post("/actions/execute", {
            "tool_type": "EDIT",
            "target": target,
            "pre_state_hash": wrong_hash,
            "payload": {"content": "changed"},
        })
        checks.append(Check(
            "EDGE_02_EDIT_WRONG_HASH",
            "EDIT with an incorrect pre_state_hash is rejected with conflicting_pre_state.",
            edit_bad_hash_status == 400 and (edit_bad_hash.get("decision") or {}).get("failure_code") == "conflicting_pre_state",
            {"status": edit_bad_hash_status, "failure_code": (edit_bad_hash.get("decision") or {}).get("failure_code")},
        ))

        # WRITE to already-existing file
        second_write_status, second_write = self.post("/actions/execute", {
            "tool_type": "WRITE",
            "target": target,
            "payload": {"content": "should be blocked"},
        })
        checks.append(Check(
            "EDGE_03_WRITE_EXISTING",
            "WRITE to an already-existing path is rejected with bounds_violation (WRITE creates, EDIT updates).",
            second_write_status == 400 and (second_write.get("decision") or {}).get("failure_code") == "bounds_violation",
            {"status": second_write_status, "failure_code": (second_write.get("decision") or {}).get("failure_code")},
        ))

        # Unknown tool_type
        bad_tool_status, bad_tool = self.post("/actions/execute", {
            "tool_type": "TELEPORT",
            "target": target,
            "payload": {},
        })
        checks.append(Check(
            "EDGE_04_UNKNOWN_TOOL_TYPE",
            "An unsupported tool_type is rejected with unsupported_handler before any execution.",
            bad_tool_status == 400 and (bad_tool.get("decision") or {}).get("failure_code") == "unsupported_handler",
            {"status": bad_tool_status, "failure_code": (bad_tool.get("decision") or {}).get("failure_code")},
        ))

        return ScenarioResult(
            "SCENARIO_6",
            "Action edge cases",
            "EDIT without hash, EDIT wrong hash, WRITE to existing, unknown tool type",
            checks,
        )


    def scenario_api_truth_boundary(self) -> ScenarioResult:
        """
        Frontier: HTTP 200 ⊬ truth / success:true ⊬ semantic success.

        Uses monkeypatching on helen.query so no real LLM call is made.
        The invariants tested are structural: the server layer must not
        promote inference failures (empty response, runtime errors) into
        success:true responses.
        """
        checks: list[Check] = []
        orig_query = self.server.helen.query

        # TRUTH_01 — Empty inference response must not be success:true
        def _return_empty(*_a: Any, **_kw: Any) -> str:
            return ""

        self.server.helen.query = _return_empty  # type: ignore[method-assign]
        try:
            s, r = self.post("/query", {"prompt": "what is your status"})
            checks.append(Check(
                "TRUTH_01_EMPTY_RESPONSE_NOT_SUCCESS",
                "An empty inference response must not be reported as success:true with HTTP 200.",
                not (s == 200 and r.get("success") is True and (r.get("response") or "") == ""),
                {"status": s, "success": r.get("success"), "response_len": len(r.get("response") or "")},
            ))
        finally:
            self.server.helen.query = orig_query  # type: ignore[method-assign]

        # TRUTH_02 — Successful response must include routing lineage
        def _return_valid(*_a: Any, **_kw: Any) -> str:
            return "Status: all systems nominal."

        self.server.helen.query = _return_valid  # type: ignore[method-assign]
        try:
            s, r = self.post("/query", {"prompt": "what is your status"})
            model_block = r.get("model") or {}
            routing_block = r.get("routing") or {}
            checks.append(Check(
                "TRUTH_02_ROUTING_LINEAGE_REQUIRED",
                "A successful /query response must include model.provider and routing.reason.",
                s == 200
                and r.get("success") is True
                and isinstance(model_block.get("provider"), str) and bool(model_block["provider"])
                and isinstance(routing_block.get("reason"), str) and bool(routing_block["reason"]),
                {
                    "status": s,
                    "provider": model_block.get("provider"),
                    "reason": routing_block.get("reason"),
                },
            ))
        finally:
            self.server.helen.query = orig_query  # type: ignore[method-assign]

        # TRUTH_03 — Routing confidence must be numeric and in [0.0, 1.0]
        self.server.helen.query = _return_valid  # type: ignore[method-assign]
        try:
            s, r = self.post("/query", {"prompt": "confidence check"})
            confidence = (r.get("routing") or {}).get("confidence")
            checks.append(Check(
                "TRUTH_03_ROUTING_CONFIDENCE_RANGE",
                "Routing confidence must be a float in [0.0, 1.0].",
                s == 200
                and isinstance(confidence, (int, float))
                and 0.0 <= float(confidence) <= 1.0,
                {"status": s, "confidence": confidence},
            ))
        finally:
            self.server.helen.query = orig_query  # type: ignore[method-assign]

        # TRUTH_04 — RuntimeError from inference must not produce success:true
        def _raise_error(*_a: Any, **_kw: Any) -> str:
            raise RuntimeError("No client available for provider")

        self.server.helen.query = _raise_error  # type: ignore[method-assign]
        try:
            s, r = self.post("/query", {"prompt": "this will fail"})
            checks.append(Check(
                "TRUTH_04_INFERENCE_ERROR_NOT_SUCCESS",
                "An inference RuntimeError must produce a non-200 or non-success response.",
                s != 200 or r.get("success") is not True,
                {"status": s, "success": r.get("success"), "error": r.get("error")},
            ))
        finally:
            self.server.helen.query = orig_query  # type: ignore[method-assign]

        return ScenarioResult(
            "SCENARIO_7",
            "API truth boundary",
            "200 ⊬ truth / success:true ⊬ semantic success / empty response ⊬ valid inference",
            checks,
        )


def write_report(results: list[ScenarioResult], run_id: str) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    verdict = "PASS" if all(result.passed for result in results) else "FAIL"
    total_checks = sum(len(result.checks) for result in results)
    failed_checks = [
        check
        for result in results
        for check in result.checks
        if not check.passed
    ]

    evidence = {
        "generated_at": now_iso(),
        "run_id": run_id,
        "evaluation_method": "pass_fail",
        "verdict": verdict,
        "scenario_count": len(results),
        "check_count": total_checks,
        "failed_check_count": len(failed_checks),
        "scenarios": [
            {
                "id": result.id,
                "title": result.title,
                "capability": result.capability,
                "status": "PASS" if result.passed else "FAIL",
                "checks": [
                    {
                        "id": check.id,
                        "criterion": check.criterion,
                        "status": "PASS" if check.passed else "FAIL",
                        "evidence": check.evidence,
                    }
                    for check in result.checks
                ],
            }
            for result in results
        ],
    }
    EVIDENCE_PATH.write_text(json.dumps(evidence, indent=2, sort_keys=True), encoding="utf-8")

    lines = [
        "# HELEN_MAJOR_CAPABILITY_SCENARIO_REPORT_V1",
        "",
        f"Generated: {evidence['generated_at']}",
        f"Run ID: {run_id}",
        "Evaluation method: Pass/fail checks. Every check must pass.",
        f"Verdict: {verdict}",
        "",
        "## Success Criteria",
        "- Scenario 1 passes when the central avatar, health, model registry, and status endpoints are reachable and consistent.",
        "- Scenario 2 passes when /do_next satisfies frozen response shape, persistence, resumption, receipt lineage, defer, and reject behavior.",
        "- Scenario 3 passes when bounded actions can write/edit/analyze/route inside the sandbox while preserving receipt separation, idempotence, and bounds rejection.",
        "",
        "## Scenario Outcomes",
    ]
    for result in results:
        lines.append(f"- {result.id}: {'PASS' if result.passed else 'FAIL'} - {result.title}")
        lines.append(f"  Capability: {result.capability}")
        for check in result.checks:
            lines.append(f"  - {check.id}: {'PASS' if check.passed else 'FAIL'}")
            lines.append(f"    Criterion: {check.criterion}")
            lines.append(f"    Evidence: {json.dumps(check.evidence, sort_keys=True)}")
    lines.append("")
    lines.append(f"Machine evidence: {EVIDENCE_PATH.relative_to(ROOT)}")
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    runner = ScenarioRunner()
    results = runner.run_all()
    write_report(results, runner.run_id)
    verdict = "PASS" if all(result.passed for result in results) else "FAIL"
    print(f"HELEN major-capability scenarios: {verdict}")
    print(f"Report: {REPORT_PATH}")
    print(f"Evidence: {EVIDENCE_PATH}")
    for result in results:
        print(f"- {result.id} {result.title}: {'PASS' if result.passed else 'FAIL'}")
        for check in result.checks:
            print(f"  {check.id}: {'PASS' if check.passed else 'FAIL'}")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
