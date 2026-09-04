# STOCHASTIC CONFORMITY RECEIPTS V0 — the receipt is the delta-map
🟣 CLAIM · PROPOSAL · NON_SOVEREIGN · authority: false · NO_CLAIM beyond proposal

## Problem
NO RECEIPT = NO CLAIM assumes deterministic replay. Generative pipelines without seed access
cannot replay: hashing the job-id is a receipt of the REQUEST, not the GENERATION ("receipts theater").

## Proposal
Where determinism is unavailable, the receipt proves **measured conformity**, not reproducibility:
`receipt = hash(reference_id + prompt + job_id + measured_deltas)` where measured_deltas are
MECHANICAL gates run on the output (e.g. deltaE76 in CIE Lab vs a calibrated reference; edge-frequency
ratio vs texture floor). The delta-map IS the receipt: an auditable statement of how far the artifact
sits from its anchored reference, re-checkable forever from the stored artifact + reference.

## Laws
1. A conformity receipt NEVER claims replay. It claims: "this artifact, hashed X, measured D from reference R under check C_version."
2. Gates must be pure code (no model in the judge lane) and must carry their own discriminance proof
   (a synthetic violation the gate demonstrably rejects).
3. Tolerance bands are frozen per reference BEFORE batch generation (frozen-judge rule).
4. An artifact without a conformity receipt is a picture; with one, it is evidence of conformity — never more.

## Provenance
Emerged from AR_5400 goblin autoresearch (2026-07-26): contrarian kill "receipts theater" transmuted;
anchored same-day by delta_e_check.py on real assets (sanity 0.0 / lineage 4.05 PASS / injected-drift 13.64 REJECT).
Located: helen_kernel ar_5400 (kernel-side). Enforced: not yet (this is the proposal). Replay-tested: gate
discriminance proven; doctrine itself NOT admitted — per DOCTRINE_ADMISSION rules, needs operator + gate.
