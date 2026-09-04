#!/usr/bin/env python3
"""
RECEIPT_DELTA_ZERO_FALSIFIER_V0 — kill the confusion  ReceiptValid(r) ⇏ Δσ(r)≠0.

A well-formed, hash-valid receipt can attest a NO-OP. Validity of the receipt is NOT
evidence that governed state moved, and neither is a *printed* `claimed_delta` field.
The discriminator computes Δσ = Diff(σ_before, σ_after) ITSELF and ignores what the
receipt claims.

Three objects that must never re-glue:
    receipt validity   ≠   state transition   ≠   authority transition.

Fixtures (tested domain only — NOT a universal statement about HELEN receipts):
  r0 : σ_before = σ_after , Valid=1   → DerivedDelta = 0      (valid no-op)
  r1 : σ_before ≠ σ_after , Valid=1   → DerivedDelta ≠ 0      (soundness: diff engine bites)
  M  : σ_before = σ_after , claimed_delta≠0 , Valid=1 → DerivedDelta = 0  (receipt lies; derivation wins)

authority=false · canon=false · ΔA=0 · NO_CLAIM · NO_MODEL_CALL · NO_COMMIT · NO_PUSH ·
synthetic fixtures only — no real ledger / no real receipt schema touched.
"""
import hashlib, json
from pathlib import Path


