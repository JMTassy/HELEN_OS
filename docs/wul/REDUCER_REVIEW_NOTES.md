# REDUCER_REVIEW_NOTES

Operational log for WUL_REDUCER_V0 sync work. authority=false · canon=NO_SHIP · no commit.
Not poetic. Source of truth = REDUCER_SPEC_V0 + executable tests + replay traces.

---

## Epoch 04 — GO SYNC REDUCER (REDUCER_V0 only), 2026-06-17

**Mission:** sync `src/wul_reducer.py` to the corrected spec + hardened sandbox reference
behavior. Close the split-brain (sandbox reference hardened; production stale/flag-trusting).

**Files changed (this hand):**
- `src/wul_reducer.py` — BED 02/03 hardening (see below)
- `tests/test_wul_reducer.py` — rebuilt to use derived predicates + adversarial vectors
- `docs/wul/REDUCER_REVIEW_NOTES.md` — this note

**Untouched (deliberately):** `docs/wul/REDUCER_SPEC_V0.md` (sibling-authored, coherent),
ledger, firewall/kernel/identity, all other external-writer files. No commit / stage / push.

**Hardening landed (the point of the sync):**
- ③ **Replay-derived predicates** — `typed`, `has_hash`, `gate_green`, `seal_valid`,
  `det_replay` are now DERIVED (`derive_facts()` recomputes the content hash and reads
  gate/replay attestations from a `ReplayContext`), never trusted as caller flags. A claim
  can no longer describe its own validity.
- ② **Un-self-conferrable seal** — `CanonAdmit` requires an external seal OBJECT bound to the
  candidate hash, issued by an OPERATOR role ≠ proposer, with a receipt known to the replay
  context. A bare `human_seal=true` flag is ignored.
- `Admit(c) ≠ CanonAdmit(c)` — kept and tested (`can_admit` vs `canon_admit`).

**Tests:** `.venv/bin/pytest tests/test_wul_reducer.py -q` → **28 passed**.

**Coverage checked:**
- T1 illegal promotion ............ covered
- T2 missing hash (L1) ............ covered (derived hash mismatch)
- T3 terminal frozen .............. covered  (+ T3b pre-terminal lawful-exit cases)
- T4 replay admissibility ......... covered
- T5 spec ceiling (L2) ............ covered  (authority-level + SPECULATIVE cap → REJECT_SPEC_CEILING)
- T6 terminal conflict (L7) ....... covered
- T7 happy path .................. covered
- T8 missing receipt ............. covered
- T10 reason missing (L5) ........ covered
- T12 max-state ceiling (L6) ...... covered
- T13 supersession + S_SUPERSEDED . covered
- forbidden transition matrix ..... covered (explicit FORBIDDEN_TRANSITIONS, tested)
- closed reject enum .............. covered (matrix values ⊆ REJECT_CODES)
- Admit(c) ≠ CanonAdmit(c) ........ covered
- BED 03 self-assert-by-flags ..... covered (bogus flags → S_REJECTED)
- BED 02 seal-must-be-external .... covered (issuer == proposer → REJECT_HUMAN_SEAL_MISSING)

**Sandbox cross-check (read-only):** `sandbox/wul_reducer/` reference — 12 vectors green,
mutation score 12/12 (100%, no survivors). Independent second proof, different state model
(admission_state axis vs S0–S6 ladder); behavior agrees.

**Concurrent-writer note:** during this sync a second runtime co-edited
`src/wul_reducer.py` + `tests/test_wul_reducer.py`. The merge converged coherently
(SPECULATIVE → REJECT_SPEC_CEILING; S_REJECTED/S_SUPERSEDED made pre-terminal with one
lawful exit to S_TERMINAL; +6 tests). Result is green and better-aligned to the closed
11-code enum. **File contention is live** — quiesce the second writer before any commit.

**Remaining blocker:**
- File contention (two writers on the same two files) — operational, not logical.
- `gate_green` / `det_replay` are attested by a `ReplayContext` stub; wiring to the REAL
  K-gate replay + a real receipt store is V1, not V0 (spec ceiling holds).

**State:** synced; reducer committed at `75dc168` (by the concurrent writer's broad commit).

---

## Epoch 05 — K2 peer review, 2026-06-17

Independent fresh-context review (reviewer ≠ proposer; proposer wrote both impl and tests).
Re-ran every check; ran an 8-vector adversarial battery.

**Verdict: peer_review_pass — 10/10 criteria, NO EXPLOIT.**
- predicates DERIVED (recompute hash; gate/replay from `ReplayContext`), not caller flags ✓
- seal un-self-conferrable: `receipt_hash ∈ rc.known_receipts` is the load-bearing barrier — the
  claim cannot populate the external `ReplayContext`, so no self-asserted seal passes ✓
- `Admit(c) ≠ CanonAdmit(c)` ✓ · forbidden matrix (12×12, only 18 lawful edges) ✓ ·
  terminal frozen / pre-terminal one-exit ✓ · determinism (hashlib+json only) ✓ ·
  cross-check vs independent sandbox reference: 12/12 mutation, 100% ✓

**Advisory (non-blocking) follow-ups:**
1. `verify_external_seal` trusts any `issuer_role="OPERATOR"` string — sound today (receipts
   unforgeable from claim side); future: `rc.authorized_operators` allowlist. — OPEN
2. dead `REJECT_CEILING_EXCEEDED` (12 codes vs spec's 11). — CLOSED at `ca79bf4`
3. `compute_candidate_hash` is content-scoped (ignores unknown fields); add a `$comment`. — OPEN

Boundary: this is a reviewer finding only; it does not admit to the ledger. Artifact remains
`authority=OPERATOR_BOUND · canon=NO_SHIP`, awaiting operator countersignature per spec header.

**State:** HOLD_FOR_OPERATOR. No push (needs PUSH_AUTHORIZATION=YES). No canon claim.
