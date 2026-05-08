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

**LATENT_HYPOTHESIS** — A natural-language hypothesis inferred to explain the pattern of communication acts and verified anchors. The model generates this as a readable candidate explanation, not a hidden vector. It is inspectable, taggable, and auditable. This is the query target: HELEN asks about factual hypotheses, not about what a person would say.

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

## HELEN law

> Language is not reality.
> Communication is evidence of expression.
> Verification is evidence of truth.
> Latent hypotheses are explanations, not canon.

A statement in language is not automatically a claim about reality. It is first a receipt of expression. Only later may it become evidence. Only after verification may it approach truth. Only after reducer admission may it approach canon.

---

## Canon line

> The witness does not see through walls.
> It says: "Given what I have observed and what has been verified, here is my best inference — and here is how much I trust that inference."
> The canon does not follow from the inference.
> The canon follows from the admission.
