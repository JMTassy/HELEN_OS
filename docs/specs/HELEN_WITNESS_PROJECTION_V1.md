---
authority: NON_SOVEREIGN
canon: DRAFT
lifecycle: FROZEN_SPEC
status: IMPLEMENTATION_PENDING
version: 1.0.0
---

# HELEN_WITNESS_PROJECTION_V1

Formal specification for the HELEN witness layer: structural and numeric projection
of runtime state against the ledger truth baseline.

**Canonical position in the architecture:**

> Cognition proposes. Witness measures. Reducer decides. Ledger records.
> Autoresearch improves. Receipts authorize. Nothing else is sovereign.

The witness layer occupies the measurement slot. It reads; it does not write.
It classifies; it does not authorize. A COUPLED verdict does not mean SHIP.

---

## 1. Scope

This spec governs:

- `pi_struct` — the structural gate (binary pass/fail per check)
- `pi_num` — the numeric projection (value vs trusted baseline)
- Classification algorithm producing COUPLED / SOFT_DRIFT / HARD_DRIFT
- False-green test detection invariant
- API surface for witness comparison and profiling

It does NOT govern:

- Reducer decisions (LEGORACLE spec governs those)
- Ledger writes (kernel_daemon + helen_say.py govern those)
- Autoresearch epoch logic (AUTORESEARCH spec governs that)

---

## 2. Terminology

| Term | Definition |
|---|---|
| Trust Reality (`R_T`) | What the ledger asserts through its full replay |
| Runtime Reality (`R_R`) | What the filesystem and live processes show |
| Δ_R | The drift vector: `R_R − R_T` |
| pi_struct | Structural projection: ordered set of binary checks |
| pi_num | Numeric projection: ordered set of (value, baseline, tolerance) triples |
| Trust Baseline | The snapshot derived from full ledger replay; immutable until next ledger write |
| HARD_DRIFT | Any structural check fails; δ = +∞; operator must acknowledge |
| SOFT_DRIFT | All structural checks pass; at least one numeric projection diverges |
| COUPLED | All structural checks pass; all numeric projections within tolerance |

---

## 3. Structural Projection (pi_struct)

`pi_struct` is an ordered 7-tuple of binary checks. Each check is either PASS or FAIL.
A single FAIL anywhere in pi_struct produces HARD_DRIFT for the full witness result.

### 3.1 Checks

| ID | Name | What it verifies |
|---|---|---|
| S1 | `ledger_chain_integrity` | No unanchored dangling cum_hashes; no unexplained chain breaks; every LEDGER_SEQ_CORRECTION_V1 entry references a real dangling cum_hash |
| S2 | `skill_hash_consistency` | For all `s ∈ active_sovereign_skills`: `sha256(s.file_path) == s.candidate_identity_hash`; no sovereign skill file missing from disk |
| S3 | `sovereign_files_clean` | No file matching sovereign path patterns is modified outside the authorized writer; git-status check on all sovereign paths except `ledger_v1.ndjson` (expected dirty) |
| S4 | `reducer_schema_hash` | If a reducer deployment receipt exists in the ledger: `sha256(current_reducer.py) == receipt.reducer_hash`; PASS if no receipt exists (not yet admitted) |
| S5 | `required_receipts_present` | For all `a ∈ REQUIRED_RECEIPT_MANIFEST`: at least one sovereign receipt naming `a` exists in the ledger |
| S6 | `skill_manifest_linkage` | For all `s ∈ active_skill_manifest`: `s.file_path` exists on disk and is a non-empty file; no ghost skill references |
| S7 | `epoch_binding` | Full replay from seq=0 reproduces the live tail cum_hash; replay is deterministic and identity-consistent across epochs |

### 3.2 Sovereign path patterns (S3)

The patterns are inherited from `tools/reality_coupling_probe.py::_SOVEREIGN_PATTERNS`:

```
oracle_town/kernel/
helen_os/governance/
helen_os/schemas/
town/ledger_v1*.ndjson        # excluded from S3 check (expected dirty)
mayor_*.json
GOVERNANCE/CLOSURES/
GOVERNANCE/TRANCHE_RECEIPTS/
```

### 3.3 REQUIRED_RECEIPT_MANIFEST (S5)

Initial manifest (to be extended as receipts are issued):

```json
[]
```

The manifest is empty at spec freeze. Each artifact admitted via sovereign promotion
adds an entry. The manifest is stored at `docs/specs/schemas/REQUIRED_RECEIPT_MANIFEST.json`.

### 3.4 Formal definition of HARD_DRIFT

Let `π_s = (S1, S2, S3, S4, S5, S6, S7)` where each `Sᵢ ∈ {PASS, FAIL}`.

```
HARD_DRIFT ⟺ ∃ Sᵢ ∈ π_s : Sᵢ = FAIL
```

