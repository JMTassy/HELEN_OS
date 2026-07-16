#!/usr/bin/env python3
"""
TRACE_ONLY AUTORESEARCH LOOP

Seed: HELEN begins by locating jurisdiction before cognition.

Mode:
- authority=false
- admission=FORBIDDEN
- no writes (stdout + optional /tmp candidates only)
- no web
- no ledger
- no commits
- proposal candidates only

Implements the exact 8-step loop from the doctrine.

Run:
  python temple/autoresearch/trace_only_autoresearch_loop.py --epochs 10 --seed "HELEN begins by locating jurisdiction before cognition."

Output: compressed invariants per epoch, convergence when stable for 3 epochs.

All output is trace/proposal. NO CLAIM.
"""

import argparse
import re
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

REPO_ROOT = Path("/Users/jean-marietassy/Documents/GitHub/helen_os_v1")

def current_doctrine(seed: str, epoch: int, history: list) -> str:
    """Step 1: State the current strongest operational doctrine."""
    if epoch == 0 or not history:
        return seed
    return history[-1]  # feed the last compressed as current for mutation

def mutate(doctrine: str, epoch: int = 0) -> str:
    """Step 2: Generate one stronger, simpler, or more general formulation.
    Uses epoch to vary and explore the three core forms over long runs.
    """
    d = doctrine.strip().rstrip('.')
    # Cycle through the distilled kernels and strengthen
    cores = [
        "No location → no doctrine.",
        "No test → no gate.",
        "No replay → no admission.",
    ]
    core = cores[epoch % 3]
    if "location" in d.lower() or epoch % 5 == 0:
        return core
    if "test" in d.lower() or epoch % 7 == 1:
        return core
    if "replay" in d.lower() or epoch % 11 == 2:
        return core
    # Strengthen the input
    return d + " " + core + " Must be enforced at the membrane."

def attack(doctrine: str, epoch: int = 0) -> str:
    """Step 3: Assume it is wrong. Find the strongest counterexample.
    Vary attacks to keep the loop alive for 100+ epochs.
    """
    dlower = doctrine.lower()
    attacks = [
        f"Counter: {doctrine} can be stated in docs but has no code enforcement (no gate calls the check).",
        f"Counter: A reflection can bypass and directly influence state without location or test.",
        f"Counter: The doctrine assumes replay but the implementation has no full ledger replay for this specific rule.",
        f"Counter: High-level models can generate equivalent behavior without ever naming the jurisdiction step.",
        f"Counter: In the Warren simulation, agents can act on 'proposals' that were never receipted.",
    ]
    return attacks[epoch % len(attacks)]

def locate(doctrine: str) -> Dict[str, str]:
    """Step 4: Locate - where does this live? code? docs? testable? 
    Now does real (read-only) scans for enforcement points.
    """
    locations = {
        "in_code": False,
        "in_docs": False,
        "testable": False,
        "replayable": False,
        "governance_compatible": False,
        "enforcement_points": [],
    }
    dlower = doctrine.lower()

    # Scan docs
    doc_files = list(REPO_ROOT.glob("docs/**/*.md")) + list(REPO_ROOT.glob("temple/**/*.md"))
    for f in doc_files[:20]:  # limit for trace
        try:
            text = f.read_text().lower()
            if any(k in text for k in ["jurisdiction", "metabolism", "proposal ⊬", "receipt", "gate"]):
                locations["in_docs"] = True
                locations["enforcement_points"].append(str(f.relative_to(REPO_ROOT)))
        except:
            pass

    # Scan code for enforcement
    code_files = list(REPO_ROOT.glob("temple/**/*.py")) + list(REPO_ROOT.glob("scripts/*.py"))
    for f in code_files[:30]:
        try:
            text = f.read_text().lower()
            if "receipt" in dlower and "receipt" in text and "mark" in text:
                locations["in_code"] = True
                locations["enforcement_points"].append(str(f.relative_to(REPO_ROOT)))
            if "replay" in dlower and ("ledger" in text or "replay" in text):
                locations["replayable"] = True
            if "test" in dlower and "def test_" in text:
                locations["testable"] = True
        except:
            pass

    locations["governance_compatible"] = locations["in_docs"] or locations["in_code"]

    if any(v for k,v in locations.items() if k != "enforcement_points"):
        return locations
    return {"status": "doctrine_only", "details": "No concrete location found in scanned sources."}

