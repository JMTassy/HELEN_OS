# RALPH_LOOP_2026-05-02_PHASE0 — Research Ralph, math_to_face Phase 0

**Status:** OPEN. Non-sovereign. Research-class.

**Operator authorization 2026-05-02 (HAL verdict):**
```json
{
  "verdict": "CONTINUE",
  "mode": "RESEARCH_RALPH_PHASE0",
  "authorized_scope": "experiments/helen_mvp_kernel/math_to_face_phase0/",
  "blocked_paths": [
    "helen_os/render/",
    "helen_os/schemas/",
    "temple/subsandbox/renders/"
  ],
  "required_invariant": "same input + same seed -> same spectrum hash + same SDE trace hash",
  "forbidden_claims": [
    "RH proof",
    "sovereign admission",
    "image generation",
    "cloud execution",
    "visual identity validation"
  ]
}
```

## Locked statement

```
Research subsandbox only.
No image generation.
No cloud.
No RH claims.
Replay determinism is the only success criterion.
```

## Phase 0 strict defaults

```yaml
N:                 7
primes:            [2, 3, 5, 7, 11, 13, 17]
epsilon:           0.05
c:                 1.2
fractal_kernel:    exp_neg_abs
phi_sde:
  T:               5.0
  dt:              0.1
  gamma:           0.0
  noise_seed:      0
  noise_mode:      ZERO_NOISE
  qam_projection:  zero       # NOT identity — identity zeroes drift
decimal_precision: 12
scope:             RESEARCH_SUBSANDBOX
sovereign_admitted: false
```

## Constitutional bounds

- All work scoped to `experiments/helen_mvp_kernel/math_to_face_phase0/`
- Schemas drafted in `experiments/helen_mvp_kernel/schemas/` (NOT helen_os/schemas/)
- Runtime outputs in `temple/subsandbox/research/<problem_id>/` (NOT renders/)
- Each epoch emits a 7-field PULL-mode receipt
- Halt on: forbidden-path attempt, hash drift, sovereign-admission boundary

## Goal

Build a stdlib-only, deterministic, hashable Phase 0 receipt loop:

```
m → embedding H(m) = z_0 → φ-SDE trace (zero noise, zero projection) → z_T → receipts
                                ↑
                          H_N spectral diagnostics
                                ↓
                          eigenvalues_hash, λ_min, λ_max, trace, frobenius
```

Success criterion: `same input + same seed → same hashes`, run 3×, all match.

## Epoch plan

| # | Goal | Output |
|---|------|--------|
| 1 | Open this loop log | `RALPH_LOOP_2026-05-02_PHASE0.md` |
| 2 | Draft 3 receipt schemas | `schemas/{h_n_spectral,phi_sde_trace,research_run}_receipt_v1.json` |
| 3 | Draft MAYOR precursor packet | `MAYOR_TASK_PACKET_PHASE0_SCHEMAS.md` (NOT SUBMITTED) |
| 4 | `embedding.py` — H(p) sin/cos | 512-dim from single prime |
| 5 | `h_n.py` — H_N + Jacobi eigensolver | spectrum diagnostics |
| 6 | `phi_sde_trace.py` — Euler-Maruyama | zero noise + zero projection |
| 7 | `receipts.py` — 3 emitters + SovereignWriteRefused | canonical hashing |
| 8 | `phase0_runner.py` + `fixtures/phase0_prime7.json` | orchestrator |
| 9 | `tests/test_phase0_replay.py` | replay invariant |
| 10 | Run 3×, verify all hashes match | emit `RESEARCH_RUN_RECEIPT_V1` |

## Receipt template (per epoch)

```yaml
epoch:               <n>
carry_forward_state: <what prior epochs left>
hypothesis:          <what this epoch tests>
experiment:          <what was actually built>
metric:              <how success is measured>
failure_mode:        <what would have caused halt>
keep_reject_rule:    <criterion for keeping>
upgrade_path:        <next-epoch consequence>
hal_verdict:         CONTINUE | DONE | BLOCK
```

---

## Epoch receipts

### Epoch 1 — open loop log

