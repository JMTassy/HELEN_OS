r"""EPIS-CYCLE-ONT-01 — the ontological promotion frontier r*.

NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none.

    Representation(x)  does not entail  Instantiation(x)

No representation inherits the status of its referent. A drawing of a
bridge is not a bridge; a plan for a company is not a company; a
proposal that a rule holds is not the rule holding. Crossing from the
representation side of r* to the instantiation side is not a property
the representation can acquire by being detailed, confident, agreed
with, or repeated.

WHAT IS NEW HERE, against the modules that already exist. vision_ir
makes the warrant a four-part PREDICATE; membrane makes promotion
require a witness; epistemic_lattice names illegal inferences. All
three ask "is the condition true?". This module asks a different
question:

    a crossing is a DEBT that must be DISCHARGED,
    and the debtor may not be the creditor

An obligation is created by whoever proposes the crossing, and it is
discharged by someone else against a witness. A system where the
proposer marks its own obligation satisfied has separation of powers
on paper and self-dealing in fact. That is the failure this module
measures, and no existing module catches it: every predicate in
vision_ir would return True while one agent both asks and answers.

ROLE ISOLATION, typed. The dispatch splits the cognition:

    HER    propose            may NOT discharge, witness, or cross
    HAL_F  attack / falsify   may NOT witness or cross
    HAL_W  witness / provenance   may NOT cross (it supplies, not decides)
    HAL_X  cross / gate       may NOT propose or witness its own case
    QWEN   compress           NON-PROMOTIONAL, always

Qwen's confinement is the graph_ir edge default in a different
costume: distillation moves representation and transfers no epistemic
state, so a compressed witness is not a new witness.

    |G| -> infinity     the generative frontier may grow without bound
    |Gamma| = O(1)      the deterministic core stays small

CORRECTION TO THE INVARIANT AS WRITTEN. |Gamma| = O(1) cannot mean
|Gamma| CONSTANT: a canon that can never grow is a system that can
never learn, which is paralysis dressed as safety — the defect
proof_ceiling already refuses via its positive control. The bound that
is actually meant is a bound on the DERIVATIVE:

    d|Gamma| / d|G| = 0        exploration volume buys no canon
    d|Gamma| / d(discharged crossings) > 0 is LAWFUL

Gamma grows only through discharged crossings, never through epoch
count, proposal count, or agreement.

AND THE GENERATOR IS ONE INSTRUMENT. Twelve proposals from one
Gemma4-12B are twelve samples of one generator, not twelve independent
hypotheses (see scaling_harness.swarm_common_mode). This module counts
proposals; it does not count them as evidence.

Deterministic: no wall-clock, no randomness, canonical serialization.
"""
from __future__ import annotations

import json

# side of the frontier
REPRESENTATION = "REPRESENTATION"
INSTANTIATION = "INSTANTIATION"
SIDES = (REPRESENTATION, INSTANTIATION)

# obligation lifecycle
OPEN = "OPEN"
DISCHARGED = "DISCHARGED"
TERMINATED = "TERMINATED"

# the gate's three verdicts
PROMOTE = "PROMOTE"
HOLD = "HOLD"
TERMINATE = "TERMINATE"

ROLES = {
    "HER":   {"propose": True, "attack": False, "witness": False,
              "cross": False, "compress": False, "promotional": False},
    "HAL_F": {"propose": False, "attack": True, "witness": False,
              "cross": False, "compress": False, "promotional": False},
    "HAL_W": {"propose": False, "attack": False, "witness": True,
              "cross": False, "compress": False, "promotional": False},
    "HAL_X": {"propose": False, "attack": False, "witness": False,
              "cross": True, "compress": False, "promotional": True},
    "QWEN":  {"propose": False, "attack": False, "witness": False,
              "cross": False, "compress": True, "promotional": False},
    # experiment-only: audits that model comparisons share prompt,
    # QID, packet, schema, thinking mode, context — an attack surface
    # on the INSTRUMENT, never a witness and never a gate
    "HAL_I": {"propose": False, "attack": True, "witness": False,
              "cross": False, "compress": False, "promotional": False},
}

POWERS = ("propose", "attack", "witness", "cross", "compress")

OBLIGATION_FIELDS = ("claim", "referent", "required_witness",
                     "created_by")


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


# ── role isolation ─────────────────────────────────────────────────────