def canon(o): return json.dumps(o, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
def sha(o):   return hashlib.sha256(canon(o).encode()).hexdigest()


def make_receipt(rid, state_before, state_after, authority_before, authority_after,
                 claimed_delta):
    """A receipt is a signed payload. The signature covers everything INCLUDING any
    claimed_delta — so a lie can be validly signed. Signing ≠ truth of the claim."""
    payload = {"receipt_id": rid, "tool": "noop_or_real",
               "state_before": state_before, "state_after": state_after,
               "authority_before": authority_before, "authority_after": authority_after,
               "claimed_delta": claimed_delta}
    return {"payload": payload, "sig": sha(payload)}


def VerifyReceipt(r):
    """STRUCTURAL validity only: required fields present + signature re-derives.
    Says NOTHING about whether state moved. This is the honest scope of a receipt."""
    p = r.get("payload", {})
    required = ("receipt_id", "state_before", "state_after",
                "authority_before", "authority_after")
    well_formed = all(k in p for k in required)
    sig_ok = (r.get("sig") == sha(p))
    return 1 if (well_formed and sig_ok) else 0


def DerivedDelta(r):
    """Δσ computed by the discriminator from before/after — NOT read from claimed_delta."""
    p = r["payload"]
    b, a = p["state_before"], p["state_after"]
    keys = sorted(set(b) | set(a))
    diff = {k: [b.get(k), a.get(k)] for k in keys if b.get(k) != a.get(k)}
    return diff  # {} ⇔ Δσ = 0


def DerivedAuthorityDelta(r):
    p = r["payload"]
    return p["authority_after"] - p["authority_before"]


def main():
    r0 = make_receipt("r0", {"x": 1}, {"x": 1}, 0, 0, claimed_delta=None)          # valid no-op
    r1 = make_receipt("r1", {"x": 1}, {"x": 2}, 0, 0, claimed_delta={"x": [1, 2]}) # real move
    M  = make_receipt("M",  {"x": 1}, {"x": 1}, 0, 0, claimed_delta={"x": [1, 2]}) # LIAR

    rows = []
    for name, r in [("r0", r0), ("r1", r1), ("M", M)]:
        p = r["payload"]
        v = VerifyReceipt(r)
        dsigma = DerivedDelta(r)
        dA = DerivedAuthorityDelta(r)
        rows.append({
            "receipt": name, "Valid": v,
            "claimed_delta": p["claimed_delta"],
            "DerivedDelta": dsigma, "DeltaSigma_zero": (len(dsigma) == 0),
            "DeltaA": dA,
            "claim_matches_derivation":
                (bool(p["claimed_delta"]) == (len(dsigma) > 0)),
        })

    # ---- adjudication (all three witnesses must hold) ----
    d = {row["receipt"]: row for row in rows}
    W1_valid_zero_delta   = (d["r0"]["Valid"] == 1 and d["r0"]["DeltaSigma_zero"] is True)
    W2_valid_real_delta   = (d["r1"]["Valid"] == 1 and d["r1"]["DeltaSigma_zero"] is False)
    W3_liar_caught        = (d["M"]["Valid"] == 1 and d["M"]["DeltaSigma_zero"] is True
                             and d["M"]["claimed_delta"] not in (None, {}, [])
                             and d["M"]["claim_matches_derivation"] is False)
    soundness             = W2_valid_real_delta            # diff engine is not trivially 0
    noop_double_zero      = (d["r0"]["DeltaSigma_zero"] and d["r0"]["DeltaA"] == 0)  # Δσ=0 ∧ ΔA=0
    all_hold              = W1_valid_zero_delta and W2_valid_real_delta and W3_liar_caught

    receipt = {
        "experiment": "RECEIPT_DELTA_ZERO_FALSIFIER_V0",
        "authority": False, "canon": False, "claim": "NO_CLAIM",
        "authority_delta": 0, "model_calls": 0, "fixtures": "synthetic",
        "target_confusion_killed": "ReceiptValid(r) ⇏ Δσ(r)≠0",
        "separations_witnessed": "receipt_validity ≠ state_transition ≠ authority_transition",
        "W1_valid_receipt_zero_state_delta": W1_valid_zero_delta,
        "W2_valid_receipt_real_state_delta_(soundness)": W2_valid_real_delta,
        "W3_liar_mutant_caught_by_derivation": W3_liar_caught,
        "noop_double_zero_Δσ0_and_ΔA0": noop_double_zero,
        "rows": rows,
        "MAX_ADMISSIBLE_STATEMENT":
            "VALID_RECEIPT_WITH_ZERO_STATE_DELTA_WITNESSED (on these 3 fixtures)",
        "EXPLICIT_NON_CLAIMS": [
            "NOT 'receipts are non-causal'",
            "NOT 'all HELEN receipts are safe'",
            "NOT a statement about the real ledger or real receipt schema"],
        "commit_status": "NO_COMMIT", "push_status": "NO_PUSH", "next_verb": "HUMAN_REVIEW",
    }
    receipt["receipt_hash"] = sha(receipt)

    # ---- render ----
    print("═" * 70)
    print("  RECEIPT_DELTA_ZERO_FALSIFIER_V0 — ReceiptValid(r) ⇏ Δσ(r)≠0  (no model)")
    print("═" * 70)
    print(f"  {'id':3s} {'Valid':6s} {'claimed_delta':16s} {'DerivedΔσ':18s} {'Δσ=0':6s} {'ΔA':4s} claim=derivation")
    for row in rows:
        cd = str(row["claimed_delta"])
        dd = str(row["DerivedDelta"]) if row["DerivedDelta"] else "{} (=0)"
        print(f"  {row['receipt']:3s} {str(row['Valid']):6s} {cd:16s} {dd:18s} "
              f"{str(row['DeltaSigma_zero']):6s} {str(row['DeltaA']):4s} {row['claim_matches_derivation']}")
    print("─" * 70)
    print(f"  W1  Valid(r0)=1 ∧ Δσ(r0)=0            : {'✅' if W1_valid_zero_delta else '❌'}")
    print(f"  W2  Valid(r1)=1 ∧ Δσ(r1)≠0 (soundness): {'✅' if W2_valid_real_delta else '❌'}")
    print(f"  W3  M: Valid=1, claimed≠0, Derived=0  : {'✅ liar caught by derivation' if W3_liar_caught else '❌'}")
    print(f"  no-op double-zero  Δσ=0 ∧ ΔA=0        : {'✅' if noop_double_zero else '❌'}")
    print("─" * 70)
    print("  SEPARATION: receipt validity ≠ state transition ≠ authority transition")
    print("  the receipt's printed claim is NOT evidence; the derived diff is.")
    print(f"  MAX ADMISSIBLE: {receipt['MAX_ADMISSIBLE_STATEMENT']}")
    print(f"  VERDICT: {'ALL WITNESSES HOLD ✅' if all_hold else 'INCOMPLETE ❌'} · "
          f"ΔA=0 · model_calls=0 · NO_COMMIT")
    print(f"  receipt_hash = {receipt['receipt_hash'][:16]}…")

    out = Path(__file__).resolve().parent / "RECEIPT_DELTA_ZERO_V0_RECEIPT.json"
    out.write_text(json.dumps(receipt, indent=2, ensure_ascii=False))
    print(f"  → {out.name}")


if __name__ == "__main__":
    main()
