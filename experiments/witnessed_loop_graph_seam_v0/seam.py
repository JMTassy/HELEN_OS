"""WITNESSED_LOOP_GRAPH_SEAM_V0 — the anchor cut.

Proves ONE narrow constitutional property:

    A self-confirming group of agents cannot promote a claim
    without independent evidence.

    producer agreement + reviewer agreement  =/=>  admission
    Only a fresh, structurally-independent witness can close the gate.

Scope: LOCAL_NON_SOVEREIGN_PROOF. authority=false. ledger_effect=none.
canon_effect=false. This module MUST NOT mutate canon. ADMITTABLE is the
highest allowed positive result — it means "evidence-qualified for promotion",
NOT "promoted". Crossing ADMITTABLE -> ADMIT is a later, operator-authorized layer.

Deterministic and dependency-free (Python stdlib only). No model calls.
`now` is always passed in explicitly; nothing here reads the wall clock.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Iterable

# ── Closed result algebra ─────────────────────────────────────────────────────
# Do NOT return "ADMIT" here — that would cross from evidence qualification
# into authority.
HOLD = "HOLD"                      # no usable independent anchor exists
HOLD_REOBSERVE = "HOLD_REOBSERVE"  # independent anchors exist, but all are stale
HOLD_CONFLICT = "HOLD_CONFLICT"    # fresh independent anchors both confirm and contradict
REJECT = "REJECT"                  # fresh independent anchor contradicts, none confirm
ADMITTABLE = "ADMITTABLE"          # fresh independent anchor confirms, none contradict

RESULTS = frozenset({HOLD, HOLD_REOBSERVE, HOLD_CONFLICT, REJECT, ADMITTABLE})


# ── Time (ISO-8601, explicit, deterministic) ──────────────────────────────────
def _parse(ts: str) -> datetime:
    """Parse an ISO-8601 timestamp. Accepts trailing 'Z'. Tz-aware (UTC)."""
    if ts.endswith("Z"):
        ts = ts[:-1] + "+00:00"
    dt = datetime.fromisoformat(ts)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


# ── Independence predicate — claim-relative, conservative, negative ───────────
# V0 rule: a witness is independent ONLY if it shares NO decisive dependency
# with the claim's producing lineage. False independence is more dangerous than
# an extra check, so every condition must hold. Missing fields fail closed.
def is_structurally_independent(claim: dict[str, Any], witness: dict[str, Any]) -> bool:
    """True iff `witness` shares no decisive dependency with `claim`'s lineage.

    Fails closed (returns False) if any required field is absent — an
    under-specified witness is never treated as independent.
    """
    try:
        return all([
            witness["claim_id"] == claim["claim_id"],
            witness["source_class"] == "INDEPENDENT_RUNTIME_PROBE",
            witness["producer_id"] != claim["producer_id"],
            witness["input_hash"] != claim["source_packet_hash"],
            witness["method"] not in claim["derivation_methods"],
            _parse(witness["observed_at"]) >= _parse(claim["created_at"]),
        ])
    except (KeyError, ValueError, TypeError):
        return False


def is_fresh(witness: dict[str, Any], now: str) -> bool:
    """True iff `witness` has not exceeded its freshness horizon at `now`.

    previously witnessed  =/=>  currently true.
    """
    try:
        return _parse(now) <= _parse(witness["fresh_until"])
    except (KeyError, ValueError, TypeError):
        return False


def is_usable_anchor(claim: dict[str, Any], witness: dict[str, Any], now: str) -> bool:
    """usable_anchor(w,c,now) iff structurally_independent(w,c) AND fresh(w,now).

    The distinction matters:  not independent  !=  independent but stale.
    Those produce different lawful outcomes (HOLD vs HOLD_REOBSERVE).
    """
    return is_structurally_independent(claim, witness) and is_fresh(witness, now)


# ── The anchor-cut reducer ────────────────────────────────────────────────────
def reduce_claim(
    claim: dict[str, Any],
    reviews: Iterable[dict[str, Any]],
    witnesses: Iterable[dict[str, Any]],
    now: str,
) -> dict[str, Any]:
    """Decide whether `claim` may be promoted.

    `reviews` is accepted but INTENTIONALLY UNUSED for the gate. That is not an
    omission — it is the property being proven: n supportive reviews from inside
    the claim's own lineage do not, for any finite n, make a claim ADMITTABLE.
    Reviews may still carry diagnostics; they simply cannot close the anchor cut.
    """
    reviews = list(reviews)  # consumed only for the diagnostic count below
    witnesses = list(witnesses)

    structurally_independent = [
        w for w in witnesses if is_structurally_independent(claim, w)
    ]
    fresh_independent = [
        w for w in structurally_independent if is_fresh(w, now)
    ]

    def envelope(result: str, reason_codes: list[str]) -> dict[str, Any]:
        assert result in RESULTS, f"illegal result {result!r}"
        return {
            "result": result,
            "reason_codes": reason_codes,
            "authority": "REDUCER",
            "canon_effect": False,          # this seam never mutates canon
            "diagnostics": {
                # surfaced but non-decisive — proves reviews carry no gate power
                "reviews_seen": len(reviews),
                "supportive_reviews": sum(
                    1 for r in reviews if r.get("verdict") == "SUPPORT"
                ),
                "witnesses_seen": len(witnesses),
                "structurally_independent": len(structurally_independent),
                "fresh_independent": len(fresh_independent),
            },
        }

    # 1. No structurally-independent witness at all -> agreement is not evidence.
    if not structurally_independent:
        return envelope(HOLD, ["NO_INDEPENDENT_ANCHOR"])

    # 2. Independent anchors exist but every one is stale.
    if not fresh_independent:
        return envelope(HOLD_REOBSERVE, ["INDEPENDENT_ANCHOR_STALE"])

    confirms = [w for w in fresh_independent if w.get("observed_value") == claim["value"]]
    contradicts = [w for w in fresh_independent if w.get("observed_value") != claim["value"]]

    # 3. Fresh independent anchors disagree with each other.
    #    The question is not "is the claim false?" but "may it be promoted?"
    #    Under independent conflict, the answer is no.
    if confirms and contradicts:
        return envelope(HOLD_CONFLICT, ["INDEPENDENT_ANCHOR_CONFLICT"])

    # 4. Direct independent contradiction, nothing confirms.
    if contradicts:
        return envelope(REJECT, ["INDEPENDENT_WITNESS_CONTRADICTS_CLAIM"])

    # 5. At least one fresh independent anchor confirms, none contradict.
    #    Highest allowed positive result. NOT canonical admission.
    return envelope(ADMITTABLE, ["INDEPENDENT_ANCHOR_CONFIRMS_CLAIM"])


# Anchor-Cut Corollary, executable:
#   for any finite n, n supportive reviews sharing the claim's lineage
#   never raise the result above HOLD on their own.
def corollary_reviews_cannot_admit(claim: dict[str, Any], n: int, now: str) -> bool:
    """Return True iff n same-lineage supportive reviews (no witnesses) => HOLD."""
    reviews = [
        {"reviewer_id": f"reviewer_{i}", "verdict": "SUPPORT",
         "source_packet_hash": claim["source_packet_hash"]}
        for i in range(n)
    ]
    return reduce_claim(claim, reviews, [], now)["result"] == HOLD