When HARD_DRIFT: `δ = +∞` (symbolic). The system is not safe for automatic state transitions.
Operator acknowledgement is required before any new sovereign ledger write.

---

## 4. Numeric Projection (pi_num)

`pi_num` is an ordered 7-tuple of numeric projections. Each projection is a triple
`(value, baseline, tolerance)` where:

- `value` — measured from runtime state
- `baseline` — derived from full ledger replay (the trust source)
- `tolerance` — acceptable divergence (0 for invariant-class checks)

A divergence in any `nᵢ` (i.e. `|nᵢ.value − nᵢ.baseline| > nᵢ.tolerance`) causes SOFT_DRIFT
if and only if all pi_struct checks are PASS.

### 4.1 Projections

| ID | Name | Measured from | Baseline | Tolerance |
|---|---|---|---|---|
| N1 | `ledger_entry_count` | Count of valid NDJSON lines in live ledger | Count after full replay | 0 |
| N2 | `active_skill_count` | Count of sovereignly active skills (promotions minus revocations) | Count from ledger replay | 0 |
| N3 | `correction_count` | Count of LEDGER_SEQ_CORRECTION_V1 entries | Count from ledger replay | 0 |
| N4 | `pending_receipt_count` | Count of operations without receipts awaiting admission | 0 (invariant) | 0 |
| N5 | `test_failure_count` | Count of failing test functions in `helen_os/tests/` + `tests/` | 0 (invariant) | 0 |
| N6 | `false_green_test_count` | Count of test functions with zero meaningful assertions (see §5) | 0 (invariant) | 0 |
| N7 | `critical_file_count` | Count of expected critical files present on disk | Derived from REQUIRED_RECEIPT_MANIFEST length + 4 fixed probes | 0 |

### 4.2 Baseline derivation

For N1–N3: the baseline is the count produced by `_replay_trust(ledger_path)` in
`tools/reality_coupling_probe.py`. No external snapshot is required; the ledger is
the truth source.

For N4–N6: the baseline is the constant 0. These are invariants, not time-varying counters.
Any deviation is immediately SOFT_DRIFT.

For N7: the baseline is `len(REQUIRED_RECEIPT_MANIFEST) + 4` where the 4 fixed probes are:
`tools/reality_coupling_probe.py`, `tools/reference_drift_probe.py`,
`scripts/helen_k8_lint.py`, `scripts/helen_k_tau_lint.py`.

### 4.3 Formal definition of SOFT_DRIFT

Let `π_n = (N1, ..., N7)` where each `Nᵢ = (value, baseline, tolerance)`.

```
SOFT_DRIFT ⟺ all(Sᵢ = PASS for Sᵢ ∈ π_s)
            AND ∃ Nᵢ ∈ π_n : |Nᵢ.value − Nᵢ.baseline| > Nᵢ.tolerance
```

### 4.4 Formal definition of COUPLED

```
COUPLED ⟺ all(Sᵢ = PASS for Sᵢ ∈ π_s)
         AND all(|Nᵢ.value − Nᵢ.baseline| ≤ Nᵢ.tolerance for Nᵢ ∈ π_n)
```

---

## 5. False-Green Test Detection

A **false-green test** is a test function that the test runner reports as PASS
without having exercised any meaningful assertion.

### 5.1 Formal definition

Let `T` be the set of all functions whose names match `test_*` in `helen_os/tests/`
and `tests/` (repo root).

A test `t ∈ T` is **false-green** iff:

```
count_meaningful_asserts(t) == 0
AND NOT is_explicitly_skipped(t)
AND NOT is_explicitly_xfailed(t)
```

Where:
- `count_meaningful_asserts(t)` = count of `assert` statements in `t`'s body where
  the asserted expression is not the literal `True` and not the literal `1`
- `is_explicitly_skipped(t)` = `t` is decorated with `@pytest.mark.skip` or
  `@pytest.mark.skipif`
- `is_explicitly_xfailed(t)` = `t` is decorated with `@pytest.mark.xfail`

### 5.2 False-green count

```
FG = |{t ∈ T : is_false_green(t)}|
```

**Invariant: `FG = 0`**

`FG` maps to `N6.value` in pi_num. Any `FG > 0` triggers SOFT_DRIFT.

### 5.3 Implementation target

`scripts/helen_false_green_lint.py` — AST-based scanner, no test execution required.
Output: list of (file, function, line) for each false-green test found.

---

## 6. Classification Algorithm

```python
def classify(pi_struct: list[Check], pi_num: list[NumericCheck]) -> str:
    if any(c.result == FAIL for c in pi_struct):
        return HARD_DRIFT
    if any(abs(n.value - n.baseline) > n.tolerance for n in pi_num):
        return SOFT_DRIFT
    return COUPLED
```

HARD takes precedence over SOFT. SOFT takes precedence over COUPLED.
COUPLED is the only safe state for automatic state transitions.

