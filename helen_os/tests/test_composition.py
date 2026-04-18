"""
Tests for HELEN HTML_COMPOSITION_V1.

C1: same plan + artifact → same HTML (deterministic)
C2: authority=False always
C3: composition_hash = sha256(html + canonical(assets))
C4: full provenance chain (plan_hash + source_receipt_hash)
C5: all 4 styles produce valid compositions
C6: HTML contains required shot structure
C7: run_hyperframes_render (stub mode) returns all 4 objects
C8: different plans → different compositions
"""
import dataclasses

import pytest

from helen_os.render.models import ExecutionArtifactV1
from helen_os.render.director import direct
from helen_os.render.composition import HTMLCompositionV1, director_to_html
from helen_os.render.contracts import canonical_json, sha256_hex
from helen_os.render.pipeline import run_hyperframes_render

RECEIPT_HASH = "sha256:" + "a" * 64
PREV_HASH    = "sha256:" + "0" * 64


def _artifact(**kw) -> ExecutionArtifactV1:
    defaults = dict(
        artifact_id="art_001", run_id="run_001",
        receipt_hash=RECEIPT_HASH,
        content="We closed the seam.",
        tone="calm", persona="helen",
    )
    defaults.update(kw)
    return ExecutionArtifactV1(**defaults)


def _comp(style="meditation", **kw) -> HTMLCompositionV1:
    a    = _artifact(**kw)
    plan = direct(a, style)
    return director_to_html(plan, a)


# ── C1: determinism ────────────────────────────────────────────────────────────

def test_composition_is_deterministic():
    a    = _artifact()
    plan = direct(a, "meditation")
    c1   = director_to_html(plan, a)
    c2   = director_to_html(plan, a)
    assert c1.html              == c2.html
    assert c1.composition_hash  == c2.composition_hash
    assert c1.composition_id    == c2.composition_id


def test_composition_deterministic_across_styles():
    for style in ("meditation", "oracle", "witness", "declaration"):
        a    = _artifact()
        plan = direct(a, style)
        c1   = director_to_html(plan, a)
        c2   = director_to_html(plan, a)
        assert c1.composition_hash == c2.composition_hash, f"{style}: not deterministic"


# ── C2: authority ─────────────────────────────────────────────────────────────

def test_composition_authority_is_false():
    c = _comp()
    assert c.authority is False


def test_composition_authority_cannot_be_true():
    c = _comp()
    with pytest.raises((ValueError, TypeError)):
        HTMLCompositionV1(**{**dataclasses.asdict(c), "authority": True})


# ── C3: composition_hash integrity ────────────────────────────────────────────

def test_composition_hash_is_sha256_prefixed():
    c = _comp()
    assert c.composition_hash.startswith("sha256:")


def test_composition_hash_changes_with_content():
    c1 = _comp(content="first phrase")
    c2 = _comp(content="second phrase")
    assert c1.composition_hash != c2.composition_hash


# ── C4: provenance chain ───────────────────────────────────────────────────────

def test_composition_carries_plan_hash():
    a    = _artifact()
    plan = direct(a, "oracle")
    c    = director_to_html(plan, a)
    assert c.plan_hash           == plan.plan_hash
    assert c.plan_id             == plan.plan_id
    assert c.source_receipt_hash == a.receipt_hash
    assert c.source_artifact_id  == a.artifact_id


def test_composition_html_embeds_provenance():
    c = _comp()
    assert c.source_receipt_hash in c.html
    assert c.plan_id             in c.html
    assert "authority:           false" in c.html.lower()


# ── C5: all styles ────────────────────────────────────────────────────────────

@pytest.mark.parametrize("style", ["meditation", "oracle", "witness", "declaration"])
def test_all_styles_produce_valid_composition(style):
    c = _comp(style=style)
    assert c.type     == "HTML_COMPOSITION_V1"
    assert c.duration > 0
    assert len(c.html) > 500
    assert len(c.assets) >= 1
    assert c.width  == 1920
    assert c.height == 1080
    assert c.fps    == 30


# ── C6: HTML structure ────────────────────────────────────────────────────────

def test_html_contains_shot_divs():
    a    = _artifact()
    plan = direct(a, "meditation")
    c    = director_to_html(plan, a)
    # Should have one div per shot
    shot_count = len(plan.shots)
    assert c.html.count('class="shot ') == shot_count


def test_html_contains_gsap_timeline():
    c = _comp()
    assert "gsap.timeline" in c.html
    assert "data-start"    in c.html
    assert "data-duration" in c.html


def test_html_contains_helen_visual_dna():
    c = _comp()
    assert "#050a1a" in c.html   # deep blue background
    assert "#d4a843" in c.html   # amber/gold accent
    assert "Cormorant Garamond" in c.html


def test_html_contains_voice_directive():
    c = _comp()
    assert "VOICE DIRECTIVE" in c.html


# ── C7: full pipeline (stub) ───────────────────────────────────────────────────

def test_hyperframes_pipeline_returns_four_objects():
    media, receipt, plan, comp = run_hyperframes_render(
        _artifact(), PREV_HASH,
        director_style="meditation", mode="stub",
    )
    # MediaArtifactV1 has no authority field; the chain is governed via receipt
    assert receipt.authority is False
    assert plan.authority    is False
    assert comp.authority    is False
    assert media.content_hash.startswith("sha256:")


def test_hyperframes_pipeline_provenance_chain():
    a = _artifact()
    media, receipt, plan, comp = run_hyperframes_render(
        a, PREV_HASH, director_style="oracle", mode="stub",
    )
    assert plan.source_receipt_hash  == a.receipt_hash
    assert comp.source_receipt_hash  == a.receipt_hash
    assert receipt.source_receipt_hash == a.receipt_hash
    assert comp.plan_hash            == plan.plan_hash


def test_hyperframes_pipeline_style_propagates():
    media, receipt, plan, comp = run_hyperframes_render(
        _artifact(), PREV_HASH, director_style="witness", mode="stub",
    )
    assert plan.style == "witness"
    assert "data-start" in comp.html


# ── C8: uniqueness ────────────────────────────────────────────────────────────

def test_different_artifacts_produce_different_compositions():
    a1 = _artifact(artifact_id="art_001", content="first")
    a2 = _artifact(artifact_id="art_002", content="second")
    p1 = direct(a1, "meditation"); c1 = director_to_html(p1, a1)
    p2 = direct(a2, "meditation"); c2 = director_to_html(p2, a2)
    assert c1.composition_hash != c2.composition_hash
    assert c1.composition_id   != c2.composition_id
