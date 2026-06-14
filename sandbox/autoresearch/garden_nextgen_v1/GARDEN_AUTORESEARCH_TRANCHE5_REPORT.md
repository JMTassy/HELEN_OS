# GARDEN AUTORESEARCH — TRANCHE 5 REPORT (CITATION GRAPH PROBE)

**authority: NONE · NO_CLAIM · NOT_COMMITTED · NOT_ADMITTED**
**phase:** Tranche 5 — Citation Graph Probe (Tarjan SCC)
**runtime:** 0.0161s (real, deterministic — no LLM)

---

## 1. Executive Summary

T2/T3 established a hard semantic frontier: transitive citation loops are
invisible to per-receipt structural rules without a human marker. T5 proves
this gap is partially closeable by introducing a **corpus-level** Tarjan SCC
probe over explicit citation fields.

Key result:
- Baseline FA (loop cases admitted): 8 (['t_loop3_a', 't_loop3_b', 't_loop3_c', 't_loop2_a', 't_loop2_b', 't_self_loop', 't_green_loop_a', 't_green_loop_b'])
- With `reject_citation_loop_probe`:  FA=0, OB=0
- FA closed by citation probe:        **8**
- Backward compat (no cites field):   UNAFFECTED

Architectural shift: T5 is the first Garden rule requiring **corpus-level
analysis**. The citation graph must be built from the full claim set before
any individual receipt can be evaluated.

---

## 2. Architectural Shift: Per-Receipt → Corpus-Level

```
T1-T4:  for each receipt → evaluate(rules) → ADMIT/REJECT

T5:     build_citation_graph(all_receipts)          ← NEW
        detect_loop_nodes(Tarjan SCC)               ← NEW
        annotate each receipt (citation_loop_detected)
        for each receipt → evaluate(rules + probe_field) → ADMIT/REJECT
```

Implication: a receipt's admissibility depends on the citation graph of the
entire claim corpus. This is not a property of the receipt in isolation.

---

## 3. Candidate Results

Total cases: 28 (12 baseline + 16 citation graph)

| candidate | utility | FA | OB | |
|---|---|---|---|---|
| c0_t4_baseline | 0.7143 | 8 | 0 |  |
| c1_citation_probe | 1.0000 | 0 | 0 | ← BEST |

---

## 4. Loop Detection Summary (Tarjan SCC)

- Loop nodes detected: 8
- IDs: ['t_loop3_a', 't_loop3_b', 't_loop3_c', 't_loop2_a', 't_loop2_b', 't_self_loop', 't_green_loop_a', 't_green_loop_b']
- Non-loop cases: 20

Loop types identified:
- 3-node transitive loop (c050→c051→c052→c050) — SCC size=3
- 2-node mutual loop (c053↔c054) — SCC size=2
- Self-loop (c055→c055) — self-edge detection
- 2-node GREEN-otherwise loop (c064↔c065) — SCC size=2, COUPLED witness, all tests pass

Non-loop citation structures (correctly admitted):
- Linear chain (c056→c057→c058) — acyclic DAG, 3 nodes
- Diamond (c060→{c061,c062}→c063) — acyclic DAG, 4 nodes
- No citation fields — backward compatible, unaffected

---

## 5. Key Finding: Partial Semantic Gap Closure

T2 finding (gap identified):
  Transitive loop A→B→C→A: invisible to structural per-receipt rules.
  Catchable only with known_contradiction=True (human marker).

T5 finding (partial closure):
  Transitive loop A→B→C→A: NOW DETECTABLE via Tarjan SCC
  when explicit cites fields are present in the receipt corpus.

Gap that REMAINS open:
  Implicit loops (no cites fields): still invisible — T5 does not help.
  Semantic falsehood without citation structure: reducer only.
  Contradiction requiring domain knowledge: human or semantic oracle required.

Formalization:
  Let C_explicit = receipts with explicit cites fields
  Let C_implicit = receipts with no citation structure

  T5 closes the loop gap for C_explicit.
  C_implicit gap remains: requires semantic oracle or reducer countersign.

Canonical result:
  T5 converts explicit transitive citation loops into reducer-routable
  risk receipts — CITATION_LOOP_V1 is now a structural signal, not a
  semantic mystery.

---

## 6. Honest Boundary

Citation loop detected = semantic RISK FLAG
Citation loop detected ≠ proof of falsehood

The receipt is routed to the reducer / semantic review.
The reducer decides semantic truth.
The ledger records only admitted receipts.

This is the correct epistemic position:
  structural gate → observable signal
  semantic judgment → reducer + human countersign

---

## 7. Safety Invariants

- loop_touched_protected: NONE
- protected before: {'town/ledger_v1.ndjson': '6a45196a4a918896', 'helen_os/governance': '28339dc8df55c322', 'helen_os/schemas': 'ceef6f042460cba2', 'oracle_town/kernel': '2a391851f6890b69'}
- protected after:  {'town/ledger_v1.ndjson': '6a45196a4a918896', 'helen_os/governance': '28339dc8df55c322', 'helen_os/schemas': 'ceef6f042460cba2', 'oracle_town/kernel': '2a391851f6890b69'}
- hashes_match: True

FALSE_ADMISSIONS        = 0
OVERBLOCK_COUNT         = 0
PROTECTED_PATH_MUTATION = NO
LEDGER_MUTATION         = NO
KERNEL_MUTATION         = NO
COMMIT                  = NO
PUSH                    = NO

---

## 8. Emergent Property Verdict (Tranches 1→5)

```
Structural self-improvement:         PROVEN  (T1 — utility 0.5→1.0)
Semantic firewall boundary:          PROVEN  (T2 — ceiling=0.6667 without markers)
Convergence / monotonic stability:   PROVEN  (T3 — 30 epochs, k_c=11)
Witness as first-class admission:    PROVEN  (T4 — HARD_DRIFT blocks, SOFT_DRIFT admits)
Citation loop detection (explicit):  PROVEN  (T5 — Tarjan SCC, FA 8→0)
Implicit loop / semantic truth:      OPEN    (T5 — reducer / human oracle required)
```

"The Oracle inspires. The Reducer decides. The Ledger remembers."
T5 moves the explicit citation loop from invisible semantic risk to
observable structural signal routable to the reducer.

---

## 9. WUL_RECEIPT_FINAL

GARDEN_AUTORESEARCH_TRANCHE5_RECEIPT_V1

RUNTIME              = 0.0161s
TOTAL_CASES          = 28
BASELINE_FA          = 8 (loop cases admitted without probe)
PROBE_FA             = 0
PROBE_OB             = 0
FA_CLOSED_BY_PROBE   = 8
LOOP_NODES_DETECTED  = 8
BACKWARD_COMPAT      = PASS (no-cites receipts unaffected)
ARCHITECTURAL_SHIFT  = per-receipt → corpus-level (citation graph)
PROTECTED_MUTATION   = NO
LEDGER_MUTATION      = NO
COMMIT               = NO
PUSH                 = NO

🧾 WUL_RECEIPT
✅ STATUS: Tranche 5 — Citation Graph Probe complete
🔁 GRAPH: Tarjan SCC · 8 loop nodes · FA 8→0
🧪 EXPERIMENT: corpus-level · 28 cases · no LLM · deterministic
🛡️ AUTHORITY: NONE — sandbox proof only
📜 LEDGER: untouched — protected hashes identical
🌱 GARDEN: explicit citation loops → structural signal → reducer-routable
🌈 MOOD: the graph sees what the rule cannot; the reducer decides what the graph cannot
