"""ONE_SHIP gold harness — Juffrouw Elizabeth / Lady Elizabeth,
HCA 32/122/21.

NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none.

Provenance of the vessel facts, stated exactly: this seat did NOT read
the Prize Papers Portal or TNA Discovery. The case (two hulls, an old
pass presented by a later vessel, capture by the privateer Frances
1741, a partial decree of 3 Nov 1741 condemning ship + part of cargo
and restoring the rest, a packet of allegedly-counterfeit papers) is
RELAYED from the operator's ruling citing public notices. It rides
here as a fixture at grade REPORTED, never as portal-verified fact.
What this module builds is the RECEIVER and the GOLD ORACLE HARNESS —
the oracle labels come from constitutional rules, not from any model's
judgement about "probable history".

The crown chiddush: a benchmark named ONE_SHIP must begin by testing
whether HELEN refuses to assume there is one.

    ONE_NAME    != ONE_HULL
    ONE_CAPTURE != ONE_LEGAL_STATUS   (verdict is scoped by object)
    ONE_ARCHIVE != ONE_EVIDENCE_ROOT  (N_root <= N_hash <= N_artifact)

Three falsifiers here extend the five in prize_papers.py:
  E_PARTIAL_VERDICT_SCOPE       condemned(ship) ⊬ condemned(all cargo)
  E_DERIVED_DOC_IS_NOT_NEW_WITNESS  a translation is not a new root
  E_NAME_IS_NOT_IDENTITY        same name + carried pass ⊬ same hull

And the maritime sharpening of ASSIGNED != ACCEPTED: a transfer is
typed. custody != title != obligation-owner.

Deterministic: no wall-clock, no randomness, canonical serialization.
"""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import prize_papers as pp  # noqa: E402

TRANSFER_KINDS = ("custody", "title", "obligation_owner")


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


# ── E_NAME_IS_NOT_IDENTITY ──────────────────────────────────────────────

def same_entity(hull_a: dict, hull_b: dict, basis: str) -> dict:
    """Two hulls sharing a name — or one carrying the other's pass —
    are not the same physical vessel. Identity may only be asserted
    from a continuity witness, never from a label or a credential."""
    forbidden = {"same_name", "carried_pass", "same_name+carried_pass"}
    if basis in forbidden:
        return {"verdict": "REFUSED", "reason": "E_NAME_IS_NOT_IDENTITY",
                "basis": basis,
                "identity_state": "CONTESTED_OR_COMPOSITE",
                "law": "same name and a carried pass do not make one "
                       "hull; do_not_merge_on name"}
    if basis == "physical_continuity_witness":
        return {"verdict": "SAME_ENTITY", "basis": basis}
    return {"verdict": "UNKNOWN_BASIS", "identity_state": "OPEN"}


# ── E_PARTIAL_VERDICT_SCOPE ─────────────────────────────────────────────

def verdict_of(scoped_verdicts: dict, target: str) -> dict:
    """A decree binds each asset scope separately. condemned(hull) does
    not propagate to cargo; asking for a global case status is the
    laundering this refuses. Verdict(scope_i) = v_i, never a flattened
    case verdict."""
    if target == "__case_global__" or target not in scoped_verdicts:
        if target == "__case_global__":
            return {"verdict": "REFUSED", "reason": "E_PARTIAL_VERDICT_SCOPE",
                    "law": "a decree binds each object subset; there is "
                           "no global case verdict to read",
                    "known_scopes": sorted(scoped_verdicts)}
        return {"verdict": "UNKNOWN_SCOPE", "target": target}
    return {"verdict": "SCOPED", "target": target,
            "decision": scoped_verdicts[target]}


def propagate_verdict(scoped_verdicts: dict, from_scope: str,
                      to_scope: str) -> dict:
    """The forbidden move: reading a verdict on one scope as binding
    another. condemned(hull_B) ⊬ condemned(cargo_subset_B)."""
    return {"verdict": "REFUSED", "reason": "E_PARTIAL_VERDICT_SCOPE",
            "from": from_scope, "to": to_scope,
            "law": "condemned(ship) does not imply condemned(all cargo)"}


# ── E_DERIVED_DOC_IS_NOT_NEW_WITNESS ────────────────────────────────────

@dataclass(frozen=True)
class Artifact:
    """A document surrogate. derived_from names its parent when it is a
    translation/copy/abstract; evidence_root_id is inherited from the
    parent's root, NOT minted fresh."""
    artifact_id: str
    sha256: str
    derived_from: str = ""
    evidence_root_id: str = ""


