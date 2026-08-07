# Evidence Contract API V0 — Typed Admissible Projection Theory

**status:** PROPOSAL · HYPOTHESIZED  
**authority:** false  
**claim:** NO_CLAIM  
**canon:** false  
**ship:** NO_SHIP  
**admission:** NO_ADMISSION  
**empirical_receipt:** NO_RECEIPT  
**epochs:** 20/20 (LULU/ZACK)  
**theory:** TYPED_ADMISSIBLE_PROJECTION_THEORY  
**core_operator:** `ASSESS`  
**api_name:** EVIDENCE_CONTRACT_API  
**implementation_claim:** none  
**HOLD_FOR_OPERATOR**

## Problem

Not: “decide whether a statement is true.”

**Given** a typed claim and a finite submitted evidence package,  
**determine** the strongest warranted classification  
**without** converting attribution, absence, contradiction, or operator action into proof.

## Assessment boundary

\[
B = (r, \rho, \nu)
\]

- \(r\): one finite request  
- \(\rho\): resolver environment  
- \(\nu\): verifier family  

**Rule:** Assessment is bounded to the submitted request and evaluator environment.  
**PROVEN** is never universal certification.

## Objects

| Object | Role |
|---|---|
| Claim | `(subject, predicate, T, v)` |
| Witness | locator + verifier + observation scope (no caller polarity) |
| Provenance | authenticated report or hypothesis (not direct observation) |
| Decision | authenticated operator disposition |

## Three orthogonal output axes

| Axis | Values |
|---|---|
| EvidenceState | ABSENT · SUPPORTED · CONTRADICTED · CONFLICTED |
| EpistemicStatus | PROVEN · REPORTED · HYPOTHESIZED · null |
| OperatorDisposition | DEFERRED · REJECTED · ACTED · null |

**Invariant:** EpistemicStatus ⊥ OperatorDisposition  
Evidence topology is a third independent axis. Never flatten to one enum.

## Typing

\[
TypedValue = (T, v),\quad
T \in \{\mathrm{BOOLEAN}, \mathrm{INTEGER}, \mathrm{DECIMAL}, \mathrm{STRING}, \mathrm{TIMESTAMP}, \mathrm{ARRAY}, \mathrm{OBJECT}\}
\]

Strict type equality; **no cross-type coercion**.  
`INTEGER 1` ≠ `STRING "1"`.

## Witness admissibility

\[
\mathrm{Adm}(w,c) \iff
\mathrm{Reachable}(w) \land \mathrm{Verified}(w) \land \mathrm{Relevant}(w,c) \land \mathrm{TypeCompatible}(w,c)
\]

Separate **resolve** from **verify**:

```text
resolve_ρ(locator) → bytes
verify_ν(kind, bytes, expected) → TypedObservation ∪ Error
```

A witness contributes only after both succeed.  
Verification failure → neither support nor contradiction.

## Relevance

\[
\mathrm{scope}(c) = (\mathrm{subject}(c), \mathrm{predicate}(c))
\]

Exact scope equality only. Related ≠ relevant.

## Provenance ≠ proof

\[
\mathrm{Authenticated}(report) \not\Rightarrow \mathrm{Proven}(claim)
\]

Priority for epistemic status:

1. direct admissible support (no contradiction) → **PROVEN**  
2. else authenticated reports → **REPORTED**  
3. else authenticated hypotheses → **HYPOTHESIZED**  
4. else null  

## Polarity & evidence topology (presence, not votes)

\[
S = \{w \mid \mathrm{Adm} \land \mathrm{SUPPORT}\},\quad
N = \{w \mid \mathrm{Adm} \land \mathrm{CONTRADICTION}\}
\]

| S | N | EvidenceState |
|---|---|---|
| ∅ | ∅ | ABSENT |
| ≠∅ | ∅ | SUPPORTED |
| ∅ | ≠∅ | CONTRADICTED |
| ≠∅ | ≠∅ | CONFLICTED |

Ten supports + one contradiction → **CONFLICTED**, never SUPPORTED.

## Normalization \(N_T\)

Typed, serialization-blind, lossless (exact decimals; no binary float).  
`DECIMAL 1.000` and `DECIMAL 1` support when both decode equal under \(N_T\).

## Forbidden decorative fields

confidence, authority, importance, priority, source_reputation, weight, trust_score, explanation_style  

**Retain field iff removing it changes normative semantics.**  
Caller-submitted `verified` / `polarity` / `evidence_state` → UNKNOWN_FIELD.

## Projection theorem

\[
\Pi(r;\rho,\nu) = (S, N, A, Q, D)
\]

