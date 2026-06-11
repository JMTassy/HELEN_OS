"""Test: epoch_writer writes EPOCH_STATE_V1."""
import json
from pathlib import Path
from helen_os.boot.epoch_writer import write_epoch_state


def test_writes_epoch_state(tmp_path):
    epoch = {"epoch_id": "E1", "status": "complete"}
    path = write_epoch_state(epoch, str(tmp_path))
    data = json.loads(Path(path).read_text())
    assert data["schema"] == "EPOCH_STATE_V1"
    assert data["epoch_id"] == "E1"


def test_creates_storage_dir(tmp_path):
    d = tmp_path / "epoch_store"
    write_epoch_state({"epoch_id": "E0"}, str(d))
    assert d.exists()
