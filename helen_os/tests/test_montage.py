"""
MONTAGE_PLAN_V1 — Timeline Compiler v3 tests.

Invariant groups:
  M1-M10  Core authority / determinism / shape (unchanged from v2)
  T1-T8   Timeline solver
  A1-A3   Audio alignment
  E1-E3   Emotion → rhythm mapping
  R1-R4   Receipt completeness (upgraded fields)
"""
from __future__ import annotations

import pytest

from helen_os.render.montage import (
    AudioAlignment,
    AudioSpec,
    ClipSpec,
    EMOTION_RHYTHM,
    MontagePlanV1,
    RHYTHM_PRESETS,
    RHYTHMS,
    TimelineEntry,
    TRANSITIONS,
    align_audio,
    build_montage_plan,
    compute_timeline,
    render_montage_stub,
    rhythm_from_emotion,
)


# ── Fixtures ───────────────────────────────────────────────────────────────────

CLIPS_3 = ["/fake/clip_a.mp4", "/fake/clip_b.mp4", "/fake/clip_c.mp4"]
CLIPS_2 = ["/fake/a.mp4", "/fake/b.mp4"]


def _plan(clips=None, duration_target=30.0, rhythm="cinematic_breath",
          emotion="") -> MontagePlanV1:
    return build_montage_plan(
        clips or CLIPS_3,
        duration_target=duration_target,
        rhythm=rhythm,
        emotion=emotion,
    )


# ── M1-M2: authority & determinism ────────────────────────────────────────────

def test_plan_authority_false():
    assert _plan().authority is False


def test_receipt_authority_false():
    assert render_montage_stub(_plan(), "/out.mp4")["authority"] is False


def test_plan_hash_deterministic():
    assert _plan().plan_hash == _plan().plan_hash


def test_plan_hash_changes_with_clips():
    assert _plan(CLIPS_3).plan_hash != _plan(["/fake/x.mp4"]).plan_hash


def test_plan_hash_changes_with_duration():
    assert _plan(duration_target=30.0).plan_hash != _plan(duration_target=60.0).plan_hash


# ── M3: transitions follow rhythm ─────────────────────────────────────────────

@pytest.mark.parametrize("rhythm", list(RHYTHM_PRESETS.keys()))
def test_transitions_follow_rhythm(rhythm):
    plan  = build_montage_plan(CLIPS_3, rhythm=rhythm)
    cycle = RHYTHM_PRESETS[rhythm].transitions
    for i, spec in enumerate(plan.clips):
        assert spec.transition_out == cycle[i % len(cycle)]


# ── M4: duration_target preserved ─────────────────────────────────────────────

@pytest.mark.parametrize("target", [10.0, 30.0, 60.0])
def test_duration_target_preserved(target):
    assert _plan(duration_target=target).duration_target == target


# ── M5-M7: stub receipt ────────────────────────────────────────────────────────

REQUIRED_KEYS = (
    "type", "plan_id", "plan_hash", "timeline_hash", "clip_count",
    "duration", "rhythm", "output_path", "video_hash", "audio_hash",
    "clips", "rendered_at", "stub", "success", "authority",
)

def test_stub_receipt_required_keys():
    receipt = render_montage_stub(_plan(), "/out.mp4")
    for k in REQUIRED_KEYS:
        assert k in receipt, f"missing: {k}"


def test_stub_receipt_type():
    assert render_montage_stub(_plan(), "/out.mp4")["type"] == "MONTAGE_RECEIPT_V1"


def test_stub_receipt_success_and_stub_flags():
    r = render_montage_stub(_plan(), "/out.mp4")
    assert r["success"] is True
    assert r["stub"] is True


def test_stub_deterministic():
    r1 = render_montage_stub(_plan(), "/out.mp4")
    r2 = render_montage_stub(_plan(), "/out.mp4")
    assert r1["video_hash"] == r2["video_hash"]
    assert r1["timeline_hash"] == r2["timeline_hash"]


def test_stub_no_subprocess(monkeypatch):
    import subprocess as sp
    called = []
    monkeypatch.setattr(sp, "run", lambda *a, **kw: called.append(a))
    render_montage_stub(_plan(), "/out.mp4")
    assert not called


# ── M8: authority=True guard ───────────────────────────────────────────────────

