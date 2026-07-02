# HELEN Loop Taxonomy

Reference doc, not doctrine — maps the 3-loop / loop-anatomy framework
onto HELEN's actual architecture, with the gaps named plainly.

## The three timescale loops, mapped

| Loop | Timescale | Generic shape | HELEN's actual instance |
|---|---|---|---|
| **1. Agentic** | minutes | agent writes, tests, iterates against spec+evals, no human | A single skill's inner cycle — one math-garden epoch (hypothesis → construct → deterministic proof hash → verdict), one `/code-review` pass, one `/goal`-bounded session |
| **2. Developer feedback** | hours | human reviews output, steers, translates vision→spec | **This entire session.** Every "gO patch" / "run 80 more epochs" / model-routing amendment is this loop, turn by turn. `.claude/commands/*.md` files ARE the accumulated spec this loop produces. |
| **3. External feedback** | days | alpha testers, friends, production A/B — real usage feeding back into vision | **Does not exist.** Zero live daemons found, zero non-operator users found, 940 PROPOSED artifacts against 1 `canon: true` file (steelman audit, this session). This isn't a diagram gap — it's the same finding under a name. |

Loop 1 is running hot (80-epoch math garden, compost swarms — pure
agentic velocity). Loop 2 is dense and working (this conversation).
**Loop 3 is the one that's actually missing, and no amount of Loop 1/2
intensity substitutes for it** — a faster inner loop just produces more
unvalidated output, faster, which is exactly the rigor-theater pattern
the steelman audit already confirmed.

## Anatomy of a loop, mapped onto HELEN's existing 5-stage progression

The generic shape (Trigger → Action → Proof → Memory → Stop) is
already HELEN's Continual Learning Bench progression
(`instructions.md`: FAIL → INVESTIGATE → VERIFY → DISTILL → CONSULT),
plus one thing that progression leaves implicit: **named STOP states.**

| Node | HELEN instance |
|---|---|
| Trigger | almost entirely operator-initiated (`gO patch`, a pasted directive) — the `governance-watch` and `pr-watch` `/loop` patterns are the only scheduled/external triggers that exist, and both watch internal state, not external signal |
| Action | the skill runs — `/code-review`, `/math-garden`, a tranche epoch |
| Proof | `/verify`, HAL-gate, a REFUTED/CONFIRMED verdict, a deterministic proof hash |
| Memory | `.claude/STATE.md`, the skill file itself, a tranche receipt |
| **Stop (named states)** | tranche sealed · REFUTED → halt pipeline · operator-gated (K-tau needle, 17 days) · PULL-mode halt · **revert — quality got worse** ← this state doesn't exist anywhere in HELEN yet |

## The PM Loop Engineering Cycle — the one precise gap

Change Artifact → Run Agent → **Evaluate Output → Keep or Revert** →
Commit Learning → Better Version Next.

HELEN's current Memory Protocol only implements the outer ring:
change the skill, run it, commit the lesson. It has no step 3/4 — no
explicit "is the new version actually better than the last one, and
if not, revert." Every skill distillation this session (12 files
created, several amended by workflow) went straight from "change" to
"commit" with no comparison gate in between. That's not hypothetical —
it's what actually happened.

Fixed directly in `instructions.md` (see diff): the Memory Protocol
now has an explicit Evaluate + Keep/Revert step between distillation
and commit.

## What NOT to build from this

The "Weekly Product Signal Loop" diagram (gather evidence → cluster
themes → compare to last week → draft memo) is the right shape for
closing the Loop 3 gap — but building it now, with zero external
signal sources, would produce a beautiful memo pipeline processing
nothing. That's the rigor-theater failure mode with a weekly cadence
attached. **The smallest real next step is not a skill — it's getting
one external touchpoint** (one non-operator person using one surface:
the Telegram bot, or `helen_simple_ui.py` at localhost:5001) before
any measurement infrastructure gets built around it. Measuring zero
signal, elaborately, is worse than not measuring.

---
authority=false · canon=false · reference doc, not doctrine
