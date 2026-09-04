"""MATERIAL_WITNESS_BOUNDARY_BEZAE_V0 — status follows the warrant consumed, not plausibility. 🔵 OBSERVED.

Grounded in Scrivener's 1864 practice: record every recoverable stroke; never restore letters merely
because they can be conjectured. Four adversarial cases + the hard invariants.
"""
from helen_os.audit.conjectural_emendation import (
    CONJECTURE, RECONSTRUCTED_TRACE, UNSUPPORTED, WITNESSED, WITNESSED_CORRECTION,
    Reading, admissible_as_conjecture, classify, conjecture_grade, may_serve_as_root, witness_states,
)


# ─────────── the four Bezae boundary cases ───────────
def test_case1_visible_first_hand_is_witnessed():
    assert classify(Reading(material=1)) == WITNESSED


def test_case2_visible_correction_is_witnessed_correction_never_conjecture():
    r = Reading(material=1, is_correction=True, corrects="reading_r0")
    assert classify(r) == WITNESSED_CORRECTION           # a corrector's ink is material evidence
    assert classify(r) != CONJECTURE
    assert witness_states(r) == ("W0:reading_r0", "W1:correction")  # both temporal layers witnessed


def test_case3_partial_trace_is_reconstruction_not_conjecture_not_full_witness():
    r = Reading(material=0, trace=True, derivation=("coherence",))
    assert classify(r) == RECONSTRUCTED_TRACE            # partial physical trace — preserve uncertainty
    assert classify(r) not in (WITNESSED, CONJECTURE)


def test_case4_editor_supply_no_trace_is_conjecture():
    r = Reading(material=0, trace=False, derivation=("explains_variants", "lectio_difficilior"))
    assert classify(r) == CONJECTURE
    assert admissible_as_conjecture(r) is True           # motivated, admissible AS conjecture — still not witnessed


# ─────────── hard invariants ───────────
def test_derivation_cannot_substitute_for_material():
    # every internal canon satisfied, but zero material and zero trace → still only a conjecture
    r = Reading(material=0, trace=False,
                derivation=("explains_variants", "lectio_difficilior", "intrinsic_fit", "coherence"))
    assert classify(r) == CONJECTURE                     # D(r) ⊬ WITNESSED, however persuasive


def test_later_correctness_does_not_manufacture_a_witness():
    # strengthening the derivational argument NEVER moves a conjecture toward witnessed;
    # only material/trace changes the class.
    weak = Reading(material=0, derivation=("coherence",))
    strong = Reading(material=0, derivation=("explains_variants", "lectio_difficilior", "intrinsic_fit", "coherence"))
    assert classify(weak) == CONJECTURE and classify(strong) == CONJECTURE
    # add ONE material attestation → and only then does it become witnessed
    assert classify(Reading(material=1, derivation=weak.derivation)) == WITNESSED


def test_interpolation_and_singular_reading_are_witnessed_not_conjecture():
    # THE correction to the earlier intuition: a wild, singular, interpolated reading that is
    # PHYSICALLY IN the manuscript is WITNESSED — not a conjecture, not N_epi=0. Its being an
    # interpolation is a hypothesis about an EARLIER state, scored elsewhere (epistemic_roots).
    singular_interpolation = Reading(material=1)          # attested only by Bezae, but attested
    assert classify(singular_interpolation) == WITNESSED
    assert classify(singular_interpolation) != CONJECTURE


# ─────────── the root fence ───────────
def test_only_material_readings_may_serve_as_root():
    assert may_serve_as_root(Reading(material=1)) is True
    assert may_serve_as_root(Reading(material=1, is_correction=True)) is True
    assert may_serve_as_root(Reading(material=0, trace=True)) is False        # uncertain trace, not a clean root
    assert may_serve_as_root(Reading(material=0, derivation=("explains_variants",))) is False  # conjecture ⊬ root


def test_no_material_no_trace_no_derivation_is_unsupported():
    assert classify(Reading()) == UNSUPPORTED
    assert conjecture_grade(Reading()) is None
    assert classify(Reading(derivation=("vibes",))) == UNSUPPORTED            # non-canon criteria ignored
