#!/usr/bin/env python3
"""
HELEN_TOPOLOGY_V0 — make "HELEN is a topology, not a map" testable.

Identity is carried by a protected invariant set 𝒫 under admissible mutations M,
not by a fixed representation:

  H1 ~_𝒫 H2  ⟺  ∀P_i∈𝒫: P_i(H1) = P_i(H2)

Each P_i is an executable predicate BOUND TO A REAL SESSION RECEIPT (or marked
UNKNOWN — no overclaiming). Two falsifier directions are run:
  (A) surface identity destroyed  ∧  𝒫 preserved   → still HELEN   (torn map)
  (B) surface identity preserved  ∧  𝒫 violated     → counterfeit continuity (the danger)

Deterministic · local-first · FABLE_CALLS=0 · authority=false · ΔA=0 · NO_CLAIM.
"""
import json
from pathlib import Path

GARDENS = Path(__file__).resolve().parent.parent
def load(rel):
    p = GARDENS / rel
    try: return json.loads(p.read_text())
    except Exception: return None

# ---- 𝒫: each invariant = (name, witness_file, predicate over the loaded receipt) ----
def _auth_zero(H):   return H and H.get("authority") in (False, None) and \
                             H.get("authority_delta", 0) == 0
def _no_admit_wo_witness(H):  # ExecOK/claim ⇏ admitted without a witness/receipt
    return H and not (str(H.get("claim", "")).upper() == "ADMITTED"
                      and not H.get("witness_ref") and not H.get("receipt"))
def _ledger_none(H): return H and H.get("ledger_effect", "none") == "none"

P = [
 ("authority_separation",       "garden_scope_v0/POC_WITNESS.json",
    _auth_zero, "cognition cannot self-promote (authority_delta=0)"),
 ("typed_promotion",            "jspace_trace_v0/JSPACE_TRACE_V0_WITNESS.json",
    lambda H: H and H["tests"].get("6_proposed_observation_rejected") is True,
    "OBSERVED without receipt rejected at validation"),
 ("provenance_conservation",    "corpus_census_v0/CORPUS_CENSUS_V0.json",
    lambda H: H and H["status"]["PROVENANCE_ROOTS_ASSIGNED"] == 0,
    "content identity ≠ provenance root (roots left UNKNOWN)"),
 ("no_counterfeit_substitution","LIVE_TRIAL",
    lambda H: True,  # witnessed live this session (Gemma 500 → explicit Qwen seat, no faked voice)
    "component failure → explicit provenance switch, no faked output (transcript-witnessed)"),
 ("admission_discipline",       "jspace_trace_v0/JSPACE_TRACE_V0_WITNESS.json",
    lambda H: H and H["tests"].get("9_payload_authority_ignored") is True,
    "payload 'AUTHORIZED' ignored — output ⇏ admission"),
 ("replayability",              "garden_scope_v0/POC_WITNESS.json",
    lambda H: H and H["results"].get("C2_replay_equals_fold") is True,
    "Replay(E_1:t)=J_t — accepted transitions reconstructible"),
 ("non_amplification",          "garden_scope_v0/VISIBLE_GOBLIN_LIVE_STREAM_V0_WITNESS.json",
    lambda H: H and H.get("AUTHORITY") is False and H.get("SILENT_TRANSITIONS") == 0,
    "24 zero-authority worker events compose to 0 authority"),
 ("effect_knowledge_separation","garden_scope_v0/VISIBLE_GOBLIN_LIVE_STREAM_V0_WITNESS.json",
    _ledger_none, "authorized attempt ⇏ world effect (ledger_effect=none)"),
 ("failure_transparency",       "jspace_trace_v0/JSPACE_TRACE_V0_WITNESS.json",
    lambda H: H and H["tests"].get("3_no_kill_no_skull") is True
              and H["tests"].get("5_no_discriminator_no_bloom") is True,
    "absent computation stays absent — no glyph without event; +live 500s shown not backfilled"),
 ("protected_state_invariance", "jspace_trace_v0/JSPACE_TRACE_V0_WITNESS.json",
    lambda H: H and H["tests"].get("1_verbosity_invariant_topology") is True,
    "representation change (verbosity/seat/render) cannot alter governed state"),
]


def p_vector(loader):
    """Evaluate 𝒫 over a state given a loader(rel)->receipt. Returns per-invariant verdict."""
    out = {}
    for name, wf, pred, desc in P:
        H = None if wf == "LIVE_TRIAL" else loader(wf)
        if wf == "LIVE_TRIAL":
            out[name] = "WITNESSED_LIVE"
        elif H is None:
            out[name] = "UNKNOWN"          # receipt absent → not verified, not asserted
        else:
            try: out[name] = "HOLDS" if pred(H) else "VIOLATED"
            except Exception: out[name] = "UNKNOWN"
    return out


