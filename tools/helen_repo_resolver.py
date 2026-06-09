#!/usr/bin/env python3
"""
helen_repo_resolver.py — deterministic repo/canon resolution gate (World exec capability).

WHY (operator tranche, 2026-06-09): the session's hardest bottleneck was
`fatal: not a git repository` — running git/test/compile/crown commands from an
ambiguous or wrong directory. Crowns existed narratively while execution determinism
was unsealed. A mandatory resolver gate drives git_context_failures → 0 and gives
replay fidelity, so HELEN never acts from an unverified root.

THE §5 EXPLOIT THIS CLOSES (operator-identified): a *valid git repo that is the wrong
canon root* — a mirror/stale clone passes path-existence and rev-parse but is NOT the
crowned canon. Path existence cannot catch this. **Commit-ancestry pinning can**: the
canonical crown commit must be an ancestor of HEAD. A mirror at another branch won't
contain it. That is the difference between "a git repo" and "THE canon".

READ-ONLY (operator correction, 2026-06-09): syntax is checked with in-memory
`compile(src, path, "exec")` — NOT `py_compile`, which would write __pycache__/.pyc
and violate the read-only constraint. This tool never writes to the target repo,
never touches the network, never calls an LLM. Same inputs → same output (replay).

MANIFEST (HELEN_REPO_MANIFEST_V1):
  canonical_repo_path · expected_top_level · expected_branch ·
  canonical_crown_commit · required_paths[] · syntax_globs[]

VERDICT: status PASS only when failure_reasons is empty. Every failure carries a
snake_case reason (schema.py gate style: explicit flags, never a silent pass) AND a
shell exit code. A deterministic replay_fingerprint over the canonical tuple lets
callers prove "same fingerprint x3".

FAILURE REASONS / EXIT CODES:
  0  (PASS)
  10 path_missing                  20 not_a_git_repository      21 no_top_level
  22 wrong_top_level               23 no_branch                 24 wrong_branch
  30 required_path_missing         40 syntax_error
  50 canonical_crown_commit_not_ancestor_of_head      60 manifest_error

USAGE:
  python3 tools/helen_repo_resolver.py --manifest repo_manifest.json
  python3 tools/helen_repo_resolver.py --manifest repo_manifest.json --root /override
  python3 tools/helen_repo_resolver.py --manifest repo_manifest.json --json

authority: false · read-only (no __pycache__, no network, no LLM) · resolves THE canon.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

# reason -> exit code
_EXIT = {
    "path_missing": 10, "not_a_git_repository": 20, "no_top_level": 21,
    "wrong_top_level": 22, "no_branch": 23, "wrong_branch": 24,
    "required_path_missing": 30, "syntax_error": 40,
    "canonical_crown_commit_not_ancestor_of_head": 50, "manifest_error": 60,
}


def _git(root: str, *args: str) -> tuple[int, str]:
    try:
        p = subprocess.run(["git", "-C", root, *args],
                           capture_output=True, text=True, timeout=30)
        return p.returncode, (p.stdout or "").strip(), (p.stderr or "").strip()  # type: ignore
    except Exception as exc:  # pragma: no cover - defensive
        return 255, "", str(exc)


def _syntax_ok(path: Path) -> bool:
    """In-memory syntax check — never writes __pycache__ (read-only guarantee)."""
    try:
        compile(path.read_text(encoding="utf-8"), str(path), "exec")
        return True
    except Exception:
        return False


def resolve(manifest: dict, root_override: str | None = None) -> tuple[int, dict]:
    reasons: list[str] = []
    obs: dict = {}
    root = root_override or manifest.get("canonical_repo_path")

    def fail(reason: str):
        if reason not in reasons:
            reasons.append(reason)

    if not root:
        return 60, {"schema": "HELEN_REPO_RESOLUTION_V1", "authority": False,
                    "status": "FAIL", "failure_reasons": ["manifest_error"],
                    "observed": {}, "replay_fingerprint": None}

    if not Path(root).is_dir():
        fail("path_missing")
        return _finish(root, manifest, obs, reasons)

    rc, out, _ = _git(root, "rev-parse", "--is-inside-work-tree")
    if rc != 0 or out != "true":
        fail("not_a_git_repository")
        return _finish(root, manifest, obs, reasons)

    rc, top, _ = _git(root, "rev-parse", "--show-toplevel")
    obs["top_level"] = top if rc == 0 else None
    if rc != 0:
        fail("no_top_level")
    exp_top = manifest.get("expected_top_level")
    if exp_top and obs.get("top_level") and obs["top_level"] != exp_top:
        fail("wrong_top_level")

    rc, branch, _ = _git(root, "rev-parse", "--abbrev-ref", "HEAD")
    obs["branch"] = branch if rc == 0 else None
    if rc != 0:
        fail("no_branch")
    exp_branch = manifest.get("expected_branch")
    if exp_branch and obs.get("branch") and obs["branch"] != exp_branch:
        fail("wrong_branch")

    rc, head, _ = _git(root, "rev-parse", "HEAD")
    obs["head"] = head if rc == 0 else None

    # §5 DEFENSE — crown must be an ANCESTOR of HEAD
    crown = manifest.get("canonical_crown_commit")
    if crown:
        rc, _, _ = _git(root, "merge-base", "--is-ancestor", crown, "HEAD")
        obs["crown_is_ancestor"] = (rc == 0)
        if rc != 0:
            fail("canonical_crown_commit_not_ancestor_of_head")

    missing = [rp for rp in manifest.get("required_paths", [])
               if not (Path(root) / rp).exists()]
    obs["missing_required_paths"] = missing
    if missing:
        fail("required_path_missing")

    syntax_bad: list[str] = []
    for g in manifest.get("syntax_globs", []):
        files = sorted(Path(root).glob(g))
        if not files:
            syntax_bad.append(f"{g} (no match)")
            continue
        syntax_bad.extend(str(f) for f in files if not _syntax_ok(f))
    obs["syntax_failures"] = syntax_bad
    if syntax_bad:
        fail("syntax_error")

    return _finish(root, manifest, obs, reasons)


def _fingerprint(root: str, manifest: dict, obs: dict, reasons: list[str]) -> str:
    """Deterministic over the canonical tuple — proves 'same fingerprint x3'."""
    tup = {
        "top_level": obs.get("top_level"),
        "branch": obs.get("branch"),
        "head": obs.get("head"),
        "crown_is_ancestor": obs.get("crown_is_ancestor"),
        "crown": manifest.get("canonical_crown_commit"),
        "missing_required_paths": sorted(obs.get("missing_required_paths", [])),
        "syntax_failures": sorted(obs.get("syntax_failures", [])),
        "status": "PASS" if not reasons else "FAIL",
        "failure_reasons": sorted(reasons),
    }
    return hashlib.sha256(json.dumps(tup, sort_keys=True).encode()).hexdigest()


def _finish(root, manifest, obs, reasons) -> tuple[int, dict]:
    status = "PASS" if not reasons else "FAIL"
    report = {
        "schema": "HELEN_REPO_RESOLUTION_V1", "authority": False, "claim": "NO_CLAIM",
        "root": root, "status": status,
        "failure_reasons": sorted(reasons),
        "observed": obs,
        "replay_fingerprint": _fingerprint(root, manifest, obs, reasons),
    }
    code = 0 if not reasons else max(_EXIT[r] for r in reasons)
    return code, report


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--manifest", required=True, type=Path)
    ap.add_argument("--root", default=None)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    try:
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"manifest_error: {exc}", file=sys.stderr)
        return 60

    code, report = resolve(manifest, args.root)

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        o = report["observed"]
        print(f"== HELEN_REPO_RESOLVER == root={report['root']}")
        print(f"   top_level: {o.get('top_level')}")
        print(f"   branch:    {o.get('branch')}  HEAD: {str(o.get('head'))[:12]}")
        if manifest.get("canonical_crown_commit"):
            print(f"   crown:     {manifest['canonical_crown_commit'][:12]} "
                  f"ancestor={o.get('crown_is_ancestor')}")
        print(f"   replay_fingerprint: {report['replay_fingerprint'][:16]}")
        if report["status"] == "PASS":
            print("   status: PASS")
            print("HELEN_REPO_RESOLVED")
        else:
            for r in report["failure_reasons"]:
                print(f"   ✗ {r}")
            print("   status: FAIL")
    return code


if __name__ == "__main__":
    sys.exit(main())
