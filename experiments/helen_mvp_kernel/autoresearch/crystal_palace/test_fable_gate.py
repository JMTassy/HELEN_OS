"""FABLE-gate falsifiers. 🔵 OBSERVED · authority=0.

Closes the live counterexample from epoch 02: C_valid=0 (no witnessed hypotheses) yet n_eff_H=2 —
synthesis minting mechanisms from nothing. The gate enforces: opacity ⊬ synthesis; cluster ⊬
corroboration. Run: python3 test_fable_gate.py  (standalone; no ollama needed).
"""
import importlib.util, os

_spec = importlib.util.spec_from_file_location(
    "loop_driver", os.path.join(os.path.dirname(os.path.abspath(__file__)), "loop_driver.py"))
loop_driver = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(loop_driver)
synthesis_is_witnessed = loop_driver.synthesis_is_witnessed


def _g(H=(), error=False, exhausted=False, O=()):
    return {"H": list(H), "O": list(O), "error": error, "S": {"exhausted": exhausted}}


def test_fable01_e02_reproduction_all_opaque_is_gated():
    # the exact e02 shape: 10 goblins, all errored/empty → synthesis must be UNKNOWN, not fabricated
    goblins = [_g(error=True, H=[]) for _ in range(10)]
    assert synthesis_is_witnessed(goblins) is False   # ← was the laundering path; now gated


def test_fable01b_observations_without_hypotheses_are_not_synthesis_input():
    # goblins produced observations (O) but ZERO hypotheses (H) → FABLE has nothing to cluster → gated
    goblins = [_g(H=[], O=["saw a table"]) for _ in range(10)]
    assert synthesis_is_witnessed(goblins) is False


def test_fable02_one_witnessed_hypothesis_ungates():
    goblins = [_g(error=True) for _ in range(9)] + [_g(H=["numbering is addressability"])]
    assert synthesis_is_witnessed(goblins) is True    # positive control (non-vacuity)


def test_fable03_errored_or_exhausted_goblin_H_does_not_count():
    # a hypothesis from an ERRORED goblin is untrusted; from an EXHAUSTED slice is empty coverage
    assert synthesis_is_witnessed([_g(H=["x"], error=True)]) is False
    assert synthesis_is_witnessed([_g(H=["x"], exhausted=True)]) is False


if __name__ == "__main__":
    import traceback
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    fails = 0
    for t in tests:
        try:
            t(); print(f"  PASS {t.__name__}")
        except Exception:
            fails += 1; print(f"  FAIL {t.__name__}"); traceback.print_exc()
    print(f"\n{len(tests)-fails}/{len(tests)} passed")
    raise SystemExit(1 if fails else 0)
