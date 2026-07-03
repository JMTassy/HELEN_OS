"""Tests for tools/helen_sandbox_agent_adapter.py — implements AR-1f936d1bda4b
(top test_gap in the autoresearch triage queue: adapter had zero tests).

Covers the four HELEN checks (anti-ghost, capability registry, authority linter,
forbidden paths), canonical hashing, and receipt binding. NON_SOVEREIGN.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))
from helen_sandbox_agent_adapter import (  # noqa: E402
    _canon,
    _sha256_hex,
    anti_ghost_check,
    build_local_receipt,
    capability_registry_check,
    check_forbidden_paths,
    run_helen_checks,
)


def _full_packet():
    return {
        "trace_id": "sbx-test123",
        "diff_summary": "added a null-guard in parser",
        "files_touched": ["tools/example.py"],
        "tests_run": {"passed": 3, "failed": 0, "total": 3},
        "capability_claims": ["run_tests", "propose_patch"],
        "operator_task": "fix the parser guard",
        "local_receipt": {"packet_hash": "deadbeef"},
    }


# --- canonical hashing -------------------------------------------------------

def test_canon_is_deterministic_and_sorted():
    a = _canon({"b": 1, "a": [2, 1]})
    b = _canon({"a": [2, 1], "b": 1})
    assert a == b == '{"a":[2,1],"b":1}'


def test_sha256_str_bytes_equivalent():
    assert _sha256_hex("x") == _sha256_hex(b"x")


# --- forbidden paths ---------------------------------------------------------

def test_forbidden_paths_catch_sovereign_prefixes():
    hits = check_forbidden_paths([
        "town/ledger_v1.ndjson",
        "helen_os/governance/x.py",
        "mayor_keys.json",
        "some/nested/oracle_town/kernel/daemon.py",
    ])
    assert len(hits) == 4


def test_forbidden_paths_pass_safe_files():
    assert check_forbidden_paths(["tools/x.py", "tests/test_x.py", "docs/a.md"]) == []


# --- anti-ghost --------------------------------------------------------------

def test_anti_ghost_blocks_empty_packet():
    verdict, findings = anti_ghost_check({})
    assert verdict == "GHOST"
    assert any("trace_id" in f for f in findings)
    assert any("no evidence" in f for f in findings)


def test_anti_ghost_passes_evidenced_packet():
    verdict, findings = anti_ghost_check(_full_packet())
    assert verdict == "PASS"
    assert findings == []


# --- capability registry -----------------------------------------------------

def test_dangerous_capability_flagged():
    verdict, findings = capability_registry_check(["run_tests", "write_ledger"])
    assert verdict == "FLAGGED"
    assert any("dangerous" in f for f in findings)


def test_unknown_capability_recorded_not_silent():
    verdict, findings = capability_registry_check(["telepathy"])
    assert verdict == "FLAGGED"
    assert any("unknown" in f for f in findings)


def test_safe_capabilities_pass():
    verdict, _ = capability_registry_check(["run_tests", "propose_patch"])
    assert verdict == "PASS"


def test_non_list_claims_flagged():
    verdict, findings = capability_registry_check("run_tests")  # type: ignore[arg-type]
    assert verdict == "FLAGGED"


# --- local receipt -----------------------------------------------------------

def test_receipt_hash_excludes_receipt_itself_and_is_stable():
    pkt = _full_packet()
    r1 = build_local_receipt("t", pkt)
    pkt_with_receipt = dict(pkt, local_receipt=r1)
    r2 = build_local_receipt("t", pkt_with_receipt)
    assert r1["packet_hash"] == r2["packet_hash"]  # receipt never hashes itself
    assert r1["authority"] == "NON_SOVEREIGN"
    assert r1["canon"] == "NO_SHIP"
    assert r1["ledger_effect"] == "none"


# --- integration: all four checks -------------------------------------------

def test_run_helen_checks_clean_packet_holds_for_operator():
    out = run_helen_checks(_full_packet())
    assert out["anti_ghost"] == "PASS"
    assert out["forbidden_path"] == "PASS"
    assert out["overall"] == "HOLD_FOR_OPERATOR"  # never self-admits


def test_run_helen_checks_ghost_packet_marked_with_findings():
    out = run_helen_checks({"capability_claims": []})
    assert out["anti_ghost"] == "GHOST"
    assert out["overall"] == "HOLD_FOR_OPERATOR_WITH_FINDINGS"
