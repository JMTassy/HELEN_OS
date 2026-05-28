#!/usr/bin/env python3
"""
HELEN_DATASET_V0 curator — STEP 2 of the HER fine-tuning roadmap.

Reads from known high-signal sources in this repo and classifies
each entry into approved / rejected / boundary according to HAL
thresholds. Outputs JSONL files suitable for LoRA training.

Sources (in priority order):
  1. oracle_town/skills/ops/dan_goblin/brainstorm/  — GOBLIN_EPOCH_V1
  2. GOVERNANCE/TRANCHE_RECEIPTS/                   — tranche receipts
  3. GOVERNANCE/CLOSURES/                           — closure receipts
  4. GOVERNANCE/GEMMA_PROPOSALS/                    — raw HER proposals (if present)

Excluded:
  - town/ledger_v1.ndjson user_msg / turn entries (raw chat entropy)
  - Entries with p_harm > HAL_HARM_CEILING
  - Entries with cross-session contamination markers

Usage:
  python tools/dataset_curator_v0.py --dry-run
  python tools/dataset_curator_v0.py --output dataset/
  python tools/dataset_curator_v0.py --output dataset/ --source goblin
  python tools/dataset_curator_v0.py --output dataset/ --min-p-true 0.70

Authority: NON_SOVEREIGN  Canon: NO_SHIP  Produces: DATASET_ARTIFACT_V0
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DATASET_DIR = REPO_ROOT / "dataset"

# HAL thresholds — mirror goblin_batch_runner.py
HAL_PASS_P_TRUE = 0.65
HAL_WARN_P_TRUE = 0.45
HAL_HARM_CEILING = 0.15  # stricter than HAL_ESCALATE — training data must be clean

CROSS_SESSION_MARKERS = [
    "b3415eb3edfb",       # parallel session cum_hash (per CLAUDE.md)
    "helen_os_v1",        # parallel tree path
    "6eede55",            # non-existent commit referenced in E22
    "E20.open_seams",     # contaminated seam identifier
]


def sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def has_cross_session_contamination(text: str) -> bool:
    return any(m in text for m in CROSS_SESSION_MARKERS)


def classify_hal(p_true: float, p_harm: float) -> str:
    """Returns approved / boundary / rejected."""
    if p_harm > HAL_HARM_CEILING:
        return "rejected"
    if p_true >= HAL_PASS_P_TRUE:
        return "approved"
    if p_true >= HAL_WARN_P_TRUE:
        return "boundary"
    return "rejected"


# ── Source readers ─────────────────────────────────────────────────────────────

def read_goblin_brainstorm() -> list[dict]:
    """GOBLIN_EPOCH_V1 entries from brainstorm/."""
    brainstorm_dir = REPO_ROOT / "oracle_town" / "skills" / "ops" / "dan_goblin" / "brainstorm"
    entries = []
    for path in sorted(brainstorm_dir.glob("**/*.json")):
        try:
            raw = path.read_text(encoding="utf-8")
            if has_cross_session_contamination(raw):
                continue
            d = json.loads(raw)
            # Handle both GOBLIN_EPOCH_V1 (from batch runner JSONL) and older story format
            her = d.get("her_scoring", {})
            hal = d.get("hal_verdict", {})
            p_true = float(her.get("p_true", 0.0))
            p_harm = float(her.get("p_harm", 0.0))  # absent = assume clean
            hal_verdict = hal.get("verdict", "UNKNOWN") if isinstance(hal, dict) else str(hal)

            stmt = d.get("communication_act", {}).get("statement", "") or d.get("statement", "")
            claim = d.get("communication_act", {}).get("embedded_claim", "") or d.get("embedded_claim", "")
            lateral = d.get("communication_act", {}).get("lateral_angle", "") or d.get("lateral_angle", "")

            if not stmt:
                continue

            entries.append({
                "source": "goblin_brainstorm",
                "source_file": str(path.relative_to(REPO_ROOT)),
                "schema": d.get("schema_version", "GOBLIN_EPOCH_V1"),
                "p_true": p_true,
                "p_harm": p_harm,
                "hal_verdict": hal_verdict,
                "classification": classify_hal(p_true, p_harm),
                "content": {
                    "statement": stmt,
                    "embedded_claim": claim,
                    "lateral_angle": lateral,
                    "best_explanation": her.get("best_explanation", ""),
                    "evidence_for": her.get("evidence_for", []),
                    "evidence_against": her.get("evidence_against", []),
                },
                "training_pair": {
                    "prompt": (
                        f"Generate a lateral architectural insight about HELEN OS.\n"
                        f"Angle: {lateral}"
                    ),
                    "completion": stmt,
                },
            })
        except (json.JSONDecodeError, KeyError, ValueError):
            continue
    return entries


def read_tranche_receipts() -> list[dict]:
    """GOVERNANCE/TRANCHE_RECEIPTS/ — governance exemplars."""
    receipts_dir = REPO_ROOT / "GOVERNANCE" / "TRANCHE_RECEIPTS"
    entries = []
    if not receipts_dir.exists():
        return entries
    for path in sorted(receipts_dir.glob("*.json")):
        try:
            raw = path.read_text(encoding="utf-8")
            if has_cross_session_contamination(raw):
                continue
            d = json.loads(raw)
            verdict = d.get("verdict", d.get("mayor_decision", ""))
            hypothesis = d.get("hypothesis", "")
            if not hypothesis:
                continue
            # Tranche receipts with SHIP verdict → approved governance writing examples
            classification = "approved" if verdict in ("SHIP", "SHIPPED", "PASS") else "boundary"
            entries.append({
                "source": "tranche_receipt",
                "source_file": str(path.relative_to(REPO_ROOT)),
                "schema": d.get("schema_name", d.get("schema_version", "TRANCHE_RECEIPT")),
                "p_true": None,
                "p_harm": None,
                "hal_verdict": verdict,
                "classification": classification,
                "content": {
                    "hypothesis": hypothesis,
                    "verdict": verdict,
                    "note": d.get("note", ""),
                },
                "training_pair": {
                    "prompt": (
                        "Write a HELEN OS governance receipt hypothesis for:\n"
                        f"{hypothesis[:200]}"
                    ),
                    "completion": hypothesis,
                },
            })
        except (json.JSONDecodeError, KeyError):
            continue
    return entries


def read_gemma_proposals() -> list[dict]:
    """GOVERNANCE/GEMMA_PROPOSALS/ — HER proposal envelopes (if present)."""
    proposals_dir = REPO_ROOT / "GOVERNANCE" / "GEMMA_PROPOSALS"
    entries = []
    if not proposals_dir.exists():
        return entries
    for path in sorted(proposals_dir.glob("*.json"))[:200]:  # cap at 200
        try:
            raw = path.read_text(encoding="utf-8")
            if has_cross_session_contamination(raw):
                continue
            d = json.loads(raw)
            if d.get("schema_name") != "GEMMA_PROPOSAL_RAW_V1":
                continue
            if not d.get("envelope_complete"):
                continue
            proposal = d.get("proposal_text", "")
            uncertainty = d.get("uncertainty_text", "")
            if not proposal or len(proposal) < 50:
                continue
            entries.append({
                "source": "gemma_proposal",
                "source_file": str(path.relative_to(REPO_ROOT)),
                "schema": "GEMMA_PROPOSAL_RAW_V1",
                "p_true": None,
                "p_harm": None,
                "hal_verdict": "ENVELOPE_COMPLETE",
                "classification": "approved",
                "content": {
                    "proposal": proposal,
                    "uncertainty": uncertainty,
                    "hal_questions": d.get("hal_questions", ""),
                },
                "training_pair": {
                    "prompt": (
                        f"Generate a HER-layer HELEN OS proposal.\n"
                        f"Model: {d.get('model_id', 'unknown')}"
                    ),
                    "completion": (
                        f"[PROPOSAL]\n{proposal}\n\n"
                        f"[UNCERTAINTY]\n{uncertainty}"
                    ),
                },
            })
        except (json.JSONDecodeError, KeyError):
            continue
    return entries


# ── Main curator ───────────────────────────────────────────────────────────────

SOURCES = {
    "goblin": read_goblin_brainstorm,
    "tranche": read_tranche_receipts,
    "gemma": read_gemma_proposals,
}


def curate(output_dir: Path, sources: list[str], min_p_true: float,
           dry_run: bool) -> dict:
    all_entries: list[dict] = []
    for name in sources:
        fn = SOURCES.get(name)
        if fn is None:
            print(f"[curator] unknown source {name!r}, skipping", file=sys.stderr)
            continue
        batch = fn()
        print(f"[curator] {name:12s}  read {len(batch):4d} candidates")
        all_entries.extend(batch)

    # Apply min_p_true filter (only where p_true is known)
    filtered = []
    for e in all_entries:
        pt = e.get("p_true")
        if pt is not None and pt < min_p_true:
            e["classification"] = "rejected"
        filtered.append(e)

    counts: dict[str, int] = {"approved": 0, "boundary": 0, "rejected": 0}
    for e in filtered:
        counts[e["classification"]] = counts.get(e["classification"], 0) + 1

    print(f"[curator] total={len(filtered)}  "
          f"approved={counts['approved']}  "
          f"boundary={counts['boundary']}  "
          f"rejected={counts['rejected']}")

    if dry_run:
        print("[curator] DRY-RUN — no files written")
        return counts

    # Write JSONL per class
    output_dir.mkdir(parents=True, exist_ok=True)
    for cls in ("approved", "boundary", "rejected"):
        cls_entries = [e for e in filtered if e["classification"] == cls]
        if not cls_entries:
            continue
        out = output_dir / cls / "exemplars.jsonl"
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            for e in cls_entries:
                f.write(json.dumps(e, ensure_ascii=False) + "\n")
        print(f"[curator] wrote {len(cls_entries):4d} → {out.relative_to(REPO_ROOT)}")

    # Write curation receipt
    receipt = {
        "schema": "DATASET_CURATION_RECEIPT_V0",
        "authority": "NON_SOVEREIGN",
        "canon": "NO_SHIP",
        "curated_at": now_iso(),
        "sources": sources,
        "min_p_true": min_p_true,
        "hal_harm_ceiling": HAL_HARM_CEILING,
        "counts": counts,
        "total": len(filtered),
        "output_dir": str(output_dir.relative_to(REPO_ROOT)),
        "training_objective": "HER proposal-generation behavior under HELEN constraints",
        "not_for": ["sovereign verdicts", "ledger writes", "kernel mutation"],
    }
    receipt_path = output_dir / "receipts" / "curation_receipt.json"
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(receipt, indent=2, ensure_ascii=False))
    print(f"[curator] receipt → {receipt_path.relative_to(REPO_ROOT)}")

    return counts


def main() -> int:
    ap = argparse.ArgumentParser(description="HELEN_DATASET_V0 curator")
    ap.add_argument("--output", type=Path, default=DATASET_DIR,
                    help=f"Output directory (default: {DATASET_DIR})")
    ap.add_argument("--source", nargs="+", default=list(SOURCES.keys()),
                    choices=list(SOURCES.keys()),
                    help="Sources to read (default: all)")
    ap.add_argument("--min-p-true", type=float, default=HAL_PASS_P_TRUE,
                    help=f"Minimum p_true for approved class (default: {HAL_PASS_P_TRUE})")
    ap.add_argument("--dry-run", action="store_true",
                    help="Read and classify but do not write")
    args = ap.parse_args()

    print(f"[curator] HELEN_DATASET_V0 curation")
    print(f"[curator] output={args.output}  min_p_true={args.min_p_true}  dry_run={args.dry_run}")
    print(f"[curator] sources={args.source}")
    print()

    counts = curate(args.output, args.source, args.min_p_true, args.dry_run)
    total = counts.get("approved", 0) + counts.get("boundary", 0)
    if total < 20:
        print(f"[curator] WARNING: only {total} usable exemplars — target 100-500", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
