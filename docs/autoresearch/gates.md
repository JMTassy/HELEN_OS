# Autoresearch Gate Stack

Gates for validating research claims before receipt emission.
Every gate is binary: PASS or FAIL. One FAIL blocks the receipt.

| Gate | Name | What it checks | Failure mode |
|---|---|---|---|
| K0 | Syntax valid | Claim is parseable, no corrupt JSON, no truncated text | Emit ERROR receipt |
| K1 | Source bound | Claim references ≥1 file path or ledger entry | Claim is ungrounded |
| K2 | Claim explicit | Claim uses definite language: counts, paths, hashes — not "probably" | Symbolic inflation |
| K3 | Evidence attached | source_path, source_hash, method all present | Unverifiable claim |
| K4 | Method declared | Probe type specified (FREQUENCY/COUPLING/EVOLUTION/CONTRADICTION) | Unreproducible |
| K5 | Contradiction scan | Claim does not contradict existing CONFIRMED receipts at same source | False update |
| K6 | Provenance stable | Source file sha matches what was bound at probe time | Drift during epoch |
| K7 | Replay path | Claim can be reconstructed from evidence bindings alone | Non-replayable |
| K8 | Deterministic artifact | No ND output in claim chain (no model output, no random) | K8 mu_NDWRAP |
| Kτ | Temporal coherence | Timestamp plausible; utcnow() pattern only; no datetime.now() | K-τ mu_DETERMINISM |
| W  | Witness coupling | Claimed state matches observed ledger state | Δ_R > 0 |

## Gate Scoring

Each gate scores 0 or 1.
Total gate score = sum / 11.
Receipt is emitted only if all 11 gates PASS (score = 1.0).
Partial scores are diagnostic only — never admission.

## Gate Relationship to Production Gates

These autoresearch gates mirror the production gate stack:

| Autoresearch gate | Production equivalent |
|---|---|
| K0-K4 | Schema validation (helen_os/schemas/) |
| K5 | Contradiction scan (LEGORACLE replay gate) |
| K6 | K8 mu_NDARTIFACT (provenance sidecar) |
| K7 | Replay path (helen_os/tests/test_ledger_replay.py) |
| K8 | scripts/helen_k8_lint.py mu_NDWRAP |
| Kτ | scripts/helen_k_tau_lint.py mu_DETERMINISM |
| W  | tools/witness_projection_probe.py |

## Honest Boundary

K5 (contradiction scan) cannot detect semantic contradictions — only structural ones
(same source path, different claim type). Semantic falsity requires reducer/human oracle.
This is the same gap as T5: structural ceiling = 0.6667 on semantic cases.
