"""Tests for scripts/helen_garden.py — the ASCII GARDEN renderer.

Covers the constitutional guarantees: render is pure/deterministic, health
flags fire on real conditions, and absence is rendered (never crashes).
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import helen_garden as hg  # noqa: E402


def _bed(name, file_count=0, flags=None, dense=False, children=None):
    return {
        "name": name,
        "depth": 1,
        "file_count": file_count,
        "subdir_count": 0,
        "is_dense": dense,
        "flags": sorted(flags or []),
        "children": children or [],
    }


def _state(beds, **kw):
    base = {
        "root": "helen_os/knowledge",
        "exists": True,
        "beds": beds,
        "orphans": [],
        "reading_path": False,
        "stale_corpus": None,
        "max_count": max((b["file_count"] for b in beds), default=0),
    }
    base.update(kw)
    return base


def test_render_is_deterministic():
    """Same state dict → byte-identical output, twice (pure render)."""
    state = _state([
        _bed("classified", 8, flags=["no_readme"]),
        _bed("patterns", 2, flags=["no_readme"]),
    ])
    a = hg.render_garden(state)
    b = hg.render_garden(state)
    assert a == b


def test_no_readme_flag_renders():
    state = _state([_bed("classified", 8, flags=["no_readme"])])
    out = hg.render_garden(state)
    assert "no README" in out


def test_dense_forest_summarized_not_enumerated():
    state = _state([_bed("embeddings", 27000, flags=["dense"], dense=True)])
    out = hg.render_garden(state)
    assert "dense forest" in out
    assert "27000" in out
    # one bed line, not 27k lines
    assert out.count("embeddings/") == 1


def test_missing_root_renders_absence_not_crash():
    state = _state([], exists=False, root="/nonexistent/kb")
    out = hg.render_garden(state)
    assert "no garden here" in out
    assert "/nonexistent/kb" in out


def test_reading_path_rendered_honestly_when_absent():
    state = _state([_bed("classified", 8)], reading_path=False)
    out = hg.render_garden(state)
    assert "reading-path:" in out
    assert "(none)" in out


def test_scan_missing_root_returns_exists_false(tmp_path):
    state = hg.scan_garden(str(tmp_path / "does_not_exist"))
    assert state["exists"] is False
    assert state["beds"] == []


def test_scan_flags_missing_readme(tmp_path):
    bed = tmp_path / "concepts"
    bed.mkdir()
    (bed / "a.md").write_text("seed")
    state = hg.scan_garden(str(tmp_path))
    names = {b["name"]: b for b in state["beds"]}
    assert "concepts" in names
    assert "no_readme" in names["concepts"]["flags"]
    assert names["concepts"]["file_count"] == 1


def test_scan_readme_clears_flag(tmp_path):
    bed = tmp_path / "meta"
    bed.mkdir()
    (bed / "README.md").write_text("hi")
    (bed / "x.md").write_text("seed")
    state = hg.scan_garden(str(tmp_path))
    meta = {b["name"]: b for b in state["beds"]}["meta"]
    assert "no_readme" not in meta["flags"]


def test_orphans_collected(tmp_path):
    (tmp_path / "access_log.ndjson").write_text("x")
    (tmp_path / "bed").mkdir()
    state = hg.scan_garden(str(tmp_path))
    assert "access_log.ndjson" in state["orphans"]


def test_no_color_uses_plain_tokens():
    state = _state([_bed("classified", 8, flags=["no_readme"])])
    out = hg.render_garden(state, color=False)
    assert "🌿" not in out
    assert "⚠" not in out
    assert "! no README" in out
