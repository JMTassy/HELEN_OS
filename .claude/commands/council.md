# HELEN Council — Five-Advisor Deliberation

Adapted from the generic 5-advisor council pattern. Not five invented
personas — five roles HELEN already has, reused for their actual fit.

## Inputs

$ARGUMENTS — the question or decision to put before the council.

## The five advisors (mapped, not invented)

| # | Role | HELEN persona | Why the fit is exact, not forced |
|---|---|---|---|
| 1️⃣ | **Opposer** | **HAL** | Already the strict, rule-following gate. `MODEL_ROUTING_V1.md` names the exact failure mode a good Opposer avoids: a model that "tries to reason its way around the rules" instead of just applying them. |
| 2️⃣ | **Essential Thinker** | **JESTER** | Previously an undefined canon role (model-assigned, no doctrine). The jester's actual function — say the unsayable, cut pretense, ignore what the room wants to hear — *is* "ignore the frills, solve the real problem." This gives JESTER a job. |
| 3️⃣ | **Expander** | **HER** | Already the proposer: "creative cognition... generation diversity > strict compliance." Exact match, no adaptation needed. |
| 4️⃣ | **Outside Perspective** | **GOBLIN** | `compost-chiddush.md` already specifies GOBLIN lanes as "independent... blind to what the others surface." That blindness-to-priors *is* the outside perspective — someone who doesn't know the assumptions, by design. |
| 5️⃣ | **Implementer** | **CLAW** | Already "deterministic tool dispatcher... EXECUTION layer should not be an LLM." No cognition, no opinions, just next practical steps. Exact match. |

## Recipe

1. **Activate all five in parallel, each briefed only with the question
   and their own role** — not the other advisors' framing, not each
   other's output. This is the GOBLIN-lane discipline applied to all
   five, not just #4: cross-contamination between advisors defeats the
   point of having five distinct angles.
2. **Every advisor marks low-confidence claims UNVERIFIED or says "I
   don't know"** — this is not new for HELEN, it's the existing
   Verification Protocol (`instructions.md`) applied to opinion, not
   just code: unverified is a valid, required answer, not a failure.
3. **MAYOR phase** — package the five outputs into one comparative
   packet. MAYOR does not judge, does not eliminate, does not add
   claims — only organizes, and explicitly flags where advisors
   contradict each other. Contradiction is signal, not noise to smooth
   over at this stage.
4. **REDUCER phase, independent pass** — eliminate weak opinions and
   produce the one summary. Proposer≠validator: REDUCER must not be
   the same context that ran MAYOR's packaging, per the existing
   MAYOR-prepares/REDUCER-decides split (`CLAUDE_MAYOR_CODEX.md`).

## What "eliminate weak opinions" actually means

Not "pick a winner." An advisor's position is eliminated only if:
- another advisor directly rebuts it, **and**
- nothing in a fresh read defends it after the rebuttal

Otherwise: **surviving disagreement is reported as the finding.** False
consensus is worse than visible dissent — this follows directly from
the anti-K2 doctrine already governing this repo (convergence without
independent verification is suspect, not reassuring).

## Model routing — flagged, not resolved

`HER` and `GOBLIN`(Expander/Outside) route per `MODEL_ROUTING_V1.md`
cleanly: big/creative. `HAL`(Opposer) is where this skill must NOT
hardcode a tag: as of this writing, HAL's model assignment is drifted
across three disagreeing sources (spec says `mistral:latest`, live
code in `tools/hal_driver.py` runs `deepseek-r1:14b` — the spec's own
named forbidden pattern — and this session's `memory.md` says a third
thing, `gemma4:e2b`). Until that's resolved, this skill uses whatever
HAL is actually configured to run live, and says so in the output —
it does not silently pick one and paper over the drift.

## Output format

```
🏛️ COUNCIL — VERDICT
⚔️ OPPOSER (HAL) — attack surfaced
🎯 ESSENTIAL (JESTER) — real problem, stripped
🌱 EXPANDER (HER) — opportunity surfaced
👁️ OUTSIDE (GOBLIN) — missing obvious fact
🔧 IMPLEMENTER (CLAW) — next steps
🧾 SURVIVING DISAGREEMENT — [none | named, if any]
🚦 ONE SUMMARY
```

## Constraints

- Never let the REDUCER summary paper over real, surviving
  disagreement between advisors — say it plainly if it's there.
- "I don't know" is expected output for any advisor whose confidence
  is genuinely low, not a fallback for when you can't think of
  anything.
- MAYOR and REDUCER must be separate context/passes — packaging and
  verdict collapsing into one step is the exact violation the split
  exists to prevent.

## Loop Engineering (Fable)

Light question → run inline, five short takes plus one synthesis, no
subagent spawn needed. Consequential decision, or ultracode active →
`parallel()` the five advisors as independent agent calls (+ MAYOR +
REDUCER = 7 calls total), so blindness-to-each-other is structurally
enforced rather than just instructed.
