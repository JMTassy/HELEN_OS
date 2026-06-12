# SKILL_ADMISSION_PROTOCOL_V1

## Core Formula

conversation ≠ constitution
artifact ≠ admission
ADMIT text ≠ ACTIVE state
ledger event + replay = governed reality

## Purpose

This protocol defines the lawful path by which a HELEN skill becomes institutionally ACTIVE.

## Required Pipeline

1. Temple Proposal
   - Candidate skill idea or implementation is proposed.
   - Authority: false.
   - World effect: none.

2. Oracle Pressure
   - Risks, overclaims, missing tests, provenance gaps, and injection risks are identified.
   - Oracle may critique but cannot admit.

3. Mayor Packet
   - Candidate is packetized with evidence:
     - files
     - tests
     - hashes
     - scope
     - authority boundaries
     - world-effect declaration

4. Reducer Decision
   - Reducer returns exactly one of:
     - ADMIT
     - REJECT
     - REQUEST_CHANGES

5. Decision Ledger Append
   - A conformant SKILL_PROMOTION_DECISION_V1 object is appended through the authorized decision-ledger path.
   - Speech receipts and routing ACKs are not sufficient.

6. Replay Verification
   - replay_ledger_to_state reconstructs governed state.
   - Skill is ACTIVE only if replay state says ACTIVE.

7. Operational Witness
   - The admitted skill is run once against live repository artifacts.
   - Output is committed as first operational witness.

## Non-Admission Artifacts

The following do not create institutional admission:

- chat messages
- helen_say.py routing receipts
- GATE_FETCH_PASS
- KERNEL_ACCEPT
- mutations: []
- countersigns
- test success alone
- ADMIT text outside decision-ledger replay

## Admission Test

A skill is institutionally active only when all are true:

- implementation exists
- tests pass
- valid SKILL_PROMOTION_DECISION_V1 exists
- decision ledger append exists
- replay state exists
- replay state marks skill ACTIVE
- operational witness exists

## Doctrine

Evidence proposes.
Ledger records.
Replay decides reality.
