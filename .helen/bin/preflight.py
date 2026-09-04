#!/usr/bin/env python3
"""
HELEN M1 — Preflight gate.

P: (task, runtime_state) -> {PROCEED, HOLD, REJECT}

Fail closed: anything other than PROCEED means no worker dispatch.

Checks:
  1. Task manifest exists, parses, and validates against helen-task-manifest.v0.
  2. Repository dirty state — dirty files in task scope => HOLD.
  3. Protected paths (kernel / ledger / constitution / .helen itself) in scope => HOLD.
  4. Pinned commit exists in repo => else REJECT.
  5. Authority is 'none', canon false, ledger_effect none (schema enforces; belt+braces here).

Output (stdout): JSON preflight packet. Exit codes: 0 PROCEED, 2 HOLD, 3 REJECT.
"""
import argparse
import fnmatch
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPO_ROOT / ".helen" / "schemas" / "helen-task-manifest.v0.json"

PROTECTED_PATTERNS = [
    "GOVERNANCE/KERNEL*",
    "GOVERNANCE/CONSTITUTION*",
    "town/ledger_v1.ndjson",
    ".helen/schemas/*",
    ".helen/bin/*",
    ".helen/policies/*",
]


def sha256_file(p: Path) -> str:
    return "sha256:" + hashlib.sha256(p.read_bytes()).hexdigest()


def load_task(path: Path) -> dict:
    text = path.read_text()
    if path.suffix in (".yaml", ".yml"):
        if yaml is None:
            raise RuntimeError("pyyaml not installed; use JSON manifest or pip install pyyaml")
        return yaml.safe_load(text)
    return json.loads(text)


def validate_schema(task: dict) -> list:
    """Minimal structural validation without jsonschema dependency."""
    problems = []
    schema = json.loads(SCHEMA_PATH.read_text())
    for key in schema["required"]:
        if key not in task:
            problems.append(f"missing required field: {key}")
    if task.get("authority") != "none":
        problems.append("authority must be 'none' (Law 1: authority conservation)")
    if task.get("canon") is not False:
        problems.append("canon must be false at intake")
    if task.get("ledger_effect") != "none":
        problems.append("ledger_effect must be 'none' for V0 tasks")
    adm = task.get("admission", {})
    if adm.get("automatic") is not False or adm.get("human_seal_required") is not True:
        problems.append("admission must be {automatic: false, human_seal_required: true} (Law 7)")
    mp = task.get("mutation_policy", {})
    if mp.get("main_checkout") != "forbidden":
        problems.append("mutation_policy.main_checkout must be 'forbidden'")
    inputs = task.get("inputs", {})
    if not inputs.get("files"):
        problems.append("inputs.files must be non-empty")
    if not inputs.get("commit"):
        problems.append("inputs.commit must pin a commit")
    return problems


def git(*args) -> str:
    return subprocess.run(
        ["git", "-C", str(REPO_ROOT), *args],
        capture_output=True, text=True, check=False
    ).stdout.strip()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", required=True)
    args = ap.parse_args()

    task_path = Path(args.task)
    packet = {
        "schema": "helen.preflight.v0",
        "task_path": str(task_path),
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "decision": None,
        "reasons": [],
    }

    # 1. Parse + validate
    try:
        task = load_task(task_path)
    except Exception as e:
        packet["decision"] = "REJECT"
        packet["reasons"].append(f"manifest unreadable: {e}")
        print(json.dumps(packet, indent=2))
        return 3

    problems = validate_schema(task)
    if problems:
        packet["decision"] = "REJECT"
        packet["reasons"].extend(problems)
        print(json.dumps(packet, indent=2))
        return 3

    packet["task_id"] = task["task_id"]
    packet["task_hash"] = sha256_file(task_path)

    # 2. Dirty state in scope
    dirty = [l[3:] for l in git("status", "--porcelain").splitlines() if l.strip()]
    scoped_dirty = [
        f for f in dirty
        if any(fnmatch.fnmatch(f, pat) or f == inp for inp in task["inputs"]["files"] for pat in [inp])
    ]
    if scoped_dirty:
        packet["decision"] = "HOLD"
        packet["reasons"].append(f"DIRTY_STATE_DECISION_PACKET: uncommitted changes in task scope: {scoped_dirty}")

    # 3. Protected paths in scope
    protected_hits = [
        f for f in task["inputs"]["files"]
        for pat in PROTECTED_PATTERNS
        if fnmatch.fnmatch(f, pat)
    ]
    if protected_hits:
        packet["decision"] = "HOLD"
        packet["reasons"].append(f"protected paths in scope, operator scoping required: {protected_hits}")

    # 4. Pinned commit exists
    commit = task["inputs"]["commit"]
    if git("cat-file", "-t", commit) != "commit":
        packet["decision"] = "REJECT"
        packet["reasons"].append(f"pinned commit not found in repo: {commit}")
        print(json.dumps(packet, indent=2))
        return 3

    # 5. Input files exist at pinned commit
    for f in task["inputs"]["files"]:
        if subprocess.run(
            ["git", "-C", str(REPO_ROOT), "cat-file", "-e", f"{commit}:{f}"],
            capture_output=True
        ).returncode != 0:
            packet["decision"] = "REJECT"
            packet["reasons"].append(f"input file absent at pinned commit: {f}")

    if packet["decision"] == "REJECT":
        print(json.dumps(packet, indent=2))
        return 3
    if packet["decision"] == "HOLD":
        packet["reasons"].append("NO_RECEIPT")
        packet["reasons"].append("HOLD_FOR_OPERATOR")
        print(json.dumps(packet, indent=2))
        return 2

    packet["decision"] = "PROCEED"
    print(json.dumps(packet, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
