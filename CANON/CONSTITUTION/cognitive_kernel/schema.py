"""Kernel structure validation for HELEN admission gates.

The functions here are deliberately conservative. They validate static
structure and namespace consistency, then return explicit flags instead of
silently accepting ambiguous governance.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping, Sequence

from roles import KERNEL_NAMESPACE, ROLE_SCHEMAS, RoleSchema


class ValidationStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"


@dataclass(frozen=True)
class ValidationFlag:
    code: str
    message: str
    path: str

    def as_dict(self) -> dict[str, str]:
        return {"code": self.code, "message": self.message, "path": self.path}


@dataclass(frozen=True)
class ValidationReport:
    status: ValidationStatus
    flags: tuple[ValidationFlag, ...]

    @property
    def ok(self) -> bool:
        return self.status is ValidationStatus.PASS

    def as_dict(self) -> dict[str, object]:
        return {
            "status": self.status.value,
            "ok": self.ok,
            "flags": [flag.as_dict() for flag in self.flags],
        }


REQUIRED_ROLE_KEYS = frozenset(
    {
        "USER",
        "HER",
        "HAL",
        "JESTER",
        "LEDGER",
        "REDUCER",
        "EXECUTOR",
    }
)

REQUIRED_RECEIPT_TYPES = ("PROPOSAL", "ADMISSION", "VALIDATION", "EXECUTION")

SOVEREIGN_LAYERS = frozenset({"proof_substrate"})


def _finish(flags: list[ValidationFlag]) -> ValidationReport:
    status = ValidationStatus.FAIL if flags else ValidationStatus.PASS
    return ValidationReport(status=status, flags=tuple(flags))


def _flag(flags: list[ValidationFlag], code: str, message: str, path: str) -> None:
    flags.append(ValidationFlag(code=code, message=message, path=path))


def _as_role_schema(value: Any, path: str, flags: list[ValidationFlag]) -> RoleSchema | None:
    if isinstance(value, RoleSchema):
        return value
    _flag(flags, "ROLE_SCHEMA_TYPE", "role entry must be a RoleSchema", path)
    return None


def validate_structure(
    role_schemas: Mapping[str, RoleSchema] = ROLE_SCHEMAS,
    required_role_keys: Sequence[str] = tuple(sorted(REQUIRED_ROLE_KEYS)),
) -> ValidationReport:
    """Validate role shape, authority separation, and receipt gate coverage."""

    flags: list[ValidationFlag] = []

    if not isinstance(role_schemas, Mapping):
        _flag(flags, "ROLE_SCHEMAS_NOT_MAPPING", "ROLE_SCHEMAS must be a mapping", "ROLE_SCHEMAS")
        return _finish(flags)

    actual_keys = set(role_schemas.keys())
    required_keys = set(required_role_keys)

    for missing in sorted(required_keys - actual_keys):
        _flag(flags, "ROLE_MISSING", f"required role {missing} is missing", f"ROLE_SCHEMAS.{missing}")

    for unexpected in sorted(actual_keys - required_keys):
        _flag(
            flags,
            "ROLE_UNEXPECTED",
            f"unexpected role {unexpected} is not part of the kernel role set",
            f"ROLE_SCHEMAS.{unexpected}",
        )

    admitters: list[str] = []
    executors: list[str] = []
    truth_writers: list[str] = []

    for key, value in role_schemas.items():
        path = f"ROLE_SCHEMAS.{key}"
        role = _as_role_schema(value, path, flags)
        if role is None:
            continue

        if key != key.upper():
            _flag(flags, "ROLE_KEY_CASE", "role mapping key must be uppercase", path)

        if key != role.key:
            _flag(flags, "ROLE_KEY_MISMATCH", "role mapping key must match role.key", f"{path}.key")

        if not role.title:
            _flag(flags, "ROLE_TITLE_EMPTY", "role title is required", f"{path}.title")

        if not role.layer:
            _flag(flags, "ROLE_LAYER_EMPTY", "role layer is required", f"{path}.layer")

        if not role.authority:
            _flag(flags, "ROLE_AUTHORITY_EMPTY", "role authority tuple must not be empty", f"{path}.authority")

        if not role.constraints:
            _flag(flags, "ROLE_CONSTRAINTS_EMPTY", "role constraints must not be empty", f"{path}.constraints")

        if role.may_admit:
            admitters.append(key)

        if role.may_execute:
            executors.append(key)

        if role.may_write_truth:
            truth_writers.append(key)

        if role.sovereign and role.layer not in SOVEREIGN_LAYERS:
            _flag(
                flags,
                "SOVEREIGN_LAYER_INVALID",
                "sovereign role must live in an approved sovereign layer",
                f"{path}.layer",
            )

        if role.may_write_truth and (not role.sovereign or role.layer not in SOVEREIGN_LAYERS):
            _flag(
                flags,
                "TRUTH_WRITE_AUTHORITY_CREEP",
                "only sovereign proof-substrate roles may write truth",
                f"{path}.may_write_truth",
            )

        if role.may_admit and role.may_execute:
            _flag(
                flags,
                "ADMIT_EXECUTE_COLLAPSE",
                "one role must not both admit and execute",
                path,
            )

        if role.may_propose and role.may_admit and key != "USER":
            _flag(
                flags,
                "PROPOSE_ADMIT_COLLAPSE",
                "non-human role must not both propose and admit",
                path,
            )

    if "REDUCER" not in admitters:
        _flag(flags, "REDUCER_NOT_ADMITTER", "REDUCER must be able to admit", "ROLE_SCHEMAS.REDUCER")

    if "EXECUTOR" not in executors:
        _flag(flags, "EXECUTOR_NOT_EXECUTOR", "EXECUTOR must be able to execute", "ROLE_SCHEMAS.EXECUTOR")

    if truth_writers != ["LEDGER"]:
        _flag(
            flags,
            "TRUTH_WRITER_SET_INVALID",
            "LEDGER must be the only role with truth-write authority",
            "ROLE_SCHEMAS",
        )

    return _finish(flags)


def validate_namespace_consistency(
    role_schemas: Mapping[str, RoleSchema] = ROLE_SCHEMAS,
    namespace_root: str = KERNEL_NAMESPACE,
) -> ValidationReport:
    """Validate stable kernel namespace usage across role schemas."""

    flags: list[ValidationFlag] = []

    if not namespace_root or namespace_root.strip() != namespace_root:
        _flag(flags, "NAMESPACE_ROOT_INVALID", "namespace root must be non-empty and trimmed", "namespace_root")
        return _finish(flags)

    seen_namespaces: set[str] = set()

    for key, value in role_schemas.items():
        path = f"ROLE_SCHEMAS.{key}"
        role = _as_role_schema(value, path, flags)
        if role is None:
            continue

        expected = f"{namespace_root}.role.{key.lower()}"

        if role.namespace != expected:
            _flag(
                flags,
                "ROLE_NAMESPACE_MISMATCH",
                f"namespace must be {expected}",
                f"{path}.namespace",
            )

        if not role.namespace.startswith(f"{namespace_root}."):
            _flag(
                flags,
                "ROLE_NAMESPACE_OUTSIDE_KERNEL",
                "role namespace must remain inside kernel namespace root",
                f"{path}.namespace",
            )

        if role.namespace in seen_namespaces:
            _flag(flags, "ROLE_NAMESPACE_DUPLICATE", "role namespace must be unique", f"{path}.namespace")

        seen_namespaces.add(role.namespace)

    return _finish(flags)


def validate_kernel_admission_gates(
    role_schemas: Mapping[str, RoleSchema] = ROLE_SCHEMAS,
) -> ValidationReport:
    """Run all kernel admission gate checks as one report."""

    reports = (
        validate_structure(role_schemas),
        validate_namespace_consistency(role_schemas),
    )
    flags = [flag for report in reports for flag in report.flags]
    return _finish(flags)


def kernel_schema_summary() -> dict[str, object]:
    """Return a compact, serializable view for manual inspection."""

    return {
        "namespace": KERNEL_NAMESPACE,
        "required_roles": sorted(REQUIRED_ROLE_KEYS),
        "required_receipt_types": list(REQUIRED_RECEIPT_TYPES),
        "roles": {key: role.as_dict() for key, role in ROLE_SCHEMAS.items()},
        "gate_report": validate_kernel_admission_gates().as_dict(),
    }