def test_authority_true_raises():
    with pytest.raises(ValueError, match="authority must be False"):
        MontagePlanV1(
            plan_id="x", duration_target=30, clips=[],
            audio=AudioSpec(), rhythm="minimal", authority=True,
        )


# ── M9-M10: to_dict ───────────────────────────────────────────────────────────

def test_to_dict_authority_false():
    d = _plan().to_dict()
    assert d["authority"] is False
    assert d["type"] == "MONTAGE_PLAN_V1"


def test_to_dict_audio_nested():
    plan = build_montage_plan(CLIPS_3, voiceover="/vo.wav", music="/mus.mp3")
    d = plan.to_dict()
    assert d["audio"]["voiceover"] == "/vo.wav"
    assert d["audio"]["music"] == "/mus.mp3"


# ── T1-T8: Timeline solver ─────────────────────────────────────────────────────

def test_timeline_first_entry_starts_at_zero():
    plan = _plan()
    tl = compute_timeline(plan)
    assert tl[0].tl_start == 0.0


def test_timeline_first_entry_has_no_transition():
    plan = _plan()
    tl = compute_timeline(plan)
    assert tl[0].transition_in == "none"
    assert tl[0].trans_duration == 0.0


def test_timeline_entry_count_equals_clips():
    plan = _plan(CLIPS_3)
    assert len(compute_timeline(plan)) == 3


def test_timeline_tl_end_equals_start_plus_duration():
    plan = _plan(CLIPS_3)
    for entry in compute_timeline(plan):
        assert abs(entry.tl_end - (entry.tl_start + entry.clip_duration)) < 1e-6


def test_timeline_offsets_account_for_transition_overlap():
    """
    For 2 clips with 1s fade, clip[1].tl_start = clip[0].duration - 1.0.
    """
    clips = [
        ClipSpec(src="/a.mp4", duration=8.0, transition_out="fade"),
        ClipSpec(src="/b.mp4", duration=6.0, transition_out="fade"),
    ]
    plan = build_montage_plan(clips, duration_target=13.0)
    tl   = compute_timeline(plan)
    fade_dur = TRANSITIONS["fade"]["duration"]
    expected_start = tl[0].clip_duration - fade_dur
    assert abs(tl[1].tl_start - expected_start) < 1e-4


def test_timeline_total_duration_formula():
    """
    Total = sum(D_i) - sum(T_i for i in 0..n-2).
    """
    plan = _plan(CLIPS_3)
    tl   = compute_timeline(plan)
    total_clips = sum(e.clip_duration for e in tl)
    total_trans = sum(
        TRANSITIONS.get(plan.clips[i].transition_out, TRANSITIONS["fade"])["duration"]
        for i in range(len(plan.clips) - 1)
    )
    expected = total_clips - total_trans
    assert abs(tl[-1].tl_end - expected) < 1e-4


def test_timeline_hash_deterministic():
    plan = _plan()
    tl1  = compute_timeline(plan)
    tl2  = compute_timeline(plan)
    from helen_os.render.montage import _timeline_hash
    assert _timeline_hash(tl1) == _timeline_hash(tl2)


def test_timeline_hash_changes_with_duration():
    plan_a = build_montage_plan(CLIPS_2, duration_target=20.0)
    plan_b = build_montage_plan(CLIPS_2, duration_target=40.0)
    from helen_os.render.montage import _timeline_hash
    assert _timeline_hash(compute_timeline(plan_a)) != _timeline_hash(compute_timeline(plan_b))


# ── A1-A3: Audio alignment ────────────────────────────────────────────────────

def test_audio_align_voice_start_equals_plan_delay():
    plan    = build_montage_plan(CLIPS_3, voiceover="/vo.wav")
    tl      = compute_timeline(plan)
    align   = align_audio(plan, tl)
    assert align.voice_start == plan.audio.voiceover_delay


def test_audio_align_music_fade_out_near_end():
    plan  = _plan(duration_target=30.0)
    tl    = compute_timeline(plan)
    align = align_audio(plan, tl)
    assert abs(align.music_fade_out - (align.total_duration - 2.0)) < 0.01


def test_audio_align_total_duration_matches_timeline():
    plan  = _plan(CLIPS_3)
    tl    = compute_timeline(plan)
    align = align_audio(plan, tl)
    assert abs(align.total_duration - tl[-1].tl_end) < 1e-3


