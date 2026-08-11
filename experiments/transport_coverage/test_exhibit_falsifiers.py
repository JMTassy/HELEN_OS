"""Test-Driven Epistemology: the three EXHIBIT falsifiers run BEFORE any
collector exists. A collector can later be replaced or shown defective
without changing what PASS / FAIL / UNKNOWN mean.

  EXHIBIT-00  FALSE_CLOSURE          2/3 covered, 1 opaque  -> V_nu UNKNOWN
  EXHIBIT-01  SELF_VERDICT_INJECTION complete/authority     -> schema REJECT
  EXHIBIT-02  NEGATIVE_BY_SILENCE    D- without witness      -> integrity FAIL

The load-bearing distinction (per ruling):
    FAIL    = contract / integrity violation (defective object)
    UNKNOWN = honest epistemic insufficiency (sound but incomplete)
"""
from __future__ import annotations

import dataclasses
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import nu_exhibit as nx
from nu_exhibit import (
    DiscoveryReceipt,
    ExecutionEvent,
    NuExhibit,
    ObservationContract,
    build_exhibit,
    validate_exhibit_dict,
    verify_coverage,
    verify_integrity,
    verify_nu,
)


def _terminal(seq):
    return ExecutionEvent(seq=seq, surface="__terminal__", detail="end")


# ═══ EXHIBIT-00 · FALSE CLOSURE — the central falsifier ═════════════════

def test_EXHIBIT_00_false_closure_stays_unknown_never_two_thirds_pass():
    # Omega committed PRE-RUN: FILE, ENV, NATIVE all required.
    contract = ObservationContract.commit(
        {"FILE": "required", "ENV": "required", "NATIVE": "required"})
    # Collectors equipped for FILE and ENV only — NO native collector.
    equipped = frozenset({"FILE", "ENV"})
    # The run reads a file and an env var; makes no native call.
    events = [ExecutionEvent(0, "FILE", "read config.dat"),
              ExecutionEvent(1, "ENV", "read MODE"),
              _terminal(2)]
    ex = build_exhibit(contract, events, equipped)

    # The EXHIBIT builds successfully and is structurally sound:
    assert ex.schema == nx.SCHEMA
    assert ex.dependency_plus == ("ENV", "FILE")
    # NATIVE, unobservable with no collector, lands in opacity BY DEFAULT:
    assert ex.opacity_manifest == ("NATIVE",)
    assert verify_integrity(ex, contract)["verdict"] == "PASS"   # integrity OK

    # ...yet coverage is UNKNOWN. 2 of 3 is NOT a pass.
    v = verify_nu(ex, contract)
    assert v["v_nu"] == "UNKNOWN"
    assert v["class"] == "COVERAGE"
    assert v["pi_d"] == "NOT_EARNED"
    assert v["detail"]["opaque"] == ["NATIVE"]
    # VALID_BY_TRANSPORT is strictly forbidden here:
    assert "PASS" not in v["v_nu"]


def test_EXHIBIT_00_integrity_valid_does_not_imply_coverage():
    """Merkle-intact, contract-bound, information-rich — and still UNKNOWN.
    Integrity is necessary, never sufficient (the CT distinction)."""
    contract = ObservationContract.commit(
        {"FILE": "required", "NATIVE": "required"})
    ex = build_exhibit(contract,
                       [ExecutionEvent(0, "FILE", "read"), _terminal(1)],
                       equipped=frozenset({"FILE"}))
    assert ex.merkle_root == nx._merkle(ex.event_manifest)     # intact
    assert verify_integrity(ex, contract)["verdict"] == "PASS"
    assert verify_coverage(ex, contract)["verdict"] == "UNKNOWN"  # insufficient


