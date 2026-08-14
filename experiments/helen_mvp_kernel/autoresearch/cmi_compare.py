#!/usr/bin/env python3
"""CMI comparator — two-stage: CAPABILITY GATE → yield comparison. 🔵 OBSERVED · authority=false.

Lesson from the Qwen3.5-4B pilot (it emitted [] on all seeds): a model that fails the
task-capability gate is INELIGIBLE_FOR_YIELD_COMPARISON, not ΔQ=0. Conflating the two
would launder 'model below floor' into 'lineage has no value' — a false conclusion the
experiment does not license. So: gate first, compare only eligible arms.

CAPABILITY_GATE(arm) = PASS iff at least one seed is PARSED_NONEMPTY AND the arm's useful
observational-class set is non-empty (min structural coverage). Else FAIL → UNMEASURED.
"""
import glob
import json
import os

HERE = os.path.dirname(__file__)
ARM_DIR = os.path.join(HERE, "..", "artifacts", "local_first")


def load_arms():
    arms = {}
    for p in sorted(glob.glob(os.path.join(ARM_DIR, "cmi_v0_*.json"))):
        d = json.load(open(p))
        arms[d["arm"]] = d
    return arms


def capability_gate(arm) -> bool:
    any_nonempty = any(s["state"] == "PARSED_NONEMPTY" for s in arm["per_seed"])
    has_useful = len(arm["Q_useful"]) > 0
    return bool(any_nonempty and has_useful)


def main():
    arms = load_arms()
    if not arms:
        print("no arm files found in", ARM_DIR)
        return
    qids = {a["qid"] for a in arms.values()}
    print(f"QID(s): {qids}  {'(frozen, matched)' if len(qids)==1 else '!! QID MISMATCH — arms not comparable'}")
    print("=" * 68)
    eligible = {}
    for name, a in arms.items():
        g = capability_gate(a)
        verdict = "PASS" if g else "FAIL → INELIGIBLE_FOR_YIELD_COMPARISON"
        print(f"{name:16} exec={a['execution_yield']:.2f} parse={a['parse_yield']:.2f} "
              f"Q_useful={a['Q_useful']}")
        print(f"{'':16} CAPABILITY_GATE = {verdict}")
        if g:
            eligible[name] = set(a["Q_useful"])
    print("=" * 68)
    if len(eligible) < 2:
        ineligible = [n for n in arms if n not in eligible]
        print(f"YIELD COMPARISON: NOT POSSIBLE — only {len(eligible)} arm(s) passed the capability gate.")
        for n in ineligible:
            print(f"  {n}: LINEAGE_VALUE = UNMEASURED (below task-capability floor; ΔQ is NOT a lineage finding)")
        print("\nNEXT (per experiment sequence): need a different-lineage model ABOVE the demonstrated")
        print("floor (C3) before the cross-lineage ΔQ question can be answered. A failed small-model")
        print("arm does NOT establish that cross-lineage diversity has zero value.")
        return
    names = list(eligible)
    print("YIELD COMPARISON (eligible arms only):")
    for i in range(len(names)):
        for j in range(len(names)):
            if i == j:
                continue
            a, b = names[i], names[j]
            print(f"  ΔQ_useful,{a}|{b} = {sorted(eligible[a] - eligible[b])}")


if __name__ == "__main__":
    main()