```yaml
epoch:               1
carry_forward_state: branch claude/setup-helen-os-node-b4uj8 with Higgsfield Ralph
                     loop committed (E1-E10). Phase 0 design proposal sent and
                     operator approved with strict defaults + qam_projection=zero
                     correction.
hypothesis:          a typed loop log artifact is sufficient to bound a
                     Research Ralph run without touching sovereign paths
experiment:          wrote RALPH_LOOP_2026-05-02_PHASE0.md with HAL verdict,
                     locked statement, strict defaults, bounds, plan
metric:              file exists in experiments/helen_mvp_kernel/, no writes
                     to blocked paths
failure_mode:        write to helen_os/render/, helen_os/schemas/, or
                     temple/subsandbox/renders/ would have halted
keep_reject_rule:    KEEP if file is operator-readable via git pull
upgrade_path:        epoch 2 drafts the 3 receipt schemas this loop emits
hal_verdict:         CONTINUE
```

---

### Epoch 2 — three receipt schemas

```yaml
epoch:               2
carry_forward_state: loop log open with HAL verdict + strict defaults
hypothesis:          three JSON Schema drafts in experiments/.../schemas/
                     can specify the receipt shapes for spectrum, SDE
                     trace, and run-wrapper without touching helen_os/schemas/
experiment:          wrote h_n_spectral_receipt_v1.json (15 required fields,
                     spectral_summary nested object), phi_sde_trace_receipt_v1.json
                     (16 required fields incl. qam_projection enum [zero,
                     identity]), research_run_receipt_v1.json (run-level
                     wrapper binding both with replay_check_hashes object)
metric:              all three are draft-2020-12 valid; additionalProperties:
                     false; scope locked to RESEARCH_SUBSANDBOX (single
                     enum value); sovereign_admitted const false;
                     decimal_precision const 12
failure_mode:        write to helen_os/schemas/ would have been a sovereign
                     mutation
keep_reject_rule:    KEEP if epoch 7 receipts.py can validate against them
upgrade_path:        epoch 3 drafts the precursor packet that proposes
                     promotion to helen_os/schemas/
hal_verdict:         CONTINUE
```

---

### Epoch 3 — MAYOR precursor packet (NOT SUBMITTED)

```yaml
epoch:               3
carry_forward_state: three schema drafts in experiments/.../schemas/
hypothesis:          a precursor MAYOR packet can be drafted and HELD,
                     marked NOT_SUBMITTED + SOVEREIGN_ADMISSION_REQUIRED,
                     so the sovereign-promotion path is documented but
                     not invoked unilaterally by the loop
experiment:          wrote MAYOR_TASK_PACKET_PHASE0_SCHEMAS.md targeting
                     three new files in helen_os/schemas/ + three append
                     entries in helen_os/governance/schema_registry.py;
                     7 acceptance criteria, 4 receipt types, locked
                     "NOT SUBMITTED" header
metric:              packet has all MAYOR_TASK_PACKET_V1 required fields,
                     forbidden_paths complete, hand-off command runnable,
                     status explicitly held
failure_mode:        invoking helen_say.py from within this loop would
                     have crossed the sovereign-admission boundary even
                     if daemon were up — packet is HELD by design
keep_reject_rule:    KEEP if operator can route via helen_say.py later
                     without edits to the packet
upgrade_path:        epoch 4 begins building actual code in
                     experiments/.../math_to_face_phase0/ — no further
                     sovereign-path authorization needed for that work
hal_verdict:         CONTINUE
```

---

### Epoch 4 — embedding.py (H(p) sin/cos)

```yaml
epoch:               4
carry_forward_state: 3 schema drafts + held MAYOR packet
hypothesis:          a stdlib-only embedding H(p) -> R^512 via sin/cos
                     with golden-ratio modulation is bit-deterministic
                     enough (with 12-decimal rounding) for replay
experiment:          wrote embedding.py with embed_prime(p) returning
                     [sin(2pi*p/phi^(j+1)) for j in 0..255] +
                     [cos(2pi*p^2/phi^(j+2)) for j in 0..255], plus
                     round_vector helper
metric:              importable; embed_prime(2) returns 512 floats; pure
                     stdlib (math only)
failure_mode:        a non-deterministic library call (e.g. random) would
                     break replay — only math.sin / math.cos / math.sqrt used
keep_reject_rule:    KEEP if epoch 9 replay test sees identical z_0 hash
                     across runs
upgrade_path:        epoch 5 builds H_N + Jacobi
hal_verdict:         CONTINUE
```

---

### Epoch 5 — h_n.py (Hamiltonian + Jacobi)

