# SENTINEL_LOOP_V0 — iterative-deepening corpus loop (cumulative, falsification-gated)
authority=false · canon=false · ledger_effect=none · NON-SOVEREIGN. A harness, not a corpus reader.

**It does not read the Drive.** It is a corpus-agnostic STATE MACHINE + PROMOTION GATE. The Drive-connected
side (HER-GPT / claude.ai with connectors) does MAP/READ/EXTRACT and feeds this loop claim-atoms; this governs
accumulation, novelty, and promotion so the loop is cumulative and cannot promote hallucinated structure.

Loop: `MAP → READ → EXTRACT → LINK → FALSIFY → EXPAND → COMPRESS → STATE` (state persists between rounds).

## Plug-in (Drive side, per round)
```python
from sentinel_loop import SentinelState, ClaimAtom, Falsification
st = SentinelState()                       # or restore from a prior campaign
# 1. your reader extracts claim-atoms (with provenance + independent root_id) from the files it read:
st.ingest_round(read_files=[...], partial_files=[...],
                new_claims=[ClaimAtom(claim, source, date, entity, evidence_class, root_id), ...],
                new_contradictions=[(a,b,note), ...], new_open_witnesses=[...], new_relations=[...],
                queries=[...], docs_read=N)
# 2. for each interesting hypothesis, run a contra-search and record the result:
st.falsify("H", Falsification("H", attempted=True, refuting_witness="" or "counterexample text"))
# 3. recompute promotions + decide whether to continue:
st.derive({"H": [claims_for_H, ...]})
cont, why = st.should_continue(coverage=<0..1>, target=0.9, budget_remaining=True)
report = st.report()                       # emit ONLY when the frontier advanced
```

## The gates (why it can't be gamed — see test_sentinel_loop.py, 12 green)
- **provenance**: `evidence_class ∈ {OBSERVED,REPORTED,INFERRED,PROPOSAL,UNKNOWN}`; no source / UNKNOWN ⇒ NOT_KNOWLEDGE, contributes 0 to novelty.
- **fan-out law**: a PATTERN needs ≥2 **independent roots** (`root_id`), not ≥2 docs — N docs from one root = one root.
- **falsification**: a CHIDDUSH needs a PATTERN **and** a falsification that was *attempted* and *survived*; a refuted pattern is demoted.
- **novelty gate is INSIDE the count** — hallucinated/provenance-less claims cannot inflate `Novelty_n`.
- **stop**: `novelty < ε` for K consecutive rounds ⇒ HOLD (knowing we can't discriminate), or coverage/budget.

## Provenance & scope
Client corpus (UZIK/Calvi/NEPTION/Agentics) stays LOCAL — never pushed. This harness is generic; the corpus
is not in it. `1 source→observation · n independent→pattern · +survived falsification→chiddush`.
