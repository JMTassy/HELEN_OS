# The J1→J7 depth model

Research depth is a ladder of STRUCTURE, not of effort. Each level
names the kind of object that must newly exist for the level to be
earned. Reading more documents changes no level.

## The levels

| level | name | the object that earns it |
|---|---|---|
| J1 | Census | a source inventory with access states + a timeline skeleton |
| J2 | Relations | verified email↔file↔attachment links (exact IDs from message bodies beat title-search inference) |
| J3 | Decisions & methods | a reconstructed decision with its decision-time variables, or a candidate method with its predictors |
| J4 | Failures & counterexamples | a compiled C/D/U failure, a counterexample, or a NEGATIVE CONTROL (predictors present, effect absent, method survived/died scored) |
| J5 | Independent roots | a provenance finding: artifact families collapsed to roots, a copy exposed as non-independent, or a genuinely new root |
| J6 | Campaign reconstruction | an end-to-end institutional arc: Brief → Recommendation → Decision → Production → Deployment → Outcome, with role edges at each hop |
| J7 | Adversarial synthesis | a prior interpretation actively attacked and BOUNDED: a revised claim narrower than the old one, carrying the counterexample that forced the revision |

## The earning rule

    J(n+1) is earned only through NEW structure.

A genuine advancement requires at least one new: relation, decision,
contradiction, independent provenance root, counterexample, campaign
reconstruction, or falsification — that did not exist in the prior
package. The receipt must NAME the earning witness ("J4 earned by
negative control NC-3: relance cadence present, no unblock"). If no
new structure emerged, `DEPTH_LEVEL_EARNED` stays at the prior level
and the run is still a success — a clean census that earns only J1
outranks an asserted J7.

## Level discipline

- Levels are cumulative: J4 work stands on a J1 census and J2/J3
  structures for the same TARGET; do not parachute into J6 with no
  timeline underneath.
- At J4 and above, every candidate method must be hunted for the
  case where its predictors were present and the expected effect
  absent. An unscored negative control reinforces nothing.
- J7 is adversarial BY CONSTRUCTION: it starts from an existing
  interpretation and searches for what happened afterward, for the
  disconfirming thread, for the survival of the thing declared dead.
  Its typical product is a bound: "X causes friction and temporary
  blocking risk — NOT terminal loss."
- Confirmations accumulate and never reinforce. Reinforcement is
  bought only where the method could have died and did not.

## Anti-inflation

`DEPTH_LEVEL_TARGET` comes from the contract; `DEPTH_LEVEL_EARNED`
comes from the witness. They are independent fields and routinely
differ. Asserting J7 without a bounding witness is the depth
equivalent of an untyped amount — the validator refuses it.
