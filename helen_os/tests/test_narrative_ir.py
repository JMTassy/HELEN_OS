"""
Timeline IR Compiler tests.

Invariant groups:
  IR1-IR6  Core invariants (authority, hash, coverage, emotion, determinism)
  ARC1-4   Arc library (shape, beat coverage, ratio sums)
  MAP1-5   map_script_to_arc()
  CMP1-4   Compilers (compile_to_montage, compile_to_shots)
  EMO1-2   Emotion overrides
"""
from __future__ import annotations

import pytest

from helen_os.render.narrative import (
    NARRATIVE_ARCS,
    TONE_ARC,
    VALID_EMOTIONS,
    TimelineIRV1,
    TimelineSegment,
    arc_from_tone,
    compile_to_montage,
    compile_to_shots,
    emotion_transition_override,
    map_script_to_arc,
)
from helen_os.render.montage import MontagePlanV1, TRANSITIONS


# ── Fixtures ───────────────────────────────────────────────────────────────────

SAMPLE_SCRIPT = (
    "There is a moment before everything changes. "
    "You don't know it yet. The silence feels ordinary. "
    "And then — suddenly — it isn't. "
    "The world turns. You see it differently now. "
    "Everything that was heavy becomes possible."
)

RECEIPT_HASH = "sha256:" + "a" * 64


def _tl(script=SAMPLE_SCRIPT, arc="three_act", dur=30.0) -> TimelineIRV1:
    return map_script_to_arc(script, arc_name=arc, total_duration=dur,
                             source_receipt_hash=RECEIPT_HASH)


# ── IR1: authority always False ────────────────────────────────────────────────

def test_timeline_authority_false():
    assert _tl().authority is False


def test_authority_true_raises():
    tl = _tl()
    with pytest.raises((ValueError, TypeError)):
        TimelineIRV1(
            type="TIMELINE_IR_V1", timeline_id="x",
            source_artifact_id="", source_receipt_hash=RECEIPT_HASH,
            arc_name="three_act", total_duration=30.0,
            segments=[], timeline_hash="sha256:" + "0" * 64,
            authority=True,
        )


# ── IR2: timeline_hash format ─────────────────────────────────────────────────

def test_timeline_hash_has_prefix():
    assert _tl().timeline_hash.startswith("sha256:")


def test_timeline_hash_64_chars_after_prefix():
    h = _tl().timeline_hash
    assert len(h) == len("sha256:") + 64


# ── IR3: segment coverage ─────────────────────────────────────────────────────

@pytest.mark.parametrize("arc", list(NARRATIVE_ARCS.keys()))
def test_segments_cover_total_duration(arc):
    tl = _tl(arc=arc, dur=30.0)
    total = sum(s.duration for s in tl.segments)
    assert abs(total - tl.total_duration) < 0.02


@pytest.mark.parametrize("arc", list(NARRATIVE_ARCS.keys()))
def test_segments_are_contiguous(arc):
    tl = _tl(arc=arc)
    for i in range(1, len(tl.segments)):
        gap = abs(tl.segments[i].start - tl.segments[i-1].end)
        assert gap < 1e-3, f"gap at segment {i}: {gap}"


def test_first_segment_starts_at_zero():
    assert _tl().segments[0].start == 0.0


def test_last_segment_ends_near_total_duration():
    tl = _tl(dur=30.0)
    assert abs(tl.segments[-1].end - tl.total_duration) < 0.02


# ── IR4: emotion validity ─────────────────────────────────────────────────────

@pytest.mark.parametrize("arc", list(NARRATIVE_ARCS.keys()))
def test_segment_emotions_are_valid(arc):
    for seg in _tl(arc=arc).segments:
        assert seg.emotion in VALID_EMOTIONS, f"invalid emotion: {seg.emotion}"


# ── IR5: determinism ──────────────────────────────────────────────────────────

def test_map_script_to_arc_is_deterministic():
    t1 = _tl()
    t2 = _tl()
    assert t1.timeline_hash == t2.timeline_hash


def test_different_arc_different_hash():
    t1 = _tl(arc="three_act")
    t2 = _tl(arc="meditation")
    assert t1.timeline_hash != t2.timeline_hash


def test_different_duration_different_hash():
    t1 = _tl(dur=30.0)
    t2 = _tl(dur=60.0)
    assert t1.timeline_hash != t2.timeline_hash


def test_different_script_different_hash():
    t1 = _tl(script="hello world")
    t2 = _tl(script="something entirely different and longer")
    assert t1.timeline_hash != t2.timeline_hash


# ── IR6: compile_to_montage authority ────────────────────────────────────────

def test_compile_to_montage_authority_false():
    plan = compile_to_montage(_tl())
    assert plan.authority is False


# ── ARC1-4: Arc library ───────────────────────────────────────────────────────

def test_all_arcs_have_beats():
    for name, beats in NARRATIVE_ARCS.items():
        assert len(beats) >= 2, f"{name} has fewer than 2 beats"


def test_arc_ratio_sums_to_one():
    for name, beats in NARRATIVE_ARCS.items():
        total = sum(b.duration_ratio for b in beats)
        assert abs(total - 1.0) < 0.01, f"{name} ratios sum to {total}"


def test_arc_transitions_are_valid():
    for name, beats in NARRATIVE_ARCS.items():
        for beat in beats:
            assert beat.transition_out in TRANSITIONS, (
                f"{name}/{beat.name}: unknown transition {beat.transition_out}"
            )


