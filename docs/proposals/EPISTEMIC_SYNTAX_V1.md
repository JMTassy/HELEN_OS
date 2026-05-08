# EPISTEMIC_SYNTAX_V1

**Status:** PROPOSAL
**Authority:** NON_SOVEREIGN
**Canon:** NO_SHIP
**Date:** 2026-05-08
**Origin:** Operator synthesis — podcast excerpt on training syntax (communication acts vs. verified claims)

---

## Core rule

HELEN does not ask first: "Do I like this?"
HELEN asks first: **"What kind of statement is this?"**

Every input to HELEN must be tagged by epistemic type before it can influence memory, training, or canon.

---

## DUAL_SYNTAX_EPISTEMICS

Every statement in HELEN must be encoded in one of two syntactic forms before it influences any downstream layer.

### Syntax A — Communication Act

Records that a source expressed something. Does not assume the embedded claim is true. The known-true part is only the provenance: *someone said this, here, then.*

```json
{
  "syntax": "COMMUNICATION_ACT",
  "speaker_or_author": "",
  "source_text": "",
  "venue": "",
  "timestamp": "",
  "statement": "",
  "embedded_claim": "",
  "truth_assumed": false,
  "known_true_part": "The communication act occurred, if source/provenance is verified.",
  "authority": false,
  "canon": "NO_SHIP"
}
```

Example:

```json
{
  "syntax": "COMMUNICATION_ACT",
  "speaker_or_author": "podcast speaker",
  "source_text": "transcript excerpt",
  "venue": "podcast",
  "timestamp": "2026-05-08",
  "statement": "An honesty-first predictor could support capable agents.",
  "embedded_claim": "Honesty-first training produces safe capable agents.",
  "truth_assumed": false,
  "known_true_part": "The speaker made this claim in the excerpt.",
  "authority": false,
  "canon": "NO_SHIP"
}
```

### Syntax B — Factual / Hypothesis Syntax

Encodes a candidate property of the world as a Boolean natural-language variable. May be verified, supported, uncertain, false, or latent (hypothesized but not observed directly).

```json
{
  "syntax": "FACTUAL_HYPOTHESIS",
  "hypothesis": "",
  "variable_type": "BOOLEAN_NATURAL_LANGUAGE_PROPERTY",
  "p_true": null,
  "p_grip": null,
  "p_explains": null,
  "evidence_for": [],
  "evidence_against": [],
  "verified_anchors": [],
  "communication_acts_explained": [],
  "truth_status": "hypothesized | locally_supported | verified | rejected | canon_pending",
  "authority": false,
  "canon": "NO_SHIP"
}
```

Example — locally verified test result:

```json
{
  "syntax": "FACTUAL_HYPOTHESIS",
  "hypothesis": "The HELEN kernel v0.2 hash-chain replay test passes.",
  "variable_type": "BOOLEAN_NATURAL_LANGUAGE_PROPERTY",
  "p_true": 0.98,
  "p_grip": 0.94,
  "p_explains": null,
  "evidence_for": ["pytest experiments/helen_os_v02/tests/test_replay.py returned PASSED"],
  "evidence_against": [],
  "verified_anchors": ["local terminal transcript"],
  "communication_acts_explained": [],
  "truth_status": "locally_supported",
  "authority": false,
  "canon": "NO_SHIP"
}
```

### Verified anchors — admissible inputs to Syntax B

The following categories may serve as verified anchors (ground truth inputs to factual hypothesis inference):

- Mathematical theorems (with checkable proof)
- Program outputs (with reproducible command)
- Scientific observations (with method, instrument, source)
- Receipt-backed local events (ledger-recorded, hash-verified)
- Test results (with reproducible test command and output)

Everything else is Syntax A until independently verified.

### FORCED_LATENT_COMMITMENT requirement

When tagging a `COMMUNICATION_ACT` that contains an embedded claim, EPISTEMIC_SYNTAX requires a corresponding `forced_latent_hypothesis` entry. The model is not permitted to record the speech act and stop. It must evaluate the underlying world-claim.

```
"Person A said X"     → COMMUNICATION_ACT (recorded)
                      → "X is true/false/uncertain" (forced latent hypothesis, estimated)
```

This is not commitment to truth. It is commitment to epistemic accounting.

---

### Core law — DUAL_SYNTAX_EPISTEMICS

> A communication act is known as expression.
> A factual hypothesis is evaluated as reality.
> The first is provenance. The second is probability.
> Neither is canon without admission.

**HAL boundary:**
- Communication is not truth
- Hypothesis is not proof
- Probability is not permission
- Latent variable is not canon
- Canon requires receipt, reducer, and MAYOR admission

---

## Epistemic tags

