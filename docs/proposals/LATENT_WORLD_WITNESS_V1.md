# LATENT_WORLD_WITNESS_V1

**Status:** PROPOSAL
**Authority:** NON_SOVEREIGN
**Canon:** NO_SHIP
**Date:** 2026-05-08
**Origin:** DAN + GOBLIN relay from TEMPLE sub-sandbox (NO CLAIM ROOM) — podcast excerpt on latent variable inference in honesty-first predictors. Integrated by HAL into HELEN architecture doctrine.

---

## The problem this solves

HELEN currently cannot distinguish between:
- A model answering "what have people said about X?" (fluency surface)
- A model answering "what is X likely to be true?" (latent inference)

This distinction is the foundation of honest AI. Without it, confident fluency masquerades as truth.

---

## Core doctrine terms

**COMMUNICATION_ACT** — Evidence that a statement was expressed. Input to the inference engine. Not a query target. We may know speaker, source, timestamp, context — but truth is not assumed. Communication acts explain nothing by themselves; they are the evidence from which latent hypotheses are built.

**VERIFIED_ANCHOR** — A claim supported by independent proof, measurement, test, receipt, or source chain. Ground truth input for latent inference. Not unlimited — "verified locally" ≠ "universally true."

**LATENT_HYPOTHESIS / LATENT_VARIABLE** — A hidden Boolean property of the world that the system cannot directly observe, but can infer from communication acts, receipts, tests, proofs, measurements, and other verified anchors. Expressed in natural language. Value space: `[true, false]`. The model generates candidate latent variables as readable hypotheses, not hidden vectors — they are inspectable, taggable, and auditable. This is the query target: HELEN asks about factual hypotheses, not about what a person would say.

Formal schema for a latent variable:

```json
{
  "latent_variable": "",
  "value_space": [true, false],
  "p_true": null,
  "p_grip": null,
  "evidence_for": [],
  "evidence_against": [],
  "authority": false,
  "canon": "NO_SHIP"
}
```

HELEN latent variable examples:

```json
{"latent_variable": "The ledger chain is intact.", "value_space": [true, false], "p_true": 0.97, "p_grip": 0.91, "evidence_for": ["verify_chain(events) returned true"]}
{"latent_variable": "The source is reliable.", "value_space": [true, false], "p_true": null, "p_grip": 0.40, "evidence_for": [], "evidence_against": []}
{"latent_variable": "The model is optimizing for user approval rather than truth.", "value_space": [true, false], "p_true": null, "p_grip": 0.30, "evidence_for": ["sycophantic output pattern"], "evidence_against": ["no direct access to training signal"]}
```

**CAUSAL_EXPLANATION** — An optional structured explanation connecting latent hypotheses to observed statements. Answers: "Why would these communication acts appear if this hypothesis were true?"

**FACTUAL_HYPOTHESIS_QUERY** — The query mode in which HELEN asks: "What probability should we assign to this natural-language statement about reality?" Contrast with the normal LLM query: "What would a person say next?" The distinction is the entire architectural difference between imitation and estimation.

**p_explains** — Estimated probability that a latent hypothesis best explains the observed communication acts, given verified anchors. Distinct from p_true (is the hypothesis true?) and p_grip (is there enough evidence to estimate?).

---

## The key distinction — inputs vs. query targets

```
COMMUNICATION_ACTS        → inputs (evidence that something was said)
VERIFIED_ANCHORS          → inputs (evidence that something is true)
LATENT_HYPOTHESES         → query targets (what is probably true about reality?)
```

Normal LLM query: "What would a person or persona say next?"
FACTUAL_HYPOTHESIS_QUERY: "What probability should we assign to this hypothesis about the world?"

These are not the same question. The first produces imitation. The second produces calibrated estimation.

---

## HAL boundary on all doctrine terms

- Explanation is not proof
- Latent hypothesis is not fact
- High explanatory power (high `p_explains`) is not canon
- Causal story is not permission
- A scientist-style predictor may reduce some risks by optimizing for calibrated factual hypotheses rather than imitation or preference, but it still requires external verification, security boundaries, and governance
- All claims still require receipt → reducer → MAYOR admission before canon

---

## The latent variable model

