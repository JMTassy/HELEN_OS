from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Iterable, Mapping


class HistoryFiberError(ValueError):
    pass


def canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_hex(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def state_hash(state: Mapping[str, Any]) -> str:
    return sha256_hex(canonical_json(dict(state)))


@dataclass(frozen=True)
class Movement:
    movement_id: str
    pre_hash: str
    post_state: Mapping[str, Any]
    effectful: bool = True
    authority_ref: str | None = None
    receipt_ref: str | None = None
    obligations_generated: tuple[str, ...] = ()
    obligations_discharged: tuple[str, ...] = ()
    discharge_witnesses: Mapping[str, str] | None = None

    def __post_init__(self) -> None:
        if not self.movement_id.strip():
            raise HistoryFiberError("movement_id must be non-empty")
        if self.effectful and not self.authority_ref:
            raise HistoryFiberError("HF-012 RETROACTIVE_AUTHORITY_FORBIDDEN: effectful movement lacks authority_ref")
        if self.obligations_discharged:
            witnesses = dict(self.discharge_witnesses or {})
            missing = [o for o in self.obligations_discharged if not witnesses.get(o)]
            if missing:
                raise HistoryFiberError(
                    "HF-003 OBLIGATION_DISCHARGE_REQUIRES_WITNESS: " + ",".join(sorted(missing))
                )

    def fingerprint_body(self) -> dict[str, Any]:
        return {
            "movement_id": self.movement_id,
            "pre_hash": self.pre_hash,
            "post_hash": state_hash(self.post_state),
            "effectful": self.effectful,
            "authority_ref": self.authority_ref,
            "receipt_ref": self.receipt_ref,
            "obligations_generated": list(self.obligations_generated),
            "obligations_discharged": list(self.obligations_discharged),
            "discharge_witnesses": dict(sorted((self.discharge_witnesses or {}).items())),
        }


@dataclass(frozen=True)
class GovernedState:
    visible_state: Mapping[str, Any]
    movement_fingerprint: str
    open_obligations: frozenset[str]

    @property
    def visible_hash(self) -> str:
        return state_hash(self.visible_state)

    def constitutionally_equivalent(self, other: "GovernedState") -> bool:
        return (
            self.visible_hash == other.visible_hash
            and self.movement_fingerprint == other.movement_fingerprint
            and self.open_obligations == other.open_obligations
        )


def replay_history(
    genesis_state: Mapping[str, Any],
    movements: Iterable[Movement],
    *,
    genesis_obligations: Iterable[str] = (),
) -> GovernedState:
    current = dict(genesis_state)
    obligations = set(genesis_obligations)
    fingerprint_chain: list[dict[str, Any]] = []

    for movement in movements:
        expected = state_hash(current)
        if movement.pre_hash != expected:
            raise HistoryFiberError(
                f"HF-001 ORPHAN_OR_STALE_HISTORY: movement {movement.movement_id} pre_hash mismatch"
            )

        for obligation in movement.obligations_discharged:
            if obligation not in obligations:
                raise HistoryFiberError(
                    f"HF-003 OBLIGATION_DISCHARGE_REQUIRES_EXISTING_OBLIGATION: {obligation}"
                )
            obligations.remove(obligation)

        obligations.update(movement.obligations_generated)
        current = dict(movement.post_state)
        fingerprint_chain.append(movement.fingerprint_body())

    movement_fingerprint = sha256_hex(canonical_json(fingerprint_chain))
    return GovernedState(
        visible_state=current,
        movement_fingerprint=movement_fingerprint,
        open_obligations=frozenset(obligations),
    )


__all__ = [
    "GovernedState",
    "HistoryFiberError",
    "Movement",
    "canonical_json",
    "replay_history",
    "sha256_hex",
    "state_hash",
]