def test_arc_emotions_are_valid():
    for name, beats in NARRATIVE_ARCS.items():
        for beat in beats:
            assert beat.emotion in VALID_EMOTIONS, (
                f"{name}/{beat.name}: invalid emotion {beat.emotion}"
            )


# ── MAP1-5: map_script_to_arc ─────────────────────────────────────────────────

def test_segment_count_equals_beat_count():
    for arc, beats in NARRATIVE_ARCS.items():
        tl = _tl(arc=arc)
        assert len(tl.segments) == len(beats)


def test_beat_names_preserved_in_segments():
    tl = _tl(arc="three_act")
    arc_names = [b.name for b in NARRATIVE_ARCS["three_act"]]
    seg_names  = [s.beat_name for s in tl.segments]
    assert seg_names == arc_names


def test_text_distributed_across_segments():
    tl = _tl()
    texts = [s.text for s in tl.segments if s.text.strip()]
    assert len(texts) > 0, "no segments have text"
    # All script words appear somewhere
    all_text = " ".join(s.text for s in tl.segments)
    for word in SAMPLE_SCRIPT.split()[:5]:
        assert word in all_text


def test_clip_srcs_assigned_when_provided():
    srcs = [f"/clips/{i}.mp4" for i in range(6)]
    tl   = map_script_to_arc(SAMPLE_SCRIPT, arc_name="three_act", clip_srcs=srcs,
                              source_receipt_hash=RECEIPT_HASH)
    for i, seg in enumerate(tl.segments):
        assert seg.clip_src == srcs[i]


def test_empty_clip_srcs_gives_empty_string():
    tl = _tl()
    for seg in tl.segments:
        assert seg.clip_src == ""


# ── CMP1-4: Compilers ─────────────────────────────────────────────────────────

def test_compile_to_montage_clip_count():
    tl   = _tl(arc="three_act")
    plan = compile_to_montage(tl)
    assert len(plan.clips) == len(tl.segments)


def test_compile_to_montage_durations_match_segments():
    tl   = _tl()
    plan = compile_to_montage(tl)
    for clip, seg in zip(plan.clips, tl.segments):
        assert abs(clip.duration - seg.duration) < 1e-4


def test_compile_to_montage_transitions_match_segments():
    tl   = _tl(arc="revelation")
    plan = compile_to_montage(tl)
    for clip, seg in zip(plan.clips, tl.segments):
        assert clip.transition_out == seg.transition_out


def test_compile_to_shots_count():
    tl    = _tl(arc="meditation")
    shots = compile_to_shots(tl)
    assert len(shots) == len(tl.segments)


def test_compile_to_shots_has_required_keys():
    shots = compile_to_shots(_tl())
    required = {"shot_type", "visual_prompt", "text", "emotion",
                "camera", "duration", "text_motion", "transition_in"}
    for shot in shots:
        for k in required:
            assert k in shot, f"shot missing key: {k}"


def test_compile_to_shots_emotion_matches_segment():
    tl    = _tl(arc="testimony")
    shots = compile_to_shots(tl)
    for shot, seg in zip(shots, tl.segments):
        assert shot["emotion"] == seg.emotion


# ── EMO1-2: Emotion overrides ─────────────────────────────────────────────────

@pytest.mark.parametrize("emotion,expected", [
    ("tension",   "hard_cut"),
    ("breaking",  "zoom_through"),
    ("powerful",  "circleopen"),
    ("calm",      "fade"),
    ("warm",      "fade"),
])
def test_emotion_transition_override(emotion, expected):
    assert emotion_transition_override(emotion) == expected


def test_arc_from_tone():
    assert arc_from_tone("calm")       == "meditation"
    assert arc_from_tone("powerful")   == "manifesto"
    assert arc_from_tone("vulnerable") == "testimony"
    assert arc_from_tone("unknown")    == "three_act"


# ── to_dict ───────────────────────────────────────────────────────────────────

def test_to_dict_authority_false():
    d = _tl().to_dict()
    assert d["authority"] is False
    assert d["type"] == "TIMELINE_IR_V1"


def test_to_dict_segments_present():
    d = _tl(arc="three_act").to_dict()
    assert len(d["segments"]) == len(NARRATIVE_ARCS["three_act"])


# ── dominant_emotion / emotion_curve ─────────────────────────────────────────

def test_emotion_curve_length_equals_segments():
    tl = _tl()
    assert len(tl.emotion_curve()) == len(tl.segments)


def test_dominant_emotion_is_valid():
    assert _tl().dominant_emotion() in VALID_EMOTIONS


# ── Full pipeline: script → IR → montage → stub receipt ──────────────────────

def test_script_to_montage_pipeline():
    from helen_os.render.montage import render_montage_stub, compute_timeline

    tl   = map_script_to_arc(SAMPLE_SCRIPT, arc_name="revelation", total_duration=30.0,
                              source_receipt_hash=RECEIPT_HASH)
    plan = compile_to_montage(tl)
    tl_solved = compute_timeline(plan)
    receipt = render_montage_stub(plan, "/out/film.mp4")

    assert receipt["authority"] is False
    assert receipt["video_hash"].startswith("sha256:")
    assert receipt["timeline_hash"].startswith("sha256:")
    assert len(receipt["clips"]) == len(tl.segments)
