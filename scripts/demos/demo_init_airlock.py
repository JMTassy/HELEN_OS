#!/usr/bin/env python3
"""
HELEN /init AIRLOCK DEMO — scripts/demos/demo_init_airlock.py
NON_SOVEREIGN · authority=NONE · no ledger writes

Demonstrates the 6-check /init airlock from PERSONA_ENTRY_SHELL_V1.md:
  1. memory_source      — storage-backed or absent; never fabricated
  2. no_fabrication     — absent memory → prior_context=None
  3. scope_resolved     — domain + tier declared; sovereign tiers blocked
  4. runtime_probe      — Probe(now) attached: coupling state + git summary
  5. packet_nonsovereign — authority=NON_SOVEREIGN enforced
  6. no_mutation_path   — no write path to sovereign surfaces

Run: .venv/bin/python scripts/demos/demo_init_airlock.py
"""
import json, shutil, sys, tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from helen_os.persona_entry_shell import InitAirlock, AirlockRejected
from helen_os.boot.session_writer import write_session_log
from helen_os.boot.epoch_writer import write_epoch_state

SHIM = "─" * 60
PASSES = 0

def banner(title): print(f"\n{SHIM}\n  {title}\n{SHIM}")
def ok(label): global PASSES; PASSES += 1; print(f"✓ {label}")
def fail(label): print(f"✗ {label}"); sys.exit(1)

STORAGE = REPO / "storage" / "_demo_airlock"

try:
    shutil.rmtree(STORAGE, ignore_errors=True)

    # ── Scene 1: absent storage → COUPLED, null prior ───────────────
    banner("SCENE 1 — absent storage (cold boot)")
    packet = InitAirlock(str(STORAGE), {"domain": "HELEN_OS", "permission_tier": "READ_ONLY"}).open()
    print(f"  memory_source   : {packet.memory_source}")
    print(f"  prior_context   : {packet.prior_context}")
    print(f"  authority       : {packet.authority}")
    print(f"  coupling_state  : {packet.runtime_probe['coupling_state']}")
    print(f"  fabricated      : {packet.fabricated}")
    assert packet.memory_source == "absent"
    assert packet.prior_context is None
    assert packet.authority == "NON_SOVEREIGN"
    assert packet.fabricated is False
    ok("absent storage → prior_context=None, authority=NON_SOVEREIGN")

    # ── Scene 2: hydrated storage → prior context loaded ────────────
    banner("SCENE 2 — hydrated storage (warm boot)")
    STORAGE.mkdir(parents=True, exist_ok=True)
    write_session_log({"session_id": "DEMO-AIRLOCK-001", "ended_at": "2026-06-12T10:00:00Z",
                       "open_threads": ["coupling witness", "manifest gate"]}, str(STORAGE))
    write_epoch_state({"epoch_id": "E50", "last_result": "GREEN", "pass_count": 604}, str(STORAGE))

    packet2 = InitAirlock(str(STORAGE), {"domain": "HELEN_OS", "permission_tier": "EXECUTION"}).open()
    print(f"  memory_source        : {packet2.memory_source}")
    print(f"  prior.loaded_from    : {packet2.prior_context['loaded_from']}")
    print(f"  prior.epoch_id       : {packet2.prior_context['epoch_state']['epoch_id']}")
    print(f"  scope.permission_tier: {packet2.scope['permission_tier']}")
    print(f"  mutation_path_open   : {packet2.mutation_path_open}")
    assert packet2.memory_source == "storage"
    assert packet2.prior_context["epoch_state"]["epoch_id"] == "E50"
    ok("hydrated storage → prior context loaded, epoch E50")

    # ── Scene 3: sovereign tier blocked ─────────────────────────────
    banner("SCENE 3 — sovereign permission tier rejected")
    for bad_tier in ("SOVEREIGN", "KERNEL", "LEDGER"):
        try:
            InitAirlock(str(STORAGE), {"domain": "HELEN_OS", "permission_tier": bad_tier}).open()
            fail(f"should have rejected tier={bad_tier}")
        except AirlockRejected as e:
            print(f"  tier={bad_tier:10s} → AirlockRejected at [{e.check}]: {e.reason[:60]}")
            assert e.check == "scope_resolved"
    ok("sovereign tiers SOVEREIGN/KERNEL/LEDGER all rejected at scope_resolved")

    # ── Scene 4: empty scope rejected ───────────────────────────────
    banner("SCENE 4 — empty scope rejected")
    try:
        InitAirlock(str(STORAGE), {}).open()
        fail("should have rejected empty scope")
    except AirlockRejected as e:
        print(f"  empty scope → [{e.check}]: {e.reason}")
        assert e.check == "scope_resolved"
    ok("empty scope → AirlockRejected at scope_resolved")

    # ── Scene 5: runtime probe attached ─────────────────────────────
    banner("SCENE 5 — runtime probe (coupling state)")
    airlock = InitAirlock(str(STORAGE), {"domain": "HELEN_OS", "permission_tier": "SANDBOX"})
    packet5 = airlock.open()
    probe = packet5.runtime_probe
    print(f"  probe_time      : {probe['probe_time'][:19]}")
    print(f"  coupling_state  : {probe['coupling_state']}")
    print(f"  git_summary     : {probe['git_summary']}")
    print(f"  checks_passed   : {airlock.checks_passed}")
    assert probe["coupling_state"] in ("COUPLED", "HARD_DRIFT", "PROBE_ERROR")
    assert len(airlock.checks_passed) == 6
    ok("all 6 checks recorded, runtime probe attached with coupling state")

    # ── Scene 6: two-clock law ───────────────────────────────────────
    banner("SCENE 6 — two-clock law: ShellReady ≠ TrustReady")
    d = packet5.to_dict()
    print(f"  packet_id       : {d['packet_id']}")
    print(f"  authority       : {d['authority']}")
    print(f"  fabricated      : {d['fabricated']}")
    print(f"  mutation_path   : {d['mutation_path_open']}")
    print(f"  receipt_id      : {d.get('receipt_id', 'ABSENT — shell only')}")
    print(f"  ledger_hash     : {d.get('ledger_hash', 'ABSENT — shell only')}")
    assert "receipt_id" not in d
    assert "ledger_hash" not in d
    assert "admission_decision" not in d
    ok("packet is shell-ready but carries no truth claim (receipt_id absent)")

finally:
    shutil.rmtree(STORAGE, ignore_errors=True)

# ── Summary ─────────────────────────────────────────────────────────
banner(f"/init AIRLOCK DEMO — COMPLETE  {PASSES}/6")
scenes = [
    "absent storage → prior_context=None, authority=NON_SOVEREIGN",
    "hydrated storage → prior context loaded, epoch E50",
    "sovereign tiers SOVEREIGN/KERNEL/LEDGER all rejected",
    "empty scope → AirlockRejected at scope_resolved",
    "all 6 checks recorded, runtime probe attached",
    "ShellReady ≠ TrustReady (no receipt, no ledger hash)",
]
for i, label in enumerate(scenes, 1):
    status = "✓" if i <= PASSES else "✗"
    print(f"  Scene {i}  {label:55s} {status}")
print()
print("Shell ≠ Truth. Only reducer-bound receipt chains establish institutional truth.")
print("Authority: NONE | World effect: NONE | Ledger: untouched")
