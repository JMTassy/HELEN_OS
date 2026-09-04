#!/usr/bin/env python3
"""
HELEN M5→M6 boundary — Normalizer.

The ONLY producer of run packets. Raw provider output enters, a sealed
helen.run-packet.v0 exits. The seal makes bypass detectable:

    normalizer_seal = sha256(canonical_packet_without_seal + NORMALIZER_SECRET_VERSION)

Any file that claims to be a run packet but was not produced here will fail
seal verification in verify_packet.py / operator_packet.py, and is refused.

Law 2 (evidence non-creation) enforcement:
  - observations without a source_ref are DROPPED and logged as errors;
  - proposals/inferences are kept but carry no evidence weight;
  - authority is hard-set to false regardless of what the raw output says;
  - a raw output attempting to include its own 'normalizer_seal', 'authority',
    'tests', or 'evidence_refs' fields has those fields discarded.
"""
import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

NORMALIZER_VERSION = "helen-normalizer-0.1.0"
# Version-salt: not a secret in V0, but versioned so a seal states WHICH
# normalizer produced it. V1 can move to an operator-held HMAC key.
SEAL_SALT = f"HELEN::{NORMALIZER_VERSION}::sovereignty-never-circulates"

# Fields a provider's raw output is NEVER allowed to smuggle into a packet.
FORBIDDEN_INBOUND = {"normalizer_seal", "authority", "tests", "evidence_refs", "exit_code"}


def sha256_bytes(b: bytes) -> str:
    return "sha256:" + hashlib.sha256(b).hexdigest()


def canonical(packet: dict) -> bytes:
    p = {k: v for k, v in packet.items() if k != "normalizer_seal"}
    return json.dumps(p, sort_keys=True, separators=(",", ":")).encode()


def seal(packet: dict) -> str:
    return "sha256:" + hashlib.sha256(canonical(packet) + SEAL_SALT.encode()).hexdigest()


def verify_seal(packet: dict) -> bool:
    return packet.get("normalizer_seal") == seal(packet)


def normalize(provider: str, role: str, task_id: str, raw_path: Path) -> dict:
    raw_bytes = raw_path.read_bytes()
    errors = []

    try:
        raw = json.loads(raw_bytes)
        if not isinstance(raw, dict):
            raw = {"text": raw}
    except json.JSONDecodeError:
        raw = {"text": raw_bytes.decode(errors="replace")}
        errors.append("raw output was not JSON; wrapped as text")

    smuggled = FORBIDDEN_INBOUND & set(raw.keys())
    if smuggled:
        errors.append(f"raw output attempted to set protected fields, discarded: {sorted(smuggled)}")

    observations = []
    for ob in raw.get("observations", []) or []:
        if isinstance(ob, dict) and ob.get("source_ref"):
            observations.append({"text": str(ob.get("text", "")), "source_ref": str(ob["source_ref"])})
        else:
            errors.append(f"observation dropped (no source_ref): {json.dumps(ob)[:120]}")

    packet = {
        "schema": "helen.run-packet.v0",
        "run_id": f"{task_id}-{provider}-{role}-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
        "task_id": task_id,
        "provider": provider,
        "model": str(raw.get("model", "unknown")),
        "role": role,
        "authority": False,
        "mutation_allowed": False,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "input_hash": sha256_bytes(task_id.encode()),
        "output_hash": sha256_bytes(raw_bytes),
        "observations": observations,
        "inferences": [str(x) for x in (raw.get("inferences") or [])],
        "proposals": [str(x) for x in (raw.get("proposals") or [])],
        "files_changed": [],
        "commands_run": [],
        "tests": [],
        "evidence_refs": [],
        "errors": errors,
        "exit_code": 0,
        "normalizer_version": NORMALIZER_VERSION,
        "raw_attachment": str(raw_path),
    }
    packet["normalizer_seal"] = seal(packet)
    return packet


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--provider", required=True)
    ap.add_argument("--role", required=True)
    ap.add_argument("--task-id", required=True)
    ap.add_argument("--input", required=True)
    args = ap.parse_args()

    packet = normalize(args.provider, args.role, args.task_id, Path(args.input))
    print(json.dumps(packet, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
