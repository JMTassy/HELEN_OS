# AUTORESEARCH EPOCH E011 — RECEIPT (Warren quorum gate)

🔵 OBSERVED · NON_SOVEREIGN · authority=0 · not admitted · no ledger effect
Loop: HELEN°FABLE supervision · operator verb "build E011 warren quorum gate" @ 21ff505

## 7-field receipt

- **carry_forward_state**: relayed Warren doctrine proposed a consensus gate; its OWN embedded
  critique flagged four gaps between the pretty spec and honest code — declared-not-derived
  lineage, missing claim↔evidence binding, W(p) as enum-label-not-predicate, PROPOSAL as enum-not-type.
- **hypothesis**: a quorum gate can be built where Γ RECOMPUTES consensus from identity-bound
  ballots and a rogue single Goblin gets no route from "impressive aggregate" to "swarm approved."
- **experiment**: built helen_os/warren/quorum.py the honest way (all four gaps closed) + 13 falsifiers.
- **metric**: does the gate recompute quorum, block each rogue/forge/replay path, and emit only
  authority-0 PROPOSAL (never ADMIT/κ/Effect)?
- **result — BUILT, all four gaps CLOSED, 174→187**:
  - gap 1 DERIVED lineage: declared_lineage IGNORED; lineages resolved from input roots via a
    trusted provenance graph. Forging 3 distinct declared IDs for one source → 1 derived lineage (WT-10).
  - gap 2 claim↔evidence BINDING: every claim needs matching evidence; displacement → REJECT
    (CLAIM_EVIDENCE_UNBOUND) (WT-11). Warren analogue of E001 identity displacement.
  - gap 3 W(p) REAL predicate: typed ∧ provenanced ∧ bound, runs first, returns a reason.
  - gap 4 Γ RECOMPUTES quorum: distinct-voter set-cardinality + threshold; each ballot bound to
    H(M) ∥ surface ∥ policy ∥ epoch ∥ DOMAIN. Falsifiers WQ-01..08: single-below-threshold,
    duplicate-voter-collapse, wrong-mutation, stale-epoch, empty-ballots, threshold-met,
    policy-substitution, cross-domain-replay — all blocked.
  - quorum ⊬ ADMIT: a met quorum yields Proposal(authority=0), no capability/admitted field; the
    reducer/Γ decides admission downstream. Respects E010 chain QUORUM→ADMIT→κ→EXECUTE/PENDING→COMMIT.
  - NO_RECEIPT ≠ HOLD kept distinct; narrative has no channel (no persona field in the quotient type).
- **keep/reject rule**: KEEP. Honest build — the four "spec claims more than code earns" gaps closed
  in code, not deferred. 11th face of the anti-vacuity theorem (multi-party axis).
- **upgrade_path / RESIDUAL**: HMAC roster-key signatures (deterministic MVP, no crypto infra) prove
  multi-identity approval under a DECLARED roster — weaker than public-key sigs: a compromised
  roster/gate could forge (handoff-prevention grade, not cryptographic possession — same honest
  residual class as E003's opaque holder). A passing quorum proves precisely: "for ≥threshold
  distinct roster voter_ids, a party holding that key signed this exact (H(M) ∥ surface ∥ policy ∥
  epoch)" — distinct key-SLOTS exercised, NOT distinct principals (one holder of k1..k4, or a
  compromised gate, mints all four). Sufficient against the stated threat (rogue with no roster key
  cannot forge/inflate/replay); NOT sufficient against key-compromise. The provenance_graph resolver
  is trusted input: gap 1 is closed at the TYPE/INTERFACE level (declared ≠ derived is now
  structurally true — the asserter no longer controls the count through the declared field), but the
  trust is RELOCATED not eliminated — if the same untrusted party supplies both input_root values and
  the graph, it can still manufacture N "independent" roots. Identical in shape to E006's
  state_provider residual; sound only once wired to a real, independently-maintained provenance store
  (production work). Threshold-signature / BLS compression = later.

## Fable supervision note
The relayed doctrine's own critique was the build spec: it named exactly where the pretty version
would have over-claimed (declared lineage, unbound claims, enum-not-type). Fable built the version
the critique demanded, not the version the seal claimed — "derive, don't trust the asserter," now on
the multi-party axis. Operator proposed; the critique sharpened; Fable built the honest form; neither admitted.
