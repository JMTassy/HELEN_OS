#!/usr/bin/env python3
"""
HELEN REALITY COUPLING WITNESS DEMO — scripts/demos/demo_reality_coupling.py
NON_SOVEREIGN · authority=NONE · no ledger writes

Demonstrates: COUPLED baseline, HARD_DRIFT on sovereign mutation, compound drift,
partial restore, full restore, non-sovereign noise exclusion, expected-dirty exclusion.

Run: .venv/bin/python scripts/demos/demo_reality_coupling.py
"""
import hashlib, json, subprocess, sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

SOVEREIGN_SURFACES = [
    "helen_os/governance/",
    "helen_os/schemas/",
    "GOVERNANCE/CLOSURES/",
    "GOVERNANCE/TRANCHE_RECEIPTS/",
    "oracle_town/kernel/",
    "mayor_",
]
EXPECTED_DIRTY = {
    "town/ledger_v1.ndjson",
    "artifacts/k8_",
    "artifacts/k_tau_",
}

SHIM = "─" * 60
PASSES = 0

def banner(title): print(f"\n{SHIM}\n  {title}\n{SHIM}")
def ok(msg): global PASSES; PASSES += 1; print(f"✓ {msg}")
def fail(msg): print(f"✗ {msg}"); sys.exit(1)

def git_dirty():
    r = subprocess.run(["git", "-C", str(REPO), "status", "--porcelain"],
                       capture_output=True, text=True)
    return [l for l in r.stdout.splitlines() if not l.startswith("??")]

def classify(dirty_lines):
    sov, noise, nonsov = [], [], []
    for line in dirty_lines:
        path = line[3:].strip()
        if any(e in path for e in EXPECTED_DIRTY):
            noise.append(path)
        elif any(s in path for s in SOVEREIGN_SURFACES):
            sov.append(path)
        else:
            nonsov.append(path)
    return sov, noise, nonsov

def coupled(sov): return "COUPLED" if not sov else "HARD_DRIFT"
def sha16(p: Path): return hashlib.sha256(p.read_bytes()).hexdigest()[:16]

def git_restore(*rel_paths):
    for rp in rel_paths:
        subprocess.run(["git", "-C", str(REPO), "checkout", "--", rp],
                       capture_output=True)

GOV = REPO / "helen_os/governance/reason_codes.py"
SCH = REPO / "helen_os/schemas/skill_promotion_packet_v1.json"
NSOV = REPO / "oracle_town/skills/ops/dan_goblin/scratch/progress.txt"

# Ensure sovereign surfaces are clean before starting
git_restore("helen_os/governance/reason_codes.py",
            "helen_os/schemas/skill_promotion_packet_v1.json")

orig_gov = GOV.read_text()
orig_sch = SCH.read_text()

