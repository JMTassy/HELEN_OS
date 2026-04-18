"""
Tests for helen_os.render — three mandatory invariants.

R1: no render without governed source (receipt_hash required)
R2: no authority from rendering (authority=False always)
R4: same artifact + profile => byte-stable compiled spec
R5: render receipt always bound to source receipt hash
"""
import pytest

from helen_os.render.models import ExecutionArtifactV1, RenderReceiptV1
from helen_os.render.contracts import canonical_json, sha256_hex
from helen_os.render.video import (
    VideoRenderProfileV1, compile_video_spec, PROFILE_MEDITATION,
)
from helen_os.render.pipeline import run_video_render


# ── Fixtures ──────────────────────────────────────────────────────────────────

RECEIPT_HASH = "sha256:" + "a" * 64


def _artifact(**kwargs) -> ExecutionArtifactV1:
    defaults = dict(
        artifact_id="art_001",
        run_id="run_001",
        receipt_hash=RECEIPT_HASH,
        content="We closed the seam. No receipt, no claim.",
    )
    defaults.update(kwargs)
    return ExecutionArtifactV1(**defaults)


def _profile() -> VideoRenderProfileV1:
    return PROFILE_MEDITATION


# ── Test 1: same artifact + profile => same compiled spec (R4) ────────────────

def test_compile_spec_is_deterministic():
    artifact = _artifact()
    profile  = _profile()

    spec_a = compile_video_spec(artifact, profile)
    spec_b = compile_video_spec(artifact, profile)

    assert canonical_json(spec_a) == canonical_json(spec_b), (
        "R4 violated: same artifact + profile must produce byte-stable spec"
    )


def test_compile_spec_changes_with_different_content():
    a1 = _artifact(content="text one")
    a2 = _artifact(content="text two")
    profile = _profile()

    assert canonical_json(compile_video_spec(a1, profile)) != \
           canonical_json(compile_video_spec(a2, profile))


# ── Test 2: render receipt authority=False always (R2) ────────────────────────

def test_render_receipt_authority_is_always_false():
    artifact = _artifact()
    media, receipt = run_video_render(
        artifact, _profile(), previous_hash="sha256:" + "0" * 64, renderer_name="stub"
    )

    assert receipt.authority is False, "R2 violated: receipt.authority must be False"
    assert media.source_artifact_id == artifact.artifact_id


def test_render_receipt_authority_cannot_be_set_true():
    with pytest.raises(ValueError, match="authority"):
        RenderReceiptV1(
            type="RENDER_RECEIPT_V1",
            run_id="r", source_artifact_id="a", source_receipt_hash=RECEIPT_HASH,
            render_kind="video", renderer="stub",
            input_hash="sha256:" + "b" * 64,
            output_hash="sha256:" + "c" * 64,
            previous_hash="sha256:" + "0" * 64,
            receipt_hash="sha256:" + "d" * 64,
            authority=True,
        )


# ── Test 3: render receipt bound to source receipt hash (R5) ─────────────────

def test_render_receipt_bound_to_source_receipt_hash():
    artifact = _artifact()
    _, receipt = run_video_render(
        artifact, _profile(), previous_hash="sha256:" + "0" * 64, renderer_name="stub"
    )

    assert receipt.source_receipt_hash == artifact.receipt_hash, (
        "R5 violated: receipt must carry source receipt hash"
    )
    assert receipt.source_artifact_id == artifact.artifact_id


def test_different_artifacts_produce_different_receipts():
    a1 = _artifact(artifact_id="art_001", content="first")
    a2 = _artifact(artifact_id="art_002", content="second")
    prev = "sha256:" + "0" * 64

    _, r1 = run_video_render(a1, _profile(), previous_hash=prev, renderer_name="stub")
    _, r2 = run_video_render(a2, _profile(), previous_hash=prev, renderer_name="stub")

    assert r1.receipt_hash != r2.receipt_hash
    assert r1.output_hash  != r2.output_hash


# ── Test 4: governed source required (R1) ────────────────────────────────────

def test_execution_artifact_requires_receipt_hash_prefix():
    with pytest.raises(ValueError, match="sha256:"):
        ExecutionArtifactV1(
            artifact_id="art_x",
            run_id="run_x",
            receipt_hash="not-a-hash",
            content="test",
        )


def test_execution_artifact_valid_with_correct_prefix():
    a = _artifact()
    assert a.receipt_hash.startswith("sha256:")
