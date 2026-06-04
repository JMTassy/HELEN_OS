"""
helen_executor_v0.py — the HELEN Executor (Option B: sovereign, local, no Hermes SaaS).

We take the *execution concepts* (task routing, execution discipline, keep/reject gates),
not the external service. The Executor sits between the kernel and the Hands:

    HELEN Kernel -> Executor -> Hands {fs_inspect, git_status, test_run, memory_index, map_builder}
    each execution -> Receipt + Metric + Decision(KEEP/REJECT) -> back to kernel

Discipline:
  * Every execution emits a receipt (what, args, output_sha, metric, decision, authority=false).
  * Decision is by EXPLICIT metric, never vibe.
  * An execution flagged as an INTEGRATION candidate must additionally pass I()
    (invariant_checker_v0) — no I()=1, no KEEP. This is where self-building is gated.
  * Hands are typed + bounded. Read hands run now; write/world hands are declared slots
    (NO_SHIP) until separately gated. authority=false, claim=NO_CLAIM.

Deterministic where it can be; subprocess hands carry timeouts and capture exit codes.
"""
from __future__ import annotations
import hashlib, importlib.util, json, subprocess, time
from pathlib import Path
from typing import Any, Dict

_HERE = Path(__file__).resolve().parent
REPO = _HERE.parents[1]

# load I() (same dir) without a package
_spec = importlib.util.spec_from_file_location("invck", _HERE / "invariant_checker_v0.py")
invck = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(invck)


def _sha(x: Any) -> str:
    return "sha256:" + hashlib.sha256(str(x).encode()).hexdigest()[:16]


# ── Hands (typed capabilities) ───────────────────────────────────────────────
def hand_fs_inspect(args) -> Dict[str, Any]:
    p = Path(str(args.get("path", "."))).expanduser()
    if not p.exists():
        return {"success": False, "output": f"not found: {p}", "n": 0}
    if p.is_dir():
        items = sorted(x.name for x in p.iterdir())[:200]
        return {"success": True, "output": items, "n": len(items)}
    text = p.read_text(errors="ignore")[:2000]
    return {"success": True, "output": text, "n": len(text)}


def _run(cmd, cwd=None, timeout=120):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True,
                           timeout=timeout, cwd=str(cwd or REPO))
        return r.returncode, (r.stdout or "")[:4000], (r.stderr or "")[:1000]
    except subprocess.TimeoutExpired:
        return -1, "", f"timeout after {timeout}s"
    except Exception as exc:
        return -1, "", str(exc)


def hand_git_status(args) -> Dict[str, Any]:
    code, out, err = _run("git status --short")
    return {"success": code == 0, "output": out or err, "exit": code,
            "dirty_files": len([l for l in out.splitlines() if l.strip()])}


def hand_test_run(args) -> Dict[str, Any]:
    target = str(args.get("target", "tests"))
    code, out, err = _run(f"python3 -m pytest -q {target}")
    tail = (out or err).splitlines()[-1:] or [""]
    return {"success": code == 0, "output": tail[0], "exit": code}


def hand_memory_index(args) -> Dict[str, Any]:
    # DECLARED SLOT — would call the librarian; not run here (NO_SHIP).
    return {"success": True, "output": "DECLARED_SLOT: memory_index not yet wired", "declared": True}


def hand_map_builder(args) -> Dict[str, Any]:
    # DECLARED SLOT — world hand; gated separately (NO_SHIP).
    return {"success": True, "output": "DECLARED_SLOT: map_builder not yet wired", "declared": True}


HANDS = {
    "fs_inspect": {"kind": "read", "fn": hand_fs_inspect},
    "git_status": {"kind": "read", "fn": hand_git_status},
    "test_run":   {"kind": "read", "fn": hand_test_run},
    "memory_index": {"kind": "read", "fn": hand_memory_index},
    "map_builder":  {"kind": "world", "fn": hand_map_builder},
}


def execute(task: Dict[str, Any], invariant_check=invck.check) -> Dict[str, Any]:
    """Route a task to a hand, run it, emit Receipt + Metric + Decision.

    task = {"hand": str, "args": {...},
            "integration_candidate": {<I()-checkable descriptor>}?}
    """
    name = task.get("hand", "")
    spec = HANDS.get(name)
    t0 = time.monotonic()
    if spec is None:
        metric = {"success": False, "reason": f"unknown hand {name!r}"}
        out = metric["reason"]
    else:
        out = spec["fn"](task.get("args", {}))
        metric = {"success": bool(out.get("success")), "kind": spec["kind"]}
    latency_ms = round((time.monotonic() - t0) * 1000)

    # Decision by explicit metric.
    decision = "KEEP" if metric.get("success") else "REJECT"
    inv_report = None
    # Integration candidates must additionally pass I() — self-building gate.
    if task.get("integration_candidate") is not None:
        inv_report = invariant_check(task["integration_candidate"])
        if inv_report["I"] != 1:
            decision = "REJECT"
            metric["reason"] = "I()=0: " + ",".join(inv_report["failed_invariants"])

    receipt = {
        "schema": "EXECUTOR_RECEIPT_V0", "authority": False, "claim": "NO_CLAIM",
        "hand": name, "kind": spec["kind"] if spec else None,
        "args": task.get("args", {}),
        "output_sha256": _sha(out),
        "latency_ms": latency_ms,
        "metric": metric,
        "decision": decision,
        "I": (inv_report["I"] if inv_report else None),
        "note": "Executor proposes; reducer admits. No KEEP integrates without I()=1.",
    }
    return {"receipt": receipt, "metric": metric, "decision": decision,
            "output": out, "invariant_check": inv_report}


if __name__ == "__main__":
    import sys
    t = json.load(open(sys.argv[1])) if len(sys.argv) > 1 else {"hand": "git_status", "args": {}}
    r = execute(t)
    print(json.dumps(r["receipt"], indent=2, default=str))
    sys.exit(0 if r["decision"] == "KEEP" else 1)
