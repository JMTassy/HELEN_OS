# AUTORESEARCH EPOCH ν — RECEIPT (execution-exhibit tracer, NU_EXECUTION_EXHIBIT_V1)

🔵 OBSERVED · NON_SOVEREIGN · authority=0 · not admitted · no ledger effect
Loop: HELEN°FABLE supervision · operator directive "build ν" @ 8ffe0ff

## 7-field receipt

- **carry_forward_state**: C17's disclosed residual was the injected `true_support` oracle — a real
  ν must OBSERVE support, not be handed ground truth. The relayed ν-EXHIBIT spec locked the honest
  contract: the tracer mints ADDRESSED VISIBILITY, not conclusions.
- **hypothesis**: ν can separate event / dependency / coverage into three objects — a content-
  addressed EXHIBIT that cannot carry a verdict, plus a pure VerifyCoverage — and prove it can never
  launder a pretty trace into completeness.
- **experiment**: built helen_os/audit/nu.py — ObsClass Ω, typed ExecutionEvent, PositiveDep (event
  refs), NegativeDep (discovery witness), OpaqueClass (𝒰), NuExhibit (content-address, closed verdict
  surface), pure verify_coverage(). 10 falsifiers incl. EXHIBIT-00.
- **metric**: does the EXHIBIT structurally exclude verdict fields, bind Ω pre-run, refuse forged/
  unwitnessed coverage, keep 𝒰 undeletable, and return UNKNOWN (not PASS/FAIL) on relevant opacity —
  while a fully-covered run still PASSes (non-vacuity)?
- **result — BUILT, GREEN (258→268)**:
  - **EXHIBIT-00 False Closure (constitutional test)**: Ω={FILE,ENV,NATIVE}, FILE+ENV covered with
    events, NATIVE opaque → EXHIBIT structure VALID, verify_coverage → **UNKNOWN** (RELEVANT_OPACITY),
    Π_D NOT earned. Not 2/3 PASS, not 66.7% — a beautiful JSON trace alone never earns coverage.
  - **anti-circularity**: `omega_pre_hash` bound to Ω; a retrospective Ω substitution → FAIL
    INVALID_CONTRACT. The tracer cannot define success after seeing its own blind spots.
  - **pessimistic law `d∉D⁺ ⊬ d∈D⁻`**: an unaccounted relevant class → FAIL UNCLASSIFIED_CLASS, never
    silently "covered." D⁻ is a witnessed discovery obligation, not an absent event.
  - **no forged/empty coverage**: a D⁺ citing a nonexistent seq → FORGED_EVENT_REF; empty evidence →
    COVERED_WITHOUT_EVIDENCE; NA without justification → NA_WITHOUT_JUSTIFICATION; double-classified
    class → OVERLAP_CLASS. All FAIL.
  - **𝒰 undeletable / partition conserved**: relevant opacity ⇒ UNKNOWN, and every relevant class must
    land in exactly one of covered ⊔ opaque ⊔ NA — no silent disappearance.
  - **closed verdict surface**: `_FORBIDDEN ∩ Fields(NuExhibit) = ∅` asserted at module load —
    complete / pi_d_pass / admit / authority / ledger_append / valid_by_transport cannot even appear.
    Closed verdict surface ≠ frozen vocabulary (like WVIS).
  - **content-address excludes views**: exhibit_id = H(identity_body) with `views` excluded — a new
    rendering view is not a new evidence identity; a real content change is. Positive control:
    fully-covered → PASS (non-vacuity). Determinism: pure; canon reuses ledger hash_chain.
- **keep/reject rule**: KEEP. This closes C17's injected-oracle residual honestly: Σ (coverage
  accounting) ≠ Π_D (verdict); EXHIBIT ≠ Π_D ≠ ADMIT. ν produces enough structured, addressed
  information for VerifyCoverage to judge whether the DECLARED contract was satisfied — it does not
  certify the world was fully observed.
- **upgrade_path / RESIDUAL**: the EXHIBIT is minted from INJECTED events (the falsifiers supply the
  ExecutionEvent list). A live ν must run real collectors — a narrow `sys.addaudithook` collector for
  FILE/ENV/IMPORT (one collector `C_audit ∈ Collectors(ν)`, NOT a sandbox, bypassable, native→𝒰),
  git/worktree frame binding, and namespace-discovery for D⁻. Wiring live collectors + pre-run Ω
  commitment in-process is production work (same derive-at-source residual class). Then ν feeds C17
  and C17 feeds C16. NON_SOVEREIGN, no sovereign path touched.

## KNOWN GAP (disclosed pre-commit — do NOT read this receipt as SHIP)
Adversarial re-review found **Negative-by-Silence** in `verify_coverage` (nu.py): a class is counted
covered if a `NegativeDep` of that class exists, but the function does NOT require the NegativeDep to
carry a witness (event refs / enumeration). So `¬Observed(d) → Excluded(d)` is currently expressible —
the "D⁻ is a witnessed discovery obligation" claim above is the INTENT, not yet enforced by code.
Fix pending (`harden ν`): require `NegativeDep.witness` non-empty + an EXHIBIT-02 (Negative-by-Silence)
falsifier + a wire-level `validate_exhibit_payload`. Committed as GREEN-WITH-KNOWN-GAP WIP, not SHIP.
ν was NOT independently peer-reviewed (proposer≠validator) before this commit.

## Fable supervision note
"build ν": built the locked EXHIBIT spec — event ≠ dependency ≠ exhibit ≠ coverage verdict ≠
transport. EXHIBIT-00 proves false closure returns UNKNOWN, not PASS; the verdict surface is closed
by construction; Ω pre-commitment defeats retroactive self-narration. The tracer mints addresses,
not conclusions. Neither admitted.
