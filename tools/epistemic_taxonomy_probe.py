#!/usr/bin/env python3
"""
tools/epistemic_taxonomy_probe.py — HELEN epistemic failure taxonomy oracle.
authority: NONE · NON_SOVEREIGN

Classifies artifacts in the repo by epistemic failure class:
  CLEAN               commit_sha matches HEAD
  MISSING_PROVENANCE  no .provenance.json sidecar found
  MISSING_COMMIT_SHA  sidecar exists but has no commit_sha field
  TEMPORAL_STALENESS  commit_sha present but ≠ HEAD

Usage:
  python3 tools/epistemic_taxonomy_probe.py --scan oracle_town/skills/video
  python3 tools/epistemic_taxonomy_probe.py --scan artifacts
  python3 tools/epistemic_taxonomy_probe.py --scan .  # full repo
  python3 tools/epistemic_taxonomy_probe.py --json    # JSON output
  python3 tools/epistemic_taxonomy_probe.py --scan . --json

Output: per-file verdict table + P2_ROUTER typed summary verdict.
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

KNOWN_ARTIFACT_EXTENSIONS = {".jpg", ".jpeg", ".png", ".mp4", ".wav", ".json"}
PROVENANCE_SUFFIX = ".provenance.json"


def get_head_sha() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else "UNKNOWN"


def find_artifact_candidates(scan_path: Path) -> list:
    """Find all files that could have a provenance sidecar."""
    candidates = []
    for f in sorted(scan_path.rglob("*")):
        if not f.is_file():
            continue
        if f.name.endswith(PROVENANCE_SUFFIX):
            continue
        if f.suffix.lower() in KNOWN_ARTIFACT_EXTENSIONS:
            candidates.append(f)
    return candidates


def classify_artifact(artifact: Path, head_sha: str) -> dict:
    """Classify one artifact by its provenance staleness class."""
    prov_path = artifact.with_name(artifact.stem + PROVENANCE_SUFFIX)
    # Also check <file>.provenance.json (stem.ext.provenance.json pattern)
    prov_path2 = artifact.parent / (artifact.name + ".provenance.json")

    found_prov = None
    for pp in (prov_path, prov_path2):
        if pp.exists():
            found_prov = pp
            break

    if found_prov is None:
        return {
            "artifact": str(artifact.relative_to(ROOT)),
            "t6_class": "MISSING_PROVENANCE",
            "verdict": "ROUTE",
            "commit_sha": None,
            "provenance_file": None,
        }

    try:
        prov_data = json.loads(found_prov.read_text())
    except Exception:
        return {
            "artifact": str(artifact.relative_to(ROOT)),
            "t6_class": "STRUCTURAL_INVALID",
            "verdict": "ROUTE",
            "commit_sha": None,
            "provenance_file": str(found_prov.relative_to(ROOT)),
        }

    commit_sha = prov_data.get("commit_sha")
    if commit_sha is None:
        return {
            "artifact": str(artifact.relative_to(ROOT)),
            "t6_class": "MISSING_COMMIT_SHA",
            "verdict": "WARN",
            "commit_sha": None,
            "provenance_type": prov_data.get("type") or prov_data.get("schema"),
            "provenance_file": str(found_prov.relative_to(ROOT)),
        }

    if commit_sha != head_sha:
        return {
            "artifact": str(artifact.relative_to(ROOT)),
            "t6_class": "TEMPORAL_STALENESS",
            "verdict": "ROUTE",
            "commit_sha": commit_sha,
            "head_sha": head_sha,
            "provenance_file": str(found_prov.relative_to(ROOT)),
        }

    return {
        "artifact": str(artifact.relative_to(ROOT)),
        "t6_class": "CLEAN",
        "verdict": "OBSERVE",
        "commit_sha": commit_sha,
        "provenance_file": str(found_prov.relative_to(ROOT)),
    }


def run_probe(scan_path: Path) -> dict:
    head_sha = get_head_sha()
    candidates = find_artifact_candidates(scan_path)

    results = [classify_artifact(c, head_sha) for c in candidates]

    counts = {}
    for r in results:
        cls = r["t6_class"]
        counts[cls] = counts.get(cls, 0) + 1

    route_count = sum(1 for r in results if r["verdict"] == "ROUTE")
    warn_count  = sum(1 for r in results if r["verdict"] == "WARN")

    if route_count > 0:
        verdict = {
            "probe": "epistemic_taxonomy_probe",
            "probe_class": "P2_ROUTER",
            "verdict": "ROUTE",
            "reason": "TEMPORAL_STALENESS_OR_MISSING_PROVENANCE",
            "requires": "SEMANTIC_REVIEW_RECEIPT_V1",
            "route_count": route_count,
            "warn_count": warn_count,
        }
    elif warn_count > 0:
        verdict = {
            "probe": "epistemic_taxonomy_probe",
            "probe_class": "P2_ROUTER",
            "verdict": "WARN",
            "reason": "TEMPORAL_OPACITY",
            "warn_count": warn_count,
        }
    else:
        verdict = {
            "probe": "epistemic_taxonomy_probe",
            "probe_class": "P2_ROUTER",
            "verdict": "OBSERVE",
            "reason": "CLEAN",
            "artifact_count": len(results),
        }

    return {
        "head_sha": head_sha,
        "scanned": str(scan_path),
        "artifact_count": len(candidates),
        "class_counts": counts,
        "verdict": verdict,
        "artifacts": results,
    }


def main() -> int:
    args = sys.argv[1:]
    scan_target = "."
    emit_json = False
    i = 0
    while i < len(args):
        if args[i] == "--scan" and i + 1 < len(args):
            scan_target = args[i + 1]
            i += 2
        elif args[i] == "--json":
            emit_json = True
            i += 1
        else:
            i += 1

    scan_path = (ROOT / scan_target).resolve()
    if not scan_path.exists():
        print(f"[ERROR] path not found: {scan_path}", file=sys.stderr)
        return 1

    result = run_probe(scan_path)

    if emit_json:
        print(json.dumps(result, indent=2))
        return 0

    v = result["verdict"]
    print(f"\n── HELEN Epistemic Taxonomy Probe ───────────────────────")
    print(f"  head_sha      : {result['head_sha'][:16]}...")
    print(f"  scanned       : {result['scanned']}")
    print(f"  artifacts     : {result['artifact_count']}")
    print()
    for cls, count in sorted(result["class_counts"].items()):
        marker = "✅" if cls == "CLEAN" else ("⚠️ " if cls == "MISSING_COMMIT_SHA" else "❌")
        print(f"  {marker} {cls:<28} {count}")
    print()
    print(f"  verdict       : {v['verdict']}  ({v.get('reason', '')})")
    if v.get("route_count"):
        print(f"  route_count   : {v['route_count']}")
    if v.get("warn_count"):
        print(f"  warn_count    : {v['warn_count']}")
    print()
    if v["verdict"] != "OBSERVE":
        print("  Artifacts requiring attention:")
        for r in result["artifacts"]:
            if r["verdict"] != "OBSERVE":
                print(f"    [{r['verdict']}] {r['artifact']}  ({r['t6_class']})")
    print("──────────────────────────────────────────────────────────")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
