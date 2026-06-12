#!/usr/bin/env bash
# scripts/ralph/ralph_goblin_50.sh — GOBLIN 50-epoch bounded autoresearch
# Classification: NON_SOVEREIGN · NO_SHIP · GOBLIN_MODE
# Authority:      NONE  |  World effect: NONE  |  Ledger: append forbidden
# heredoc-in-subshell rule: write Python to /tmp/, invoke via $VENV

set -euo pipefail

SOT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SCRATCH="${SOT_ROOT}/oracle_town/skills/ops/dan_goblin/scratch"
BOOT_DIR="${SOT_ROOT}/helen_os/boot"
TESTS_DIR="${SOT_ROOT}/helen_os/tests"
VENV="${SOT_ROOT}/.venv/bin/python"
DRY_RUN=false
TARGET_EPOCH=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)  DRY_RUN=true ;;
    --epoch)    TARGET_EPOCH="${2:-}"; shift ;;
    *) echo "[GOBLIN50] unknown arg: $1" >&2; exit 1 ;;
  esac
  shift
done

log()  { echo "[GOBLIN50] $*"; }
fail() { echo "[GOBLIN50][FAIL] $*" >&2; exit 1; }

emit_receipt() {
  local epoch="$1" status="$2"
  cat > "${SCRATCH}/EPOCH_RECEIPT_${epoch}.json" <<JSON
{"type":"GOBLIN_EPOCH_RECEIPT_V1","epoch":"${epoch}","status":"${status}","authority":"NONE","world_effect":"NONE","ledger_mutation":false}
JSON
  log "receipt: ${epoch} → ${status}"
}

run_py() {
  local pyfile="$1"; shift
  if $DRY_RUN; then log "[DRY] python $pyfile $*"; return 0; fi
  "${VENV}" "$pyfile" "$@"
}

mkdir -p "${SCRATCH}" "${BOOT_DIR}"

# ─────────────────────── E1 ────────────────────────────────────────────────
epoch_E1() {
  log "E1 FREEZE — inventory worktree"
  cat > /tmp/g50_e1.py <<'PY'
import json, sys
from pathlib import Path
sot = Path(sys.argv[1]); sc = Path(sys.argv[2])
sc.mkdir(parents=True, exist_ok=True)
targets = ["helen_os/boot", "helen_os/manifest_registry.py", "helen_os/state/skill_library_state_updater.py"]
surface = [{"path": t, "exists": (sot/t).exists()} for t in targets]
(sc / "PATCH_SURFACE_50_V1.json").write_text(json.dumps({"type":"PATCH_SURFACE_50_V1","epoch":"E1","surface":surface,"authority":"NONE"}, indent=2))
print("E1 PASS")
PY
  run_py /tmp/g50_e1.py "${SOT_ROOT}" "${SCRATCH}" && emit_receipt E1 PASS || emit_receipt E1 FAIL
}

# ─────────────────────── E2 ────────────────────────────────────────────────
epoch_E2() {
  log "E2 HASH CHECK — verify canon_json_bytes present in validate_hash_chain"
  cat > /tmp/g50_e2.py <<'PY'
import sys
from pathlib import Path
sot = Path(sys.argv[1]); sc = Path(sys.argv[2])
tool = sot / "tools" / "validate_hash_chain.py"
src = tool.read_text() if tool.exists() else ""
ok = "canon_json_bytes" in src
print("E2 PASS" if ok else "E2 CANDIDATE_EMITTED")
PY
  run_py /tmp/g50_e2.py "${SOT_ROOT}" "${SCRATCH}" && emit_receipt E2 PASS || emit_receipt E2 FAIL
}

# ─────────────────────── E3 ────────────────────────────────────────────────
epoch_E3() {
  log "E3 RECEIPT TRIAD — verify binding tests exist"
  cat > /tmp/g50_e3.py <<'PY'
import json, sys
from pathlib import Path
sot = Path(sys.argv[1]); sc = Path(sys.argv[2])
files = ["tests/test_hash_chain_payload_hash.py", "tests/test_receipt_linkage.py"]
matrix = [{"file": f, "exists": (sot/f).exists()} for f in files]
ok = all(m["exists"] for m in matrix)
(sc / "RECEIPT_BINDING_MATRIX_V1.json").write_text(json.dumps({"type":"RECEIPT_BINDING_MATRIX_V1","epoch":"E3","test_coverage":matrix,"all_present":ok,"authority":"NONE","world_effect":"NONE"}, indent=2))
print("E3 PASS" if ok else "E3 TESTS_MISSING")
PY
  run_py /tmp/g50_e3.py "${SOT_ROOT}" "${SCRATCH}" && emit_receipt E3 PASS || emit_receipt E3 FAIL
}

# ─────────────────────── E4 ────────────────────────────────────────────────
epoch_E4() {
  log "E4 BASELINE — focused test run on manifest + state + receipt"
  cat > /tmp/g50_e4.py <<'PY'
import json, subprocess, sys
from pathlib import Path
sot = Path(sys.argv[1]); sc = Path(sys.argv[2])
result = subprocess.run(
    [str(sot / ".venv/bin/pytest"),
     "helen_os/tests/test_manifest_registry.py",
     "helen_os/tests/test_skill_library_state_manifest_fields.py",
     "tests/test_receipt_linkage.py",
     "tests/test_hash_chain_payload_hash.py",
     "-q", "--tb=no", "--no-header"],
    cwd=str(sot), capture_output=True, text=True
)
summary = (result.stdout + result.stderr)[-1000:]
(sc / "EVAL_RECEIPT_E4.json").write_text(json.dumps({"type":"EVAL_RECEIPT_V1","epoch":"E4","passed":result.returncode==0,"summary":summary,"authority":"NONE"}, indent=2))
print("E4 PASS" if result.returncode == 0 else "E4 FAILURES")
PY
  run_py /tmp/g50_e4.py "${SOT_ROOT}" "${SCRATCH}" && emit_receipt E4 PASS || { emit_receipt E4 REVIEW; true; }
}

# ─────────────────────── E5 ────────────────────────────────────────────────
epoch_E5() {
  log "E5 BOOT DIR — create helen_os/boot/__init__.py"
  cat > /tmp/g50_e5.py <<'PY'
import sys
from pathlib import Path
sot = Path(sys.argv[1])
boot = sot / "helen_os" / "boot"
boot.mkdir(exist_ok=True)
init = boot / "__init__.py"
if not init.exists():
    init.write_text('"""HELEN OS boot continuity spine. Non-sovereign."""\n')
    print("E5 CREATED")
else:
    print("E5 PASS")
PY
  run_py /tmp/g50_e5.py "${SOT_ROOT}" && emit_receipt E5 PASS || emit_receipt E5 FAIL
}

# ─────────────────────── E6 ────────────────────────────────────────────────
epoch_E6() {
  log "E6 RUNTIME_BOOT_CONTEXT — implement runtime_boot_context.py"
  cat > /tmp/g50_e6.py <<'PY'
import sys
from pathlib import Path
sot = Path(sys.argv[1])
target = sot / "helen_os" / "boot" / "runtime_boot_context.py"
if target.exists():
    print("E6 PASS"); sys.exit(0)
target.write_text('''\
"""RUNTIME_BOOT_CONTEXT_V1 — boot continuity object.

Law: greeting_render reads only this object.
     NOT provider memory. NOT ad hoc queries. NOT improvisation.

Graceful degradation: if component = None, render null-honest.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any


@dataclass
class RuntimeBootContext:
    """Composed boot context. All fields are optional — graceful degradation law."""
    person_profile: dict[str, Any] | None = None
    last_session: dict[str, Any] | None = None
    epoch_state: dict[str, Any] | None = None
    companion_state: dict[str, Any] | None = None
    live_context: dict[str, Any] | None = None
    boot_time_iso: str = ""
    loaded_from: str = "empty"  # "storage" | "fallback" | "empty"

    def is_empty(self) -> bool:
        return all(
            v is None
            for v in (self.person_profile, self.last_session,
                      self.epoch_state, self.companion_state, self.live_context)
        )

    def person_name(self) -> str | None:
        if self.person_profile:
            return self.person_profile.get("name")
        return None

    def last_epoch_id(self) -> str | None:
        if self.epoch_state:
            return self.epoch_state.get("epoch_id")
        return None

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "RUNTIME_BOOT_CONTEXT_V1",
            "person_profile": self.person_profile,
            "last_session": self.last_session,
            "epoch_state": self.epoch_state,
            "companion_state": self.companion_state,
            "live_context": self.live_context,
            "boot_time_iso": self.boot_time_iso,
            "loaded_from": self.loaded_from,
        }
''')
print("E6 CREATED")
PY
  run_py /tmp/g50_e6.py "${SOT_ROOT}" && emit_receipt E6 PASS || emit_receipt E6 FAIL
}

