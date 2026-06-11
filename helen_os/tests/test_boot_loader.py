"""Test: boot_loader — loads RuntimeBootContext from storage."""
import json, pytest
from pathlib import Path
from helen_os.boot.boot_loader import load_boot_context


def test_empty_storage_dir_returns_empty_context(tmp_path):
    ctx = load_boot_context(str(tmp_path))
    assert ctx.is_empty()
    assert ctx.loaded_from == "empty"


def test_loads_person_profile(tmp_path):
    (tmp_path / "person_profile_v1.json").write_text(json.dumps({"name": "JM"}))
    ctx = load_boot_context(str(tmp_path))
    assert ctx.person_name() == "JM"
    assert ctx.loaded_from == "storage"


def test_loads_epoch_state(tmp_path):
    (tmp_path / "epoch_state_v1.json").write_text(json.dumps({"epoch_id": "E5"}))
    ctx = load_boot_context(str(tmp_path))
    assert ctx.last_epoch_id() == "E5"


def test_loads_last_session(tmp_path):
    (tmp_path / "last_session_v1.json").write_text(json.dumps({"session_id": "S99"}))
    ctx = load_boot_context(str(tmp_path))
    assert ctx.last_session == {"session_id": "S99"}


def test_corrupt_json_returns_none_for_that_field(tmp_path):
    (tmp_path / "person_profile_v1.json").write_text("NOT JSON {{{")
    ctx = load_boot_context(str(tmp_path))
    assert ctx.person_profile is None


def test_boot_time_iso_stored(tmp_path):
    ctx = load_boot_context(str(tmp_path), boot_time_iso="2026-06-11T00:00:00Z")
    assert ctx.boot_time_iso == "2026-06-11T00:00:00Z"


def test_partial_load_loaded_from_storage(tmp_path):
    (tmp_path / "companion_state_v1.json").write_text(json.dumps({"mood": "calm"}))
    ctx = load_boot_context(str(tmp_path))
    assert ctx.loaded_from == "storage"
    assert ctx.companion_state == {"mood": "calm"}
