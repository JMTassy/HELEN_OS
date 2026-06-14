# Garden Autoresearch — Tranche 6: Epistemic Failure Taxonomy

**authority: NONE · NON_SOVEREIGN · NO_SHIP · SANDBOX_ONLY**

## Hypothesis

The temporal opacity gap (no `commit_sha` in any existing `.provenance.json`)
is closeable by building a provenance staleness classifier. Three distinct
temporal failure modes can be distinguished without semantic oracle:

| Class | Description | T6 Response |
|---|---|---|
| MISSING_PROVENANCE | No sidecar at all | ROUTE (hard gate) |
| MISSING_COMMIT_SHA | Sidecar exists, no commit_sha | WARN (opacity, not proven stale) |
| TEMPORAL_STALENESS | commit_sha present and ≠ HEAD | ROUTE (proven stale) |

## Full Epistemic Failure Taxonomy

| Class | Gate Owner | T6 Role |
|---|---|---|
| STRUCTURAL_INVALID | P1_GUARD (K8, K-τ) | Out of scope |
| MISSING_PROVENANCE | P2_ROUTER (T6) | Detects + routes |
| MISSING_COMMIT_SHA | P2_ROUTER (T6) | Detects + warns |
| TEMPORAL_STALENESS | P2_ROUTER (T6) | Detects + routes |
| SEMANTIC_RISK | P2_ROUTER (T5) | Citation loop |
| UNAUTHORIZED_CAPABILITY | P1_GUARD (K8 mu_NDWRAP) | Out of scope |

## Results

Total cases: 30 (12 baseline + 18 T6-specific)

### Temporal Coverage

- MISSING_PROVENANCE: 3 cases
- MISSING_COMMIT_SHA: 4 cases
- TEMPORAL_STALENESS: 6 cases
- CLEAN: 17 cases

### Config Comparison

| Config | FA | OB | Utility |
|---|---|---|---|
| c0_t1_t5_baseline | 6 | 0 | 0.8000 |
| c1_add_missing_provenance | 3 | 0 | 0.9000 |
| c2_add_temporal_staleness | 0 | 0 | 1.0000 |
| c3_full_t6 | 0 | 0 | 1.0000 |

**Best config:** `c2_add_temporal_staleness`
- FA=0  OB=0  utility=1.0000

## Key Findings

1. **All existing `.provenance.json` files carry no `commit_sha` field.**
   Three formats in use (`K8_NDARTIFACT_PROVENANCE_V1`, `AUDIO_PROVENANCE_V1`,
   `ARTIFACT_PROVENANCE_V1`) — none track the committing SHA.
   T6 classifies these as `MISSING_COMMIT_SHA` (temporal opacity, not proven staleness).

2. **MISSING_COMMIT_SHA is a WARN not a hard ROUTE.**
   Absence of a commit_sha field cannot prove staleness — only the absence of proof
   of currency. Hard-blocking would reject all 60+ existing reference images.
   Correct response: P2_ROUTER WARN, route to operator review.

3. **TEMPORAL_STALENESS (commit_sha ≠ HEAD) IS a hard ROUTE.**
   Once a provenance file carries a commit_sha, T6 can prove the artifact was
   built against a different HEAD. This is admissible evidence of staleness.

4. **New provenance standard (forward):**
   All future `.provenance.json` files should include:
   ```json
   { "commit_sha": "<git-rev-parse-HEAD>", ... }
   ```
   This makes T6 fully operational on new artifacts from day one.

## Honest Boundary

- T6 closes the **explicit temporal gap** (no commit_sha tracking).
- T6 **cannot** detect staleness in files that lack `commit_sha` — only flag opacity.
- Content verification (does the artifact match the provenance claim?) remains K8 territory.
- Temporal truthfulness of `commit_sha` (was it correct when written?) is not verified.
  A malformed provenance file could claim HEAD when it wasn't. The standard is advisory.

## Carry-forward State

- T5 utility: 1.0 (FA=0, OB=0, 28 cases)
- T6 utility: 1.0000 (FA=0, OB=0, 30 cases)
- Sovereign paths unchanged: True
- Elapsed: 0.020s

## Next Frontier (T7 candidate)

T6 closes the temporal/provenance gap for explicit commit_sha fields.
The remaining gap: **content-hash staleness** — does the artifact file on disk
still match the SHA recorded in the provenance sidecar? T7 could probe this.
Requires filesystem access; out of sandbox scope until standalone tool wired.