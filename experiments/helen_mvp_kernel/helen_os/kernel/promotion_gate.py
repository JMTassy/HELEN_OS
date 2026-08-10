"""Promotion gate V2 — the gate calculus as a first-class kernel object.

Law (master):   PROMOTION = TRANSFORMATION + DECLARED_LOSS + DECLARED_ASSUMPTIONS
                + AUTHORITY_DELTA + REVERSIBILITY (+ STORAGE_DELTA).
Law (negation): NO_GATE / UNDECLARED_LOSS / HIDDEN_ASSUMPTION /
                IMPLICIT_AUTHORITY_GAIN / ILLEGAL_LOCATION_PROMOTION /
                STALE_PRE_STATE -> REJECT.

Semantic promotion, authority promotion, and location promotion are three
projections of one passage calculus:
    G = (L_from, L_to, Loss, Assumptions, dAuthority, Reversibility, dStorage)

Separations preserved from V0, each still falsified by a dedicated test:
  VALIDATED != ADMITTED       (validator pass, capability missing -> REJECT)
  DENIAL in audit history, never in state mutation
  gate bound to pre_hash: a gate validated on state A never mutates state B

Pure module: no wall-clock, no filesystem, no randomness. Same inputs ->
same receipts -> byte-identical replay.

status: NON_SOVEREIGN sandbox (experiments/helen_mvp_kernel) · authority=false
banner: 🔵 OBSERVED — merely written; admission requires operator receipt.
"""
from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Callable, Mapping

RECEIPT_TYPE = "PROMOTION_RECEIPT_V2"

Validator = Callable[[dict], tuple[bool, str]]
AssumptionCheck = Callable[[dict, dict], bool]  # (candidate, state) -> holds?

from helen_os.ledger.hash_chain import canonical_json, sha256_hex


class GateConstructionError(ValueError):
    """Raised when a gate is declared without naming its full semantic cost."""


class IrreversibleGateError(ValueError):
    """Raised when the inverse of a non-reversible gate is requested."""


def _require_nonempty_str(name: str, value: object) -> None:
    if not isinstance(value, str) or not value.strip():
        raise GateConstructionError(f"gate field '{name}' must be a non-empty string")


def _require_nonempty_tuple(name: str, value: object, law: str) -> None:
    if not isinstance(value, tuple) or len(value) == 0:
        raise GateConstructionError(f"{law}: '{name}' must be a non-empty tuple")
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise GateConstructionError(f"{law}: '{name}' contains an empty entry")


@dataclass(frozen=True)
class PromotionGate:
    gate_id: str
    from_layer: str
    to_layer: str
    # what the promotion destroys / compresses
    information_loss: tuple
    # what it must presume to be valid
    assumptions: tuple
    # what power it adds
    authority_before: str
    authority_after: str
    # can we walk exactly back?
    reversible: bool
    inverse_gate_id: str | None
    # proof of context — the gate is bound to one state
    pre_hash: str
    # who / what may authorize the passage
    validator_id: str
    required_witnesses: tuple
    # where the promoted object may legally live
    source_storage_class: str
    target_storage_class: str

    def __post_init__(self) -> None:
        for name in (
            "gate_id", "from_layer", "to_layer", "authority_before", "authority_after",
            "pre_hash", "validator_id", "source_storage_class", "target_storage_class",
        ):
            _require_nonempty_str(name, getattr(self, name))
        _require_nonempty_tuple("information_loss", self.information_loss, "UNDECLARED_LOSS")
        _require_nonempty_tuple("assumptions", self.assumptions, "UNDECLARED_ASSUMPTION")
        if self.from_layer == self.to_layer and self.source_storage_class == self.target_storage_class:
            raise GateConstructionError(
                f"gate '{self.gate_id}': neither layer nor storage class changes; "
                "identity promotion is not a promotion"
            )
        if self.reversible and not self.inverse_gate_id:
            raise GateConstructionError(
                f"gate '{self.gate_id}' claims reversible=True without an inverse_gate_id: "
                "reversibility without an inverse path is a false declaration"
            )
        if not self.reversible and self.inverse_gate_id is not None:
            raise GateConstructionError(
                f"gate '{self.gate_id}' is reversible=False yet names inverse_gate_id "
                f"'{self.inverse_gate_id}': a non-reversible gate may not advertise an inverse"
            )

    def inverse(self) -> str:
        if not self.reversible or self.inverse_gate_id is None:
            raise IrreversibleGateError(
                f"gate '{self.gate_id}' is not reversible: no inverse gate exists"
            )
        return self.inverse_gate_id

    def to_dict(self) -> dict:
        return {
            "gate_id": self.gate_id,
            "from_layer": self.from_layer,
            "to_layer": self.to_layer,
            "information_loss": list(self.information_loss),
            "assumptions": list(self.assumptions),
            "authority_before": self.authority_before,
            "authority_after": self.authority_after,
            "reversible": self.reversible,
            "inverse_gate_id": self.inverse_gate_id,
            "pre_hash": self.pre_hash,
            "validator_id": self.validator_id,
            "required_witnesses": list(self.required_witnesses),
            "source_storage_class": self.source_storage_class,
            "target_storage_class": self.target_storage_class,
        }


@dataclass(frozen=True)
class Policy:
    """Deterministic policy environment for promote(). Everything explicit."""

    validators: Mapping = field(default_factory=dict)
    assumption_checks: Mapping = field(default_factory=dict)
    # allowed (authority_before, authority_after) pairs — default deny
    authority_transitions: frozenset = frozenset()
    # allowed (source_storage_class, target_storage_class) pairs — default deny
    storage_transitions: frozenset = frozenset()
    # capabilities held by the acting seat — VALIDATED != ADMITTED
    capabilities: frozenset = frozenset()


