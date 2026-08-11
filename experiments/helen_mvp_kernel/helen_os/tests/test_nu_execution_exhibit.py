"""ν — execution-exhibit falsifiers. 🔵 OBSERVED.

The tracer mints ADDRESSED VISIBILITY, not conclusions. EXHIBIT ≠ Π_D; a valid structure ⊬ adequate
coverage; opacity ⇒ UNKNOWN, never PASS. EXHIBIT-00 (False Closure) is the constitutional test.
"""
from dataclasses import replace

import pytest

from helen_os.audit.nu import (
    ClassDisposition, Coverage, Disposition, ExecutionEvent, NegativeDep, NuExhibit,
    NuIntegrityError, ObsClass, ObservationContract, OpaqueClass, PositiveDep,
    mint, valid_negative_witness, validate_exhibit_payload, verify_coverage,
)

FILE, ENV, NATIVE = ObsClass.FILE_READ, ObsClass.ENV_READ, ObsClass.NATIVE_BOUNDARY


def _ev(seq, cls):
    return ExecutionEvent(seq, cls, "CPYTHON_AUDIT", f"ref:{seq}", f"/x/{seq}", "read")


def _dplus(cls, seqs):
    return PositiveDep(f"dep:{cls.value}", cls, f"res:{cls.value}", tuple(seqs), "RULE_V1")


# ---- closed verdict surface: the EXHIBIT cannot carry a judgment coordinate
def test_nu_closed_verdict_surface():
    forbidden = {"complete", "pi_d_pass", "admit", "authority", "ledger_append", "valid_by_transport"}
    assert forbidden.isdisjoint(NuExhibit.__dataclass_fields__)


# ---- EXHIBIT-00 · FALSE CLOSURE (the constitutional test):
# FILE+ENV excellently covered, NATIVE opaque → structure VALID, VerifyCoverage UNKNOWN, NOT 2/3 PASS
def test_exhibit00_false_closure_is_unknown_not_pass():
    omega = ObservationContract("o", (FILE, ENV, NATIVE), "c17-python-v1", ("audit",))
    E = mint(
        omega,
        events=[_ev(1, FILE), _ev(2, ENV)],
        d_plus=[_dplus(FILE, [1]), _dplus(ENV, [2])],
        d_minus=[],
        opaque=[OpaqueClass(NATIVE, "no_defended_collector")],
    )
    v, reason = verify_coverage(E)
    assert v == Coverage.UNKNOWN and reason == "RELEVANT_OPACITY"
    assert v != Coverage.PASS          # two-of-three excellent does NOT earn PASS


# ---- retrospective Ω substitution → INVALID_CONTRACT (anti-circularity)
def test_nu_retrospective_omega_rejected():
    omega = ObservationContract("o", (FILE,), "p", ())
    E = mint(omega, [_ev(1, FILE)], [_dplus(FILE, [1])], [], [])
    tampered = replace(E, omega=ObservationContract("o", (FILE, ENV), "p", ()))  # Ω changed post-mint
    assert verify_coverage(tampered)[0] == Coverage.FAIL
    assert verify_coverage(tampered)[1] == "INVALID_CONTRACT"


# ---- d ∉ D⁺ ⊬ d ∈ D⁻: an unaccounted relevant class → UNCLASSIFIED (FAIL), never silent-covered
def test_nu_unaccounted_class_is_unclassified():
    omega = ObservationContract("o", (FILE, ENV), "p", ())
    E = mint(omega, [_ev(1, FILE)], [_dplus(FILE, [1])], [], [])   # ENV neither covered/opaque/NA
    v, reason = verify_coverage(E)
    assert v == Coverage.FAIL and reason == "UNCLASSIFIED_CLASS:ENV_READ"


# ---- forged event reference → FAIL
def test_nu_forged_event_ref_fails():
    omega = ObservationContract("o", (FILE,), "p", ())
    E = mint(omega, [_ev(1, FILE)], [_dplus(FILE, [99])], [], [])  # cites a seq that doesn't exist
    assert verify_coverage(E) == (Coverage.FAIL, "FORGED_EVENT_REF:dep:FILE_READ")


# ---- covered claim with no evidence → FAIL
def test_nu_covered_without_evidence_fails():
    omega = ObservationContract("o", (FILE,), "p", ())
    E = mint(omega, [_ev(1, FILE)], [_dplus(FILE, [])], [], [])    # empty evidence_events
    assert verify_coverage(E)[1] == "COVERED_WITHOUT_EVIDENCE:dep:FILE_READ"


# ---- NA without justification → FAIL (never an escape hatch)
def test_nu_na_without_justification_fails():
    omega = ObservationContract("o", (FILE,), "p", ())
    E = mint(omega, [], [], [], [], dispositions=[ClassDisposition(FILE, Disposition.NOT_APPLICABLE)])
    assert verify_coverage(E)[1] == "NA_WITHOUT_JUSTIFICATION:FILE_READ"


# ---- overlap: a class classified twice → FAIL (conservation, disjointness)
def test_nu_overlap_class_fails():
    omega = ObservationContract("o", (FILE,), "p", ())
    E = mint(omega, [_ev(1, FILE)], [_dplus(FILE, [1])], [], [OpaqueClass(FILE, "x")])  # covered AND opaque
    assert verify_coverage(E)[1] == "OVERLAP_CLASS:FILE_READ"


