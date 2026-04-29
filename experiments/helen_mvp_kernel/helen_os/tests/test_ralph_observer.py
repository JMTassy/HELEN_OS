"""Ralph observer — tails sidecar, yields iteration records."""
import json
from pathlib import Path

from helen_os.runtime.ralph_observer import current_ralph_state, tail_ralph


def _write_record(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as f:
        f.write(json.dumps(record) + "\n")


def test_current_ralph_state_empty(tmp_path):
    state = current_ralph_state(tmp_path / "missing.ndjson")
    assert state["iteration_count"] == 0
    assert state["complete"] is False
    assert state["last_iteration"] is None


def test_current_ralph_state_with_records(tmp_path):
    sidecar = tmp_path / "ralph.ndjson"
    _write_record(sidecar, {"ts": "t1", "model": "helen-core",
                             "prompt_hash": "a", "output_hash": "b",
                             "promise_found": False, "promise_token": "COMPLETE"})
    _write_record(sidecar, {"ts": "t2", "model": "helen-core",
                             "prompt_hash": "a", "output_hash": "c",
                             "promise_found": True, "promise_token": "COMPLETE"})
    state = current_ralph_state(sidecar)
    assert state["iteration_count"] == 2
    assert state["complete"] is True
    assert state["last_promise_found"] is True
    assert state["last_model"] == "helen-core"


def test_tail_ralph_yields_existing_records(tmp_path):
    sidecar = tmp_path / "ralph.ndjson"
    _write_record(sidecar, {"promise_found": False, "model": "m", "ts": "t",
                             "prompt_hash": "ph", "output_hash": "oh",
                             "promise_token": "DONE"})
    _write_record(sidecar, {"promise_found": True, "model": "m", "ts": "t2",
                             "prompt_hash": "ph", "output_hash": "oh2",
                             "promise_token": "DONE"})
    gen = tail_ralph(sidecar, poll_interval=0.0)
    r0 = next(gen)
    r1 = next(gen)
    assert r0["iteration_index"] == 0
    assert r0["promise_found"] is False
    assert r1["iteration_index"] == 1
    assert r1["promise_found"] is True


def test_tail_ralph_yields_new_records(tmp_path):
    sidecar = tmp_path / "ralph.ndjson"
    _write_record(sidecar, {"promise_found": False, "model": "m", "ts": "t",
                             "prompt_hash": "p", "output_hash": "o",
                             "promise_token": "X"})
    gen = tail_ralph(sidecar, poll_interval=0.0)
    r0 = next(gen)
    assert r0["iteration_index"] == 0

    _write_record(sidecar, {"promise_found": True, "model": "m", "ts": "t2",
                             "prompt_hash": "p", "output_hash": "o2",
                             "promise_token": "X"})
    r1 = next(gen)
    assert r1["iteration_index"] == 1
    assert r1["promise_found"] is True


def test_complete_flag_set_by_any_iteration(tmp_path):
    sidecar = tmp_path / "ralph.ndjson"
    _write_record(sidecar, {"promise_found": True, "model": "m", "ts": "t",
                             "prompt_hash": "p", "output_hash": "o",
                             "promise_token": "DONE"})
    _write_record(sidecar, {"promise_found": False, "model": "m", "ts": "t2",
                             "prompt_hash": "p", "output_hash": "o2",
                             "promise_token": "DONE"})
    state = current_ralph_state(sidecar)
    assert state["complete"] is True  # any promise_found=True suffices
