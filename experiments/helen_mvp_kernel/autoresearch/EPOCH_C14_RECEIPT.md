# AUTORESEARCH EPOCH C14 — RECEIPT (composition / edge witnesses)

🔵 OBSERVED · NON_SOVEREIGN · authority=0 · not admitted · no ledger effect
Loop: HELEN°FABLE supervision · operator directive "build C14" @ c94fe32

## 7-field receipt

- **carry_forward_state**: C13 gave frame-bound NODE witnesses. The relayed doctrine flagged the
  next obligation: a system summary cannot inherit the witness status of its components —
  `⋀_i P_i ⊬ P_system`. The dual-head fracture class lives on an EDGE (W_{SM,TR}), not a node;
  MASTER_SYNTHESIS_COMPLETE was refused for exactly this reason.
- **hypothesis**: composition can be made a computed verdict — a system is GREEN only if every
  critical edge carries a witness that the field transported across it matches on both endpoints;
  green nodes + one missing/false critical edge ⇒ NOT green.
- **experiment**: built helen_os/compose/edge.py — `EdgeWitness` (reusing C13's self-binding
  receipt shape), `edge_status` (WITNESSED/FALSIFIED/UNWITNESSED, derived), `system_status`
  (NodeStatus × EdgeStatus → GREEN_SCOPED/RED/UNKNOWN), and `measure_executor_tx_edge` that reads
  the REAL kernel edge. 11 falsifiers.
- **metric**: does the system verdict fall to UNKNOWN on a missing critical edge, RED on a
  falsified one, and GREEN only when nodes AND critical edges are witnessed — and does the real
  TX→Executor edge measure WITNESSED here while the machinery still detects a simulated split?
- **result — BUILT, GREEN (199→210)**:
  - edge machinery: matching endpoints → WITNESSED; mismatch → FALSIFIED (dual-head class);
    unmeasured endpoint → UNWITNESSED; tampered receipt (self-hash fails) → UNWITNESSED.
  - **core law (C14-05)**: two GREEN nodes with the critical edge ABSENT → system UNKNOWN
    (`EDGE_MISSING`), never GREEN. green nodes ⊬ green graph, as a runnable verdict.
  - falsified critical edge → RED; red node dominates → RED; unknown node → UNKNOWN;
    all nodes green + critical edge witnessed → GREEN_SCOPED.
  - **real edge, measured not asserted**: `measure_executor_tx_edge` reads SOURCE = GovernedStore
    head (TX committed head) and TARGET = `current_state_hash` (capability/executor-layer root).
    After a real prepare→execute→evidence→commit (G0→G1) both are G1 → WITNESSED (C14-10). When
    `current_state_hash` is manually left stale at G0 (a simulated dual head), the same measurement
    → FALSIFIED (C14-11). So the edge the relay named the canonical fracture is 🟢 in THIS frame
    (E009 single head / E010 sync), and C14 would catch it if it ever weren't.
  - full suite: 210 passed / 1 skipped / 2 pre-existing surface_grammar failures (CWD-glob).
- **keep/reject rule**: KEEP. Moves "system status" from a prose summary to a node×edge verdict.
  The one edge that matters most is grounded in real kernel objects, not a toy graph.
- **upgrade_path / RESIDUAL**: (1) `measure_executor_tx_edge` reads the two roots off the live
  TransactionRuntime — honest for THIS edge; generalizing to every critical edge
  (C13→HAL, HAL→Γ, Γ→κ, κ→Executor, TX→Replay) requires a measurer per edge, each with its own
  derive-at-source discipline (same residual class as C13's caller-supplied digests). (2) the
  `critical_edges` set is caller-declared — a complete system verdict needs the edge SET itself to
  be derived from the real call graph (the C11 mutation-surface / reachability problem). C14 proves
  the composition ALGEBRA and one real edge; enumerating the full critical-edge set is the next tranche.

## Fable supervision note
The doctrine relay proposed C14 (composition-witness completeness) as the layer above C13. Operator
directed the build. Fable built the algebra AND wired the marquee edge to real kernel objects, so the
dual-head class is detectable in code — confirming that in this frame the Executor/Transaction edge is
coherent (E009/E010), while refusing to let "green nodes" imply "green system." Neither admitted.