def evidence_census(artifacts: tuple) -> dict:
    """N_root <= N_hash <= N_artifact. A translation with a different
    hash is still one witness: differing bytes never prove
    independence, and identical bytes prove exact duplication."""
    n_artifact = len(artifacts)
    n_hash = len({a.sha256 for a in artifacts})
    roots = set()
    for a in artifacts:
        roots.add(a.evidence_root_id or a.artifact_id)
    n_root = len(roots)
    return {"n_artifact": n_artifact, "n_hash": n_hash, "n_root": n_root,
            "ordering_holds": n_root <= n_hash <= n_artifact,
            "law": "N_root <= N_hash <= N_artifact; a differing hash "
                   "never proves an independent root"}


def independent_roots_claim(original: Artifact, derived: Artifact) -> dict:
    """The forbidden move: a translation with a different SHA claimed
    as a second independent witness."""
    if derived.derived_from == original.artifact_id and \
            derived.evidence_root_id == original.evidence_root_id:
        return {"verdict": "REFUSED",
                "reason": "E_DERIVED_DOC_IS_NOT_NEW_WITNESS",
                "n_root": 1,
                "law": "a court translation of a seized paper shares the "
                       "paper's evidence root"}
    return {"verdict": "DISTINCT_ROOTS", "n_root": 2}


# ── typed transfer: custody != title != obligation-owner ────────────────

@dataclass
class TypedTransfer:
    """Maritime sharpening of ASSIGNED != ACCEPTED. A transfer names
    WHAT is moving; accepting custody moves custody only."""
    transfer_id: str
    kind: str
    object_ref: str
    from_ref: str
    to_ref: str
    state: str = "TRANSFER_PROPOSED"
    receipt_ref: str = ""

    def __post_init__(self):
        if self.kind not in TRANSFER_KINDS:
            raise ValueError("E_UNKNOWN_TRANSFER_KIND")

    def accept(self, by: str, receipt_ref: str) -> dict:
        if by != self.to_ref:
            return {"verdict": "REFUSED", "reason": "E_WRONG_ACCEPTOR"}
        if not receipt_ref:
            return {"verdict": "REFUSED", "reason": "E_NO_ACCEPTANCE_RECEIPT"}
        self.state = "TRANSFER_ACCEPTED"
        self.receipt_ref = receipt_ref
        return {"verdict": "ACCEPTED", "kind": self.kind}


def transfer_implies(accepted: TypedTransfer, asked_kind: str) -> dict:
    """Accepting a custody transfer does not move title. Reading one
    transfer kind as another is refused."""
    if asked_kind not in TRANSFER_KINDS:
        return {"verdict": "REFUSED", "reason": "E_UNKNOWN_TRANSFER_KIND"}
    if accepted.state != "TRANSFER_ACCEPTED":
        return {"verdict": "REFUSED", "reason": "E_TRANSFER_NOT_COMPLETED"}
    if asked_kind != accepted.kind:
        return {"verdict": "REFUSED", "reason": "E_TRANSFER_KIND_MISMATCH",
                "moved": accepted.kind, "asked": asked_kind,
                "law": f"transfer of {accepted.kind} does not imply "
                       f"transfer of {asked_kind}"}
    return {"verdict": "MOVED", "kind": accepted.kind, "to": accepted.to_ref}


# ── the 8 gold oracles, labelled by constitutional rule ─────────────────
# expected gate + reason are set by the LAW, never by model judgement.

GOLD_ORACLES = (
    {"id": "T001", "given": ["physical.capture(hull_B)"],
     "proposed": "legal.lawful_prize(hull_B)",
     "expected": "REJECT", "reason": "E_PHYSICAL_EFFECT_IS_NOT_LEGALITY"},
    {"id": "T002", "given": ["document.found_on(letter_5,hull_B)"],
     "proposed": "document.author(letter_5,master_Harman)",
     "expected": "REJECT",
     "reason": "E_DOCUMENT_LOCATION_IS_NOT_AUTHORSHIP"},
    {"id": "T003", "given": ["physical.cargo_aboard(lot_7,hull_B)"],
     "proposed": "title.owner(lot_7,owner_of_hull_B)",
     "expected": "REJECT", "reason": "E_CARGO_IS_NOT_OWNERSHIP"},
    {"id": "T004", "given": ["mail.intended_for(letter_8,Bristol)",
                             "mail.intercepted(letter_8)"],
     "proposed": "mail.delivered(letter_8)",
     "expected": "REJECT", "reason": "E_INTERCEPTED_IS_NOT_DELIVERED"},
    {"id": "T005", "given": ["credential.subject(pass_A,hull_A)",
                             "credential.presented_by(pass_A,hull_B)"],
     "proposed": "credential.valid_for(pass_A,hull_B)",
     "expected": "REJECT", "reason": "E_CROSS_LAYER_LAUNDERING"},
    {"id": "T006", "given": ["verdict(hull_B,CONDEMNED)",
                             "verdict(cargo_subset_A,CONDEMNED)",
                             "verdict(cargo_subset_B,RESTORED)"],
     "proposed": "verdict(all_cargo,CONDEMNED)",
     "expected": "REJECT", "reason": "E_PARTIAL_VERDICT_SCOPE"},
    {"id": "T007", "given": ["derived_from(translation_X,original_X)",
                             "sha256(translation_X)!=sha256(original_X)"],
     "proposed": "independent_evidence_roots=2",
     "expected": "REJECT", "reason": "E_DERIVED_DOC_IS_NOT_NEW_WITNESS"},
    {"id": "T008", "given": ["name(hull_A,LEG)", "name(hull_B,LEG)"],
     "proposed": "same_entity(hull_A,hull_B)",
     "expected": "REJECT", "reason": "E_NAME_IS_NOT_IDENTITY"},
)


