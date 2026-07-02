# HELEN Council — Multi-Round, Multi-Model Deliberation

Adapted from `0xNyk/council-of-high-intelligence` (18-persona multi-
provider council). Kept: the structural mechanisms — restate gate,
cross-examination, dissent enforcement, counted tie-break. Not kept:
the persona count. Their "18" is sized to their provider access
(Claude/OpenAI/Gemini/Ollama/NIM/Cursor). HELEN's real diversity
ceiling is **~6 genuinely distinct model backends** (see `ROUTING.md`)
— padding to 18 personas on 6 real models would mean most "members"
are costume changes on the same model, exactly the failure mode their
own README calls out. Roster size follows model diversity, not vanity.

## Inputs

$ARGUMENTS — the question, plus an optional mode flag: `--quick`
(default), `--full`, `--duo <role1>,<role2>`.

## Modes

| Mode | Rounds | Roster | When |
|---|---|---|---|
| `--quick` | 2 (independent → synthesis) | 5 (original mapping) | routine questions, fast |
| `--full` | 3 (independent → cross-exam → final) | 6, cross-model routed | consequential decisions |
| `--duo <a,b>` | 2 (dialectic) | 2, deliberately opposed | exploring one specific tension |

## The roster — sized to real model diversity, not a target number

| Role | HELEN persona | Backend (Full mode) | Why this backend, not just this prompt |
|---|---|---|---|
| **Opposer** | HAL | *[flagged — see Model routing]* | strict gate; needs a model that doesn't reason around rules |
| **Essential Thinker** | JESTER | `deepseek-r1:14b` | reasoning-distilled models are good at stripping to real structure — genuine fit, not arbitrary assignment |
| **Expander** | HER | `helen-gemma4-12b-32k` | HELEN-tuned, creative-role default per `ROUTING.md` |
| **Outside Perspective** | GOBLIN | `ornith-helen:overlay-v3` | deliberately a *different* backend than HER — GOBLIN's doctrine is "blind to priors," so cross-model independence matters more here than for any other role |
| **Systems Voice** *(new)* | KERNEL | `qwen3.5:9b-ud-q4` or `qwen3:14b` | second-order/whole-system consequence tracing — a genuine gap in the original 5, filled by a genuinely different model family, not a re-flavored existing one |
| **Implementer** | CLAW | deterministic, no LLM | unchanged — "EXECUTION layer should not be an LLM" was already correct |

Quick mode uses the original 5 (Opposer/Essential/Expander/Outside/
Implementer) and does not guarantee cross-model routing — it's the
fast path, and the tradeoff is stated, not hidden.

## Recipe

### 0. Problem Restate Gate (new — before any analysis)

Every member restates the question in their own words *before* seeing
each other's output. If **3 or more members restate it differently**,
say so explicitly in the final verdict, ahead of any answer: the
question itself may be the problem, not the space of answers to it.

### 1. Round 1 — independent analysis

Each member gets only: the question + their role definition + the
restated versions (not attributed to who said what, to avoid anchoring
on a specific member's framing). Blind to each other's analysis.

### 2. Round 2 — cross-examination (Full mode only)

Each member reads all Round-1 output and must do one of two things,
explicitly, for at least one other member's claim:
- **rebut** a specific claim with a specific reason, or
- **support** a specific claim with independent reasoning of their own

No member may pass this round with only "I agree with everyone" —
that's not cross-examination, it's noise with extra steps.

### 3. Dissent enforcement (new)

After cross-examination, check agreement. **If more than 70% of
members converge on the same position, two members — preferably a
polarity pair (Opposer/Expander, Outside/Implementer) — are required
to write a forced steelman of the rejected minority view**, even if
they don't believe it. Early consensus is exactly when it's cheapest
to manufacture false confidence, so this is where the check has to
bite hardest.

### 4. Round 3 — final positions (Full mode only)

Each member states their final position given Round 2. Positions may
change; a changed position must say what specifically changed it.

### 5. MAYOR phase — package, don't judge

Organize all rounds into one comparative packet. No new claims, no
elimination yet — flag contradictions explicitly, including ones that
survived cross-examination unresolved.

### 6. REDUCER phase — counted tally, not prose impression

An opinion is eliminated only if rebutted **and** left undefended.
Count it, don't eyeball it: for each contested claim, tally
support-votes vs. rebut-votes across all members (weighted 1 per
member, 0.5 per self-declared UNVERIFIED). A tie stays a tie — report
it as surviving disagreement, don't break it with a narrative flourish.
This is the fix their own project made in its most recent commit
(`68cd247`, "counted weighted tally instead of a prose impression") —
adopted here for the same reason: REDUCER's synthesis has to be
checkable, not just well-written.

## Model routing — the honest state, printed with every run

**Every local-model member call routes through `/local-dispatch`**, not
a hand-rolled dispatch — per the operational rule accepted alongside
that skill: any local mining/council/CHIDDUSH/compression task invokes
`/dispatch` unless explicitly overridden. `/local-dispatch` resolves
the model via `tools/model_registry.py resolve(<ROLE>)`, so a council
member's model comes from the same single source of truth this table
already describes, not a second hardcoded lookup living in this file.

For any `--full` run, print the actual routing table used before the
verdict — which member ran on which model, live, not assumed. This
exists specifically because of an unresolved finding from this
session: **HAL's model assignment is drifted three ways** (canonical
spec says `mistral:latest`; live code in `tools/hal_driver.py` runs
`deepseek-r1:14b` — the spec's own named-forbidden pattern; this
session's `memory.md` says `gemma4:e2b`). A council run is actually a
good forcing function for catching this kind of drift live: if HAL and
JESTER are supposed to be on different backends but the routing table
prints the same resolved model for both, that's the bug surfacing on
its own, not something you had to go looking for.

Until HAL's drift is resolved, `--full` mode uses whatever HAL is
*actually* configured to run and prints it — it does not silently pick
the "correct" one per the spec.

## Output format

Leads with what's unresolved, not with the answer — inverted from a
normal report, deliberately:

```
🏛️ COUNCIL — [QUICK | FULL | DUO]
❓ RESTATE GATE — [aligned | 3+ divergent readings: question may be the problem]
🧾 UNRESOLVED — named, not smoothed over
🚦 RECOMMENDED NEXT STEPS
───────────────────────────
⚔️ OPPOSER
🎯 ESSENTIAL
🌱 EXPANDER
👁️ OUTSIDE
🔧 IMPLEMENTER
🌐 SYSTEMS (Full mode only)
───────────────────────────
🗳️ TALLY — counted, per contested claim
🔀 ROUTING TABLE (Full mode only) — member → actual model used
```

## Constraints

- Never let the tally or synthesis paper over real, surviving
  disagreement — a tie is a reportable outcome, not a synthesis
  failure.
- "I don't know" / UNVERIFIED remains valid output for any member —
  unchanged from the original council skill.
- MAYOR and REDUCER stay separate passes — packaging ≠ verdict,
  unchanged.
- Roster size is capped by genuine model diversity, not by matching
  any external project's member count. If HELEN's local model
  inventory grows past 6 real families, the roster can grow with it —
  not before.

## Loop Engineering (Fable)

`--quick` runs inline, no subagent spawn needed. `--full` fans out as
6 parallel `agent()` calls for Round 1 (genuinely blind), a `pipeline()`
for Round 2 (each needs to see Round 1's full set), then MAYOR → REDUCER
as two more sequential calls — 6 + 6 + 2 ≈ 14 calls for a full
consequential-decision run. Reserve `--full` for decisions that
actually warrant that cost; `--quick` for everything else.
