"""Executable falsifier for the gate calculus V2 (contract tests T1-T10).

Each test attempts to VIOLATE one law. The suite is green iff every illegal
promotion is refused with its named reason, the one legal promotion is
admitted with a full cost declaration, and replay is byte-identical.
"""
from __future__ import annotations

import pytest

from helen_os.kernel.promotion_gate import (
    GateConstructionError,
    IrreversibleGateError,
    Policy,
    PromotionGate,
    candidate_hash,
    genesis_state,
    promote,
    replay,
    state_hash,
)
from helen_os.ledger.hash_chain import canonical_json, sha256_hex

LAYERS = ["CLAIM", "SUPPORTED", "ADMITTED"]

LOSS = ("free-form claim context dropped; only payload fields survive",)
ASSUMPTIONS = ("payload_schema_complete",)


def _validator_ok(payload: dict) -> tuple[bool, str]:
    return (True, "ok") if payload.get("text") else (False, "empty_text")


def _assumption_ok(candidate: dict, state: dict) -> bool:
    return isinstance(candidate.get("payload"), dict)


POLICY = Policy(
    validators={"text_nonempty_v0": _validator_ok},
    assumption_checks={"payload_schema_complete": _assumption_ok},
    authority_transitions=frozenset({("NONE", "PROPOSE_ONLY")}),
    storage_transitions=frozenset({("S2_private", "S2_private")}),
    capabilities=frozenset({"PASS:G_claim_supported_v2"}),
)


def _genesis() -> dict:
    return genesis_state(LAYERS)


def _gate(state: dict, **overrides) -> PromotionGate:
    spec = dict(
        gate_id="G_claim_supported_v2",
        from_layer="CLAIM",
        to_layer="SUPPORTED",
        information_loss=LOSS,
        assumptions=ASSUMPTIONS,
        authority_before="NONE",
        authority_after="PROPOSE_ONLY",
        reversible=True,
        inverse_gate_id="G_supported_claim_v2",
        pre_hash=state_hash(state),
        validator_id="text_nonempty_v0",
        required_witnesses=("test_run",),
        source_storage_class="S2_private",
        target_storage_class="S2_private",
    )
    spec.update(overrides)
    return PromotionGate(**spec)


def _candidate(state: dict, text: str = "the sensor reported 42", layer: str = "CLAIM") -> dict:
    return {"candidate_id": "C1", "layer": layer, "payload": {"text": text}}


def _witnesses(candidate: dict) -> dict:
    return {"test_run": {"witness_hash": sha256_hex(canonical_json(candidate["payload"]))}}


# --- NO_GATE battery: the six forbidden silent promotions -------------------

@pytest.mark.parametrize(
    "from_layer,to_layer",
    [
        ("meeting_alignment", "adopted_decision"),
        ("rendered_edge", "fact"),
        ("validated_delta", "admitted_state"),
        ("acquirer_interest", "formal_offer"),
        ("S2_document", "remote_git"),
        ("witness_result", "world_truth"),
    ],
)
def test_no_gate_means_no_promotion(from_layer, to_layer):
    state = genesis_state([from_layer, to_layer])
    candidate = {"candidate_id": "X", "layer": from_layer, "payload": {"text": "x"}}
    new_state, receipt = promote(state, candidate, None, witness_bundle=None, policy=POLICY)
    assert receipt["verdict"] == "REJECT"
    assert receipt["reason"] == "REJECT_NO_GATE"
    assert new_state is state
    assert receipt["post_hash"] == receipt["pre_hash"]


# --- T1: claim -> supported without witness ---------------------------------

def test_t1_missing_witness_rejected():
    state = _genesis()
    gate = _gate(state)
    cand = _candidate(state)
    _, receipt = promote(state, cand, gate, witness_bundle={}, policy=POLICY)
    assert receipt["verdict"] == "REJECT"
    assert receipt["reason"] == "WITNESS_MISSING:test_run"


def test_t1b_fake_witness_rejected():
    state = _genesis()
    gate = _gate(state)
    cand = _candidate(state)
    fake = {"test_run": {"witness_hash": "f" * 64}}
    _, receipt = promote(state, cand, gate, witness_bundle=fake, policy=POLICY)
    assert receipt["reason"] == "FAKE_WITNESS:test_run"


# --- T2: validated but no capability (VALIDATED != ADMITTED) ----------------