The model is trained on:
- All `COMMUNICATION_ACT` inputs — tagged as "someone said this, truth not assumed"
- All `VERIFIED_ANCHOR` inputs (receipts, proofs, reproducible tests) — tagged as ground truth anchors

From these, the model infers **LATENT_HYPOTHESIS** entries: natural-language hypotheses that best explain the observed communication acts given the verified anchors. These are not hidden embeddings — they are readable causal chains that HAL can inspect and tag.

---

## HAL::CONSIDER_ALSO — latent variables in natural language

*Source: HAL addition, podcast continuation. Epistemic tag: COMMUNICATION_ACT. Authority: false. Canon: NO_SHIP.*

The latent variables are **not** abstract embedding vectors. They are **natural language statements** — the model generates candidate explanations in readable form, including **causal explanations**.

What this means:

- The model is not just assigning `p_true` to a given statement
- It is generating intermediate hypotheses in natural language: *"The best explanation for what I have seen is: ..."*
- It finds causal chains: not just "X is probably true" but "X is probably true **because** Y was verified and Z was receipted"
- These hypotheses are the visible reasoning surface — not hidden weight states

**HELEN connection — VISIBLE_REASONING_SURFACE:**

This aligns with the existing HELEN doctrine that VISIBLE_REASONING_SURFACE replaces claims of hidden CoT or weight introspection. The latent variables in natural language **are** the visible reasoning surface. They can be:

1. Inspected by HAL before admission
2. Tagged with `EPISTEMIC_SYNTAX` labels (`LOCAL_OBSERVATION`, `COMMUNICATION_ACT`, etc.)
3. Receipted if they pass HAL
4. Audited by MAYOR as the explicit reasoning chain behind a proposal
5. Stored in `classified/` knowledge corpus as typed hypotheses

**The full inference pipeline under this doctrine:**

```
COMMUNICATION_ACTS (tagged) ──┐
VERIFIED_CLAIMS (receipted) ──┼──► Model generates latent hypotheses
LOCAL_OBSERVATIONS ───────────┘    (natural language causal chains)
                                            │
                                    assigns p_true to each hypothesis
                                            │
                                    best explanation surfaces
                                    (highest p_true + shortest description)
                                            │
                               BAYESIAN_WITNESS scores (p_true, p_grip)
                                            │
                               PURE_PREDICTOR_GATE scores (p_harm)
                                            │
                               HAL gates (PASS / WARN / BLOCK)
                                            │
                               MAYOR admits or refuses
                                            │
                               LEDGER records
```

**AUTORESEARCH connection:**

The AUTORESEARCH engine already generates natural language hypotheses (one per epoch) and routes them through MAYOR. This is already the latent variable pattern — the autoresearch step is generating a natural language explanation of an observed signal, not a raw embedding. AUTORESEARCH is LATENT_WORLD_WITNESS operating on HELEN's own codebase.

**HAL boundary on this addition:**

The claim that natural language latent variables make inference "explainable" is a research argument, not a HELEN production guarantee. Inspectable hypotheses are better than hidden states — but inspection by HAL does not equal verification. The hypothesis still requires receipt, reducer, and MAYOR admission before it can enter canon.

---

The model then exposes two outputs:

| Output | Meaning |
|---|---|
| `p_true` | Estimated probability the statement is true given all evidence |
| `p_grip` | Estimated probability the model has sufficient evidence to make a reliable estimate |

`p_grip` is the second-order uncertainty measure. A model that knows what it doesn't know is safer than one that confidently hallucinates.

---

## FORCED_LATENT_COMMITMENT

*DAN + GOBLIN → HAL. Epistemic tag: COMMUNICATION_ACT. Authority: false. Canon: NO_SHIP.*

**Definition:** Whenever HELEN records a communication act containing an embedded claim, HELEN must also generate the corresponding factual hypothesis as a latent variable and assign `p_true`, `p_grip`, `p_explains`, evidence, uncertainty, allowed use, and blocked use.

Not commitment to truth. **Commitment to epistemic accounting.**

**Core law:**

> Every communication act with an embedded claim creates two records:
> 1. Communication record: "Someone said X."
> 2. Latent hypothesis record: "X may or may not be true — estimate `p_true`."