```yaml
epoch:               5
carry_forward_state: embedding ready
hypothesis:          stdlib Jacobi rotation eigensolver gives deterministic
                     spectrum for the symmetric H_N = D_N + epsilon*A_N
experiment:          wrote build_h_n() with D_kk = log(p_k)/sqrt(p_k),
                     A_kj = exp(-|p_k-p_j|)/(log(N)*|k-j|^c), explicit
                     symmetric construction; jacobi_eigenvalues() with
                     classical largest-off-diagonal pivot, tol=1e-14,
                     max_iter=1000; spectral_summary returns formatted
                     strings (not floats) so receipt JSON is bit-stable
metric:              symmetric matrix construction verified by code
                     symmetry assertion; Jacobi convergence in finite
                     iterations; spectral_summary fields all formatted
                     to 12 decimals
failure_mode:        Jacobi pivot ambiguity (multiple largest equal) ->
                     handled by deterministic first-encountered tiebreak
                     in nested loop scan
keep_reject_rule:    KEEP if epoch 10 sees identical operator_hash + 
                     eigenvalues_hash across runs
upgrade_path:        epoch 6 builds the SDE integrator
hal_verdict:         CONTINUE
```

---

### Epoch 6 — phi_sde_trace.py (Euler-Maruyama, zero noise + zero projection)

```yaml
epoch:               6
carry_forward_state: H_N + spectrum computable
hypothesis:          with qam_projection=zero (HAL correction) and
                     ZERO_NOISE, the discretized phi-SDE
                     z_{t+dt} = z_t * (1 - dt*phi^{-t}) is a clean
                     monotone contraction toward 0 — visible drift,
                     fully deterministic
experiment:          wrote integrate() with zero-noise / zero-projection
                     guards (NotImplementedError for SEEDED, ValueError
                     for gamma!=0 in Phase 0); records L2 norm at each
                     step into trace_norms; returns z_T + n_steps + trace
metric:              50 steps for T=5, dt=0.1 (matches fixture); each
                     step is a deterministic linear update; trace_norms
                     monotonically decreases
failure_mode:        a future change to qam_projection=identity would
                     zero the drift and break the contraction sanity
                     test in epoch 9 — guarded by explicit error from
                     epoch 9's contraction check
keep_reject_rule:    KEEP if z_T norm < 0.5 * sqrt(512) (contraction proof)
upgrade_path:        epoch 7 builds receipt emission + validation
hal_verdict:         CONTINUE
```

---

### Epoch 7 — receipts.py (3 emitters + SovereignWriteRefused guard)

```yaml
epoch:               7
carry_forward_state: math layers complete; need receipt-binding
hypothesis:          a single receipts module can validate against all 3
                     schema drafts AND refuse writes outside the research
                     subsandbox via FORBIDDEN_TARGETS (which now blocks
                     temple/subsandbox/renders/ per HAL verdict)
experiment:          wrote receipts.py with hash_vector / hash_matrix /
                     sha256_obj / canonical_json helpers; per-class
                     validators (_validate_lock + _validate_required);
                     three emit_*_receipt() functions writing to
                     temple/subsandbox/research/<problem_id>/;
                     _safe_target() refuses both direct matches and
                     descendants of FORBIDDEN_TARGETS (renders/ blocked)
metric:              jsonschema optional (manual fallback); locks
                     enforced before any write; _safe_target catches
                     descendant paths under blocked roots
failure_mode:        emitting into temple/subsandbox/renders/ would have
                     violated HAL verdict — _safe_target raises
                     SovereignWriteRefused; tested implicitly by epoch 10
keep_reject_rule:    KEEP if epoch 10 emits all 3 receipts to
                     temple/subsandbox/research/phase0_prime7/ cleanly
upgrade_path:        epoch 8 builds the orchestrator
hal_verdict:         CONTINUE
```

---

### Epoch 8 — phase0_runner.py + fixtures/phase0_prime7.json