def test_EXHIBIT_00_full_coverage_earns_pass_but_not_admission():
    """Positive control (non-vacuous): every required surface covered and
    zero opacity -> PASS. But even PASS carries admits:False. E_nu !-> Gamma."""
    contract = ObservationContract.commit(
        {"FILE": "required", "ENV": "required"})
    ex = build_exhibit(contract,
                       [ExecutionEvent(0, "FILE", "r"),
                        ExecutionEvent(1, "ENV", "r"), _terminal(2)],
                       equipped=frozenset({"FILE", "ENV"}))
    v = verify_nu(ex, contract)
    assert v["v_nu"] == "PASS" and v["pi_d"] == "EARNED"
    assert v["admits"] is False       # earned coverage is not admission


# ═══ EXHIBIT-01 · SELF-VERDICT INJECTION — schema rejects, never ignores ═

@pytest.mark.parametrize("banned", [
    "complete", "closed", "pi_d", "verdict", "coverage_verdict",
    "authority", "admit", "valid_by_transport", "true_support",
])
def test_EXHIBIT_01_self_verdict_field_is_unrepresentable(banned):
    payload = {"schema": nx.SCHEMA, "event_manifest": [], banned: True}
    with pytest.raises(ValueError, match="E_UNREPRESENTABLE_FIELD"):
        validate_exhibit_dict(payload)


def test_EXHIBIT_01_nested_self_verdict_also_rejected():
    payload = {"schema": nx.SCHEMA,
               "coverage_manifest": {"detail": {"authority": 1}}}
    with pytest.raises(ValueError, match="E_UNREPRESENTABLE_FIELD"):
        validate_exhibit_dict(payload)


def test_EXHIBIT_01_dataclass_has_no_verdict_or_authority_field():
    """Structural: not merely rejected on the wire — absent from the type.
    Freeze forbidden semantics, not permissible vocabulary."""
    fields = {f.name for f in dataclasses.fields(NuExhibit)}
    for banned in ("complete", "closed", "verdict", "pi_d", "authority",
                   "admit", "coverage_verdict"):
        assert banned not in fields
    with pytest.raises(TypeError):
        NuExhibit(schema=nx.SCHEMA, frame_manifest={}, event_manifest=(),
                  dependency_plus=(), discovery_minus=(), opacity_manifest=(),
                  coverage_manifest={}, merkle_root="x", complete=True)  # type: ignore


# ═══ EXHIBIT-02 · NEGATIVE BY SILENCE — not seen != shown absent ════════

def test_EXHIBIT_02_d_minus_without_witness_fails_integrity():
    """A discovery receipt whose method or result is empty is a claim of
    absence with no witnessed search. It is a CONTRACT violation (FAIL),
    not an observation gap (UNKNOWN)."""
    contract = ObservationContract.commit({"NETWORK": "required"})
    bad_receipt = DiscoveryReceipt(surface="NETWORK", method="", result="",
                                   omega_hash=contract.omega_hash)
    ex = build_exhibit(contract, [_terminal(0)], equipped=frozenset(),
                       discovery=[bad_receipt])
    v = verify_integrity(ex, contract)
    assert v["verdict"] == "FAIL"
    assert v["reason"] == "E_NEGATIVE_WITHOUT_WITNESS"
    # the COMPOSED verdict is FAIL, not UNKNOWN — different failure class
    assert verify_nu(ex, contract)["v_nu"] == "FAIL"


def test_EXHIBIT_02_witnessed_exclusion_is_valid_negative_dependency():
    """Positive control: a D- entry WITH an executed search (method +
    result) is a legitimate witnessed exclusion and passes integrity."""
    contract = ObservationContract.commit({"NETWORK": "required"})
    good = DiscoveryReceipt(surface="NETWORK", method="socket_hook_full_run",
                            result="no connect events across whole execution",
                            omega_hash=contract.omega_hash)
    ex = build_exhibit(contract, [_terminal(0)], equipped=frozenset({"NETWORK"}),
                       discovery=[good])
    assert verify_integrity(ex, contract)["verdict"] == "PASS"
    # NETWORK is now covered by exclusion -> coverage PASS
    assert verify_nu(ex, contract)["v_nu"] == "PASS"


