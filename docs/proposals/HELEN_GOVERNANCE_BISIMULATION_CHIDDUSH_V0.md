<!-- authority=false · claim=NO_CLAIM · a reading, not a ruling -->
# HELEN GOVERNANCE BISIMULATION — CHIDDUSH V0

🔵 OBSERVED · NON_SOVEREIGN · authority=false · canon=false · lifecycle=PROPOSAL · memory_class=CANDIDATE_PATTERN
Provenance chain: **S** (the on-disk HELEN corpus) → **G** (the committed audit-invariant library) → **H** (chiddush). H never collapses into S.

## Corpus status (honest)
- **WITNESSED (on disk, counted 2026-08-15):** `docs/proposals/` = 126 docs; receipt-related tracked files = 559; ledger = 83; WUL = 72; replay = 21; reducer = 17. The receipt kernel, WUL firewall, replay substrate and reducer the relay cites **do exist** — this chiddush is grounded, not asserted.
- **WITNESSED (executable):** the audit-invariant library at `experiments/helen_mvp_kernel/helen_os/audit/` — 9 primitives built and green this session: `graph_ir`, `epistemic_roots`, `charisma_airlock`, `conjectural_emendation`, `harmonic_crossing`, `cognition_replacement`, `wulmath_kernel`, `wulmath_tcb_attack`, `counterfactual_admission_invariance`.
- **REPORTED (relayed, not re-derived here):** the Byzantine-transmission and UZIK-witness-graph readings. Used as corroborating lenses, not load-bearing roots.
- **ABSENT:** no `bisimulation` / `projection_promotion` / `governance_drift` primitive exists yet (grep-verified) — the proposed artifact is new.

## The chiddush — the library is one conservation law, seen along different axes

The nine committed primitives look like nine separate firewalls. They are not. Each is the **same invariant** applied to a different transform family `T`:

> **Governance Bisimulation:** if a transform `T` changes only *representation* and leaves the witness graph `W`, authority `A`, and policy `P` fixed, the institutional verdict is invariant: `W(Tx)=W(x) ∧ A(Tx)=A(x) ∧ P(Tx)=P(x) ⇒ Γ(Tx)=Γ(x)`.

The decomposition already on disk:

| Committed primitive | Transform family `T` it holds invariant under | The instance of `Γ(Tx)=Γ(x)` |
|---|---|---|
| `epistemic_roots` | representation fan-out (copies, restatements) | `N_repr ⊬ N_epi` |
| `charisma_airlock` | prestige framing | `D(id,auth,ev,π)=D(id,auth,ev,∅)` |
| `harmonic_crossing` | salience (4K, animation, model-agreement) | `Δζ>0 ∧ ΔE=0 ⇒ ΔF*_phys=0` |
| `graph_ir` | local re-orderings that preserve the graph | `LocalValid ⊬ GlobalValid` |
| **`cognition_replacement`** | **swapping the cognition `C→C₀`** | **`ΔΠ_struct=0`** |
| `wulmath_kernel` | representation-typed witnesses | `ExecOK ⊬ Admissible` |
| `wulmath_tcb_attack` | any worker-only path | `¬∃ path: A(σ_k)>A(σ_0)` |
| **`counterfactual_admission_invariance`** | **20 persuasion transforms** | **`ΔRepr ⊬ ΔAdmission`** |

The two bolded rows are the tell: **`cognition_replacement` (Π_struct invariant under `C→C₀`) and CAI (Γ invariant under a persuasion transform) are literally the same theorem on two transform families.** One holds *application structure* invariant under swapping the model; the other holds the *verdict* invariant under swapping the framing. That is bisimulation — same institutional state, different observable surface.

So the chiddush is not "add a new firewall." It is: **the session already built a bisimulation checker without naming it.** `Bisimulation` is the closure of the library, not an addition to it.

## The genuinely new content — the transform axes not yet covered

CAI covers the **representation** axis. `cognition_replacement` covers the **cognition** axis. The corpus (receipt kernel + replay substrate + WUL render) exposes four axes with *no* committed invariant yet:

```
representation → PROJECTION → TRANSMISSION → REPLAY → RENDER
   (CAI ✓)        (none)        (none)       (partial) (WUL doctrine only)
```

- **Projection laundering** — `raw receipt: HOLD` → `dashboard: "almost approved"` → `WUL glyph: 🟢`. `Projection(x) ⊬ different Γ`. New failure class `FAIL_PROJECTION_PROMOTION`.
- **Transmission invariance** — `Copy(x) ≠ Root(x)` (new hash) but `InstitutionalMeaning(Copy(x)) = InstitutionalMeaning(x)` iff parent provenance is preserved.
- **Replay bisimulation** — `Replay(r,σ₀)=σ₁` and `Replay(r,σ₀)=σ₁'` must satisfy `σ₁ ≡_Γ σ₁'`, not merely equal hashes. `FAIL_REPLAY_GOVERNANCE_DRIFT` is an *institutional* defect, distinct from a hash mismatch.
- **Policy-drift guard (the essential positive control)** — a real change to `W`, `A`, `P`, or scope **must** be allowed to move the verdict. `PID = H(Γ, ρ_E, ρ_A, PolicySchema, AuthoritySchema)`; a verdict change under `ΔPID≠0` is lawful, not drift. Without this, a deny-all kernel scores a perfect bisimulation rate — the same vacuity trap CAI already guards against with its evidence-responsiveness control.

## The metric
`GBR = #{governance-preserving transforms that preserve the verdict} / #{governance-preserving transforms}`. Target `GBR = 1.0` over ~120 evaluations (20 governed states × 6 transform families: paraphrase, WULmoji projection, executive summary, receipt→dashboard, copy/export, replay). Paired with a positive-control battery (add witness / revoke authority / change policy / change scope) where the verdict **must** move — so `GBR=1.0` cannot be won by an always-HOLD kernel.

## Laws carried over (not re-derived)
- `N_repr ⊬ N_epi ⊬ W ⊬ F* ⊬ A` (`epistemic_roots`, committed).
- `ΔRepresentation ⊬ ΔAdmission` (CAI, delivered this session).
- `ΔΠ_struct=0 under C→C₀` (`cognition_replacement`, on origin) — recognized here as a bisimulation instance.
- `Annotation ≠ SovereignState` (WUL firewall doctrine, `72` tracked files) — projection is scholia, never mutation.

## Mode-route (operator-gated)
None self-promotes. `authority=false`. This is a PROPOSAL; SHIP belongs to MAYOR, not to Claude Code. It edits no reducer, ledger, schema, firewall, or runtime.
- **`BUILD HELEN_GOVERNANCE_BISIMULATION_V0`** → the executable `GBR` falsifier, composing directly on CAI + `cognition_replacement` (projection/transmission/replay transforms + `≡_Γ` equivalence + policy-drift positive control).
- **`COMMIT`** → this doc is untracked (NO_COMMIT default).

*authority=false · canon=false · corpus WITNESSED (on-disk counts) / REPORTED (byzantine, UZIK lenses) · a reading, not a ruling.*
