"""The auditor must witness its own engagement: tests that the frame
audit detects presence, absence, and ghosts correctly in THIS frame."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from audit import (
    CONFIRMED_UNBUILT,
    PRESENT_UNVERIFIED,
    REGISTRY_GHOST,
    WITNESSED_HERE,
    audit,
    canon,
    render,
)


def _rows(report):
    return {r["id"]: r for r in report["rows"]}


def test_all_constitution_rows_covered():
    report = audit("test-frame")
    assert set(_rows(report)) == {f"C{i}" for i in range(1, 14)}


def test_functional_rows_witnessed_in_this_frame():
    # On the integration branch the codec and witness calculus exist and
    # their probes EXECUTE — these rows earn green here, not by grep.
    rows = _rows(audit("test-frame"))
    for cid in ("C1", "C2", "C3"):
        assert rows[cid]["status"] == WITNESSED_HERE, rows[cid]


def test_claimed_witnessed_without_artifacts_is_registry_ghost():
    rows = _rows(audit("test-frame"))
    # C4 (kappa_T binding) and C10 (tri-valued controls) are claimed
    # WITNESSED in matrix V1.2 but have no artifact on the SOT.
    assert rows["C4"]["status"] == REGISTRY_GHOST
    assert rows["C10"]["status"] == REGISTRY_GHOST
    assert "C4" in audit("test-frame")["registry_ghosts"]


def test_grep_never_earns_green():
    # Artifact-scan rows can at most be PRESENT_UNVERIFIED.
    rows = _rows(audit("test-frame"))
    for r in rows.values():
        if "artifacts matched" in r.get("evidence", ""):
            assert r["status"] == PRESENT_UNVERIFIED


def test_claimed_unbuilt_and_absent_is_agreement_not_ghost():
    rows = _rows(audit("test-frame"))
    assert rows["C11"]["status"] in (CONFIRMED_UNBUILT, PRESENT_UNVERIFIED)
    if rows["C11"]["status"] == CONFIRMED_UNBUILT:
        assert rows["C11"]["id"] not in audit("test-frame")["registry_ghosts"]


def test_verdict_reflects_ghosts():
    report = audit("test-frame")
    assert report["registry_ghosts"]
    assert report["verdict"] == "MATRIX_NOT_FULLY_WITNESSED_IN_FRAME"


def test_deterministic():
    assert canon(audit("f1")) == canon(audit("f1"))


def test_frame_id_is_input_never_sampled():
    a, b = audit("frame-A"), audit("frame-B")
    assert a["frame_id"] == "frame-A" and b["frame_id"] == "frame-B"
    ra, rb = dict(a), dict(b)
    ra.pop("frame_id"), rb.pop("frame_id")
    assert canon(ra) == canon(rb)  # only the declared frame differs


def test_render_carries_deny_footer():
    out = render(audit("test-frame"))
    assert "AUTHORITY: DENY" in out and "LEDGER_EFFECT: NONE" in out
