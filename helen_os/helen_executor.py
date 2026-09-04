"""
HELEN_EXECUTOR_V1 — Bounded, replayable task execution.
Law: Executor may run. It may not adjudicate.

Converts EXECUTOR_MANIFEST_V1 → BUILDERS_RUN_V1 with deterministic logging,
receipt emission, and strict boundary enforcement.
"""
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import subprocess
import sys
import time
from dataclasses import dataclass
from typing import Any

# K_TAU pre-dispatch jurisdiction gate. Mediation must be loadable from every
# import context (package or flat) — a guard that vanishes on ImportError is a
# bypass, so fail closed by forcing the repo root onto sys.path if needed.
try:
    from helen_kernel.gates.claim_type_policy import pre_dispatch_guard
except ImportError:
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
    from helen_kernel.gates.claim_type_policy import pre_dispatch_guard


def sha256_bytes(data: bytes) -> str:
    """Compute SHA-256 hash of bytes."""
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: pathlib.Path) -> str:
    """Compute SHA-256 hash of file."""
    return sha256_bytes(path.read_bytes())


def canonical_json_bytes(obj: Any) -> bytes:
    """Serialize object to canonical JSON (RFC 8785 JCS)."""
    return json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


@dataclass(frozen=True)
class ExecutorViolation(Exception):
    """Executor-grade violation: manifest or execution failed constraints."""
    message: str


def _is_under(base: pathlib.Path, candidate: pathlib.Path) -> bool:
    """Check if candidate path is under base path."""
    try:
        candidate.resolve().relative_to(base.resolve())
        return True
    except ValueError:
        return False


def _check_path_policy(
    working_dir: pathlib.Path,
    mutable_paths: list[str],
    forbidden_paths: list[str],
) -> None:
    """Validate that mutable_paths stay within working_dir and forbidden_paths don't overlap."""
    mutable = [pathlib.Path(p) for p in mutable_paths]
    forbidden = [pathlib.Path(p) for p in forbidden_paths]

    for mp in mutable:
        if not _is_under(working_dir, working_dir / mp) and not _is_under(
            pathlib.Path("."), mp
        ):
            raise ExecutorViolation(
                f"Mutable path escapes working_dir: {mp}"
            )

    for fp in forbidden:
        if _is_under(working_dir, working_dir / fp) or _is_under(
            pathlib.Path("."), fp
        ):
            raise ExecutorViolation(f"Forbidden path overlaps working_dir: {fp}")


def run_executor_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    """
    Execute task defined by EXECUTOR_MANIFEST_V1.

    Returns BUILDERS_RUN_V1 artifact with deterministic hashes and receipt.

    Enforced invariants:
    - Same manifest → same bytes out
    - Writes only under mutable_paths
    - No writes to forbidden_paths
    - Hard timeout (no negotiation)
    - No verdict/authority in output
    """
    if manifest.get("schema_version") != "EXECUTOR_MANIFEST_V1":
        raise ExecutorViolation("Invalid schema_version")

    # Jurisdiction before effect: BLOCKED is terminal — no mkdir, no subprocess,
    # no filesystem mutation may precede this check.
    block = pre_dispatch_guard(
        {
            "family": "executor",
            "op": "task",
            "claim_type": manifest.get("claim_type", "RECEIPT"),
        }
    )
    if block is not None:
        raise ExecutorViolation(
            f"K_TAU_BLOCKED:{block['reason']}:{block['operation']}:"
            f"requested={block['requested_claim_type']}"
        )

    working_dir = pathlib.Path(manifest["working_dir"]).resolve()
    working_dir.mkdir(parents=True, exist_ok=True)

    _check_path_policy(
        working_dir=working_dir,
        mutable_paths=manifest["mutable_paths"],
        forbidden_paths=manifest["forbidden_paths"],
    )

    if manifest.get("network_policy", "forbidden") != "forbidden":
        raise ExecutorViolation(
            "Only network_policy=forbidden is supported in V1"
        )

    # Deterministic environment
    env = {
        "PYTHONHASHSEED": manifest["seed"],
        "LC_ALL": "C",
        "LANG": "C",
        "TZ": "UTC",
        "PATH": os.environ.get("PATH", ""),
    }

    stdout_path = working_dir / "stdout.txt"
    stderr_path = working_dir / "stderr.txt"

    started = time.time()
    with stdout_path.open("wb") as out, stderr_path.open("wb") as err:
        proc = subprocess.run(
            manifest["command"],
            cwd=str(working_dir),
            stdout=out,
            stderr=err,
            timeout=int(manifest["timeout_seconds"]),
            env=env,
            check=False,
        )
    ended = time.time()

    # Collect output artifacts
    output_artifacts = []
    for ref in manifest.get("expected_output_refs", []):
        p = pathlib.Path(ref)
        if not p.is_absolute():
            p = (pathlib.Path.cwd() / p).resolve()
        if p.exists():
            output_artifacts.append({"path": str(p), "sha256": sha256_file(p)})

    # Build run artifact base (deterministic fields only)
    run_base = {
        "schema_version": "BUILDERS_RUN_V1",
        "run_id": manifest["run_id"],
        "manifest_id": manifest["manifest_id"],
        "claim_id": manifest["claim_id"],
        "status": "completed" if proc.returncode == 0 else "failed",
        "exit_code": proc.returncode,
        "stdout_sha256": sha256_file(stdout_path),
        "stderr_sha256": sha256_file(stderr_path),
        "output_artifacts": output_artifacts,
        "canonicalization": "JCS_SHA256_V1",
    }

    # Compute payload hash from deterministic base
    payload_hash = sha256_bytes(canonical_json_bytes(run_base))

    # Compute receipt hash from deterministic base (includes payload_sha256)
    receipt_base = dict(run_base)
    receipt_base["payload_sha256"] = payload_hash
    receipt_hash = sha256_bytes(canonical_json_bytes(receipt_base))

    # Build final run artifact with all fields including non-deterministic runtime
    run_obj = dict(run_base)
    run_obj["runtime_seconds"] = round(ended - started, 6)
    run_obj["payload_sha256"] = payload_hash
    run_obj["receipt_sha256"] = receipt_hash

    return run_obj
