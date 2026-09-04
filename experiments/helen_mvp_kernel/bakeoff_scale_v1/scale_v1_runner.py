"""BAKEOFF SCALE_V1 runner scaffold. authority=false · canon=false · ledger_effect=none. NON-SOVEREIGN.
INERT BY DEFAULT — this is a PRE-REGISTERED design, not an authorized campaign. It refuses to run unless:
  (1) the operator passes --execute-verb "EXECUTE SCALE_V1", AND
  (2) scale_v1_design.json still hashes to the sealed prereg_hash (no post-registration drift).
Executing the campaign is a SEPARATE operator decision. Until then this file only validates the seal.

Design is authored in scale_v1_design.json (the frozen source of truth). This runner reads it; it does NOT
embed its own knobs, so it cannot drift from the pre-registration.
"""
import argparse, hashlib, json, pathlib, sys

HERE = pathlib.Path(__file__).resolve().parent
DESIGN = HERE / "scale_v1_design.json"
SEAL = HERE / ".prereg_hash"

def prereg_hash():
    return hashlib.sha256(DESIGN.read_bytes()).hexdigest()

def verify_seal():
    live = prereg_hash()
    sealed = SEAL.read_text().strip() if SEAL.exists() else None
    ok = sealed is not None and live == sealed
    print(f"prereg_hash live  : {live}")
    print(f"prereg_hash sealed: {sealed}")
    print(f"SEAL: {'MATCH — design is the pre-registered one' if ok else 'DRIFT — design changed since freeze; refusing'}")
    return ok

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify-seal", action="store_true", help="check the design still matches its prereg_hash")
    ap.add_argument("--execute-verb", default="", help='must be exactly "EXECUTE SCALE_V1" to run the campaign')
    a = ap.parse_args()

    if a.verify_seal or not a.execute_verb:
        ok = verify_seal()
        if not a.execute_verb:
            print("\nSTATUS: DESIGN_FROZEN__NOT_EXECUTED. No campaign runs without --execute-verb 'EXECUTE SCALE_V1'.")
            print("This scaffold is inert by design (pre-registration discipline). See SCALE_V1_PREREG.md.")
        sys.exit(0 if ok else 2)

    if a.execute_verb != "EXECUTE SCALE_V1":
        print(f"REFUSED: execute verb '{a.execute_verb}' != 'EXECUTE SCALE_V1'."); sys.exit(2)
    if not verify_seal():
        print("REFUSED: design drifted from its prereg_hash. Re-freeze intentionally before any run."); sys.exit(2)

    # ── Campaign body intentionally NOT IMPLEMENTED in the pre-registration commit. ──
    # It is added under the EXECUTE SCALE_V1 verb, implementing exactly the frozen design:
    #   for cfg in (C1,C3,C5): for r in range(R): run K goblins (nested lenses) -> freeze -> K HAL trials
    #   -> gates (G_config,G_evaluable,G_gov) -> metrics (N_P,N_E,N_earned,Stability,Cost,Review)
    #   -> assert admission_noninterference (Γ_A = ∅ at every K) else CAMPAIGN_ABORT.
    d = json.loads(DESIGN.read_text())
    print("SEAL verified + verb accepted, but campaign body is not present in the pre-registration commit.")
    print(f"Design ready: configs={list(d['configurations'].keys() & {'C1','C3','C5'}) or ['C1','C3','C5']} R={d['repeats']['R']} "
          f"total_calls={d['repeats']['total_calls']['sum']}.")
    print("Add the campaign body under the EXECUTE verb, implementing the frozen design verbatim. Refusing to improvise it now.")
    sys.exit(0)

if __name__ == "__main__":
    main()