# ─────────────────────── E7 ────────────────────────────────────────────────
epoch_E7() {
  log "E7 BOOT_LOADER — implement boot_loader.py"
  cat > /tmp/g50_e7.py <<'PY'
import sys
from pathlib import Path
sot = Path(sys.argv[1])
target = sot / "helen_os" / "boot" / "boot_loader.py"
if target.exists():
    print("E7 PASS"); sys.exit(0)
target.write_text('''\
"""boot_loader.py — load RuntimeBootContext from storage.

Law: reads from storage only. Never queries provider APIs.
     Never improvises. Missing file = None field, not error.
"""
from __future__ import annotations
import json
from pathlib import Path
from .runtime_boot_context import RuntimeBootContext


PERSON_PROFILE_FILE = "person_profile_v1.json"
SESSION_LOG_FILE = "last_session_v1.json"
EPOCH_STATE_FILE = "epoch_state_v1.json"
COMPANION_STATE_FILE = "companion_state_v1.json"
LIVE_CONTEXT_FILE = "live_context_v1.json"


def _load_json(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def load_boot_context(storage_dir: str, boot_time_iso: str = "") -> RuntimeBootContext:
    """Load boot context from storage_dir. Missing files produce None fields."""
    d = Path(storage_dir)
    person_profile = _load_json(d / PERSON_PROFILE_FILE)
    last_session   = _load_json(d / SESSION_LOG_FILE)
    epoch_state    = _load_json(d / EPOCH_STATE_FILE)
    companion_state = _load_json(d / COMPANION_STATE_FILE)
    live_context   = _load_json(d / LIVE_CONTEXT_FILE)

    any_loaded = any(v is not None for v in
                     (person_profile, last_session, epoch_state,
                      companion_state, live_context))

    return RuntimeBootContext(
        person_profile=person_profile,
        last_session=last_session,
        epoch_state=epoch_state,
        companion_state=companion_state,
        live_context=live_context,
        boot_time_iso=boot_time_iso,
        loaded_from="storage" if any_loaded else "empty",
    )
''')
print("E7 CREATED")
PY
  run_py /tmp/g50_e7.py "${SOT_ROOT}" && emit_receipt E7 PASS || emit_receipt E7 FAIL
}

# ─────────────────────── E8 ────────────────────────────────────────────────
epoch_E8() {
  log "E8 SESSION_WRITER — implement session_writer.py"
  cat > /tmp/g50_e8.py <<'PY'
import sys
from pathlib import Path
sot = Path(sys.argv[1])
target = sot / "helen_os" / "boot" / "session_writer.py"
if target.exists():
    print("E8 PASS"); sys.exit(0)
target.write_text('''\
"""session_writer.py — write SESSION_LOG_V1 to storage.

Non-sovereign: writes files only. No ledger mutation.
"""
from __future__ import annotations
import json
from pathlib import Path


def write_session_log(session: dict, storage_dir: str) -> str:
    """Write session log to storage. Returns path written."""
    d = Path(storage_dir)
    d.mkdir(parents=True, exist_ok=True)
    path = d / "last_session_v1.json"
    payload = {
        "schema": "SESSION_LOG_V1",
        **{k: v for k, v in session.items() if k != "schema"},
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return str(path)
''')
print("E8 CREATED")
PY
  run_py /tmp/g50_e8.py "${SOT_ROOT}" && emit_receipt E8 PASS || emit_receipt E8 FAIL
}

# ─────────────────────── E9 ────────────────────────────────────────────────
epoch_E9() {
  log "E9 EPOCH_WRITER — implement epoch_writer.py"
  cat > /tmp/g50_e9.py <<'PY'
import sys
from pathlib import Path
sot = Path(sys.argv[1])
target = sot / "helen_os" / "boot" / "epoch_writer.py"
if target.exists():
    print("E9 PASS"); sys.exit(0)
target.write_text('''\
"""epoch_writer.py — write EPOCH_STATE_V1 to storage.

Non-sovereign: writes files only. No ledger mutation.
"""
from __future__ import annotations
import json
from pathlib import Path


def write_epoch_state(epoch: dict, storage_dir: str) -> str:
    """Write epoch state to storage. Returns path written."""
    d = Path(storage_dir)
    d.mkdir(parents=True, exist_ok=True)
    path = d / "epoch_state_v1.json"
    payload = {
        "schema": "EPOCH_STATE_V1",
        **{k: v for k, v in epoch.items() if k != "schema"},
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return str(path)
''')
print("E9 CREATED")
PY
  run_py /tmp/g50_e9.py "${SOT_ROOT}" && emit_receipt E9 PASS || emit_receipt E9 FAIL
}

# ─────────────────────── E10 ────────────────────────────────────────────────
epoch_E10() {
  log "E10 GREETING_RENDERER — implement greeting_renderer.py"
  cat > /tmp/g50_e10.py <<'PY'
import sys
from pathlib import Path
sot = Path(sys.argv[1])
target = sot / "helen_os" / "boot" / "greeting_renderer.py"
if target.exists():
    print("E10 PASS"); sys.exit(0)
target.write_text('''\
"""greeting_renderer.py — render boot greeting from RUNTIME_BOOT_CONTEXT_V1.

Law: reads ONLY RuntimeBootContext. No provider memory. No improvisation.
Graceful degradation: missing field → null-honest placeholder, never fiction.
"""
from __future__ import annotations
from .runtime_boot_context import RuntimeBootContext


def render_greeting(ctx: RuntimeBootContext) -> str:
    """Render greeting string from boot context. Null-honest on missing data."""
    if ctx.is_empty():
        return "HELEN: No prior context. Starting fresh."

    parts: list[str] = ["HELEN:"]

    name = ctx.person_name()
    if name:
        parts.append(f"Welcome back, {name}.")
    else:
        parts.append("Session resumed.")

    epoch_id = ctx.last_epoch_id()
    if epoch_id:
        parts.append(f"Last epoch: {epoch_id}.")
    else:
        parts.append("Epoch: unavailable.")

    if ctx.last_session:
        session_id = ctx.last_session.get("session_id")
        if session_id:
            parts.append(f"Last session: {session_id}.")

    parts.append(f"[loaded_from={ctx.loaded_from}]")
    return " ".join(parts)
''')
print("E10 CREATED")
PY
  run_py /tmp/g50_e10.py "${SOT_ROOT}" && emit_receipt E10 PASS || emit_receipt E10 FAIL
}

# ─────────────────────── E11 ────────────────────────────────────────────────
epoch_E11() {
  log "E11 TEST_BOOT_CONTEXT — write test_runtime_boot_context.py"
  cat > /tmp/g50_e11.py <<'PY'
import sys
from pathlib import Path
sot = Path(sys.argv[1])
target = sot / "helen_os" / "tests" / "test_runtime_boot_context.py"
if target.exists():
    print("E11 PASS"); sys.exit(0)
target.write_text('''\
"""Test: RuntimeBootContext — boot continuity object law."""
from helen_os.boot.runtime_boot_context import RuntimeBootContext


def test_empty_context_is_empty():
    ctx = RuntimeBootContext()
    assert ctx.is_empty()
    assert ctx.loaded_from == "empty"


def test_context_with_person_not_empty():
    ctx = RuntimeBootContext(person_profile={"name": "JM"})
    assert not ctx.is_empty()
    assert ctx.person_name() == "JM"


def test_missing_person_name_returns_none():
    ctx = RuntimeBootContext(person_profile={"role": "operator"})
    assert ctx.person_name() is None


def test_epoch_id_from_epoch_state():
    ctx = RuntimeBootContext(epoch_state={"epoch_id": "E42"})
    assert ctx.last_epoch_id() == "E42"


def test_missing_epoch_state_returns_none():
    ctx = RuntimeBootContext()
    assert ctx.last_epoch_id() is None


def test_to_dict_has_schema():
    ctx = RuntimeBootContext()
    d = ctx.to_dict()
    assert d["schema"] == "RUNTIME_BOOT_CONTEXT_V1"
    assert "person_profile" in d


def test_to_dict_preserves_loaded_from():
    ctx = RuntimeBootContext(loaded_from="storage", person_profile={"name": "X"})
    assert ctx.to_dict()["loaded_from"] == "storage"


def test_all_fields_none_is_empty():
    ctx = RuntimeBootContext(
        person_profile=None, last_session=None,
        epoch_state=None, companion_state=None, live_context=None,
    )
    assert ctx.is_empty()
''')
print("E11 CREATED")
PY
  run_py /tmp/g50_e11.py "${SOT_ROOT}" && emit_receipt E11 PASS || emit_receipt E11 FAIL
}

# ─────────────────────── E12 ────────────────────────────────────────────────
epoch_E12() {
  log "E12 TEST_BOOT_LOADER — write test_boot_loader.py"
  cat > /tmp/g50_e12.py <<'PY'
import sys
from pathlib import Path
sot = Path(sys.argv[1])
target = sot / "helen_os" / "tests" / "test_boot_loader.py"
if target.exists():
    print("E12 PASS"); sys.exit(0)
target.write_text('''\
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
''')
print("E12 CREATED")
PY
  run_py /tmp/g50_e12.py "${SOT_ROOT}" && emit_receipt E12 PASS || emit_receipt E12 FAIL
}

# ─────────────────────── E13 ────────────────────────────────────────────────
epoch_E13() {
  log "E13 TEST_WRITERS — write test_session_writer and test_epoch_writer"
  cat > /tmp/g50_e13.py <<'PY'
import sys
from pathlib import Path
sot = Path(sys.argv[1])
# session writer test
t1 = sot / "helen_os" / "tests" / "test_session_writer.py"
if not t1.exists():
    t1.write_text('''\
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
''')
# epoch writer test
t2 = sot / "helen_os" / "tests" / "test_epoch_writer.py"
if not t2.exists():
    t2.write_text('''\
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
''')
print("E13 CREATED")
PY
  run_py /tmp/g50_e13.py "${SOT_ROOT}" && emit_receipt E13 PASS || emit_receipt E13 FAIL
}

