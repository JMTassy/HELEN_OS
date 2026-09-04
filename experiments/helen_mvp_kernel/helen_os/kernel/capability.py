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

from helen_os.ledger.hash_chain import canonical_json, sha256_hex


def h_v(x) -> str:
    """Canonical hash — same canonicalizer as the ledger/HAL. No second one."""
    return sha256_hex(canonical_json(x))


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
    # h_pre — CALLER CONTRACT (E002): pre_state_hash MUST be a TOTAL commitment over
    # all admission-relevant state (e.g. h_v(full_canonical_state)), not a partial
    # digest. The layer checks equality only; it cannot see fields the caller omitted.
    # Under-hashing lets a mutation to an unhashed field slip a stale-context write
    # through — a caller violation, not a kernel defect. Total-hashing catches it via
    # PRE_STATE_MISMATCH (see test_hal_e002_total_state_commitment).
    pre_state_hash: str
    scope: str             # e.g. "ledger.append"
    expiry_tick: int
    nonce: str
    # holder — E003: binds κ to its intended holder so cross-actor HANDOFF is refused
    # (affine consumption only stops REUSE). Opaque id in this MVP; the production form
    # is holder_pubkey + a signature check at invoke. Empty "" = unbound (legacy,
    # back-compatible). Residual after binding: credential/key theft still lets the
    # true-holder-secret bearer invoke — reduction, not elimination.
    holder: str = ""
    # effect_hash — E004: binds κ to ONE exact effect, so a κ minted for effect e1 cannot
    # be redirected to a different e2 sharing the same scope (scope authorizes a CLASS).
    # Empty "" = unbound (legacy). CRITICAL (E004 finding): the executor DERIVES the
    # effect hash from the presented request at the choke point — it is NOT a caller-
    # supplied assertion. Residual: binds_hash (candidate) and pre_state_hash remain
    # caller-asserted in this MVP; deriving them needs a governed-state object +
    # canonical candidate — the "derive all facts at choke point" upgrade (next epoch).
    effect_hash: str = ""


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
        holder: str = "",
        effect_hash: str = "",
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
            holder=holder,
            effect_hash=effect_hash,
        )


@dataclass(frozen=True)
class InvokeResult:
    status: str  # EXECUTED | ALREADY_CONSUMED | EXPIRED | BIND_MISMATCH | PRE_STATE_MISMATCH | SCOPE_MISMATCH | HOLDER_MISMATCH | EFFECT_MISMATCH | CAP_TYPE_MISMATCH | STATE_MIGRATED
    effect_ran: bool


class Executor:
    """Affine invoker: one successful use consumes κ forever."""

    def __init__(self, clock: LogicalClock, state_provider: Optional[Callable[[], str]] = None) -> None:
        self._clock = clock
        self._consumed: set[tuple[str, str]] = set()
        self._active: Optional[tuple[str, str]] = None
        # E006: derive-at-choke-point for pre-state. When set, the executor obtains the
        # CURRENT governed-state hash from this authoritative source and IGNORES the
        # caller-supplied pre_state_hash — closing the stale-state caller-assertion gap.
        # None = legacy (trusts the caller-supplied pre_state_hash).
        self._state_provider = state_provider

    def invoke(
        self,
        cap: Capability,
        *,
        expected_hash: str,
        pre_state_hash: str,
        scope: str,
        effect: Optional[Callable[[], None]] = None,
        presented_holder: str = "",
        effect_request: object = None,
    ) -> InvokeResult:
        # #10 forged-type guard: a duck-typed dict must be REFUSED cleanly, not crash
        # with AttributeError. CorrectType(κ) ⊬ ValidCapability(κ) — this only blocks
        # non-Capability objects; a forged real Capability instance is a separate,
        # documented residual (needs a mint registry, not isinstance).
        if not isinstance(cap, Capability):
            return InvokeResult("CAP_TYPE_MISMATCH", False)
        key = (cap.cap_id, cap.nonce)
        if key in self._consumed:
            return InvokeResult("ALREADY_CONSUMED", False)
        # E003 holder binding: a bound κ (holder != "") refuses any invoker who does
        # not present the matching holder credential — cross-actor handoff blocked.
        # Unbound κ (holder == "") keeps legacy behavior. Checked BEFORE consumption
        # so a wrong-holder attempt neither fires nor spends the capability.
        if cap.holder != "" and cap.holder != presented_holder:
            return InvokeResult("HOLDER_MISMATCH", False)
        if self._clock.now() > cap.expiry_tick:
            return InvokeResult("EXPIRED", False)
        if cap.binds_hash != expected_hash:
            return InvokeResult("BIND_MISMATCH", False)
        # E006: if an authoritative state source is present, DERIVE the current state
        # hash and compare to the capability — the caller-supplied pre_state_hash is
        # IGNORED. A stale-state attack fails even if the caller echoes cap.pre_state_hash,
        # because the derived current hash reflects the ACTUAL (moved) governed state.
        effective_pre_state = self._state_provider() if self._state_provider else pre_state_hash
        if cap.pre_state_hash != effective_pre_state:
            return InvokeResult("PRE_STATE_MISMATCH", False)
        if cap.scope != scope:
            return InvokeResult("SCOPE_MISMATCH", False)
        # E004 exact-effect binding: the executor DERIVES the effect hash from the
        # presented request (h_v = sha256(canonical_json)) — never trusts a caller-
        # supplied effect_hash string. A κ bound to effect e1 refuses a different e2.
        if cap.effect_hash != "":
            derived = h_v(effect_request)
            if derived != cap.effect_hash:
                return InvokeResult("EFFECT_MISMATCH", False)
        self._consumed.add(key)  # consume BEFORE effect: no retry window
        self._active = key       # sink guards accept ONLY during this window
        try:
            if effect is not None:
                effect()
                # E007: atomic recheck AFTER the effect DETECTS intra-transaction migration
                # — this does NOT prevent the bad transition (the effect at line above has
                # ALREADY run against the moved state; effect_ran=True below says so). It is a
                # compensating detection signal (STATE_MIGRATED) enabling downstream
                # reconciliation/rollback. If a re-entrant effect (or a nested invoke it
                # triggered) moved the governed state, the post-effect derivation no longer
                # matches cap.pre_state_hash. Detects the RE-ENTRANCY case. RESIDUAL: true
                # multi-thread concurrency (another thread mutating mid-effect) is neither
                # detected nor prevented — needs a lock/version-CAS (infrastructure; MVP is
                # single-threaded). E007 makes the single-threaded assumption CHECKED (after
                # the fact) for re-entrancy, not silent — but it is detection, not prevention.
                if self._state_provider is not None:
                    if self._state_provider() != cap.pre_state_hash:
                        return InvokeResult("STATE_MIGRATED", True)
        finally:
            self._active = None
        return InvokeResult("EXECUTED", True)

    def is_live(self, cap: Capability) -> bool:
        return (cap.cap_id, cap.nonce) not in self._consumed and self._clock.now() <= cap.expiry_tick

    def authorizes(self, cap: Optional[Capability]) -> bool:
        """True only while THIS executor is mid-invocation with exactly this κ.
        A live cap presented directly to a sink (bypassing invoke) is refused."""
        return cap is not None and self._active == (cap.cap_id, cap.nonce)
