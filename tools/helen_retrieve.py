"""
helen_retrieve — keyword-based retrieval from HELEN_KB + JMT framework catalog.

Implements the RETRIEVE → INJECT step of the KB pipeline:

  SCAN → INDEX → RETRIEVE → INJECT → RESPOND → RECEIPT → VERIFY → IMPROVE

Usage:
    python3 tools/helen_retrieve.py "cyberpunk assets"
    python3 tools/helen_retrieve.py "governance framework"
    python3 tools/helen_retrieve.py "emotions images" --type image
    python3 tools/helen_retrieve.py "list" --all

Output: JSON to stdout, one block ready for context injection.

NO RECEIPT = NO CLAIM: this script retrieves only. It does not write to the
ledger and does not issue receipts. Call tools/helen_say.py for admitted writes.
"""

import argparse
import json
import sys
from pathlib import Path

KB_ROOT = Path.home() / "HELEN_KB"
FRAMEWORKS_MANIFEST = Path(__file__).parent / "JMT_FRAMEWORKS_MANIFEST.json"


def load_manifest(kb_root: Path) -> list[dict]:
    p = kb_root / "manifests" / "kb_manifest.json"
    if not p.exists():
        return []
    return json.loads(p.read_text(encoding="utf-8")).get("entries", [])


def load_frameworks(manifest_path: Path) -> list[dict]:
    if not manifest_path.exists():
        return []
    d = json.loads(manifest_path.read_text(encoding="utf-8"))
    return d.get("frameworks", [])


def tokenize(query: str) -> list[str]:
    return [w.lower().strip(".,!?;:\"'") for w in query.split() if w]


def score_asset(entry: dict, tokens: list[str]) -> int:
    text = " ".join(entry.get("tags", [])) + " " + entry.get("name", "").lower()
    return sum(1 for t in tokens if t in text)


def score_framework(fw: dict, tokens: list[str]) -> int:
    keywords = [k.lower() for k in fw.get("trigger_keywords", [])]
    text = (fw.get("name", "") + " " + fw.get("domain", "") + " " + fw.get("purpose", "")).lower()
    kw_hits = sum(1 for t in tokens if t in keywords)
    text_hits = sum(1 for t in tokens if t in text)
    return kw_hits * 2 + text_hits


def retrieve(query: str, asset_type: str | None = None, top_k: int = 5,
             kb_root: Path = KB_ROOT) -> dict:
    tokens = tokenize(query)
    entries = load_manifest(kb_root)
    frameworks = load_frameworks(FRAMEWORKS_MANIFEST)

    # Asset retrieval
    if asset_type:
        entries = [e for e in entries if e.get("type") == asset_type]

    scored_assets = [(score_asset(e, tokens), e) for e in entries]
    scored_assets = [(s, e) for s, e in scored_assets if s > 0]
    scored_assets.sort(key=lambda x: -x[0])
    top_assets = [e for _, e in scored_assets[:top_k]]

    # Framework retrieval
    scored_fws = [(score_framework(fw, tokens), fw) for fw in frameworks]
    scored_fws = [(s, fw) for s, fw in scored_fws if s > 0]
    scored_fws.sort(key=lambda x: -x[0])
    top_fws = [fw for _, fw in scored_fws[:3]]

    return {
        "query": query,
        "tokens": tokens,
        "assets": [
            {
                "id": e.get("id"),
                "name": e["name"],
                "type": e["type"],
                "path": e["path"],
                "tags": e.get("tags", []),
                "helen_canonical": e.get("helen_canonical", False),
            }
            for e in top_assets
        ],
        "frameworks": [
            {
                "id": fw.get("id"),
                "name": fw.get("name"),
                "domain": fw.get("domain"),
                "purpose": fw.get("purpose"),
                "key_concepts": fw.get("key_concepts", []),
            }
            for fw in top_fws
        ],
        "authority": "NON_SOVEREIGN",
        "ledger_effect": "NONE",
        "inject_ready": True,
    }


def list_all(kb_root: Path = KB_ROOT) -> dict:
    entries = load_manifest(kb_root)
    frameworks = load_frameworks(FRAMEWORKS_MANIFEST)
    by_type: dict[str, int] = {}
    for e in entries:
        t = e.get("type", "other")
        by_type[t] = by_type.get(t, 0) + 1
    return {
        "total_assets": len(entries),
        "by_type": by_type,
        "total_frameworks": len(frameworks),
        "frameworks": [{"id": fw.get("id"), "name": fw.get("name"), "domain": fw.get("domain")}
                       for fw in frameworks],
    }


def main():
    parser = argparse.ArgumentParser(description="Retrieve from HELEN KB + framework catalog.")
    parser.add_argument("query", nargs="?", default="", help="Natural-language retrieval query")
    parser.add_argument("--type", dest="asset_type", choices=["image", "audio", "video", "document"],
                        help="Filter assets by type")
    parser.add_argument("--top", type=int, default=5, help="Max assets to return (default: 5)")
    parser.add_argument("--all", dest="list_all", action="store_true", help="List full KB index")
    parser.add_argument("--kb", type=Path, default=KB_ROOT, help=f"KB root (default: {KB_ROOT})")
    args = parser.parse_args()

    if args.list_all:
        result = list_all(args.kb)
    elif not args.query:
        parser.print_help()
        sys.exit(0)
    else:
        result = retrieve(args.query, asset_type=args.asset_type, top_k=args.top, kb_root=args.kb)

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
