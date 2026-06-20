# HELEN_MAJOR_CAPABILITY_SCENARIO_REPORT_V1

Generated: 2026-06-20T16:11:07.816680Z
Run ID: 36cc83ccd8
Evaluation method: Pass/fail checks. Every check must pass.
Verdict: PASS

## Success Criteria
- Scenario 1 passes when the central avatar, health, model registry, and status endpoints are reachable and consistent.
- Scenario 2 passes when /do_next satisfies frozen response shape, persistence, resumption, receipt lineage, defer, and reject behavior.
- Scenario 3 passes when bounded actions can write/edit/analyze/route inside the sandbox while preserving receipt separation, idempotence, and bounds rejection.

## Scenario Outcomes
- SCENARIO_1: PASS - Central avatar and control plane
  Capability: Avatar selection, health, model registry, system status
  - AVATAR_01_HEALTH: PASS
    Criterion: Health endpoint returns 200 and initialized HELEN state.
    Evidence: {"body": {"helen_initialized": true, "status": "healthy", "timestamp": "2026-06-20T18:11:07.764208"}, "status": 200}
  - AVATAR_02_LIST: PASS
    Criterion: Avatar registry is reachable and contains the central HELEN avatar.
    Evidence: {"count": 4, "current": "helen", "status": 200}
  - AVATAR_03_SWITCH: PASS
    Criterion: Central avatar can be selected through the public API.
    Evidence: {"body": {"avatar": "helen", "emoji": "\ud83e\udde0", "greeting": "Hello! I'm HELEN, your multi-model AI companion.", "name": "HELEN"}, "status": 200}
  - AVATAR_04_MODELS: PASS
    Criterion: Model control plane is reachable and returns at least one model entry.
    Evidence: {"count": 9, "status": 200}
  - AVATAR_05_STATUS: PASS
    Criterion: System status reflects the active central avatar.
    Evidence: {"avatar": "helen", "status": 200, "system": "operational"}
- SCENARIO_2: PASS - Persistent constitutional /do_next lifecycle
  Capability: Request validation, persistence, resumption, audit, dispatch, receipts, reject/defer paths
  - DONEXT_01_SCHEMA: PASS
    Criterion: /do_next accepted path returns the frozen response fields.
    Evidence: {"body": {"context_items_used": [], "continuity": 1.0, "epoch": 1, "mode": "deterministic", "model": "test-model", "receipt_id": "c944a034-8c57-4954-b8c9-bb5a70049d12", "reply": "prepare a concise operational next step", "run_id": 1, "session_id": "scenario_36cc83ccd8_kernel"}, "status": 200}
  - DONEXT_02_RESUMPTION: PASS
    Criterion: A second call to the same session resumes and advances exactly one run/epoch.
    Evidence: {"epoch": 2, "run_id": 2, "status": 200}
  - DONEXT_03_RECEIPT_LINEAGE: PASS
    Criterion: Resumed call has SESSION_RESUMPTION as root parent for KNOWLEDGE_AUDIT and complete execution receipts.
    Evidence: {"events": ["CONCLUSION", "SESSION_COMMIT", "SESSION_RESUMPTION", "KNOWLEDGE_AUDIT", "DISPATCH_DECISION", "INFERENCE_EXECUTION", "CONCLUSION", "SESSION_COMMIT"], "latest_audit_parent": "b773eb33-662f-418b-b7b3-c819cd5e18e8", "latest_resumption": "b773eb33-662f-418b-b7b3-c819cd5e18e8"}
  - DONEXT_04_PERSISTENCE_HASH: PASS
    Criterion: Persisted session state hash verifies after the accepted lifecycle.
    Evidence: {"epoch": 2, "recent_receipts": 11, "run_count": 2, "state_hash": "sha256:b01bd7d163393b85bba347d610ce39fb81df58ecf97e5a959a13a88a8225cb0f"}
  - DONEXT_05_DEFER: PASS
    Criterion: Audit DEFER path returns 200, no reply, and a conclusion receipt.
    Evidence: {"body": {"context_items_used": [], "continuity": 1.0, "epoch": 1, "mode": "deterministic", "model": "test-model", "receipt_id": "4fc1da21-cf14-4fe2-806c-c2ba6a973ee0", "reply": null, "run_id": 1, "session_id": "scenario_36cc83ccd8_defer"}, "status": 200}
  - DONEXT_06_REJECT: PASS
    Criterion: Audit REJECT path returns 400 with no reply, no conclusion receipt, and no accepted epoch.
    Evidence: {"body": {"context_items_used": [], "continuity": 1.0, "epoch": 0, "mode": "deterministic", "model": "test-model", "receipt_id": null, "reply": null, "run_id": 0, "session_id": "scenario_36cc83ccd8_reject"}, "status": 400}
