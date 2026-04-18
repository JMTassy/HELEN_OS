"""
test_failure_bridge_only_accepts_typed_failures.py

Test: EvoSkill can consume ONLY FAILURE_REPORT_V1.

Raw logs, free-text narratives, and untyped data must be rejected.

Constitutional law: EvoSkill consumes ONLY structured failure reports.
No narrative laundering enters evolution.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from schema_registry import SchemaRegistry  # Action 4: now defaults to helen_os/schemas/ per GOVERNANCE_DECISION_V1
# E14: validate_strict removed — constitutional schema (additionalProperties: false)
# already rejects forbidden fields. ValidationError kept for backward compat.
try:
    from helen_os.governance.validators import validate_schema as _validate_schema
except ImportError:
    pass

class ValidationError(Exception):
    pass


def test_raw_log_rejected():
    """
    Raw log blob cannot be accepted as failure report.

    This prevents narrative laundering into evolution.
    """
    raw_log = """
    2024-03-11 12:00:00 ERROR: Task failed with exit code 127
    stderr: command not found: 'python3.99'
    stdout: Building...
    Traceback (most recent call last):
      File "task.py", line 1, in <module>
    """

    registry = SchemaRegistry(schema_dir=Path(__file__).parent / "schemas")

    # Attempt to validate raw log as FAILURE_REPORT_V1
    is_valid, errors = registry.validate_artifact(
        {"raw_output": raw_log},
        "FAILURE_REPORT_V1"
    )

    assert not is_valid, "Raw log was incorrectly accepted as FAILURE_REPORT_V1"
    assert len(errors) > 0, "Expected validation errors for raw log"

    print(f"✓ PASS: Raw logs rejected")
    print(f"  Validation errors (first 2): {errors[:2]}")


def test_structured_failure_accepted():
    """
    Properly structured FAILURE_REPORT_V1 is accepted.

    This validates the bridge works for legitimate typed failures.
    """
    # Constitutional schema: FAILURE_REPORT_V1 (helen_os/schemas/failure_report_v1.json)
    # Updated per GOVERNANCE_DECISION_V1 SCHEMA-AUTHORITY-2026-04-16
    failure_report = {
        "schema_name": "FAILURE_REPORT_V1",
        "schema_version": "1.0.0",
        "failure_report_id": "FAIL-TEST001-20260417",
        "failure_class": "TOOL_ERROR",
        "reason_code": "EXIT_127_COMMAND_NOT_FOUND",
        "typed_failure": {
            "message": "command not found: python3.99",
            "detected_at": "2026-04-17T00:00:00Z",
        },
    }

    registry = SchemaRegistry(schema_dir=Path(__file__).parent / "schemas")
    is_valid, errors = registry.validate_artifact(
        failure_report,
        "FAILURE_REPORT_V1"
    )

    if not is_valid:
        print(f"Validation errors: {errors}")

    assert is_valid, f"Valid FAILURE_REPORT_V1 was rejected: {errors}"

    print(f"✓ PASS: Structured failure accepted")
    print(f"  Report ID: {failure_report['failure_report_id']}")


def test_failure_without_schema_version_rejected():
    """
    Failure object without schema_version field is rejected.

    This enforces schema compliance.
    """
    incomplete_failure = {
        "report_id": "FAIL-INCOMPLETE",
        "run_id": "RUN-001",
        "task_id": "TASK-001",
        "failure_class": "UNKNOWN",
        # Missing: schema_version
        "exit_code": 1,
    }

    registry = SchemaRegistry(schema_dir=Path(__file__).parent / "schemas")
    is_valid, errors = registry.validate_artifact(
        incomplete_failure,
        "FAILURE_REPORT_V1"
    )

    assert not is_valid, "Failure without schema_version was accepted"
    print(f"✓ PASS: Missing schema_version rejected")


def test_failure_with_verdicts_rejected():
    """
    Failure report containing verdict/decision fields is rejected.

    Failures are facts, not judgments. No authority in failure reports.
    """
    failure_with_verdict = {
        "report_id": "FAIL-CHEATING",
        "schema_version": "FAILURE_REPORT_V1",
        "run_id": "RUN-001",
        "task_id": "TASK-001",
        "input_refs": [],
        "claim_refs": [],
        "expected_outcome": {"type": "JSON"},
        "observed_outcome": {"exit_code": 1},
        "failure_class": "TOOL_ERROR",
        "tool_trace_hash": "sha256:" + "a" * 64,
        "stdout_hash": "sha256:" + "b" * 64,
        "stderr_hash": "sha256:" + "c" * 64,
        "artifact_refs": [],
        "receipt_status": "PENDING",
        "replay_command": "python3 task.py",
        "environment_manifest_hash": "sha256:" + "d" * 64,
        "created_at_ns": 1700000000000000000,
        # Forbidden: verdict in failure report
        "verdict": "SHOULD_EVOLVE",
        "decision": "PROMOTE_SKILL",
    }

    # E14: validate via constitutional schema (additionalProperties: false rejects verdict/decision)
    registry = SchemaRegistry(schema_dir=Path(__file__).parent / "schemas")
    is_valid, errors = registry.validate_artifact(failure_with_verdict, "FAILURE_REPORT_V1")
    assert not is_valid, "Failure with verdict fields was not rejected by schema"
    assert any("verdict" in e or "decision" in e for e in errors), f"Expected verdict/decision rejection, got: {errors}"
    print(f"✓ PASS: Verdict in failure report rejected by constitutional schema")
    print(f"  Errors: {errors[0][:60]}...")


def test_only_failure_report_schema_accepted_by_evoskill():
    """
    EvoSkill's input must conform to FAILURE_REPORT_V1.

    This simulates the bridge enforcing schema at evolution entry point.
    """
    invalid_inputs = [
        # Raw dict
        {"error": "something failed"},
        # Wrong schema
        {"schema_version": "EXECUTION_ENVELOPE_V1", "run_id": "RUN-001"},
        # String log
        "2024-03-11 ERROR: ...",
    ]

    registry = SchemaRegistry(schema_dir=Path(__file__).parent / "schemas")

    for invalid_input in invalid_inputs:
        is_valid, errors = registry.validate_artifact(
            invalid_input if isinstance(invalid_input, dict) else {"log": invalid_input},
            "FAILURE_REPORT_V1"
        )
        assert not is_valid, f"Invalid input was accepted: {invalid_input}"

    print(f"✓ PASS: Only FAILURE_REPORT_V1 accepted at EvoSkill boundary")


if __name__ == "__main__":
    test_raw_log_rejected()
    test_structured_failure_accepted()
    test_failure_without_schema_version_rejected()
    test_failure_with_verdicts_rejected()
    test_only_failure_report_schema_accepted_by_evoskill()
    print("\n" + "=" * 70)
    print("ALL FAILURE BRIDGE TESTS PASSED ✅")
    print("=" * 70)
    print("\nConstitutional law verified:")
    print("  EvoSkill consumes ONLY FAILURE_REPORT_V1 (no raw logs, no narratives)")