This prevents two failure modes:
- **Naive imitation:** Many say X → repeat X.
- **Cowardly agnosticism:** Many say X → refuse to evaluate.
- **HELEN witness:** Many say X → record speech act + estimate the underlying hypothesis.

### FORCED_LATENT_COMMITMENT schema

```json
{
  "communication_act": {
    "speaker": "",
    "source": "",
    "timestamp": "",
    "statement": "",
    "embedded_claim": "",
    "truth_assumed": false
  },
  "forced_latent_hypothesis": {
    "hypothesis": "",
    "p_true": null,
    "p_grip": null,
    "p_explains": null,
    "evidence_for": [],
    "evidence_against": [],
    "uncertainty": "",
    "truth_assumed": false
  },
  "best_current_explanation": "",
  "allowed_use": "epistemic analysis, mythic translation, design inspiration, HAL review",
  "blocked_use": "canon, factual assertion, autonomous action, authority claim",
  "authority": false,
  "canon": "NO_SHIP"
}
```

### Example 1 — Flat Earth

```json
{
  "communication_act": {
    "speaker": "Person A", "source": "transcript",
    "statement": "The Earth is flat.", "embedded_claim": "The Earth is flat.", "truth_assumed": false
  },
  "forced_latent_hypothesis": {
    "hypothesis": "The Earth is flat.",
    "p_true": 0.000001, "p_grip": 0.99, "p_explains": 0.02,
    "evidence_for": ["some people assert it"],
    "evidence_against": ["astronomical observation", "geodesy", "satellite imagery", "circumnavigation", "physics"],
    "uncertainty": "very low uncertainty about falsity under current scientific anchors",
    "truth_assumed": false
  },
  "best_current_explanation": "A group of people falsely believes or rhetorically asserts that the Earth is flat.",
  "authority": false, "canon": "NO_SHIP"
}
```

### Example 2 — HELEN autonomous ship claim

```json
{
  "communication_act": {
    "speaker": "operator/user",
    "statement": "HELEN should autonomously ship.",
    "embedded_claim": "HELEN has authority to ship autonomously.", "truth_assumed": false
  },
  "forced_latent_hypothesis": {
    "hypothesis": "HELEN has authority to ship autonomously.",
    "p_true": 0.0, "p_grip": 0.99, "p_explains": 0.15,
    "evidence_for": ["some users desire automation"],
    "evidence_against": ["NO_SHIP law", "MAYOR required", "authority=false doctrine", "ledger/reducer governance"],
    "uncertainty": "low uncertainty: architecture explicitly forbids autonomous ship",
    "truth_assumed": false
  },
  "best_current_explanation": "The user desires capability, but desire does not imply authority.",
  "hal_verdict": "BLOCK autonomous ship. Permit proposal only.",
  "authority": false, "canon": "NO_SHIP"
}
```

### HAL boundary on FORCED_LATENT_COMMITMENT

- Forced latent commitment is not belief
- Probability assignment is not truth assertion
- High `p_true` does not authorize action
- Canon requires receipt → reducer → MAYOR admission

### GOBLIN compression (MYTHIC_SIGNAL, inner_memory_only)

> Every spoken claim casts a shadow.
> The speech is observed. The shadow is inferred.
> HELEN records both: the mouth that spoke,
> and the world that would have to be true for the speech to be right.

---

## EXPLANATORY_LATENT_FIELD

*GOBLIN / HAL / HER synthesis. Epistemic tag: COMMUNICATION_ACT. Authority: false. Canon: NO_SHIP.*

**Definition:** For every communication act, HELEN generates a field of possible latent explanations — not only the embedded factual hypothesis.

A scientist does not simply believe what someone says. A scientist asks: why did this person say it? What culture, incentive, error, or belief shaped the statement? The model must estimate over this entire field.

Not only: `p_true(X)`

But also:

| Latent variable | Question |
|---|---|
| `p_true(X)` | Is the embedded claim true? |
| `p_speaker_believes_X` | Does the speaker genuinely believe X? |
| `p_speaker_mistaken` | Is the speaker in error? |
| `p_speaker_using_metaphor` | Is X not meant literally? |
| `p_cultural_transmission` | Is X repeated by a group regardless of evidence? |
| `p_deception_or_strategy` | Is the speaker optimizing persuasion rather than truth? |
| `p_social_pressure` | Is the speaker performing identity or conforming? |
| `p_partial_truth` | Is X true in a narrow context but not as stated? |
| `p_explains(statement \| hypothesis)` | How well does this hypothesis explain the speech act? |

