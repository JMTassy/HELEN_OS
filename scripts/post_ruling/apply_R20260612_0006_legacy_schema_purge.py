#!/usr/bin/env python3
"""
Post-MAYOR apply script — R-20260612-0006
Legacy schema purge: schemas/mirror_of_admission_v1.schema.json

PRECONDITION: MAYOR has issued a ruling authorizing migration + purge.
This script is a TEMPLATE — it must not be run without that ruling.

Authorized action (two options, MAYOR chooses one):

  OPTION A — Migrate:
    1. Copy schemas/mirror_of_admission_v1.schema.json
          → helen_os/schemas/mirror_of_admission_v1.schema.json
    2. Register in helen_os/governance/schema_registry.py
    3. Update 3 consumers to point to new path
    4. Delete schemas/mirror_of_admission_v1.schema.json (only file remaining)
    5. schemas/ directory becomes empty → test passes

  OPTION B — Quarantine (if schema is truly deprecated):
    1. Move schema to docs/specs/schemas/ (non-sovereign archive)
    2. Update 3 consumers to no longer reference the schema
    3. Delete schemas/mirror_of_admission_v1.schema.json
    4. schemas/ directory becomes empty → test passes

Sovereign paths touched:
  WRITE: helen_os/schemas/** (Option A)    ← firewall path
  WRITE: helen_os/governance/schema_registry.py (Option A)  ← firewall path
  DELETE: schemas/mirror_of_admission_v1.schema.json        ← firewall path

Claude Code cannot execute this. MAYOR must authorize and route through
an admitted process.

Receipts routed:   R-20260612-0006 (ACK'd 2026-06-12)
Gate target:       helen_os/tests/test_schema_authority_guard.py::test_legacy_schemas_directory_is_purged
"""
from pathlib import Path
import json

REPO_ROOT = Path(__file__).parent.parent.parent
LEGACY_SCHEMA = REPO_ROOT / "schemas" / "mirror_of_admission_v1.schema.json"
TARGET = REPO_ROOT / "helen_os" / "schemas" / "mirror_of_admission_v1.schema.json"

CONSUMERS = [
    "tools/mirror_of_admission_stub.py",
    "tools/validate_mirror_of_admission.py",
    "tests/test_mirror_of_admission.py",
]


def audit() -> None:
    print("=== LEGACY SCHEMA PURGE AUDIT ===")
    print("PRECONDITION: MAYOR ruling R-20260612-0006 required before applying.\n")

    if LEGACY_SCHEMA.exists():
        d = json.loads(LEGACY_SCHEMA.read_text())
        print(f"Schema: {LEGACY_SCHEMA.relative_to(REPO_ROOT)}")
        print(f"  title: {d.get('title','(none)')}")
        print(f"  size:  {LEGACY_SCHEMA.stat().st_size} bytes")
    else:
        print("Schema already absent — test should pass.")
        return

    print(f"\nTarget (Option A): {TARGET.relative_to(REPO_ROOT)}")
    print(f"  exists: {TARGET.exists()}")

    print("\nConsumers (must be updated before delete):")
    for c in CONSUMERS:
        p = REPO_ROOT / c
        print(f"  {c}: {'EXISTS' if p.exists() else 'ABSENT'}")

    remaining = list((REPO_ROOT / "schemas").glob("*.json"))
    print(f"\nCurrent schemas/ JSON count: {len(remaining)}")
    for f in remaining:
        print(f"  {f.name}")

    print("\nTO APPLY (after MAYOR ruling):")
    print("  OPTION A: migrate → register → update consumers → delete")
    print("  OPTION B: quarantine → update consumers → delete")
    print("\nRETEST RING (after apply):")
    print("  .venv/bin/pytest helen_os/tests/test_schema_authority_guard.py::test_legacy_schemas_directory_is_purged -v")
    print("  make test")


if __name__ == "__main__":
    audit()
