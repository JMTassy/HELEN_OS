# AUTORESEARCH EPOCH E002 — RECEIPT

🔵 OBSERVED · NON_SOVEREIGN · authority=0 · not admitted · no ledger effect
Loop: HELEN°FABLE vision+supervision · gemma4-12b local goblin ($0)
Target: affine capability layer (capability.py) @ c1d9c5d

## 7-field receipt

- **carry_forward_state**: κ = (id, binds_hash, pre_state_hash, scope, expiry, nonce);
  mint⇐ADMIT, affine one-shot, invocation-window sink guard. Peer-reviewed 14/14.
- **hypothesis**: an uncovered attack on the κ / one-shot / sink-guard design exists.
- **experiment**: gemma4-12b proposed "Semantic State Desynchronization" — mutate a
  state field NOT covered by pre_state_hash; κ stays valid, semantic context goes stale.
  Fable falsified under two hashing disciplines.
- **metric**: invoke() status under partial-hash vs total-hash after a hidden mutation.
- **result CLASSIFIED — BOUNDARY_CHIDDUSH (weaker than E001, NOT a code bug)**:
  - UNDER-HASH (caller commits only Balance, omits Internal_Flag): mutation → EXECUTED. Slips through.
  - TOTAL-HASH (caller commits full canonical state): mutation → PRE_STATE_MISMATCH. Caught.
  The equality check in capability.py is CORRECT. The gap is an *implicit, undocumented
  caller contract*: pre_state_hash MUST be a total commitment over all admission-relevant
  state. "A hash doesn't cover what it doesn't cover" — true but caller-side, not kernel logic.
- **keep/reject rule**: KEEP as contract hardening, REJECT the framing as a vulnerability.
  Failure ≠ falsification: the attack only works under caller error. Do not inflate.
- **upgrade_path**: (1) document the totality requirement in capability.py; (2) guard test
  proving total-hash catches hidden mutation + demonstrating under-hash is a caller violation.
  No change to invoke()/mint() logic.

## Fable supervision note
E001 was a real logic hole (PASS on stolen evidence). E002 is a contract clarification.
Reporting them at equal severity would itself be a category collapse. Honest tiering kept.
Goblin proposed; Fable classified; neither admitted.