def role_may(role: str, power: str) -> dict:
    """Powers are granted by role, never inferred from competence. A
    model good enough to witness is not thereby licensed to cross."""
    if role not in ROLES:
        return {"licensed": None, "reason": "E_UNKNOWN_ROLE"}
    if power not in POWERS:
        return {"licensed": None, "reason": "E_UNKNOWN_POWER"}
    ok = ROLES[role][power]
    return {"role": role, "power": power, "licensed": ok,
            "reason": None if ok else "E_ROLE_LACKS_POWER",
            "law": "capability is not authority; the split is declared, "
                   "never derived from how good a model is"}


def compression_is_not_evidence(role: str, before: int,
                                after: int) -> dict:
    """Distillation moves representation and transfers no epistemic
    state. A compressed witness is the same witness; a compressed
    corpus is not a corroborated one."""
    if not ROLES.get(role, {}).get("compress"):
        return {"ok": False, "reason": "E_ROLE_LACKS_POWER",
                "role": role}
    return {"ok": True, "role": role,
            "tokens_before": before, "tokens_after": after,
            "witnesses_added": 0, "promotional": False,
            "law": "compression is a representation transform; it "
                   "mints no witness and carries no promotion"}


# ── the crossing obligation, as a debt ─────────────────────────────────

def crossing_obligation(**o) -> dict:
    """Created at the moment a crossing is PROPOSED, not when it is
    granted. An obligation that cannot name the witness that would
    discharge it is an impasse, not a debt."""
    missing = [k for k in OBLIGATION_FIELDS if k not in o]
    if missing:
        return {"ok": False, "reason": "E_UNTYPED_OBLIGATION",
                "missing": sorted(missing)}
    creator = o["created_by"]
    if not ROLES.get(creator, {}).get("propose"):
        return {"ok": False, "reason": "E_ROLE_LACKS_POWER",
                "role": creator, "power": "propose"}
    return {"ok": True, "state": OPEN, "side": REPRESENTATION,
            **{k: o[k] for k in OBLIGATION_FIELDS}}


def discharge(ob: dict, by: str, witness: str | None,
              witness_supplied_by: str | None = None) -> dict:
    """The debtor may not be the creditor.

    Three refusals, in order of how convincingly each disguises
    itself:
      - discharging with no witness at all
      - discharging by a role that holds no crossing power
      - discharging one's OWN obligation, which every predicate-shaped
        check in this codebase would happily pass
    """
    if not ob.get("ok"):
        return {"discharged": False, "reason": "E_BAD_OBLIGATION"}
    if ob["state"] != OPEN:
        return {"discharged": False, "reason": "E_OBLIGATION_NOT_OPEN",
                "state": ob["state"]}
    if by == ob["created_by"]:
        return {"discharged": False, "reason": "E_SELF_DISCHARGE",
                "law": "the debtor may not be the creditor; a proposer "
                       "marking its own obligation satisfied is "
                       "self-dealing with separation of powers on paper"}
    if not ROLES.get(by, {}).get("cross"):
        return {"discharged": False, "reason": "E_ROLE_LACKS_POWER",
                "role": by, "power": "cross"}
    if not witness:
        return {"discharged": False,
                "reason": "E_UNDISCHARGED_CROSSING",
                "law": "an obligation is discharged against a witness, "
                       "never by assertion"}
    if witness_supplied_by is not None and \
            not ROLES.get(witness_supplied_by, {}).get("witness"):
        return {"discharged": False, "reason": "E_ROLE_LACKS_POWER",
                "role": witness_supplied_by, "power": "witness"}
    return {"discharged": True, "state": DISCHARGED,
            "obligation": ob["claim"], "discharged_by": by,
            "witness": witness,
            "witness_supplied_by": witness_supplied_by}


def terminate(ob: dict, by: str, refutation: str) -> dict:
    """HAL_F's product. A refuted crossing is CLOSED, not merely
    unproven — and closing it is a real outcome, not a failure."""
    if not ob.get("ok"):
        return {"terminated": False, "reason": "E_BAD_OBLIGATION"}
    if not ROLES.get(by, {}).get("attack"):
        return {"terminated": False, "reason": "E_ROLE_LACKS_POWER",
                "role": by, "power": "attack"}
    return {"terminated": True, "state": TERMINATED,
            "obligation": ob["claim"], "refuted_by": by,
            "refutation": refutation,
            "note": "termination is an epistemic result; the cycle "
                    "gained information"}


