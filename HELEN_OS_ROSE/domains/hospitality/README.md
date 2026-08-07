# Domain: Hospitality

Default privacy class: `INTERNAL_BUSINESS` (guest or property data:
`PARTNER_RESTRICTED`).

Casa Cielo, Île d'Aval, retreat and experience formats, and hospitality
operations knowledge. Casa Cielo is the internal testbed candidate for the
decision-twin pilot (Phase C of `strategy/ninety_day_plan.md`).

Rules:

- Guest-level data never leaves this domain's partition; aggregates only,
  and only per a packet's declared privacy class.
- Property ownership, residency, or family matters connected to these
  places belong to `domains/private/` rules, not here.
- Pilot instrumentation choices are recorded with receipts so results stay
  reproducible.