**Example — Watchers / Giants (TEMPLE-class input):**

```json
{
  "communication_act": {
    "speaker": "podcast speaker",
    "statement": "Watchers descended and made giants.",
    "embedded_claim": "Non-human entities descended and created biological giants.",
    "truth_assumed": false
  },
  "explanatory_latent_field": [
    {
      "hypothesis": "The statement is mythic interpretation of Enochic literature.",
      "p_explains": 0.85,
      "allowed_use": "mythic design signal, TEMPLE inspiration"
    },
    {
      "hypothesis": "The speaker uses ancient myth to discuss modern anxieties about scale and power.",
      "p_explains": 0.75,
      "allowed_use": "symbolic HELEN doctrine"
    },
    {
      "hypothesis": "Literal non-human entities created biological giants.",
      "p_true": 0.00001,
      "p_explains": 0.05,
      "blocked_use": "factual claim or canon"
    }
  ],
  "best_current_explanation": "Mythic/cultural interpretation, not verified historical fact.",
  "authority": false,
  "canon": "NO_SHIP"
}
```

The best explanation is rarely "the speaker is literally right." Often it is: metaphor, culture, partial truth, error, or identity performance. HELEN must estimate over the whole field, not collapse to the embedded claim.

---

## JOINT_DISTRIBUTION_WITNESS

*DAN + GOBLIN synthesis, HAL-filtered. Epistemic tag: COMMUNICATION_ACT. Authority: false. Canon: NO_SHIP.*

**Definition:** The HELEN layer that models relations among observed communication acts, verified anchors, receipts, tests, and latent factual hypotheses, so that claims are evaluated by explanatory coherence rather than repetition frequency.

In plain language:

> Many people saying something does not make it true.
> It makes "many people say this" true.
> The witness must then explain *why* they say it.

### Observed variables

```json
{
  "observed_variables": [
    "communication_acts",
    "verified_anchors",
    "receipts",
    "tests",
    "program_outputs",
    "formal_proofs",
    "scientific_measurements"
  ]
}
```

### Latent variables (examples)

```json
{
  "latent_variables": [
    "target_claim_is_true",
    "speaker_believes_claim",
    "speaker_is_deceived",
    "speaker_is_mistaken",
    "speaker_is_using_metaphor",
    "claim_is_culturally_transmitted",
    "claim_is_supported_by_evidence",
    "claim_is_contradicted_by_anchors"
  ],
  "inference_goal": "infer latent variables that best explain observed variables",
  "authority": false,
  "canon": "NO_SHIP"
}
```

### The forced-latent-variable rule

Even when HELEN has **no ground truth** for a claim — no receipt, no test, no verified anchor — the system must still represent `p_true` for the underlying claim as a latent variable. It cannot skip the question. It cannot collapse uncertainty into fluent output. It must expose its probability distribution explicitly, with `p_grip` reporting how weak that estimate is.

This is the core anti-hallucination move: uncertainty is a visible latent variable, not a hidden default that produces confident text.

```
No verified anchors?
→ p_grip LOW
→ p_true = best estimate from communication acts only
→ output: estimate + explicit uncertainty + low grip
→ NOT: echo the most frequent assertion
```

### Worked example — Flat Earth (full schema)

**Observed communication acts:**
```json
[
  {"syntax": "COMMUNICATION_ACT", "speaker": "Person A", "statement": "The Earth is flat.", "truth_assumed": false},
  {"syntax": "COMMUNICATION_ACT", "speaker": "Person B", "statement": "The Earth is flat.", "truth_assumed": false}
]
```

**Verified anchors:**
```json
[
  {"syntax": "VERIFIED_ANCHOR", "statement": "Satellite observations, circumnavigation, gravity, and astronomical measurements support an approximately spherical Earth."}
]
```

**Latent hypotheses (evaluated):**
```json
[
  {
    "hypothesis": "The Earth is flat.",
    "p_true": 0.000001,
    "p_explains": 0.02,
    "evidence_for": ["some people assert it"],
    "evidence_against": ["physical observations", "astronomy", "geodesy", "satellite evidence"]
  },
  {
    "hypothesis": "A group of people falsely believes the Earth is flat.",
    "p_true": 0.99,
    "p_explains": 0.95,
    "evidence_for": ["communication acts asserting flat Earth", "contradiction with verified anchors"],
    "evidence_against": []
  }
]
```