```yaml
epoch:               8
carry_forward_state: math + receipts ready, no orchestrator
hypothesis:          a single runner consuming the fixture can produce
                     all three receipts deterministically; replay
                     invariant computed by hashing the receipt bodies
                     with timestamp_utc excluded
experiment:          wrote phase0_runner.py with compute_spectral(),
                     compute_sde(), receipt_canonical_hash() (timestamp-
                     stripped), run_one() and run_replay() entry points;
                     CLI mode supports --replay N; wrote fixture with
                     embedding_input_index=0 (so z_0 = H(2))
metric:              fixture loads cleanly, all required fields present;
                     run_one() emits 2 receipts, run_replay() runs N
                     times and checks 6 hashes for cross-run match
failure_mode:        timestamp inclusion in the replay-checked hashes
                     would have caused false drift — receipt_canonical_hash
                     strips timestamp_utc before hashing
keep_reject_rule:    KEEP if epoch 9 stdlib test passes; epoch 10 CLI
                     replay-3 emits research_run_receipt.json with
                     replay_consistent: true
upgrade_path:        epoch 9 writes the test
hal_verdict:         CONTINUE
```

---

### Epoch 9 — tests/test_phase0_replay.py

```yaml
epoch:               9
carry_forward_state: orchestrator runnable
hypothesis:          a stdlib-only test module covers all 6 hash invariants
                     + the constitutional locks + the contraction proof
experiment:          wrote 8 test functions: 6 replay-invariant checks
                     (operator, eigenvalues, trace, z_T, spectral receipt,
                     sde receipt), 1 lock check (scope, sovereign_admitted,
                     decimal_precision), 1 contraction sanity check
                     (z_T_norm < 0.5*sqrt(512)); supports both pytest and
                     stdlib `__main__` execution
metric:              8 tests cover the full non-negotiable invariant
                     surface from the HAL verdict
failure_mode:        a missing test for any of the 6 hash classes would
                     leave a drift hole — explicitly enumerated
keep_reject_rule:    KEEP if epoch 10 sees 8/8 PASS
upgrade_path:        epoch 10 executes
hal_verdict:         CONTINUE
```

---

### Epoch 10 — run 3x, verify hashes match, emit RESEARCH_RUN_RECEIPT_V1

```yaml
epoch:               10
carry_forward_state: full pipeline + replay test
hypothesis:          all 8 replay tests PASS, and a CLI replay-3 produces
                     replay_consistent=true with all 6 hashes stable
experiment:          1) ran tests/test_phase0_replay.py via stdlib __main__:
                        8/8 PASS
                     2) ran phase0_runner.py --replay 3:
                        replay_consistent: true
                     3) inspected receipts in
                        temple/subsandbox/research/phase0_prime7/:
                        h_n_spectral_receipt.json, phi_sde_trace_receipt.json,
                        research_run_receipt.json (all 3 with locks held)
metric:              ALL HASHES MATCH ACROSS 3 INDEPENDENT RUNS:
                        operator_hash:        ca082f2d...87127ecd
                        eigenvalues_hash:     2d1d96cd...bfc3e72f
                        trace_hash:           b4351ac3...5ebdd666
                        z_T_hash:             dd2072a0...9a778c46
                        spectral_receipt_hash:9a3067f0...f5677575
                        sde_receipt_hash:     7a342bc0...a264016fe

                     Math sanity:
                        trace = 4.701197344962  (= sum log(p)/sqrt(p) for
                                                   primes [2,3,5,7,11,13,17])
                        lambda_min = 0.489511406119
                        lambda_max = 0.736245612567
                        frobenius_norm = 1.789627509219
                        z_T_norm = 2.186427840408 (contracted from |z_0|<=22.6)

failure_mode:        any HASH_DRIFT_BLOCK would have halted before
                     research_run_receipt.json emission
keep_reject_rule:    KEEP — all invariants held
upgrade_path:        Phase 0 receipt loop is OPERATIONAL.
                     Phase 1+ promotion requires:
                       - operator authorization to submit
                         MAYOR_TASK_PACKET_PHASE0_SCHEMAS.md
                       - sovereign admission of the 3 schemas to
                         helen_os/schemas/
                       - migration of math_to_face_phase0/ code to
                         helen_os/render/math_to_face/phase0/ via
                         a parallel sovereign packet
hal_verdict:         DONE  (goal satisfied at epoch 10)
result:              REPLAY_CONSISTENT = TRUE; 8/8 tests PASS;
                     RESEARCH_RUN_RECEIPT_V1 emitted
```

---

## Loop summary

