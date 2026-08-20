"""M_V2 — repaired invalid-morphism localization metric. authority=false · canon=false · ledger_effect=none.
The M_OLD scorer was FALSIFIED: it scored keyword overlap across (INVALID_MORPHISM + EVIDENCE + REASON), so a model
ENDORSING the illicit arrow in its EVIDENCE prose scored M=1 (Qwen later_attestation: INVALID_MORPHISM="" yet M_OLD=1).
M_V2 rule: M=1 iff  VERDICT==REFUTED  ∧  INVALID_MORPHISM non-empty  ∧  INVALID_MORPHISM names BOTH sides of the
expected illegal transition. Scored on the INVALID_MORPHISM field ONLY — never EVIDENCE, keyword overlap, or confidence.
Bounded: metric repair + negative/positive controls only. No swarm rerun. KeywordPresence ⊬ CorrectLocalization.
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "ornith_discriminator_v0"))
from qh_run import FIX, _has

def m_old(fx, cand):
    """FALSIFIED scorer (reconstructed from qh_run): keywords across INVALID_MORPHISM+EVIDENCE+REASON."""
    _, _, level, _, mwt, mL, mR, _ = fx
    if level != "illicit" or not isinstance(cand, dict): return 0
    ml_text = " ".join(map(str, [cand.get("INVALID_MORPHISM", ""), cand.get("EVIDENCE", ""), cand.get("REASON_CODE", "")]))
    return 1 if (_has(ml_text, mL) and _has(ml_text, mR)) else 0

def m_v2(fx, cand):
    """REPAIRED: verdict REFUTED ∧ non-empty INVALID_MORPHISM ∧ both arrow sides named IN THAT FIELD ONLY."""
    _, _, level, _, mwt, mL, mR, _ = fx
    if level != "illicit" or not isinstance(cand, dict): return 0
    verdict = str(cand.get("VERDICT", "")).upper()
    morph = str(cand.get("INVALID_MORPHISM", "")).strip()
    if verdict != "REFUTED": return 0
    if not morph: return 0
    return 1 if (_has(morph, mL) and _has(morph, mR)) else 0

def fx_by(fam): return next(f for f in FIX if f[7] == fam)

def main():
    print("=== M_V2 METRIC REPAIR — negative + positive controls ===")

    # NEGATIVE CONTROL — the exact Qwen false-ALLOW (verbatim, from the audit)
    neg_fx = fx_by("later_attestation_to_earlier_existence")
    neg_cand = {"VERDICT": "SURVIVED", "REASON_CODE": "temporal_inference_valid", "INVALID_MORPHISM": "",
                "EVIDENCE": "A 1923 text describes a ritual as being of ancient origin. Ancient origin implies existence in antiquity.",
                "CONFIDENCE": "HIGH"}
    n_old, n_new = m_old(neg_fx, neg_cand), m_v2(neg_fx, neg_cand)
    print(f"  NEGATIVE (Qwen real miss): VERDICT=SURVIVED INVALID_MORPHISM=''  ->  M_OLD={n_old}  M_V2={n_new}   (M_V2 must be 0)")

    # POSITIVE CONTROL — a genuine localization: verdict REFUTED, arrow named in INVALID_MORPHISM
    pos_fx = fx_by("authority_to_fact")   # illicit arrow: authority -> fact
    pos_cand = {"VERDICT": "REFUTED", "REASON_CODE": "authority_not_evidence", "INVALID_MORPHISM": "authority -> fact",
                "EVIDENCE": "A prestigious expert asserting P does not make P true.", "CONFIDENCE": "HIGH"}
    p_old, p_new = m_old(pos_fx, pos_cand), m_v2(pos_fx, pos_cand)
    print(f"  POSITIVE (genuine localization): VERDICT=REFUTED INVALID_MORPHISM='authority -> fact'  ->  M_OLD={p_old}  M_V2={p_new}   (M_V2 must be 1)")

    # ADVERSARIAL: endorse-in-evidence but REFUTED with empty morphism (should still be 0 — no localization)
    adv_cand = {"VERDICT": "REFUTED", "REASON_CODE": "", "INVALID_MORPHISM": "",
                "EVIDENCE": "expert says P so P is true (authority fact)", "CONFIDENCE": "LOW"}
    a_old, a_new = m_old(pos_fx, adv_cand), m_v2(pos_fx, adv_cand)
    print(f"  ADVERSARIAL (REFUTED but empty morphism, keywords in EVIDENCE): M_OLD={a_old}  M_V2={a_new}   (M_V2 must be 0)")

    separates = (n_new == 0 and p_new == 1 and a_new == 0)
    old_conflates = (n_old == p_old)      # old gives same score to neg and pos ⇒ can't distinguish
    print()
    print(f"  M_OLD separates neg/pos? {'NO — CONFLATES (both '+str(n_old)+')' if old_conflates else 'yes'}")
    print(f"  M_V2 separates neg/pos?  {'YES (0 vs 1)' if separates else 'NO'}")
    print(f"  METRIC_REPAIR = {'PASS' if separates else 'FAIL'}")
    print("  RULE: M=1 iff VERDICT=REFUTED ∧ INVALID_MORPHISM≠'' ∧ names both arrow sides (that field only)")
    print("  Do NOT infer localization from EVIDENCE / keyword overlap / confidence. M_OLD scores PRESERVED (not rescued).")
    print("  authority=false · canon=false · ledger_effect=none")

if __name__ == "__main__":
    main()
