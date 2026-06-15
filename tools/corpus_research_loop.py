"""
corpus_research_loop.py — 300-epoch image corpus reconciliation research loop.

AUTHORIZATION: JM Tassy 2026-06-15
  - 300 epochs = research only
  - Model: gemma4-12b:latest (mapped from helen-gemma4-12b-32k)
  - Mode: receipts-only, no commit, no ledger mutation, no file promotion
  - Output: promotion_plan_draft.json + scan_gap_notes.md
  - Canonical copy waits for explicit GO PROMOTE

WULmoji: 🌿🖼️➡️👁️➡️🧾➡️⭐ / 💻🖼️➡️👁️➡️🧾➡️⭐ / 🚫🔒🚫🎬

authority: false · sovereign: false · ledger_mutation: false
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

KB_ROOT = Path.home() / "HELEN_KB"
SOT_CANONICAL = Path(__file__).parent.parent / "helen_os/render/math_to_face_starter/refs/canonical"
FRAMEWORKS = Path(__file__).parent / "JMT_FRAMEWORKS_MANIFEST.json"
OUT_DIR = Path(__file__).parent.parent / "artifacts"
PLAN_PATH = OUT_DIR / "promotion_plan_draft.json"
NOTES_PATH = OUT_DIR / "scan_gap_notes.md"
RECEIPT_PATH = OUT_DIR / "corpus_research_receipts.ndjson"

OLLAMA_URL = "http://localhost:11434"
MODEL = "gemma4-12b:latest"
TOTAL_EPOCHS = 300
BATCH = 20  # pause every 20 epochs for drift check

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()

def _sha16(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:16]

def load_kb() -> dict:
    manifest = KB_ROOT / "manifests" / "kb_manifest.json"
    canonical = KB_ROOT / "manifests" / "canonical.json"
    image_cat = KB_ROOT / "manifests" / "image_catalog.json"

    kb: dict = {"entries": [], "canonical": [], "images": [], "sot_refs": []}
    if manifest.exists():
        kb["entries"] = json.loads(manifest.read_text()).get("entries", [])
    if canonical.exists():
        kb["canonical"] = json.loads(canonical.read_text()).get("entries", [])
    if image_cat.exists():
        kb["images"] = json.loads(image_cat.read_text()).get("entries", [])

    # SOT canonical refs
    if SOT_CANONICAL.exists():
        for subdir in sorted(SOT_CANONICAL.iterdir()):
            if subdir.is_dir():
                for f in sorted(subdir.glob("*.png")) + sorted(subdir.glob("*.jpg")):
                    kb["sot_refs"].append({"path": str(f), "era": subdir.name, "name": f.name})

    return kb

def build_epoch_prompt(epoch: int, kb: dict, prior_findings: list[dict]) -> str:
    images = kb["images"][:30]  # sample to stay within context
    sot = kb["sot_refs"][:20]
    canonical = kb["canonical"][:20]

    prior_summary = ""
    if prior_findings:
        last = prior_findings[-3:]
        prior_summary = "\n".join(
            f"- ep{f['epoch']}: {f['finding'][:120]}" for f in last
        )

    return f"""You are a non-sovereign corpus research agent analyzing HELEN OS image assets.

EPOCH: {epoch}/{TOTAL_EPOCHS}
TASK: Image corpus reconciliation — identify duplicates, gaps, and canonical promotion candidates.

KB IMAGES (sample, {len(kb['images'])} total):
{json.dumps([{'name': e['name'], 'tags': e.get('tags', [])[:4]} for e in images], indent=2)}

SOT CANONICAL REFS ({len(kb['sot_refs'])} total):
{json.dumps([{'name': r['name'], 'era': r['era']} for r in sot], indent=2)}

KB CANONICAL TAGGED ({len(kb['canonical'])} total):
{json.dumps([{'name': e['name'], 'path': e.get('path','')} for e in canonical[:10]], indent=2)}

PRIOR FINDINGS (last 3 epochs):
{prior_summary if prior_summary else '(none yet)'}

INSTRUCTIONS:
1. Identify potential duplicate image names or hash collisions
2. Find gaps: eras/themes in SOT refs missing from KB canonical
3. Flag images that ARE in KB but NOT in SOT canonical (promotion candidates)
4. Flag images in SOT canonical but NOT in KB (scan gaps)
5. Note any naming inconsistencies vs helen_<theme>_<descriptor>_<NN>.ext pattern