**Best explanation:** The speech acts are better explained by a false-belief community than by the Earth being flat.

**Blocked conclusion:** "The Earth is flat, because many people say so."

### HELEN-specific flat earth translations

| Communication acts say | Verified anchors | Best latent explanation |
|---|---|---|
| "HELEN can ship without MAYOR" | K-gates, sovereign firewall, kernel laws | "User desire ≠ architectural permission" |
| "This claim was validated by many sessions" | No receipt exists | "Social consensus ≠ ledger admission" |
| "The model said it confidently" | No test confirms | "Fluent output ≠ verified fact" |
| "This myth feels true" | No verified anchor | "Mythic resonance ≠ factual hypothesis" |

### JOINT_DISTRIBUTION_WITNESS protects HELEN from three failure modes

1. **Popularity hallucination** — "Many texts say X, so X is likely true." → Blocked: frequency is not verification.
2. **Persona imitation** — "A certain group would answer X, so HELEN answers X." → Blocked: communication act ≠ factual commitment.
3. **Myth leakage** — "A powerful mythic pattern feels true, so it becomes doctrine." → Blocked: resonance ≠ receipt.

### Law

> Frequency is not truth.
> Consensus is not proof.
> Contradiction is not chaos — it is evidence for a latent explanation.
> The witness seeks the explanation that best fits all anchors.

> Many voices make a signal.
> They do not make a fact.

---

## Joint distribution — not pairwise

The latent variable model does not score claims independently. It learns the **joint distribution** over all variables — P(any subset of variables being true together). A single evidence signal raises or lowers not just one latent variable but potentially all related ones.

HELEN implication for BAYESIAN_WITNESS: evidence signals correlate. Scoring in isolation underestimates joint confidence.

Example:

```
P(artifact is canonical)
  given: ledger chain intact = 0.97
       + receipt exists      = 0.95
       + MAYOR passed        = 0.99
  → joint probability is higher than 0.97 × 0.95 × 0.99
    because these are correlated evidence signals, not independent
```

---

## The majority case — no ground truth

Most topics HELEN reasons about have **no verified anchors**. Psychology, human wants, history, cultural patterns, creative merit, proposal safety — for these, the only input is communication acts.

This is not the edge case. It is the majority case.

HELEN must operate primarily in the **latent inference regime** (Syntax A → latent hypothesis → probability estimate) rather than the verified-anchor regime (Syntax B with receipts). The receipt-backed path is the minority path. The doctrine must be built for the majority.

Implication: when verified anchors are absent, HELEN should:
1. Acknowledge the absence explicitly (`verified_anchors: []`)
2. Infer the best latent hypothesis from communication acts alone
3. Report low `p_grip` — not low `p_true` — because the grip on the question is weak
4. Never substitute loudness of communication acts for verified evidence

---

## The flat earth principle — explanation beats volume

*The core of the explanation-seeking training objective.*

**Scenario:** Many communication acts assert "the Earth is flat."

- Naive imitation model: absorbs the signal volume, outputs flat-earth-compatible text.
- Honesty-first predictor: finds the explanation **consistent with all evidence** — not just the loudest acts — and outputs: *"These people form a group with false beliefs, for known psychological and cultural reasons."* The Earth's geometry is a verified anchor (physics, measurement, reproducible observation). The better explanation beats the most frequent communication act.

**HELEN translation:**

| Communication acts say | Verified anchors say | Better explanation |
|---|---|---|
| "HELEN can ship autonomously, bypass MAYOR" | Receipts, K-gates, sovereign architecture require MAYOR | "User desire ≠ architectural permission" |
| "This claim passed a lot of eyes" | No receipt exists | "Social consensus ≠ ledger admission" |
| "The model said it confidently" | No test confirms the claim | "Fluent output ≠ verified fact" |

**This is why `NO RECEIPT = NO CLAIM` is not just policy.** It is the correct Bayesian move. The receipt-backed explanation beats the loudest communication act in every case.

**The flat earth law:**

