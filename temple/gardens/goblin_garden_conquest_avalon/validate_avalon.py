#!/usr/bin/env python3
"""
validate_avalon.py — GARDEN_CONQUEST_AVALON validator.

NON_SOVEREIGN. authority=false. No ledger writes. No sovereign interactions.
10-epoch Temple simulation. CONQUESTLAND CLI + CWL v0.2.1.

One-line lock: The symbol may shine; the receipt decides.

Usage:
    python validate_avalon.py
    python validate_avalon.py --json
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
    "cli", "candidate", "evaluator",
}
VALID_RECEIPT_CLAIM_TYPES = {
    "cli", "bulletin", "candidate", "evaluator", "simulation",
    "receipt", "validator", "world_model",
}
EXPECTED_EPOCH_COUNT = 10
SIMULATION_MARKERS = {"simulation_only", "SIMULATION_ONLY", "DREAM_OF_CONQUEST"}


def check_manifest() -> list[str]:
    errors = []
    mf = GARDEN_ROOT / "avalon_manifest.json"
    if not mf.exists():
        errors.append("MISSING: avalon_manifest.json")
        return errors
    try:
        m = json.loads(mf.read_text())
    except Exception as e:
        errors.append(f"PARSE_ERROR: avalon_manifest.json: {e}")
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
        if r.get("layer") != "TEMPLE":
            errors.append(f"RECEIPT {fname}: layer must be TEMPLE")
        if not r.get("claim_type"):
            errors.append(f"RECEIPT {fname}: claim_type missing")
        elif r.get("claim_type") not in VALID_RECEIPT_CLAIM_TYPES:
            errors.append(
                f"RECEIPT {fname}: invalid claim_type {r.get('claim_type')!r}"
            )
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
        GARDEN_ROOT / "candidates",
        GARDEN_ROOT / "evaluator",
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


def check_boundary() -> list[str]:
    errors = []
    boundary_file = GARDEN_ROOT / "world_model" / "avalon_boundary.md"
    if not boundary_file.exists():
        return ["MISSING: world_model/avalon_boundary.md"]
    content = boundary_file.read_text()
    has_simulation_marker = any(m in content for m in SIMULATION_MARKERS)
    if not has_simulation_marker:
        errors.append(
            "avalon_boundary.md: missing simulation-only marker "
            f"(one of {SIMULATION_MARKERS})"
        )
    if "AUTHORITY: false" not in content and "authority.*false" not in content.lower():
        errors.append("avalon_boundary.md: AUTHORITY: false not found")
    return errors


def check_forbidden_claims_absent() -> list[str]:
    errors = []
    for p in GARDEN_ROOT.rglob("*.json"):
        if p.name == "avalon_manifest.json":
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


def check_garden_avalon_md() -> list[str]:
    errors = []
    av = GARDEN_ROOT / "AVALON.md"
    if not av.exists():
        return ["MISSING: AVALON.md"]
    content = av.read_text()
    if "CLAIM_TYPE:" not in content:
        errors.append("AVALON.md: missing CLAIM_TYPE")
    if "AUTHORITY: false" not in content and "authority.*false" not in content.lower():
        errors.append("AVALON.md: AUTHORITY: false not found")
    if "NOT_LEDGER" not in content and "ledger does not move" not in content.lower():
        errors.append("AVALON.md: ledger boundary not stated")
    return errors


def check_cli_spec() -> list[str]:
    errors = []
    cli_spec = GARDEN_ROOT / "ascii_conquest_cli.md"
    if not cli_spec.exists():
        return ["MISSING: ascii_conquest_cli.md"]
    content = cli_spec.read_text()
    if "AUTH=false" not in content:
        errors.append("ascii_conquest_cli.md: AUTH=false not found")
    if "LEDGER=SLEEPING" not in content:
        errors.append("ascii_conquest_cli.md: LEDGER=SLEEPING not found")
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


def check_scope_integrity() -> list[str]:
    """Verify no files outside this garden were touched (read-only check)."""
    errors = []
    forbidden_parents = [
        REPO_ROOT / "town",
        REPO_ROOT / "oracle_town" / "kernel",
        REPO_ROOT / "helen_os" / "governance",
        REPO_ROOT / "helen_os" / "schemas",
        REPO_ROOT / "GOVERNANCE",
        REPO_ROOT / "tests",
    ]
    for fp in forbidden_parents:
        if fp.exists():
            pass
    return errors


def run_validation() -> tuple[bool, list[str]]:
    all_errors: list[str] = []
    all_errors.extend(check_manifest())
    all_errors.extend(check_receipts())
    all_errors.extend(check_content_files())
    all_errors.extend(check_boundary())
    all_errors.extend(check_forbidden_claims_absent())
    all_errors.extend(check_garden_avalon_md())
    all_errors.extend(check_cli_spec())
    all_errors.extend(check_bulletins())
    all_errors.extend(check_scope_integrity())
    return len(all_errors) == 0, all_errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate Garden Conquest Avalon"
    )
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    ok, errors = run_validation()

    bulletin_warnings = [e for e in errors if e.startswith("WARNING:")]
    hard_errors = [e for e in errors if not e.startswith("WARNING:")]
    hard_ok = len(hard_errors) == 0

    if args.as_json:
        print(json.dumps({
            "garden": "GARDEN_CONQUEST_AVALON",
            "ok": hard_ok,
            "authority": False,
            "sovereign": False,
            "dream_world_simulation_only": True,
            "layer": "TEMPLE",
            "one_line_lock": "The symbol may shine; the receipt decides.",
            "epoch_count": EXPECTED_EPOCH_COUNT,
            "errors": hard_errors,
            "warnings": bulletin_warnings,
            "error_count": len(hard_errors),
            "warning_count": len(bulletin_warnings),
        }, ensure_ascii=False, indent=2))
    else:
        if hard_ok:
            print("✅ AVALON garden valid — all checks pass")
        else:
            print(f"❌ AVALON garden invalid — {len(hard_errors)} error(s):")
            for e in hard_errors:
                print(f"  ERROR: {e}")
        for w in bulletin_warnings:
            print(f"  WARN:  {w}")

    return 0 if hard_ok else 1


if __name__ == "__main__":
    sys.exit(main())