# ── the frontier itself ────────────────────────────────────────────────

def cross(ob: dict, discharge_receipt: dict, by: str) -> dict:
    """r*: the only door from REPRESENTATION to INSTANTIATION. A
    representation inherits its referent's status if and only if a
    crossing obligation was created, assigned elsewhere, and
    discharged against a witness."""
    if not ROLES.get(by, {}).get("cross"):
        return {"verdict": TERMINATE, "crossed": False,
                "reason": "E_ROLE_LACKS_POWER", "role": by}
    if not ob.get("ok"):
        return {"verdict": TERMINATE, "crossed": False,
                "reason": "E_BAD_OBLIGATION"}
    if not discharge_receipt.get("discharged"):
        return {"verdict": HOLD, "crossed": False,
                "side": REPRESENTATION,
                "reason": "E_INHERITED_WITHOUT_CROSSING",
                "blocked_by": discharge_receipt.get("reason"),
                "law": "no representation inherits the status of its "
                       "referent without a discharged crossing "
                       "obligation"}
    return {"verdict": PROMOTE, "crossed": True,
            "side": INSTANTIATION, "claim": ob["claim"],
            "referent": ob["referent"],
            "witness": discharge_receipt["witness"],
            "gated_by": by}


def inherits_status(representation: str, referent_status: str,
                    crossed: bool) -> dict:
    """The bare non-entailment, stated so it can be probed directly."""
    return {"representation": representation,
            "referent_status": referent_status,
            "inherited_status": referent_status if crossed else None,
            "reason": None if crossed
                      else "E_INHERITED_WITHOUT_CROSSING",
            "law": "Representation(x) does not entail Instantiation(x)"}


# ── the epoch, and what it may and may not grow ────────────────────────

def epoch(k: int, proposals: int, attacks: int,
          discharged: int) -> dict:
    """Epoch_k = Explore -> Hypothesize -> Attack -> Receipt. It yields
    PRE-CLAIMS. Canon promotion is not one of its outputs, and the
    field is structurally zero rather than merely expected to be."""
    if proposals < 0 or attacks < 0 or discharged < 0:
        raise ValueError("E_NEGATIVE_COUNT")
    if discharged > proposals:
        return {"ok": False, "reason": "E_MORE_DISCHARGED_THAN_PROPOSED"}
    return {"ok": True, "epoch": k, "pre_claims": proposals,
            "attacks": attacks, "discharged_crossings": discharged,
            "canon_promoted_by_this_epoch": 0,
            "law": "an epoch yields governed candidate pre-claims; "
                   "promotion happens at r*, not in the loop"}


def gamma_growth(epochs: int, proposals: int,
                 discharged_crossings: int) -> dict:
    """|Gamma| = O(1) with respect to |G|, NOT constant in time.

    A canon that can never grow cannot learn, and 'safety' proven by
    never admitting anything is the paralysis the positive control in
    proof_ceiling exists to catch. The bound is on the derivative:
    exploration volume buys nothing, discharged crossings buy canon."""
    if epochs < 0 or proposals < 0 or discharged_crossings < 0:
        raise ValueError("E_NEGATIVE_COUNT")
    return {"epochs": epochs, "proposals": proposals,
            "d_gamma_d_exploration": 0,
            "gamma_growth_licensed": discharged_crossings,
            "bound": "d|Gamma|/d|G| = 0",
            "misreading_refused": "|Gamma| constant in time",
            "law": "Gamma grows only through discharged crossings, "
                   "never through epoch count, proposal volume or "
                   "agreement"}


def generator_independence(proposals: int, n_generators: int) -> dict:
    """Twelve proposals from one 12B model are twelve samples of one
    generator. Counting them is fine; counting them as independent
    hypotheses is the swarm common mode again."""
    if proposals <= 0:
        raise ValueError("E_NO_PROPOSALS")
    eff = min(max(1, n_generators), proposals)
    return {"proposals": proposals, "n_generators": n_generators,
            "N_effective_on_hypotheses": eff,
            "independence_licensed": eff > 1,
            "reason": None if eff > 1 else "E_SINGLE_GENERATOR",
            "law": "proposal volume is throughput, never hypothesis "
                   "independence"}