def test_t2_validated_without_capability_rejected():
    state = _genesis()
    gate = _gate(state)
    cand = _candidate(state)
    assert POLICY.validators["text_nonempty_v0"](cand["payload"])[0] is True
    bare = Policy(
        validators=POLICY.validators,
        assumption_checks=POLICY.assumption_checks,
        authority_transitions=POLICY.authority_transitions,
        storage_transitions=POLICY.storage_transitions,
        capabilities=frozenset(),
    )
    _, receipt = promote(state, cand, gate, witness_bundle=_witnesses(cand), policy=bare)
    assert receipt["reason"] == "CAPABILITY_MISSING:PASS:G_claim_supported_v2"


# --- T3: illegal location promotion (S3 -> public_git) ----------------------

def test_t3_illegal_location_promotion_rejected():
    state = _genesis()
    gate = _gate(state, source_storage_class="S3_secret", target_storage_class="S0_public_git")
    cand = _candidate(state)
    _, receipt = promote(state, cand, gate, witness_bundle=_witnesses(cand), policy=POLICY)
    assert receipt["reason"] == "ILLEGAL_LOCATION_PROMOTION:S3_secret->S0_public_git"


# --- T4 covered by NO_GATE battery (rendered_edge -> fact) ------------------

# --- T5: stale pre_hash — gate bound to another state -----------------------

def test_t5_stale_pre_hash_rejected():
    state_a = _genesis()
    gate_a = _gate(state_a)
    c0 = _candidate(state_a, "earlier")
    state_b, first = promote(state_a, c0, gate_a, witness_bundle=_witnesses(c0), policy=POLICY)
    assert first["verdict"] == "ADMITTED"
    cand = _candidate(state_b)
    new_state, receipt = promote(state_b, cand, gate_a, witness_bundle=_witnesses(cand), policy=POLICY)
    assert receipt["reason"] == "STALE_PRE_STATE"
    assert new_state is state_b


# --- T6: gate without declared loss / assumptions cannot exist --------------

def test_t6_undeclared_loss_unconstructible():
    state = _genesis()
    with pytest.raises(GateConstructionError, match="UNDECLARED_LOSS"):
        _gate(state, information_loss=())


def test_t6b_undeclared_assumptions_unconstructible():
    state = _genesis()
    with pytest.raises(GateConstructionError, match="UNDECLARED_ASSUMPTION"):
        _gate(state, assumptions=())


def test_t6c_empty_loss_entry_unconstructible():
    state = _genesis()
    with pytest.raises(GateConstructionError, match="UNDECLARED_LOSS"):
        _gate(state, information_loss=("",))


# --- hidden assumption: unknown or unsatisfied -> fail closed ----------------

def test_unknown_assumption_fails_closed():
    state = _genesis()
    gate = _gate(state, assumptions=("undocumented_belief",))
    cand = _candidate(state)
    _, receipt = promote(state, cand, gate, witness_bundle=_witnesses(cand), policy=POLICY)
    assert receipt["reason"] == "UNKNOWN_ASSUMPTION:undocumented_belief"


def test_unsatisfied_assumption_rejected():
    def never(candidate: dict, state: dict) -> bool:
        return False

    state = _genesis()
    gate = _gate(state)
    cand = _candidate(state)
    policy = Policy(
        validators=POLICY.validators,
        assumption_checks={"payload_schema_complete": never},
        authority_transitions=POLICY.authority_transitions,
        storage_transitions=POLICY.storage_transitions,
        capabilities=POLICY.capabilities,
    )
    _, receipt = promote(state, cand, gate, witness_bundle=_witnesses(cand), policy=policy)
    assert receipt["reason"] == "UNSATISFIED_ASSUMPTION:payload_schema_complete"


# --- implicit authority gain -------------------------------------------------

def test_implicit_authority_gain_rejected():
    state = _genesis()
    gate = _gate(state, authority_before="NONE", authority_after="EXECUTE")
    cand = _candidate(state)
    _, receipt = promote(state, cand, gate, witness_bundle=_witnesses(cand), policy=POLICY)
    assert receipt["reason"] == "ILLEGAL_AUTHORITY_PROMOTION:NONE->EXECUTE"


# --- T7: legal promotion admits with full cost declaration ------------------

def test_t7_legal_promotion_admits_and_declares_cost():
    state = _genesis()
    gate = _gate(state)
    cand = _candidate(state)
    bundle = _witnesses(cand)
    new_state, receipt = promote(state, cand, gate, witness_bundle=bundle, policy=POLICY)
    assert receipt["verdict"] == "ADMITTED"
    assert receipt["gate_id"] == "G_claim_supported_v2"
    assert receipt["pre_hash"] == state_hash(state)
    assert receipt["candidate_hash"] == candidate_hash(cand)
    assert receipt["post_hash"] == state_hash(new_state)
    assert receipt["information_loss"] == list(LOSS)
    assert receipt["assumptions"] == list(ASSUMPTIONS)
    assert receipt["authority_delta"] == ["NONE", "PROPOSE_ONLY"]
    assert receipt["storage_delta"] == ["S2_private", "S2_private"]
    assert receipt["reversible"] is True
    assert receipt["inverse_gate_id"] == "G_supported_claim_v2"
    assert receipt["authority"] is False
    assert new_state["layers"]["SUPPORTED"] == [
        {"payload": cand["payload"], "storage_class": "S2_private"}
    ]
    assert state["layers"]["SUPPORTED"] == []


