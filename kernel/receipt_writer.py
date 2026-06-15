#!/usr/bin/env python3
"""
Receipt writing and artifact management.

Receipts are the proof that a tool ran deterministically.

Structure:
- request.json: what was asked
- response.json: what the tool produced
- receipt.json: metadata + hashes binding both
"""

import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime, UTC
from dataclasses import dataclass, asdict

try:
    from kernel.canonical_json import to_canonical_json
    from kernel.hashing import sha256_file, sha256_canonical_json, sha256_str
except ImportError:
    from .canonical_json import to_canonical_json
    from .hashing import sha256_file, sha256_canonical_json, sha256_str


@dataclass
class ArtifactRef:
    """Reference to an artifact (with proof)"""
    path: str
    sha256: str
    artifact_type: Optional[str] = None
    description: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict, excluding None values"""
        return {k: v for k, v in asdict(self).items() if v is not None}


def write_json(file_path: str, data: Any) -> str:
    """
    Write data as canonical JSON and return its hash.

    Args:
        file_path: Where to write
        data: Python object to serialize

    Returns:
        SHA256 hash of written file
    """
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    # Serialize canonically
    canonical = to_canonical_json(data)

    # Write
    path.write_text(canonical, encoding="utf-8")

    # Return hash
    return sha256_str(canonical)


def write_receipt(
    receipt_path: str,
    plugin_name: str,
    plugin_version: str,
    request_data: Dict[str, Any],
    response_data: Dict[str, Any],
    request_file: Optional[str] = None,
    response_file: Optional[str] = None,
    determinism_class: str = "DETERMINISTIC",
    bound_artifacts: Optional[List[ArtifactRef]] = None,
) -> str:
    """
    Create a receipt recording a plugin execution.

    A receipt proves:
    - What was asked (request)
    - What was produced (response)
    - That both are hash-bound
    - The plugin version and determinism class

    Args:
        receipt_path: Where to write receipt.json
        plugin_name: Name of plugin (e.g., "rho_lint")
        plugin_version: Version string (e.g., "v1.0")
        request_data: Input to plugin (dict)
        response_data: Output from plugin (dict)
        request_file: Optional path to request file (will be hashed)
        response_file: Optional path to response file (will be hashed)
        determinism_class: "DETERMINISTIC", "SEEDED", or "NONDETERMINISTIC"
        bound_artifacts: List of artifacts used/produced

    Returns:
        SHA256 hash of receipt

    Raises:
        ValueError: If determinism_class is invalid
        FileNotFoundError: If request_file or response_file don't exist
    """
    if determinism_class not in ("DETERMINISTIC", "SEEDED", "NONDETERMINISTIC"):
        raise ValueError(f"Invalid determinism_class: {determinism_class}")

    # Hash inputs/outputs
    request_hash = sha256_canonical_json(request_data)
    response_hash = sha256_canonical_json(response_data)

    # Optionally hash files
    request_file_hash = None
    if request_file:
        request_file_hash = sha256_file(request_file)

    response_file_hash = None
    if response_file:
        response_file_hash = sha256_file(response_file)

    # Build receipt
    receipt = {
        "schema": "helen.receipt.v1",
        "plugin": {
            "name": plugin_name,
            "version": plugin_version,
            "determinism": determinism_class,
        },
        "inputs": {
            "request_hash": request_hash,
            "request_file_hash": request_file_hash,
        },
        "outputs": {
            "response_hash": response_hash,
            "response_file_hash": response_file_hash,
        },
        "bound_artifacts": (
            [a.to_dict() for a in bound_artifacts] if bound_artifacts else []
        ),
        "metadata": {
            "timestamp": datetime.now(UTC).replace(tzinfo=None).isoformat() + "Z",
            "environment": {
                "python_version": "3.9+",
                "platform": "deterministic",
            },
        },
    }

    # Compute receipt hash (excluding receipt_hash itself)
    receipt_canonical = to_canonical_json(receipt)
    receipt_hash = sha256_str(receipt_canonical)

    # Add hash to receipt
    receipt["receipt_hash"] = receipt_hash

    # Write receipt
    path = Path(receipt_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(to_canonical_json(receipt), encoding="utf-8")

    return receipt_hash