- \(S,N\): support / contradiction presence  
- \(A\): authenticated report presence  
- \(Q\): authenticated hypothesis presence  
- \(D\): set of decision kinds  

**Theorem:** \(\Pi_1 = \Pi_2 \Rightarrow \mathrm{ASSESS}_1 = \mathrm{ASSESS}_2\)  
Classifier consumes presence bits + distinct decision set only (counts do not matter).

## Single operator

\[
\mathrm{ASSESS} = \mathrm{classify} \circ \mathrm{project} \circ \mathrm{evaluate} \circ \mathrm{validate}
\]

All public classifications derive from ASSESS. No parallel `/prove`.

## Classification

- Evidence from \(S,N\)  
- Epistemic: SUPPORTED→PROVEN; else A→REPORTED; else Q→HYPOTHESIZED; else null  
- Disposition: \(|D|=0\) null; \(|D|=1\) unique; \(|D|>1\) HOLD_FOR_OPERATOR (set cardinality, not order)

**Invariant:** PROVEN ⇔ SUPPORTED  
**Derived:** NO_RECEIPT ⇔ outcome ≠ INVALID ∧ epistemic_status = null

## Request / response (minimal)

```json
{
  "claim": {},
  "witnesses": [],
  "provenance": [],
  "decisions": []
}
```

```json
{
  "outcome": "ASSESSED | INVALID | HOLD_FOR_OPERATOR",
  "epistemic_status": "PROVEN | REPORTED | HYPOTHESIZED | null",
  "evidence_state": "ABSENT | SUPPORTED | CONTRADICTED | CONFLICTED | null",
  "operator_disposition": "DEFERRED | REJECTED | ACTED | null"
}
```

## Error algebra

| Class | Codes (examples) | Effect |
|---|---|---|
| Fatal | MALFORMED_REQUEST, UNKNOWN_FIELD, MISSING_FIELD, INVALID_ENUM, DUPLICATE_OBJECT_KEY, UNSUPPORTED_VALUE_TYPE, LOSSY_BINDING | INVALID |
| ItemReject | UNREACHABLE, VERIFICATION_FAILED, TYPE_MISMATCH, IRRELEVANT, AUTHENTICATION_FAILED, … | exclude item; continue |
| Hold | DECISION_CONFLICT | HOLD_FOR_OPERATOR |

Diagnostics must not alter projection.

## Conformance (conjunctive)

30 normative tests including: no vote-proof, no report→proof, no action→proof, no failure→contradiction, permutation/duplicate invariance, exact decimal, strict typing, docs must not claim universal PROVEN.

```text
Conformant(I) ⇔ ∧_t Pass(I,t)
```

No percentage compliance.

## Keep / reject rule

\[
\mathrm{KEEP}(x) \iff A(x)\land P(x)\land F(x)\land M(x)\land B(x)
\]

- **A** ambiguity or burden decreases  
- **P** prior invariants preserved  
- **F** falsifiable adversarial test exists  
- **M** no second semantic truth source  
- **B** bounded non-sovereign scope  

**Box:** Keep only changes that reduce ambiguity without duplicating semantics.

## One-day implementation plan (if authorized)

1. Immutable contract types  
2. Closed-schema validation  
3. Exact typed normalization  
4. One resolver interface  
5. One verifier registry  
6. Witness / provenance / decision evaluators  
7. Immutable projection  
8. Pure classifier  
9. Bind `POST /v1/assess`  
10. Encode + run all 30 fixtures  

First-day verifiers: EXACT_VALUE, DIGEST, JSON_POINTER_VALUE, SIGNED_PROVENANCE, SIGNED_DECISION  

No DB, graph, ranking, authority model, ledger, or deploy platform required for the prototype.

## Public example (semantics)

Direct support + ACTED decision →  
`PROVEN` + `SUPPORTED` + `ACTED`  
**ACTED did not cause PROVEN.**

## NEXT_OPERATOR_ACTION

**HOLD_FOR_OPERATOR**

Human must **authorize or reject** a non-sovereign local prototype of `POST /v1/assess` against this frozen proposal.

Before any stronger claim:

1. local implementation  
2. every normative fixture  
3. machine-readable receipts  
4. exact-decimal verification  
5. timestamp-normalization verification  
6. cold-start reproducibility  
7. no sovereign component changed  
8. separate auth for any later SHIP/admission  

## Final state

```text
artifact_state: HYPOTHESIZED
empirical_receipt: NO_RECEIPT
proposal_only: true
NO_CLAIM · NO_SHIP · NO_ADMISSION
```
