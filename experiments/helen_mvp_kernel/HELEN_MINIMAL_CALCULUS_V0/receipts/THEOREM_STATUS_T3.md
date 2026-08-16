# HELEN THEOREM STATUS — T3_REPLAY_CONFLUENCE
Date: 2026-08-16 · NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none

SEMANTIC VERSION
  nu = sha256:eff29d80be0091c0   (Lean sources + jurisdiction gate + bounded executor)

FORMAL (Lean 4.33.0, lake build, zero sorry, zero axiom)
  Statement ................. FROZEN
  Definitions ............... PASS   (Step, Admissible, StrongIndependent — C1 folded in)
  replay_append ............. PASS
  replay_adjacent_swap ...... PASS   (the atomic brick; proof stayed short — definitions held)
  confluence_of_swapConnected PASS
  LinExt connectivity ....... OPEN   (explicit hypothesis; trace-theory argument unformalized)
  Global T3 ................. CONDITIONAL (closes when OPEN closes)

OBLIGATIONS ................. MAPPED (7; obligations/T3.yaml)

FALSIFIERS (real kernel: BoundedExecutor + TCB scan)
  hidden_state_probe ........ STATE_DETERMINISTIC=True; receipts deterministic
                              ONLY modulo witnessed ND surface {uuids, *_refs,
                              created_at} — REAL FINDING, feeds nu-canonicalization
  commutator_probe .......... COMMUTE on disjoint pairs; false-independence
                              claim REFUTED as ADMISSION_INSTABILITY (probe works)
  model_identity_probe ...... B_nu_token_level = 0 across 6 TCB components
  hidden-edge search ........ UNWIRED (needs causal-edge annotation on receipts)

COUNTEREXAMPLES
  0 found / obligations O1-O3, O5, O7 exercised; O4 unwired; O6 pattern established

CLAIM
  Confluence-under-swap-connectivity formally follows from the stated
  assumptions (machine-checked). No violation of the mapped, exercised
  obligations observed on the tested corpus.

NOT CLAIMED
  Global T3 unconditionally proved (connectivity OPEN) · implementation
  formally verified · receipt-level byte determinism (explicitly refuted —
  see finding) · anything beyond the tested corpus and this seat.

---
## T-003 CLOSURE WITNESS (frozen 2026-08-16, exact machine output)

ENVIRONMENT
  lean          = 4.33.0 (leanprover/lean4:v4.33.0, arm64-apple-darwin, commit d8b1897832)
  lake build    = "Build completed successfully (7 jobs)"
  mathlib       = NONE (zero external dependencies — pure core Lean)
  git           = repo HEAD aa315a7; HELEN_MINIMAL_CALCULUS_V0/ is UNTRACKED
                  (freeze witnessed by hash + this record, git-attestable only after COMMIT)

#print axioms (verbatim):
  'HMC.replay_adjacent_swap' does not depend on any axioms
  'HMC.replay_confluence_of_swapConnected' does not depend on any axioms
  'HMC.replay_confluence_of_linExt_connectivity' does not depend on any axioms
  (no sorryAx; not even propext / Classical.choice / Quot.sound)

EXACT SIGNATURES (from #check, verbatim in /tmp/t3_audit.lean run):
  replay_adjacent_swap :
    ∀ {State Receipt} (step) (s₀) (l₁ l₂) (r q),
      (∀ s', replay step s₀ l₁ = some s' → StrongIndependent step s' r q) →
      replay step s₀ (l₁ ++ r :: q :: l₂) = replay step s₀ (l₁ ++ q :: r :: l₂)
  replay_confluence_of_swapConnected :
    SwapConnected step s₀ l₁ l₂ → replay step s₀ l₁ = replay step s₀ l₂
  replay_confluence_of_linExt_connectivity :
    (∀ {l₁ l₂}, LinExt l₁ → LinExt l₂ → SwapConnected step s₀ l₁ l₂) →
    LinExt l₁ → LinExt l₂ → replay step s₀ l₁ = replay step s₀ l₂

T-003 = DONE. Promotion condition met (build ✓, declarations resolve ✓, no sorryAx ✓).

## ND-SURFACE SEMANTIC AUDIT (closes the canonicalization blocker for THIS kernel)

Witnessed by code inspection of bounded_executor_v1.py: no ND field
(decision_id, execution_id, artifact_id, created_at, decision_id_ref,
execution_id_ref, artifact_refs) is ever READ by execute(); receipts are
write-only outputs. The single receipt-derived feedback into future behavior
is execution_identity (registry duplicate-check), computed ONLY from
{tool_type, normalized_target, normalized_payload, pre_state_hash,
policy_version} — all semantic. Classification: ALL 7 ND fields =
OPERATIONAL-BY-CONSTRUCTION for this kernel; stripping them in π_sem is a
justified canonicalization HERE.
SCOPE CAVEAT (upstream suspicion remains valid elsewhere): in any future
ledger-replay kernel where receipts ARE inputs to F, artifact_refs becomes
potentially semantically live and must be re-audited before stripping.

T-004 (LinExt → SwapConnected connectivity): now UNBLOCKED, still OPEN.
No mathlib bridge assumed; project has zero deps — the finite-list bridge
will be built from scratch when its verb arrives.
