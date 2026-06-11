"""Test: full boot sequence — write → load → render."""
import json
from pathlib import Path
from helen_os.boot.session_writer import write_session_log
from helen_os.boot.epoch_writer import write_epoch_state
from helen_os.boot.boot_loader import load_boot_context
from helen_os.boot.greeting_renderer import render_greeting


def test_full_boot_sequence(tmp_path):
    # Write context
    (tmp_path / "person_profile_v1.json").write_text(json.dumps({"name": "JM"}))
    write_session_log({"session_id": "S10"}, str(tmp_path))
    write_epoch_state({"epoch_id": "E5", "status": "complete"}, str(tmp_path))

    # Load
    ctx = load_boot_context(str(tmp_path), boot_time_iso="2026-06-11T00:00:00Z")
    assert ctx.loaded_from == "storage"
    assert ctx.person_name() == "JM"
    assert ctx.last_epoch_id() == "E5"

    # Render
    greeting = render_greeting(ctx)
    assert "JM" in greeting
    assert "E5" in greeting
    assert "storage" in greeting


def test_boot_without_context_gives_honest_greeting(tmp_path):
    ctx = load_boot_context(str(tmp_path))
    greeting = render_greeting(ctx)
    # Must not claim to know anything
    assert "JM" not in greeting
    assert "E" not in greeting or "empty" in greeting or "No prior" in greeting


def test_partial_context_no_crash(tmp_path):
    write_epoch_state({"epoch_id": "E1"}, str(tmp_path))
    ctx = load_boot_context(str(tmp_path))
    greeting = render_greeting(ctx)
    assert isinstance(greeting, str)
    assert "E1" in greeting


def test_boot_context_to_dict_round_trip(tmp_path):
    (tmp_path / "person_profile_v1.json").write_text(json.dumps({"name": "X"}))
    ctx = load_boot_context(str(tmp_path))
    d = ctx.to_dict()
    assert d["schema"] == "RUNTIME_BOOT_CONTEXT_V1"
    assert d["person_profile"]["name"] == "X"
