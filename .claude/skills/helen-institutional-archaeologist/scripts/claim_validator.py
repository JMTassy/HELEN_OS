#!/usr/bin/env python3
"""Validate a CLAIMS_DELTA against the epistemic protocol.

Enforces mechanically what free-form reasoning drifts on: legal
access/claim states, grounding, witnessed promotions, the forbidden
promotions (a diagnosis never becomes a fact by repetition), typed
commercial amounts, and non-absorbing temporal states.

Input (stdin or file arg): JSON list of claims:
    {"id": str,
     "state": OBSERVED|REPORTED|INFERRED|HYPOTHESIZED|PROVEN|
              CONTRADICTED|NO_RECEIPT,
     "basis": [source refs],           # may be [] only for NO_RECEIPT
     "basis_access": access state of the weakest basis source,
     "promoted_from": str | absent,    # prior state if promoted
     "witness": str | absent,          # what earned the promotion
     "amount_state": str | absent,     # required if the claim carries a number
     "temporal": {"state": str, "outcome_receipt": str|null} | absent,
     "falsifier": str | absent}        # required for HYPOTHESIZED

Output: JSON verdict; exit 1 on any violation. Deterministic,
stdlib only. Run `claim_validator.py --selftest` first.
"""
from __future__ import annotations

import json
import sys

ACCESS_STATES = ("METADATA_SEEN", "CONTENT_OPENED", "CONTENT_EXTRACTED",
                 "CONTENT_CROSS_CORROBORATED", "NO_ACCESS")
CLAIM_STATES = ("OBSERVED", "REPORTED", "INFERRED", "HYPOTHESIZED",
                "PROVEN", "CONTRADICTED", "NO_RECEIPT")
COMMERCIAL_STATES = ("ESTIMATE", "REQUESTED", "LIKELY", "APPROVED",
                     "CONTRACTED", "INVOICED", "PAID")
TEMPORAL_STATES = ("DISCOVERED", "QUALIFYING", "PROBE", "GO", "BLOCKED",
                   "HOLD", "RECOVERED", "EXECUTING", "COMPLETED",
                   "LOST", "UNKNOWN")

# Promotions that no witness can cure — these are category errors,
# not missing evidence.
NEVER_PROMOTABLE = frozenset({
    ("HYPOTHESIZED", "OBSERVED"),   # a guess cannot become a sighting
    ("INFERRED", "OBSERVED"),       # a deduction is not a sighting
    ("REPORTED", "PROVEN"),         # hearsay proves nothing directly
    ("NO_RECEIPT", "OBSERVED"),
    ("NO_RECEIPT", "PROVEN"),
})
# Promotions that are legal ONLY with a named witness.
WITNESS_REQUIRED = frozenset({
    ("REPORTED", "OBSERVED"),       # witness = the primary artifact
    ("INFERRED", "PROVEN"),         # witness = corroborating root
    ("HYPOTHESIZED", "INFERRED"),
    ("HYPOTHESIZED", "PROVEN"),
    ("OBSERVED", "PROVEN"),         # witness = 2nd independent root
})
# Claim states that themselves demand strong access on their basis.
MIN_ACCESS = {
    "OBSERVED": ("CONTENT_OPENED", "CONTENT_EXTRACTED",
                 "CONTENT_CROSS_CORROBORATED"),
    "PROVEN": ("CONTENT_CROSS_CORROBORATED",),
}


def validate_claim(c: dict) -> list[dict]:
    errs = []
    cid = c.get("id", "?")

    def err(reason, **kw):
        errs.append({"claim": cid, "reason": reason, **kw})

    state = c.get("state")
    if state not in CLAIM_STATES:
        err("E_UNKNOWN_CLAIM_STATE", got=state)
        return errs

    basis = c.get("basis", [])
    if not basis and state != "NO_RECEIPT":
        err("E_UNGROUNDED_CLAIM")
    if basis and state == "NO_RECEIPT":
        err("E_NO_RECEIPT_WITH_BASIS")

    acc = c.get("basis_access")
    if basis:
        if acc not in ACCESS_STATES:
            err("E_UNKNOWN_ACCESS_STATE", got=acc)
        elif state in MIN_ACCESS and acc not in MIN_ACCESS[state]:
            # title != content: METADATA_SEEN can ground existence
            # claims at REPORTED strength, never OBSERVED/PROVEN.
            err("E_ACCESS_TOO_WEAK_FOR_STATE", state=state, access=acc)

    prior = c.get("promoted_from")
    if prior is not None:
        pair = (prior, state)
        if prior not in CLAIM_STATES:
            err("E_UNKNOWN_PRIOR_STATE", got=prior)
        elif pair in NEVER_PROMOTABLE:
            err("E_FORBIDDEN_PROMOTION", promotion=list(pair))
        elif pair in WITNESS_REQUIRED and not c.get("witness"):
            err("E_UNWITNESSED_PROMOTION", promotion=list(pair))

    if state == "HYPOTHESIZED" and not c.get("falsifier"):
        err("E_HYPOTHESIS_WITHOUT_FALSIFIER")

    if "amount_state" in c:
        if c["amount_state"] not in COMMERCIAL_STATES:
            err("E_UNTYPED_AMOUNT", got=c["amount_state"])
        if "amount" in c or "figure" in c:
            # figures never travel through the package (privacy zone law)
            err("E_RESTRICTED_FIGURE_IN_PACKAGE")

    t = c.get("temporal")
    if t is not None:
        ts = t.get("state")
        if ts not in TEMPORAL_STATES:
            err("E_UNKNOWN_TEMPORAL_STATE", got=ts)
        elif ts == "LOST" and not t.get("outcome_receipt"):
            # blocked != terminal loss: only a closure receipt absorbs
            err("E_BLOCK_TREATED_AS_ABSORBING")

    return errs


