# CAUSAL-EDGE DECISION RECORD — OPERATOR RULING (b): CAUSAL PARENTS
Date: 2026-08-16 · Ruled by: operator (JM Tassy) · NON_SOVEREIGN record

## Ruling
Receipt hash topology is CAUSAL: h(r) binds to canon(op) + sorted causal-parent
hashes. History is a DAG; any linear file is one serialization of it. The
former sequence-chained head H_{n+1}=h(H_n‖r_n) is demoted to bookkeeping —
it carries no semantic weight where confluence holds (H_n ≠ S_n).

## What this resolves
- The (H)-vs-T3 tension flagged earlier this session: T3/L4' confluence over
  linear extensions is now a REAL property of the ledger model, not vacuous.
- O4's production form: hidden-edge search over declared antichains becomes
  executable at ledger scale (E3).

## Implemented at REFERENCE level (this commit scope)
- causal_ledger/causal_receipt_v0.py — CausalLedger: parent-bound hashes,
  verify, incomparable-pair enumeration, seeded random linearizations.
  Acyclicity by construction (only existing hashes referenceable).
- falsifiers/antichain_probe.py — run 2026-08-16 vs real BoundedExecutor:
    WELL_FORMED (true parents declared): 8 linearizations, 1 outcome
      -> CONFLUENT — first T3 witness on a causal ledger + real kernel.
    BROKEN (EDIT/EDIT dependency omitted): 8 linearizations, 2 outcomes
      -> 💥 HIDDEN EDGE; proposed exactly MissingEdge(EDIT,EDIT on h.txt).
      Proposal only — diagnostic ⊬ DAGMutation, witnessed.

## Explicitly NOT done (firewalled — MAYOR-routed)
The production ledger (town/ledger_v1.ndjson), its writers (tools/helen_say.py
→ tools/ndjson_writer.py) and helen_os/schemas/** are untouched. Adopting
CAUSAL_RECEIPT_V1 in the sovereign spine requires a schema + writer change
routed through HELEN's own machinery (operator → MAYOR), not this shell.
This record is the input to that routing, not a substitute for it.

authority=false · canon=false · ledger_effect=none
