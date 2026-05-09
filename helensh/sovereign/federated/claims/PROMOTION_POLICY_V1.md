# PROMOTION_POLICY_V1

**Status:** PROPOSAL  
**Class:** FEDERATED_SOVEREIGN  
**Authority:** NON_SOVEREIGN  
**Canon:** NO_SHIP until MAYOR review  
**Author:** JM Tassy  
**Date:** 2026-05-09

---

## Purpose

Defines the rules by which a pre-claim fragment becomes a `VerifiableClaim` in the shared sovereign layer. MAYOR approves **promotion rules**, not every promotion manually.

---

## Pipeline

```
PRE_CLAIM → TRIAGE → EVIDENCE_REQUIRED → VERIFIABLE_CLAIM → CANONICAL | REJECTED | DEFERRED
```

---

## Five Required Fields

No pre-claim becomes sovereign truth without:

1. `proposed_class` — receipt class assignment (EPHEMERAL / LOCAL_SOVEREIGN / FEDERATED_SOVEREIGN / PUBLIC_SOVEREIGN / REBUILDABLE / SEALED)
2. `evidence` — at least one non-empty pointer
3. `falsification_test` — a concrete test that could falsify the claim
4. `reviewer` — assigned role (MAYOR / GOVERNOR / TEST / PUBLIC)
5. `receipt_hash` — hash trail from source to claim

---

## Three Promotion Gates

MAYOR approves these rules once. Individual promotions flow through the gate automatically.

### Gate A — AUTO-PROMOTABLE
**Eligible status:** `OBSERVED`, `PROVEN`, `SHIPPED`  
**Requirement:** receipt hash only — no human review needed  
**Rationale:** empirically confirmed or already in code; promotion is administrative

### Gate B — REVIEW-PROMOTABLE
**Eligible category:** `DOCTRINE`, `ARCHITECTURE`, `MECHANISM`  
**Requirement:** MAYOR or GOVERNOR review before promotion  
**Rationale:** these claims reshape the constitutional surface; must be adjudicated

### Gate C — TEST-PROMOTABLE
**Eligible category:** `INVARIANT`, `ATTACK_SURFACE`, `GAP`, `TEST`  
**Requirement:** must produce at minimum one of: experiment result, documented failure mode, or patch  
**Rationale:** these claims are falsifiable — promotion without evidence is doctrine pollution

---

## Claim Schema

Three-field decision model — each claim passes through three independent verdict layers:

```
decision          — Gate A verdict (AUTO | PENDING)
reviewer_decision — GOVERNOR or TEST verdict (PENDING | PASS | FAIL | DEFERRED)
mayor_decision    — MAYOR terminal gate (PENDING | SHIP | NO_SHIP | DEFERRED)
```

**MAYOR's NO_SHIP is unconditional.** A claim can hold `decision: AUTO` and `reviewer_decision: PASS` and still receive `mayor_decision: NO_SHIP` if MAYOR rules it irrelevant to the current sovereign direction. Even KEEPER-class claims are subject to this gate.

HAL `APPROVE` at confidence 1.0 is necessary but not sufficient. It proves direction coherence. It does not prove artifact existence, codebase grounding, real evidence, or current relevance. MAYOR is the terminal legitimacy gate.

See `promotion_queue.jsonl` for the canonical field structure.

---

## Keeper Lines

> The swarm is 51 pre-claims competing for 51 promotion votes; MAYOR is not the oracle of truth, MAYOR is the bottleneck of legitimacy.

> Shared reality begins when a swarm-fragment survives promotion into a signed claim.

---

*HELEN OS — created by JM Tassy.*