- SCENARIO_3: PASS - Central avatar executes bounded actions
  Capability: WRITE, EDIT, ANALYZE, ROUTE, receipt separation, idempotence, sandbox bounds
  - ACTION_01_WRITE: PASS
    Criterion: WRITE action creates a sandboxed artifact with decision/result/artifact receipts.
    Evidence: {"body": {"artifact": {"artifact_id": "artifact_456398ccf8ba424894c0d7e327645bf6", "bytes": 44, "created_at": "2026-06-20T16:11:07.767847Z", "execution_id_ref": "exec_9fa86af355bf44d9a0fe3eb8a1b13527", "schema_name": "ARTIFACT_WRITE_V1", "schema_version": "1.0.0", "sha256": "sha256:dad9769b3049c223ad34c7610e90f523d78abbe4faabf422fbc5a3d7a652454f", "target_path": "scenario_runs/36cc83ccd8/operator_note.md"}, "avatar": "helen", "decision": {"created_at": "2026-06-20T16:11:07.767692Z", "decision": "ALLOW", "decision_id": "dec_6975dafdb84e401e82e2d53b3446d2dd", "execution_identity": "sha256:cf7882cc36e9e07e15fa955a0b2e756319fb6cb70e9a77ba517d8cc413ee6b4d", "failure_code": null, "normalized_payload_sha256": "sha256:76c682b240e7bc1673b78e915d52f820d7ba46c5904473e3526f7f0f494b3d1e", "normalized_target": "scenario_runs/36cc83ccd8/operator_note.md", "notes": null, "policy_version": "STAGE_B1_V1", "pre_state_hash": "sha256:0000000000000000000000000000000000000000000000000000000000000000", "schema_name": "EXECUTION_DECISION_V1", "schema_version": "1.0.0", "tool_type": "WRITE"}, "result": {"artifact_refs": ["artifact_456398ccf8ba424894c0d7e327645bf6"], "created_at": "2026-06-20T16:11:07.767861Z", "decision_id_ref": "dec_6975dafdb84e401e82e2d53b3446d2dd", "execution_id": "exec_9fa86af355bf44d9a0fe3eb8a1b13527", "execution_identity": "sha256:cf7882cc36e9e07e15fa955a0b2e756319fb6cb70e9a77ba517d8cc413ee6b4d", "failure_code": null, "notes": null, "output_sha256": "sha256:5f758529ad4ee0ac25a6ddb45ceddd318e79ad109732437c758cfb4c8e1d662b", "post_state_hash": "sha256:dad9769b3049c223ad34c7610e90f523d78abbe4faabf422fbc5a3d7a652454f", "pre_state_hash": "sha256:0000000000000000000000000000000000000000000000000000000000000000", "schema_name": "EXECUTION_RESULT_V1", "schema_version": "1.0.0", "status": "SUCCESS", "tool_type": "WRITE"}, "sandbox_dir": "/Users/jean-marietassy/Documents/GitHub/helen_os_v1/storage/action_sandbox", "success": true}, "status": 200}
  - ACTION_02_SANDBOX_EFFECT: PASS
    Criterion: WRITE action effect exists only at the sandbox target with expected content.
    Evidence: {"exists": true, "path": "/Users/jean-marietassy/Documents/GitHub/helen_os_v1/storage/action_sandbox/scenario_runs/36cc83ccd8/operator_note.md"}
  - ACTION_03_EDIT: PASS
    Criterion: EDIT action requires and consumes the current pre_state_hash, then updates the artifact.
    Evidence: {"body": {"artifact": {"artifact_id": "artifact_52643f0251b6461eb9a448f7be6b23fe", "bytes": 52, "created_at": "2026-06-20T16:11:07.774100Z", "execution_id_ref": "exec_434c9c9a4fce44239604b2c9c40b9051", "schema_name": "ARTIFACT_WRITE_V1", "schema_version": "1.0.0", "sha256": "sha256:35234dfda1d74cd94a4e0462a2bfcd1d506923b856eb7930fa05fd249ce85932", "target_path": "scenario_runs/36cc83ccd8/operator_note.md"}, "avatar": "helen", "decision": {"created_at": "2026-06-20T16:11:07.774003Z", "decision": "ALLOW", "decision_id": "dec_68355869d09c44a487ce06f4aae1c592", "execution_identity": "sha256:b45ba3293de5c5a5983c6bdc0c023d94c7ff66b0c7c51ebde1b09b379aa0764c", "failure_code": null, "normalized_payload_sha256": "sha256:d8579b1cc7e7987b822f42d21679f3dcf23637e5a0dca939f137257da98e634b", "normalized_target": "scenario_runs/36cc83ccd8/operator_note.md", "notes": null, "policy_version": "STAGE_B1_V1", "pre_state_hash": "sha256:dad9769b3049c223ad34c7610e90f523d78abbe4faabf422fbc5a3d7a652454f", "schema_name": "EXECUTION_DECISION_V1", "schema_version": "1.0.0", "tool_type": "EDIT"}, "result": {"artifact_refs": ["artifact_52643f0251b6461eb9a448f7be6b23fe"], "created_at": "2026-06-20T16:11:07.774111Z", "decision_id_ref": "dec_68355869d09c44a487ce06f4aae1c592", "execution_id": "exec_434c9c9a4fce44239604b2c9c40b9051", "execution_identity": "sha256:b45ba3293de5c5a5983c6bdc0c023d94c7ff66b0c7c51ebde1b09b379aa0764c", "failure_code": null, "notes": null, "output_sha256": "sha256:f65f6a54ee71b65dcd9af8d1d7ebb3d2b34cad0ab360774ec2b50f71324a4ffb", "post_state_hash": "sha256:35234dfda1d74cd94a4e0462a2bfcd1d506923b856eb7930fa05fd249ce85932", "pre_state_hash": "sha256:dad9769b3049c223ad34c7610e90f523d78abbe4faabf422fbc5a3d7a652454f", "schema_name": "EXECUTION_RESULT_V1", "schema_version": "1.0.0", "status": "SUCCESS", "tool_type": "EDIT"}, "sandbox_dir": "/Users/jean-marietassy/Documents/GitHub/helen_os_v1/storage/action_sandbox", "success": true}, "pre_state_hash": "sha256:dad9769b3049c223ad34c7610e90f523d78abbe4faabf422fbc5a3d7a652454f", "status": 200}
  - ACTION_04_ANALYZE_AND_IDEMPOTENCE: PASS
    Criterion: ANALYZE is non-mutating and duplicate execution identity is rejected.
    Evidence: {"analyze_status": 200, "duplicate_failure": "duplicate_execution", "duplicate_status": 409}
  - ACTION_05_ROUTE_NON_MUTATING: PASS
    Criterion: ROUTE action is advisory/non-mutating and emits no artifact.
    Evidence: {"body": {"artifact": null, "avatar": "helen", "decision": {"created_at": "2026-06-20T16:11:07.786750Z", "decision": "ALLOW", "decision_id": "dec_ff3a5b5d3bd848fdb3bffd5a75c982b1", "execution_identity": "sha256:56a7d19b2c065751fdaa79c09403e906124a9d8c0b87972f6bb95ec703474b05", "failure_code": null, "normalized_payload_sha256": "sha256:5fdbaaee4cb38d1b119332876cf238cca91c969cb994fb42464c589e1b820df7", "normalized_target": "scenario_runs/36cc83ccd8/route.txt", "notes": null, "policy_version": "STAGE_B1_V1", "pre_state_hash": "sha256:0000000000000000000000000000000000000000000000000000000000000000", "schema_name": "EXECUTION_DECISION_V1", "schema_version": "1.0.0", "tool_type": "ROUTE"}, "result": {"artifact_refs": [], "created_at": "2026-06-20T16:11:07.786764Z", "decision_id_ref": "dec_ff3a5b5d3bd848fdb3bffd5a75c982b1", "execution_id": "exec_166385c29142446a80157f1339ca758a", "execution_identity": "sha256:56a7d19b2c065751fdaa79c09403e906124a9d8c0b87972f6bb95ec703474b05", "failure_code": null, "notes": null, "output_sha256": "sha256:3648233e065f17ac24ccaa1e7bccc7463e206171130a218e785787ddb8eed8f4", "post_state_hash": null, "pre_state_hash": "sha256:0000000000000000000000000000000000000000000000000000000000000000", "schema_name": "EXECUTION_RESULT_V1", "schema_version": "1.0.0", "status": "SUCCESS", "tool_type": "ROUTE"}, "sandbox_dir": "/Users/jean-marietassy/Documents/GitHub/helen_os_v1/storage/action_sandbox", "success": true}, "status": 200}
  - ACTION_06_BOUNDS_REJECT: PASS
    Criterion: Path traversal target is rejected before any artifact write.
    Evidence: {"body": {"artifact": null, "avatar": "helen", "decision": {"created_at": "2026-06-20T16:11:07.790450Z", "decision": "REJECT", "decision_id": "dec_6d7dc2ace44140fcbf1857e1805c9e56", "execution_identity": "sha256:70e5c497932d484914af1a24ca7bdc3d40542ca8516c4d4f8d81f521b1817557", "failure_code": "bounds_violation", "normalized_payload_sha256": "sha256:44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a", "normalized_target": "", "notes": null, "policy_version": "STAGE_B1_V1", "pre_state_hash": "sha256:0000000000000000000000000000000000000000000000000000000000000000", "schema_name": "EXECUTION_DECISION_V1", "schema_version": "1.0.0", "tool_type": "WRITE"}, "result": {"artifact_refs": [], "created_at": "2026-06-20T16:11:07.790462Z", "decision_id_ref": "dec_6d7dc2ace44140fcbf1857e1805c9e56", "execution_id": "exec_101e991ac1f64ac8884f0398843d7ae3", "execution_identity": "sha256:70e5c497932d484914af1a24ca7bdc3d40542ca8516c4d4f8d81f521b1817557", "failure_code": "bounds_violation", "notes": null, "output_sha256": "sha256:47f5338b4702eab92dea00539dada328c763886030d35defa9ebecec7b76d19b", "post_state_hash": null, "pre_state_hash": "sha256:0000000000000000000000000000000000000000000000000000000000000000", "schema_name": "EXECUTION_RESULT_V1", "schema_version": "1.0.0", "status": "FAILURE", "tool_type": "WRITE"}, "sandbox_dir": "/Users/jean-marietassy/Documents/GitHub/helen_os_v1/storage/action_sandbox", "success": false}, "status": 400}
