#!/usr/bin/env python3
"""
HELEN Superteam Egregor — MVP Pipeline Runner

Manages artifact handoff between the five pipeline stages:
    GOBLIN → HER → HAL → MAYOR → JM admission queue

Authority: NON_SOVEREIGN  Canon: NO_SHIP  Ledger effect: none
This runner enforces: cadence limits, blindness protocol, schema validation.
It does NOT call LLMs — that happens externally. It manages artifact I/O.

Usage:
    python superteam_pipeline.py status
    python superteam_pipeline.py ingest <file_or_text> [--type pdf|tweet|article|...]
    python superteam_pipeline.py seed <seed_json>          # GOBLIN writes a DreamSeed
    python superteam_pipeline.py insight <insight_json>    # HER writes an InsightCandidate
    python superteam_pipeline.py claim <claim_json>        # HAL writes a ClaimCandidate
    python superteam_pipeline.py validate <validation_json> # MAYOR writes ValidationReceiptCandidate
    python superteam_pipeline.py queue                     # Show admission queue (YES verdicts)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ── paths ──────────────────────────────────────────────────────────────────────

SUPERTEAM_ROOT = Path(__file__).resolve().parent
SCHEMAS_ROOT = SUPERTEAM_ROOT.parent.parent.parent.parent / "schemas" / "helen_superteam"

COMPOST_DIR = SUPERTEAM_ROOT / "compost"
INSIGHTS_DIR = SUPERTEAM_ROOT / "insights"
CLAIMS_DIR = SUPERTEAM_ROOT / "claims"
VALIDATION_DIR = SUPERTEAM_ROOT / "validation"
ADMISSION_DIR = SUPERTEAM_ROOT / "admission"

# ── cadence limits ─────────────────────────────────────────────────────────────

CADENCE = {
    "seeds_per_run": 20,       # GOBLIN max DreamSeeds per epoch
    "inputs_per_run": 10,      # GOBLIN max raw inputs
    "insights_max": 5,         # HER keeps at most 5 InsightCandidates total
    "claims_max": 2,           # HAL keeps at most 2 ClaimCandidates total
    "validation_per_run": 1,   # MAYOR validates at most 1 per epoch
    "admission_per_run": 1,    # JM reviews at most 1
}

# ── id generation ──────────────────────────────────────────────────────────────

def _make_id(prefix: str, content: str) -> str:
    h = hashlib.sha256(content.encode()).hexdigest()[:8]
    return f"{prefix}-{h}"

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()

# ── schema validation ──────────────────────────────────────────────────────────

def _load_schema(name: str) -> dict[str, Any] | None:
    path = SCHEMAS_ROOT / f"{name}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text())

def _validate(artifact: dict[str, Any], schema_name: str) -> list[str]:
    """Minimal field-presence validation (jsonschema optional)."""
    schema = _load_schema(schema_name)
    if schema is None:
        return [f"schema not found: {schema_name}"]
    errors = []
    required = schema.get("required", [])
    for field in required:
        if field not in artifact:
            errors.append(f"missing required field: {field}")
    # Check const constraints
    props = schema.get("properties", {})
    for field, spec in props.items():
        if "const" in spec and field in artifact:
            if artifact[field] != spec["const"]:
                errors.append(f"{field}: expected {spec['const']!r}, got {artifact[field]!r}")
    return errors

# ── blindness protocol enforcement ────────────────────────────────────────────

ALLOWED_FIELDS_FOR_HER = {
    "seed_id", "source_refs", "raw_fragments", "motifs",
    "wild_connections", "why_it_feels_interesting", "input_type",
    "claim_status", "authority", "actor", "created_at", "notes"
}

ALLOWED_FIELDS_FOR_HAL = {
    "insight_id", "derived_from_seed_ids", "insight_sentence",
    "source_refs", "resonance", "possible_use", "uncertainty",
    "evidence_needed", "claim_status", "authority", "actor", "created_at"
}

ALLOWED_FIELDS_FOR_MAYOR = {
    "claim_id", "claim_sentence", "claim_type", "source_refs",
    "evidence_refs", "evidence_requirement", "test_or_review_path",
    "risk_if_wrong", "hal_reason", "derived_from_insight_id",
    "claim_status", "authority", "actor", "created_at"
}

def _strip_for_her(seed: dict) -> dict:
    """HER sees DreamSeed artifact fields only — no GOBLIN process notes beyond spec."""
    return {k: v for k, v in seed.items() if k in ALLOWED_FIELDS_FOR_HER}

def _strip_for_hal(insight: dict) -> dict:
    """HAL sees InsightCandidate artifact fields only."""
    return {k: v for k, v in insight.items() if k in ALLOWED_FIELDS_FOR_HAL}

def _strip_for_mayor(claim: dict) -> dict:
    """MAYOR sees ClaimCandidate artifact fields only. No lineage beyond claim_id."""
    stripped = {k: v for k, v in claim.items() if k in ALLOWED_FIELDS_FOR_MAYOR}
    # Remove upstream lineage: MAYOR must not see insight_id or seed_id
    stripped.pop("derived_from_insight_id", None)
    return stripped

# ── artifact I/O ──────────────────────────────────────────────────────────────

def _write_artifact(directory: Path, artifact_id: str, artifact: dict) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{artifact_id}.json"
    path.write_text(json.dumps(artifact, indent=2, ensure_ascii=False))
    return path

def _read_artifacts(directory: Path) -> list[dict]:
    if not directory.exists():
        return []
    return [
        json.loads(p.read_text())
        for p in sorted(directory.glob("*.json"))
    ]

# ── commands ──────────────────────────────────────────────────────────────────

def cmd_status() -> None:
    seeds = _read_artifacts(COMPOST_DIR)
    insights = _read_artifacts(INSIGHTS_DIR)
    claims = _read_artifacts(CLAIMS_DIR)
    validations = _read_artifacts(VALIDATION_DIR)
    admissions = _read_artifacts(ADMISSION_DIR)

    yes_count = sum(1 for v in validations if v.get("mayor_verdict") == "YES")
    hold_count = sum(1 for v in validations if v.get("mayor_verdict") == "HOLD")
    no_count = sum(1 for v in validations if v.get("mayor_verdict") == "NO")

    print("── HELEN SUPERTEAM STATUS ──────────────────────────────")
    print(f"  COMPOST   {len(seeds):>3} DreamSeeds        (limit: {CADENCE['seeds_per_run']}/run)")
    print(f"  INSIGHTS  {len(insights):>3} InsightCandidates (limit: {CADENCE['insights_max']} total)")
    print(f"  CLAIMS    {len(claims):>3} ClaimCandidates   (limit: {CADENCE['claims_max']} total)")
    print(f"  VALIDATE  {len(validations):>3} ValidationRCs     (YES:{yes_count} HOLD:{hold_count} NO:{no_count})")
    print(f"  ADMISSION {len(admissions):>3} in queue")
    print()
    cadence_ok = len(insights) <= CADENCE["insights_max"] and len(claims) <= CADENCE["claims_max"]
    print(f"  Cadence: {'OK' if cadence_ok else 'OVER LIMIT — prune before next run'}")
    print()
    if yes_count > 0:
        print(f"  → {yes_count} ValidationReceiptCandidate(s) await JM admission review.")


def cmd_seed(seed_json: str) -> None:
    """GOBLIN writes a DreamSeed. Validates schema, assigns ID, writes to compost/."""
    existing = _read_artifacts(COMPOST_DIR)
    if len(existing) >= CADENCE["seeds_per_run"]:
        print(f"CADENCE BLOCK: {CADENCE['seeds_per_run']} seeds already in compost. Prune before adding more.")
        sys.exit(1)

    artifact = json.loads(seed_json)

    # Assign ID if not present
    if "seed_id" not in artifact:
        artifact["seed_id"] = _make_id("SEED", json.dumps(artifact, sort_keys=True))
    if "created_at" not in artifact:
        artifact["created_at"] = _now()
    if "actor" not in artifact:
        artifact["actor"] = "GOBLIN"
    if "authority" not in artifact:
        artifact["authority"] = False
    if "claim_status" not in artifact:
        artifact["claim_status"] = "NO_CLAIM"

    errors = _validate(artifact, "dream_seed_v0")
    if errors:
        print("SCHEMA ERRORS:", errors)
        sys.exit(1)

    path = _write_artifact(COMPOST_DIR, artifact["seed_id"], artifact)
    print(f"DreamSeed written: {path.name}")
    print(f"  claim_status: {artifact['claim_status']}  authority: {artifact['authority']}")


def cmd_insight(insight_json: str) -> None:
    """HER writes an InsightCandidate. Validates blindness: HER must reference seed_ids from compost."""
    existing = _read_artifacts(INSIGHTS_DIR)
    if len(existing) >= CADENCE["insights_max"]:
        print(f"CADENCE BLOCK: {CADENCE['insights_max']} insights already exist. HER must prune — only the best survive.")
        sys.exit(1)

    artifact = json.loads(insight_json)

    if "insight_id" not in artifact:
        artifact["insight_id"] = _make_id("INS", json.dumps(artifact, sort_keys=True))
    if "created_at" not in artifact:
        artifact["created_at"] = _now()
    if "actor" not in artifact:
        artifact["actor"] = "HER"
    if "authority" not in artifact:
        artifact["authority"] = False
    if "claim_status" not in artifact:
        artifact["claim_status"] = "CANDIDATE"

    # Blindness check: seed_ids must exist in compost
    seed_ids = {s.get("seed_id") for s in _read_artifacts(COMPOST_DIR)}
    for ref in artifact.get("derived_from_seed_ids", []):
        if ref not in seed_ids:
            print(f"BLINDNESS VIOLATION: seed_id {ref!r} not found in compost/. HER cannot fabricate lineage.")
            sys.exit(1)

    errors = _validate(artifact, "insight_candidate_v0")
    if errors:
        print("SCHEMA ERRORS:", errors)
        sys.exit(1)

    path = _write_artifact(INSIGHTS_DIR, artifact["insight_id"], artifact)
    print(f"InsightCandidate written: {path.name}")
    print(f"  derived_from: {artifact.get('derived_from_seed_ids')}")
    print(f"  claim_status: {artifact['claim_status']}  authority: {artifact['authority']}")


def cmd_claim(claim_json: str) -> None:
    """HAL writes a ClaimCandidate. Validates blindness: must reference insight from insights/."""
    existing = _read_artifacts(CLAIMS_DIR)
    if len(existing) >= CADENCE["claims_max"]:
        print(f"CADENCE BLOCK: {CADENCE['claims_max']} claims already exist. HAL must reject more than it admits.")
        sys.exit(1)

    artifact = json.loads(claim_json)

    if "claim_id" not in artifact:
        artifact["claim_id"] = _make_id("CLM", json.dumps(artifact, sort_keys=True))
    if "created_at" not in artifact:
        artifact["created_at"] = _now()
    if "actor" not in artifact:
        artifact["actor"] = "HAL"
    if "authority" not in artifact:
        artifact["authority"] = False
    if "claim_status" not in artifact:
        artifact["claim_status"] = "CLAIM_CANDIDATE"

    # Blindness check: insight_id must exist in insights/
    insight_ids = {i.get("insight_id") for i in _read_artifacts(INSIGHTS_DIR)}
    ref = artifact.get("derived_from_insight_id", "")
    if ref and ref not in insight_ids:
        print(f"BLINDNESS VIOLATION: insight_id {ref!r} not found in insights/. HAL cannot fabricate lineage.")
        sys.exit(1)

    errors = _validate(artifact, "claim_candidate_v0")
    if errors:
        print("SCHEMA ERRORS:", errors)
        sys.exit(1)

    path = _write_artifact(CLAIMS_DIR, artifact["claim_id"], artifact)
    print(f"ClaimCandidate written: {path.name}")
    print(f"  claim: {artifact.get('claim_sentence', '')[:80]}")
    print(f"  claim_status: {artifact['claim_status']}  authority: {artifact['authority']}")


def cmd_validate(validation_json: str) -> None:
    """MAYOR writes a ValidationReceiptCandidate. Blindness: MAYOR receives stripped ClaimCandidate only."""
    existing = [v for v in _read_artifacts(VALIDATION_DIR)]
    recent_yes = sum(1 for v in existing if v.get("mayor_verdict") in ("YES", "NO", "HOLD")
                     and v.get("created_at", "")[:10] == _now()[:10])
    if recent_yes >= CADENCE["validation_per_run"]:
        print(f"CADENCE BLOCK: MAYOR has already validated {CADENCE['validation_per_run']} claim(s) today.")
        sys.exit(1)

    artifact = json.loads(validation_json)

    if "validation_id" not in artifact:
        artifact["validation_id"] = _make_id("VAL", json.dumps(artifact, sort_keys=True))
    if "created_at" not in artifact:
        artifact["created_at"] = _now()
    if "actor" not in artifact:
        artifact["actor"] = "MAYOR"
    if "authority" not in artifact:
        artifact["authority"] = False
    if "ledger_effect" not in artifact:
        artifact["ledger_effect"] = "none"
    if "claim_status" not in artifact:
        artifact["claim_status"] = "VALIDATED_CLAIM_CANDIDATE"

    # Blindness check: claim_id must exist in claims/
    claim_ids = {c.get("claim_id") for c in _read_artifacts(CLAIMS_DIR)}
    ref = artifact.get("claim_id", "")
    if ref and ref not in claim_ids:
        print(f"BLINDNESS VIOLATION: claim_id {ref!r} not found in claims/. MAYOR cannot validate phantom claims.")
        sys.exit(1)

    errors = _validate(artifact, "validation_receipt_candidate_v0")
    if errors:
        print("SCHEMA ERRORS:", errors)
        sys.exit(1)

    path = _write_artifact(VALIDATION_DIR, artifact["validation_id"], artifact)
    verdict = artifact["mayor_verdict"]
    print(f"ValidationReceiptCandidate written: {path.name}")
    print(f"  mayor_verdict: {verdict}  next_gate: {artifact.get('next_gate')}")
    print(f"  ledger_effect: {artifact['ledger_effect']}  authority: {artifact['authority']}")

    if verdict == "YES":
        print()
        print("  → Ready for JM admission review. Run: python superteam_pipeline.py queue")


def cmd_queue() -> None:
    """Show ValidationReceiptCandidates with YES verdict awaiting JM admission review."""
    validations = _read_artifacts(VALIDATION_DIR)
    yes_items = [v for v in validations if v.get("mayor_verdict") == "YES"]
    hold_items = [v for v in validations if v.get("mayor_verdict") == "HOLD"]

    if not yes_items and not hold_items:
        print("Admission queue is empty. No YES or HOLD verdicts.")
        return

    print("── ADMISSION QUEUE ─────────────────────────────────────")
    if yes_items:
        print(f"\nREADY FOR JM REVIEW ({len(yes_items)}):")
        for v in yes_items:
            print(f"  {v['validation_id']}  claim: {v['claim_id']}")
            print(f"    reason: {v.get('reason', '')[:100]}")
            print(f"    dissent: {v.get('dissent', '') or 'none'}")
            print()

    if hold_items:
        print(f"\nHOLD — awaiting evidence ({len(hold_items)}):")
        for v in hold_items:
            print(f"  {v['validation_id']}  claim: {v['claim_id']}")
            print(f"    missing: {v.get('missing_evidence', '')[:100]}")
            print()

    print("Rule: Validated claim ≠ kernel truth. JM/reducer decides. Ledger moves by receipt and replay.")


def cmd_context(stage: str) -> None:
    """Print stripped artifact for a pipeline stage — enforces blindness in LLM prompts."""
    if stage == "her":
        seeds = _read_artifacts(COMPOST_DIR)
        print("── HER CONTEXT (DreamSeeds stripped for blindness) ─────")
        for s in seeds:
            print(json.dumps(_strip_for_her(s), indent=2, ensure_ascii=False))
    elif stage == "hal":
        insights = _read_artifacts(INSIGHTS_DIR)
        print("── HAL CONTEXT (InsightCandidates stripped for blindness) ─")
        for i in insights:
            print(json.dumps(_strip_for_hal(i), indent=2, ensure_ascii=False))
    elif stage == "mayor":
        claims = _read_artifacts(CLAIMS_DIR)
        print("── MAYOR CONTEXT (ClaimCandidates stripped for blindness) ─")
        for c in claims:
            print(json.dumps(_strip_for_mayor(c), indent=2, ensure_ascii=False))
    else:
        print(f"Unknown stage: {stage}. Use: her | hal | mayor")
        sys.exit(1)


# ── main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="HELEN Superteam MVP Pipeline — NON_SOVEREIGN, authority=false"
    )
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("status", help="Show pipeline state and cadence")
    sub.add_parser("queue", help="Show admission queue (YES verdicts)")

    p_seed = sub.add_parser("seed", help="GOBLIN: write a DreamSeed")
    p_seed.add_argument("seed_json", help="JSON string or @file.json")

    p_insight = sub.add_parser("insight", help="HER: write an InsightCandidate")
    p_insight.add_argument("insight_json", help="JSON string or @file.json")

    p_claim = sub.add_parser("claim", help="HAL: write a ClaimCandidate")
    p_claim.add_argument("claim_json", help="JSON string or @file.json")

    p_val = sub.add_parser("validate", help="MAYOR: write a ValidationReceiptCandidate")
    p_val.add_argument("validation_json", help="JSON string or @file.json")

    p_ctx = sub.add_parser("context", help="Print stripped artifact for LLM prompt")
    p_ctx.add_argument("stage", choices=["her", "hal", "mayor"])

    args = parser.parse_args()

    def _load_arg(raw: str) -> str:
        if raw.startswith("@"):
            return Path(raw[1:]).read_text()
        return raw

    if args.command == "status":
        cmd_status()
    elif args.command == "queue":
        cmd_queue()
    elif args.command == "seed":
        cmd_seed(_load_arg(args.seed_json))
    elif args.command == "insight":
        cmd_insight(_load_arg(args.insight_json))
    elif args.command == "claim":
        cmd_claim(_load_arg(args.claim_json))
    elif args.command == "validate":
        cmd_validate(_load_arg(args.validation_json))
    elif args.command == "context":
        cmd_context(args.stage)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