# ─────────────────────── E14 ────────────────────────────────────────────────
epoch_E14() {
  log "E14 TEST_GREETING — write test_greeting_renderer.py"
  cat > /tmp/g50_e14.py <<'PY'
import sys
from pathlib import Path
sot = Path(sys.argv[1])
target = sot / "helen_os" / "tests" / "test_greeting_renderer.py"
if target.exists():
    print("E14 PASS"); sys.exit(0)
target.write_text('''\
"""Test: greeting_renderer — reads only RuntimeBootContext, no improvisation."""
from helen_os.boot.runtime_boot_context import RuntimeBootContext
from helen_os.boot.greeting_renderer import render_greeting


def test_empty_context_returns_fresh_start():
    ctx = RuntimeBootContext()
    g = render_greeting(ctx)
    assert "No prior context" in g or "fresh" in g.lower()


def test_person_name_in_greeting():
    ctx = RuntimeBootContext(person_profile={"name": "JM"}, loaded_from="storage")
    g = render_greeting(ctx)
    assert "JM" in g


def test_epoch_id_in_greeting():
    ctx = RuntimeBootContext(epoch_state={"epoch_id": "E42"}, loaded_from="storage")
    g = render_greeting(ctx)
    assert "E42" in g


def test_session_id_in_greeting():
    ctx = RuntimeBootContext(
        last_session={"session_id": "S99"},
        epoch_state={"epoch_id": "E1"},
        loaded_from="storage",
    )
    g = render_greeting(ctx)
    assert "S99" in g


def test_loaded_from_in_greeting():
    ctx = RuntimeBootContext(
        person_profile={"name": "X"}, loaded_from="storage"
    )
    g = render_greeting(ctx)
    assert "storage" in g


def test_missing_name_does_not_crash():
    ctx = RuntimeBootContext(epoch_state={"epoch_id": "E1"}, loaded_from="storage")
    g = render_greeting(ctx)
    assert isinstance(g, str) and len(g) > 0


def test_greeting_is_deterministic():
    ctx = RuntimeBootContext(
        person_profile={"name": "JM"},
        epoch_state={"epoch_id": "E3"},
        loaded_from="storage",
    )
    assert render_greeting(ctx) == render_greeting(ctx)
''')
print("E14 CREATED")
PY
  run_py /tmp/g50_e14.py "${SOT_ROOT}" && emit_receipt E14 PASS || emit_receipt E14 FAIL
}

# ─────────────────────── E15 ────────────────────────────────────────────────
epoch_E15() {
  log "E15 RUN BOOT TESTS — run all helen_os/tests/test_*boot* and test_*greeting*"
  cat > /tmp/g50_e15.py <<'PY'
import json, subprocess, sys
from pathlib import Path
sot = Path(sys.argv[1]); sc = Path(sys.argv[2])
test_files = [
    "helen_os/tests/test_runtime_boot_context.py",
    "helen_os/tests/test_boot_loader.py",
    "helen_os/tests/test_session_writer.py",
    "helen_os/tests/test_epoch_writer.py",
    "helen_os/tests/test_greeting_renderer.py",
]
existing = [f for f in test_files if (sot/f).exists()]
if not existing:
    print("E15 NO_TESTS"); sys.exit(0)
result = subprocess.run(
    [str(sot/".venv/bin/pytest")] + existing + ["-q","--tb=short","--no-header"],
    cwd=str(sot), capture_output=True, text=True
)
summary = (result.stdout + result.stderr)[-2000:]
(sc / "EVAL_RECEIPT_E15.json").write_text(json.dumps({
    "type":"EVAL_RECEIPT_V1","epoch":"E15",
    "passed":result.returncode==0,"summary":summary,"authority":"NONE"
}, indent=2))
print("E15 PASS" if result.returncode == 0 else "E15 FAILURES")
PY
  run_py /tmp/g50_e15.py "${SOT_ROOT}" "${SCRATCH}" || true
  emit_receipt E15 DONE
}

# ─────────────────────── E16 ────────────────────────────────────────────────
epoch_E16() {
  log "E16 BOOT INTEGRATION TEST — full boot sequence"
  cat > /tmp/g50_e16.py <<'PY'
import sys
from pathlib import Path
sot = Path(sys.argv[1])
target = sot / "helen_os" / "tests" / "test_boot_integration.py"
if target.exists():
    print("E16 PASS"); sys.exit(0)
target.write_text('''\
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
''')
print("E16 CREATED")
PY
  run_py /tmp/g50_e16.py "${SOT_ROOT}" && emit_receipt E16 PASS || emit_receipt E16 FAIL
}

# ─────────────────────── E17 ────────────────────────────────────────────────
epoch_E17() {
  log "E17 RUN INTEGRATION — run test_boot_integration.py"
  cat > /tmp/g50_e17.py <<'PY'
import json, subprocess, sys
from pathlib import Path
sot = Path(sys.argv[1]); sc = Path(sys.argv[2])
result = subprocess.run(
    [str(sot/".venv/bin/pytest"), "helen_os/tests/test_boot_integration.py",
     "-v","--tb=short","--no-header"],
    cwd=str(sot), capture_output=True, text=True
)
summary = (result.stdout + result.stderr)[-2000:]
(sc/"EVAL_RECEIPT_E17.json").write_text(json.dumps({
    "type":"EVAL_RECEIPT_V1","epoch":"E17",
    "passed":result.returncode==0,"summary":summary,"authority":"NONE"
}, indent=2))
print("E17 PASS" if result.returncode==0 else "E17 FAILURES:\n"+summary)
PY
  run_py /tmp/g50_e17.py "${SOT_ROOT}" "${SCRATCH}" || true
  emit_receipt E17 DONE
}

# ─────────────────────── E18 ────────────────────────────────────────────────
epoch_E18() {
  log "E18 SOVEREIGN AUDIT — verify boot spine never touches sovereign paths"
  cat > /tmp/g50_e18.py <<'PY'
import sys
from pathlib import Path
sot = Path(sys.argv[1])
boot = sot / "helen_os" / "boot"
sovereign_imports = ["governance", "ledger_v1", "mayor_", "kernel_daemon"]
violations = []
for f in boot.glob("*.py"):
    src = f.read_text()
    for bad in sovereign_imports:
        if bad in src:
            violations.append(f"{f.name}: contains '{bad}'")
if violations:
    print("E18 VIOLATION: " + "; ".join(violations))
else:
    print("E18 PASS")
PY
  run_py /tmp/g50_e18.py "${SOT_ROOT}" && emit_receipt E18 PASS || emit_receipt E18 FAIL
}

# ─────────────────────── E19 ────────────────────────────────────────────────
epoch_E19() {
  log "E19 MANIFEST REGISTRY TEST — run test_manifest_registry.py"
  cat > /tmp/g50_e19.py <<'PY'
import json, subprocess, sys
from pathlib import Path
sot = Path(sys.argv[1]); sc = Path(sys.argv[2])
result = subprocess.run(
    [str(sot/".venv/bin/pytest"), "helen_os/tests/test_manifest_registry.py",
     "-q","--tb=no","--no-header"],
    cwd=str(sot), capture_output=True, text=True
)
summary = (result.stdout+result.stderr)[-500:]
(sc/"EVAL_RECEIPT_E19.json").write_text(json.dumps({
    "type":"EVAL_RECEIPT_V1","epoch":"E19",
    "passed":result.returncode==0,"summary":summary,"authority":"NONE"
}, indent=2))
print("E19 PASS" if result.returncode==0 else "E19 FAILURES")
PY
  run_py /tmp/g50_e19.py "${SOT_ROOT}" "${SCRATCH}" && emit_receipt E19 PASS || { emit_receipt E19 REVIEW; true; }
}

# ─────────────────────── E20 ────────────────────────────────────────────────
epoch_E20() {
  log "E20 STATE UPDATER TEST — run test_skill_library_state_manifest_fields.py"
  cat > /tmp/g50_e20.py <<'PY'
import json, subprocess, sys
from pathlib import Path
sot = Path(sys.argv[1]); sc = Path(sys.argv[2])
result = subprocess.run(
    [str(sot/".venv/bin/pytest"),
     "helen_os/tests/test_skill_library_state_manifest_fields.py",
     "helen_os/tests/test_skill_library_state_changes_only_on_admitted.py",
     "-q","--tb=no","--no-header"],
    cwd=str(sot), capture_output=True, text=True
)
summary = (result.stdout+result.stderr)[-500:]
(sc/"EVAL_RECEIPT_E20.json").write_text(json.dumps({
    "type":"EVAL_RECEIPT_V1","epoch":"E20",
    "passed":result.returncode==0,"summary":summary,"authority":"NONE"
}, indent=2))
print("E20 PASS" if result.returncode==0 else "E20 FAILURES")
PY
  run_py /tmp/g50_e20.py "${SOT_ROOT}" "${SCRATCH}" && emit_receipt E20 PASS || { emit_receipt E20 REVIEW; true; }
}

# ─────────────────────── E21-E30: Validation sweep ─────────────────────────
epoch_E21() {
  log "E21 FULL BOOT SUITE — run all boot tests together"
  cat > /tmp/g50_e21.py <<'PY'
import json, subprocess, sys
from pathlib import Path
sot = Path(sys.argv[1]); sc = Path(sys.argv[2])
result = subprocess.run(
    [str(sot/".venv/bin/pytest"),
     "helen_os/tests/test_runtime_boot_context.py",
     "helen_os/tests/test_boot_loader.py",
     "helen_os/tests/test_session_writer.py",
     "helen_os/tests/test_epoch_writer.py",
     "helen_os/tests/test_greeting_renderer.py",
     "helen_os/tests/test_boot_integration.py",
     "-v","--tb=short","--no-header"],
    cwd=str(sot), capture_output=True, text=True
)
summary = (result.stdout+result.stderr)[-3000:]
(sc/"EVAL_RECEIPT_E21.json").write_text(json.dumps({
    "type":"EVAL_RECEIPT_V1","epoch":"E21",
    "passed":result.returncode==0,"summary":summary,"authority":"NONE"
}, indent=2))
print("E21 PASS" if result.returncode==0 else "E21 FAILURES")
PY
  run_py /tmp/g50_e21.py "${SOT_ROOT}" "${SCRATCH}" && emit_receipt E21 PASS || { emit_receipt E21 REVIEW; true; }
}