- SCENARIO_4: PASS - API surface completeness
  Capability: Root info, version, task-types, stats endpoints
  - SURFACE_01_ROOT: PASS
    Criterion: Root endpoint is operational and returns name, status, and an endpoint map.
    Evidence: {"endpoint_count": 10, "name": "HELEN OS Multi-Model API", "op_status": "operational", "status": 200}
  - SURFACE_02_VERSION: PASS
    Criterion: Version endpoint returns api_version and helen_version fields.
    Evidence: {"api_version": "1.0", "helen_version": "1.0", "status": 200}
  - SURFACE_03_TASK_TYPES: PASS
    Criterion: Task-types endpoint returns a non-empty task_types dict and a routing_map.
    Evidence: {"route_count": 9, "status": 200, "type_count": 9}
  - SURFACE_04_STATS: PASS
    Criterion: Stats endpoint returns a statistics key with a timestamp.
    Evidence: {"has_statistics": true, "has_timestamp": true, "status": 200}
- SCENARIO_5: PASS - Error and safety boundaries
  Capability: Missing prompt, invalid task type, unknown avatar consistency, empty do_next body
  - SAFETY_01_QUERY_MISSING_PROMPT: PASS
    Criterion: POST /query without a prompt field returns 400.
    Evidence: {"body": {"error": "Missing 'prompt' field"}, "status": 400}
  - SAFETY_02_QUERY_INVALID_TASK_TYPE: PASS
    Criterion: POST /query with an invalid task_type returns 400 and a valid_types hint.
    Evidence: {"error": "Invalid task type: BOGUS_TASK_XYZ", "status": 400, "valid_types_count": 9}
  - SAFETY_03_UNKNOWN_AVATAR_CONSISTENCY: PASS
    Criterion: Switching to an unknown avatar is rejected (4xx) or the returned avatar key belongs to the registry.
    Evidence: {"known_keys": ["claude", "helen", "sage", "spark"], "returned_key": null, "status": 404}
  - SAFETY_04_DO_NEXT_EMPTY_BODY: PASS
    Criterion: POST /do_next with null body returns 400.
    Evidence: {"status": 400}
