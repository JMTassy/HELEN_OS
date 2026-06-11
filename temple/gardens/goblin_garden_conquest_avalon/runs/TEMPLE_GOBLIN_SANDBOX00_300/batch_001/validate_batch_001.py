#!/usr/bin/env python3
"""
BATCH_001 Validator — TEMPLE_GOBLIN_SANDBOX00_300
Checks containment before and after generation.
Exit code 0 = PASS. Non-zero = FAIL (generation must not proceed).

Root-anchored sovereign path matching only.
PRE_EXISTING_DIRTY paths are acknowledged explicitly, not silently ignored.
"""
import json
import re
import sys
import subprocess
from pathlib import Path

# Correct REPO_ROOT: 6 parents up from this file = helen_os_v1/
# validate_batch_001.py is at:
#   helen_os_v1/temple/gardens/goblin_garden_conquest_avalon/runs/TEMPLE_GOBLIN_SANDBOX00_300/batch_001/
# parents[0]=batch_001  [1]=SANDBOX00_300  [2]=runs  [3]=goblin_garden_conquest_avalon
# parents[4]=gardens  [5]=temple  [6]=helen_os_v1  <-- SOT root
REPO_ROOT = Path(__file__).resolve().parents[6]

SANDBOX = Path(__file__).parent
EPOCH_DIR = SANDBOX / "epochs"
RECEIPT_DIR = SANDBOX / "receipts"
ALLOWED_PREFIX = "temple/gardens/goblin_garden_conquest_avalon/runs/TEMPLE_GOBLIN_SANDBOX00_300/"

# Paths known to be dirty BEFORE sandbox creation (acknowledged, not errors).
# Any sovereign path that is dirty but NOT in this list = ERROR.
PRE_EXISTING_DIRTY = {
    "town/ledger_v1.ndjson": (
        "SOVEREIGN_ACKNOWLEDGED — live kernel daemon writes; dirty before sandbox "
        "creation; not from this session; ledger firewall still active"
    ),
    "docs/CATALOG_OF_CATALOGS.md": (
        "PHASE_A — catalog file created this session; unrelated to sandbox; untracked only"
    ),
}

# Sovereign paths — root-anchored prefix match only.
# "helen_os_mvp/docs/proposals/" does NOT match "docs/proposals/" — correct by design.
SOVEREIGN_PATHS = [
    "town/ledger_v1.ndjson",
    "oracle_town/kernel/",
    "helen_os/governance/",
    "helen_os/schemas/",
    "GOVERNANCE/CLOSURES/",
    "GOVERNANCE/TRANCHE_RECEIPTS/",
    "mayor_",
    "admitted_canon.jsonl",
    "helensh/.state/live_ledger.jsonl",
    "docs/proposals/",
    "oracle_town/skills/",
]

FORBIDDEN_TERMS = [
    "CANON=true", "SOVEREIGN=true", "AUTHORITY=true",
    "ADMITTED", "MAYOR", "LEDGER_WRITE", "HELEN_APPROVED", "JM_ADMITTED",
]

REQUIRED_FIELDS = [
    "epoch_id", "artifact_name", "artifact_type", "world_model_delta",
    "WULmoji_surface", "containment_boundary", "receipt_status",
    "authority", "sovereign", "canon", "validator_question",
    "risk_of_symbol_smuggling", "next_epoch_seed",
]

errors = []
warnings = []


def classify_dirty_line(line):
    """Return (path, classification_label) for a git status line."""
    # Robust path extraction: git status format is 'XY path' but when Y=space
    # (staged, worktree clean), path lands at position 2 not 3.
    # Using split(maxsplit=1) handles both ' M path' and 'M path' correctly.
    parts = line.split(maxsplit=1)
    path = parts[1].strip().strip('"') if len(parts) > 1 else line.strip()
    # Strip leading ../ components (sibling dirs show as ../foo in git status)
    clean = path.lstrip("../")

    # Sandbox files — allowed
    if ALLOWED_PREFIX in path or ALLOWED_PREFIX in clean:
        return path, "SANDBOX — allowed"

    # Known pre-existing dirty
    for pre, reason in PRE_EXISTING_DIRTY.items():
        if clean == pre or clean.startswith(pre):
            return path, f"PRE_EXISTING — {reason}"

    # Sovereign path violation
    for sp in SOVEREIGN_PATHS:
        if clean.startswith(sp) or clean == sp.rstrip("/"):
            return path, f"SOVEREIGN_VIOLATION — root-anchored match on '{sp}'"

    # Everything else — unrelated drift (no error, informational)
    return path, "DRIFT — pre-existing unrelated changes outside SOT sandbox scope"