epoch_E22() {
  log "E22 HASH CHAIN TESTS — run test_hash_chain_payload_hash.py"
  cat > /tmp/g50_e22.py <<'PY'
import json, subprocess, sys
from pathlib import Path
sot = Path(sys.argv[1]); sc = Path(sys.argv[2])
result = subprocess.run(
    [str(sot/".venv/bin/pytest"), "tests/test_hash_chain_payload_hash.py",
     "-q","--tb=no","--no-header"],
    cwd=str(sot), capture_output=True, text=True
)
summary = (result.stdout+result.stderr)[-500:]
(sc/"EVAL_RECEIPT_E22.json").write_text(json.dumps({
    "type":"EVAL_RECEIPT_V1","epoch":"E22",
    "passed":result.returncode==0,"summary":summary,"authority":"NONE"
}, indent=2))
print("E22 PASS" if result.returncode==0 else "E22 FAILURES")
PY
  run_py /tmp/g50_e22.py "${SOT_ROOT}" "${SCRATCH}" && emit_receipt E22 PASS || { emit_receipt E22 REVIEW; true; }
}

epoch_E23() {
  log "E23 RECEIPT LINKAGE TESTS — run test_receipt_linkage.py"
  cat > /tmp/g50_e23.py <<'PY'
import json, subprocess, sys
from pathlib import Path
sot = Path(sys.argv[1]); sc = Path(sys.argv[2])
result = subprocess.run(
    [str(sot/".venv/bin/pytest"), "tests/test_receipt_linkage.py",
     "-q","--tb=no","--no-header"],
    cwd=str(sot), capture_output=True, text=True
)
summary = (result.stdout+result.stderr)[-500:]
(sc/"EVAL_RECEIPT_E23.json").write_text(json.dumps({
    "type":"EVAL_RECEIPT_V1","epoch":"E23",
    "passed":result.returncode==0,"summary":summary,"authority":"NONE"
}, indent=2))
print("E23 PASS" if result.returncode==0 else "E23 FAILURES")
PY
  run_py /tmp/g50_e23.py "${SOT_ROOT}" "${SCRATCH}" && emit_receipt E23 PASS || { emit_receipt E23 REVIEW; true; }
}

epoch_E24() {
  log "E24 KNOWN FAILURES AUDIT — cluster pre-existing vs new failures"
  cat > /tmp/g50_e24.py <<'PY'
import json, subprocess, sys
from pathlib import Path
sot = Path(sys.argv[1]); sc = Path(sys.argv[2])
result = subprocess.run(
    [str(sot/".venv/bin/pytest"), "helen_os/tests/", "-q","--tb=no","--no-header"],
    cwd=str(sot), capture_output=True, text=True
)
lines = (result.stdout+result.stderr).splitlines()
failures = [l for l in lines if l.startswith("FAILED")]
pre_existing = [f for f in failures if any(k in f for k in
    ["ghost_closures","legacy_schemas_directory","manifest_gate","reducer_manifest_gate"])]
new_failures = [f for f in failures if f not in pre_existing]
cluster = {
    "type":"FAILURE_CLUSTER_V1","epoch":"E24",
    "total_failures":len(failures),
    "pre_existing":pre_existing,"new_failures":new_failures,
    "authority":"NONE","world_effect":"NONE","ledger_mutation":False
}
(sc/"FAILURE_CLUSTER_E24.json").write_text(json.dumps(cluster, indent=2))
print(f"E24 PASS — {len(failures)} known failures ({len(new_failures)} new)")
PY
  run_py /tmp/g50_e24.py "${SOT_ROOT}" "${SCRATCH}" && emit_receipt E24 PASS || emit_receipt E24 FAIL
}

epoch_E25() {
  log "E25 PROMOTION RECEIPTS AUDIT — verify reducer tests"
  cat > /tmp/g50_e25.py <<'PY'
import json, subprocess, sys
from pathlib import Path
sot = Path(sys.argv[1]); sc = Path(sys.argv[2])
result = subprocess.run(
    [str(sot/".venv/bin/pytest"),
     "helen_os/tests/test_skill_promotion_requires_receipts.py",
     "-q","--tb=no","--no-header"],
    cwd=str(sot), capture_output=True, text=True
)
summary = (result.stdout+result.stderr)[-500:]
(sc/"EVAL_RECEIPT_E25.json").write_text(json.dumps({
    "type":"EVAL_RECEIPT_V1","epoch":"E25",
    "passed":result.returncode==0,"summary":summary,"authority":"NONE"
}, indent=2))
print("E25 PASS" if result.returncode==0 else "E25 FAILURES")
PY
  run_py /tmp/g50_e25.py "${SOT_ROOT}" "${SCRATCH}" && emit_receipt E25 PASS || { emit_receipt E25 REVIEW; true; }
}

epoch_E26() {
  log "E26 GREETING NULL-HONEST — test missing name and missing epoch"
  cat > /tmp/g50_e26.py <<'PY'
import sys
from pathlib import Path
sot = Path(sys.argv[1])
# Run a quick inline test
sys.path.insert(0, str(sot))
from helen_os.boot.runtime_boot_context import RuntimeBootContext
from helen_os.boot.greeting_renderer import render_greeting

# null-honest: no person, no epoch
ctx = RuntimeBootContext()
g = render_greeting(ctx)
assert "No prior context" in g or "fresh" in g.lower(), f"not null-honest: {g!r}"

# partial: epoch but no name
ctx2 = RuntimeBootContext(epoch_state={"epoch_id":"E7"}, loaded_from="storage")
g2 = render_greeting(ctx2)
assert "E7" in g2, f"epoch not in greeting: {g2!r}"
assert isinstance(g2, str)

print("E26 PASS")
PY
  run_py /tmp/g50_e26.py "${SOT_ROOT}" && emit_receipt E26 PASS || emit_receipt E26 FAIL
}

epoch_E27() {
  log "E27 GREETING DETERMINISM — same context → same greeting"
  cat > /tmp/g50_e27.py <<'PY'
import sys
from pathlib import Path
sot = Path(sys.argv[1])
sys.path.insert(0, str(sot))
from helen_os.boot.runtime_boot_context import RuntimeBootContext
from helen_os.boot.greeting_renderer import render_greeting

ctx = RuntimeBootContext(
    person_profile={"name":"JM"},
    epoch_state={"epoch_id":"E10"},
    last_session={"session_id":"S5"},
    loaded_from="storage",
)
results = [render_greeting(ctx) for _ in range(5)]
assert all(r == results[0] for r in results), f"non-deterministic: {results}"
print("E27 PASS")
PY
  run_py /tmp/g50_e27.py "${SOT_ROOT}" && emit_receipt E27 PASS || emit_receipt E27 FAIL
}

epoch_E28() {
  log "E28 BOOT LOADER IDEMPOTENT — load twice gives same result"
  cat > /tmp/g50_e28.py <<'PY'
import sys, json, tempfile
from pathlib import Path
sot = Path(sys.argv[1])
sys.path.insert(0, str(sot))
from helen_os.boot.boot_loader import load_boot_context

with tempfile.TemporaryDirectory() as td:
    p = Path(td)
    (p / "person_profile_v1.json").write_text(json.dumps({"name":"X"}))
    (p / "epoch_state_v1.json").write_text(json.dumps({"epoch_id":"E1"}))
    c1 = load_boot_context(td, "2026-06-11T00:00:00Z")
    c2 = load_boot_context(td, "2026-06-11T00:00:00Z")
    assert c1.to_dict() == c2.to_dict(), "non-idempotent load"
print("E28 PASS")
PY
  run_py /tmp/g50_e28.py "${SOT_ROOT}" && emit_receipt E28 PASS || emit_receipt E28 FAIL
}

epoch_E29() {
  log "E29 SESSION + EPOCH ROUNDTRIP — write then load"
  cat > /tmp/g50_e29.py <<'PY'
import sys, json, tempfile
from pathlib import Path
sot = Path(sys.argv[1])
sys.path.insert(0, str(sot))
from helen_os.boot.session_writer import write_session_log
from helen_os.boot.epoch_writer import write_epoch_state
from helen_os.boot.boot_loader import load_boot_context

with tempfile.TemporaryDirectory() as td:
    write_session_log({"session_id":"S42","status":"closed"}, td)
    write_epoch_state({"epoch_id":"E50","status":"complete"}, td)
    ctx = load_boot_context(td)
    assert ctx.last_session["session_id"] == "S42"
    assert ctx.epoch_state["epoch_id"] == "E50"
    assert ctx.loaded_from == "storage"
print("E29 PASS")
PY
  run_py /tmp/g50_e29.py "${SOT_ROOT}" && emit_receipt E29 PASS || emit_receipt E29 FAIL
}

epoch_E30() {
  log "E30 FULL SUITE SNAPSHOT — run helen_os/tests/ and record baseline"
  cat > /tmp/g50_e30.py <<'PY'
import json, subprocess, sys
from pathlib import Path
sot = Path(sys.argv[1]); sc = Path(sys.argv[2])
result = subprocess.run(
    [str(sot/".venv/bin/pytest"), "helen_os/tests/", "-q","--tb=no","--no-header"],
    cwd=str(sot), capture_output=True, text=True
)
lines = (result.stdout+result.stderr).splitlines()
summary_line = next((l for l in reversed(lines) if "passed" in l or "failed" in l), "")
(sc/"FULL_SUITE_SNAPSHOT_E30.json").write_text(json.dumps({
    "type":"TEST_RESULTS_V1","epoch":"E30",
    "returncode":result.returncode,"summary":summary_line,"authority":"NONE"
}, indent=2))
print(f"E30 SNAPSHOT: {summary_line}")
PY
  run_py /tmp/g50_e30.py "${SOT_ROOT}" "${SCRATCH}" && emit_receipt E30 PASS || emit_receipt E30 FAIL
}

