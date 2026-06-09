#!/usr/bin/env python3
"""
helen_canon_loader.py — gated CANON → RAG index with per-chunk git provenance.

WHY (operator tranche, 2026-06-09): repository identity is solved (helen_repo_resolver).
The next weak point is canon ingestion — RAG must load from the verified root, never
from memory, mirrors, loose paths, or agent narrative. The receipt invariant applies to
chunks: NO blob-receipt = NO canonical claim.

THE EXPLOIT THIS CLOSES — "semantic memory laundering" (operator §5): resolver passes
once, the index persists, the repo changes later, and RAG keeps serving STALE chunks
that *sound* canonical. The mirror exploit, reborn at the memory layer.

DEFENSE — per-chunk blob pinning + reconstruction:
  - Every chunk is cut from the COMMITTED git blob (`git show HEAD:path`), not disk —
    canon is the committed state, not the working tree.
  - Every chunk record carries: resolver_status, git_top_level, branch, head,
    crown_commit, canon_root_fingerprint, file_path, blob_hash, line_start/end, text_sha.
  - VERIFY re-derives each chunk from git HEAD and checks text_sha. If the repo moved or
    a blob changed, the stamp no longer reconstructs → stale chunk DETECTED, not served.

GATING: index runs ONLY if helen_repo_resolver returns status=PASS. No PASS → no index.

READ-ONLY: git plumbing only (show/rev-parse/cat-file), hashlib. No writes to the repo,
no network, no LLM, no __pycache__.

USAGE:
  python3 tools/helen_canon_loader.py index  --manifest repo_manifest.json \\
        --out canon_manifest_index.jsonl [--lines 50]
  python3 tools/helen_canon_loader.py verify --manifest repo_manifest.json \\
        --index canon_manifest_index.jsonl [--sample 20]

authority: false · read-only · a chunk without a git-reconstructable receipt is NO_CLAIM.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from helen_repo_resolver import resolve  # noqa: E402


def _git(root: str, *args: str) -> tuple[int, str]:
    p = subprocess.run(["git", "-C", root, *args],
                       capture_output=True, text=True, timeout=60)
    return p.returncode, p.stdout


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _canon_root_of(rel: str) -> str:
    parts = rel.split("/")
    return parts[1] if len(parts) > 1 and parts[0] == "CANON" else "UNKNOWN"


def _gate(manifest: dict, root_override: str | None):
    """Run the resolver. Return (root, report) or exit non-zero if not PASS."""
    code, report = resolve(manifest, root_override)
    if report["status"] != "PASS":
        print(f"GATE FAILED — resolver status={report['status']} "
              f"reasons={report['failure_reasons']}", file=sys.stderr)
        print("No PASS → no index. (repo identity must be repaired first)", file=sys.stderr)
        sys.exit(code or 1)
    return report["root"], report


def cmd_index(args) -> int:
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    root, report = _gate(manifest, args.root)
    fp = report["replay_fingerprint"]
    head = report["observed"]["head"]
    branch = report["observed"]["branch"]
    top = report["observed"]["top_level"]
    crown = manifest.get("canonical_crown_commit")

    rc, listing = _git(root, "ls-tree", "-r", "--name-only", "HEAD", "CANON")
    files = [f for f in listing.splitlines() if f.strip()]

    n_chunks = 0
    with args.out.open("w", encoding="utf-8") as fh:
        for rel in files:
            rc, blob_hash = _git(root, "rev-parse", f"HEAD:{rel}")
            blob_hash = blob_hash.strip()
            rc, content = _git(root, "show", f"HEAD:{rel}")
            lines = content.splitlines()
            for start in range(0, len(lines), args.lines):
                end = min(start + args.lines, len(lines))
                chunk_text = "\n".join(lines[start:end])
                rec = {
                    "schema": "CANON_CHUNK_V1",
                    "resolver_status": report["status"],
                    "canon_root": _canon_root_of(rel),
                    "git_top_level": top,
                    "branch": branch,
                    "head": head,
                    "crown_commit": crown,
                    "canon_root_fingerprint": fp,
                    "file_path": rel,
                    "blob_hash": blob_hash,
                    "line_start": start + 1,
                    "line_end": end,
                    "text_sha": _sha(chunk_text),
                }
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
                n_chunks += 1

    # provenance coverage: by construction every record has all fields — verify it
    req = {"resolver_status", "git_top_level", "branch", "head", "crown_commit",
           "canon_root_fingerprint", "file_path", "blob_hash", "line_start",
           "line_end", "text_sha"}
    covered = 0
    for ln in args.out.read_text(encoding="utf-8").splitlines():
        r = json.loads(ln)
        if req.issubset(r) and all(r[k] not in (None, "") for k in req):
            covered += 1
    cov = covered / n_chunks if n_chunks else 0.0

    print(f"== canon_loader index ==")
    print(f"   gated by resolver: PASS  fingerprint={fp[:16]}")
    print(f"   files indexed:   {len(files)}")
    print(f"   chunks emitted:  {n_chunks}  (window={args.lines} lines)")
    print(f"   canon_chunk_provenance_coverage = {covered}/{n_chunks} = {cov:.0%}")
    print(f"   index: {args.out}")
    return 0 if cov == 1.0 else 2


def cmd_verify(args) -> int:
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    root, report = _gate(manifest, args.root)

    records = [json.loads(ln) for ln in
               args.index.read_text(encoding="utf-8").splitlines() if ln.strip()]
    if not records:
        print("empty index", file=sys.stderr)
        return 2

    rng = random.Random(1234)  # deterministic sample → replayable
    sample = records if len(records) <= args.sample else rng.sample(records, args.sample)

    ok = 0
    fails = []
    for r in sample:
        # reconstruct EXACTLY from git: HEAD blob → line range → sha
        rc, blob_now = _git(root, "rev-parse", f"HEAD:{r['file_path']}")
        blob_now = blob_now.strip()
        rc, content = _git(root, "show", f"HEAD:{r['file_path']}")
        lines = content.splitlines()
        recon = "\n".join(lines[r["line_start"] - 1: r["line_end"]])
        blob_match = (blob_now == r["blob_hash"])
        sha_match = (_sha(recon) == r["text_sha"])
        if blob_match and sha_match:
            ok += 1
        else:
            fails.append({"file": r["file_path"],
                          "lines": f"{r['line_start']}-{r['line_end']}",
                          "blob_match": blob_match, "sha_match": sha_match})

    rate = ok / len(sample)
    print(f"== canon_loader verify ==")
    print(f"   gated by resolver: PASS")
    print(f"   sampled: {len(sample)}  (seed=1234, deterministic)")
    print(f"   retrieval_replay_success = {ok}/{len(sample)} = {rate:.0%}")
    if fails:
        print("   STALE / UNRECONSTRUCTABLE chunks (the laundering exploit, caught):")
        for f in fails[:10]:
            print(f"     ✗ {f}")
    print(f"   VERDICT: {'KEEP' if rate == 1.0 else 'REJECT'}")
    return 0 if rate == 1.0 else 3


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    pi = sub.add_parser("index"); pi.set_defaults(fn=cmd_index)
    pi.add_argument("--manifest", required=True, type=Path)
    pi.add_argument("--out", default=Path("canon_manifest_index.jsonl"), type=Path)
    pi.add_argument("--lines", type=int, default=50)
    pi.add_argument("--root", default=None)
    pv = sub.add_parser("verify"); pv.set_defaults(fn=cmd_verify)
    pv.add_argument("--manifest", required=True, type=Path)
    pv.add_argument("--index", default=Path("canon_manifest_index.jsonl"), type=Path)
    pv.add_argument("--sample", type=int, default=20)
    pv.add_argument("--root", default=None)
    args = ap.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
