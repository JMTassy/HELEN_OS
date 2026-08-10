"""HAL Witness Law falsification suite — ∅ ⇒ 🟢🛡 must be unconstructible.
🔵 OBSERVED · covers the seven spec falsifications + canary discrimination."""
import pytest

from helen_os.kernel.hal import (
    FAIL, PASS, UNKNOWN, CoverageReceipt, HALCheckResult, check, h_v, summarize,
)

# --- toy evaluation package: a graph whose edges must all use ALLOWED relation
X = {"edges": [
    {"id": "e1", "rel": "OK"}, {"id": "e2", "rel": "OK"}, {"id": "e3", "rel": "OK"},
]}
X_BAD = {"edges": [{"id": "e1", "rel": "OK"}, {"id": "e2", "rel": "ILLEGAL"}]}

surface = lambda x: [e["id"] for e in x["edges"]]
derivable = lambda x: [f'{e["id"]}:{e["rel"]}' for e in x["edges"]]


def honest_witness(x):
    checked, refs, holds = [], [], True
    for e in x["edges"]:
        checked.append(e["id"])
        refs.append(f'{e["id"]}:{e["rel"]}')
        if e["rel"] != "OK":
            holds = False
    return holds, CoverageReceipt(
        input_hash=h_v(x), predicate_id="edges_ok", predicate_version="1",
        required_item_ids=tuple(surface(x)), checked_item_ids=tuple(checked),
        evidence_refs=tuple(refs),
    )


def poison(x):  # canary constructor: inject one violation
    return {"edges": x["edges"] + [{"id": "e_poison", "rel": "ILLEGAL"}]}


def run(witness, x=X, canary=poison):
    return check("edges_ok", x, witness, surface, derivable,
                 witness_id="edges_v1", canary=canary)


# --- positive controls: live witness discriminates both ways

def test_live_witness_pass_and_fail():
    r = run(honest_witness)
    assert r.verdict == PASS and r.live and r.checked_units == r.required_units == 3
    r_bad = run(honest_witness, x=X_BAD)
    assert r_bad.verdict == FAIL and r_bad.live  # live ∧ ¬P → FAIL, not UNKNOWN


# --- the seven spec falsifications: every one → UNKNOWN, never PASS

def test_empty_output_on_nonempty_input():
    def blind(x):
        return True, CoverageReceipt(h_v(x), "edges_ok", "1", tuple(surface(x)), (), ())
    r = run(blind, canary=None)
    assert r.verdict == UNKNOWN and r.reason_code == "INCOMPLETE_COVERAGE"


def test_dropped_final_element():
    def drops_last(x):
        seen = x["edges"][:-1]
        return True, CoverageReceipt(
            h_v(x), "edges_ok", "1", tuple(surface(x)),
            tuple(e["id"] for e in seen), tuple(f'{e["id"]}:{e["rel"]}' for e in seen))
    r = run(drops_last, canary=None)
    assert r.verdict == UNKNOWN and r.reason_code == "INCOMPLETE_COVERAGE"


def test_duplicate_counted_twice_does_not_fake_coverage():
    def duper(x):
        return True, CoverageReceipt(
            h_v(x), "edges_ok", "1", tuple(surface(x)),
            ("e1", "e1", "e2"),  # 3 checks claimed, only 2 distinct — dups collapse
            ("e1:OK", "e2:OK"))
    r = run(duper, canary=None)
    assert r.verdict == UNKNOWN and r.reason_code == "INCOMPLETE_COVERAGE"


def test_stale_input_hash():
    def stale(x):
        _, receipt = honest_witness(X_BAD)  # evaluated a DIFFERENT package
        return True, receipt
    r = run(stale, canary=None)
    assert r.verdict == UNKNOWN and r.reason_code == "WITNESS_NOT_BOUND"


def test_fabricated_evidence():
    def fabricator(x):
        return True, CoverageReceipt(
            h_v(x), "edges_ok", "1", tuple(surface(x)), tuple(surface(x)),
            ("e1:OK", "e99:INVENTED"))  # ref not derivable from x
    r = run(fabricator, canary=None)
    assert r.verdict == UNKNOWN and r.reason_code == "FABRICATED_EVIDENCE"


def test_parser_exception_is_not_pass():
    def crasher(x):
        raise ValueError("parse error")
    r = run(crasher, canary=None)
    assert r.verdict == UNKNOWN and r.reason_code == "WITNESS_ERROR"


def test_pass_without_evidence_object():
    def no_receipt(x):
        return True, None
    r = run(no_receipt, canary=None)
    assert r.verdict == UNKNOWN and r.reason_code == "NO_EVIDENCE"


# --- canary discrimination: engagement without the ability to fail is blindness

def test_tautological_witness_killed_by_canary():
    def tautology(x):  # consumes everything, approves everything
        return True, CoverageReceipt(
            h_v(x), "edges_ok", "1", tuple(surface(x)), tuple(surface(x)),
            tuple(derivable(x)))
    r = run(tautology)  # canary active
    assert r.verdict == UNKNOWN and r.reason_code == "WITNESS_NOT_DISCRIMINATING"
    assert run(honest_witness).verdict == PASS  # honest witness kills the canary


# --- structural unconstructibility + aggregate law

def test_pass_without_liveness_unconstructible():
    with pytest.raises(TypeError, match="WITNESS_LAW"):
        HALCheckResult("i", PASS, "h", "w", "1", 3, 3, 3, "e", live=False)
    with pytest.raises(TypeError, match="WITNESS_LAW"):
        HALCheckResult("i", FAIL, "h", "w", "1", 3, 0, 0, "e", live=False)
    with pytest.raises(TypeError, match="WITNESS_LAW"):
        HALCheckResult("i", PASS, "h", "w", "1", 3, 2, 2, "e", live=True)  # partial


def test_aggregate_fail_dominates_unknown_dominates_pass():
    ok = run(honest_witness)
    unk = run(lambda x: (True, None), canary=None)
    bad = run(honest_witness, x=X_BAD)
    assert summarize([ok, ok]) == PASS
    assert summarize([ok, unk]) == UNKNOWN
    assert summarize([ok, unk, bad]) == FAIL
