"""Affine capability layer — κ = (id, h_c, h_pre, scope, expiry, nonce).

🔵 OBSERVED · NON_SOVEREIGN sandbox · authority=NONE until operator admission.

Laws enforced here:
  - mint requires admission_decision == "ADMIT" (Γ bridge; HOLD/REJECT/HAL-PASS cannot mint)
  - invoke succeeds at most once per capability (affine consumption; replay of a
    receipt as re-authorization is structurally impossible)
  - expiry/scope/bind mismatches produce no effect
  - time is a LogicalClock tick — no wall clock, replay-pure (K-tau mu_DETERMINISM)
"""
from __future__ import annotations

import secrets
from dataclasses import dataclass, field
from typing import Callable, Optional


class LogicalClock:
    """Deterministic tick counter. No wall time anywhere in this layer."""

    def __init__(self, start: int = 0) -> None:
        self._t = start

    def now(self) -> int:
        return self._t

    def tick(self, n: int = 1) -> int:
        self._t += n
        return self._t


@dataclass(frozen=True)
class Capability:
    cap_id: str
    binds_hash: str        # h_c — candidate hash this κ authorizes
    pre_state_hash: str    # h_pre — state the mutation must start from
    scope: str             # e.g. "ledger.append"
    expiry_tick: int
    nonce: str


class CapabilityFactory:
    """Only lawful κ mint. The ADMIT check is the B_Γ bridge in code."""

    def __init__(self, clock: LogicalClock) -> None:
        self._clock = clock

    def mint(
        self,
        *,
        binds_hash: str,
        pre_state_hash: str,
        scope: str,
        admission_decision: str,
        ttl_ticks: int = 100,
    ) -> Capability:
        if admission_decision != "ADMIT":
            raise PermissionError(
                f"E_MINT_WITHOUT_ADMIT: admission_decision={admission_decision!r}"
            )
        return Capability(
            cap_id=f"cap_{secrets.token_hex(8)}",
            binds_hash=binds_hash,
            pre_state_hash=pre_state_hash,
            scope=scope,
            expiry_tick=self._clock.now() + ttl_ticks,
            nonce=secrets.token_hex(8),
        )


@dataclass(frozen=True)
class InvokeResult:
    status: str  # EXECUTED | ALREADY_CONSUMED | EXPIRED | BIND_MISMATCH | PRE_STATE_MISMATCH | SCOPE_MISMATCH
    effect_ran: bool


class Executor:
    """Affine invoker: one successful use consumes κ forever."""

    def __init__(self, clock: LogicalClock) -> None:
        self._clock = clock
        self._consumed: set[tuple[str, str]] = set()
        self._active: Optional[tuple[str, str]] = None

    def invoke(
        self,
        cap: Capability,
        *,
        expected_hash: str,
        pre_state_hash: str,
        scope: str,
        effect: Optional[Callable[[], None]] = None,
    ) -> InvokeResult:
        key = (cap.cap_id, cap.nonce)
        if key in self._consumed:
            return InvokeResult("ALREADY_CONSUMED", False)
        if self._clock.now() > cap.expiry_tick:
            return InvokeResult("EXPIRED", False)
        if cap.binds_hash != expected_hash:
            return InvokeResult("BIND_MISMATCH", False)
        if cap.pre_state_hash != pre_state_hash:
            return InvokeResult("PRE_STATE_MISMATCH", False)
        if cap.scope != scope:
            return InvokeResult("SCOPE_MISMATCH", False)
        self._consumed.add(key)  # consume BEFORE effect: no retry window
        self._active = key       # sink guards accept ONLY during this window
        try:
            if effect is not None:
                effect()
        finally:
            self._active = None
        return InvokeResult("EXECUTED", True)

    def is_live(self, cap: Capability) -> bool:
        return (cap.cap_id, cap.nonce) not in self._consumed and self._clock.now() <= cap.expiry_tick

    def authorizes(self, cap: Optional[Capability]) -> bool:
        """True only while THIS executor is mid-invocation with exactly this κ.
        A live cap presented directly to a sink (bypassing invoke) is refused."""
        return cap is not None and self._active == (cap.cap_id, cap.nonce)
