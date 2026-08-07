#!/usr/bin/env python3
"""
HELEN V0 worker — deterministic read-only observer.

The first worker is intentionally NOT an LLM. It reads the task's scoped
files at the pinned commit and emits raw observations (line counts, hashes,
headings). This proves the seam end-to-end with zero provider cost and full
replay determinism. LLM adapters (claude.sh, codex.sh, ollama.py) slot in
behind the exact same raw-output contract later.

Contract: writes RAW output (untrusted, unsealed) to stdout. It has no way
to mint a run packet — only normalize.py can do that.
"""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

REPO_ROOT = Path(__file__).resolve().parents[2]


def load_task(path: Path) -> dict:
    text = path.read_text()
    if path.suffix in (".yaml", ".yml") and yaml:
        return yaml.safe_load(text)
    return json.loads(text)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", required=True)
    args = ap.parse_args()
    task = load_task(Path(args.task))
    commit = task["inputs"]["commit"]

    observations = []
    errors = []
    for f in task["inputs"]["files"]:
        proc = subprocess.run(
            ["git", "-C", str(REPO_ROOT), "show", f"{commit}:{f}"],
            capture_output=True,
        )
        if proc.returncode != 0:
            errors.append(f"unreadable at {commit}: {f}")
            continue
        content = proc.stdout
        digest = hashlib.sha256(content).hexdigest()
        text = content.decode(errors="replace")
        lines = text.splitlines()
        headings = [l for l in lines if l.startswith("#")][:5]
        observations.append({
            "text": f"{f}: {len(lines)} lines, sha256:{digest[:16]}…, headings: {headings}",
            "source_ref": f"{commit}:{f}",
        })

    raw = {
        "model": "deterministic/readonly-observer-0.1",
        "observations": observations,
        "inferences": [],
        "proposals": [],
        "open_questions": [],
        "errors_local": errors,
    }
    print(json.dumps(raw, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
