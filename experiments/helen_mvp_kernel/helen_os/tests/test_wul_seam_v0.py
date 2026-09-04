"""WUL_SEAM_V0 — the three tonight-tests + load-bearing + reverse trace. 🔵 OBSERVED · authority=false.

Earned boundary on PASS: "in this non-sovereign prototype a WUL rule is load-bearing end to end —
ΔWUL ⇒ ΔIR ⇒ ΔΓ ⇒ ΔRuntime, and a runtime reject traces back to the IR rule and the WUL line." NOT a proof.
"""
from helen_os.kernel.wul_seam_v0 import (
    WUL_SOURCE, parse, compile_ir, gamma_wul, run_receipt, _good,
)
from helen_os.kernel.vertical_slice_v0 import GENESIS_POLICY, executor_execute, Capability, NO_EFFECT

P = GENESIS_POLICY
IR = compile_ir(parse(WUL_SOURCE))


def test_missing_witness_rejects():
    r = gamma_wul(_good(witness=None), IR, P)
    assert r.verdict == "DENY" and r.reason.startswith("REQUIRE_UNMET")


def test_valid_applicable_witness_admits():
    r = gamma_wul(_good(), IR, P)
    assert r.verdict == "AUTHORIZE" and r.capability is not None


def test_direct_executor_bypass_killed():
    assert executor_execute(None, P) == NO_EFFECT
    forged = Capability("write_file", "sandbox/out.txt", P.version_hash, "n", "x", "FORGED")
    assert executor_execute(forged, P) == NO_EFFECT


def test_delta_wul_changes_runtime_behavior():
    # remove the REQUIRE rule from the WUL → recompile → the same missing-witness proposal now ADMITs
    wul_without = "\n".join(l for l in WUL_SOURCE.splitlines() if not l.strip().startswith("REQUIRE"))
    ir2 = compile_ir(parse(wul_without))
    assert IR.ir_hash != ir2.ir_hash                                  # ΔWUL ⇒ ΔIR
    assert gamma_wul(_good(witness=None), IR, P).verdict == "DENY"    # rule present
    assert gamma_wul(_good(witness=None), ir2, P).verdict == "AUTHORIZE"  # rule gone ⇒ ΔRuntime


def test_reverse_trace_reject_to_ir_and_wul():
    r = gamma_wul(_good(witness=None), IR, P)
    assert r.ir_rule and r.ir_rule.startswith("IR:REQUIRE")
    assert r.wul_rule and r.wul_rule.startswith("WUL:L")


def test_unknown_wul_statement_fails_closed():
    import pytest
    with pytest.raises(ValueError):
        parse("TYPE X\nFROBNICATE Y")


def test_receipt_accepted():
    r = run_receipt()
    assert r["acceptance_vector"] == (True,) * 6
    assert r["accepted"] is True