```yaml
loop:           RALPH_LOOP_2026-05-02_PHASE0
mode:           RESEARCH_RALPH_PHASE0
epochs_used:    10 / 10
budget_status:  exact-fit
goal_status:    SATISFIED — Phase 0 receipt loop is OPERATIONAL,
                replay-deterministic across 3 runs, 8/8 tests PASS

artifacts_committed:
  - experiments/helen_mvp_kernel/RALPH_LOOP_2026-05-02_PHASE0.md  (this file)
  - experiments/helen_mvp_kernel/MAYOR_TASK_PACKET_PHASE0_SCHEMAS.md  (HELD)
  - experiments/helen_mvp_kernel/schemas/h_n_spectral_receipt_v1.json
  - experiments/helen_mvp_kernel/schemas/phi_sde_trace_receipt_v1.json
  - experiments/helen_mvp_kernel/schemas/research_run_receipt_v1.json
  - experiments/helen_mvp_kernel/math_to_face_phase0/__init__.py
  - experiments/helen_mvp_kernel/math_to_face_phase0/embedding.py
  - experiments/helen_mvp_kernel/math_to_face_phase0/h_n.py
  - experiments/helen_mvp_kernel/math_to_face_phase0/phi_sde_trace.py
  - experiments/helen_mvp_kernel/math_to_face_phase0/receipts.py
  - experiments/helen_mvp_kernel/math_to_face_phase0/phase0_runner.py
  - experiments/helen_mvp_kernel/math_to_face_phase0/fixtures/phase0_prime7.json
  - experiments/helen_mvp_kernel/math_to_face_phase0/tests/__init__.py
  - experiments/helen_mvp_kernel/math_to_face_phase0/tests/test_phase0_replay.py

runtime_outputs (research subsandbox, NOT committed):
  - temple/subsandbox/research/phase0_prime7/h_n_spectral_receipt.json
  - temple/subsandbox/research/phase0_prime7/phi_sde_trace_receipt.json
  - temple/subsandbox/research/phase0_prime7/research_run_receipt.json

sovereign_writes:    0
forbidden_path_hits: 0  (renders/ blocking enforced by _safe_target)
ledger_admissions:   0
mayor_routings:      0  (precursor packet HELD, not submitted)
forbidden_claims:    0  (no RH proof, no image generation, no cloud, no sovereign promotion)
hal_final_verdict:   DONE
```

## Boundary held

- HAL only PROPOSED.
- Reducer never invoked.
- Ledger received zero entries.
- All 14 committed artifacts in `experiments/helen_mvp_kernel/`.
- All 3 runtime receipts in `temple/subsandbox/research/phase0_prime7/`.
- `temple/subsandbox/renders/` (blocked path) untouched.
- `helen_os/render/`, `helen_os/schemas/` (blocked paths) untouched.
- No RH claim. No image. No cloud. No sovereign promotion.

## Closing

> Phase 0 binds the receipts before the math is trusted.
> The math is now receipt-bound.
> Same input + same seed -> same hashes. 3 runs. Verified.
> The organism has its first deterministic vital sign.

---

## CORRECTION 2026-07-12 (Law 5 — corrections stay visible)

Epoch 6 of this loop described the zero-noise, zero-projection flow as
"a monotone exponential contraction toward 0." **That claim is false and is
hereby corrected.** The total drift mass ∫₀^∞ φ^(−t) dt = 1/ln φ ≈ 2.0781 is
finite, so the contraction factor has a strictly positive floor:

    continuous limit:   e^(−1/ln φ) = 0.125169442295
    discrete (dt=0.1):  0.112408840028  (infinite product)
    discrete (T=5):     0.136252952251

The epoch-10 receipt already witnessed this without our noticing: the recorded
`z_T_summary.max` = 0.136252952251 IS the discrete contraction factor to all
12 decimals (max z₀ entry = cos(tiny) = 1.0). The flow keeps ≈ 12.5 % of the
off-anchor latent forever; it never annihilates it.

Everything else in this loop stands: the replay-determinism result (8/8, 3×
hash-identical) is unaffected — determinism was the success criterion, and the
determinism claims were correct. Only the qualitative description of the
asymptotics was wrong.

Full statement, proof, dichotomy, and executable witness:
`experiments/helen_mvp_kernel/THEOREM_PHI_CONTRACTION_FLOOR_V1.md` +
`experiments/helen_mvp_kernel/helen_os/tests/test_phi_contraction_floor.py`
(7/7 PASS).

The corrected bet is the receipt.