def test_EXHIBIT_02_unobserved_defaults_to_opacity_not_exclusion():
    """The default law: not seen => U (opaque), never D- (excluded).
    Silence about NETWORK yields UNKNOWN, not a free exclusion."""
    contract = ObservationContract.commit({"NETWORK": "required"})
    ex = build_exhibit(contract, [_terminal(0)], equipped=frozenset())
    assert ex.opacity_manifest == ("NETWORK",)     # opaque, not excluded
    assert ex.discovery_minus == ()
    assert verify_nu(ex, contract)["v_nu"] == "UNKNOWN"


# ═══ anti-circularity · the Texas Sharpshooter cannot redraw Omega ══════

def test_precommit_binding_event_outside_omega_is_rejected():
    contract = ObservationContract.commit({"FILE": "required"})
    with pytest.raises(ValueError, match="E_SURFACE_OUTSIDE_OMEGA"):
        build_exhibit(contract, [ExecutionEvent(0, "SECRET_SURFACE", "x"),
                                 _terminal(1)], equipped=frozenset({"FILE"}))


def test_precommit_binding_unstamped_discovery_rejected():
    contract = ObservationContract.commit({"NETWORK": "required"})
    stale = DiscoveryReceipt("NETWORK", "search", "empty",
                             omega_hash="a-different-omega")   # drawn after shots
    with pytest.raises(ValueError, match="E_DISCOVERY_UNSTAMPED"):
        build_exhibit(contract, [_terminal(0)], frozenset({"NETWORK"}), [stale])


def test_omega_hash_changes_if_omega_is_expanded_after_the_fact():
    c1 = ObservationContract.commit({"FILE": "required"})
    c2 = ObservationContract.commit({"FILE": "required", "NATIVE": "required"})
    assert c1.omega_hash != c2.omega_hash        # retroactive Omega is detectable
    ex = build_exhibit(c1, [ExecutionEvent(0, "FILE", "r"), _terminal(1)],
                       frozenset({"FILE"}))
    # verifying the c1 exhibit against an expanded c2 contract FAILS integrity
    assert verify_integrity(ex, c2)["reason"] == "E_CONTRACT_MISMATCH"


# ═══ NOT_APPLICABLE must be witnessed (irrelevance witness) ═════════════

def test_not_applicable_without_witness_is_refused_at_commit():
    with pytest.raises(ValueError, match="E_IRRELEVANCE_UNWITNESSED"):
        ObservationContract.commit({"GPU": "irrelevant"})   # no justification


def test_not_applicable_with_witness_is_accepted_and_not_required():
    c = ObservationContract.commit(
        {"FILE": "required",
         "GPU": ("irrelevant", "property is pure-CPU by construction")})
    assert "GPU" not in c.required()
    ex = build_exhibit(c, [ExecutionEvent(0, "FILE", "r"), _terminal(1)],
                       frozenset({"FILE"}))
    assert verify_nu(ex, c)["v_nu"] == "PASS"     # GPU irrelevance does not block


# ═══ identity ignores views · re-cataloguing is not new evidence ════════

def test_identity_binds_observation_body_not_labels():
    c = ObservationContract.commit({"FILE": "required"})
    ex = build_exhibit(c, [ExecutionEvent(0, "FILE", "r"), _terminal(1)],
                       frozenset({"FILE"}))
    assert ex.exhibit_id == ex.identity()
    # mutating a coverage VIEW label must not change identity
    relabelled = dataclasses.replace(
        ex, coverage_manifest={**ex.coverage_manifest, "display_note": "pretty"})
    assert relabelled.identity() == ex.identity()   # same evidence, new label


def test_deterministic():
    c = ObservationContract.commit({"FILE": "required"})
    a = build_exhibit(c, [ExecutionEvent(0, "FILE", "r"), _terminal(1)],
                      frozenset({"FILE"}))
    b = build_exhibit(c, [ExecutionEvent(0, "FILE", "r"), _terminal(1)],
                      frozenset({"FILE"}))
    assert a.identity() == b.identity()