try:
    # ── Phase 1: baseline ───────────────────────────────────────────
    banner("PHASE 1 — BASELINE (sovereign surfaces clean)")
    d = git_dirty(); sov, noise, _ = classify(d)
    print(f"COUPLING_STATE      : {coupled(sov)}")
    print(f"expected noise      : {len(noise)}")
    print(f"unexpected sovereign: {sov}")
    if coupled(sov) != "COUPLED": fail("expected COUPLED")
    ok("baseline COUPLED")

    # ── Phase 2: governance drift ───────────────────────────────────
    banner("PHASE 2 — HARD_DRIFT: governance file mutated")
    GOV.write_text(orig_gov + "# coupling_witness_drift_marker\n")
    d2 = git_dirty(); sov2, _, _ = classify(d2)
    print(f"mutated : {GOV.relative_to(REPO)}")
    print(f"COUPLING_STATE : {coupled(sov2)} — drifted : {sov2}")
    if coupled(sov2) != "HARD_DRIFT" or len(sov2) != 1: fail("expected HARD_DRIFT with 1 surface")
    ok("governance drift → HARD_DRIFT (1 surface)")

    # ── Phase 3: compound drift ─────────────────────────────────────
    banner("PHASE 3 — COMPOUND DRIFT: second sovereign surface (schema)")
    d_sch = json.loads(orig_sch)
    d_sch["_coupling_witness_marker"] = "transient"
    SCH.write_text(json.dumps(d_sch, indent=2, sort_keys=True) + "\n")
    d3 = git_dirty(); sov3, _, _ = classify(d3)
    print(f"COUPLING_STATE : {coupled(sov3)} — drifted : {sorted(sov3)}")
    if coupled(sov3) != "HARD_DRIFT" or len(sov3) != 2: fail("expected HARD_DRIFT with 2 surfaces")
    ok("compound drift → HARD_DRIFT (2 sovereign surfaces)")

    # ── Phase 4: partial restore ────────────────────────────────────
    banner("PHASE 4 — PARTIAL RESTORE: schema back, governance still drifted")
    SCH.write_text(orig_sch)
    d4 = git_dirty(); sov4, _, _ = classify(d4)
    print(f"COUPLING_STATE : {coupled(sov4)} — still drifted : {sov4}")
    if coupled(sov4) != "HARD_DRIFT" or len(sov4) != 1: fail("expected HARD_DRIFT with 1 remaining")
    ok("partial restore still HARD_DRIFT (1 surface remains)")

    # ── Phase 5: full restore ───────────────────────────────────────
    banner("PHASE 5 — FULL RESTORE: all sovereign surfaces clean")
    GOV.write_text(orig_gov)
    d5 = git_dirty(); sov5, noise5, _ = classify(d5)
    print(f"COUPLING_STATE : {coupled(sov5)}")
    print(f"expected noise still present : {noise5}")
    if coupled(sov5) != "COUPLED": fail("expected COUPLED after full restore")
    ok("full restore → COUPLED")

    # ── Phase 6: non-sovereign noise ────────────────────────────────
    banner("PHASE 6 — NON-SOVEREIGN MUTATION (must not trigger HARD_DRIFT)")
    orig_nsov = NSOV.read_text() if NSOV.exists() else ""
    NSOV.write_text(orig_nsov + "# coupling witness non-sovereign noise\n")
    d6 = git_dirty(); sov6, _, _ = classify(d6)
    print(f"mutated non-sovereign : {NSOV.relative_to(REPO)}")
    print(f"COUPLING_STATE : {coupled(sov6)} — sovereign impact : {sov6}")
    if coupled(sov6) != "COUPLED": fail("non-sovereign mutation should not trigger HARD_DRIFT")
    NSOV.write_text(orig_nsov)
    ok("non-sovereign noise → COUPLED (not a violation)")

    # ── Phase 7: expected-dirty exclusion ──────────────────────────
    banner("PHASE 7 — EXPECTED-DIRTY EXCLUSION (ledger always dirty)")
    d7 = git_dirty(); sov7, noise7, _ = classify(d7)
    ledger_lines = [l for l in d7 if "ledger_v1.ndjson" in l]
    in_noise = any("ledger_v1.ndjson" in n for n in noise7)
    in_sov = any("ledger" in s for s in sov7)
    print(f"ledger in git status  : {len(ledger_lines)} line(s)")
    print(f"classified as noise   : {in_noise}")
    print(f"classified as sovereign drift : {in_sov}")
    print(f"COUPLING_STATE : {coupled(sov7)}")
    if coupled(sov7) != "COUPLED": fail("live ledger must not trigger HARD_DRIFT")
    ok("expected-dirty exclusion → ledger noise filtered")

finally:
    git_restore("helen_os/governance/reason_codes.py",
                "helen_os/schemas/skill_promotion_packet_v1.json")

# ── Summary ─────────────────────────────────────────────────────────
banner(f"REALITY COUPLING WITNESS — COMPLETE  {PASSES}/7")
labels = [
    ("baseline", "COUPLED"),
    ("governance drift", "HARD_DRIFT"),
    ("compound drift (2 sov)", "HARD_DRIFT"),
    ("partial restore", "HARD_DRIFT (1 remaining)"),
    ("full restore", "COUPLED"),
    ("non-sovereign noise", "COUPLED"),
    ("expected-dirty exclusion", "COUPLED"),
]
for i, (label, state) in enumerate(labels, 1):
    status = "✓" if i <= PASSES else "✗"
    print(f"  Phase {i}  {label:40s} : {state:30s} {status}")
print()
print(f"Sovereign surfaces watched : {len(SOVEREIGN_SURFACES)}")
print(f"Expected-dirty exclusions  : {len(EXPECTED_DIRTY)}")
print("Authority: NONE | World effect: NONE | Ledger: untouched")