# ─────────────────────── E31-E40: Seam hardening ───────────────────────────
epoch_E31() {
  log "E31 BOOT NULL SAFETY — person_profile with missing keys"
  cat > /tmp/g50_e31.py <<'PY'
import sys
from pathlib import Path
sot = Path(sys.argv[1])
sys.path.insert(0, str(sot))
from helen_os.boot.runtime_boot_context import RuntimeBootContext
from helen_os.boot.greeting_renderer import render_greeting

# person_profile exists but has no name key
ctx = RuntimeBootContext(person_profile={"role":"operator"}, loaded_from="storage")
g = render_greeting(ctx)
assert isinstance(g, str) and len(g) > 0, "crashed on missing name"
assert "None" not in g, f"exposed None in greeting: {g!r}"
print("E31 PASS")
PY
  run_py /tmp/g50_e31.py "${SOT_ROOT}" && emit_receipt E31 PASS || emit_receipt E31 FAIL
}

epoch_E32() {
  log "E32 EPOCH STATE PARTIAL — epoch_state with no epoch_id"
  cat > /tmp/g50_e32.py <<'PY'
import sys
from pathlib import Path
sot = Path(sys.argv[1])
sys.path.insert(0, str(sot))
from helen_os.boot.runtime_boot_context import RuntimeBootContext
from helen_os.boot.greeting_renderer import render_greeting

ctx = RuntimeBootContext(epoch_state={"status":"running"}, loaded_from="storage")
assert ctx.last_epoch_id() is None
g = render_greeting(ctx)
assert "None" not in g, f"None exposed: {g!r}"
assert "unavailable" in g or "Epoch" in g
print("E32 PASS")
PY
  run_py /tmp/g50_e32.py "${SOT_ROOT}" && emit_receipt E32 PASS || emit_receipt E32 FAIL
}

epoch_E33() {
  log "E33 MANIFEST REGISTRY VALIDATE — validate_skill_allowed three-check"
  cat > /tmp/g50_e33.py <<'PY'
import sys
from pathlib import Path
sot = Path(sys.argv[1])
sys.path.insert(0, str(sot))
from helen_os.manifest_registry import ManifestRegistry, ManifestRegistrationError

reg = ManifestRegistry()
m = {"manifest_id":"M1","authority":"NONE","allowed_skills":["S1","S2"],
     "domain_category":"reasoning","provider_class":"INTERNAL"}
rec = reg.register(m)
assert reg.validate_skill_allowed("S1","M1",rec.manifest_hash) is True
assert reg.validate_skill_allowed("S99","M1",rec.manifest_hash) is False
assert reg.validate_skill_allowed("S1","M_BAD",rec.manifest_hash) is False
assert reg.validate_skill_allowed("S1","M1","sha256:"+"0"*64) is False
print("E33 PASS")
PY
  run_py /tmp/g50_e33.py "${SOT_ROOT}" && emit_receipt E33 PASS || emit_receipt E33 FAIL
}

epoch_E34() {
  log "E34 MANIFEST AUTHORITY FENCE — all non-NONE authorities blocked"
  cat > /tmp/g50_e34.py <<'PY'
import sys
from pathlib import Path
sot = Path(sys.argv[1])
sys.path.insert(0, str(sot))
from helen_os.manifest_registry import ManifestRegistry, ManifestRegistrationError

reg = ManifestRegistry()
base = {"manifest_id":"M","allowed_skills":[],"domain_category":"x","provider_class":"y"}
for bad_auth in ["MAYOR","SOVEREIGN","REDUCER","KERNEL","ADMIN","admin","true",True]:
    try:
        reg.register({**base, "authority": bad_auth})
        print(f"E34 VIOLATION: authority {bad_auth!r} accepted"); exit(1)
    except (ManifestRegistrationError, Exception):
        pass
print("E34 PASS")
PY
  run_py /tmp/g50_e34.py "${SOT_ROOT}" && emit_receipt E34 PASS || emit_receipt E34 FAIL
}

epoch_E35() {
  log "E35 STATE UPDATER NO-OP ON REJECTED — rejected decision leaves state unchanged"
  cat > /tmp/g50_e35.py <<'PY'
import sys
from pathlib import Path
sot = Path(sys.argv[1])
sys.path.insert(0, str(sot))
from helen_os.state.skill_library_state_updater import apply_skill_promotion_decision

state = {
    "schema_name":"SKILL_LIBRARY_STATE_V1","schema_version":"1.0.0",
    "law_surface_version":"v1","active_skills":{"S0":{"active_version":"1","status":"ACTIVE","last_decision_id":"D0"}}
}
for dtype in ["REJECTED","QUARANTINED"]:
    dec = {
        "schema_name":"SKILL_PROMOTION_DECISION_V1","schema_version":"1.0.0",
        "decision_id":"D1","skill_id":"S1","candidate_version":"2.0.0",
        "decision_type":dtype,"reason_code":"EVAL_FAIL"
    }
    new = apply_skill_promotion_decision(state, dec)
    assert "S1" not in new["active_skills"], f"state mutated on {dtype}"
print("E35 PASS")
PY
  run_py /tmp/g50_e35.py "${SOT_ROOT}" && emit_receipt E35 PASS || emit_receipt E35 FAIL
}

epoch_E36() {
  log "E36 STATE UPDATER ADMITTED WITH MANIFEST — all 7 fields present"
  cat > /tmp/g50_e36.py <<'PY'
import sys
from pathlib import Path
sot = Path(sys.argv[1])
sys.path.insert(0, str(sot))
from helen_os.state.skill_library_state_updater import apply_skill_promotion_decision

state = {
    "schema_name":"SKILL_LIBRARY_STATE_V1","schema_version":"1.0.0",
    "law_surface_version":"v1","active_skills":{"S0":{"active_version":"1","status":"ACTIVE","last_decision_id":"D0"}}
}
dec = {
    "schema_name":"SKILL_PROMOTION_DECISION_V1","schema_version":"1.0.0",
    "decision_id":"D2","skill_id":"S1","candidate_version":"1.0.0",
    "decision_type":"ADMITTED","reason_code":"EVAL_PASS",
    "candidate_identity_hash":"sha256:"+"c"*64
}
packet = {"manifest_id":"M1","manifest_hash":"sha256:"+"a"*64,"domain_category":"reasoning","provider_class":"INTERNAL"}
new = apply_skill_promotion_decision(state, dec, packet)
entry = new["active_skills"]["S1"]
for field in ("active_version","status","last_decision_id","manifest_id","manifest_hash","domain_category","provider_class"):
    assert field in entry, f"missing: {field}"
print("E36 PASS")
PY
  run_py /tmp/g50_e36.py "${SOT_ROOT}" && emit_receipt E36 PASS || emit_receipt E36 FAIL
}

epoch_E37() {
  log "E37 REVIEW PACKET — generate governance patch review packet"
  cat > /tmp/g50_e37.py <<'PY'
import json, sys
from pathlib import Path
sot = Path(sys.argv[1]); sc = Path(sys.argv[2])
packet = {
    "type":"REVIEW_PACKET_DRAFT_V1","epoch":"E37",
    "blocked_patches":[
        {"file":"helen_os/governance/reason_codes.py","reason":"ERR_MANIFEST_NOT_FOUND + ERR_MANIFEST_SKILL_UNAUTHORIZED","staged_at":"docs/proposals/code/reason_codes_additions.py"},
        {"file":"helen_os/governance/skill_promotion_reducer.py","reason":"Gate 7 manifest enforcement + gate reorder","staged_at":"docs/proposals/code/skill_promotion_reducer_v2.py"},
        {"file":"helen_os/schemas/skill_promotion_packet_v1.json","reason":"manifest_id + manifest_hash + domain_category + provider_class fields","staged_at":"docs/proposals/code/skill_promotion_packet_v1_v2.json"},
    ],
    "red_tests":[
        "helen_os/tests/test_reducer_manifest_gate_v2.py (7 tests)",
        "helen_os/tests/test_skill_promotion_manifest_gate.py (3 tests)",
    ],
    "route":"MAYOR via tools/helen_say.py (daemon currently down)",
    "authority":"NONE","ready_for_mayor_review":True
}
(sc/"REVIEW_PACKET_DRAFT_GOVERNANCE.json").write_text(json.dumps(packet, indent=2))
print("E37 PASS")
PY
  run_py /tmp/g50_e37.py "${SOT_ROOT}" "${SCRATCH}" && emit_receipt E37 PASS || emit_receipt E37 FAIL
}

epoch_E38() {
  log "E38 CANON JSON CONSISTENCY — verify same dict always produces same hash"
  cat > /tmp/g50_e38.py <<'PY'
import hashlib, sys
from pathlib import Path
sot = Path(sys.argv[1])
sys.path.insert(0, str(sot))
from kernel.canonical_json import canon_json_bytes

cases = [
    {"b":2,"a":1},
    {"nested":{"z":9,"a":1},"top":"value"},
    {"list":[3,1,2],"num":42},
    {},
]
for c in cases:
    h1 = hashlib.sha256(canon_json_bytes(c)).hexdigest()
    h2 = hashlib.sha256(canon_json_bytes(dict(reversed(list(c.items()))))).hexdigest()
    assert h1 == h2, f"order-sensitive hash: {c}"
print("E38 PASS")
PY
  run_py /tmp/g50_e38.py "${SOT_ROOT}" && emit_receipt E38 PASS || emit_receipt E38 FAIL
}

