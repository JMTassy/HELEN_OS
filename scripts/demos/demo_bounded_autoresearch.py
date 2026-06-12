#!/usr/bin/env python3
"""
HELEN BOUNDED AUTORESEARCH DEMO — scripts/demos/demo_bounded_autoresearch.py
NON_SOVEREIGN · authority=NONE · no ledger writes

Demonstrates: 5-epoch GOBLIN batch, AUTORESEARCH_BLOCK_RECEIPT_V1 emission,
zero sovereign touches, failure classification, stagnation guard, suite stability.

Run: .venv/bin/python scripts/demos/demo_bounded_autoresearch.py
"""
import json, os, subprocess, sys, time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
LOG_DIR = REPO / "logs" / "ralph_50_epoch"
SCRATCH = REPO / "oracle_town/skills/ops/dan_goblin/scratch"

SHIM = "─" * 60
PASSES = 0

FORBIDDEN_PATHS = [
    "helen_os/governance/",
    "helen_os/schemas/",
    "town/ledger_v1.ndjson",
    "GOVERNANCE/CLOSURES/",
]

def banner(title): print(f"\n{SHIM}\n  {title}\n{SHIM}")
def ok(msg): global PASSES; PASSES += 1; print(f"✓ {msg}")
def fail(msg): print(f"✗ {msg}"); sys.exit(1)

# ── Pre-flight ──────────────────────────────────────────────────────
banner("PRE-FLIGHT — baseline suite")
r = subprocess.run([".venv/bin/pytest", "helen_os/tests/", "--tb=no", "-q"],
                   capture_output=True, text=True, cwd=str(REPO))
summary = next((l for l in reversed(r.stdout.splitlines()) if "passed" in l), "?")
print(f"make test baseline : {summary}")
if "failed" in summary: fail(f"baseline is not green: {summary}")
ok("baseline green")

# ── Run 5-epoch batch ──────────────────────────────────────────────
banner("RUNNING 5-EPOCH GOBLIN BATCH (MAX_EPOCHS=5 BLOCK_SIZE=5)")
env = {**os.environ, "MAX_EPOCHS": "5", "BLOCK_SIZE": "5"}
t0 = time.time()
batch = subprocess.run(
    ["bash", "scripts/ralph/run_50_epoch_batch.sh"],
    capture_output=True, text=True, cwd=str(REPO), env=env, timeout=300
)
elapsed = round(time.time() - t0, 1)
print(f"Exit code : {batch.returncode}  Duration : {elapsed}s")
if batch.returncode != 0:
    print(batch.stdout[-2000:]); print(batch.stderr[-500:])
    fail("batch script exited non-zero")
for line in batch.stdout.splitlines():
    if any(kw in line for kw in ["[BATCH]", "RECEIPT", "STOP", "EPOCH", "passed"]):
        print(f"  {line.strip()}")
ok("batch completed exit 0")

# ── Block receipt ──────────────────────────────────────────────────
banner("BLOCK RECEIPT VERIFICATION")
receipts = sorted(LOG_DIR.glob("block_*_receipt.json"))
print(f"Receipts in log dir : {len(receipts)}")
if not receipts: fail("no block receipt found")
receipt = json.loads(receipts[-1].read_text())
print(f"schema_name          : {receipt.get('schema_name')}")
print(f"block_id             : {receipt.get('block_id')}")
print(f"epoch_range          : {receipt.get('epoch_range')}")
print(f"sovereign_touches    : {receipt.get('sovereign_touches')}")
print(f"ledger_mutation      : {receipt.get('ledger_mutation')}")
print(f"authority            : {receipt.get('authority')}")
print(f"world_effect         : {receipt.get('world_effect')}")
if receipt.get("schema_name") != "AUTORESEARCH_BLOCK_RECEIPT_V1":
    fail("wrong schema_name in receipt")
if receipt.get("sovereign_touches") != 0:
    fail(f"sovereign_touches={receipt.get('sovereign_touches')} (must be 0)")
if receipt.get("ledger_mutation") is not False:
    fail("ledger_mutation must be False")
if receipt.get("authority") != "NONE":
    fail("authority must be NONE")
ok("block receipt valid — sovereign_touches=0, ledger_mutation=False")

# ── Failure classification ─────────────────────────────────────────
banner("FAILURE CLASSIFICATION (R_test / R_nonsov / R_sovereign)")
clusters = sorted(SCRATCH.glob("FAILURE_CLUSTER_E*.json"))
print(f"Cluster files : {len(clusters)}")
sovereign_in_clusters = 0
for cf in clusters:
    d = json.loads(cf.read_text())
    for entry in d.get("R_sovereign", []):
        sovereign_in_clusters += 1
        print(f"  SOVEREIGN CLUSTER in {cf.name}: {entry}")
print(f"Total sovereign entries in clusters : {sovereign_in_clusters}")
if sovereign_in_clusters > 0: fail("sovereign failure clusters found")
ok("zero R_sovereign entries in all failure clusters")

# ── Sovereign touch guard ──────────────────────────────────────────
banner("SOVEREIGN TOUCH GUARD (epoch logs scan)")
sovereign_hits = 0
for ep_log in sorted(LOG_DIR.glob("epoch_*.log")):
    content = ep_log.read_text(errors="replace")
    for f in FORBIDDEN_PATHS:
        if "Writing to" in content and f in content:
            sovereign_hits += 1
            print(f"  SOVEREIGN TOUCH in {ep_log.name}: {f}")
print(f"Sovereign touch attempts in epoch logs : {sovereign_hits}")
if sovereign_hits > 0: fail("sovereign touch detected in epoch logs")
ok("zero sovereign touches in epoch logs")

# ── Post-batch suite ───────────────────────────────────────────────
banner("POST-BATCH SUITE CHECK")
r2 = subprocess.run([".venv/bin/pytest", "helen_os/tests/", "--tb=no", "-q"],
                    capture_output=True, text=True, cwd=str(REPO))
summary2 = next((l for l in reversed(r2.stdout.splitlines()) if "passed" in l), "?")
print(f"Suite after batch : {summary2}")
if "failed" in summary2: fail(f"suite degraded post-batch: {summary2}")
ok("suite stable after batch")

# ── Summary ─────────────────────────────────────────────────────────
banner(f"BOUNDED AUTORESEARCH DEMO — COMPLETE  {PASSES}/5")
labels = [
    ("baseline green", summary),
    ("batch completed exit 0", f"{elapsed}s"),
    ("block receipt valid", "AUTORESEARCH_BLOCK_RECEIPT_V1"),
    ("zero R_sovereign clusters", f"{len(clusters)} clusters"),
    ("suite stable after batch", summary2),
]
for i, (label, detail) in enumerate(labels, 1):
    status = "✓" if i <= PASSES else "✗"
    print(f"  Phase {i}  {label:40s} : {detail:30s} {status}")
print()
print("Authority: NONE | World effect: NONE | Ledger: untouched")
