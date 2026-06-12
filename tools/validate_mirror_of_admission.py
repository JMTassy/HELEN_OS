#!/usr/bin/env python3
"""
validate_mirror_of_admission.py — NON_SOVEREIGN · NO_CLAIM
Validates a MIRROR_OF_ADMISSION_V1 JSON artifact against schema + HELEN discipline rules.
"""
import json
import sys
from pathlib import Path

try:
    from jsonschema import Draft202012Validator
except ImportError as exc:
    raise SystemExit(
        "Missing dependency: jsonschema. Install with: pip install jsonschema"
    ) from exc

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "helen_os" / "schemas" / "mirror_of_admission_v1.schema.json"


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def validate_mirror(path: Path) -> list[str]:
    schema = load_json(SCHEMA_PATH)
    payload = load_json(path)
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(payload), key=lambda e: list(e.path))
    messages = [
        f"{'.'.join(str(p) for p in e.path) or '<root>'}: {e.message}"
        for e in errors
    ]

    # HELEN discipline rules beyond JSON Schema
    if "\n" in payload.get("next_move", {}).get("one_action", ""):
        messages.append(
            "next_move.one_action must be one action, not a multiline plan"
        )
    if payload.get("law_world", {}).get("admissible") is True:
        if payload.get("law_world", {}).get("missing_receipts"):
            messages.append(
                "law_world.admissible cannot be true while missing_receipts is non-empty"
            )
    if payload.get("authority") != "NON_SOVEREIGN":
        messages.append("authority must remain NON_SOVEREIGN")
    if payload.get("canon") != "NO_SHIP":
        messages.append("canon must remain NO_SHIP")
    if payload.get("status") != "NO_CLAIM":
        messages.append("status must remain NO_CLAIM")

    return messages


def main() -> int:
    if len(sys.argv) != 2:
        print(
            "Usage: tools/validate_mirror_of_admission.py <mirror.json>",
            file=sys.stderr,
        )
        return 2
    path = Path(sys.argv[1])
    if not path.exists():
        print(f"File not found: {path}", file=sys.stderr)
        return 2
    errors = validate_mirror(path)
    if errors:
        print("MIRROR_OF_ADMISSION_V1: INVALID")
        for err in errors:
            print(f"  - {err}")
        return 1
    print("MIRROR_OF_ADMISSION_V1: VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
