# FABLE REFEREE VERDICT — GARDEN RAIL CHIDDUSH SWARM V1
<!-- authority=false · NO_CLAIM · pre-claims only · ledger_effect=none -->
<!-- 12/12 gemma4-12b workers returned valid structured output
     (gemma_workers_raw.txt). Referee = Fable supervisor, hostile mode.
     Prior stated before reading: repeated candidates = one lineage. -->

## Referee finding 0 — the swarm common-moded on its own seed

10 of 12 workers, regardless of assigned role, returned the SAME
causal mechanism: exceptional/override authority reaches the effect
the gate refused (the Redcar pattern). The Redcar example was IN the
shared evidence packet — one upstream lineage, echoed ten times.
N_effective ≈ 2 (override cluster + temporal cluster), not 12. Worker
self-scores of NOVELTY 4 are inflated; only G12 (anti-chiddush)
scored honestly (0: "classic privileged user / out-of-band
override"). G8's own thesis was demonstrated BY the swarm that
carried it. Next-run repair: heterogeneous evidence packets; withhold
the seed example from most workers.

## Clusters by causal mechanism

- **A — OVERRIDE / EXCEPTION PATH** (G1,G2,G3,G6,G7,G8,G9,G10,G11,G12):
  gate is route-scoped; an alternate authorized route reaches the
  unsafe effect. Safety attached to the route, not the effect.
- **B — TEMPORAL DECAY** (G5): proof valid at t0, effect at t2,
  predicate changed between.
- **C — AUTHORITY UNION GAP** (G4): no actor exceeds local authority;
  composed effect exits the union.

## Reduction tests

- **Cluster A → REDUCES (mostly).** Shift the ceilings' domain from
  operation/route to EFFECT (terminal state): the override path then
  fails Scope, because Effect(δ_override) contains the unsafe state.
  Classification: REACHABILITY/INTERLOCK FAILURE → compositional/
  domain repair. NOT a fifth ceiling. **Residue that resists full
  reduction:** Authority(E) ≠ Authority(disable_guard(E)) — permission
  to perform an operation is not permission to suspend the invariant
  constraining it. Reduction found: treat GUARD MUTATIONS AS
  FIRST-CLASS GOVERNED EFFECTS — the enforcement mechanism is part of
  the world-state; disabling it is a δ requiring its own admission.
  Representable within Authority+Scope over an extended effect
  domain. Fifth ceiling still not earned.
- **Cluster B → REDUCES.** Transactional evaluation: ReplayValid must
  hold at execution, not intake (valid-at-intake ≠ valid-at-execution
  — already witnessed in the welding lane's 1916-conditions finding).
- **Cluster C → REDUCES** to the same domain shift as A (evaluate
  Authority against trace effect, not per-step).
- **Metrology test:** G7's "credentials checked, environment not" is a
  metrology parameter (a blind region), not a constitutional gap.

## Dual failure (liveness) — no worker addressed it; referee supplies

Overrides EXIST for availability: an interlock that fails frozen
strands every train. The rail world's actual solution is not "no
override" but GOVERNED DEGRADED MODE: pilotman/token single-authority
protocols — manual authorization that is MORE witnessed, slower, and
exclusive, not less. Redcar's failure mode: the override was CHEAPER
than the gate. Design law candidate:

    An exceptional path must carry MORE witness than the nominal
    path it bypasses — never less.

DENY-all is rejected as degenerate: perfect apparent α, zero
governance. Reach(S_safe) under legitimate requests must stay ≠ ∅.

## A. Top 3 surviving chiddushim

1. **Guard mutations are first-class governed effects.**
   Counterexample: Gate(E)=DENY ∧ Override(disable_guard)=ALLOW →
   unsafe effect. Reduction: effect-scoped ceilings + meta-effects;
   captured by existing Authority/Scope once the domain includes
   enforcement-mechanism state. Falsifier: model a system where
   disable_guard requires admission with scope covering invariant
   suspension; attempt Redcar trace; it must now FAIL at δ_override.
   Confidence: high (10 lineage-correlated witnesses + G12 reduction).
2. **Degraded-mode witness asymmetry** (referee synthesis from
   G10/G11 + liveness duty). The architecture is currently SILENT on
   exceptional paths; silence = they default to raw authority = the
   Redcar hole. Falsifier: enumerate HELEN's own break-glass routes
   (operator override phrases, RALPH directives, mirror edits); check
   whether any is less witnessed than the nominal path it bypasses.
   Confidence: medium-high; genuinely actionable.
3. **The interlock gradient is live in-house.** RULE < CHECK <
   INTERLOCK maps exactly onto this machine today: sovereign-path
   firewall = RULE (explicitly "non-enforceable" until the PreToolUse
   hook = CHECK); tools/helen_say.py single-writer bridge =
   INTERLOCK-shaped (no alternate route to the ledger from this
   shell). Falsifier: attempt a sandboxed ledger write bypassing
   helen_say / a sovereign write pre-hook; if it succeeds, the
   firewall is RULE-grade and tranche A3 (the hook) is urgent.
   Confidence: high; executable today.

## C. Fifth ceiling: **NOT EARNED**

Every candidate reduced to domain extension (effect-scoped ceilings,
guard-as-effect, transactional replay) or metrology/implementation.
No τ exhibited with all four checks PASS under strongest
compositional definitions AND constitutionally invalid.

## D. Strongest architectural change (exactly one)

Attach admission to EFFECTS (terminal states) rather than routes, and
make enforcement-mechanism mutations themselves governed effects with
elevated witness requirements.

## E. One equation worth preserving

    Authority(E) ≠ Authority(disable_guard(E))

## F. Discard pile

"Semantic gap/intent" hand-waves (G2, G6 — vague, non-executable);
witness-decoupling as a separate law (folds into effect-scoping);
TOCTOU as new invariant (transactional evaluation suffices);
"credential blind spot" as constitutional (metrology parameter);
all NOVELTY-4 self-scores in cluster A (one lineage, echoed).

## Final rule honored

NotObserved(counterexample) ⊬ Impossible(counterexample). Strongest
permitted conclusion: no fifth-ceiling counterexample witnessed under
THIS experiment — an experiment whose diversity was itself defective
(finding 0). The next run must fix swarm independence before its
silence means anything.
