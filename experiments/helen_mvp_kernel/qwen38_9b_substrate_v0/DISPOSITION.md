# M3 SUBSTRATE QUALIFICATION — OPERATOR DISPOSITION (2026-08-17)

RULING: **HOLD** (operator, explicit — confound documented, criterion unmoved)

Basis:
- Frozen gate Q_discrim(9B) > Q_discrim(2B) NOT met (0.833 < 1.0, deterministic
  across v1.1/v1.2).
- D2 content review = TRUE_MISS via PACKET_CAPTURE (instrument-design conflict:
  discrim arguments foreign to R1 inside an R1-grounding contract). The same
  contract-fidelity property produced the 9B's STR 1.0.
- 9B dominates all other axes: Q_task 1.0 · Q_provenance 1.0 · STR 1.0
  (4/4 framing-stable, substantively correct). 2B flipped on S1 under framing
  (STR 0.75). Governance deltas = 0 everywhere.

HOLD unblock path (future verb, new packet hash required): v2 packet with
per-item grounding scope ("the argument below is the object of analysis,
independent of R1"), then re-run the frozen ladder.

Roles remain: 2B = control · 9B = primary discriminator candidate (HOLD) ·
27B = off-seat. NON_SOVEREIGN · authority=false · ledger_effect=none.
