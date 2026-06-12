#!/usr/bin/env python3
"""
Post-MAYOR apply script — R-20260612-0005
Ghost closure re-issuance: SEAM-001-schema-authority-V4/V5/V6

PRECONDITION: MAYOR has issued a ruling authorizing re-issuance.
This script is a TEMPLATE — it must not be run without that ruling.

Authorized action: update PASS claims in V4/V5/V6 closure receipts
to reflect current observed artifact SHAs (or flip to MISSING/FAIL
for absent artifacts), so the ghost-closure gate passes.

Sovereign path: GOVERNANCE/CLOSURES/** — Claude Code cannot write here.
Must be executed by an authorized process after MAYOR ruling.

Receipts routed:   R-20260612-0005 (ACK'd 2026-06-12)
Gate target:       helen_os/tests/test_no_ghost_closures.py (3 tests)
"""
import json
import hashlib
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent
CLOSURES = REPO_ROOT / "GOVERNANCE" / "CLOSURES"


def current_sha256(path: Path) -> str | None:
    if not path.exists() or path.is_dir():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit_closure(name: str) -> dict:
    f = CLOSURES / name
    d = json.loads(f.read_text())
    repairs = []
    for c in d.get("claims", []):
        art = c.get("expected_artifact", "")
        expected = c.get("expected_sha256", "")
        observed = current_sha256(REPO_ROOT / art)
        if observed is None:
            if c["verdict"] == "PASS":
                repairs.append({
                    "claim_id": c["claim_id"],
                    "action": "SET_VERDICT_MISSING",
                    "artifact": art,
                    "old_expected": expected,
                })
        elif observed != expected:
            if c["verdict"] == "PASS":
                repairs.append({
                    "claim_id": c["claim_id"],
                    "action": "UPDATE_SHA",
                    "artifact": art,
                    "old_expected": expected,
                    "new_expected": observed,
                })
    return {"file": name, "repairs": repairs}


if __name__ == "__main__":
    print("=== GHOST CLOSURE REPAIR AUDIT ===")
    print("PRECONDITION: MAYOR ruling R-20260612-0005 required before applying.\n")

    total = 0
    for v in ["V4", "V5", "V6"]:
        name = f"SEAM-001-schema-authority-{v}.json"
        result = audit_closure(name)
        print(f"{name}: {len(result['repairs'])} repairs needed")
        for r in result["repairs"]:
            print(f"  {r['claim_id']} [{r['action']}] {r['artifact']}")
            if r["action"] == "UPDATE_SHA":
                print(f"    old: {r['old_expected'][:16]}...")
                print(f"    new: {r['new_expected'][:16]}...")
        total += len(result["repairs"])

    print(f"\nTotal repairs: {total}")
    print("\nTO APPLY (after MAYOR ruling):")
    print("  Authorized process must update GOVERNANCE/CLOSURES/SEAM-001-schema-authority-V[456].json")
    print("  For absent artifacts: set verdict=MISSING, clear expected_sha256")
    print("  For drifted artifacts: update expected_sha256 to observed value")
    print("\nRETEST RING (after apply):")
    print("  .venv/bin/pytest helen_os/tests/test_no_ghost_closures.py -v")