def extract(doctrine: str, location: Dict[str, str]) -> str:
    """Step 5: Keep only operational, testable, replayable, governance-compatible."""
    if "doctrine_only" in str(location):
        return "REJECT: " + doctrine
    # Strip metaphors etc.
    cleaned = re.sub(r'\s+', ' ', doctrine).strip()
    # Remove non-operational
    for bad in ["consciousness", "agi", "soul", "spirit", "beautiful", "elegant", "like ", "as if"]:
        cleaned = re.sub(rf'\b{bad}\b.*?(?=\.|$)', '', cleaned, flags=re.IGNORECASE)
    return cleaned.strip(" .") + "."

def compress(extracted: str) -> str:
    """Step 6: Rewrite into a single invariant. Aim for the shortest enforceable form."""
    if extracted.startswith("REJECT"):
        return extracted
    d = extracted.lower()
    # Prioritize the user's distilled forms
    if "no location" in d or "jurisdiction" in d:
        return "No location → no doctrine."
    if "no test" in d or "enforce" in d:
        return "No test → no gate."
    if "no replay" in d or "admission" in d:
        return "No replay → no admission."
    if "proposal" in d and "state" in d:
        return "proposal ⊬ state; receipt after gate only."
    if "metabolism" in d:
        return "The sequence of typed transformations is the invariant (Model ⊬ Organ)."
    # General compression
    core = extracted.split('.')[0].strip()
    return core + " (compressed invariant)."

def verify(compressed: str) -> bool:
    """Step 7: Can this become unit test / gate / replay invariant / ledger invariant?"""
    if compressed.startswith("REJECT"):
        return False
    operational_keywords = ["test", "gate", "invariant", "replay", "ledger", "validate", "enforce", "check"]
    return any(kw in compressed.lower() for kw in operational_keywords)

def convergence_check(history: List[str]) -> bool:
    """Step 8: If unchanged for 3 consecutive epochs, stop."""
    if len(history) < 3:
        return False
    last_three = history[-3:]
    return len(set(last_three)) == 1

def run_loop(seed: str, max_epochs: int = 10, verbose: bool = True) -> List[Dict]:
    history = []
    candidates = []
    current = seed

    for epoch in range(1, max_epochs + 1):
        doctrine = current_doctrine(current, epoch - 1, history)
        mutated = mutate(doctrine, epoch)
        counter = attack(mutated, epoch)
        location = locate(mutated)
        extracted = extract(mutated, location)
        compressed = compress(extracted)
        is_valid = verify(compressed)

        epoch_result = {
            "epoch": epoch,
            "current_doctrine": doctrine,
            "mutated": mutated,
            "attack": counter,
            "location": location,
            "extracted": extracted,
            "compressed": compressed,
            "verified": is_valid,
        }
        candidates.append(epoch_result)
        history.append(compressed)

        if verbose:
            print(f"E{epoch:02d}: {compressed[:100]}... | verified={is_valid}")

        if is_valid:
            current = compressed
        else:
            current = doctrine

        if convergence_check(history):
            if verbose:
                print(f"Convergence at epoch {epoch} (stable for 3 epochs).")
            # For long runs, continue mutating to explore further variants (trace only)
            if max_epochs > 20:
                pass  # continue for full budget
            else:
                break

    return candidates

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", default="HELEN begins by locating jurisdiction before cognition.")
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--verbose", action="store_true", default=True)
    parser.add_argument("--out", default="/tmp/trace_only_candidates.json")
    args = parser.parse_args()

    print("TRACE_ONLY AUTORESEARCH LOOP")
    print(f"Seed: {args.seed}")
    print(f"Max epochs: {args.epochs}")
    print("Mode: authority=false, proposal candidates only, no writes to sovereign paths.")
    print("---")

    results = run_loop(args.seed, args.epochs, args.verbose)

    # Output only candidates (no writes except optional /tmp for trace)
    output = {
        "schema": "TRACE_ONLY_AUTORESEARCH_LOOP_V0",
        "seed": args.seed,
        "epochs_run": len(results),
        "converged": len(results) > 0 and convergence_check([r["compressed"] for r in results]),
        "candidates": [r for r in results if r["verified"]],
        "all_epochs": results,
        "timestamp": datetime.now().isoformat(),
        "authority": False,
        "admission": "FORBIDDEN",
    }

    out_path = Path(args.out)
    out_path.write_text(json.dumps(output, indent=2))
    print(f"\nWrote candidates to {out_path} (trace only).")
    print("NO CLAIM. NO SHIP. PROPOSAL CANDIDATES ONLY.")

    # Print final compressed if any
    valid = [r["compressed"] for r in results if r["verified"]]
    if valid:
        print("\nFinal compressed invariant(s):")
        for v in valid[-3:]:
            print(f"  - {v}")

if __name__ == "__main__":
    main()