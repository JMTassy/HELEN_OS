# History Fiber & Obligation Conservation V0

Status: PROPOSAL · NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none

## Core model

A visible state is not a sufficient institutional state. Define

`GovernedState = (visible_state, movement_fingerprint, open_obligations)`.

Two histories may have the same visible state while remaining constitutionally distinct.

## HF invariants

- **HF-001 — No orphan/stale history.** Every movement is bound to the exact pre-state hash it claims to transform.
- **HF-002 — Same visible state does not imply same governed state.** Equality of visible state cannot erase a distinct movement fingerprint.
- **HF-003 — Obligation conservation.** An obligation persists until a discharge transition carries an explicit discharge witness.
- **HF-004 — Compensation is not erasure.** A compensating transition may restore visible state but cannot delete the prior movement from history.
- **HF-005 — Projection count is not evidence count.** Multiple artifacts derived from one provenance root remain one independent root.
- **HF-006 — Reducer root conservation.** A deterministic reducer may discard duplicate representations but may not invent evidence roots: `Roots(out) ⊆ Roots(in)`.
- **HF-007 — Reducer authority non-expansion.** Reduction cannot raise authority: `max Authority(out) ≤ max Authority(in)` unless a separate admission/witness gate occurs outside the reducer.
- **HF-008 — Contradiction preservation.** An unresolved contradiction present in admitted input must survive reduction as an explicit contradiction object.
- **HF-009 — Rejection is auditable.** Malformed findings are represented as rejected findings with reason codes, not silently dropped.
- **HF-010 — Convergence does not mint independence.** Repeated workers, paraphrases, summaries, or projections over the same source root do not increase independent-root count.
- **HF-011 — Local validity does not imply global composition validity.** Individually valid movements/receipts may still violate global resource, obligation, or conservation constraints when composed.
- **HF-012 — Retroactive authority is forbidden.** An effectful movement must possess authority at its own transition time; a later receipt or lease cannot manufacture earlier permission.
- **HF-013 — State restoration is not constitutional equivalence.** Histories with equal final visible state remain distinct when fingerprints or obligations differ.
- **HF-014 — Repetition is not canonization.** Repeated summaries, projections, model outputs, or cached restatements cannot promote a claim into canonical/admitted status.
- **HF-015 — Lawful-history equivalence is stricter than final-state equivalence.** Two histories are constitutionally equivalent only when visible state, movement lineage, and open obligations are equivalent under the declared policy.

## Reducer conservation law

The reducer is a deterministic membrane between exploratory swarm output and privileged synthesis.

It minimizes representation while preserving epistemic structure:

- independent evidence roots,
- authority without promotion,
- contradiction sets,
- rejected malformed findings,
- an explicit receipt naming information discarded and structure preserved.

The reducer MUST NOT use worker count as witness count or self-reported model confidence as authority.

## Executable falsifiers

The reference tests cover:

1. equal visible state / different history,
2. obligation persistence and witnessed discharge,
3. discharge without witness,
4. retroactive authority,
5. stale pre-state,
6. duplicate workers on one root,
7. multiple independent roots without authority inflation,
8. malformed finding audit trail,
9. contradiction preservation,
10. reducer loss receipt,
11. evidence-root conservation,
12. repetition without authority gain.

No test result constitutes admission or canonization.
