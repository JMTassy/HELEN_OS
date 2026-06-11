"""Test: session_writer writes SESSION_LOG_V1."""
import json
from pathlib import Path
from helen_os.boot.session_writer import write_session_log


def test_writes_session_log(tmp_path):
    session = {"session_id": "S1", "operator": "JM"}
    path = write_session_log(session, str(tmp_path))
    data = json.loads(Path(path).read_text())
    assert data["schema"] == "SESSION_LOG_V1"
    assert data["session_id"] == "S1"


def test_creates_storage_dir(tmp_path):
    d = tmp_path / "new_dir"
    write_session_log({"session_id": "X"}, str(d))
    assert d.exists()


def test_overwrites_existing(tmp_path):
    write_session_log({"session_id": "OLD"}, str(tmp_path))
    write_session_log({"session_id": "NEW"}, str(tmp_path))
    data = json.loads((tmp_path / "last_session_v1.json").read_text())
    assert data["session_id"] == "NEW"
