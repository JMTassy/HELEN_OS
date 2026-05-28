#!/usr/bin/env python3
"""
Doctrine admission gate driver.

Activates DOCTRINE_ADMISSION_PROTOCOL_V1 against a real doctrine artifact by
reusing the already-green claim-classification harness and adding doctrine-file
metadata checks. Supports local files and git-ref:path targets so admission can
be smoked on bottled doctrine branches without checking them out.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HARNESS = ROOT / "tests" / "test_claim_classification.py"


def load_harness():
    spec = importlib.util.spec_from_file_location("claim_gate_harness", HARNESS)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load harness from {HARNESS}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def resolve_artifact(target: str) -> tuple[str, str]:
    """Return (display_name, markdown_text) for a local path or git ref:path target."""
    if ":" in target and not Path(target).exists():
        ref, path = target.split(":", 1)
        result = subprocess.run(
            ["git", "show", f"{ref}:{path}"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        return target, result.stdout
    path = Path(target)
    if not path.is_absolute():
        path = ROOT / path
    return str(path), path.read_text(encoding="utf-8", errors="replace")


def parse_metadata(markdown: str) -> dict[str, str]:
    match = re.search(r"```(?:\w+)?\n(.*?)\n```", markdown, re.DOTALL)
    if not match:
        return {}
    block = match.group(1)
    metadata: dict[str, str] = {}
    current_key: str | None = None
    for raw_line in block.splitlines():
        line = raw_line.rstrip()
        if not line.strip():
            continue
        if ":" in line:
            key, value = line.split(":", 1)
            current_key = key.strip().lower()
            metadata[current_key] = value.strip()
        elif current_key:
            metadata[current_key] = f"{metadata[current_key]} {line.strip()}".strip()
    return metadata


def map_impl_state(raw: str) -> str:
    lookup = {
        "NONE": "NONE",
        "PRINCIPLE_ONLY": "CONCEPT",
        "CONCEPT": "CONCEPT",
        "PARTIAL": "PARTIAL",
        "PIPELINE_LOCAL": "PIPELINE_LOCAL",
        "GENERALIZED": "GENERALIZED",
        "RECEIPTED": "RECEIPTED",
    }
    return lookup.get(raw.strip().upper(), "CONCEPT")


def infer_force(metadata: dict[str, str], markdown: str) -> str:
    explicit = metadata.get("claim_force", "").strip().upper()
    if explicit in {"DESCRIPTIVE", "ASSERTIVE", "PROOF"}:
        return explicit

    # Proposal doctrines default to descriptive unless the metadata explicitly
    # promotes them; isolated sentences inside the body should not upcast the
    # whole artifact to ASSERTIVE.
    lifecycle = metadata.get("lifecycle", "").strip().upper()
    status = metadata.get("status", "").strip().upper()
    if lifecycle in {"PROPOSAL", "DRAFT"} or status.startswith("DRAFT"):
        return "DESCRIPTIVE"

    lowered = markdown.lower()
    if any(token in lowered for token in ["invariant:", "proves", "guarantees"]):
        return "ASSERTIVE"
    return "DESCRIPTIVE"


def build_claim(display_name: str, markdown: str) -> dict[str, str]:
    metadata = parse_metadata(markdown)
    proposal_id = metadata.get("proposal_id") or Path(display_name.split(":")[-1]).stem
    status = metadata.get("status", "DRAFT_V1").upper()
    provenance = metadata.get("provenance", "NONE")
    growth_rule = metadata.get("growth_rule", "")
    hold_reason = metadata.get("hold_reason", "NONE")
    receipt_match = re.search(r"sha256:[0-9a-fA-F]{16,}", markdown)
    test_match = re.search(r"\b(?:tests?/[\w./-]+|test_[\w./-]+\.py)\b", markdown)

    claim = {
        "id": proposal_id,
        "text": markdown.splitlines()[0].strip("# ").strip() or proposal_id,
        "asserted_stratum": "DOCTRINE",
        "asserted_force_level": infer_force(metadata, markdown),
        "evidence": receipt_match.group(0) if receipt_match else "NONE",
        "admission_status": "ADMITTED" if "ADMITTED" in status else "UNADMITTED",
        "failure_mode": hold_reason if hold_reason != "NONE" else "Could fail admission if provenance, append-only growth, or constitutional mapping remain unresolved",
        "implementation_state": map_impl_state(metadata.get("implementation_status", "CONCEPT")),
        "test_pointer": test_match.group(0) if test_match else "NONE",
        "artifact_pointer": display_name,
        "notes": provenance,
    }
    if growth_rule:
        claim["notes"] = f"{claim['notes']} | growth_rule={growth_rule}"
    if metadata.get("authority"):
        claim["notes"] = f"{claim['notes']} | authority={metadata['authority']}"
    if metadata.get("canon"):
        claim["notes"] = f"{claim['notes']} | canon={metadata['canon']}"
    if metadata.get("lifecycle"):
        claim["notes"] = f"{claim['notes']} | lifecycle={metadata['lifecycle']}"
    return claim


def doctrine_missing_requirements(
    metadata: dict[str, str],
    claim: dict[str, str],
    decision: str,
    requested_promotion: str,
) -> list[str]:
    missing: list[str] = []
    if metadata.get("authority", "").upper() != "NON_SOVEREIGN":
        missing.append("non_sovereign_authority")
    if metadata.get("canon", "").upper() != "NO_SHIP":
        missing.append("no_ship_canon")
    if "APPEND-ONLY" not in metadata.get("growth_rule", "").upper():
        missing.append("append_only_growth_rule")
    if claim["evidence"] == "NONE":
        missing.append("receipt_pointer")
    if claim["test_pointer"] == "NONE":
        missing.append("passing_test_result")
    if not metadata.get("provenance"):
        missing.append("provenance_traceability")
    if metadata.get("lifecycle", "").upper() not in {"PROPOSAL", "DRAFT"}:
        missing.append("proposal_lifecycle")
    # Only suppress material bindings when no promotion is requested.
    # When requesting ADMITTED, preserve all missing items as diagnostics.
    if decision == "KEEP" and requested_promotion == "NONE":
        missing = [item for item in missing if item not in {"receipt_pointer", "passing_test_result"}]
    return missing


def evaluate(target: str, requested_promotion: str) -> dict[str, object]:
    harness = load_harness()
    display_name, markdown = resolve_artifact(target)
    metadata = parse_metadata(markdown)
    claim = build_claim(display_name, markdown)
    gate = harness.classify(claim)
    missing = doctrine_missing_requirements(metadata, claim, gate["decision"], requested_promotion)
    return {
        "claim_id": claim["id"],
        "current_stratum": gate["stratum"],
        "requested_promotion": requested_promotion,
        "decision": gate["decision"],
        "reason_codes": gate["reason_codes"],
        "missing_requirements": missing,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run doctrine admission gate on a single doctrine artifact."
    )
    parser.add_argument("target", help="Local path or git-ref:path to doctrine markdown")
    parser.add_argument("--requested-promotion", default="ADMITTED")
    args = parser.parse_args()
    result = evaluate(args.target, args.requested_promotion)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
