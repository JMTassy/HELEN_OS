#!/usr/bin/env python3
"""
tools/ecp_ci_matrix.py — HELEN Epistemic Control Plane CI matrix.
authority: NONE · NON_SOVEREIGN · diagnostic only

Runs all ECP probes in sequence, emits a unified typed verdict table.
Does NOT make admission decisions — that belongs to the reducer.

Probes run:
  P1 witness_projection    → COUPLED / SOFT_DRIFT / HARD_DRIFT
  P1 false_green_lint      → PASS / FAIL
  P1 k_tau_lint            → PASS / FAIL (τ score)
  P1 k8_lint               → PASS / FAIL (k8 score)
  P2 citation_graph_probe  → CLEAN / ROUTE (CITATION_LOOP_V1)

ECP scorecard (diagnosis only — never admission):
  structural_green_rate    fraction of P1 gates green
  witness_coupling         COUPLED / SOFT_DRIFT / HARD_DRIFT
  false_green_count        N6 from witness probe
  nd_surface_cleanliness   k8 score
  semantic_risk_open_count citations routed, not yet reviewed

Usage:
  python3 tools/ecp_ci_matrix.py
  python3 tools/ecp_ci_matrix.py --json
  python3 tools/ecp_ci_matrix.py --receipts-json  path/to/receipts.json
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VENV = ROOT / ".venv" / "bin" / "python3"
PYTHON = str(VENV) if VENV.exists() else sys.executable


def _run(cmd: list, cwd=ROOT, env_extra: dict | None = None) -> tuple:
    """Run command, return (returncode, stdout, stderr)."""
    import os
    env = {**os.environ, "PYTHONPATH": str(ROOT)}
    if env_extra:
        env.update(env_extra)
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=60, env=env)
    return r.returncode, r.stdout, r.stderr


def run_witness() -> dict:
    rc, out, err = _run([PYTHON, "tools/witness_projection_probe.py", "--no-fg", "--json"])
    if rc != 0 or not out.strip():
        return {"status": "ERROR", "error": err[:200]}
    try:
        return json.loads(out)
    except Exception:
        return {"status": "ERROR", "error": "json_parse_failed"}


def run_false_green() -> dict:
    rc, out, err = _run([PYTHON, "scripts/helen_false_green_lint.py"])
    return {
        "passed": rc == 0,
        "output": (out + err).strip()[:300],
    }


def run_k_tau() -> dict:
    rc, out, err = _run([PYTHON, "scripts/helen_k_tau_lint.py"])
    out_all = out + err
    tau = None
    for line in out_all.splitlines():
        # matches: "  tau              : 1.000" or "tau=1.000" or "τ=1.000"
        if "tau" in line.lower() or "τ" in line:
            import re as _re
            m = _re.search(r"tau\s*[=:]\s*([0-9.]+)", line, _re.IGNORECASE)
            if m:
                try:
                    tau = float(m.group(1))
                except ValueError:
                    pass
    return {
        "passed": rc == 0,
        "tau": tau,
        "output": out_all.strip()[:400],
    }


def run_k8() -> dict:
    rc, out, err = _run([PYTHON, "scripts/helen_k8_lint.py", "--mode", "all_nd"])
    out_all = out + err
    score = None
    for line in out_all.splitlines():
        if "k8=" in line:
            for part in line.split():
                if part.startswith("k8="):
                    try:
                        score = float(part[3:])
                    except ValueError:
                        pass
    return {
        "passed": score is not None and score > 0,
        "k8_score": score,
        "output": out_all.strip()[:400],
    }


def run_citation_probe(receipts_json: str | None) -> dict:
    if not receipts_json or not Path(receipts_json).exists():
        return {
            "skipped": True,
            "reason": "no receipts_json provided — run with --receipts-json path/to/receipts.json",
        }
    rc, out, err = _run([PYTHON, "tools/citation_graph_probe.py", receipts_json])
    if rc != 0 or not out.strip():
        return {"passed": False, "error": err[:200]}
    try:
        data = json.loads(out)
        loop_count = data.get("loop_count", 0)
        return {
            "passed": loop_count == 0,
            "loop_count": loop_count,
            "loop_nodes": data.get("loop_nodes", []),
            "graph_node_count": data.get("graph_node_count", 0),
        }
    except Exception:
        return {"passed": False, "error": "json_parse_failed"}


def build_matrix(results: dict) -> dict:
    witness = results["witness"]
    fg = results["false_green"]
    ktau = results["k_tau"]
    k8 = results["k8"]
    cit = results["citation_probe"]

    p1_gates = {
        "witness": witness.get("status") in ("COUPLED", "SOFT_DRIFT"),
        "false_green": fg.get("passed", False),
        "k_tau": ktau.get("passed", False),
        "k8": k8.get("passed", False),
    }
    p1_pass = sum(1 for v in p1_gates.values() if v)
    structural_green_rate = p1_pass / len(p1_gates) if p1_gates else 0.0

    witness_coupling = witness.get("status", "UNKNOWN")
    false_green_count = 0
    for proj in witness.get("pi_num", []):
        if proj.get("id") == "N6":
            false_green_count = proj.get("value", 0)
            break

    nd_cleanliness = k8.get("k8_score")
    semantic_risk = cit.get("loop_count", 0) if not cit.get("skipped") else "UNKNOWN"

    return {
        "structural_green_rate": structural_green_rate,
        "p1_gates": p1_gates,
        "witness_coupling": witness_coupling,
        "false_green_count": false_green_count,
        "nd_surface_cleanliness": nd_cleanliness,
        "semantic_risk_open_count": semantic_risk,
        "k_tau": ktau.get("tau"),
        "admission_eligible": (
            p1_gates.get("witness") and
            p1_gates.get("false_green") and
            p1_gates.get("k_tau") and
            p1_gates.get("k8") and
            (isinstance(semantic_risk, int) and semantic_risk == 0
             or semantic_risk == "UNKNOWN")
        ),
    }


def print_matrix(results: dict, scorecard: dict) -> None:
    witness = results["witness"]
    fg = results["false_green"]
    ktau = results["k_tau"]
    k8 = results["k8"]
    cit = results["citation_probe"]

    def _mark(ok: bool | None) -> str:
        if ok is None:
            return "?"
        return "✅" if ok else "❌"

    print("\n╔══════════════════════════════════════════════════════╗")
    print("║         HELEN ECP CI MATRIX                          ║")
    print("╚══════════════════════════════════════════════════════╝")
    print()
    print("── P1 GUARDS (structural) ───────────────────────────────")
    ws = witness.get("status", "ERROR")
    ws_ok = ws in ("COUPLED", "SOFT_DRIFT")
    print(f"  {_mark(ws_ok)} witness_projection   {ws}")
    print(f"  {_mark(fg.get('passed'))} false_green_lint     N6={scorecard['false_green_count']}")
    tau_str = f"τ={ktau['tau']:.3f}" if ktau.get("tau") is not None else "τ=?"
    print(f"  {_mark(ktau.get('passed'))} k_tau_lint           {tau_str}")
    k8s = scorecard['nd_surface_cleanliness']
    k8_str = f"k8={k8s:+.3f}" if k8s is not None else "k8=?"
    print(f"  {_mark(k8.get('passed'))} k8_lint              {k8s is not None and k8s > 0}  {k8_str}")
    print()
    print("── P2 ROUTER (semantic risk) ────────────────────────────")
    if cit.get("skipped"):
        print(f"  ⚪ citation_graph_probe  SKIPPED — {cit['reason']}")
    else:
        loop_ok = cit.get("loop_count", 1) == 0
        loops = cit.get("loop_count", "?")
        print(f"  {_mark(loop_ok)} citation_graph_probe  loop_count={loops}")
        if not loop_ok:
            print(f"       ROUTE → SEMANTIC_REVIEW_REQUIRED")
            print(f"       loop_nodes={cit.get('loop_nodes', [])}")
    print()
    print("── ECP SCORECARD (diagnostic only — not admission) ──────")
    sgr = scorecard["structural_green_rate"]
    print(f"  structural_green_rate  : {sgr:.2f}  ({int(sgr * 4)}/4 P1 gates)")
    print(f"  witness_coupling       : {scorecard['witness_coupling']}")
    print(f"  false_green_count      : {scorecard['false_green_count']}")
    print(f"  nd_surface_cleanliness : {scorecard['nd_surface_cleanliness']}")
    sr = scorecard['semantic_risk_open_count']
    print(f"  semantic_risk_open     : {sr}")
    print()
    ae = scorecard["admission_eligible"]
    print(f"  admission_eligible     : {_mark(ae)} {'YES' if ae else 'NO'}")
    print()
    print("── CANONICAL BOUNDARY ───────────────────────────────────")
    print("  Φ, M, d_W, P, Probe  ⊬  A")
    print("  Probe(c)=Risk → Route(c)")
    print("  A(c)↓ → L_{t+1}=L_t⊕A(c) → g_{t+1}=Replay(L_{t+1})")
    print()


def main() -> int:
    parser = argparse.ArgumentParser(description="HELEN ECP CI matrix")
    parser.add_argument("--json", action="store_true", help="Output JSON only")
    parser.add_argument("--receipts-json", default=None,
                        help="Path to receipts JSON for citation probe")
    args = parser.parse_args()

    results = {}
    if not args.json:
        print("Running ECP probes...", flush=True)

    results["witness"] = run_witness()
    results["false_green"] = run_false_green()
    results["k_tau"] = run_k_tau()
    results["k8"] = run_k8()
    results["citation_probe"] = run_citation_probe(args.receipts_json)

    scorecard = build_matrix(results)

    if args.json:
        print(json.dumps({"results": results, "scorecard": scorecard}, indent=2))
    else:
        print_matrix(results, scorecard)

    rc = 0 if scorecard["admission_eligible"] else 1
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