---

## 7. Witness Invariants

The witness layer MUST:

1. **Be read-only.** No witness operation may mutate the ledger, sovereign files, or runtime state.
2. **Produce deterministic output.** Same ledger + same filesystem state → same verdict, always.
3. **Fail closed on probe errors.** If a check cannot be evaluated, it returns FAIL (not PASS).
4. **Be composable.** Individual checks may be run in isolation for diagnostic purposes.
5. **Report exhaustively.** All failures must be reported, not just the first.

The witness layer MUST NOT:

1. Write to `town/ledger_v1.ndjson` or any sovereign path.
2. Invoke `tools/helen_say.py` or `tools/ndjson_writer.py`.
3. Emit SHIP or NO_SHIP verdicts — those belong to LEGORACLE.
4. Treat COUPLED as equivalent to ADMITTED or SHIP.
5. Block sovereign state transitions on SOFT_DRIFT — SOFT_DRIFT is informational only.

---

## 8. Relationship to Existing Probes

| Probe | File | Covers |
|---|---|---|
| REALITY_COUPLING_WITNESS_V1 | `tools/reality_coupling_probe.py` | S1 (chain integrity), S2 (skill hash), S3 (sovereign dirty) |
| REFERENCE_DRIFT_WITNESS_V1 | `tools/reference_drift_probe.py` | D(x) = C_R(x) × (1−P(x)) over artifact reference graph G_R; orthogonal to pi_struct/pi_num |
| HELEN_WITNESS_PROJECTION_V1 | `tools/witness_projection_probe.py` | Unified: π_s (S1–S7) + π_n (N1–N7) |

`tools/witness_projection_probe.py` will import from `reality_coupling_probe.py` for
the S1/S2/S3 logic rather than re-implementing it. S4–S7 and N1–N7 are net-new.

---

## 9. Output Schema

```json
{
  "schema_name": "HELEN_WITNESS_PROJECTION_V1",
  "schema_version": "1.0.0",
  "status": "COUPLED | SOFT_DRIFT | HARD_DRIFT",
  "ledger_path": "<path>",
  "pi_struct": [
    {
      "id": "S1",
      "name": "ledger_chain_integrity",
      "result": "PASS | FAIL",
      "detail": "<human-readable explanation on FAIL>"
    }
  ],
  "pi_num": [
    {
      "id": "N1",
      "name": "ledger_entry_count",
      "value": 0,
      "baseline": 0,
      "tolerance": 0,
      "divergence": 0
    }
  ],
  "false_green_tests": [],
  "delta": [
    {
      "severity": "HARD | SOFT",
      "code": "<DRIFT_CODE>",
      "detail": "<explanation>"
    }
  ],
  "deterministic": true
}
```

---

## 10. API Contracts (Phase 4 — not yet implemented)

### POST /runtime/witness/compare

Request:
```json
{
  "ledger_path": "<optional, defaults to town/ledger_v1.ndjson>",
  "checks": ["S1", "S2", "S3"]   // optional subset; default all
}
```

Response: `HELEN_WITNESS_PROJECTION_V1` output schema (§9).

### GET /runtime/witness/profile/:id

Returns the most recent stored witness result for a named profile `id`.
Profile IDs are assigned by the operator; the endpoint is read-only.

**Both endpoints are measurement surfaces only. They do not authorize state transitions.**

---

## 11. Implementation Status

| Component | Status |
|---|---|
| S1 — ledger_chain_integrity | LIVE (`reality_coupling_probe.py`) |
| S2 — skill_hash_consistency | LIVE (`reality_coupling_probe.py`) |
| S3 — sovereign_files_clean | LIVE (`reality_coupling_probe.py`) |
| S4 — reducer_schema_hash | PENDING |
| S5 — required_receipts_present | PENDING |
| S6 — skill_manifest_linkage | PENDING |
| S7 — epoch_binding | PENDING |
| N1–N3 — ledger-derived counts | PENDING |
| N4 — pending_receipt_count | PENDING |
| N5 — test_failure_count | PENDING |
| N6 — false_green_test_count | PENDING |
| N7 — critical_file_count | PENDING |
| False-green lint script | PENDING |
| Unified probe (`witness_projection_probe.py`) | PENDING |
| FastAPI endpoints | PENDING |

---

## 12. Implementation Order

1. `docs/specs/HELEN_WITNESS_PROJECTION_V1.md` — this document (DONE)
2. `scripts/helen_false_green_lint.py` — AST scanner, FG count
3. Extend `tools/reality_coupling_probe.py` — add S4, S5, S6, S7
4. `tools/witness_projection_probe.py` — unified probe composing S1–S7 + N1–N7
5. `helen_os/tests/test_witness_projection_probe.py` — test suite
6. FastAPI endpoints (Phase 5)