# ---- positive control (non-vacuity): all relevant covered by evidence/discovery → PASS
def test_nu_all_covered_passes():
    omega = ObservationContract("o", (FILE, ENV), "p", ())
    E = mint(
        omega,
        events=[_ev(1, FILE), _ev(2, ENV)],
        d_plus=[_dplus(FILE, [1]), _dplus(ENV, [2])],
        # D⁻ now must be a valid, EXECUTED, bound witness — not a bare placeholder
        d_minus=[NegativeDep(ObsClass.NAMESPACE_DISCOVERY, "ns/**", "recursive-v2", 37, "sha:m", executed=True)],
        opaque=[],
    )
    v, reason = verify_coverage(E)
    assert v == Coverage.PASS and reason == "ALL_RELEVANT_COVERED_OR_NA"


# ---- content-address: same body → same id; a VIEW change does NOT change identity
def test_nu_exhibit_id_excludes_views():
    omega = ObservationContract("o", (FILE,), "p", ())
    a = mint(omega, [_ev(1, FILE)], [_dplus(FILE, [1])], [], [])
    b = replace(a, views=("WULsigma", "json"))     # add rendering views only
    assert a.exhibit_id() == b.exhibit_id()        # new view ⊬ new evidence identity
    c = replace(a, opaque=(OpaqueClass(NATIVE, "x"),))  # a real content change
    assert a.exhibit_id() != c.exhibit_id()


# ============================================================================================
# EXHIBIT-02 · NEGATIVE-BY-SILENCE — silence cannot enter D⁻; only an executed, valid, bound
# exclusion witness can. "A test suite witnesses a surface; a constitution closes the boundaries."
# ============================================================================================
NET = ObsClass.EXTERNAL_SERVICE      # stands in for "NETWORK"

def _wit(cls, executed=True):
    return NegativeDep(cls, f"{cls.value}/**", "discovery-v2", 12, f"sha:{cls.value}", executed=executed)


# ---- EXHIBIT-02A · CONSTRUCTOR: a D⁻ exclusion with no witness (executed=False) → FAIL, never covered
def test_exhibit02a_constructor_negative_by_silence():
    omega = ObservationContract("o", (FILE, NET), "p", ())
    E = mint(omega, [_ev(1, FILE)], [_dplus(FILE, [1])],
             d_minus=[NegativeDep(NET, "net/**", "discovery-v2", 0, "sha:n", executed=False)],  # declared, not run
             opaque=[])
    v, reason = verify_coverage(E)
    assert v == Coverage.FAIL and reason == "UNWITNESSED_EXCLUSION:EXTERNAL_SERVICE"
    # the predicate agrees: an unexecuted obligation is not a witness
    assert not valid_negative_witness(NegativeDep(NET, "net/**", "discovery-v2", 0, "sha:n", executed=False))


# ---- EXHIBIT-02B · WIRE: a schema-shaped JSON payload with an unwitnessed D⁻ is REJECTED semantically
def test_exhibit02b_wire_payload_negative_by_silence():
    payload = {"schema_version": "NU_EXECUTION_EXHIBIT_V1",
               "d_plus": [{"cls": "FILE_READ"}],
               "d_minus": [{"cls": "EXTERNAL_SERVICE"}]}   # JSON well-formed + shaped, but no witness
    with pytest.raises(NuIntegrityError, match="UNWITNESSED_EXCLUSION_WIRE"):
        validate_exhibit_payload(payload)
    # a wire payload smuggling a verdict coordinate is also rejected (closed surface on the wire)
    for bad in ("authority", "complete", "admit", "pi_d_pass"):
        with pytest.raises(NuIntegrityError, match="FORBIDDEN_VERDICT_FIELD"):
            validate_exhibit_payload({bad: True, "d_minus": []})
    # a fully-witnessed, executed D⁻ passes the wire gate (non-vacuity)
    ok = {"d_minus": [{"cls": "EXTERNAL_SERVICE", "scope": "net/**",
                       "discovery_rule": "v2", "manifest_hash": "sha:n", "executed": True}]}
    assert validate_exhibit_payload(ok) is True


# ---- EXHIBIT-02C · WITNESS-LAUNDERING: one valid witness may NOT cover a second unwitnessed subject
def test_exhibit02c_witness_laundering():
    omega = ObservationContract("o", (FILE, NET, ENV), "p", ())
    E = mint(omega, [_ev(1, FILE)], [_dplus(FILE, [1])],
             # NET is validly witnessed+executed; ENV is declared but NOT executed → must still FAIL on ENV
             d_minus=[_wit(NET, executed=True), NegativeDep(ENV, "env/**", "v2", 3, "sha:e", executed=False)],
             opaque=[])
    v, reason = verify_coverage(E)
    assert v == Coverage.FAIL and reason == "UNWITNESSED_EXCLUSION:ENV_READ"   # NET's witness cannot launder ENV


# ---- positive control: two validly-witnessed executed exclusions cover their subjects → PASS
def test_exhibit02_valid_witnesses_pass():
    omega = ObservationContract("o", (FILE, NET, ENV), "p", ())
    E = mint(omega, [_ev(1, FILE)], [_dplus(FILE, [1])],
             d_minus=[_wit(NET, executed=True), _wit(ENV, executed=True)], opaque=[])
    v, reason = verify_coverage(E)
    assert v == Coverage.PASS and reason == "ALL_RELEVANT_COVERED_OR_NA"
