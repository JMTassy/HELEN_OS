# UZIK LS — J4 PREREGISTRATION — frozen before search

authority=false · canon=false · ledger_effect=none · NO_PII · NO_FIGURES
DATE = 2026-08-14 · J3_STATUS = EARNED (operator-ratified)
J4_MODE = FAILURES + COUNTEREXAMPLES + NEGATIVE_CONTROLS

## THE LAW THIS RUN TESTS

A candidate method is REINFORCED only if it survives a case where its
predictive variables are present but its expected effect is absent.
Confirmations accumulate and never reinforce. The expected J4 gain is
not a new method — it is an estimate of WHERE the J3 methods stop
being valid. (Encoded: decision_boundaries.reinforcement.)

## PREREGISTERED TARGETS (before extraction, per corpus law)

Each target names its method, its predicted evidence, and — the J4
addition — the NEGATIVE that would bound the method.

1. GOOGLE DMT — close REQUESTED -> APPROVED -> CONTRACTED ->
   INVOICED -> PAID for the 2020 envelope.
   - Method under test: budget state typing (M-04).
   - Negative control sought: a LIKELY-state amount never approved,
     or an amount that jumped states with no intermediate witness in
     the record (which would mean the state machine is imposed, not
     observed).
   - NOTE: this lane already extracted the secured-revenue
     decomposition (RUN_2026-08-14_deepdive); start from that
     receipt, do not re-buy it.

2. APPSFLYER — the final decision after the same-day HOLD.
   - Method under test: qualification gate (M-01 / CHIDDUSH-01).
   - Negative controls sought, BOTH directions: the HOLD lost a good
     opportunity (weak qualification would have won), or a
     comparable weakly-qualified brief elsewhere in the corpus that
     was pursued and SUCCEEDED. Either bounds the gate.
   - Probe: sent-mail search for the reply to the client; any later
     thread with the same counterpart.

3. CALVI — the signed contract after the December email agreement,
   terms compared to the negotiated model.
   - Method under test: commitment coupling (M-02 / D_gov).
   - Negative control sought: a dossier with high apparent D_gov and
     NO measurable friction (no escalation, no pause threat, no
     late-negotiation cost) — the case that bounds the metric.
   - PRECONDITION (blocking): C_op / C_econ observable codebook must
     be frozen and versioned BEFORE scoring any dossier
     (decision_boundaries.governance_debt refuses otherwise).

4. MANUCURIST — objective acceptance criteria comparing internal
   baseline vs external tests; the voice-AI experiments stopped for
   quality.
   - Method under test: dynamic baseline (M-03 / CHIDDUSH-03).
   - Negative control sought: an external solution KEPT against a
     strong internal baseline that turned out well — bounding
     "SWITCH on Delta V <= 0".

## DECISION SURFACE HARVEST (cross-target)

Every dossier read in J4 yields surface points
(decision in {GO, PROBE, HOLD, REJECT, STOP, SWITCH}, variables
known at decision time, evidence, outcome-or-NO_RECEIPT) via
decision_boundaries.surface_point — hindsight variables refused at
ingestion. The DECISION BOUNDARY ENGINE consumes these points and
reconstructs boundaries; it does not recommend.

## STOP CONDITIONS

- A target whose expected IG falls below epsilon after the
  structural sample STOPs (information_gain_gate).
- Figures and names stay in chat/vault; receipts in this repo carry
  states, roles and dates only.
- Read-only: no Gmail/Drive mutation, no publication, no weight
  changes.
