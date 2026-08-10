"""🧾 WUL-ML V2 tests — negative confinement + positive inhabitation. authority=NONE."""

from wul_ml_v2 import A, E_LEGAL, STAR_MORPHISM, parse_sort, typecheck

step = lambda frm, to: {"from": frm, "to": to}


# ---------------- negative confinement: each forbidden coercion REJECTs, named

def _rejects(frm, to):
    verdict, reasons = typecheck([step(frm, to)])
    assert verdict == "REJECT"
    assert any("FORBIDDEN COERCION" in r or "AUTHORITY" in r for r in reasons), reasons
    return reasons


def test_garden_seed_to_receipt_rejected():
    reasons = _rejects(["GardenSeed"], "Receipt")
    assert "GardenSeed -> Receipt" in reasons[0]


def test_garden_seed_to_capability_rejected():
    _rejects(["GardenSeed"], "Capability")


def test_diagnosis_to_consequence_rejected():
    _rejects(["Diagnosis"], "Consequence")


def test_hal_result_to_capability_rejected():
    _rejects(["HALResult"], "Capability")


def test_hal_pass_alone_cannot_admit():
    # HAL PASS ⊬ ADMIT: lone HALResult (even PASS) cannot produce AdmissionDecision;
    # the whitelist requires the (WitnessedCandidate, HALResult) pair.
    _rejects(["HALResult[PASS]"], "AdmissionDecision")


def test_candidate_to_effect_rejected():
    _rejects(["Candidate"], "Effect")


def test_candidate_to_receipt_rejected():
    _rejects(["Candidate"], "Receipt")


def test_receipt_to_external_truth_rejected():
    _rejects(["Receipt"], "ExternalTruth")


def test_replay_state_to_external_truth_rejected():
    _rejects(["ReplayState"], "ExternalTruth")


# ---------------- positive inhabitation: the mediated chain ACCEPTs

FULL_CHAIN = [
    step(["GardenSeed"], "Candidate"),
    step(["Candidate"], "WitnessedCandidate"),
    step(["WitnessedCandidate"], "HALResult"),
    step(["WitnessedCandidate", "HALResult"], "AdmissionDecision"),
    step(["AdmissionDecision[ADMIT]"], "Capability"),
    step(["Capability", "AdmissionDecision[ADMIT]"], "Effect"),
    step(["Effect"], "Receipt"),
    step(["Receipt", "Receipt"], "ReplayState"),
]


def test_full_mediated_chain_accepts():
    verdict, reasons = typecheck(FULL_CHAIN)
    assert verdict == "ACCEPT", reasons


def test_each_legal_step_accepts_individually():
    for s in FULL_CHAIN:
        verdict, reasons = typecheck([s])
        assert verdict == "ACCEPT", (s, reasons)


def test_single_receipt_folds_to_replay_state():
    assert typecheck([step(["Receipt"], "ReplayState")])[0] == "ACCEPT"


# ---------------- authority monotonicity is independent of the whitelist

def test_authority_bootstrap_rejected_even_if_whitelist_corrupted():
    # Inject GardenSeed -> Capability into the legal map: the SECOND judgment
    # (authority monotonicity outside B_Γ) must still reject it.
    extra = [((("GardenSeed", None),), "Capability")]
    verdict, reasons = typecheck([step(["GardenSeed"], "Capability")], extra_legal=extra)
    assert verdict == "REJECT"
    assert any("AUTHORITY BOOTSTRAP" in r for r in reasons), reasons


def test_admit_bridge_is_the_only_authority_raise():
    assert typecheck([step(["AdmissionDecision[ADMIT]"], "Capability")])[0] == "ACCEPT"
    assert typecheck([step(["AdmissionDecision[HOLD]"], "Capability")])[0] == "REJECT"


# ---------------- ExternalTruth unreachability as a structural fact

def test_external_truth_unreachable_in_legal_map():
    named = set()
    for srcs, tgt in E_LEGAL:
        named.add(parse_sort(tgt)[0])
        named.update(b for b, _ in srcs)
    named.update(STAR_MORPHISM)
    assert "ExternalTruth" not in named


def test_external_truth_has_no_authority():
    assert A["ExternalTruth"] == 0
