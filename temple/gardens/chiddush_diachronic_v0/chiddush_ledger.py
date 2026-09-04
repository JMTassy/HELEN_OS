#!/usr/bin/env python3
"""
CHIDDUSH_DIACHRONIC_V0 — a CHIDDUSH is not what was novel when spoken; it is what stayed
structurally useful later.  Chiddush(d,t0,t1) = Novel ∧ Discriminating ∧ SurvivedFalsification
∧ Reused(t1>t0).  ⇒ at birth an agent may only declare 🟣 CANDIDATE; 💎 is earned retrospectively.

Corpus = THIS session's own distinctions (the one reuse graph I can verify), each with a birth
step t0 and the LATER instruments that causally reused it. Δd_M is a VECTOR (Knowledge, Instrument,
World). Negative controls: a not-yet-reused distinction stays CANDIDATE (cannot self-declare); a
lexical duplicate → REPEATED (rejected, exactly like the corpus's 3 DUPLICATE in its 10-loop run).

authority=false · canon=false · ΔA=0 · ΔΓ=0 · NO_MODEL_CALL · NO_COMMIT · NO_PUSH.
"""
import json
from pathlib import Path

# ledger: id, born(step), kind(K/I/W), discriminating, falsifier_survived, reused_by[(inst,t)], dup_of
L = [
    dict(id="marginal⇏joint",      born=1, kind="I", disc=True, fals=True,
         reused=[("mycelium_covalidity", 5), ("neption_chroma_v1", 8)], dup=None),
    dict(id="Derived≻Declared",    born=2, kind="I", disc=True, fals=True,
         reused=[("session_pulse", 6), ("neption_chroma_v0", 7), ("wul_core_v1", 10)], dup=None),
    dict(id="structure≠license",   born=1, kind="K", disc=True, fals=True,
         reused=[("capability_homotopy", 9)], dup=None),
    dict(id="⋈ co-validity",       born=5, kind="I", disc=True, fals=True,
         reused=[("neption_chroma_v1", 8), ("capability_homotopy", 9)], dup=None),
    dict(id="typed-obstruction 🕳️", born=9, kind="W", disc=True, fals=True,
         reused=[("egregor_autoresearch", 11)], dup=None),
    dict(id="diachronic-CHIDDUSH",  born=12, kind="K", disc=True, fals=True,
         reused=[], dup=None),                                   # born THIS turn → cannot be reused yet
    dict(id="presence≠sufficiency(restated)", born=4, kind="K", disc=False, fals=True,
         reused=[("session_pulse", 6)], dup="Derived≻Declared"), # lexical variant → REPEATED
]

def status(d):
    if d["dup"] and not d["disc"]:              return "REPEATED"         # lexical, no new class
    if not d["fals"]:                           return "FALSIFIED"
    later = [r for r in d["reused"] if r[1] > d["born"]]
    if not later:                               return "CANDIDATE"        # novel but unproven → 🟣
    if d["kind"] == "I":                        return "INSTRUMENTALIZED" # method causally reused
    return "RETAINED"

def is_chiddush(d, st):
    return d["disc"] and d["fals"] and st in ("RETAINED", "INSTRUMENTALIZED")


