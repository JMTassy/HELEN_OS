"""
tests/test_helen_object_cli.py — CLI smoke tests for helen_object.py
Run: .venv/bin/pytest tests/test_helen_object_cli.py -v
"""
import json, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from click.testing import CliRunner
from tools.helen_object import cli


def _run(*args):
    result = CliRunner().invoke(cli, ["create"] + list(args))
    return result


def _json(*args):
    r = _run(*args)
    assert r.exit_code == 0, r.output
    return json.loads(r.output)


def test_basic_create_is_admissible():
    d = _json("--source", "src_001", "--claim", "test claim")
    assert d["status"] == "ADMISSIBLE"

def test_authority_always_false():
    d = _json("--source", "src_001", "--claim", "test claim")
    assert d["authority"] is False

def test_type_is_receipt_v0():
    d = _json("--source", "src_001", "--claim", "test claim")
    assert d["type"] == "SOURCEBOUND_OBJECT_RECEIPT_V0"

def test_source_ref_preserved():
    d = _json("--source", "src_muse_spark", "--claim", "claim")
    assert d["source_ref"] == "src_muse_spark"

def test_claim_preserved():
    d = _json("--source", "src_001", "--claim", "my claim here")
    assert "my claim here" in d["claims"]

def test_multiple_claims():
    d = _json("--source", "src_001", "--claim", "c1", "--claim", "c2")
    assert "c1" in d["claims"]
    assert "c2" in d["claims"]

def test_explicit_evidence():
    d = _json("--source", "src_001", "--claim", "c", "--evidence", "ev_manual_001")
    assert "ev_manual_001" in d["evidence_refs"]

def test_risk_flag_preserved():
    d = _json("--source", "src_001", "--claim", "c", "--risk", "low_confidence")
    assert "low_confidence" in d["risk_flags"]

def test_hash_present_and_64_chars():
    d = _json("--source", "src_001", "--claim", "c")
    assert len(d["hash"]) == 64

def test_fail_validator_exits_nonzero():
    r = _run("--source", "src_001", "--claim", "c", "--validator", "FAIL")
    assert r.exit_code != 0
    d = json.loads(r.output)
    assert d["status"] == "REJECTED"
    assert d["authority"] is False

def test_receipt_and_replay_auto_generated():
    d = _json("--source", "src_001", "--claim", "c")
    assert d["receipt_ref"].startswith("rcpt_")
    assert d["replay_path"].startswith("replay/sourcebound/")
