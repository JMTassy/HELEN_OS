"""Witness verification MVP — cleartext Live + set coverage.

NON_SOVEREIGN · authority=false · ledger_effect=none.

A witness is not a story; it is a coverage receipt claiming "I evaluated
surface S_P(x) of package x under predicate P." The verifier RECOMPUTES
whether the claim holds:

    Live(W, x) = B_bind ∧ B_coverage ∧ B_activity ∧ B_consistency

Laws hardcoded here:
  - The receipt's own `claims_live` flag is NEVER read for the verdict.
    The witness does not get to set live=True.
  - required_ids are recomputed from x, never taken from W.
  - PASS ⇒ Live ∧ P(x);  ¬Live ⇒ UNKNOWN;  ∅ ⇏ green.
  - There is NO admit function in this module. HAL_PASS ⊬ ADMIT — the
    gate consumes verdicts elsewhere; a verifier that could admit would
    be the collapse this protocol exists to prevent.
  - A validator must witness its own engagement before it may witness
    anything else: an ill-typed or vacuous receipt is UNKNOWN, not FAIL —
    absence of evidence is not evidence of failure, and never of success.

Deterministic: hashlib over canonical JSON; no wall-time, no randomness.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Callable, Mapping

PASS, FAIL, UNKNOWN = "PASS", "FAIL", "UNKNOWN"

EMPTY_FORBIDDEN = "EMPTY_FORBIDDEN"
EMPTY_ALLOWED = "EMPTY_ALLOWED"


def package_hash(x: Mapping[str, Any]) -> str:
    canon = json.dumps(x, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()


def required_ids(x: Mapping[str, Any]) -> frozenset[str]:
    """S_P(x): the surface, recomputed from the package itself."""
    return frozenset(item["id"] for item in x.get("items", []))


@dataclass(frozen=True)
class CoverageReceipt:
    witness_id: str
    input_hash: str
    checked_ids: tuple = field(default_factory=tuple)
    evidence: tuple = field(default_factory=tuple)  # ({"item_id","package_hash",...},)
    claims_live: bool = False  # deliberately ignored by the verifier


def verify_witness(receipt: Any,
                   x: Mapping[str, Any],
                   predicate: Callable[[Mapping[str, Any], tuple], bool],
                   empty_policy: str = EMPTY_FORBIDDEN) -> dict[str, Any]:
    """The end-to-end sequence. Extensional: checks what was touched,
    never how eloquent the report is."""
    checks = {"bind_ok": False, "coverage_ok": False,
              "activity_ok": False, "consistency_ok": False}

    def verdict(v, reason):
        return {"verdict": v, "reason": reason, "checks": dict(checks)}

    # 1. typing — reject ill-typed receipts as UNKNOWN
    if not isinstance(receipt, CoverageReceipt):
        return verdict(UNKNOWN, "E_ILL_TYPED")

    # 2. recompute the surface from x, not from W
    required = required_ids(x)
    xh = package_hash(x)

    # 3. bind
    if receipt.input_hash != xh:
        return verdict(UNKNOWN, "E_STALE_BIND")
    checks["bind_ok"] = True

    # 4. coverage — set equality AND no duplicate inflation
    checked = list(receipt.checked_ids)
    if len(checked) != len(set(checked)):
        return verdict(UNKNOWN, "E_DUPLICATE_IDS")
    if set(checked) != set(required):
        return verdict(UNKNOWN, "E_COVERAGE_GAP")
    checks["coverage_ok"] = True

    # 5. activity — vacuous work is not work
    if not receipt.evidence:
        if required and empty_policy != EMPTY_ALLOWED:
            return verdict(UNKNOWN, "E_VACUOUS")
        if required and empty_policy == EMPTY_ALLOWED:
            return verdict(UNKNOWN, "E_VACUOUS")  # non-empty x still needs evidence
    checks["activity_ok"] = True

    # 6. consistency — every evidence item bound to THIS package
    for ev in receipt.evidence:
        if ev.get("package_hash") != xh:
            return verdict(FAIL, "E_FOREIGN_EVIDENCE")
        if ev.get("item_id") not in required:
            return verdict(FAIL, "E_EVIDENCE_OFF_SURFACE")
    checks["consistency_ok"] = True

    # 7. predicate — only now, under Live, is P consulted
    try:
        holds = bool(predicate(x, receipt.evidence))
    except Exception:
        return verdict(UNKNOWN, "E_PREDICATE_ERROR")
    if holds:
        return verdict(PASS, "OK")
    return verdict(FAIL, "E_PREDICATE_FALSE")


def aggregate(verdicts: list[Mapping[str, Any]]) -> str:
    """Multi-invariant aggregation: FAIL dominates, UNKNOWN taints,
    PASS only if unanimous. An empty panel proves nothing."""
    if not verdicts:
        return UNKNOWN
    vs = [v["verdict"] for v in verdicts]
    if FAIL in vs:
        return FAIL
    if UNKNOWN in vs:
        return UNKNOWN
    return PASS


def independent_components(witness_ids: list[str],
                           dependence_edges: list[tuple[str, str]]) -> int:
    """Gate weight counts independent components of the dependence graph,
    not receipts: 2 receipts ⇏ 2 independent witnesses."""
    ids = sorted(set(witness_ids))
    parent = {w: w for w in ids}

    def find(w):
        while parent[w] != w:
            parent[w] = parent[parent[w]]
            w = parent[w]
        return w

    for a, b in dependence_edges:
        if a in parent and b in parent:
            parent[find(a)] = find(b)
    return len({find(w) for w in ids})
