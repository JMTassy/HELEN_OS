#!/usr/bin/env python3
"""
HELEN BOOT RITUAL DEMO — scripts/demos/demo_boot_ritual.py
NON_SOVEREIGN · authority=NONE · no ledger writes

Demonstrates: null-honest boot, warm restart, persistence, corrupt-file resilience.
Run: .venv/bin/python scripts/demos/demo_boot_ritual.py
"""
import json, shutil, sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from helen_os.boot.boot_loader import load_boot_context
from helen_os.boot.session_writer import write_session_log
from helen_os.boot.epoch_writer import write_epoch_state
from helen_os.boot.greeting_renderer import render_greeting

SHIM = "─" * 60
STORAGE = REPO / "storage" / "_demo_boot_ritual"
PASSES = 0

def banner(title): print(f"\n{SHIM}\n  {title}\n{SHIM}")
def ok(msg): global PASSES; PASSES += 1; print(f"✓ {msg}")
def fail(msg): print(f"✗ {msg}"); sys.exit(1)

try:
    # ── Phase 1: cold boot ──────────────────────────────────────────
    banner("PHASE 1 — COLD BOOT (empty storage)")
    shutil.rmtree(STORAGE, ignore_errors=True)
    ctx = load_boot_context(str(STORAGE), boot_time_iso="2026-06-12T10:00:00")
    greeting = render_greeting(ctx)
    assert ctx.loaded_from == "empty", f"expected empty, got {ctx.loaded_from}"
    assert ctx.last_epoch_id() is None
    assert ctx.person_name() is None
    assert "no prior" in greeting.lower() or "fresh" in greeting.lower() or "empty" in greeting.lower()
    print(f"  loaded_from : {ctx.loaded_from}")
    print(f"  greeting    : {greeting.strip()[:80]}…")
    ok("cold boot null-honest")

    # ── Phase 2: write cycle ────────────────────────────────────────
    banner("PHASE 2 — WRITE CYCLE (session + epoch state)")
    STORAGE.mkdir(parents=True, exist_ok=True)
    write_session_log({"session_id": "DEMO-001", "ended_at": "2026-06-12T10:00:00",
                       "open_threads": ["ghost closure resolution", "manifest gate"]},
                      str(STORAGE))
    write_epoch_state({"epoch_id": "E50", "last_result": "GREEN", "pass_count": 584},
                      str(STORAGE))
    assert (STORAGE / "last_session_v1.json").exists()
    assert (STORAGE / "epoch_state_v1.json").exists()
    ok("session + epoch state written")

    # ── Phase 3: warm boot ──────────────────────────────────────────
    banner("PHASE 3 — WARM BOOT (prior context present)")
    ctx2 = load_boot_context(str(STORAGE), boot_time_iso="2026-06-12T11:00:00")
    greeting2 = render_greeting(ctx2)
    assert ctx2.loaded_from == "storage"
    assert ctx2.last_epoch_id() == "E50"
    print(f"  loaded_from : {ctx2.loaded_from}")
    print(f"  last_epoch  : {ctx2.last_epoch_id()}")
    print(f"  greeting    : {greeting2.strip()[:80]}…")
    ok("warm boot loaded prior context")

    # ── Phase 4: persistence verification ──────────────────────────
    banner("PHASE 4 — PERSISTENCE VERIFICATION")
    raw_session = json.loads((STORAGE / "last_session_v1.json").read_text())
    raw_epoch = json.loads((STORAGE / "epoch_state_v1.json").read_text())
    assert raw_session["session_id"] == "DEMO-001"
    assert raw_epoch["epoch_id"] == "E50"
    assert raw_epoch["pass_count"] == 584
    print(f"  session_id  : {raw_session['session_id']}")
    print(f"  epoch_id    : {raw_epoch['epoch_id']}")
    print(f"  pass_count  : {raw_epoch['pass_count']}")
    ok("persisted values match written values")

    # ── Phase 5: corrupt file resilience ───────────────────────────
    banner("PHASE 5 — CORRUPT FILE RESILIENCE")
    (STORAGE / "epoch_state_v1.json").write_text("{INVALID JSON")
    ctx3 = load_boot_context(str(STORAGE), boot_time_iso="2026-06-12T12:00:00")
    assert ctx3.loaded_from in ("partial", "empty", "storage"), f"bad state: {ctx3.loaded_from}"
    assert ctx3.last_epoch_id() is None or ctx3.loaded_from == "storage"
    print(f"  loaded_from after corrupt file : {ctx3.loaded_from}")
    ok("corrupt file does not crash — graceful degradation")

finally:
    shutil.rmtree(STORAGE, ignore_errors=True)

# ── Summary ─────────────────────────────────────────────────────────
banner(f"BOOT RITUAL DEMO — COMPLETE  {PASSES}/5")
for i, label in enumerate([
    "cold boot null-honest",
    "session + epoch state written",
    "warm boot loaded prior context",
    "persisted values match written values",
    "corrupt file does not crash",
], 1):
    status = "✓" if i <= PASSES else "✗"
    print(f"  Phase {i}  {label:45s} : {status}")
print()
print("Authority: NONE | World effect: NONE | Ledger: untouched")