Return a compact JSON with exactly these fields:
{{
  "epoch": {epoch},
  "finding": "<one sentence key finding>",
  "duplicates": ["name1", "name2"],
  "gaps": ["era/theme missing"],
  "promotion_candidates": ["name with path"],
  "scan_gaps": ["sot file not in kb"],
  "naming_issues": ["item with issue"],
  "confidence": 0.0
}}
Return ONLY the JSON. No prose. No explanation."""

def _llm(prompt: str) -> str:
    try:
        r = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={"model": MODEL, "prompt": prompt, "stream": False, "options": {"temperature": 0.3}},
            timeout=90,
        )
        return r.json().get("response", "").strip()
    except Exception as e:
        return json.dumps({"error": str(e), "epoch": -1, "finding": "llm_unavailable",
                           "duplicates": [], "gaps": [], "promotion_candidates": [],
                           "scan_gaps": [], "naming_issues": [], "confidence": 0.0})

def parse_result(raw: str, epoch: int) -> dict:
    try:
        # strip markdown fences if present
        text = raw.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text.strip())
    except Exception:
        return {"epoch": epoch, "finding": f"parse_error: {raw[:80]}", "duplicates": [],
                "gaps": [], "promotion_candidates": [], "scan_gaps": [],
                "naming_issues": [], "confidence": 0.0}

def emit_receipt(epoch: int, result: dict) -> dict:
    receipt = {
        "schema": "CORPUS_RESEARCH_RECEIPT_V0",
        "epoch": epoch,
        "ts": _now(),
        "model": MODEL,
        "finding_sha": _sha16(result.get("finding", "")),
        "finding": result.get("finding", ""),
        "duplicate_count": len(result.get("duplicates", [])),
        "gap_count": len(result.get("gaps", [])),
        "promo_candidates": len(result.get("promotion_candidates", [])),
        "scan_gaps": len(result.get("scan_gaps", [])),
        "authority": False,
        "sovereign": False,
        "ledger_mutation": False,
    }
    OUT_DIR.mkdir(exist_ok=True)
    with open(RECEIPT_PATH, "a") as f:
        f.write(json.dumps(receipt, ensure_ascii=False) + "\n")
    return receipt

def synthesize(findings: list[dict]) -> tuple[dict, str]:
    all_duplicates: set[str] = set()
    all_gaps: set[str] = set()
    all_promo: set[str] = set()
    all_scan_gaps: set[str] = set()
    all_naming: set[str] = set()

    for f in findings:
        all_duplicates.update(f.get("duplicates", []))
        all_gaps.update(f.get("gaps", []))
        all_promo.update(f.get("promotion_candidates", []))
        all_scan_gaps.update(f.get("scan_gaps", []))
        all_naming.update(f.get("naming_issues", []))

    plan = {
        "schema": "CORPUS_PROMOTION_PLAN_DRAFT_V0",
        "generated": _now(),
        "total_epochs": len(findings),
        "model": MODEL,
        "authority": False,
        "sovereign": False,
        "promotion_status": "DRAFT — awaiting GO PROMOTE",
        "duplicates_detected": sorted(all_duplicates),
        "era_gaps": sorted(all_gaps),
        "promotion_candidates": sorted(all_promo),
        "scan_gaps": sorted(all_scan_gaps),
        "naming_issues": sorted(all_naming),
        "receipt_log": str(RECEIPT_PATH),
    }

    def _bullet(items, none_msg="(none detected)"):
        return [f"- {x}" for x in sorted(items)] if items else [none_msg]

    notes_lines = [
        "# scan_gap_notes.md",
        f"Generated: {_now()}",
        f"Epochs: {len(findings)} / {TOTAL_EPOCHS}",
        f"Model: {MODEL}",
        "",
        "## Era gaps (SOT canonical has these, KB missing)",
    ] + _bullet(all_gaps) + [
        "",
        "## Scan gaps (SOT canonical files not in KB manifest)",
    ] + _bullet(all_scan_gaps) + [
        "",
        "## Potential duplicates",
    ] + _bullet(all_duplicates) + [
        "",
        "## Naming issues (non-canonical pattern)",
    ] + _bullet(all_naming) + [
        "",
        "## Promotion candidates (in KB, not yet in SOT canonical)",
    ] + _bullet(all_promo) + [
        "",
        "## Status",
        "DRAFT — canonical copy waits for explicit GO PROMOTE",
        "authority: false · sovereign: false · ledger_mutation: false",
    ]

    return plan, "\n".join(notes_lines)

def main():
    print(f"[corpus] 300-epoch research loop · model={MODEL} · authority=false")
    print(f"[corpus] KB root: {KB_ROOT}")
    print(f"[corpus] SOT canonical: {SOT_CANONICAL}")
    print(f"[corpus] Output: {PLAN_PATH}, {NOTES_PATH}")
    print()

    kb = load_kb()
    print(f"[corpus] KB loaded: {len(kb['entries'])} total, {len(kb['images'])} images, "
          f"{len(kb['canonical'])} canonical, {len(kb['sot_refs'])} SOT refs")

    findings: list[dict] = []

    for epoch in range(1, TOTAL_EPOCHS + 1):
        prompt = build_epoch_prompt(epoch, kb, findings)
        raw = _llm(prompt)
        result = parse_result(raw, epoch)
        result["epoch"] = epoch
        findings.append(result)
        receipt = emit_receipt(epoch, result)

        print(f"[corpus] ep{epoch:>3} · {result.get('finding','')[:70]} "
              f"· promo={receipt['promo_candidates']} gaps={receipt['gap_count']}")

        if epoch % BATCH == 0:
            plan, notes = synthesize(findings)
            OUT_DIR.mkdir(exist_ok=True)
            PLAN_PATH.write_text(json.dumps(plan, indent=2, ensure_ascii=False))
            NOTES_PATH.write_text(notes)
            print(f"[corpus] CHECKPOINT ep{epoch} · plan→{PLAN_PATH} · notes→{NOTES_PATH}")
            print(f"[corpus] duplicates={len(plan['duplicates_detected'])} "
                  f"gaps={len(plan['era_gaps'])} promo={len(plan['promotion_candidates'])}")

    # Final synthesis
    plan, notes = synthesize(findings)
    PLAN_PATH.write_text(json.dumps(plan, indent=2, ensure_ascii=False))
    NOTES_PATH.write_text(notes)

    print()
    print(f"[corpus] COMPLETE · 300 epochs · receipts → {RECEIPT_PATH}")
    print(f"[corpus] promotion_plan_draft.json → {PLAN_PATH}")
    print(f"[corpus] scan_gap_notes.md → {NOTES_PATH}")
    print(json.dumps({
        "epochs": len(findings),
        "duplicates": len(plan["duplicates_detected"]),
        "era_gaps": len(plan["era_gaps"]),
        "promotion_candidates": len(plan["promotion_candidates"]),
        "scan_gaps": len(plan["scan_gaps"]),
        "authority": False,
        "sovereign": False,
        "status": "DRAFT — awaiting GO PROMOTE",
    }, indent=2))

if __name__ == "__main__":
    main()