def validate(claims: list[dict]) -> dict:
    ids = [c.get("id") for c in claims]
    errors: list[dict] = []
    if len(ids) != len(set(ids)):
        errors.append({"claim": None, "reason": "E_DUPLICATE_CLAIM_ID"})
    for c in claims:
        errors.extend(validate_claim(c))
    return {"ok": not errors, "n_claims": len(claims),
            "n_errors": len(errors), "errors": errors}


def selftest() -> None:
    ok = {"id": "c1", "state": "OBSERVED",
          "basis": ["msg:171b2c"], "basis_access": "CONTENT_EXTRACTED"}
    assert validate([ok])["ok"], validate([ok])

    # NO_RECEIPT is a lawful, basis-free outcome.
    assert validate([{"id": "c2", "state": "NO_RECEIPT",
                      "basis": []}])["ok"]

    # title != content.
    v = validate([{"id": "c3", "state": "OBSERVED",
                   "basis": ["thread:x"],
                   "basis_access": "METADATA_SEEN"}])
    assert v["errors"][0]["reason"] == "E_ACCESS_TOO_WEAK_FOR_STATE"

    # A diagnosis never becomes a sighting; hearsay never proves.
    for pair in (("INFERRED", "OBSERVED"), ("REPORTED", "PROVEN"),
                 ("HYPOTHESIZED", "OBSERVED")):
        v = validate([{"id": "c4", "state": pair[1], "basis": ["b"],
                       "basis_access": "CONTENT_CROSS_CORROBORATED",
                       "promoted_from": pair[0], "witness": "w"}])
        assert any(e["reason"] == "E_FORBIDDEN_PROMOTION"
                   for e in v["errors"]), (pair, v)

    # Legal promotion needs its witness.
    up = {"id": "c5", "state": "OBSERVED", "basis": ["msg:9"],
          "basis_access": "CONTENT_OPENED", "promoted_from": "REPORTED"}
    assert validate([up])["errors"][0]["reason"] == \
        "E_UNWITNESSED_PROMOTION"
    assert validate([{**up, "witness": "primary artifact msg:9"}])["ok"]

    # Hypotheses carry falsifiers or they are not hypotheses.
    v = validate([{"id": "c6", "state": "HYPOTHESIZED", "basis": ["b"],
                   "basis_access": "CONTENT_OPENED"}])
    assert v["errors"][0]["reason"] == "E_HYPOTHESIS_WITHOUT_FALSIFIER"

    # Amounts are typed and figures never travel.
    v = validate([{"id": "c7", "state": "OBSERVED", "basis": ["b"],
                   "basis_access": "CONTENT_OPENED",
                   "amount_state": "BUDGET"}])
    assert v["errors"][0]["reason"] == "E_UNTYPED_AMOUNT"
    v = validate([{"id": "c8", "state": "OBSERVED", "basis": ["b"],
                   "basis_access": "CONTENT_OPENED",
                   "amount_state": "REQUESTED", "amount": 100000}])
    assert v["errors"][0]["reason"] == "E_RESTRICTED_FIGURE_IN_PACKAGE"

    # blocked != terminal loss.
    v = validate([{"id": "c9", "state": "OBSERVED", "basis": ["b"],
                   "basis_access": "CONTENT_OPENED",
                   "temporal": {"state": "LOST",
                                "outcome_receipt": None}}])
    assert v["errors"][0]["reason"] == "E_BLOCK_TREATED_AS_ABSORBING"
    assert validate([{"id": "c9", "state": "OBSERVED", "basis": ["b"],
                      "basis_access": "CONTENT_OPENED",
                      "temporal": {"state": "LOST",
                                   "outcome_receipt": "receipt:closure"}
                      }])["ok"]

    # Determinism.
    batch = [ok, {"id": "c2", "state": "NO_RECEIPT", "basis": []}]
    assert json.dumps(validate(batch), sort_keys=True) == \
        json.dumps(validate(batch), sort_keys=True)
    print("claim_validator selftest: OK (12 checks)")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
        sys.exit(0)
    src = sys.argv[1] if len(sys.argv) > 1 else None
    data = json.load(open(src)) if src else json.load(sys.stdin)
    out = validate(data)
    print(json.dumps(out, indent=2, sort_keys=True))
    sys.exit(0 if out["ok"] else 1)
