"""
ecp_verdict_algebra.py — HELEN Epistemic Control Plane unified verdict types.
authority: NONE · NON_SOVEREIGN · diagnostic only

Every probe in the ECP emits a typed Verdict. This prevents category errors
between probe classes and enforces the routing/admission distinction.

Probe classes:
  P0 OBSERVER  — detects state, cannot block
  P1 GUARD     — blocks structurally invalid mutations
  P2 ROUTER    — flags semantic risk, routes to reducer / human review
  P3 ADMISSION — contributes to reducer acceptance when formalized

Verdict algebra:
  OBSERVE(signal)             — P0 only; informational
  WARN(reason)                — P0/P1; informational with escalation flag
  BLOCK(reason)               — P1 only; hard gate
  ROUTE(reason, reviewer)     — P2; semantic risk flag → review queue
  HOLD(reason, revocable)     — P1/P2; suspended pending condition
  CANDIDATE(receipts)         — P2/P3; receipt bundle for reducer
  ADMIT(receipt)              — P3 only; reducer acceptance
  REJECT(reason)              — P3 only; final rejection

Admission invariant (preserved — no verdict can bypass this):
  ADMISSION(P) = Claim(P) ∧ Evidence(P) ∧ Receipt(P) ∧ CHRONOS(P)
               ∧ RequiredProbePass(P) ∧ RequiredSemanticReceipt(P)

No weighted score may compensate for a missing gate.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ProbeClass(Enum):
    P0_OBSERVER = "P0_OBSERVER"   # detects, cannot block
    P1_GUARD = "P1_GUARD"         # blocks structural failures
    P2_ROUTER = "P2_ROUTER"       # flags semantic risk, routes
    P3_ADMISSION = "P3_ADMISSION" # contributes to reducer acceptance


class VerdictKind(Enum):
    OBSERVE = "OBSERVE"
    WARN = "WARN"
    BLOCK = "BLOCK"
    ROUTE = "ROUTE"
    HOLD = "HOLD"
    CANDIDATE = "CANDIDATE"
    ADMIT = "ADMIT"
    REJECT = "REJECT"


# Allowed verdict kinds per probe class
_ALLOWED: dict[ProbeClass, set[VerdictKind]] = {
    ProbeClass.P0_OBSERVER:  {VerdictKind.OBSERVE, VerdictKind.WARN},
    ProbeClass.P1_GUARD:     {VerdictKind.OBSERVE, VerdictKind.WARN, VerdictKind.BLOCK, VerdictKind.HOLD},
    ProbeClass.P2_ROUTER:    {VerdictKind.OBSERVE, VerdictKind.WARN, VerdictKind.ROUTE, VerdictKind.HOLD, VerdictKind.CANDIDATE},
    ProbeClass.P3_ADMISSION: {VerdictKind.CANDIDATE, VerdictKind.ADMIT, VerdictKind.REJECT},
}


@dataclass
class Verdict:
    probe: str
    probe_class: ProbeClass
    kind: VerdictKind
    reason: str
    detail: dict[str, Any] = field(default_factory=dict)
    reviewer: str | None = None         # P2_ROUTER: target reviewer
    revocable: bool = True              # HOLD: whether condition can be cleared
    requires: str | None = None         # ROUTE: receipt type required to proceed
    semantic_claim: bool = False        # explicitly marks semantic vs structural

    def __post_init__(self) -> None:
        allowed = _ALLOWED.get(self.probe_class, set())
        if self.kind not in allowed:
            raise ValueError(
                f"{self.probe_class.value} may not emit {self.kind.value}. "
                f"Allowed: {[k.value for k in allowed]}"
            )

    @property
    def is_blocking(self) -> bool:
        return self.kind == VerdictKind.BLOCK

    @property
    def is_routing(self) -> bool:
        return self.kind == VerdictKind.ROUTE

    def to_dict(self) -> dict:
        return {
            "probe": self.probe,
            "probe_class": self.probe_class.value,
            "verdict": self.kind.value,
            "reason": self.reason,
            "detail": self.detail,
            "reviewer": self.reviewer,
            "revocable": self.revocable,
            "requires": self.requires,
            "semantic_claim": self.semantic_claim,
        }


# ------------------------------------------------------------------ #
# Canonical probe surface registry                                    #
# ------------------------------------------------------------------ #

PROBE_REGISTRY: dict[str, ProbeClass] = {
    "witness_projection":       ProbeClass.P1_GUARD,
    "false_green_lint":         ProbeClass.P1_GUARD,
    "k_tau_lint":               ProbeClass.P1_GUARD,
    "k8_lint":                  ProbeClass.P1_GUARD,
    "citation_graph_probe":     ProbeClass.P2_ROUTER,
    "garden_autoresearch":      ProbeClass.P0_OBSERVER,
    "semantic_reviewer":        ProbeClass.P3_ADMISSION,
}


# ------------------------------------------------------------------ #
# Convenience constructors                                            #
# ------------------------------------------------------------------ #

def observe(probe: str, reason: str, **detail) -> Verdict:
    pc = PROBE_REGISTRY.get(probe, ProbeClass.P0_OBSERVER)
    return Verdict(probe=probe, probe_class=pc, kind=VerdictKind.OBSERVE,
                   reason=reason, detail=detail)


def warn(probe: str, reason: str, **detail) -> Verdict:
    pc = PROBE_REGISTRY.get(probe, ProbeClass.P1_GUARD)
    return Verdict(probe=probe, probe_class=pc, kind=VerdictKind.WARN,
                   reason=reason, detail=detail)


def block(probe: str, reason: str, **detail) -> Verdict:
    pc = PROBE_REGISTRY.get(probe, ProbeClass.P1_GUARD)
    return Verdict(probe=probe, probe_class=pc, kind=VerdictKind.BLOCK,
                   reason=reason, detail=detail)


def route(probe: str, reason: str, reviewer: str, requires: str,
          semantic_claim: bool = False, **detail) -> Verdict:
    pc = PROBE_REGISTRY.get(probe, ProbeClass.P2_ROUTER)
    return Verdict(probe=probe, probe_class=pc, kind=VerdictKind.ROUTE,
                   reason=reason, reviewer=reviewer, requires=requires,
                   semantic_claim=semantic_claim, detail=detail)
