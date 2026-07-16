#!/usr/bin/env python3
"""
fable_jmt_collapse.py — FABLE collapse layer for JMT Consulting

STRICT RULE (enforced in code):
  Only items with schema == "CHIDDUSH_RECEIPT_V0" are processed.
  Everything else is ignored with a clear message.

FABLE turns CHIDDUSH receipts into candidate dashboard cards.
FABLE does not create tasks, invoices, or deadlines.
Only JMT + Natalia decisions may become admin reality.

Usage:
  python tools/fable_jmt_collapse.py --receipts artifacts/chiddush/
  python tools/fable_jmt_collapse.py --receipt artifacts/chiddush/CHID-....json --format md
"""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "fable_jmt_collapse.prompt"

CATEGORIES = ["admin", "finance", "client", "legal", "operations", "strategy"]
OWNERS = ["Jean-Marie", "Natalia", "external"]
STATUSES = ["candidate", "needs_decision", "actionable", "blocked"]

def load_prompt() -> str:
    if PROMPT_PATH.exists():
        return PROMPT_PATH.read_text(encoding="utf-8")
    return "FABLE prompt not found. Using embedded rules."

def is_valid_chiddush(receipt: dict) -> bool:
    return (
        receipt.get("schema") == "CHIDDUSH_RECEIPT_V0"
        and receipt.get("authority") is False
        and receipt.get("claim") == "NO_CLAIM"
        and "invariant" in receipt
    )

def collapse_one(receipt: dict) -> dict[str, Any]:
    if not is_valid_chiddush(receipt):
        return {
            "error": "REJECTED: not a valid CHIDDUSH_RECEIPT_V0",
            "input": receipt.get("chiddush_id", "unknown")
        }

    invariant = receipt["invariant"]
    chiddush_id = receipt["chiddush_id"]

    # Simple heuristic classification (in real use: feed to Claude Fable with the prompt)
    text_lower = invariant.lower()
    category = "operations"
    if any(k in text_lower for k in ["invoice", "payment", "budget", "fee", "cash"]):
        category = "finance"
    elif any(k in text_lower for k in ["client", "customer", "meeting", "call"]):
        category = "client"
    elif any(k in text_lower for k in ["contract", "legal", "nda", "agreement"]):
        category = "legal"
    elif any(k in text_lower for k in ["strategy", "vision", "positioning", "market"]):
        category = "strategy"
    elif any(k in text_lower for k in ["admin", "email", "calendar", "process"]):
        category = "admin"

    owner = "Jean-Marie" if "jean" in text_lower or "jmt" in text_lower else "Natalia"

    # Default status — FABLE proposes, humans decide
    status = "candidate"
    if "block" in text_lower or "risk" in text_lower:
        status = "blocked"
    elif "decision" in text_lower or "choose" in text_lower:
        status = "needs_decision"

    card = {
        "card_id": f"CARD-{chiddush_id}",
        "from_chiddush": chiddush_id,
        "invariant": invariant,
        "category": category,
        "proposed_owner": owner,
        "status": status,
        "dashboard_title": invariant[:70] + ("..." if len(invariant) > 70 else ""),
        "suggested_action": f"Review invariant and decide next step for {owner}",
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "authority": False,
        "fable_claim": "FABLE_COLLAPSE_LAYER",
        "requires_human_confirmation": True,
        "metabolism_stage": "📖 FABLE (Translation)"
    }
    return card

def format_markdown(card: dict) -> str:
    return f"""### {card['dashboard_title']}
**Category:** {card['category']}  
**Owner:** {card['proposed_owner']}  
**Status:** {card['status']}  
**Source:** {card['from_chiddush']}

{card['invariant']}

**Suggested:** {card['suggested_action']}

> Requires human confirmation. FABLE does not admit to reality.
"""

def main():
    parser = argparse.ArgumentParser(description="FABLE collapse — only CHIDDUSH_RECEIPT_V0 allowed")
    parser.add_argument("--receipts", type=Path, help="Directory of CHIDDUSH receipts")
    parser.add_argument("--receipt", type=Path, help="Single CHIDDUSH receipt JSON")
    parser.add_argument("--format", choices=["json", "md", "both"], default="both")
    parser.add_argument("--out", type=Path, default=Path("artifacts/jmt_consulting"))
    args = parser.parse_args()

    receipts: list[dict] = []

    if args.receipt:
        data = json.loads(args.receipt.read_text())
        receipts.append(data)
    elif args.receipts:
        for f in sorted(args.receipts.glob("*.json")):
            try:
                receipts.append(json.loads(f.read_text()))
            except Exception:
                pass
    else:
        print("Provide --receipt or --receipts")
        return

    args.out.mkdir(parents=True, exist_ok=True)

    valid_cards = []
    rejected = []

    for r in receipts:
        if is_valid_chiddush(r):
            card = collapse_one(r)
            valid_cards.append(card)
        else:
            rejected.append(r.get("chiddush_id", str(r)[:60]))

    print(f"\nFABLE processed {len(receipts)} items")
    print(f"  Valid CHIDDUSH receipts collapsed: {len(valid_cards)}")
    if rejected:
        print(f"  Rejected (not CHIDDUSH_RECEIPT_V0): {len(rejected)}")

    # Output
    if valid_cards:
        if args.format in ("json", "both"):
            out_json = args.out / "fable_candidate_cards.json"
            out_json.write_text(json.dumps(valid_cards, indent=2, ensure_ascii=False))
            print(f"\nWrote: {out_json}")

        if args.format in ("md", "both"):
            md = "# FABLE Dashboard Candidates (JMT Consulting)\n\n"
            md += "Generated by FABLE collapse layer. Only from CHIDDUSH_RECEIPTs.\n\n"
            for c in valid_cards:
                md += format_markdown(c) + "\n"
            md += "\n---\nDecisions needed from JMT + Natalia only.\n"
            out_md = args.out / "fable_dashboard_candidates.md"
            out_md.write_text(md)
            print(f"Wrote: {out_md}")

    if rejected:
        print("\nRejected items (free talk / raw ideas / non-CHIDDUSH):")
        for r in rejected:
            print(f"  - {r}")

    print("\nRemember: FABLE collapse ⊬ ledger admission. Humans decide.")

if __name__ == "__main__":
    main()