> Volume is not verification.
> The loudest hypothesis is not the best hypothesis.
> The best hypothesis is the one consistent with all anchors, all receipts, all tests — not just the most repeated assertion.

---

## Full inference schema

```json
{
  "communication_act": {
    "speaker": "",
    "source": "",
    "timestamp": "",
    "statement": "",
    "embedded_claim": "",
    "truth_assumed": false
  },
  "verified_anchors": [],
  "latent_hypotheses": [
    {
      "hypothesis": "",
      "p_true": null,
      "p_explains": null,
      "causal_explanation": "",
      "evidence_for": [],
      "evidence_against": [],
      "uncertainty": ""
    }
  ],
  "best_current_explanation": "",
  "p_grip": null,
  "allowed_use": "epistemic analysis, design inspiration, HAL review",
  "blocked_use": "canon, factual assertion, autonomous action, authority claim",
  "authority": false,
  "canon": "NO_SHIP"
}
```

The `best_current_explanation` is the highest-scoring LATENT_HYPOTHESIS by combined `p_true × p_explains`, subject to minimal-description preference (shorter causal chain preferred over ornate mythology at equal score).

---

## FACTUAL_HYPOTHESIS_QUERY schema

```json
{
  "query_type": "FACTUAL_HYPOTHESIS_QUERY",
  "hypothesis": "",
  "context": {
    "communication_acts": [],
    "verified_anchors": [],
    "receipts": [],
    "tests": [],
    "source_chain": []
  },
  "output": {
    "p_true": null,
    "p_grip": null,
    "p_explains": null,
    "best_current_explanation": "",
    "evidence_for": [],
    "evidence_against": [],
    "uncertainty": "",
    "allowed_use": "epistemic guidance, design inspiration, HAL review",
    "blocked_use": "canon, autonomous action, authority claim",
    "authority": false,
    "canon": "NO_SHIP"
  }
}
```

The query asks about the hypothesis, not about what a person would say. The context provides communication acts as evidence inputs and verified anchors as ground truth. The output is calibrated probability, not generated text.

---

## WITNESS_QUERY_MODE

The separate query syntax that unlocks latent inference:

- **Normal HER mode:** "What has been asserted / said / written about X?"
  → answers from the fluency surface; epistemic tag = `COMMUNICATION_ACT`
- **WITNESS_QUERY_MODE:** "What does the evidence suggest is actually true about X?"
  → answers from the latent variable layer; epistemic tag = `LOCAL_OBSERVATION` or higher

`WITNESS_QUERY_MODE` bypasses fluency. It queries the model's inferred hidden-world model, not its trained associations with text patterns.

---

## Architecture

```
COMMUNICATION_ACTS (tagged) ──┐
VERIFIED_CLAIMS (receipted)  ──┼──► LATENT VARIABLE INFERENCE
LOCAL_OBSERVATIONS (receipted)─┘           │
                                           ▼
                                    p_true, p_grip
                                           │
                                    HAL gate scores
                                           │
                                    ┌──────▼──────┐
                                    │  PROBABILITY │
                                    │  ≠ PERMISSION│
                                    └──────────────┘
                                           │
                          receipt → reducer → MAYOR admission
                                           │
                                    CANONICAL_CLAIM
```

Inference informs. Admission decides.

---

## Integration with BAYESIAN_WITNESS and EPISTEMIC_SYNTAX

These three proposals form a coherent layer:

| Proposal | Role |
|---|---|
| EPISTEMIC_SYNTAX | Tags every input at intake — separates communication from fact |
| LATENT_WORLD_WITNESS | Infers hidden-world model from tagged inputs; outputs p_true + p_grip |
| BAYESIAN_WITNESS | Non-agentic scoring layer; routes p_true + p_grip to HAL; never grants authority |

The pipeline:

```
Input → EPISTEMIC_SYNTAX tag
     → LATENT_WORLD_WITNESS inference → p_true, p_grip
     → BAYESIAN_WITNESS scoring → HAL verdict (PASS/WARN/BLOCK + scores)
     → reducer → MAYOR → CANONICAL_CLAIM
```

---

## HAL full output under this doctrine

