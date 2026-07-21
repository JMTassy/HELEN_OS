# WITNESSED_LOOP_GRAPH_SEAM_V0

**One narrow constitutional proof.** Not a graph compiler. Not a Village. One seam:

> A self-confirming group of agents cannot promote a claim without independent evidence.

`authority: false` · `ledger_effect: none` · `canon_effect: false` · `scope: LOCAL_NON_SOVEREIGN_PROOF`

`ADMITTABLE` is the highest positive result this artifact can reach. It never mutates canon.

## Run the proof (deterministic, dependency-free)

```bash
python3 test_seam.py          # stdlib unittest — no pytest, no network, no models
```

Expected: 9 tests OK (6 T-cases + 3 corollary checks).

## What it proves

```
many_agents_can_agree        : true
agreement_can_be_wrong       : true
shared_lineage_is_not_independence : true
independent_anchor_is_required     : true
admission_without_anchor           : impossible
```

The reducer (`seam.py::reduce_claim`) takes one claim, any number of reviews, any
number of witnesses, and an explicit `now`, and returns exactly one of:

`HOLD` · `HOLD_REOBSERVE` · `HOLD_CONFLICT` · `REJECT` · `ADMITTABLE`

**Reviews are accepted but structurally excluded from the gate.** That is the
property being proven, not an omission: `n` supportive reviews sharing the claim's
lineage never raise the verdict above `HOLD` on their own — for `n` = 10, 100, or
1,000,000.

## Files

| File | Role |
|---|---|
| `seam.py` | the anchor-cut reducer + independence/freshness predicates |
| `spec.md` | frozen shapes, result algebra, the anchor-cut theorem |
| `test_seam.py` | 6 required tests + corollary, stdlib only |
| `fixtures/t1..t6*.json` | one frozen scenario per test |
| `goblin_swarm_demo.py` | live embodiment: real LLM swarm agrees, one anchor refutes |
| `RECEIPT_TEMPLATE.json` | non-sovereign receipt shape |
| `receipt.json` | generated after a passing run |

## Live embodiment — the goblin swarm

`goblin_swarm_demo.py` makes the corollary tangible. N goblins (a local Ollama
model) each read the **same** runtime packet and confirm a false claim. Their
unanimity reduces to `HOLD`. Then one `INDEPENDENT_RUNTIME_PROBE` of the actual
serving process contradicts them → `REJECT`.

```
N goblin confirmations  <  1 independent contradiction
what I believed happened  !=  what the world reveals happened
```

## The growth sequence (deferred — do not build yet)

Anchor-cut seam → loop-graph schema → distinction planner → minimal loop selector
→ agent embodiment → Goblin Village. Each is a later layer. This artifact only
freezes the first seam so everything above can safely stand on it.

## Game translation

Lulu hears a hum and concludes "the blue engine runs." Bram reads Lulu's note and
agrees. Both are wrong — they saw the same signal. The player opens the hatch; a
separate gauge shows the red engine running. The world refuses to reward the
shared conclusion. *Two minds agreeing can still be one observation repeated twice.*
