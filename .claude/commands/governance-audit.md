# HELEN Governance Audit

Run the full governance gate battery and report violations.

## Inputs

$ARGUMENTS — scope. Options: "full", "kernel_guard", "palette", "drift", "k8", "ktau", "schema". Default: "full".

## Recipe

### Gate Battery (run in parallel where possible)

1. **kernel_guard** — `bash tools/kernel_guard.sh`
   - Checks RULE 1 (only admitted writers touch ledger) and RULE 2 (CONSUMER_ALLOWLIST)
   - Every allowlist entry must have an inline authorization citation
   - File-level allowlisting does not auto-extend to new handlers

2. **palette_disjointness** — `.venv/bin/pytest tests/test_wulmoji_palette_disjointness.py -v`
   - One glyph one meaning per namespace
   - STATUS ∩ VERBS = ∅
   - Validator ↔ canonical table coverage
   - Doctrine-sync: parses CLAUDE.md palette line

3. **drift_algebra** — `.venv/bin/pytest tests/test_transport_drift.py -v`
   - D1-D4 law witnesses (identity, symmetry, triangle, soundness)
   - I1: palette coverage Δ=0
   - I2: cross-namespace divergence = CROSS_NAMESPACE_REUSE
   - I3: K-tau needle contradiction Δ>0

4. **k8_lint** — `.venv/bin/python scripts/helen_k8_lint.py --mode all_nd`
   - mu_NDWRAP, mu_NDARTIFACT, mu_NDLEDGER

5. **ktau_lint** — `.venv/bin/python scripts/helen_k_tau_lint.py`
   - mu_BOUNDARY, mu_IO, mu_DETERMINISM, mu_ALLOWLIST, mu_SCHEMA

6. **schema_audit** — `.venv/bin/python helen_os/governance/schema_index_audit.py`
   - Dual-recognizer audit of schema registry

7. **full_test_suite** — `make test`

### Analysis

For each gate failure:
- Classify: STALE_ALLOWLIST / DRIFT / DETERMINISM / COVERAGE_GAP / SCHEMA_ORPHAN
- If STALE_ALLOWLIST: prepare allowlist reconciliation packet (cite authorization docs)
- If DRIFT: compute Δ(doc, impl) and Δ(doc, guard) using `transport.drift`
- If DETERMINISM: identify the violation source and proposed fix
- Report all findings; patch only STALE_ALLOWLIST (requires explicit authorization citations)

### Output

Governance audit receipt with per-gate PASS/FAIL and finding details.

## Constraints

- Never edit sovereign files to make a gate pass — report the failure.
- kernel_guard fixes require dual-tier citations (DOCTRINE + filed authorization).
- After any fix: re-run the specific gate to confirm green.

## Loop Engineering (Fable)

Weekly audit cadence. Each run's findings become regression fixtures for the next:
```
findings = governance_audit("full")
for f in findings:
    if f.type == "STALE_ALLOWLIST" and f.has_authorization:
        patch(f)  # auto-fix with citation
    else:
        report(f)  # operator queue
```
