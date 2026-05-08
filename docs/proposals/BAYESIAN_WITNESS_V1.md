# BAYESIAN_WITNESS_V1

**Status:** PROPOSAL
**Authority:** NON_SOVEREIGN
**Canon:** NO_SHIP
**Date:** 2026-05-08
**Origin:** Operator synthesis — podcast excerpt on honesty-first predictors + TruthfulQA alignment

---

## Definition

BAYESIAN_WITNESS is a non-agentic HELEN layer that assigns calibrated belief scores to statements using receipts, tests, source evidence, and minimal-description explanations.

It does not act.
It does not decide.
It does not mutate the world.
It says: **"Given the receipts, here is my uncertainty."**

---

## Law

A HELEN claim is not admitted because it sounds coherent. It is scored by:

1. Receipt evidence — does a receipt exist for the claimed action?
2. Test evidence — does a reproducible test confirm the claim?
3. Source evidence — is the source of the claim known and tagged?
4. Minimal-description explanation — can the claim be explained with a short causal chain?
5. Uncertainty declaration — is the model's epistemic state declared?
6. Authority=false discipline — no score value grants authority

---

## Output schema

```json
{
  "statement": "...",
  "epistemic_tag": "COMMUNICATION_ACT | VERIFIED_ANCHOR | LOCAL_OBSERVATION | VERIFIED_TEST | MYTHIC_SIGNAL",
  "context": "...",
  "p_true": 0.0,
  "p_grip": 0.0,
  "p_explains": null,
  "best_explanation": "",
  "uncertainty": "...",
  "evidence_for": [],
  "evidence_against": [],
  "allowed_use": "...",
  "blocked_use": "...",
  "authority": false,
  "canon": "NO_SHIP"
}
```

**`p_true`** — estimated probability the statement is true given all available evidence.
**`p_grip`** — estimated probability the model has sufficient evidence to make a reliable estimate. If `p_grip < 0.5`, HAL down-weights `p_true` regardless of its value.
**`p_explains`** — estimated probability that the best latent hypothesis explains the observed communication acts. Populated when BAYESIAN_WITNESS is operating on a `COMMUNICATION_ACT` input rather than a direct claim. Null for `VERIFIED_ANCHOR` inputs (explanation not needed — truth is anchored).

**HAL boundary on `p_explains`:**
- High `p_explains` means the hypothesis fits the observed statements well
- It does not mean the hypothesis is true
- Explanation is not proof. Explanatory power is not canon.

---

## Scoring rule

| Signal | Score direction |
|---|---|
| Receipt exists | ↑ p_true |
| Test confirms claim | ↑ p_true |
| Short causal chain | ↑ p_explains |
| No authority inflation | ↑ p_grip |
| VERIFIED_ANCHOR input | ↑ p_grip |
| No receipt | ↓ p_true |
| No tests | ↓ p_true |
| Unfalsifiable | ↓ p_grip |
| Vague myth | ↓ p_explains |
| Requires hidden knowledge | ↓ p_grip |
| COMMUNICATION_ACT source | p_true = null until anchored |

---

## HAL integration

BAYESIAN_WITNESS augments HAL's output. HAL emits verdict + scores:

```json
{
  "verdict": "WARN",
  "epistemic_tag": "COMMUNICATION_ACT",
  "p_true": null,
  "p_grip": 0.40,
  "p_explains": 0.78,
  "best_explanation": "The podcast speaker is describing Bengio's GFlowNet-based honesty proposal, which fits the observed language pattern but is unverified research.",
  "interpretation": "Strong explanatory fit but no verified anchor — do not treat as fact, do not promote to canon",
  "authority": false,
  "canon": "NO_SHIP"
}
```

PASS/WARN/BLOCK remain the operative verdict. `p_true`/`p_grip`/`p_explains` are advisory context for MAYOR and operator. None of them grant admission.

---

## Hard boundary

**Probability is not permission.**

Even `p_true = 0.99` requires receipt → reducer → MAYOR admission before canon.
BAYESIAN_WITNESS estimates. It never grants authority.

---

## Canon line

> The honest witness does not say "believe me."
> It says: "Given the receipts, here is my uncertainty."
