"""
Tests for REFERENCE_DRIFT_WITNESS_V1.

NON_SOVEREIGN — no ledger writes, no sovereign path access.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from oracle_town.skills.reference_drift_witness.skill import (
    ReferenceDriftWitness,
    ReferenceDriftReport,
    ArtifactStatus,
    REPORT_SCHEMA,
)


# ── Helpers ────────────────────────────────────────────────────────────────────

def sha(content: bytes) -> str:
    return "sha256:" + hashlib.sha256(content).hexdigest()


# ── Fixtures ───────────────────────────────────────────────────────────────────

@pytest.fixture()
def tree(tmp_path):
    """Minimal artifact tree under tmp_path."""
    a = tmp_path / "EPOCH_RECEIPT_E51.json"
    b = tmp_path / "EPOCH_RECEIPT_E52.json"
    c = tmp_path / "EPOCH_RECEIPT_E55.json"
    a.write_bytes(b'{"epoch": "E51"}')
    b.write_bytes(b'{"epoch": "E52"}')
    c.write_bytes(b'{"epoch": "E55"}')
    return tmp_path, a, b, c


# ── Schema / output invariants ─────────────────────────────────────────────────

def test_report_schema_constant():
    assert REPORT_SCHEMA == "REFERENCE_DRIFT_REPORT_V1"


def test_report_authority_never_sovereign(tree):
    root, a, b, c = tree
    witness = ReferenceDriftWitness(sot_root=root)
    report = witness.scan([{"path": a.name, "expected_sha": None}])
    assert report.authority == "NONE"
    assert report.world_effect == "NONE"
    assert report.sovereign_touch is False


def test_report_to_dict_has_schema(tree):
    root, a, *_ = tree
    witness = ReferenceDriftWitness(sot_root=root)
    report = witness.scan([{"path": a.name, "expected_sha": None}])
    d = report.to_dict()
    assert d["schema"] == REPORT_SCHEMA
    assert "artifacts" in d
    assert "scanned_at" in d


# ── Clean path ─────────────────────────────────────────────────────────────────

def test_clean_when_sha_matches(tree):
    root, a, *_ = tree
    expected = sha(a.read_bytes())
    witness = ReferenceDriftWitness(sot_root=root)
    report = witness.scan([{"path": a.name, "expected_sha": expected}])
    assert report.clean
    assert report.drift_count == 0
    assert report.missing_count == 0
    assert report.stale_count == 0


def test_clean_when_no_expected_sha(tree):
    root, a, b, c = tree
    witness = ReferenceDriftWitness(sot_root=root)
    report = witness.scan([
        {"path": a.name, "expected_sha": None},
        {"path": b.name, "expected_sha": None},
    ])
    assert report.clean
    assert report.total_artifacts == 2


# ── Drift detection ────────────────────────────────────────────────────────────

def test_drift_detected_when_sha_changed(tree):
    root, a, *_ = tree
    stale_sha = "sha256:" + "0" * 64
    witness = ReferenceDriftWitness(sot_root=root)
    report = witness.scan([{"path": a.name, "expected_sha": stale_sha}])
    assert report.drift_count == 1
    assert not report.clean
    art = report.artifacts[0]
    assert art.drift is True
    assert art.missing is False


def test_no_drift_when_expected_sha_absent(tree):
    root, a, *_ = tree
    a.write_bytes(b"changed content")
    witness = ReferenceDriftWitness(sot_root=root)
    report = witness.scan([{"path": a.name, "expected_sha": None}])
    assert report.drift_count == 0


# ── Missing detection ──────────────────────────────────────────────────────────

def test_missing_when_file_absent(tree):
    root, *_ = tree
    witness = ReferenceDriftWitness(sot_root=root)
    report = witness.scan([{"path": "EPOCH_RECEIPT_E99.json", "expected_sha": "sha256:abc"}])
    assert report.missing_count == 1
    assert not report.clean
    art = report.artifacts[0]
    assert art.missing is True
    assert art.present is False
    assert art.actual_sha is None


def test_no_missing_flag_when_no_expected_sha(tree):
    root, *_ = tree
    witness = ReferenceDriftWitness(sot_root=root)
    report = witness.scan([{"path": "EPOCH_RECEIPT_E99.json", "expected_sha": None}])
    assert report.missing_count == 0


# ── Staleness detection ────────────────────────────────────────────────────────

def test_stale_when_epoch_lag_exceeds_threshold(tree):
    root, a, *_ = tree
    # a is EPOCH_RECEIPT_E51.json; current_epoch=65, threshold=10 → lag=14 > 10
    witness = ReferenceDriftWitness(sot_root=root, current_epoch=65, staleness_epochs=10)
    report = witness.scan([{"path": a.name, "expected_sha": None}])
    assert report.stale_count == 1
    art = report.artifacts[0]
    assert art.stale is True
    assert art.stale_reason is not None


def test_not_stale_within_threshold(tree):
    root, a, *_ = tree
    # a is EPOCH_RECEIPT_E51.json; current_epoch=55, threshold=10 → lag=4 <= 10
    witness = ReferenceDriftWitness(sot_root=root, current_epoch=55, staleness_epochs=10)
    report = witness.scan([{"path": a.name, "expected_sha": None}])
    assert report.stale_count == 0


def test_no_stale_on_non_epoch_filename(tmp_path):
    f = tmp_path / "REDUCER_SUBMISSION_PACKET_V1.json"
    f.write_bytes(b"{}")
    witness = ReferenceDriftWitness(sot_root=tmp_path, current_epoch=100, staleness_epochs=1)
    report = witness.scan([{"path": f.name, "expected_sha": None}])
    assert report.stale_count == 0


# ── Directory scan ─────────────────────────────────────────────────────────────

def test_scan_directory_finds_all_matching(tree):
    root, a, b, c = tree
    witness = ReferenceDriftWitness(sot_root=root)
    report = witness.scan_directory(directory=root, pattern="EPOCH_RECEIPT_E*.json")
    assert report.total_artifacts == 3
    assert report.manifest_source == "directory_scan"


def test_scan_directory_uses_expected_shas(tree):
    root, a, b, c = tree
    stale_sha = "sha256:" + "f" * 64
    expected = {a.name: stale_sha}
    witness = ReferenceDriftWitness(sot_root=root)
    report = witness.scan_directory(
        directory=root,
        pattern="EPOCH_RECEIPT_E*.json",
        expected_shas=expected,
    )
    drifted = [art for art in report.artifacts if art.drift]
    assert len(drifted) == 1
    assert drifted[0].path == a.name


# ── Snapshot ────────────────────────────────────────────────────────────────────

def test_snapshot_records_current_shas(tree):
    root, a, b, c = tree
    witness = ReferenceDriftWitness(sot_root=root)
    manifest = [{"path": x.name, "expected_sha": None} for x in (a, b, c)]
    snap = witness.snapshot(manifest)
    assert len(snap) == 3
    for entry in snap:
        p = root / entry["path"]
        assert entry["sha"] == sha(p.read_bytes())


def test_snapshot_skips_missing(tree):
    root, a, *_ = tree
    witness = ReferenceDriftWitness(sot_root=root)
    manifest = [
        {"path": a.name, "expected_sha": None},
        {"path": "DOES_NOT_EXIST.json", "expected_sha": None},
    ]
    snap = witness.snapshot(manifest)
    assert len(snap) == 1
    assert snap[0]["path"] == a.name


def test_snapshot_then_scan_is_clean(tree):
    root, a, b, c = tree
    witness = ReferenceDriftWitness(sot_root=root)
    manifest = [{"path": x.name, "expected_sha": None} for x in (a, b, c)]
    snap = witness.snapshot(manifest)
    manifest_with_shas = [{"path": e["path"], "expected_sha": e["sha"]} for e in snap]
    report = witness.scan(manifest_with_shas)
    assert report.clean


def test_snapshot_then_mutate_then_scan_drifts(tree):
    root, a, b, c = tree
    witness = ReferenceDriftWitness(sot_root=root)
    manifest = [{"path": x.name, "expected_sha": None} for x in (a, b, c)]
    snap = witness.snapshot(manifest)
    a.write_bytes(b"mutated content")
    manifest_with_shas = [{"path": e["path"], "expected_sha": e["sha"]} for e in snap]
    report = witness.scan(manifest_with_shas)
    assert report.drift_count == 1
    assert not report.clean


# ── Report counts ──────────────────────────────────────────────────────────────

def test_counts_aggregate_correctly(tree):
    root, a, b, c = tree
    stale_sha = "sha256:" + "0" * 64
    witness = ReferenceDriftWitness(sot_root=root, current_epoch=65, staleness_epochs=10)
    manifest = [
        {"path": a.name, "expected_sha": stale_sha},   # drift + stale
        {"path": b.name, "expected_sha": None},          # stale only (E52, lag=13)
        {"path": "MISSING.json", "expected_sha": "sha256:" + "1" * 64},  # missing
    ]
    report = witness.scan(manifest)
    assert report.drift_count == 1
    assert report.missing_count == 1
    assert report.stale_count == 2
    assert report.total_artifacts == 3
