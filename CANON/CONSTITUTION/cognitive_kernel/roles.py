"""Role declarations for the HELEN kernel admission gates.

This file is intentionally small and deterministic. Roles describe
capabilities and authority boundaries; they do not execute actions and they
do not grant sovereign writes by themselves.
"""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping


KERNEL_NAMESPACE = "helen.kernel"


@dataclass(frozen=True)
class RoleSchema:
    """Static role contract used by schema validation."""

    key: str
    namespace: str
    title: str
    layer: str
    sovereign: bool
    authority: tuple[str, ...]
    may_propose: bool
    may_admit: bool
    may_execute: bool
    may_write_truth: bool
    constraints: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "key": self.key,
            "namespace": self.namespace,
            "title": self.title,
            "layer": self.layer,
            "sovereign": self.sovereign,
            "authority": list(self.authority),
            "may_propose": self.may_propose,
            "may_admit": self.may_admit,
            "may_execute": self.may_execute,
            "may_write_truth": self.may_write_truth,
            "constraints": list(self.constraints),
        }


_ROLE_SCHEMAS: dict[str, RoleSchema] = {
    "USER": RoleSchema(
        key="USER",
        namespace=f"{KERNEL_NAMESPACE}.role.user",
        title="User",
        layer="human_authority",
        sovereign=False,
        authority=("request", "authorize", "reject", "clarify"),
        may_propose=True,
        may_admit=True,
        may_execute=False,
        may_write_truth=False,
        constraints=(
            "human_authority_required_for_irreversible_or_high_risk_actions",
            "admission_requires_explicit_receipt",
        ),
    ),
    "HER": RoleSchema(
        key="HER",
        namespace=f"{KERNEL_NAMESPACE}.role.her",
        title="HER",
        layer="shell_synthesis",
        sovereign=False,
        authority=("generate", "synthesize", "route_candidate"),
        may_propose=True,
        may_admit=False,
        may_execute=False,
        may_write_truth=False,
        constraints=(
            "may_not_author_kernel_truth",
            "may_not_self_admit",
            "outputs_are_candidates_until_admitted",
        ),
    ),
    "HAL": RoleSchema(
        key="HAL",
        namespace=f"{KERNEL_NAMESPACE}.role.hal",
        title="HAL",
        layer="governance_gate",
        sovereign=False,
        authority=("gate", "block", "request_repair", "classify_policy"),
        may_propose=False,
        may_admit=False,
        may_execute=False,
        may_write_truth=False,
        constraints=(
            "gates_do_not_create_truth",
            "blocked_actions_need_safe_repair_or_explanation",
            "must_not_replace_reducer_admission",
        ),
    ),
    "JESTER": RoleSchema(
        key="JESTER",
        namespace=f"{KERNEL_NAMESPACE}.role.jester",
        title="JESTER",
        layer="adversarial_review",
        sovereign=False,
        authority=("invert", "stress_test", "surface_contradiction"),
        may_propose=True,
        may_admit=False,
        may_execute=False,
        may_write_truth=False,
        constraints=(
            "adversarial_output_is_trace_only_until_admitted",
            "must_resolve_markers_to_referents",
            "may_not_certify_own_findings",
        ),
    ),
    "LEDGER": RoleSchema(
        key="LEDGER",
        namespace=f"{KERNEL_NAMESPACE}.role.ledger",
        title="Ledger",
        layer="proof_substrate",
        sovereign=True,
        authority=("record", "replay", "hash_chain", "preserve_receipts"),
        may_propose=False,
        may_admit=False,
        may_execute=False,
        may_write_truth=True,
        constraints=(
            "writes_only_through_validated_receipts",
            "no_receipt_no_claim",
            "replay_safety_required",
        ),
    ),
    "REDUCER": RoleSchema(
        key="REDUCER",
        namespace=f"{KERNEL_NAMESPACE}.role.reducer",
        title="Reducer",
        layer="admission_gate",
        sovereign=False,
        authority=("admit", "reject", "request_changes"),
        may_propose=False,
        may_admit=True,
        may_execute=False,
        may_write_truth=False,
        constraints=(
            "cannot_be_same_actor_as_proposer_for_canonization",
            "admission_must_emit_admission_receipt",
            "admission_does_not_execute_action",
        ),
    ),
    "EXECUTOR": RoleSchema(
        key="EXECUTOR",
        namespace=f"{KERNEL_NAMESPACE}.role.executor",
        title="Executor",
        layer="tool_gateway",
        sovereign=False,
        authority=("execute_admitted_action", "emit_execution_receipt"),
        may_propose=False,
        may_admit=False,
        may_execute=True,
        may_write_truth=False,
        constraints=(
            "executes_only_after_admission",
            "validates_action_schema_before_dispatch",
            "execution_receipt_required",
        ),
    ),
}


ROLE_SCHEMAS: Mapping[str, RoleSchema] = MappingProxyType(_ROLE_SCHEMAS)


def get_role_schema(role_key: str) -> RoleSchema:
    """Return a role schema by canonical key."""

    normalized = role_key.strip().upper()
    return ROLE_SCHEMAS[normalized]