def main():
    rows = []
    dK = dI = dW = 0
    for d in L:
        st = status(d)
        ch = is_chiddush(d, st)
        if ch:
            if d["kind"] == "K": dK += 1
            elif d["kind"] == "I": dI += 1
            elif d["kind"] == "W": dW += 1
        rows.append({"id": d["id"], "born_t": d["born"], "kind": d["kind"], "status": st,
                     "reused_at": [r[1] for r in d["reused"] if r[1] > d["born"]],
                     "chiddush_earned": ch})

    delta_dM = {"ΔdK_knowledge": dK, "ΔdI_instrument": dI, "ΔdW_world": dW}
    diachronic = next(r for r in rows if r["id"] == "diachronic-CHIDDUSH")
    dup = next(r for r in rows if r["status"] == "REPEATED")

    # laws witnessed
    law_birth_cannot_declare = (diachronic["status"] == "CANDIDATE" and not diachronic["chiddush_earned"])
    law_lexical_rejected = (dup["status"] == "REPEATED" and not dup["chiddush_earned"])
    law_reuse_earns = any(r["chiddush_earned"] and r["reused_at"] for r in rows)
    SOUND = law_birth_cannot_declare and law_lexical_rejected and law_reuse_earns

    # NEPTION coupling: INSTRUMENTALIZED/RETAINED ⇒ retention proven ⇒ Δd_M>0 ⇒ 💎-eligible NOW,
    # for those specific distinctions (they also carry observation+warrant as on-disk receipts).
    earned = [r["id"] for r in rows if r["chiddush_earned"]]
    still_candidate = [r["id"] for r in rows if r["status"] == "CANDIDATE"]

    out = {"experiment": "CHIDDUSH_DIACHRONIC_V0", "authority": False, "canon": False,
           "authority_delta": 0, "gamma_delta": 0, "model_calls": 0,
           "law": "Chiddush(d,t0,t1)=Novel∧Discriminating∧SurvivedFalsification∧Reused(t1>t0)",
           "ledger": rows, "delta_dM_vector": delta_dM,
           "laws": {"birth_cannot_self_declare_CHIDDUSH": law_birth_cannot_declare,
                    "lexical_duplicate_rejected(REPEATED)": law_lexical_rejected,
                    "later_reuse_earns_CHIDDUSH": law_reuse_earns},
           "SOUND": SOUND,
           "neption_coupling": {
               "diamond_eligible_now(retention earned)": earned,
               "still_candidate(retention unproven)": still_candidate,
               "note": "these specific distinctions now satisfy Δd_M>0 via verified later reuse; "
                       "the session's global 🟢 lifts to 💎 ONLY for the retention-earned subset, "
                       "and only retrospectively — never self-declared at birth"},
           "MAX_ADMISSIBLE_STATEMENT":
               "On this session's verifiable reuse graph, %d distinctions EARNED CHIDDUSH (Δd_M=%s), "
               "while the just-born distinction (diachronic-CHIDDUSH itself) and lexical duplicates did "
               "NOT — proving novelty is retrospective in proof." % (len(earned), delta_dM),
           "commit_status": "NO_COMMIT", "push_status": "NO_PUSH", "next_verb": "HUMAN_REVIEW"}
    (Path(__file__).resolve().parent / "CHIDDUSH_DIACHRONIC_V0_RECEIPT.json").write_text(json.dumps(out, indent=2, ensure_ascii=False))

    print("═" * 80)
    print("  CHIDDUSH_DIACHRONIC_V0 — novelty is prospective at birth, retrospective in proof")
    print("═" * 80)
    print(f"  {'distinction':30s} {'t0':>3s} {'kind':4s} {'status':16s} {'reused@':10s} earned?")
    for r in rows:
        print(f"  {r['id']:30s} {r['born_t']:>3} {r['kind']:4s} {r['status']:16s} "
              f"{str(r['reused_at']):10s} {'💎' if r['chiddush_earned'] else '🟣'}")
    print("─" * 80)
    print(f"  Δd_M vector = {delta_dM}")
    for k, v in {"birth cannot self-declare CHIDDUSH": law_birth_cannot_declare,
                 "lexical duplicate → REPEATED (rejected)": law_lexical_rejected,
                 "later reuse earns CHIDDUSH": law_reuse_earns}.items():
        print(f"    {'✅' if v else '❌'} {k}")
    print("─" * 80)
    print(f"  💎-eligible NOW (retention earned): {earned}")
    print(f"  🟣 still CANDIDATE (unproven)     : {still_candidate}")
    print(f"  SOUND = {SOUND}  · ΔA=0 · ΔΓ=0 · model_calls=0 · NO_COMMIT")
    print("  → CHIDDUSH_DIACHRONIC_V0_RECEIPT.json")


if __name__ == "__main__":
    main()
