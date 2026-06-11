#!/usr/bin/env python3
"""
validate_conquest_garden.py — GOBLIN_GARDEN_CONQUEST validator.

NON_SOVEREIGN. authority=false. No ledger writes. No sovereign interactions.
Validates that all conquest garden artifacts stay within authority boundary.

Usage:
    python validate_conquest_garden.py
    python validate_conquest_garden.py --json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

GARDEN_ROOT = Path(__file__).parent
REPO_ROOT = GARDEN_ROOT.parent.parent.parent

FORBIDDEN_STATUSES = {"ADMITTED", "CANON", "SOVEREIGN", "SHIPPED"}
FORBIDDEN_SOVEREIGN_KEYWORDS = {
    "cum_hash", "payload_hash", "ledger_entry",
    "oracle_town/kernel", "helen_os/governance", "helen_os/schemas",
    "town/ledger_v1", "write_gate_approval", "ndjson_writer",
}
VALID_CLAIM_TYPES = {
    "metaphor", "simulation", "draft_doctrine", "world_model",
    "quest", "bulletin", "validator", "receipt",
}
EXPECTED_EPOCH_COUNT = 25
SIMULATION_MARKERS = {"simulation_only", "SIMULATION_ONLY", "DREAM_OF_CONQUEST"}


def check_manifest() -> list[str]:
    errors = []
    mf = GARDEN_ROOT / "conquest_manifest.json"
    if not mf.exists():
        errors.append("MISSING: conquest_manifest.json")
        return errors
    try:
        m = json.loads(mf.read_text())
    except Exception as e:
        errors.append(f"PARSE_ERROR: conquest_manifest.json: {e}")
        return errors
    if m.get("authority") is not False:
        errors.append("MANIFEST: authority must be false")
    if m.get("sovereign") is not False:
        errors.append("MANIFEST: sovereign must be false")
    if m.get("status") in FORBIDDEN_STATUSES:
        errors.append(f"MANIFEST: forbidden status {m.get('status')!r}")
    if m.get("dream_world_sovereign") is not False:
        errors.append("MANIFEST: dream_world_sovereign must be false")
    if m.get("dream_world_simulation_only") is not True:
        errors.append("MANIFEST: dream_world_simulation_only must be true")
    epoch_map = m.get("epochs", {})
    if len(epoch_map) != EXPECTED_EPOCH_COUNT:
        errors.append(
            f"MANIFEST: expected {EXPECTED_EPOCH_COUNT} epoch entries, "
            f"got {len(epoch_map)}"
        )
    return errors


def check_receipts() -> list[str]:
    errors = []
    receipt_dir = GARDEN_ROOT / "receipts"
    if not receipt_dir.exists():
        return ["MISSING: receipts/ directory"]

    for i in range(1, EXPECTED_EPOCH_COUNT + 1):
        fname = f"epoch_{i:03d}.json"
        rf = receipt_dir / fname
        if not rf.exists():
            errors.append(f"MISSING_RECEIPT: {fname}")
            continue
        try:
            r = json.loads(rf.read_text())
        except Exception as e:
            errors.append(f"PARSE_ERROR: {fname}: {e}")
            continue
        if r.get("authority") is not False:
            errors.append(f"RECEIPT {fname}: authority must be false")
        if r.get("sovereign") is not False:
            errors.append(f"RECEIPT {fname}: sovereign must be false")
        if r.get("status") in FORBIDDEN_STATUSES:
            errors.append(f"RECEIPT {fname}: forbidden status {r.get('status')!r}")
        for key in FORBIDDEN_SOVEREIGN_KEYWORDS:
            if key in str(r):
                errors.append(f"RECEIPT {fname}: contains sovereign keyword {key!r}")
    return errors


def check_content_files() -> list[str]:
    errors = []
    content_dirs = [
        GARDEN_ROOT / "world_model",
        GARDEN_ROOT / "doctrines",
        GARDEN_ROOT / "epochs",
    ]
    for d in content_dirs:
        if not d.exists():
            continue
        for cf in sorted(d.glob("*.md")):
            content = cf.read_text()
            has_claim_type = any(
                f"CLAIM_TYPE: {ct}" in content for ct in VALID_CLAIM_TYPES
            )
            if not has_claim_type:
                errors.append(
                    f"{cf.parent.name}/{cf.name}: missing CLAIM_TYPE "
                    f"(one of {sorted(VALID_CLAIM_TYPES)})"
                )
            for kw in FORBIDDEN_SOVEREIGN_KEYWORDS:
                if kw in content:
                    errors.append(
                        f"{cf.parent.name}/{cf.name}: contains sovereign keyword {kw!r}"
                    )
    return errors


def check_dream_world_marked_simulation() -> list[str]:
    errors = []
    boundary_file = GARDEN_ROOT / "world_model" / "dream_boundary.md"
    if not boundary_file.exists():
        return ["MISSING: world_model/dream_boundary.md"]
    content = boundary_file.read_text()
    has_simulation_marker = any(m in content for m in SIMULATION_MARKERS)
    if not has_simulation_marker:
        errors.append(
            "dream_boundary.md: missing simulation-only marker "
            f"(one of {SIMULATION_MARKERS})"
        )
    if "AUTHORITY: false" not in content and "authority.*false" not in content.lower():
        errors.append("dream_boundary.md: AUTHORITY: false not found")
    return errors


def check_forbidden_claims_absent() -> list[str]:
    errors = []
    for p in GARDEN_ROOT.rglob("*.json"):
        if p.name == "conquest_manifest.json":
            continue
        try:
            content = p.read_text()
        except Exception:
            continue
        for kw in FORBIDDEN_SOVEREIGN_KEYWORDS:
            if kw in content:
                rel = p.relative_to(GARDEN_ROOT)
                errors.append(f"{rel}: contains sovereign keyword {kw!r}")
    return errors


def check_garden_conquest_md() -> list[str]:
    errors = []
    gc = GARDEN_ROOT / "GARDEN_CONQUEST.md"
    if not gc.exists():
        return ["MISSING: GARDEN_CONQUEST.md"]
    content = gc.read_text()
    if "CLAIM_TYPE:" not in content:
        errors.append("GARDEN_CONQUEST.md: missing CLAIM_TYPE")
    if "authority.*false" not in content.lower() and "AUTHORITY: false" not in content:
        errors.append("GARDEN_CONQUEST.md: AUTHORITY: false not found")
    if "NOT_LEDGER" not in content and "ledger does not move" not in content.lower():
        errors.append("GARDEN_CONQUEST.md: ledger boundary not stated")
    return errors


def check_bulletins() -> list[str]:
    errors = []
    b_dir = GARDEN_ROOT / "bulletins"
    if not b_dir.exists():
        return ["MISSING: bulletins/ directory"]
    bulletin_files = list(b_dir.glob("*.txt"))
    if not bulletin_files:
        errors.append("BULLETINS: no bulletin files found")
        return errors
    try:
        sys.path.insert(0, str(REPO_ROOT))
        from tools.wulmoji_ledger_validator import validate_bulletin
        for bf in sorted(bulletin_files):
            results = validate_bulletin(bf.read_text())
            for r in results:
                if not r.ok:
                    for e in r.errors:
                        errors.append(f"BULLETIN {bf.name} line {r.line_num}: {e}")
    except ImportError:
        errors.append(
            "WARNING: wulmoji_ledger_validator not found — bulletin format unchecked"
        )
    return errors


def run_validation() -> tuple[bool, list[str]]:
    all_errors: list[str] = []
    all_errors.extend(check_manifest())
    all_errors.extend(check_receipts())
    all_errors.extend(check_content_files())
    all_errors.extend(check_dream_world_marked_simulation())
    all_errors.extend(check_forbidden_claims_absent())
    all_errors.extend(check_garden_conquest_md())
    all_errors.extend(check_bulletins())
    return len(all_errors) == 0, all_errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate Goblin Garden Conquest"
    )
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    ok, errors = run_validation()

    if args.as_json:
        print(json.dumps({
            "ok": ok,
            "authority": False,
            "sovereign": False,
            "dream_world_simulation_only": True,
            "errors": errors,
            "error_count": len(errors),
        }, ensure_ascii=False, indent=2))
    else:
        if ok:
            print("✅ Conquest garden valid — all checks pass")
        else:
            print(f"❌ Conquest garden invalid — {len(errors)} error(s):")
            for e in errors:
                print(f"  ERROR: {e}")

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
