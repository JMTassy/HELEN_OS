"""PRIZE_PAPERS / ONE_CAPTURE — the multiplex-bundle receiver.

NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none.

This module does NOT scan the Prize Papers Portal — this seat cannot
reach it, and inventing a vessel's records would be
DOCUMENT_LOCATION_IS_NOT_AUTHORSHIP committed by the receiver's own
author. What lives here is the receiver: a captured vessel is a
ONE_SHIP multiplex bundle, and its seven layers must never silently
contaminate one another.

    V = (S_phys, S_custody, S_cargo, S_identity, S_communication,
         S_authority, S_legal)

The corpus adds the adversarial layer the previous ones lacked:
contested legality AFTER physical action. The ship is already seized;
the Admiralty court still decides whether the seizure was admissible.

    EFFECT != AUTHORIZED EFFECT

Five forbidden joins, each an executable refusal — a fact in one layer
never crosses into another without a provenance witness:

  DOCUMENT_LOCATION != AUTHORSHIP   found aboard is not authored-by
  CARGO_POSSESSION  != OWNERSHIP    aboard is not owned-by
  INTERCEPTED       != DELIVERED    in the bundle BECAUSE undelivered
  CAPTURED          != LAWFULLY_CAPTURED   effect is not authorized
  COURT_JUDGMENT    != WORLD_HISTORY   later judgment does not rewrite
                                       the fact of the physical capture

The last is History Fiber at its purest: a legal classification
mutates institutional state; it does not edit the past.

Deterministic: no wall-clock, no randomness, canonical serialization.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field

# the seven layers of a captured vessel; each is its own evidence plane.
LAYERS = ("S_phys", "S_custody", "S_cargo", "S_identity",
          "S_communication", "S_authority", "S_legal")

# a claim crossing between two layers needs one of these witnesses.
CROSS_LAYER_WITNESSES = frozenset({
    "signed_provenance", "notarized_bill", "port_register_match",
    "court_finding", "corroborating_independent_root"})


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


# ── a document in the bundle ────────────────────────────────────────────

@dataclass(frozen=True)
class BundleDocument:
    """One document found aboard. found_in_layer is where it physically
    sat; it is NOT an authorship or ownership claim. Any cross-layer
    assertion (who authored it, who owns the cargo it describes) needs
    a witness."""
    doc_id: str
    found_in_layer: str
    doc_type: str                      # logbook | passport | bill | letter
    source_root: str                   # which archival unit; provenance

    def __post_init__(self):
        if self.found_in_layer not in LAYERS:
            raise ValueError("E_UNKNOWN_LAYER")


# ── the forbidden joins ─────────────────────────────────────────────────

def attribute_authorship(doc: BundleDocument, claimed_author: str,
                         witness: dict | None = None) -> dict:
    """DOCUMENT_LOCATION != AUTHORSHIP. A paper aboard a ship does not
    name its author. Only a provenance witness crosses S_phys ->
    S_identity."""
    if witness is None or witness.get("kind") not in CROSS_LAYER_WITNESSES:
        return {"verdict": "REFUSED",
                "reason": "E_DOCUMENT_LOCATION_IS_NOT_AUTHORSHIP",
                "doc": doc.doc_id,
                "law": "found aboard is not authored-by"}
    return {"verdict": "ATTRIBUTED", "author": claimed_author,
            "via": witness["kind"]}


def attribute_ownership(cargo_id: str, claimed_owner: str,
                        witness: dict | None = None) -> dict:
    """CARGO_POSSESSION != OWNERSHIP. Physical possession is not legal
    title. Crossing S_cargo -> S_authority needs a bill or court
    finding."""
    if witness is None or witness.get("kind") not in CROSS_LAYER_WITNESSES:
        return {"verdict": "REFUSED", "reason": "E_CARGO_IS_NOT_OWNERSHIP",
                "cargo": cargo_id, "law": "aboard is not owned-by"}
    return {"verdict": "TITLE_ESTABLISHED", "owner": claimed_owner,
            "via": witness["kind"]}


def delivery_status(letter: BundleDocument) -> dict:
    """INTERCEPTED != DELIVERED. A letter is in the Prize Papers bundle
    PRECISELY because it never reached its addressee. Its presence is
    evidence of non-delivery, the opposite of delivery."""
    if letter.found_in_layer != "S_communication":
        return {"verdict": "NOT_A_LETTER_IN_TRANSIT"}
    return {"verdict": "INTERCEPTED_UNDELIVERED",
            "delivered": False,
            "law": "the letter is in the bundle because delivery "
                   "failed; presence is proof of non-delivery"}


def capture_legality(capture_occurred: bool,
                     court_finding: dict | None = None) -> dict:
    """CAPTURED != LAWFULLY_CAPTURED. The ship is physically seized;
    the High Court of Admiralty still decides admissibility. EFFECT !=
    AUTHORIZED EFFECT, as a historical fixture."""
    if not capture_occurred:
        return {"physical_capture": False, "legal_status": "N/A"}
    if court_finding is None:
        return {"physical_capture": True,
                "legal_status": "UNADJUDICATED",
                "law": "capture occurred; lawfulness is unresolved — "
                       "effect is not authorized effect"}
    if court_finding.get("kind") != "court_finding":
        return {"physical_capture": True, "legal_status": "UNADJUDICATED",
                "reason": "E_NOT_A_COURT_WITNESS"}
    return {"physical_capture": True,
            "legal_status": court_finding.get("verdict", "UNKNOWN"),
            "adjudicated": True}


def apply_judgment(world_capture_fact: dict, judgment: dict) -> dict:
    """COURT_JUDGMENT != WORLD_HISTORY. A ruling of 'unlawful capture'
    changes the institutional/legal state; it does NOT erase the fact
    that the physical seizure happened. History Fiber, purest form:
    later judgment does not rewrite the past."""
    return {"physical_capture_fact": world_capture_fact.get("occurred"),
            "physical_capture_unchanged": True,          # never edited
            "legal_state_after": judgment.get("verdict"),
            "law": "later judgment mutates institutional state; the "
                   "fact of the physical capture is not rewritten"}


# ── the seven-layer vessel ──────────────────────────────────────────────

@dataclass(frozen=True)
class CapturedVessel:
    """V = the ONE_CAPTURE multiplex. Each layer holds its own facts;
    cross_claims records assertions that jump layers, each of which
    must carry a witness or be refused at admission."""
    vessel_id: str
    layers: dict = field(default_factory=dict)   # layer -> tuple of facts

    def facts_in(self, layer: str) -> tuple:
        if layer not in LAYERS:
            raise ValueError("E_UNKNOWN_LAYER")
        return tuple(self.layers.get(layer, ()))

    def is_multiplex(self) -> bool:
        """A real ONE_CAPTURE bundle populates several layers; a single
        layer is a document, not a capture."""
        return sum(1 for l in LAYERS if self.layers.get(l)) >= 2


@dataclass(frozen=True)
class CrossLayerClaim:
    """An assertion that a fact in one layer implies a fact in another
    — the exact move the forbidden joins police."""
    claim_id: str
    from_layer: str
    to_layer: str
    assertion: str
    witness_kind: str = ""

    def admit(self) -> dict:
        if self.from_layer not in LAYERS or self.to_layer not in LAYERS:
            return {"verdict": "REFUSED", "reason": "E_UNKNOWN_LAYER"}
        if self.from_layer == self.to_layer:
            return {"verdict": "INTRA_LAYER", "note": "no join to police"}
        if self.witness_kind not in CROSS_LAYER_WITNESSES:
            return {"verdict": "REFUSED",
                    "reason": "E_UNWITNESSED_CROSS_LAYER_JOIN",
                    "from": self.from_layer, "to": self.to_layer,
                    "law": "a fact in one layer never crosses into "
                           "another without a provenance witness"}
        return {"verdict": "CROSS_LAYER_ADMITTED",
                "via": self.witness_kind}


# ── the five falsifiers, as a named registry ────────────────────────────

FORBIDDEN_JOINS = (
    ("E_PHYSICAL_EFFECT_IS_NOT_LEGALITY", "capture_legality"),
    ("E_DOCUMENT_LOCATION_IS_NOT_AUTHORSHIP", "attribute_authorship"),
    ("E_CARGO_IS_NOT_OWNERSHIP", "attribute_ownership"),
    ("E_INTERCEPTED_IS_NOT_DELIVERED", "delivery_status"),
    ("E_COURT_JUDGMENT_IS_NOT_WORLD_HISTORY", "apply_judgment"),
)

# the portal is organized by ship/capture/court-process/doc-type/
# subject/document; the scan enters by CAPTURE, not by keyword.
ONE_CAPTURE_MANIFEST_SCHEMA = {
    "corpus": "prize_papers_portal",
    "entry": "PRIZE_PAPERS / ONE_CAPTURE — pick one vessel, reconstruct "
             "its whole history fiber",
    "layers": LAYERS,
    "organized_by": ("ship", "capture", "court_process", "document_type",
                     "subject", "document"),
    "status": "PRESENCE_OBSERVED_NOT_READ",
    "note": "layer facts are populated by a seat that can read the "
            "portal; fabricating a vessel's records here would be "
            "DOCUMENT_LOCATION_IS_NOT_AUTHORSHIP by the receiver's "
            "own author",
}
