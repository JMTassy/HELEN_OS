"""Epistemic layers around 1851 — the historical state machine, and
the receiver for HER's 40-item packet.

NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none.

    H -> P -> D -> J -> F -> C -> D'

    procedure -> claim -> demonstration -> judgment -> failure ->
    constraint -> next generation

Four bounded corpus-volumes surround the same technological moment:

    A  pre-1851 patent claims          layer P   (the Garden analogue)
    B  Crystal Palace demonstrations   layer D   (observed capability)
    C  1851 jury judgments             layer J   (JUDGE)
    D  railway failure reports         layer F   (adversarial witness)

The laws this module enforces on any incoming item:

  SIGMA IS COMPUTED, NEVER DECLARED   sigma(q) = highest gate
      LEGITIMATELY crossed = the longest contiguous prefix of
      (P, D, J, F, C) for which the item holds a witness FROM THAT
      LAYER'S corpus. A jury citation with no demonstration witness
      does not make a thing demonstrated — it exposes a layer gap.
      A declared sigma above the computed one is E_SIGMA_OVERCLAIM.

  PATENT CLAIM != DEMONSTRATED CAPABILITY   and every other adjacent
      pair likewise; promotion is one layer per witnessed crossing.

  ROLE SEPARATION != SOURCE INDEPENDENCE   The catalogue and the jury
      reports are two ROLES inside one Exhibition ecosystem — one
      evidential root. Different agents are not independent
      witnesses; different institutions are not necessarily
      independent evidence.

  FAILURE YIELDS CONSTRAINT CANDIDATES, TYPED LATER   An accident
      falsifies an assumed-admissible transition. What it reveals is
      a candidate missing guard G* OR missing invariant I* — both
      HYPOTHESIS grade until analysis types them. Reality was the
      witness; the classification is ours.

  EXTERNALIZATION IS MEASURED, NOT ASSUMED MONOTONE   E(x) =
      (e_S, e_M, e_J, e_A, e_G). The trend function reports what the
      sample shows and keeps H0 (non-monotone) and H1 (externalization
      shifts rather than rises) alive in its output.

Deterministic: no wall-time, no randomness, canonical serialization.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from crystal_palace import canon_hash  # noqa: E402

LAYER_CHAIN = ("H", "P", "D", "J", "F", "C", "D_next")

SIGMA_LADDER = ("claimed", "demonstrated", "judged",
                "operationally_survived", "institutionally_required")
SIGMA_LAYER = {"claimed": "P", "demonstrated": "D", "judged": "J",
               "operationally_survived": "F",
               "institutionally_required": "C"}

CORPUS_VOLUMES = {
    "A": {"name": "pre-1851 patent claims (Repertory)", "layer": "P",
          "helen_analogue": "Garden candidate"},
    "B": {"name": "Crystal Palace demonstrations", "layer": "D",
          "helen_analogue": "observed capability"},
    "C": {"name": "1851 jury judgments", "layer": "J",
          "helen_analogue": "JUDGE"},
    "D": {"name": "railway failure reports", "layer": "F",
          "helen_analogue": "adversarial witness"},
}


# ── sigma: computed from witnesses, never taken on declaration ─────────

_UPPER = ("demonstrated", "judged", "operationally_survived",
          "institutionally_required")            # strict chain: D<J<F<C

# sigma as a PROMOTION SIGNATURE — the product space, not the maximum.
# A technology does not move along one ladder; it accumulates typed
# credentials. Absence of a witness on an axis is UNKNOWN, never NO,
# and no axis entails another (harakeke: demonstrated=WITNESSED while
# claimed=UNKNOWN is a legal signature, not a defect).
SIGNATURE_AXES = ("claimed", "demonstrated", "judged",
                  "operationally_survived", "institutionally_required")


def sigma_signature(witnesses: tuple) -> dict:
    """sigma(q) = (sigma_P, sigma_D, sigma_J, sigma_F, sigma_C) as
    independent typed credentials. Each witness may carry a graded
    'value' (e.g. jury_novelty=MEDIUM); a bare witness credential is
    WITNESSED; an absent axis is UNKNOWN. There is deliberately NO
    scalar aggregate — collapsing the vector is the semantic-collapse
    failure this object exists to prevent."""
    by_layer: dict = {}
    for w in witnesses:
        by_layer.setdefault(w["layer"], []).append(w)
    sig = {}
    for axis in SIGNATURE_AXES:
        layer = SIGMA_LAYER[axis]
        if layer not in by_layer:
            sig[axis] = "UNKNOWN"
        else:
            graded = [w["value"] for w in by_layer[layer] if w.get("value")]
            sig[axis] = graded[0] if graded else "WITNESSED"
    return {"signature": sig,
            "law": "typed credentials accumulate independently; "
                   "no axis entails another, and UNKNOWN is not NO"}


def compute_sigma(witness_layers: frozenset) -> dict:
    """'claimed' is an ENTRY rung, not a prerequisite: demonstration
    does not require a prior patent claim (harakeke: exhibited 1851,
    patented elsewhere only in 1861). From D upward the chain is
    strict — a witness above an unwitnessed rung is stranded, and the
    gap is surfaced, never bridged."""
    sigma = "claimed" if "P" in witness_layers else None
    prefix_end = 0
    for i, status in enumerate(_UPPER):
        layer = SIGMA_LAYER[status]
        if layer in witness_layers:
            if i != prefix_end:
                return {"sigma": sigma, "gap": True,
                        "reason": "E_LAYER_GAP",
                        "stranded_witness": layer}
            sigma = status
            prefix_end += 1
    return {"sigma": sigma, "gap": False}


# ── role vs root ────────────────────────────────────────────────────────

def roles_and_roots(witnesses: tuple) -> dict:
    """Each witness: {"role": ..., "root": ...}. Evaluation
    independence comes from roles; evidential independence ONLY from
    roots."""
    roles = {w["role"] for w in witnesses}
    roots = {w["root"] for w in witnesses}
    return {"independent_roles": len(roles),
            "independent_roots": len(roots),
            "evaluation_independence": len(roles) > 1,
            "evidential_independence": len(roots) > 1,
            "law": "ROLE SEPARATION != SOURCE INDEPENDENCE"}


# ── failure -> constraint candidates ────────────────────────────────────

@dataclass(frozen=True)
class Accident:
    accident_id: str
    state_before: str
    action: str                       # the transition assumed admissible
    bad_state: str
    procedural_context: str = ""


def infer_missing_constraint(acc: Accident) -> dict:
    """What reality falsified. Two candidate repairs, BOTH hypothesis
    grade — typing them (guard vs invariant) is analysis, not given."""
    return {"falsified_transition": (acc.state_before, acc.action,
                                     acc.bad_state),
            "candidates": (
                {"kind": "missing_guard",
                 "form": f"G*: ({acc.state_before}, {acc.action}) "
                         "-> REJECT"},
                {"kind": "missing_invariant",
                 "form": f"I*: forbids reaching {acc.bad_state} on "
                         "ANY path"}),
            "grade": "HYPOTHESIS",
            "law": "reality was the witness; the classification is "
                   "ours, and GATE != INVARIANT decides which repair "
                   "is stronger"}


def constraint_externalization(acc: Accident, constraint: str,
                               next_gen_witness: str = "") -> dict:
    """failure -> missing invariant discovered -> constraint
    externalized -> new architecture. Without a next-generation
    witness, the mechanism is proposed, not shown."""
    if not next_gen_witness:
        return {"verdict": "PROPOSED_CONSTRAINT", "constraint": constraint,
                "reason": "E_NEXT_GENERATION_UNWITNESSED"}
    return {"verdict": "EXTERNALIZATION_WITNESSED",
            "constraint": constraint,
            "from_failure": acc.accident_id,
            "into": next_gen_witness}


# ── externalization depth ───────────────────────────────────────────────

@dataclass(frozen=True)
class ExternalizationDepth:
    """E(x) = (e_S, e_M, e_J, e_A, e_G): sensing, memory, judgment,
    actuation, governance externalized into the artifact."""
    e_s: float
    e_m: float
    e_j: float
    e_a: float
    e_g: float

    def vector(self) -> tuple:
        return (self.e_s, self.e_m, self.e_j, self.e_a, self.e_g)

    def total(self) -> float:
        return sum(self.vector())


def externalization_trend(series: tuple) -> dict:
    """series: ((year, ExternalizationDepth), ...). Reports the sample;
    never asserts the theory. H0 and H1 ride every output."""
    if len(series) < 2:
        return {"verdict": "UNKNOWN", "reason": "E_TREND_NEEDS_TWO_POINTS"}
    totals = [d.total() for _y, d in sorted(series)]
    rising = all(b >= a for a, b in zip(totals, totals[1:]))
    strictly = all(b > a for a, b in zip(totals, totals[1:]))
    return {"verdict": ("MONOTONE_IN_SAMPLE" if rising
                        else "NON_MONOTONE_IN_SAMPLE"),
            "strict": strictly,
            "totals": totals,
            "live_counter_hypotheses": (
                "H0: E(t) does not monotonically increase",
                "H1: externalization shifts between human and artifact "
                "rather than simply rising"),
            "note": "sample-level report; the theory stays a candidate"}


# ── the 40-item packet receiver ─────────────────────────────────────────

PACKET_ITEM_FIELDS = ("item_id", "corpus_volume", "claim", "sigma",
                      "witnesses")


def validate_packet_item(item: dict) -> dict:
    missing = [f for f in PACKET_ITEM_FIELDS if f not in item]
    if missing:
        return {"verdict": "REFUSED", "reason": "E_PACKET_FIELD_MISSING",
                "missing": missing}
    if item["corpus_volume"] not in CORPUS_VOLUMES:
        return {"verdict": "REFUSED", "reason": "E_UNKNOWN_VOLUME"}
    layers = frozenset(w["layer"] for w in item["witnesses"])
    computed = compute_sigma(layers)
    if computed.get("reason") == "E_LAYER_GAP" and computed["sigma"] is None:
        return {"verdict": "REFUSED", "reason": "E_LAYER_GAP",
                "computed": computed}
    if item["sigma"] != computed["sigma"]:
        if computed["sigma"] is None or (
                item["sigma"] in SIGMA_LADDER and computed["sigma"] in
                SIGMA_LADDER and SIGMA_LADDER.index(item["sigma"]) >
                SIGMA_LADDER.index(computed["sigma"])):
            return {"verdict": "REFUSED", "reason": "E_SIGMA_OVERCLAIM",
                    "declared": item["sigma"], "computed": computed["sigma"]}
        return {"verdict": "REFUSED", "reason": "E_SIGMA_MISMATCH",
                "declared": item["sigma"], "computed": computed["sigma"]}
    return {"verdict": "VALID", "sigma": computed["sigma"],
            "gap": computed.get("gap", False),
            "signature": sigma_signature(item["witnesses"])["signature"]}


def validate_packet(items: tuple) -> dict:
    """HER promised exactly 10 per volume. Shape is checked before
    content; every item validates individually; the packet freezes."""
    counts: dict = {}
    for it in items:
        counts[it.get("corpus_volume", "?")] = \
            counts.get(it.get("corpus_volume", "?"), 0) + 1
    if sorted(counts.keys()) != ["A", "B", "C", "D"] or \
            any(v != 10 for v in counts.values()):
        return {"verdict": "REFUSED", "reason": "E_PACKET_SHAPE",
                "expected": "10 items x 4 volumes", "got": counts}
    results = [validate_packet_item(it) for it in items]
    bad = [(it["item_id"], r) for it, r in zip(items, results)
           if r["verdict"] != "VALID"]
    if bad:
        return {"verdict": "REFUSED", "reason": "E_PACKET_ITEMS_INVALID",
                "invalid": [b[0] for b in bad], "details": bad[:3]}
    return {"verdict": "PACKET_ACCEPTED",
            "packet_hash": canon_hash(
                [(it["item_id"], it["corpus_volume"], it["sigma"])
                 for it in items]),
            "count": len(items)}
