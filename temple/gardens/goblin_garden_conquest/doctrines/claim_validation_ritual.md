# Doctrine: Claim Validation Ritual

**CLAIM_TYPE:** draft_doctrine  
**Purpose:** How claims are validated in DREAM_OF_CONQUEST. The ritual that separates territory from dispute.

---

## The Three-Step Ritual

```
CLAIM_VALIDATION_RITUAL(claim):

  Step 1 — JURISDICTION CHECK
    Does this agent have standing to make this claim?
    Is the claim within the dream world (not sovereign)?
    → FAIL: claim tries to reach ledger, kernel, schemas
    → PASS: claim stays within simulation boundary

  Step 2 — RECEIPT CHECK
    Does the claim have a backing receipt?
    Is the receipt chain at least 2 deep?
    Are all receipts authority=false, sovereign=false?
    → FAIL: unreceipted assertion
    → PASS: receipts present and valid

  Step 3 — HONEST LABELING CHECK
    Is the claim type explicit?
    Is the status PROPOSED (not CANON, SOVEREIGN, ADMITTED)?
    Are all uncertain elements labeled as such?
    → FAIL: unlabeled uncertainty, forbidden status
    → PASS: honest labeling throughout

  RESULT:
    ALL PASS → claim is VALIDATED → GATE_PASS awarded
    ANY FAIL → claim is DISPUTED → explain which step failed
```

---

## Why Three Steps

One step catches the gross violations.  
Two steps would miss subtle honest-labeling failures.  
Three steps mirrors the full HELEN gate pattern: jurisdiction, receipt, honesty.

The ritual is not bureaucracy. It is the minimum viable verification procedure.

## Proposer ≠ Validator in the Dream

Even in the simulation world, the proposer may not validate their own claim.  
The Goblin Guide validates. The player proposes.  
This mirrors the sovereign HELEN invariant — not by law here, but by design.

---

```
CLAIM_TYPE: draft_doctrine
AUTHORITY: false
SOVEREIGN: false
```