# ── E1-E3: Emotion → rhythm ───────────────────────────────────────────────────

@pytest.mark.parametrize("emotion,expected", [
    ("tension",   "fast_cuts"),
    ("breaking",  "dramatic"),
    ("calm",      "cinematic_breath"),
    ("intimate",  "minimal"),
    ("warm",      "cinematic_breath"),
    ("ascending", "cinematic_breath"),
])
def test_emotion_to_rhythm_mapping(emotion, expected):
    assert rhythm_from_emotion(emotion) == expected


def test_unknown_emotion_defaults_to_cinematic_breath():
    assert rhythm_from_emotion("nonexistent") == "cinematic_breath"


def test_emotion_overrides_rhythm_in_build():
    plan = build_montage_plan(CLIPS_3, emotion="tension", rhythm="cinematic_breath")
    assert plan.rhythm == "fast_cuts"


# ── R1-R4: Receipt fields ─────────────────────────────────────────────────────

def test_receipt_timeline_hash_has_prefix():
    r = render_montage_stub(_plan(), "/out.mp4")
    assert r["timeline_hash"].startswith("sha256:")


def test_receipt_video_hash_has_prefix():
    r = render_montage_stub(_plan(), "/out.mp4")
    assert r["video_hash"].startswith("sha256:")


def test_receipt_clips_list_length():
    plan = _plan(CLIPS_3)
    r    = render_montage_stub(plan, "/out.mp4")
    assert len(r["clips"]) == 3


def test_receipt_clips_have_tl_fields():
    r = render_montage_stub(_plan(CLIPS_3), "/out.mp4")
    for clip in r["clips"]:
        assert "tl_start" in clip
        assert "tl_end"   in clip
        assert clip["tl_start"] >= 0.0
        assert clip["tl_end"]   > clip["tl_start"]


# ── Integration ───────────────────────────────────────────────────────────────

def test_build_and_stub_roundtrip():
    plan = build_montage_plan(
        CLIPS_3,
        duration_target=30.0,
        voiceover="/fake/vo.wav",
        music="/fake/mus.mp3",
        rhythm="dramatic",
        labels=["opening", "mid", "close"],
    )
    r = render_montage_stub(plan, "/out.mp4")
    assert r["authority"]       is False
    assert r["plan_id"]         == plan.plan_id
    assert r["plan_hash"]       == plan.plan_hash
    assert r["clip_count"]      == 3
    assert r["duration"]        > 0
    assert r["rhythm"]          == "dramatic"
    assert r["video_hash"].startswith("sha256:")
    assert r["timeline_hash"].startswith("sha256:")


def test_single_clip_plan():
    plan = build_montage_plan(["/only.mp4"], duration_target=10.0)
    tl   = compute_timeline(plan)
    assert len(tl) == 1
    assert tl[0].tl_start == 0.0
    r = render_montage_stub(plan, "/out.mp4")
    assert r["success"] is True


def test_clipspec_transition_preserved_in_plan():
    specs = [
        ClipSpec(src="/a.mp4", duration=5.0, transition_out="circleopen"),
        ClipSpec(src="/b.mp4", duration=8.0, transition_out="dissolve"),
    ]
    plan = build_montage_plan(specs, duration_target=13.0)
    assert plan.clips[0].transition_out == "circleopen"
    assert plan.clips[1].transition_out == "dissolve"


def test_duration_pattern_scales_to_target():
    plan = build_montage_plan(CLIPS_3, duration_target=30.0, rhythm="cinematic_breath")
    tl   = compute_timeline(plan)
    # total duration should be close to 30s (within transition rounding)
    assert abs(tl[-1].tl_end - 30.0) < 2.0


def test_all_rhythm_presets_produce_valid_plans():
    for rhythm in RHYTHM_PRESETS:
        plan = build_montage_plan(CLIPS_3, rhythm=rhythm)
        assert plan.authority is False
        tl = compute_timeline(plan)
        assert len(tl) == 3
        assert tl[0].tl_start == 0.0


def test_rhythms_compat_alias():
    """RHYTHMS backward-compat alias returns transition lists."""
    for k, v in RHYTHMS.items():
        assert isinstance(v, list)
        assert all(isinstance(t, str) for t in v)
        assert all(t in TRANSITIONS for t in v)