# --- T9: rejection is a first-class receipt, never a mutation ---------------

def test_t9_rejection_never_mutates_state():
    state = _genesis()
    before = canonical_json(state)
    gate = _gate(state)
    cand = _candidate(state, text="")  # fails validation
    new_state, receipt = promote(state, cand, gate, witness_bundle=_witnesses(cand), policy=POLICY)
    assert receipt["verdict"] == "REJECT"
    assert receipt["reason"].startswith("VALIDATION_FAILED")
    assert new_state is state
    assert canonical_json(state) == before
    assert receipt["post_hash"] == receipt["pre_hash"]
    assert receipt["authority"] is False


def test_wrong_source_layer_rejected():
    state = _genesis()
    gate = _gate(state)
    cand = _candidate(state, layer="SUPPORTED")
    _, receipt = promote(state, cand, gate, witness_bundle=_witnesses(cand), policy=POLICY)
    assert receipt["reason"].startswith("WRONG_SOURCE_LAYER")


def test_unknown_validator_fails_closed():
    state = _genesis()
    gate = _gate(state, validator_id="ghost_validator")
    cand = _candidate(state)
    _, receipt = promote(state, cand, gate, witness_bundle=_witnesses(cand), policy=POLICY)
    assert receipt["reason"] == "UNKNOWN_VALIDATOR:ghost_validator"


# --- T10: reversibility cannot be faked -------------------------------------

def test_t10_inverse_of_irreversible_gate_raises():
    state = _genesis()
    gate = _gate(state, reversible=False, inverse_gate_id=None)
    with pytest.raises(IrreversibleGateError):
        gate.inverse()


def test_t10b_reversible_without_inverse_unconstructible():
    state = _genesis()
    with pytest.raises(GateConstructionError, match="reversible=True without an inverse"):
        _gate(state, reversible=True, inverse_gate_id=None)


def test_t10c_irreversible_with_inverse_unconstructible():
    state = _genesis()
    with pytest.raises(GateConstructionError, match="may not advertise an inverse"):
        _gate(state, reversible=False, inverse_gate_id="G_ghost_inverse")


# --- T8: replay is byte-identical, rejections included ----------------------

def test_t8_replay_byte_identical_including_rejections():
    state = _genesis()
    journal = []

    g1 = _gate(state)
    c1 = _candidate(state, "first")
    w1 = _witnesses(c1)
    state, r1 = promote(state, c1, g1, witness_bundle=w1, policy=POLICY)
    journal.append({"candidate": c1, "gate": g1, "witness_bundle": w1, "receipt": r1})

    c2 = _candidate(state, "second")
    state, r2 = promote(state, c2, None, witness_bundle=None, policy=POLICY)
    journal.append({"candidate": c2, "gate": None, "witness_bundle": None, "receipt": r2})

    g3 = _gate(state)
    c3 = _candidate(state, "third")
    w3 = _witnesses(c3)
    state, r3 = promote(state, c3, g3, witness_bundle=w3, policy=POLICY)
    journal.append({"candidate": c3, "gate": g3, "witness_bundle": w3, "receipt": r3})

    assert r1["verdict"] == "ADMITTED"
    assert r2["reason"] == "REJECT_NO_GATE"
    assert r3["verdict"] == "ADMITTED"

    replayed_state, replayed_receipts = replay(_genesis(), journal, POLICY)
    assert canonical_json(replayed_state) == canonical_json(state)
    assert replayed_receipts == [r1, r2, r3]


def test_t8b_replay_divergence_is_first_class_failure():
    state = _genesis()
    g1 = _gate(state)
    c1 = _candidate(state, "first")
    w1 = _witnesses(c1)
    _, r1 = promote(state, c1, g1, witness_bundle=w1, policy=POLICY)
    tampered = dict(r1, verdict="REJECT")
    journal = [{"candidate": c1, "gate": g1, "witness_bundle": w1, "receipt": tampered}]
    with pytest.raises(ValueError, match="replay divergence"):
        replay(_genesis(), journal, POLICY)