- SCENARIO_6: PASS - Action edge cases
  Capability: EDIT without hash, EDIT wrong hash, WRITE to existing, unknown tool type
  - EDGE_01_EDIT_NO_HASH: PASS
    Criterion: EDIT without pre_state_hash is rejected with precondition_failed.
    Evidence: {"failure_code": "precondition_failed", "status": 400}
  - EDGE_02_EDIT_WRONG_HASH: PASS
    Criterion: EDIT with an incorrect pre_state_hash is rejected with conflicting_pre_state.
    Evidence: {"failure_code": "conflicting_pre_state", "status": 400}
  - EDGE_03_WRITE_EXISTING: PASS
    Criterion: WRITE to an already-existing path is rejected with bounds_violation (WRITE creates, EDIT updates).
    Evidence: {"failure_code": "bounds_violation", "status": 400}
  - EDGE_04_UNKNOWN_TOOL_TYPE: PASS
    Criterion: An unsupported tool_type is rejected with unsupported_handler before any execution.
    Evidence: {"failure_code": "unsupported_handler", "status": 400}
- SCENARIO_7: PASS - API truth boundary
  Capability: 200 ⊬ truth / success:true ⊬ semantic success / empty response ⊬ valid inference
  - TRUTH_01_EMPTY_RESPONSE_NOT_SUCCESS: PASS
    Criterion: An empty inference response must not be reported as success:true with HTTP 200.
    Evidence: {"response_len": 0, "status": 503, "success": false}
  - TRUTH_02_ROUTING_LINEAGE_REQUIRED: PASS
    Criterion: A successful /query response must include model.provider and routing.reason.
    Evidence: {"provider": "ollama", "reason": "top choice for conversation + local execution (privacy, speed) + low latency (50ms)", "status": 200}
  - TRUTH_03_ROUTING_CONFIDENCE_RANGE: PASS
    Criterion: Routing confidence must be a float in [0.0, 1.0].
    Evidence: {"confidence": 0.86, "status": 200}
  - TRUTH_04_INFERENCE_ERROR_NOT_SUCCESS: PASS
    Criterion: An inference RuntimeError must produce a non-200 or non-success response.
    Evidence: {"error": "No client available for provider", "status": 500, "success": null}

Machine evidence: GOVERNANCE/STEP_4_CONFORMANCE/conformance_reports/HELEN_MAJOR_CAPABILITY_SCENARIO_EVIDENCE_V1.json