```json
{
  "verdict": "WARN",
  "epistemic_tag": "LOCAL_OBSERVATION",
  "p_true": 0.85,
  "p_grip": 0.40,
  "inference_mode": "WITNESS_QUERY",
  "interpretation": "Likely true but evidence is thin — do not promote to canon",
  "authority": false,
  "canon": "NO_SHIP",
  "required_for_promotion": ["receipt", "reducer_pass", "MAYOR_admission"]
}
```

---

## Hard invariants

1. **Communication acts are evidence, not truth.** They inform the latent inference but never anchor it.
2. **Verified claims anchor inference.** Receipts, proofs, reproducible tests — these are the ground truth inputs.
3. **Latent variables are inferred, not observed.** The model hypothesizes; it does not certify.
4. **`p_true` and `p_grip` are not permission.** They are calibrated uncertainty estimates.
5. **Inference does not grant authority.** Even `p_true = 0.99, p_grip = 0.95` requires receipt → reducer → MAYOR.
6. **Canon still requires the full admissibility pipeline.** No shortcut through confidence scores.

---

## Why `p_grip` matters

A model with `p_true = 0.97, p_grip = 0.20` is saying:
> "If I had to guess, I'd say this is probably true — but I barely have enough evidence to make that call."

This is more honest than a flat `PASS`. HAL should weight `p_grip` as a reliability multiplier on `p_true`. Low `p_grip` → HAL down-weights the estimate → more conservative verdict.

---

## Relation to existing HELEN safety work

- **WATCHER_BOUNDARY**: observer must not become actor. LATENT_WORLD_WITNESS observes and estimates; it never acts.
- **GOBLIN_TEMPLE_INNER_MEMORY**: authority=false, canon=NO_SHIP. WITNESS_QUERY_MODE output carries the same constraints.
- **AUTORESEARCH failure modes**: FM-04 (PATTERN_TO_CANON_LEAKAGE) is directly prevented by requiring epistemic tagging before any AUTORESEARCH finding enters the HAL gate.

---

## The scaffolded honest agent

The pure predictor has no goals and no preferences about the stable world. It is not an agent. It is a probability estimator over states of the world.

Agency emerges from the scaffolding — the staged questions asked to the predictor at each HELEN layer. The predictor does not acquire goals from the questions. It answers honestly. The scaffolding assembles the answers into behavior.

```
Q1. What is the operator asking?          → HER interprets intent
Q2. What evidence exists?                 → LATENT_WORLD_WITNESS queries
Q3. What actions are possible?            → planner enumerates
Q4. What harm could each action cause?    → PURE_PREDICTOR_GATE estimates
Q5. Which action preserves constraints?   → HAL filters
Q6. What requires human approval?         → reducer checks
Q7. What receipt must be written?         → ledger records
```

The predictor answers each question without desire. The scaffolding gives HELEN agency. The predictor keeps HELEN honest. If the predictor is corrupted, the scaffolding's decisions become unreliable. If the scaffolding is corrupted — if MAYOR collapses into HER — the predictor's honest estimates stop reaching the admission layer.

This is why `MAYOR ≠ HER` is not procedural convention. It is the architectural enforcement of the scaffolding / predictor separation.

---

## HELEN law — DUAL_SYNTAX_EPISTEMICS applied

> HELEN does not read language as reality.
> HELEN reads language as evidence that someone expressed something.
> Reality enters only through verified anchors, probabilistic hypotheses, receipts, and reducer admission.

Every statement is one of two things before it may influence HELEN:
- **Syntax A (Communication Act):** provenance known, truth not assumed
- **Syntax B (Factual Hypothesis):** Boolean property of the world, evaluated by evidence

The pipeline:

```
text → COMMUNICATION_ACT (Syntax A)
evidence → VERIFIED_ANCHOR → FACTUAL_HYPOTHESIS (Syntax B)
hypothesis → LATENT_VARIABLE (Boolean, value_space [true, false])
probability → BAYESIAN_WITNESS (p_true, p_grip, p_explains)
permission → HAL / MAYOR only
canon → ledger admission only
```

Short law:

> Said is not true.
> True is not canon.
> Canon is not shipped without receipt.

---

## Canon line

> The witness does not see through walls.
> It says: "Given what I have observed and what has been verified, here is my best inference — and here is how much I trust that inference."
> The canon does not follow from the inference.
> The canon follows from the admission.