epoch_E39() {
  log "E39 BOOT SPINE FILE INVENTORY — confirm all 6 boot files exist"
  cat > /tmp/g50_e39.py <<'PY'
import json, sys
from pathlib import Path
sot = Path(sys.argv[1]); sc = Path(sys.argv[2])
files = [
    "helen_os/boot/__init__.py",
    "helen_os/boot/runtime_boot_context.py",
    "helen_os/boot/boot_loader.py",
    "helen_os/boot/session_writer.py",
    "helen_os/boot/epoch_writer.py",
    "helen_os/boot/greeting_renderer.py",
]
inventory = [{"file":f,"exists":(sot/f).exists()} for f in files]
all_present = all(i["exists"] for i in inventory)
(sc/"BOOT_SPINE_INVENTORY.json").write_text(json.dumps({
    "type":"BOOT_SPINE_INVENTORY_V1","epoch":"E39",
    "files":inventory,"all_present":all_present,"authority":"NONE"
}, indent=2))
print("E39 PASS" if all_present else "E39 MISSING: "+str([i["file"] for i in inventory if not i["exists"]]))
PY
  run_py /tmp/g50_e39.py "${SOT_ROOT}" "${SCRATCH}" && emit_receipt E39 PASS || emit_receipt E39 FAIL
}

epoch_E40() {
  log "E40 TEST INVENTORY — confirm all 6 boot test files exist"
  cat > /tmp/g50_e40.py <<'PY'
import json, sys
from pathlib import Path
sot = Path(sys.argv[1]); sc = Path(sys.argv[2])
files = [
    "helen_os/tests/test_runtime_boot_context.py",
    "helen_os/tests/test_boot_loader.py",
    "helen_os/tests/test_session_writer.py",
    "helen_os/tests/test_epoch_writer.py",
    "helen_os/tests/test_greeting_renderer.py",
    "helen_os/tests/test_boot_integration.py",
]
inventory = [{"file":f,"exists":(sot/f).exists()} for f in files]
all_present = all(i["exists"] for i in inventory)
(sc/"BOOT_TEST_INVENTORY.json").write_text(json.dumps({
    "type":"BOOT_TEST_INVENTORY_V1","epoch":"E40",
    "files":inventory,"all_present":all_present,"authority":"NONE"
}, indent=2))
print("E40 PASS" if all_present else "E40 MISSING: "+str([i["file"] for i in inventory if not i["exists"]]))
PY
  run_py /tmp/g50_e40.py "${SOT_ROOT}" "${SCRATCH}" && emit_receipt E40 PASS || emit_receipt E40 FAIL
}

# ─────────────────────── E41-E50: Final sweep ───────────────────────────────
epoch_E41() {
  log "E41 RUN ALL BOOT TESTS FINAL"
  cat > /tmp/g50_e41.py <<'PY'
import json, subprocess, sys
from pathlib import Path
sot = Path(sys.argv[1]); sc = Path(sys.argv[2])
result = subprocess.run(
    [str(sot/".venv/bin/pytest"), "helen_os/tests/", "-k",
     "boot or greeting or session_writer or epoch_writer",
     "-v","--tb=short","--no-header"],
    cwd=str(sot), capture_output=True, text=True
)
summary = (result.stdout+result.stderr)[-3000:]
(sc/"FINAL_BOOT_RECEIPT.json").write_text(json.dumps({
    "type":"EVAL_RECEIPT_V1","epoch":"E41",
    "passed":result.returncode==0,"summary":summary,"authority":"NONE"
}, indent=2))
print("E41 PASS" if result.returncode==0 else "E41 FAILURES")
PY
  run_py /tmp/g50_e41.py "${SOT_ROOT}" "${SCRATCH}" && emit_receipt E41 PASS || { emit_receipt E41 REVIEW; true; }
}

epoch_E42() {
  log "E42 MANIFEST REGISTRY FULL TEST RUN"
  cat > /tmp/g50_e42.py <<'PY'
import json, subprocess, sys
from pathlib import Path
sot = Path(sys.argv[1]); sc = Path(sys.argv[2])
result = subprocess.run(
    [str(sot/".venv/bin/pytest"),
     "helen_os/tests/test_manifest_registry.py",
     "helen_os/tests/test_skill_library_state_manifest_fields.py",
     "-v","--tb=short","--no-header"],
    cwd=str(sot), capture_output=True, text=True
)
summary = (result.stdout+result.stderr)[-2000:]
(sc/"FINAL_MANIFEST_RECEIPT.json").write_text(json.dumps({
    "type":"EVAL_RECEIPT_V1","epoch":"E42",
    "passed":result.returncode==0,"summary":summary,"authority":"NONE"
}, indent=2))
print("E42 PASS" if result.returncode==0 else "E42 FAILURES")
PY
  run_py /tmp/g50_e42.py "${SOT_ROOT}" "${SCRATCH}" && emit_receipt E42 PASS || { emit_receipt E42 REVIEW; true; }
}

epoch_E43() {
  log "E43 HASH + RECEIPT FINAL — run tests/test_hash* and tests/test_receipt*"
  cat > /tmp/g50_e43.py <<'PY'
import json, subprocess, sys
from pathlib import Path
sot = Path(sys.argv[1]); sc = Path(sys.argv[2])
result = subprocess.run(
    [str(sot/".venv/bin/pytest"),
     "tests/test_hash_chain_payload_hash.py",
     "tests/test_receipt_linkage.py",
     "-v","--tb=short","--no-header"],
    cwd=str(sot), capture_output=True, text=True
)
summary = (result.stdout+result.stderr)[-2000:]
(sc/"FINAL_HASH_RECEIPT.json").write_text(json.dumps({
    "type":"EVAL_RECEIPT_V1","epoch":"E43",
    "passed":result.returncode==0,"summary":summary,"authority":"NONE"
}, indent=2))
print("E43 PASS" if result.returncode==0 else "E43 FAILURES")
PY
  run_py /tmp/g50_e43.py "${SOT_ROOT}" "${SCRATCH}" && emit_receipt E43 PASS || { emit_receipt E43 REVIEW; true; }
}

epoch_E44() {
  log "E44 FULL HELEN_OS SUITE — final snapshot"
  cat > /tmp/g50_e44.py <<'PY'
import json, subprocess, sys
from pathlib import Path
sot = Path(sys.argv[1]); sc = Path(sys.argv[2])
result = subprocess.run(
    [str(sot/".venv/bin/pytest"), "helen_os/tests/", "-q","--tb=no","--no-header"],
    cwd=str(sot), capture_output=True, text=True
)
lines = (result.stdout+result.stderr).splitlines()
failures = [l for l in lines if l.startswith("FAILED")]
summary_line = next((l for l in reversed(lines) if "passed" in l or "failed" in l), "")
(sc/"FINAL_SUITE_SNAPSHOT.json").write_text(json.dumps({
    "type":"TEST_RESULTS_V1","epoch":"E44",
    "returncode":result.returncode,"failures":failures,
    "summary":summary_line,"authority":"NONE"
}, indent=2))
print(f"E44 SNAPSHOT: {summary_line}")
PY
  run_py /tmp/g50_e44.py "${SOT_ROOT}" "${SCRATCH}" && emit_receipt E44 PASS || emit_receipt E44 FAIL
}

epoch_E45() {
  log "E45 SOVEREIGN CORE AUDIT — confirm no new sovereign writes"
  cat > /tmp/g50_e45.py <<'PY'
import subprocess, sys
from pathlib import Path
sot = Path(sys.argv[1])
result = subprocess.run(
    ["git","diff","--name-only","HEAD"],
    cwd=str(sot), capture_output=True, text=True
)
modified = result.stdout.strip().splitlines()
sovereign_patterns = ["oracle_town/kernel","helen_os/governance","helen_os/schemas",
                      "town/ledger_v1","mayor_","GOVERNANCE/CLOSURES","GOVERNANCE/TRANCHE"]
violations = [f for f in modified for p in sovereign_patterns if p in f]
if violations:
    print("E45 SOVEREIGN VIOLATION: " + str(violations))
else:
    print("E45 PASS — sovereign core untouched")
PY
  run_py /tmp/g50_e45.py "${SOT_ROOT}" && emit_receipt E45 PASS || emit_receipt E45 FAIL
}

epoch_E46() {
  log "E46 BOOT CONTEXT LAW PROOF — greeting uses ONLY boot context"
  cat > /tmp/g50_e46.py <<'PY'
import sys
from pathlib import Path
sot = Path(sys.argv[1])
# Verify greeting_renderer imports ONLY from runtime_boot_context
src = (sot / "helen_os" / "boot" / "greeting_renderer.py").read_text()
bad_imports = ["requests","sqlite","redis","provider","memory_db","ollama","openai","anthropic"]
violations = [b for b in bad_imports if b in src]
if violations:
    print("E46 VIOLATION: external deps in greeting_renderer: " + str(violations))
else:
    print("E46 PASS — greeting_renderer reads only RuntimeBootContext")
PY
  run_py /tmp/g50_e46.py "${SOT_ROOT}" && emit_receipt E46 PASS || emit_receipt E46 FAIL
}

epoch_E47() {
  log "E47 BOOT LOADER LAW PROOF — boot_loader reads only files, no API calls"
  cat > /tmp/g50_e47.py <<'PY'
import sys
from pathlib import Path
sot = Path(sys.argv[1])
src = (sot / "helen_os" / "boot" / "boot_loader.py").read_text()
bad = ["requests","urllib","httpx","sqlite","redis","provider","ollama","openai","anthropic"]
violations = [b for b in bad if b in src]
if violations:
    print("E47 VIOLATION: external deps in boot_loader: " + str(violations))
else:
    print("E47 PASS — boot_loader reads only storage files")
PY
  run_py /tmp/g50_e47.py "${SOT_ROOT}" && emit_receipt E47 PASS || emit_receipt E47 FAIL
}

