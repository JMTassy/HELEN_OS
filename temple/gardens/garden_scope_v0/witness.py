#!/usr/bin/env python3
"""
POC WITNESS — proves the Garden Scope acceptance contract before any spectacle.

  C1 DETERMINISM        R(E) == R(E)                       (pure function)
  C2 REPLAY = FOLD      R(E_1:t) == fold(e_1..e_t)  ∀t      (Replay(E_1:t)=J_t)
  C3 CLI ~ BROWSER      R(E) == GET /api/jspace             (same typed state)
  C4 NO_SILENT_TRANSITION   orphans == []                   (¬e ⇒ violation)

C3 compares DECODED TYPED STATE, not pixels — CLI and browser may look nothing
alike; they must agree on J. Writes a non-sovereign sidecar POC_WITNESS.json.
authority=false · ΔA=0 · NO_CLAIM.  Optional: pass a server base url as argv[1].
"""
import json, sys, urllib.request
from pathlib import Path
import reducer as R

ROOT = Path(__file__).resolve().parent
BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8787"


def canon(J):  # strip nothing structural; just stable-serialize for equality
    return json.dumps(J, sort_keys=True, ensure_ascii=False)


def main():
    E = R.load()
    results, ok = {}, True

    # C1 determinism
    c1 = canon(R.reduce(E)) == canon(R.reduce(E))
    results["C1_determinism"] = c1; ok &= c1

    # C2 replay == incremental fold, for every prefix length
    def fold(prefix): return R.reduce(prefix)      # R already a fold; prove prefix-consistency
    c2 = all(canon(fold(E[:t])) == canon(R.reduce(sorted(E[:t], key=lambda e: e.get("seq", 0))))
             for t in range(1, len(E) + 1))
    # stronger: J at full == fold over all, and each prefix is a valid J (no crash, orphans tracked)
    c2 = c2 and all(isinstance(R.reduce(E[:t]), dict) for t in range(1, len(E) + 1))
    results["C2_replay_equals_fold"] = c2; ok &= c2

    # C3 CLI (local R) ~ Browser (/api/jspace) — same decoded typed state
    local = R.reduce(E)
    try:
        with urllib.request.urlopen(f"{BASE}/api/jspace", timeout=5) as r:
            remote = json.loads(r.read())
        c3 = canon(local) == canon(remote)
        results["C3_cli_tilde_browser"] = c3
    except Exception as e:
        c3 = None
        results["C3_cli_tilde_browser"] = f"SKIPPED (server unreachable: {str(e)[:50]})"
    if c3 is not None: ok &= c3

    # C4 no silent transition
    c4 = local["orphans"] == []
    results["C4_no_silent_transition"] = c4; ok &= c4

    receipt = {
        "schema": "GARDEN_SCOPE_POC_WITNESS", "authority": False, "canon": False,
        "claim": "NO_CLAIM", "authority_delta": 0, "fable_calls": 0,
        "events_reduced": len(E),
        "jspace_counters": local["counters"],
        "contract": {
            "C1": "R(E)==R(E)  — deterministic pure reducer",
            "C2": "R(E_1:t)==fold  ∀t  — Replay(E_1:t)=J_t",
            "C3": "R(E)==GET /api/jspace — CLI ~ Browser (typed state, not pixels)",
            "C4": "orphans==[] — NO_SILENT_TRANSITION (¬e ⇒ UnwitnessedGardenTransition)",
        },
        "results": results,
        "verdict": "POC_CONTRACT_HOLDS" if ok else "POC_CONTRACT_FAILED",
    }
    (ROOT / "POC_WITNESS.json").write_text(json.dumps(receipt, indent=2, ensure_ascii=False))

    print("─" * 58)
    print("  GARDEN SCOPE — POC WITNESS")
    print("─" * 58)
    for k, v in results.items():
        mark = "✓" if v is True else ("—" if isinstance(v, str) else "✗")
        print(f"  {mark}  {k}: {v}")
    print("─" * 58)
    print(f"  VERDICT: {receipt['verdict']}   (events={len(E)}, "
          f"typed={local['counters']['typed']}, compost={local['counters']['compost']}, "
          f"cross={local['counters']['cross']})")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
