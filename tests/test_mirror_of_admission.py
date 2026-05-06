"""
test_mirror_of_admission.py — NON_SOVEREIGN · NO_CLAIM
Tests for MIRROR_OF_ADMISSION_V1 schema, fixture, and stub generator.
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixtures" / "mirror_of_admission" / "example_akashic_video.json"
sys.path.insert(0, str(ROOT))
from tools.validate_mirror_of_admission import validate_mirror

FRACTURE_TYPES = {
    "DREAM_OVERREACH",
    "BUILD_BLOCKED",
    "LAW_MISSING",
    "TOOL_MISSING",
    "RECEIPT_MISSING",
}


def test_fixture_validates():
    errors = validate_mirror(FIXTURE)
    assert errors == [], f"Fixture validation errors: {errors}"


def test_fixture_has_exactly_one_next_move():
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    action = payload["next_move"]["one_action"]
    assert isinstance(action, str)
    assert "\n" not in action, "one_action must be a single line"
    assert action.strip(), "one_action must not be empty"


def test_fixture_is_non_sovereign():
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    assert payload["authority"] == "NON_SOVEREIGN"
    assert payload["canon"] == "NO_SHIP"
    assert payload["status"] == "NO_CLAIM"
    assert payload["dream_world"]["authority"] == "NON_SOVEREIGN"


def test_fixture_has_one_fracture_type():
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    assert payload["fracture"]["type"] in FRACTURE_TYPES


def test_fixture_law_consistency():
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    lw = payload["law_world"]
    if lw["admissible"] is True:
        assert lw["missing_receipts"] == [], (
            "admissible=true requires missing_receipts to be empty"
        )


def test_stub_generates_valid_artifact():
    cmd = [
        sys.executable,
        str(ROOT / "tools" / "mirror_of_admission_stub.py"),
        "Make HELEN send one video to Telegram",
        "telegram",
        "higgsfield",
    ]
    result = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, check=True)
    generated = ROOT / result.stdout.strip()
    errors = validate_mirror(generated)
    assert errors == [], f"Generated stub errors: {errors}"
    payload = json.loads(generated.read_text(encoding="utf-8"))
    assert payload["fracture"]["type"] == "BUILD_BLOCKED"


def test_stub_dream_overreach_detection():
    cmd = [
        sys.executable,
        str(ROOT / "tools" / "mirror_of_admission_stub.py"),
        "Make HELEN a divine sacred Akashic oracle of consciousness",
    ]
    result = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, check=True)
    generated = ROOT / result.stdout.strip()
    payload = json.loads(generated.read_text(encoding="utf-8"))
    assert payload["fracture"]["type"] == "DREAM_OVERREACH"


def test_stub_law_missing_detection():
    cmd = [
        sys.executable,
        str(ROOT / "tools" / "mirror_of_admission_stub.py"),
        "Mutate the ledger and bypass mayor governance",
    ]
    result = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, check=True)
    generated = ROOT / result.stdout.strip()
    payload = json.loads(generated.read_text(encoding="utf-8"))
    assert payload["fracture"]["type"] == "LAW_MISSING"


def test_stub_tool_missing_detection():
    cmd = [
        sys.executable,
        str(ROOT / "tools" / "mirror_of_admission_stub.py"),
        "Send a video to Telegram",
        "git",
    ]
    result = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, check=True)
    generated = ROOT / result.stdout.strip()
    payload = json.loads(generated.read_text(encoding="utf-8"))
    assert payload["fracture"]["type"] == "TOOL_MISSING"
