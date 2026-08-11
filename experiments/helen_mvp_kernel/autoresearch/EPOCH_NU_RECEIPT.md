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

## KNOWN GAP — RESOLVED by `harden ν` (2026-08-11)
The Negative-by-Silence hole is now CLOSED. `verify_coverage` enforces the pointwise invariant
`∀d∈D⁻ ∃ valid witness` (step 3b): every declared exclusion must carry its own valid, executed, bound
witness, so `¬Observed(d) → Excluded(d)` is no longer expressible. `valid_negative_witness =
ValidStructure ∧ ValidBinding ∧ Executed` — a described-but-unexecuted obligation is NOT a witness.
Because each `NegativeDep` IS its own single-subject witness (cls=subject), one witness cannot launder
another subject's exclusion. Added wire-boundary `validate_exhibit_payload` (semantic gate, not
JSON-shape: rejects forbidden verdict fields AND unwitnessed/unexecuted D⁻ on raw input) — typed-
constructor safety ≠ wire-format safety. New falsifiers: EXHIBIT-02A (constructor), 02B (wire),
02C (witness-laundering) + unexecuted-obligation + positive control. **14/14 ν green, 272 suite green
(2 pre-existing surface failures unrelated). Independent peer-review: see verdict appended below.**

## Independent peer-review (proposer≠validator, K2/Rule 3) — SHIP 7/7
Fresh-context validator re-ran tests and re-derived every claim. Verdict: **SHIP peer_review_pass**.
- 14/14 ν falsifiers pass; full suite 272 passed (the 2 failures are pre-existing `test_surface_grammar`,
  unrelated to ν — no regression).
- Verified: step-3b enforces the pointwise D⁻ witness before partition; `valid_negative_witness` =
  Structure ∧ Binding ∧ Executed; wire gate is semantic (rejects forbidden verdict keys + unwitnessed /
  unexecuted D⁻); witness-laundering (02C) is genuinely pointwise (no `any()` shortcut — a naive
  `assert any(valid…)` would wrongly pass 02C; the code uses a per-d FAIL loop). No laundering bypass found.
- Reviewer KNOWN_GAPS (non-blocking, outside literal criteria — carried honestly, not a SHIP claim):
  (a) truthy-non-bool `executed='yes'` passes `bool(...)` — type-laundering surface, not witness-laundering
  (needs the subject's own sender to set it; cannot cover another subject). Future: strict `is True`.
  (b) `validate_exhibit_payload` scans only top-level keys — a forbidden verdict key nested inside a
  `d_plus` entry is not caught at the wire (the typed `NuExhibit` cannot carry it; only the wire top level
  is gated). Future: recursive forbidden-key scan.

## NU-INTEGRITY HARDENING V2 (2026-08-11) — both peer-review residuals CLOSED
- (a) **strict-bool `executed`**: `valid_negative_witness` now requires `d.executed is True` (not truthy);
  the wire gate requires `executed is True` too. `executed=1`, `"true"`, `[]` all REJECT. Closes the
  type-laundering surface — an execution witness must be a genuine bool True, not a coincidence of truthiness.
- (b) **recursive wire scan**: `validate_exhibit_payload` walks ALL descendant keys (`_descendant_keys`),
  so a forbidden verdict coordinate nested inside a `d_plus` entry / metadata / list cannot hide. Closed
  surface is recursive, not top-level-only.
- Falsifiers NU-03A (executed=1) / 03B (executed="true", + wire) / 03C (nested authority + deep list) /
  03D (clean nested metadata → PASS). **ν 18/18 green, full suite 276 passed (2 pre-existing surface
  failures unrelated).** Committed locally; PUSH held pending operator diff review.

## Fable supervision note
"build ν": built the locked EXHIBIT spec — event ≠ dependency ≠ exhibit ≠ coverage verdict ≠
transport. EXHIBIT-00 proves false closure returns UNKNOWN, not PASS; the verdict surface is closed
by construction; Ω pre-commitment defeats retroactive self-narration. The tracer mints addresses,
not conclusions. Neither admitted.
