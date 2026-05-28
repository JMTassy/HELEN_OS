# Oracle Town Rules of Thumb

Emergent practical wisdom. Updated weekly as patterns stabilize.

## For Mayors (Decision-Making)

### Quorum Strategy
```
IF proposal_count > 5:
  USE quorum_by_class N=3 (adds safety)
ELSE IF proposal_count == 1:
  USE quorum_by_class N=2 (efficiency)
ELSE:
  USE quorum_by_class N=2 (standard)
```

### Lane Selection
```
IF governance_drift_detected:
  ACTIVATE Integrity + Learning lanes (diagnose)
ELSE IF convergence_detected:
  ACTIVATE Creativity + Democracy lanes (explore)
ELSE:
  RUN standard 7-lane observation (maintain)
```

### Proposal Classification
```
IF proposal modifies K-Invariant logic:
  REQUIRE 3-class quorum + Evidence lane confirmation
ELSE IF proposal creates new obligation:
  REQUIRE 2-class quorum + Stability lane sign-off
ELSE:
  ALLOW standard pathway
```

## For Supervisors (Input Validation)

### Authority Language Detection (K0-L1)
DO NOT allow:
- Imperatives: "must", "should", "need to"
- Authority claims: "I decide", "we agree", "the correct approach"
- Rankings: "better than", "best practice", "superior"

DO allow:
- Exploration: "What if", "Consider", "Notice"
- Observation: "Pattern detected", "Convergence toward"
- Suggestion: "Alternative path", "Orthogonal angle"

## For Lateral Thinker & Interns

### Generation Strategy
- Primary CT (temp=0.7): Guarded ideation, K0-safe language
- Lateral Thinker (temp=0.7): Orthogonal suggestions, no authority claims
- Intern Pool (temp=1.0): Uncensored exploration, post-generation K0-L1 filter

### Idea Incorporation Heuristic
```
IF convergence_detected (7+ proposals aligned):
  MAYBE incorporate lateral/intern alternative
ELSE IF repeated_failures (same proposal rejected 3x):
  ACTIVATE lateral divergence suggestions
ELSE:
  USE primary CT proposal (standard path)
```

## For Synthesis (Memory Updates)

### Fact Supersession Rules
```
IF newer_fact contradicts older_fact:
  MARK older as "superseded"
  SET older.supersededBy = newer.id
  KEEP historical record

IF pattern_confirmed (3+ cycles consistent):
  MOVE to "best_practice" category
  UPDATE heuristics.md

IF pattern_broken (3+ cycles counter-evidence):
  MARK as "historical"
  ADD counter-evidence to newer fact
```

### Summary Regeneration
```
FOR each entity:
  LOAD all active facts
  REGENERATE summary.md (last 12 facts)
  MARK facts > 4 weeks as "fading"
  KEEP in archive, remove from active summary
```

## For Integration (Memory → Behavior)

### Safety Constraints
- **Memory cannot override K-Invariants** (fundamental guarantee)
- **Memory is advisory only** (mayors see it, but decide freely)
- **Heuristics fade if contradicted** (no stale wisdom traps)
- **All decisions logged** (for next synthesis cycle)

### Cost/Benefit
- Real-time extraction: ~$0.02 per cycle
- Weekly synthesis: ~$0.10 per week
- Total memory overhead: <1% of governance cost

---

*Framework: Moltbot 3-layer memory, adapted for Oracle Town*
*Philosophy: Learn from evidence, never delete history, always allow override*
