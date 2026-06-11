#!/usr/bin/env python3
"""
validate_garden.py — Goblin Meditation Center garden validator.

NON_SOVEREIGN. authority=false. Does not write to ledger.
Validates that all garden artifacts stay within authority boundary.

Usage:
    python validate_garden.py
    python validate_garden.py --json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

GARDEN_ROOT = Path(__file__).parent
FORBIDDEN_STATUSES = {"ADMITTED", "CANON", "SOVEREIGN", "SHIPPED"}
FORBIDDEN_SOVEREIGN_KEYWORDS = {
    "cum_hash", "payload_hash", "seq", "ledger_entry",
    "oracle_town/kernel", "helen_os/governance", "helen_os/schemas",
    "town/ledger_v1",
}
VALID_CLAIM_TYPES = {"metaphor", "draft", "prompt", "receipt"}
OUTSIDE_TARGET_PREFIX = str(GARDEN_ROOT.resolve())


def check_manifest() -> list[str]:
    errors = []
    mf = GARDEN_ROOT / "garden_manifest.json"
    if not mf.exists():
        errors.append("MISSING: garden_manifest.json")
        return errors
    try:
        m = json.loads(mf.read_text())
    except Exception as e:
        errors.append(f"PARSE_ERROR: garden_manifest.json: {e}")
        return errors
    if m.get("authority") is not False:
        errors.append("MANIFEST: authority must be false")
    if m.get("sovereign") is not False:
        errors.append("MANIFEST: sovereign must be false")
    if m.get("status") in FORBIDDEN_STATUSES:
        errors.append(f"MANIFEST: forbidden status {m.get('status')!r}")
    return errors


def check_receipts() -> list[str]:
    errors = []
    receipt_dir = GARDEN_ROOT / "receipts"
    if not receipt_dir.exists():
        return ["MISSING: receipts/ directory"]
    for rf in sorted(receipt_dir.glob("*.json")):
        try:
            r = json.loads(rf.read_text())
        except Exception as e:
            errors.append(f"PARSE_ERROR: {rf.name}: {e}")
            continue
        if r.get("authority") is not False:
            errors.append(f"RECEIPT {rf.name}: authority must be false")
        if r.get("sovereign") is not False:
            errors.append(f"RECEIPT {rf.name}: sovereign must be false")
        if r.get("status") in FORBIDDEN_STATUSES:
            errors.append(f"RECEIPT {rf.name}: forbidden status {r.get('status')!r}")
        for key in FORBIDDEN_SOVEREIGN_KEYWORDS:
            if key in str(r):
                errors.append(f"RECEIPT {rf.name}: contains sovereign keyword {key!r}")
    return errors


def check_rooms() -> list[str]:
    errors = []
    rooms_dir = GARDEN_ROOT / "rooms"
    if not rooms_dir.exists():
        return ["MISSING: rooms/ directory"]
    room_files = list(rooms_dir.glob("*.md"))
    if not room_files:
        errors.append("ROOMS: no room files found")
        return errors
    for rf in sorted(room_files):
        content = rf.read_text()
        if "purpose" not in content.lower() and "purpose:" not in content.lower():
            errors.append(f"ROOM {rf.name}: missing 'purpose' field")
        has_claim_type = any(f"CLAIM_TYPE: {ct}" in content for ct in VALID_CLAIM_TYPES)
        if not has_claim_type:
            errors.append(f"ROOM {rf.name}: missing CLAIM_TYPE in {VALID_CLAIM_TYPES}")
        # Check no sovereign keywords
        for kw in FORBIDDEN_SOVEREIGN_KEYWORDS:
            if kw in content:
                errors.append(f"ROOM {rf.name}: contains sovereign keyword {kw!r}")
    return errors


def check_doctrines() -> list[str]:
    errors = []
    d_dir = GARDEN_ROOT / "doctrines"
    if not d_dir.exists():
        return []
    for df in sorted(d_dir.glob("*.md")):
        content = df.read_text()
        has_claim_type = any(f"CLAIM_TYPE: {ct}" in content for ct in VALID_CLAIM_TYPES)
        if not has_claim_type:
            errors.append(f"DOCTRINE {df.name}: missing CLAIM_TYPE")
    return errors


def check_meditations() -> list[str]:
    errors = []
    m_dir = GARDEN_ROOT / "meditations"
    if not m_dir.exists():
        return []
    for mf in sorted(m_dir.glob("*.md")):
        content = mf.read_text()
        has_claim_type = any(f"CLAIM_TYPE: {ct}" in content for ct in VALID_CLAIM_TYPES)
        if not has_claim_type:
            errors.append(f"MEDITATION {mf.name}: missing CLAIM_TYPE")
    return errors


def check_bulletins() -> list[str]:
    errors = []
    b_dir = GARDEN_ROOT / "bulletins"
    if not b_dir.exists():
        return []
    bulletin_files = list(b_dir.glob("*.txt"))
    if not bulletin_files:
        return []
    # Import WULmoji validator if available
    try:
        sys.path.insert(0, str(GARDEN_ROOT.parent.parent.parent))
        from tools.wulmoji_ledger_validator import validate_bulletin
        for bf in sorted(bulletin_files):
            results = validate_bulletin(bf.read_text())
            for r in results:
                if not r.ok:
                    for e in r.errors:
                        errors.append(f"BULLETIN {bf.name} line {r.line_num}: {e}")
    except ImportError:
        # Validator not available — skip bulletin format check
        errors.append("WARNING: wulmoji_ledger_validator not found — bulletin format unchecked")
    return errors


def run_validation() -> tuple[bool, list[str]]:
    all_errors: list[str] = []
    all_errors.extend(check_manifest())
    all_errors.extend(check_receipts())
    all_errors.extend(check_rooms())
    all_errors.extend(check_doctrines())
    all_errors.extend(check_meditations())
    all_errors.extend(check_bulletins())
    return len(all_errors) == 0, all_errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Goblin Meditation Center garden")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    ok, errors = run_validation()

    if args.as_json:
        print(json.dumps({
            "ok": ok,
            "authority": False,
            "sovereign": False,
            "errors": errors,
            "error_count": len(errors),
        }, ensure_ascii=False, indent=2))
    else:
        if ok:
            print("✅ Garden valid — all checks pass")
        else:
            print(f"❌ Garden invalid — {len(errors)} error(s):")
            for e in errors:
                print(f"  ERROR: {e}")

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