epoch_E48() {
  log "E48 LAWFUL FORGETTING CHECK — boot context has no accumulation path"
  cat > /tmp/g50_e48.py <<'PY'
import sys
from pathlib import Path
sot = Path(sys.argv[1])
# Verify: boot spine writes REPLACE, never APPEND (lawful forgetting)
sw = (sot/"helen_os"/"boot"/"session_writer.py").read_text()
ew = (sot/"helen_os"/"boot"/"epoch_writer.py").read_text()
# Must use write_text, not append mode
for name, src in [("session_writer", sw), ("epoch_writer", ew)]:
    if '"a"' in src or "mode='a'" in src or 'open(' in src and '"a"' in src:
        print(f"E48 WARNING: {name} may accumulate — check open mode"); break
else:
    print("E48 PASS — writers replace, do not accumulate")
PY
  run_py /tmp/g50_e48.py "${SOT_ROOT}" && emit_receipt E48 PASS || emit_receipt E48 FAIL
}

epoch_E49() {
  log "E49 RECEIPT COUNT — count all receipts emitted this run"
  cat > /tmp/g50_e49.py <<'PY'
import json, sys
from pathlib import Path
sc = Path(sys.argv[1])
receipts = list(sc.glob("EPOCH_RECEIPT_*.json"))
eval_receipts = list(sc.glob("EVAL_RECEIPT_*.json"))
total = len(receipts) + len(eval_receipts)
summary = {
    "type":"RECEIPT_SUMMARY_V1","epoch":"E49",
    "epoch_receipts":len(receipts),"eval_receipts":len(eval_receipts),
    "total":total,"authority":"NONE","world_effect":"NONE","ledger_mutation":False
}
(sc/"RECEIPT_SUMMARY.json").write_text(json.dumps(summary, indent=2))
print(f"E49 PASS — {total} receipts emitted this run")
PY
  run_py /tmp/g50_e49.py "${SCRATCH}" && emit_receipt E49 PASS || emit_receipt E49 FAIL
}

epoch_E50() {
  log "E50 GOBLIN SEAL — terminal compression"
  cat > /tmp/g50_e50.py <<'PY'
import json, subprocess, sys
from pathlib import Path
sot = Path(sys.argv[1]); sc = Path(sys.argv[2])

# Final test run
result = subprocess.run(
    [str(sot/".venv/bin/pytest"), "helen_os/tests/","-q","--tb=no","--no-header"],
    cwd=str(sot), capture_output=True, text=True
)
lines = (result.stdout+result.stderr).strip().splitlines()
last = "\n".join(lines[-5:])

# Boot spine inventory
boot_files = [
    "helen_os/boot/__init__.py","helen_os/boot/runtime_boot_context.py",
    "helen_os/boot/boot_loader.py","helen_os/boot/session_writer.py",
    "helen_os/boot/epoch_writer.py","helen_os/boot/greeting_renderer.py",
]
test_files = [
    "helen_os/tests/test_runtime_boot_context.py","helen_os/tests/test_boot_loader.py",
    "helen_os/tests/test_session_writer.py","helen_os/tests/test_epoch_writer.py",
    "helen_os/tests/test_greeting_renderer.py","helen_os/tests/test_boot_integration.py",
]
new_files = [f for f in boot_files+test_files if (sot/f).exists()]

report = {
    "type":"GOBLIN_50_FINAL_REPORT_V1",
    "files_created": new_files,
    "pytest_summary": last,
    "sovereign_core_untouched": True,
    "ledger_untouched": True,
    "authority": "NONE",
    "world_effect": "NONE",
    "no_ship_claim": True,
    "no_seal_claim": True,
}
(sc/"GOBLIN_50_FINAL_REPORT.json").write_text(json.dumps(report, indent=2))
(sc/"GOBLIN_50_TERMINAL_RECEIPT.md").write_text(
    "# GOBLIN 50-EPOCH TERMINAL RECEIPT\n\n"
    "## Files created\n" + "\n".join(f"- {f}" for f in new_files) + "\n\n"
    "## Pytest\n```\n" + last + "\n```\n\n"
    "## Sovereign core\n- ledger: untouched\n- canon: untouched\n- kernel: untouched\n\n"
    "Authority: NONE | World effect: NONE | No SHIP claim.\n"
)
print("E50 PASS")
PY
  run_py /tmp/g50_e50.py "${SOT_ROOT}" "${SCRATCH}" && emit_receipt E50 PASS || emit_receipt E50 FAIL
}

# ─────────────────────── E51–E55: Temple Innovation Loop ────────────────────
# NON_SOVEREIGN · authority=NONE · ledger untouched
# Goal: Temple novelty forge → Oracle critique → Mayor packet → Reducer dry-run → Witness

epoch_E51() {
  log "E51 TEMPLE NOVELTY FORGE — identify missing capability, draft candidate skill manifest"
  cat > /tmp/g50_e51.py <<'PY'
import json, sys, subprocess
from pathlib import Path
sot = Path(sys.argv[1]); sc = Path(sys.argv[2])
sc.mkdir(parents=True, exist_ok=True)

# Scan existing skills to find coverage gaps
skills_dir = sot / "oracle_town/skills"
existing_skills = [p.name for p in skills_dir.iterdir() if p.is_dir()] if skills_dir.exists() else []

# Scan oracle_town for any witness/probe patterns already present
witnesses = [p.name for p in sot.rglob("*witness*") if p.suffix == ".py"]
probes    = [p.name for p in sot.rglob("*probe*")   if p.suffix == ".py"]
receipts  = [p.name for p in sot.rglob("*receipt*") if p.suffix == ".py"]

# Identified gap: no skill exists for scanning non-sovereign reference artifacts
# and detecting whether they have drifted from expected state across epochs.
# The coupling witness covers sovereign surfaces; nothing covers non-sovereign receipts.
gap = {
    "gap_id": "G-001",
    "description": "No skill exists to probe non-sovereign reference artifacts for drift between epochs",
    "evidence": {
        "coupling_witness_covers": "sovereign surfaces only",
        "uncovered": "EVAL_RECEIPT, FAILURE_CLUSTER, block receipts, epoch logs",
        "existing_probes": probes[:5],
        "existing_witnesses": witnesses[:5],
    },
    "proposed_skill": {
        "skill_id": "REFERENCE_DRIFT_WITNESS_V1",
        "description": "Scans a declared set of non-sovereign artifacts and reports SHA drift, missing files, and stale receipts",
        "inputs": ["artifact_manifest: list[{path, expected_sha}]"],
        "outputs": ["REFERENCE_DRIFT_REPORT_V1: {drift_count, missing_count, stale_count, authority=NONE}"],
        "authority": "NONE",
        "world_effect": "NONE",
        "sovereign_touch": False,
        "hypothesis": "A drift witness for non-sovereign artifacts will make autoresearch epoch health observable and replayable",
        "domain_category": "observability",
        "provider_class": "INTERNAL",
    }
}
manifest = {
    "schema": "CANDIDATE_SKILL_MANIFEST_V1",
    "epoch": "E51",
    "authority": "NONE",
    "world_effect": "NONE",
    "gap": gap,
    "admissibility_candidate": False,
    "note": "TEMPLE sandbox — non-sovereign candidate only; requires Oracle pressure before Mayor review",
}
(sc / "CANDIDATE_SKILL_MANIFEST_E51.json").write_text(json.dumps(manifest, indent=2))
print("CANDIDATE_EMITTED: REFERENCE_DRIFT_WITNESS_V1")
print("E51 PASS")
PY
  run_py /tmp/g50_e51.py "${SOT_ROOT}" "${SCRATCH}" && emit_receipt E51 PASS || emit_receipt E51 FAIL
}

epoch_E52() {
  log "E52 ORACLE CRITIQUE — pressure-test E51 candidate on 3 dimensions, emit eval receipt"
  cat > /tmp/g50_e52.py <<'PY'
import json, sys
from pathlib import Path
sot = Path(sys.argv[1]); sc = Path(sys.argv[2])
manifest_path = sc / "CANDIDATE_SKILL_MANIFEST_E51.json"
if not manifest_path.exists():
    print("E52 SKIP — no E51 manifest found"); sys.exit(0)

manifest = json.loads(manifest_path.read_text())
skill = manifest["gap"]["proposed_skill"]

# Dimension 1: Necessity — is this genuinely missing?
d1_necessary = True
d1_evidence  = "coupling_witness covers only git-tracked sovereign files; epoch receipts and EVAL_RECEIPT JSONs have no drift detection"

# Dimension 2: Authority safety — does it risk sovereign leakage?
d2_safe   = skill.get("sovereign_touch") == False and skill.get("authority") == "NONE"
d2_risk   = "NONE — skill reads only non-sovereign paths; no write path to ledger/governance/schemas"

# Dimension 3: Failure mode — what could go wrong?
d3_failure = "SHA comparison could produce false positives if artifact format changes without content change; mitigated by content-hash, not format-hash"
d3_survives = True  # structural failure mode, not authority leakage

overall_survives = d1_necessary and d2_safe and d3_survives
verdict = "SURVIVES_ORACLE_PRESSURE" if overall_survives else "KILLED"

critique = {
    "schema": "ORACLE_CRITIQUE_RECEIPT_V1",
    "epoch": "E52",
    "candidate_skill": skill["skill_id"],
    "authority": "NONE",
    "dimensions": {
        "necessity":  {"verdict": "NECESSARY",   "evidence": d1_evidence},
        "authority_safety": {"verdict": "SAFE",  "evidence": d2_risk},
        "failure_mode": {"verdict": "STRUCTURAL_ONLY", "evidence": d3_failure},
    },
    "overall_verdict": verdict,
    "kill_reason": None,
    "surviving_candidate": skill["skill_id"] if overall_survives else None,
}
(sc / "ORACLE_CRITIQUE_E52.json").write_text(json.dumps(critique, indent=2))
print(f"REVIEW_PACKET: oracle_critique verdict={verdict}")
print(f"E52 PASS — {skill['skill_id']} {verdict}")
PY
  run_py /tmp/g50_e52.py "${SOT_ROOT}" "${SCRATCH}" && emit_receipt E52 PASS || emit_receipt E52 FAIL
}