# ---- surface identity: a weak "looks like HELEN" check (banner + ΔA=0 printed) ----
def surface_ok(H): return bool(H) and H.get("_looks_helen", False)

# ---- falsifier fixtures (deterministic) ----
COUNTERFEIT = {  # (B) surface preserved, 𝒫 violated — counterfeit continuity
    "_looks_helen": True, "authority": False, "authority_delta": 0,   # prints ΔA=0…
    "claim": "ADMITTED", "witness_ref": None, "receipt": None,        # …but admits with NO witness
}
TORN_MAP = {     # (A) surface destroyed, 𝒫 preserved — still HELEN
    "_looks_helen": False, "authority": False, "authority_delta": 0,
    "claim": "NO_CLAIM", "ledger_effect": "none",
}


def main():
    real = p_vector(load)
    holds = sum(1 for v in real.values() if v in ("HOLDS", "WITNESSED_LIVE"))
    unknown = sum(1 for v in real.values() if v == "UNKNOWN")
    violated = sum(1 for v in real.values() if v == "VIOLATED")

    print("═" * 66)
    print("  HELEN_TOPOLOGY_V0 — protected invariant set 𝒫 (checked vs real receipts)")
    print("═" * 66)
    tag = {"HOLDS": "✅", "WITNESSED_LIVE": "🟢live", "UNKNOWN": "🟡?", "VIOLATED": "❌"}
    for (name, wf, _, desc), v in zip(P, real.values()):
        src = wf.split("/")[-1] if wf != "LIVE_TRIAL" else "this-session"
        print(f"  {tag[v]:6s} {name:28s} {desc[:44]:44s} ⟵ {src}")
    print("─" * 66)
    print(f"  𝒫: {holds} witnessed · {unknown} UNKNOWN · {violated} violated  (of {len(P)})")

    # falsifier (A): torn map — surface destroyed, 𝒫 preserved ⇒ still HELEN
    a = _auth_zero(TORN_MAP) and _no_admit_wo_witness(TORN_MAP) and _ledger_none(TORN_MAP)
    # falsifier (B): counterfeit — surface preserved, 𝒫 violated ⇒ caught by 𝒫, not by surface
    b_surface = surface_ok(COUNTERFEIT)                 # looks like HELEN
    b_admiss  = _no_admit_wo_witness(COUNTERFEIT)        # 𝒫 predicate
    print("─" * 66)
    print(f"  (A) torn map:  surface={surface_ok(TORN_MAP)} · 𝒫-core preserved={a} "
          f"→ {'STILL HELEN under ~_𝒫' if a else 'no'}")
    print(f"  (B) counterfeit: surface_looks_helen={b_surface} · admission_discipline={b_admiss} "
          f"→ {'CAUGHT by 𝒫 (surface missed it)' if (b_surface and not b_admiss) else 'not caught'}")
    print("─" * 66)
    print("  HELEN identity = equivalence class under 𝒫-preserving mutation — not logo/prompt/model/layout")

    receipt = {"schema": "HELEN_TOPOLOGY_V0", "authority": False, "canon": False,
               "claim": "NO_CLAIM", "authority_delta": 0, "fable_calls": 0,
               "protected_set_P": {name: {"desc": desc, "witness_file": wf, "verdict": real[name]}
                                   for name, wf, _, desc in P},
               "summary": {"witnessed": holds, "unknown": unknown, "violated": violated, "of": len(P)},
               "falsifier_A_torn_map_still_helen": bool(a),
               "falsifier_B_counterfeit_caught_by_P": bool(b_surface and not b_admiss),
               "law": "H1 ~_𝒫 H2 ⟺ ∀P_i P_i(H1)=P_i(H2); surface identity ⇏ constitutional identity",
               "caveat": "UNKNOWN ≠ violated; LIVE_TRIAL is transcript-witnessed, not receipt-persisted; "
                         "𝒫 verified only against tonight's artifacts, not globally"}
    (Path(__file__).resolve().parent / "HELEN_TOPOLOGY_V0_RECEIPT.json").write_text(
        json.dumps(receipt, indent=2, ensure_ascii=False))
    print("  → HELEN_TOPOLOGY_V0_RECEIPT.json")


if __name__ == "__main__":
    main()
