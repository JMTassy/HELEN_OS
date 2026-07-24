#!/usr/bin/env python3
"""
helen collapse — JM's collapse act for the quantum garden

Usage:
    python garden_collapse.py <block_hash_prefix_or_artifact_id>
    python garden_collapse.py --list         # show collapse candidates
    python garden_collapse.py --dry-run <id> # preview without writing

Authority: NON_SOVEREIGN  Ledger effect: NONE
This tool freezes a garden block and copies it to temple/proposals/.
The actual ledger entry requires JM running helen_say manually — that is the castle gate.

Collapse selects. It never deletes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

SWARM_ROOT = Path(__file__).resolve().parent
REPO_ROOT = SWARM_ROOT.parent.parent.parent
STATE_FILE = SWARM_ROOT / "garden_state.json"
PROPOSALS_DIR = REPO_ROOT / "temple" / "proposals"
SCHEMAS_ROOT = REPO_ROOT / "schemas" / "helen_superteam"

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()

def _hash8(content: str) -> str:
    return hashlib.sha256(content.encode()).hexdigest()[:8]

def load_state() -> dict:
    if not STATE_FILE.exists():
        print("ERROR: garden_state.json not found. Run garden_tick.py first.")
        sys.exit(1)
    return json.loads(STATE_FILE.read_text())

def save_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False))

def find_artifact(state: dict, query: str) -> tuple[str, dict] | None:
    """Find artifact by ID prefix or content hash prefix."""
    for artifact_id, info in state["artifacts"].items():
        if (artifact_id.startswith(query) or
            info.get("content_hash", "").startswith(query) or
            artifact_id == query):
            return artifact_id, info
    return None

def build_ancestry(state: dict, artifact_id: str, artifact: dict) -> list[str]:
    """Trace full ancestry chain of parent hashes."""
    chain = [state["artifacts"].get(artifact_id, {}).get("content_hash", "")]

    # Walk derived_from references
    derived = (
        artifact.get("derived_from_seed_ids", []) +
        ([artifact.get("derived_from_insight_id")] if artifact.get("derived_from_insight_id") else [])
    )
    for parent_id in derived:
        parent_info = state["artifacts"].get(parent_id)
        if parent_info:
            chain.append(parent_info.get("content_hash", ""))

    return [h for h in chain if h]

def cmd_list(state: dict) -> None:
    print("── COLLAPSE CANDIDATES ──────────────────────────────────")
    print("(Non-composted, non-collapsed artifacts in the garden)\n")

    for artifact_id, info in state["artifacts"].items():
        if info.get("composted") or info.get("collapsed"):
            continue
        age = state["current_cycle"] - info["created_cycle"]
        cycles_left = max(0, 7 - age)
        path = REPO_ROOT / info["path"]
        if not path.exists():
            continue

        print(f"  {artifact_id}")
        print(f"    type:   {info['artifact_type']}")
        print(f"    npc:    {info['npc']}")
        print(f"    age:    {age} cycles ({cycles_left} cycles until compost)")
        print(f"    hash:   {info['content_hash'][:20]}...")
        print()

    print("To collapse: python garden_collapse.py <artifact_id_or_hash_prefix>")

def collapse(artifact_id: str, info: dict, artifact: dict, state: dict, dry_run: bool) -> None:
    content_hash = info.get("content_hash", "")
    collapse_id = f"COL-{_hash8(f'{artifact_id}:{content_hash}')}"
    artifact_type_map = {
        "DreamSeed": "DreamSeed",
        "InsightCandidate": "InsightCandidate",
        "ClaimCandidate": "ClaimCandidate",
    }
    block_type = artifact_type_map.get(info["artifact_type"], info["artifact_type"])
    ancestry = build_ancestry(state, artifact_id, artifact)

    # Find siblings (same type, not this one, not composted/collapsed)
    siblings = [
        aid for aid, a in state["artifacts"].items()
        if a["artifact_type"] == info["artifact_type"]
        and aid != artifact_id
        and not a.get("composted")
        and not a.get("collapsed")
    ]

    receipt = {
        "collapse_id": collapse_id,
        "block_hash": content_hash,
        "block_id": artifact_id,
        "block_type": block_type,
        "ancestry_chain": ancestry,
        "collapsed_at": _now(),
        "collapsed_by": "JM",
        "destination": "temple/proposals/",
        "siblings_preserved": siblings,
        "authority": False,
        "ledger_effect": "none",
        "actor": "COLLAPSE_CLI",
        "note": f"Collapsed from garden cycle {state['current_cycle']}. Siblings remain in superposition.",
    }

    proposal_dir = PROPOSALS_DIR / artifact_id
    receipt_path = proposal_dir / "COLLAPSE_RECEIPT_V1.json"
    artifact_path = proposal_dir / f"{artifact_id}.json"

    print(f"COLLAPSE: {artifact_id}")
    print(f"  type:      {block_type}")
    print(f"  hash:      {content_hash[:20]}...")
    print(f"  ancestry:  {len(ancestry)} hashes")
    print(f"  siblings preserved in Z2: {len(siblings)}")
    print(f"  destination: {proposal_dir.relative_to(REPO_ROOT)}")
    print()

    if dry_run:
        print("[DRY RUN] Would write:")
        print(f"  {receipt_path.relative_to(REPO_ROOT)}")
        print(f"  {artifact_path.relative_to(REPO_ROOT)}")
        print()
        print("Next step (manual): helen_say '...' to produce ledger entry (JM's act)")
        return

    # Write to temple/proposals/
    proposal_dir.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(receipt, indent=2))
    artifact_path.write_text(json.dumps(artifact, indent=2))

    # Mark as collapsed in state
    state["artifacts"][artifact_id]["collapsed"] = True
    state["artifacts"][artifact_id]["collapse_id"] = collapse_id
    state["artifacts"][artifact_id]["collapsed_at"] = _now()
    save_state(state)

    print(f"Written:")
    print(f"  {receipt_path.relative_to(REPO_ROOT)}")
    print(f"  {artifact_path.relative_to(REPO_ROOT)}")
    print()
    print("Next step — JM's act (manual, to produce ledger entry):")
    print(f"  python tools/helen_say.py 'COLLAPSE:{collapse_id}' --op fetch")
    print()
    print("Rule: Collapse selects. It never deletes. Siblings remain in Z2.")

def main() -> None:
    parser = argparse.ArgumentParser(
        description="helen collapse — quantum garden collapse act. NON_SOVEREIGN."
    )
    parser.add_argument("query", nargs="?", help="Artifact ID or hash prefix to collapse")
    parser.add_argument("--list", action="store_true", help="List collapse candidates")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    args = parser.parse_args()

    state = load_state()

    if args.list or not args.query:
        cmd_list(state)
        return

    result = find_artifact(state, args.query)
    if result is None:
        print(f"ERROR: No artifact found matching {args.query!r}")
        print("Run --list to see available candidates.")
        sys.exit(1)

    artifact_id, info = result

    if info.get("composted"):
        print(f"ERROR: {artifact_id} has already been composted. Content withdrawn. Hash retained.")
        sys.exit(1)
    if info.get("collapsed"):
        print(f"ERROR: {artifact_id} has already been collapsed to {info.get('collapse_id')}.")
        sys.exit(1)

    path = REPO_ROOT / info["path"]
    if not path.exists():
        print(f"ERROR: Artifact file not found at {path}")
        sys.exit(1)

    artifact = json.loads(path.read_text())
    collapse(artifact_id, info, artifact, state, args.dry_run)

if __name__ == "__main__":
    main()