def state_hash(state: dict) -> str:
    return sha256_hex(canonical_json(state))


def candidate_hash(candidate: dict) -> str:
    return sha256_hex(canonical_json(candidate))


def genesis_state(layers: list) -> dict:
    return {"layers": {name: [] for name in layers}}


def _reject(reason: str, pre: str, cand: str, gate_id: str | None) -> dict:
    return {
        "receipt_type": RECEIPT_TYPE,
        "verdict": "REJECT",
        "reason": reason,
        "gate_id": gate_id,
        "pre_hash": pre,
        "candidate_hash": cand,
        "post_hash": pre,
        "authority": False,
    }


def promote(
    state: dict,
    candidate: dict,
    gate: PromotionGate | None,
    *,
    witness_bundle: Mapping | None,
    policy: Policy,
) -> tuple[dict, dict]:
    """Attempt one promotion through one explicit gate. Partial and fail-closed.

    Returns (new_state, receipt). On any rejection new_state IS the input
    state, unmutated: the rejection exists only as a receipt.
    """
    pre = state_hash(state)
    cand = candidate_hash(candidate)

    if gate is None:
        return state, _reject("REJECT_NO_GATE", pre, cand, None)

    if candidate.get("layer") != gate.from_layer:
        return state, _reject(
            f"WRONG_SOURCE_LAYER:{candidate.get('layer')}!={gate.from_layer}", pre, cand, gate.gate_id
        )

    if gate.pre_hash != pre:
        return state, _reject("STALE_PRE_STATE", pre, cand, gate.gate_id)

    for assumption in gate.assumptions:
        check = policy.assumption_checks.get(assumption)
        if check is None:
            return state, _reject(f"UNKNOWN_ASSUMPTION:{assumption}", pre, cand, gate.gate_id)
        if not check(candidate, state):
            return state, _reject(f"UNSATISFIED_ASSUMPTION:{assumption}", pre, cand, gate.gate_id)

    payload_hash = sha256_hex(canonical_json(candidate.get("payload", {})))
    bundle = witness_bundle or {}
    for witness_id in gate.required_witnesses:
        witness = bundle.get(witness_id)
        if witness is None:
            return state, _reject(f"WITNESS_MISSING:{witness_id}", pre, cand, gate.gate_id)
        if witness.get("witness_hash") != payload_hash:
            return state, _reject(f"FAKE_WITNESS:{witness_id}", pre, cand, gate.gate_id)

    validator = policy.validators.get(gate.validator_id)
    if validator is None:
        return state, _reject(f"UNKNOWN_VALIDATOR:{gate.validator_id}", pre, cand, gate.gate_id)
    valid, why = validator(candidate.get("payload", {}))
    if not valid:
        return state, _reject(f"VALIDATION_FAILED:{why}", pre, cand, gate.gate_id)

    capability = f"PASS:{gate.gate_id}"
    if capability not in policy.capabilities:
        return state, _reject(f"CAPABILITY_MISSING:{capability}", pre, cand, gate.gate_id)

    if (gate.authority_before, gate.authority_after) not in policy.authority_transitions:
        return state, _reject(
            f"ILLEGAL_AUTHORITY_PROMOTION:{gate.authority_before}->{gate.authority_after}",
            pre, cand, gate.gate_id,
        )

    if (gate.source_storage_class, gate.target_storage_class) not in policy.storage_transitions:
        return state, _reject(
            f"ILLEGAL_LOCATION_PROMOTION:{gate.source_storage_class}->{gate.target_storage_class}",
            pre, cand, gate.gate_id,
        )

    new_state = copy.deepcopy(state)
    new_state["layers"].setdefault(gate.to_layer, []).append(
        {"payload": candidate["payload"], "storage_class": gate.target_storage_class}
    )
    post = state_hash(new_state)

    receipt = {
        "receipt_type": RECEIPT_TYPE,
        "verdict": "ADMITTED",
        "gate_id": gate.gate_id,
        "pre_hash": pre,
        "candidate_hash": cand,
        "witness_hash": sha256_hex(canonical_json(dict(bundle))),
        "post_hash": post,
        "information_loss": list(gate.information_loss),
        "assumptions": list(gate.assumptions),
        "authority_delta": [gate.authority_before, gate.authority_after],
        "storage_delta": [gate.source_storage_class, gate.target_storage_class],
        "reversible": gate.reversible,
        "inverse_gate_id": gate.inverse_gate_id,
        "authority": False,
    }
    return new_state, receipt


def replay(
    genesis: dict,
    journal: list,
    policy: Policy,
) -> tuple[dict, list]:
    """Re-run every journal attempt from genesis. Returns (final_state, receipts).

    Journal entries: {"candidate", "gate" (PromotionGate|None), "witness_bundle",
    "receipt" (optional recorded receipt)}. Raises ValueError on replay
    divergence: a first-class failure, not a warning.
    """
    state = genesis
    receipts: list = []
    for i, entry in enumerate(journal):
        state, receipt = promote(
            state,
            entry["candidate"],
            entry.get("gate"),
            witness_bundle=entry.get("witness_bundle"),
            policy=policy,
        )
        recorded = entry.get("receipt")
        if recorded is not None and recorded != receipt:
            raise ValueError(
                f"replay divergence at journal[{i}]: recorded verdict "
                f"{recorded.get('verdict')} != recomputed {receipt.get('verdict')}"
            )
        receipts.append(receipt)
    return state, receipts