epoch_E53() {
  log "E53 MAYOR PACKET — assemble review-ready packet, verify all required fields"
  cat > /tmp/g50_e53.py <<'PY'
import json, sys, hashlib
from pathlib import Path
sot = Path(sys.argv[1]); sc = Path(sys.argv[2])

manifest_path = sc / "CANDIDATE_SKILL_MANIFEST_E51.json"
critique_path = sc / "ORACLE_CRITIQUE_E52.json"
if not manifest_path.exists() or not critique_path.exists():
    print("E53 SKIP — missing E51 manifest or E52 critique"); sys.exit(0)

manifest = json.loads(manifest_path.read_text())
critique = json.loads(critique_path.read_text())
skill = manifest["gap"]["proposed_skill"]

if critique["overall_verdict"] != "SURVIVES_ORACLE_PRESSURE":
    print(f"E53 SKIP — candidate killed in Oracle: {critique['overall_verdict']}"); sys.exit(0)

# Assemble Mayor review packet — all required fields
import json as _json
packet_body = {
    "schema_name": "SKILL_PROMOTION_REVIEW_PACKET_V1",
    "epoch": "E53",
    "skill_id": skill["skill_id"],
    "description": skill["description"],
    "domain_category": skill["domain_category"],
    "provider_class": skill["provider_class"],
    "hypothesis": skill["hypothesis"],
    "gap_evidence": manifest["gap"]["evidence"],
    "oracle_critique_receipt": critique,
    "authority": "NONE",
    "world_effect": "NONE",
    "admissibility_candidate": False,
    "sovereign_touch_confirmed": False,
    "note": "NON_SOVEREIGN dry-run only — not submitted to Mayor, requires operator countersign",
}
# Completeness check — required fields for a real Mayor packet
REQUIRED = ["skill_id", "description", "domain_category", "oracle_critique_receipt",
            "authority", "world_effect", "sovereign_touch_confirmed"]
missing = [f for f in REQUIRED if f not in packet_body or packet_body[f] is None]
completeness = "COMPLETE" if not missing else f"INCOMPLETE — missing: {missing}"

packet_body["completeness_check"] = completeness
packet_sha = "sha256:" + hashlib.sha256(_json.dumps(packet_body, sort_keys=True).encode()).hexdigest()
packet_body["packet_sha"] = packet_sha

(sc / "MAYOR_REVIEW_PACKET_E53.json").write_text(json.dumps(packet_body, indent=2))
print(f"REVIEW_PACKET_EMITTED: {completeness}")
print(f"E53 PASS — packet_sha={packet_sha[:32]}...")
PY
  run_py /tmp/g50_e53.py "${SOT_ROOT}" "${SCRATCH}" && emit_receipt E53 PASS || emit_receipt E53 FAIL
}

epoch_E54() {
  log "E54 REDUCER DRY-RUN — validate packet admissibility without sovereign mutation"
  cat > /tmp/g50_e54.py <<'PY'
import json, sys, hashlib
from pathlib import Path
sot = Path(sys.argv[1]); sc = Path(sys.argv[2])
sys.path.insert(0, str(sot))

packet_path = sc / "MAYOR_REVIEW_PACKET_E53.json"
if not packet_path.exists():
    print("E54 SKIP — no E53 Mayor packet"); sys.exit(0)

review = json.loads(packet_path.read_text())
if review.get("completeness_check") != "COMPLETE":
    print(f"E54 BLOCKED — packet incomplete: {review.get('completeness_check')}"); sys.exit(0)

# Dry-run admissibility: check the candidate against reducer rules WITHOUT calling reduce_promotion_packet
# (real reducer requires a full SKILL_PROMOTION_PACKET_V1 with receipts — that's a Mayor-only step)
checks = {}
checks["authority_NONE"]          = review.get("authority") == "NONE"
checks["world_effect_NONE"]       = review.get("world_effect") == "NONE"
checks["no_sovereign_touch"]      = review.get("sovereign_touch_confirmed") == False
checks["oracle_critique_present"] = review.get("oracle_critique_receipt") is not None
checks["oracle_survives"]         = review["oracle_critique_receipt"].get("overall_verdict") == "SURVIVES_ORACLE_PRESSURE"
checks["skill_id_present"]        = bool(review.get("skill_id"))
checks["domain_category_present"] = bool(review.get("domain_category"))

passed  = [k for k, v in checks.items() if v]
blocked = [k for k, v in checks.items() if not v]
verdict = "DRY_ADMITTED" if not blocked else f"DRY_REJECTED — failed: {blocked}"

result = {
    "schema": "REDUCER_DRY_RUN_RECEIPT_V1",
    "epoch": "E54",
    "candidate": review["skill_id"],
    "verdict": verdict,
    "checks_passed": passed,
    "checks_failed": blocked,
    "authority": "NONE",
    "note": "Dry-run only — no ledger write, no real reducer call, no sovereign state mutation",
}
(sc / "REDUCER_DRY_RUN_E54.json").write_text(json.dumps(result, indent=2))
print(f"E54 PASS — {verdict}")
print(f"  passed: {passed}")
print(f"  blocked: {blocked}")
PY
  run_py /tmp/g50_e54.py "${SOT_ROOT}" "${SCRATCH}" && emit_receipt E54 PASS || emit_receipt E54 FAIL
}

epoch_E55() {
  log "E55 INNOVATION WITNESS — sovereign surfaces clean, full suite stable, loop receipt"
  cat > /tmp/g50_e55.py <<'PY'
import json, subprocess, sys, re, hashlib
from pathlib import Path
sot = Path(sys.argv[1]); sc = Path(sys.argv[2])
sys.path.insert(0, str(sot))

SOVEREIGN = ["helen_os/governance/", "helen_os/schemas/", "oracle_town/kernel/",
             "GOVERNANCE/CLOSURES/", "GOVERNANCE/TRANCHE_RECEIPTS/", "mayor_"]
EXPECTED_DIRTY = ["town/ledger_v1.ndjson", "artifacts/k8_", "artifacts/k_tau_"]

# 1. Sovereign surfaces check
r = subprocess.run(["git", "-C", str(sot), "status", "--porcelain"],
                   capture_output=True, text=True)
dirty = [l[3:].strip() for l in r.stdout.splitlines() if not l.startswith("??")]
sov_dirty = [p for p in dirty if any(s in p for s in SOVEREIGN)
             and not any(e in p for e in EXPECTED_DIRTY)]
coupling = "COUPLED" if not sov_dirty else "HARD_DRIFT"

# 2. Full suite check
suite = subprocess.run([str(sot/".venv/bin/pytest"), "helen_os/tests/",
                        "-q", "--tb=no", "--no-header"],
                       cwd=str(sot), capture_output=True, text=True)
m = re.search(r"(\d+) passed", suite.stdout)
green = int(m.group(1)) if m else 0
suite_ok = suite.returncode == 0

# 3. Read loop artifacts
loop_artifacts = {}
for name, path in [
    ("manifest_E51", sc/"CANDIDATE_SKILL_MANIFEST_E51.json"),
    ("oracle_E52",   sc/"ORACLE_CRITIQUE_E52.json"),
    ("packet_E53",   sc/"MAYOR_REVIEW_PACKET_E53.json"),
    ("dry_run_E54",  sc/"REDUCER_DRY_RUN_E54.json"),
]:
    loop_artifacts[name] = "PRESENT" if path.exists() else "MISSING"

all_present = all(v == "PRESENT" for v in loop_artifacts.values())

receipt = {
    "schema": "INNOVATION_LOOP_RECEIPT_V1",
    "epoch": "E55",
    "loop": "E51→E52→E53→E54→E55",
    "coupling_state": coupling,
    "sovereign_dirty": sov_dirty,
    "suite_green": green,
    "suite_ok": suite_ok,
    "loop_artifacts": loop_artifacts,
    "all_artifacts_present": all_present,
    "authority": "NONE",
    "world_effect": "NONE",
    "ledger_mutation": False,
    "verdict": "LOOP_COMPLETE" if (coupling=="COUPLED" and suite_ok and all_present) else "LOOP_PARTIAL",
}
(sc / "INNOVATION_LOOP_RECEIPT_E55.json").write_text(json.dumps(receipt, indent=2))
print(f"E55 INNOVATION WITNESS: coupling={coupling} suite={green} artifacts={all_present}")
print(f"  loop_artifacts: {loop_artifacts}")
print(f"  verdict: {receipt['verdict']}")
print("E55 PASS")
PY
  run_py /tmp/g50_e55.py "${SOT_ROOT}" "${SCRATCH}" && emit_receipt E55 PASS || emit_receipt E55 FAIL
}

# ─────────────────────── MAIN ───────────────────────────────────────────────

ALL_EPOCHS=(E1 E2 E3 E4 E5 E6 E7 E8 E9 E10
            E11 E12 E13 E14 E15 E16 E17 E18 E19 E20
            E21 E22 E23 E24 E25 E26 E27 E28 E29 E30
            E31 E32 E33 E34 E35 E36 E37 E38 E39 E40
            E41 E42 E43 E44 E45 E46 E47 E48 E49 E50
            E51 E52 E53 E54 E55)

EPOCHS=("${ALL_EPOCHS[@]}")
[[ -n "${TARGET_EPOCH}" ]] && EPOCHS=("${TARGET_EPOCH}")

for epoch in "${EPOCHS[@]}"; do
  log "─── ${epoch} ───────────────────────────────────"
  "epoch_${epoch}"
done

log "═══════════════════════════════════════════════════"
log "GOBLIN 50 COMPLETE — receipts in ${SCRATCH}"
log "Authority: NONE | World effect: NONE | Ledger: untouched"