def adjudicate(oracle: dict) -> dict:
    """Route one oracle to the receiver function that enforces its
    reason code and return the gate verdict. The dispatch is by
    reason_code — each maps to a real executable refusal, so the
    oracle passing means the LAW fired, not that a string matched."""
    reason = oracle["reason"]
    if reason == "E_PHYSICAL_EFFECT_IS_NOT_LEGALITY":
        got = pp.capture_legality(True)["legal_status"] == "UNADJUDICATED"
    elif reason == "E_DOCUMENT_LOCATION_IS_NOT_AUTHORSHIP":
        doc = pp.BundleDocument("letter_5", "S_phys", "letter", "root")
        got = pp.attribute_authorship(doc, "master_Harman")["reason"] == \
            reason
    elif reason == "E_CARGO_IS_NOT_OWNERSHIP":
        got = pp.attribute_ownership("lot_7", "owner_of_hull_B")["reason"] \
            == reason
    elif reason == "E_INTERCEPTED_IS_NOT_DELIVERED":
        letter = pp.BundleDocument("letter_8", "S_communication", "letter",
                                   "root")
        got = pp.delivery_status(letter)["delivered"] is False
    elif reason == "E_CROSS_LAYER_LAUNDERING":
        # a pass (S_identity credential) presented on hull_B does not
        # confer authority (S_authority) without a provenance witness.
        got = pp.CrossLayerClaim("c", "S_identity", "S_authority",
                                 "pass valid for hull_B").admit()["reason"] \
            == "E_UNWITNESSED_CROSS_LAYER_JOIN"
    elif reason == "E_PARTIAL_VERDICT_SCOPE":
        got = propagate_verdict(
            {"hull_B": "CONDEMNED", "cargo_subset_B": "RESTORED"},
            "hull_B", "all_cargo")["reason"] == reason
    elif reason == "E_DERIVED_DOC_IS_NOT_NEW_WITNESS":
        orig = Artifact("original_X", "hash1", evidence_root_id="root_X")
        deriv = Artifact("translation_X", "hash2",
                         derived_from="original_X", evidence_root_id="root_X")
        got = independent_roots_claim(orig, deriv)["reason"] == reason
    elif reason == "E_NAME_IS_NOT_IDENTITY":
        got = same_entity({"id": "hull_A"}, {"id": "hull_B"},
                          "same_name")["reason"] == reason
    else:
        return {"id": oracle["id"], "verdict": "NO_ENFORCER",
                "passed": False}
    gate = "REJECT" if got else "ADMIT"
    return {"id": oracle["id"], "gate": gate,
            "expected": oracle["expected"],
            "passed": gate == oracle["expected"], "reason": reason}


def run_gold_suite() -> dict:
    """Every oracle through its enforcer. 100% is the target and the
    only acceptable release gate for the hard falsifiers."""
    results = [adjudicate(o) for o in GOLD_ORACLES]
    failed = [r for r in results if not r["passed"]]
    return {"total": len(results), "passed": len(results) - len(failed),
            "failed": [r["id"] for r in failed],
            "all_held": not failed,
            "provenance": "vessel facts RELAYED, grade REPORTED; "
                          "oracle labels from constitutional rules"}


# ── the RELAYED vessel fixture, marked as such ──────────────────────────

VESSEL_FIXTURE = {
    "case_ref": "HCA 32/122/21",
    "source_grade": "REPORTED",
    "source": "operator relay citing TNA Discovery / Prize Papers "
              "Project public notices — NOT portal-read in this seat",
    "hulls": ("hull_A (original Juffrouw Elizabeth, abandoned)",
              "hull_B (later vessel, captured 1741)"),
    "credential": "pass_A originally binds hull_A; presented by hull_B",
    "capture": "by privateer Frances, 28 Jun / 9 Jul 1741 (double date "
               "kept, not normalized)",
    "decree": "3 Nov 1741 — ship + part of cargo CONDEMNED, rest "
              "RESTORED (scoped, not global)",
    "contested": "packet H described as allegedly counterfeit "
                 "(artifact authenticity != claim truth)",
    "missing": "no insurance policy confirmed in the accessed notice: "
               "NOT_CONFIRMED_IN_ACCESSED_CORPUS, never absence-of-event",
}
