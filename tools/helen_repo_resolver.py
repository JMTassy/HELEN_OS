#!/usr/bin/env python3
"""
helen_repo_resolver.py — deterministic repo/canon resolution gate (World exec capability).

WHY (operator tranche, 2026-06-09): the session's hardest bottleneck was
`fatal: not a git repository` — the execution layer running git/test/compile/crown
commands from an ambiguous or wrong directory. Crowns existed narratively while
execution determinism was unsealed. Hypothesis: a mandatory resolver gate before any
git/test/compile/crown command drives git_context_failures → 0 and gives replay fidelity.

THE §5 EXPLOIT THIS CLOSES (operator-identified): a *valid git repo that is the wrong
canon root* — a mirror/stale clone passes `test -d` and `rev-parse` but is NOT the
crowned canon. Path existence cannot catch this. **Commit-ancestry pinning can**: the
canonical crown commit must be an ancestor of HEAD. A mirror at another branch won't
contain it. That is the difference between "a git repo" and "THE canon".

WHAT (read-only, no mutation, no network, no LLM — deterministic):
  Validate a checkout against a HELEN_REPO_MANIFEST_V1:
    1. path exists + is a git work tree
    2. top-level resolves
    3. current branch == expected_branch (if pinned)
    4. crown_commit is an ANCESTOR of HEAD (the §5 defense; if pinned)
    5. every required_path exists
    6. every compile_glob py_compiles clean
  Emit an explicit verdict with reason codes (schema.py gate style: flags, never a
  silent pass). Print HELEN_REPO_RESOLVED *only* if every check truly passed.

FABRICATION REFUSAL (same discipline as the other standalone tools):
  - never prints RESOLVED unless all checks pass; every failure carries a reason code
  - no network, no LLM, no env-dependent magic — same inputs → same output (replay)
  - does not invent paths or commits; reads them from the manifest

EXIT CODES (superset of operator draft):
  0  RESOLVED        10 PATH_MISSING       20 NOT_GIT_WORKTREE   21 NO_TOPLEVEL
  22 STATUS_FAILED   23 NO_BRANCH          24 WRONG_BRANCH       30 REQUIRED_PATH_MISSING
  40 COMPILE_FAILED  50 CROWN_NOT_ANCESTOR (the §5 exploit caught)  60 MANIFEST_ERROR

USAGE:
  python3 tools/helen_repo_resolver.py --manifest repo_manifest.json
  python3 tools/helen_repo_resolver.py --manifest repo_manifest.json --root /path/override
  python3 tools/helen_repo_resolver.py --manifest repo_manifest.json --json   # machine output

authority: false · read-only · resolves THE canon, refuses a mirror.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def _git(root: str, *args: str) -> tuple[int, str]:
    try:
        p = subprocess.run(["git", "-C", root, *args],
                           capture_output=True, text=True, timeout=30)
        return p.returncode, (p.stdout + p.stderr).strip()
    except Exception as exc:  # pragma: no cover - defensive
        return 255, str(exc)


def resolve(manifest: dict, root_override: str | None = None) -> tuple[int, dict]:
    """Return (exit_code, report). RESOLVED only when report['flags'] is empty."""
    flags: list[dict] = []

    def flag(code, msg, exit_code):
        flags.append({"code": code, "message": msg, "exit": exit_code})

    root = root_override or manifest.get("canonical_repo_path")
    report: dict = {
        "schema": "HELEN_REPO_RESOLUTION_V1",
        "authority": False, "claim": "NO_CLAIM",
        "root": root,
        "expected_branch": manifest.get("expected_branch"),
        "crown_commit": manifest.get("crown_commit"),
        "observed": {},
        "flags": flags,
    }
    if not root:
        flag("MANIFEST_ERROR", "manifest has no canonical_repo_path and no --root", 60)
        report["resolved"] = False
        return 60, report

    # 1. path exists
    if not Path(root).is_dir():
        flag("PATH_MISSING", f"not a directory: {root}", 10)
        report["resolved"] = False
        return 10, report

    # 2. git work tree
    rc, out = _git(root, "rev-parse", "--is-inside-work-tree")
    report["observed"]["is_work_tree"] = out
    if rc != 0 or out.strip() != "true":
        flag("NOT_GIT_WORKTREE", f"not a git work tree (got: {out[:80]!r})", 20)
        report["resolved"] = False
        return 20, report

    # 3. top-level
    rc, top = _git(root, "rev-parse", "--show-toplevel")
    report["observed"]["toplevel"] = top
    if rc != 0:
        flag("NO_TOPLEVEL", "could not resolve top-level", 21)

    # status (observability; failure is a real flag)
    rc, st = _git(root, "status", "--short")
    report["observed"]["status_short"] = st
    if rc != 0:
        flag("STATUS_FAILED", "git status failed", 22)

    # branch + HEAD (blank on error — never store stderr noise as the branch)
    rc, branch = _git(root, "rev-parse", "--abbrev-ref", "HEAD")
    if rc != 0:
        branch = None
        flag("NO_BRANCH", "could not resolve current branch (unborn/detached HEAD)", 23)
    report["observed"]["branch"] = branch
    rc, head = _git(root, "rev-parse", "HEAD")
    report["observed"]["head"] = head if rc == 0 else None

    exp_branch = manifest.get("expected_branch")
    if exp_branch and branch and branch != exp_branch:
        flag("WRONG_BRANCH", f"branch={branch!r} expected={exp_branch!r}", 24)

    # 4. §5 DEFENSE — crown commit must be an ANCESTOR of HEAD
    crown = manifest.get("crown_commit")
    if crown:
        rc, _ = _git(root, "merge-base", "--is-ancestor", crown, "HEAD")
        report["observed"]["crown_is_ancestor"] = (rc == 0)
        if rc != 0:
            flag("CROWN_NOT_ANCESTOR",
                 f"crown {crown[:12]} is NOT an ancestor of HEAD — wrong/mirror canon", 50)

    # 5. required paths
    missing = [rp for rp in manifest.get("required_paths", [])
               if not (Path(root) / rp).exists()]
    report["observed"]["missing_required_paths"] = missing
    if missing:
        flag("REQUIRED_PATH_MISSING", f"missing: {missing}", 30)

    # 6. compile globs
    compile_fail: list[str] = []
    for g in manifest.get("compile_globs", []):
        files = sorted(str(p) for p in Path(root).glob(g))
        if not files:
            compile_fail.append(f"{g} (no match)")
            continue
        rc, out = subprocess.run(
            [sys.executable, "-m", "py_compile", *files],
            capture_output=True, text=True).returncode, ""
        if rc != 0:
            compile_fail.append(g)
    report["observed"]["compile_globs_failed"] = compile_fail
    if compile_fail:
        flag("COMPILE_FAILED", f"py_compile failed: {compile_fail}", 40)

    if flags:
        report["resolved"] = False
        return flags[0]["exit"], report
    report["resolved"] = True
    return 0, report


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--manifest", required=True, type=Path)
    ap.add_argument("--root", default=None, help="override canonical_repo_path")
    ap.add_argument("--json", action="store_true", help="emit JSON report")
    args = ap.parse_args()

    try:
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"MANIFEST_ERROR: {exc}", file=sys.stderr)
        return 60

    code, report = resolve(manifest, args.root)

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"== HELEN_REPO_RESOLVER == root={report['root']}")
        obs = report["observed"]
        print(f"   branch:  {obs.get('branch')}  (expected {report['expected_branch']})")
        print(f"   HEAD:    {str(obs.get('head'))[:12]}")
        if report.get("crown_commit"):
            print(f"   crown:   {report['crown_commit'][:12]} ancestor={obs.get('crown_is_ancestor')}")
        if report["flags"]:
            for f in report["flags"]:
                print(f"   ✗ {f['code']}: {f['message']}")
            print("   VERDICT: REJECTED")
        else:
            print("   VERDICT: RESOLVED")
            print("HELEN_REPO_RESOLVED")
    return code


if __name__ == "__main__":
    sys.exit(main())
