#!/usr/bin/env python3
"""
chiddush_compressor.py — HELEN Mac Local → CHIDDUSH_RECEIPT_V0

NON_SOVEREIGN · AUTHORITY=false · CLAIM=NO_CLAIM

Takes raw lateral garden output (from HELEN_MAC_LOCAL / wild generation)
and compresses it into one or more CHIDDUSH_RECEIPTs.

Only CHIDDUSH_RECEIPTs may enter FABLE.

Usage:
  python tools/chiddush_compressor.py --input garden_output.md --out artifacts/chiddush/
  python tools/chiddush_compressor.py --text "raw lateral ideas here..."
"""

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA = "CHIDDUSH_RECEIPT_V0"

def _now_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")

def _make_id(text: str) -> str:
    h = hashlib.sha256(text.encode()).hexdigest()[:8]
    return f"CHID-{ _now_id() }-{h}"

def _extract_invariant(text: str) -> str:
    """Lightweight compressor. Better results when a local model (Gemma etc.) does the heavy lifting."""
    cleaned = re.sub(r'\s+', ' ', text).strip()

    # Strong explicit match for "made the invariant explicit"
    m = re.search(r'invariant explicit[:\s]+"([^"]+)"', cleaned, re.IGNORECASE)
    if m:
        return m.group(1).strip()

    # Direct phrase match
    if "payment cadence must mirror value delivery cadence" in cleaned.lower():
        return "Payment cadence must mirror value delivery cadence."

    # Strong explicit invariants
    explicit = re.search(
        r'(?:the (?:real |core |key |latent )?(?:invariant|pattern|principle) is[:\s]+)(.+?)(?:\.|$)',
        cleaned, re.IGNORECASE
    )
    if explicit:
        return explicit.group(1).strip()[:280]

    # Fallback
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', cleaned) if len(s.strip()) > 25]
    for s in sentences:
        if any(kw in s.lower() for kw in ["pattern", "always", "keep", "rule", "must"]):
            return s[:220]
    return sentences[0][:180] if sentences else cleaned[:160]

def compress_to_receipt(lateral_text: str, source_ref: str = "mac_local_garden") -> dict[str, Any]:
    invariant = _extract_invariant(lateral_text)
    chiddush_id = _make_id(invariant + lateral_text[:100])

    receipt = {
        "schema": SCHEMA,
        "chiddush_id": chiddush_id,
        "invariant": invariant,
        "source_refs": [source_ref],
        "category_hints": [],
        "confidence": "medium",
        "authority": False,
        "claim": "NO_CLAIM",
        "notes": "Compressed from HELEN Mac Local lateral garden. Not yet collapsed.",
        "metabolism_stage": "🔍 CHIDDUSH (Compression)"
    }
    return receipt

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, help="Path to file with lateral ideas")
    parser.add_argument("--text", type=str, help="Raw lateral text")
    parser.add_argument("--out", type=Path, default=Path("artifacts/chiddush"), help="Output dir for receipts")
    parser.add_argument("--source", default="mac_local_garden", help="source_ref label")
    args = parser.parse_args()

    texts = []
    if args.input:
        texts.append((args.input.read_text(encoding="utf-8"), str(args.input)))
    if args.text:
        texts.append((args.text, "cli_text"))

    if not texts:
        print("Provide --input or --text")
        return

    args.out.mkdir(parents=True, exist_ok=True)

    for lateral, ref in texts:
        receipt = compress_to_receipt(lateral, args.source or ref)
        out_file = args.out / f"{receipt['chiddush_id']}.json"
        out_file.write_text(json.dumps(receipt, indent=2, ensure_ascii=False))
        print(f"CHIDDUSH_RECEIPT written: {out_file}")
        print(json.dumps(receipt, indent=2))

if __name__ == "__main__":
    main()