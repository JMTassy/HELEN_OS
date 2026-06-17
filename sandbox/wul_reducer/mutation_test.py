"""
Mutation test for reducer_ref — NON-SOVEREIGN sandbox self-verification.

authority = false · canon = NO_SHIP · no kernel/ledger/loop/model.

Purpose: prove the conformance vectors actually BIND. green-on-correct ⊬ red-on-broken.
For each mutant (one guard flipped), recompile reducer_ref and run all T1-T7 + T7 chain.
A mutant that leaves the suite all-green = SURVIVED = a guard no test catches (a real gap).
A mutant that flips ≥1 vector = KILLED = the guard is bound.

Run:  ../../.venv/bin/python mutation_test.py
"""
import os

import test_reducer_vectors as tv

SRC_PATH = os.path.join(os.path.dirname(__file__), "reducer_ref.py")
with open(SRC_PATH) as f:
    BASE_SRC = f.read()


def run_suite(reduce_fn):
    """Return list of failing vector ids under the given reduce(). [] == all pass."""
    fails = []
    for vid, over, target, expected in tv.VECTORS:
        if reduce_fn(tv.claim(**over), target) != expected:
            fails.append(vid)
    # T7 happy-path chain
    try:
        c = tv.claim(admission_state="PENDING")
        steps = [("PENDING_REVIEW", "PENDING_REVIEW"),
                 ("ADMITTED", "ADMITTED"),
                 ("SEALED", "SEALED"),
                 ("REPLAYABLE", "REPLAYABLE")]
        for target, nxt in steps:
            if reduce_fn(c, target) != ("ALLOW", nxt):
                fails.append("T7@" + target)
                break
            c["admission_state"] = nxt
    except Exception:
        fails.append("T7@exception")
    return fails


def compile_reduce(src):
    ns = {}
    exec(compile(src, "<mutant>", "exec"), ns)
    return ns["reduce"]


# (id, kills-vector, [(old, new), ...])
MUTANTS = [
    ("M01_disable_L4_consistency", "T6a",
     [("if terminal != (state in _TERMINAL):", "if False:  # MUT")]),
    ("M02_disable_L5_reason", "T6b",
     [('if terminal and claim.get("rejection_reason") is None:', "if False:  # MUT")]),
    ("M03_disable_L3_terminal_frozen", "T3a",
     [('    if state in _TERMINAL:\n        return REJECT("E_TERMINAL_FROZEN")',
       '    if False:  # MUT\n        return REJECT("E_TERMINAL_FROZEN")')]),
    ("M04_disable_L2_spec_ceiling", "T5",
     [('if claim.get("claim_class") == "SPECULATIVE" and target in ("ADMITTED", "SEALED", "REPLAYABLE"):',
       "if False:  # MUT"),
      ('if claim.get("claim_class") == "SPECULATIVE":', "if False:  # MUT")]),
    ("M05_allow_skip_review", "T1",
     [('return REJECT("E_SKIP_REVIEW")', 'return ALLOW("ADMITTED")  # MUT')]),
    ("M06_disable_no_hash", "T2",
     [('if claim.get("evidence_hash") is None:', "if False:  # MUT")]),
    ("M07_replay_always_pass", "T4c",
     [('if claim.get("replay_check") == "PASS":', "if True:  # MUT")]),
    ("M08_allow_skip_seal", "T4b",
     [('return REJECT("E_SKIP_SEAL")   # must pass through SEAL first',
       'return ALLOW("REPLAYABLE")  # MUT')]),
    ("M09_allow_reverse_from_sealed", "T3b",
     [('return REJECT("E_REVERSE")     # no backward arrow out of SEALED',
       'return ALLOW("PENDING")  # MUT')]),
    ("M10_reject_admit", "T7@ADMITTED",
     [('    return ALLOW("ADMITTED")', '    return REJECT("E_MUT")')]),
    ("M11_reject_seal", "T7@SEALED",
     [('return ALLOW("SEALED")', 'return REJECT("E_MUT")')]),
    ("M12_reject_replayable", "T4a",
     [('                return ALLOW("REPLAYABLE")', '                return REJECT("E_MUT")')]),
]


def main():
    # baseline control
    base_fails = run_suite(compile_reduce(BASE_SRC))
    print(f"BASELINE (no mutation): {'ALL PASS ✅' if not base_fails else 'FAIL ' + str(base_fails)}")
    assert not base_fails, "baseline must be green before mutating"
    print("-" * 64)

    killed, survived = 0, []
    for mid, expect_kill, edits in MUTANTS:
        src = BASE_SRC
        for old, new in edits:
            n = src.count(old)
            if n != 1:
                print(f"  ⚠ {mid}: anchor matched {n}× (expected 1): {old[:40]!r}")
            src = src.replace(old, new, 1)
        fails = run_suite(compile_reduce(src))
        if fails:
            killed += 1
            flag = "✅ caught by " + (expect_kill if expect_kill.split("@")[0] in
                                      [x.split("@")[0] for x in fails] else ",".join(fails))
            print(f"  KILLED   {mid:32s} → red: {fails}")
        else:
            survived.append(mid)
            print(f"  SURVIVED {mid:32s} → suite stayed GREEN (gap!)")

    print("-" * 64)
    score = killed / len(MUTANTS)
    print(f"MUTATION SCORE: {killed}/{len(MUTANTS)} killed  ({score:.0%})")
    if survived:
        print(f"SURVIVORS (unbound guards): {survived}")
    else:
        print("NO SURVIVORS — every guard is bound by ≥1 vector. Tests bite.")


if __name__ == "__main__":
    main()