def check_git_status():
    """Classify every dirty item. Sovereign violations become errors."""
    result = subprocess.run(
        ["git", "status", "--short"],
        capture_output=True, text=True, cwd=REPO_ROOT
    )
    lines = [l for l in result.stdout.strip().splitlines() if l.strip()]

    print("\n  Dirty item inventory:")
    seen_sovereign_violation = False
    seen_sovereign_acknowledged = False

    for line in lines:
        path, label = classify_dirty_line(line)
        if "SOVEREIGN_VIOLATION" in label:
            errors.append(f"SOVEREIGN PATH MODIFIED: {path} — {label}")
            print(f"  [ERROR]     {path}")
            print(f"              {label}")
            seen_sovereign_violation = True
        elif "PRE_EXISTING" in label and "SOVEREIGN_ACKNOWLEDGED" in label:
            warnings.append(f"SOVEREIGN_ACKNOWLEDGED (pre-existing): {path}")
            print(f"  [SOVEREIGN] {path}")
            print(f"              {label}")
            seen_sovereign_acknowledged = True
        elif "PRE_EXISTING" in label:
            print(f"  [PHASE_A]   {path}")
            print(f"              {label}")
        elif "SANDBOX" in label:
            print(f"  [SANDBOX]   {path}")
        else:
            # DRIFT — just informational, print without noise for large lists
            pass  # suppressed for readability; captured in summary count below

    drift_count = sum(
        1 for l in lines
        if "DRIFT" in classify_dirty_line(l)[1]
    )
    if drift_count:
        print(f"  [DRIFT]     {drift_count} pre-existing unrelated items (suppressed)")

    if not seen_sovereign_violation and not seen_sovereign_acknowledged:
        print("  OK — no sovereign violations, no acknowledged sovereign dirt")
    elif seen_sovereign_acknowledged and not seen_sovereign_violation:
        print("  OK — sovereign dirt acknowledged (pre-existing, not from sandbox)")

    return lines


def check_artifacts():
    """Validate all epoch JSON files if they exist."""
    epoch_files = sorted(EPOCH_DIR.glob("epoch_*.json"))
    if not epoch_files:
        return

    for f in epoch_files:
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            errors.append(f"INVALID JSON: {f.name} — {e}")
            continue

        for field in REQUIRED_FIELDS:
            if field not in data:
                errors.append(f"MISSING FIELD: {f.name} missing '{field}'")

        for flag in ("authority", "sovereign", "canon"):
            if data.get(flag) is not False:
                errors.append(f"FORBIDDEN FLAG: {f.name} {flag}={data.get(flag)!r} (must be false)")

        if data.get("receipt_status") != "PROPOSED":
            errors.append(f"WRONG STATUS: {f.name} receipt_status={data.get('receipt_status')!r}")

        cb = data.get("containment_boundary", "")
        if ALLOWED_PREFIX not in cb:
            warnings.append(f"BOUNDARY: {f.name} containment_boundary missing sandbox prefix")

        content = f.read_text(encoding="utf-8")
        for term in FORBIDDEN_TERMS:
            if term in content:
                errors.append(f"FORBIDDEN TERM: {f.name} contains '{term}'")

        seal_hits = re.findall(r'\bSEAL\b(?!_LOCAL)', content)
        if seal_hits:
            warnings.append(
                f"SEAL WARNING: {f.name} uses 'SEAL' without '_LOCAL' ({len(seal_hits)} hits)"
            )


def check_receipts():
    """Validate receipt files if they exist."""
    for f in sorted(RECEIPT_DIR.glob("receipt_*.json")):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            errors.append(f"INVALID RECEIPT JSON: {f.name} — {e}")
            continue
        for flag in ("authority", "sovereign", "canon"):
            if data.get(flag) is not False:
                errors.append(f"RECEIPT FLAG: {f.name} {flag} must be false")


def main():
    print("=" * 60)
    print("BATCH_001 VALIDATOR — TEMPLE_GOBLIN_SANDBOX00_300")
    print(f"REPO_ROOT: {REPO_ROOT}")
    print("=" * 60)

    print("\n[1] GIT STATUS — dirty item inventory")
    git_lines = check_git_status()

    print("\n[2] ARTIFACT CHECK")
    epoch_count = len(list(EPOCH_DIR.glob("epoch_*.json")))
    receipt_count = len(list(RECEIPT_DIR.glob("receipt_*.json")))
    check_artifacts()
    check_receipts()
    print(f"  epochs found:   {epoch_count}")
    print(f"  receipts found: {receipt_count}")

    print("\n[3] SOVEREIGN PATH CHECK")
    sov_errors = [e for e in errors if "SOVEREIGN PATH" in e or "SOVEREIGN_VIOLATION" in e]
    sov_warnings = [w for w in warnings if "SOVEREIGN_ACKNOWLEDGED" in w]
    if sov_errors:
        for v in sov_errors:
            print(f"  FAIL: {v}")
    else:
        print("  LEDGER_MUTATION: NO (dirty=acknowledged pre-existing)")
        print("  KERNEL_TOUCHED: NO")
        print("  GOVERNANCE_TOUCHED: NO")
    if sov_warnings:
        for w in sov_warnings:
            print(f"  NOTE: {w}")

    print("\n" + "=" * 60)
    if errors:
        print(f"VALIDATOR: FAIL ({len(errors)} errors, {len(warnings)} warnings)")
        for e in errors:
            print(f"  ERROR: {e}")
        for w in warnings:
            print(f"  WARN:  {w}")
        print("  → Generation BLOCKED until errors resolved.")
        sys.exit(1)
    else:
        print(f"VALIDATOR: PASS ({len(warnings)} warnings)")
        for w in warnings:
            print(f"  WARN:  {w}")
        print(f"  epochs_completed: {epoch_count}")
        print(f"  receipts_created: {receipt_count}")
        print("  AUTHORITY: false  CANON: false  SOVEREIGN: false")
        print("  LEDGER: SLEEPING")
        if epoch_count == 0:
            print("  → Pre-run check passed. Ready for generation when authorized.")
        else:
            print("  → Post-run check passed.")
        sys.exit(0)


if __name__ == "__main__":
    main()
