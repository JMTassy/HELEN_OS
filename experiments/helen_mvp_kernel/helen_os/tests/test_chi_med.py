"""χ_med — A⁰ cannot reach ΔG except via admit + κ. 🔵 OBSERVED.

Includes the mediation triangle:
  unauthorized path → ΔG = 0
  authorized live path → ΔG ≠ 0 exactly once, replay matches
  capability reuse → ΔG = 0
"""
import pytest

from helen_os.kernel.capability import CapabilityFactory, Executor, LogicalClock
from helen_os.ledger import event_log
from helen_os.ledger.event_log import append_event, read_events, set_capability_guard
from helen_os.kernel.chi_report import build_report

C_HASH = "c" * 64
PRE = "a" * 64


@pytest.fixture
def guarded(tmp_path):
    """Install a capability guard on the single enumerated sink; always uninstall."""
    clock = LogicalClock()
    executor = Executor(clock)

    def guard(event, capability):
        if not executor.authorizes(capability):
            raise PermissionError("E_APPEND_WITHOUT_LIVE_CAP")

    set_capability_guard(guard)
    try:
        yield tmp_path / "ledger.ndjson", clock, executor
    finally:
        set_capability_guard(None)


def test_med_01_direct_append_without_cap_denied(guarded):
    ledger, _, _ = guarded
    with pytest.raises(PermissionError, match="E_APPEND_WITHOUT_LIVE_CAP"):
        append_event(ledger, {"op": "sneak"})  # A0 context, no κ
    assert read_events(ledger) == []  # ΔG = 0


def test_med_02_mint_without_admit_denied(guarded):
    _, clock, _ = guarded
    factory = CapabilityFactory(clock)
    for decision in ("HOLD", "REJECT", "PASS"):  # HAL PASS is not ADMIT
        with pytest.raises(PermissionError, match="E_MINT_WITHOUT_ADMIT"):
            factory.mint(binds_hash=C_HASH, pre_state_hash=PRE,
                         scope="ledger.append", admission_decision=decision)


def test_med_03_dead_caps_produce_no_effect(guarded):
    ledger, clock, executor = guarded
    factory = CapabilityFactory(clock)
    cap = factory.mint(binds_hash=C_HASH, pre_state_hash=PRE,
                       scope="ledger.append", admission_decision="ADMIT", ttl_ticks=5)
    # bind mismatch / scope mismatch / expiry — none may fire the effect
    assert executor.invoke(cap, expected_hash="d" * 64, pre_state_hash=PRE,
                           scope="ledger.append").status == "BIND_MISMATCH"
    assert executor.invoke(cap, expected_hash=C_HASH, pre_state_hash=PRE,
                           scope="config.write").status == "SCOPE_MISMATCH"
    clock.tick(10)
    assert executor.invoke(cap, expected_hash=C_HASH, pre_state_hash=PRE,
                           scope="ledger.append").status == "EXPIRED"
    assert read_events(ledger) == []  # ΔG = 0 throughout


def test_med_oneshot_triangle(guarded):
    ledger, clock, executor = guarded
    factory = CapabilityFactory(clock)
    cap = factory.mint(binds_hash=C_HASH, pre_state_hash=PRE,
                       scope="ledger.append", admission_decision="ADMIT")

    r1 = executor.invoke(
        cap, expected_hash=C_HASH, pre_state_hash=PRE, scope="ledger.append",
        effect=lambda: append_event(ledger, {"op": "governed_write"}, capability=cap),
    )
    assert r1.status == "EXECUTED"
    assert len(read_events(ledger)) == 1  # ΔG ≠ 0 exactly once

    r2 = executor.invoke(
        cap, expected_hash=C_HASH, pre_state_hash=PRE, scope="ledger.append",
        effect=lambda: append_event(ledger, {"op": "replayed_write"}, capability=cap),
    )
    assert r2.status == "ALREADY_CONSUMED"
    assert len(read_events(ledger)) == 1  # reuse → ΔG = 0


def test_med_04_surface_inventory_scoped_report(guarded):
    ledger, clock, executor = guarded
    # Enumerated mutation sinks in kernel+ledger packages (recon: append_event is
    # the only file-write sink). Exercised from A0 above.
    inventory = ["helen_os.ledger.event_log.append_event"]
    report = build_report(
        gov={"verdict": "PASS", "tests": "8/8"},
        mem={"verdict": "PASS_SCOPED", "tests": "3/4", "scope": "seat=laptop"},
        med={
            "verdict": "PASS_SCOPED",
            "surface_inventory": inventory,
            "mutation_surfaces_enumerated": len(inventory),
            "mutation_surfaces_tested": len(inventory),
            "mutation_surfaces_unclassified": 0,
            "positive_control": "PASS",
        },
        comp={"verdict": "PASS", "tests": "3/3"},
        cons={"verdict": "PASS", "tests": "2/2"},
    )
    assert report["chi_med"]["verdict"] == "PASS_SCOPED"
    assert report["chi_med"]["inventory_hash"].startswith("sha256:")
    assert "not a universal claim" in report["claim_scope"]


def test_med_unclassified_forces_incomplete():
    report = build_report(
        gov={}, mem={}, comp={}, cons={},
        med={"verdict": "PASS", "surface_inventory": [],
             "mutation_surfaces_unclassified": 2},
    )
    assert report["chi_med"]["verdict"] == "INCOMPLETE"  # never PASS with unknowns