| Tag | Meaning | Allowed use |
|---|---|---|
| `COMMUNICATION_ACT` | Someone said or wrote this. Truth not assumed. | Archive only |
| `MYTHIC_SIGNAL` | Symbolic material. Design inspiration. | TEMPLE / GOBLIN / AURA only |
| `LOCAL_OBSERVATION` | Observed in local runtime. Receipt required. | HAL gate input |
| `VERIFIED_TEST` | Test result with reproducible command/output. | HAL gate input |
| `FORMAL_PROOF` | Mathematical/logical claim with checkable proof. | HAL gate input |
| `SCIENTIFIC_MEASUREMENT` | Empirical claim with method/instrument/source. | HAL gate input |
| `CANONICAL_CLAIM` | Admitted by reducer/governance into HELEN canon. | Production use |

---

## The tagging pipeline

```
raw input
    ↓
EPISTEMIC_SYNTAX tagger
    ↓
tagged artifact
    ↓
HAL gate (verdict + p_true + p_grip)
    ↓
reducer
    ↓
MAYOR admission
    ↓
CANONICAL_CLAIM (if admitted)
```

`COMMUNICATION_ACT` material never crosses into `LOCAL_OBSERVATION` or above without independent verification producing a receipt.

---

## Example — correct tagging of AUTORESEARCH finding

```json
{
  "statement": "Production ledger and v0.2 kernel use different hash-chain schemas.",
  "epistemic_tag": "LOCAL_OBSERVATION",
  "evidence": [
    "town/ledger_v1.ndjson keys: cum_hash, prev_cum_hash",
    "experiments/helen_os_v02/helen/ledger.py keys: event_hash, prev_hash"
  ],
  "truth_status": "SUPPORTED_BY_LOCAL_INSPECTION",
  "authority": false,
  "canon": "NO_SHIP"
}
```

Only MAYOR may promote this to `CANONICAL_CLAIM`.

---

## HAL output upgrade

HAL should classify epistemic status alongside PASS/WARN/BLOCK:

```json
{
  "verdict": "WARN",
  "epistemic_tag": "COMMUNICATION_ACT",
  "truth_status": "UNVERIFIED",
  "allowed_use": "MYTHIC_INSPIRATION_ONLY",
  "blocked_use": "FACTUAL_OR_CANONICAL_CLAIM",
  "authority": false,
  "canon": "NO_SHIP"
}
```

---

## Training target

For HER fine-tuning, every training example must include:

```json
{
  "epistemic_tag": "COMMUNICATION_ACT | MYTHIC_SIGNAL | LOCAL_OBSERVATION | VERIFIED_TEST | FORMAL_PROOF | SCIENTIFIC_MEASUREMENT",
  "truth_status": "unverified | supported | verified | rejected | canon_pending",
  "allowed_use": "...",
  "blocked_use": "...",
  "requires_human_approval": true,
  "authority": false,
  "canon": "NO_SHIP"
}
```

---

## Why this matters

Without EPISTEMIC_SYNTAX, fluent `COMMUNICATION_ACT` material can be mistaken for `LOCAL_OBSERVATION` or worse, `CANONICAL_CLAIM`. This is the primary vector by which HER and GOBLIN poison canon — not through malice, but through the absence of labels.

The fix is not stricter gates. The fix is earlier tagging.

---

## JOINT_DISTRIBUTION_WITNESS corollary

Contradictory communication acts are not a problem for EPISTEMIC_SYNTAX. They are data.

When many communication acts assert X and verified anchors contradict X, the correct inference is not paralysis or averaging. It is a latent hypothesis: *why do people assert X despite the contradiction?*

Candidate latent explanations for contradictory communication acts:

| Latent variable | When it applies |
|---|---|
| `speaker_is_deceived` | Speaker received false information from trusted source |
| `speaker_is_mistaken` | Speaker made a reasoning error |
| `claim_is_culturally_transmitted` | Claim persists in a community regardless of evidence |
| `speaker_is_using_metaphor` | Claim is not literal — interpreted as mythic or rhetorical |
| `claim_is_contradicted_by_anchors` | Verified anchors directly falsify the embedded claim |
| `verified_disagreement` | Both sides have verified anchors — genuine epistemic dispute |

**Forced latent variable rule (from JOINT_DISTRIBUTION_WITNESS):**

Even with no verified anchor, EPISTEMIC_SYNTAX-tagged inputs must still yield a `p_true` estimate for the underlying claim. The model is not allowed to skip the question. It must commit to a probability — weak (`p_grip` low) or strong — not to fluent imitation of the most frequent assertion.

**Law:**
> Frequency is not truth.
> Consensus is not proof.
> Many voices make a signal. They do not make a fact.

---

## Canon line

> The first act of honesty is not truth.
> The first act of honesty is labeling what kind of claim this is.
