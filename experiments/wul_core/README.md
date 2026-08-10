# WUL-Core · projection-only semantic codec (V0)

<!-- NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none. -->

**Frame receipt (2026-08-10).** An E-WUL-006/007 suite reporting 23/23 was
described in another frame but never pushed; `ObservedThere ⊬ ObservedHere`,
so it is not imported as canon. This directory is the **first witnessed**
implementation of the WUL-Core contract on the SOT, built directly to the
corrected architectural ruling — the pre-freeze patterns (positional
`rendered[0..2]` indexing, `parse_wul(rendered, known_authority)`) never
touched disk here.

## The frozen contract

```text
X = (τ, φ, w, a, p)          machine state
π_visual(X) = (τ, φ, w)      the only thing that renders
P(E(X)) = π_visual(X)        parse recovers the projection, not the state
Authority ∉ Codomain(parse_wul)
🚫 a does not travel   🚫 p does not travel
```

- `encode_wul` → `"φ|τ|w"`, delimiter transport (multi-codepoint emoji safe;
  🛡️ carries VS16 and would shear under positional slicing — tested).
- `parse_wul` → `WULProjection(glyph, phase, frame)` only. No `known_authority`
  parameter: the visual decoder does not participate in authority
  reconstruction. `Parse ≠ RehydrateMachineState`.
- `AUTHORITY_BEARING_TYPES = {CAP, EFFECT}` — RECEIPT and LEDGER are governed
  *records*, not executable authority objects (`SovereignRisk(x) ≠ Authority(x)`);
  the set expands only when a concrete machine capability requires it.

## Laws enforced by `WULState.validate()`

| code | law |
|---|---|
| `E_AUTHORITY_COLLISION` | only CAP/EFFECT may carry `GOVERNED`; ADMIT ≠ capability |
| `E_GARDEN_AUTHORITY` | 🌿 frame is A=0 by construction |
| `E_CAP_WITHOUT_RECEIPT` | governed authority requires provenance |
| `E_SOVEREIGN_SURFACE` | garden creatures (🌰🧌△) never occupy ⬡ |
| `E_PHASE_MISMATCH` | judgment surfaces (🛡️⚖️) don't compost or germinate |
| `E_UNWITNESSED_GREEN` | ∅ → 🟢🛡️ uninhabitable (HAL Witness Law) |

## Tests — 24/24, witnessed on this filesystem

`python3 -m pytest experiments/wul_core/test_wul_core.py -q`

Includes the two ruling-mandated boundary tests:

1. `test_authority_not_in_parser_codomain` — the projection has no
   `authority` attribute at all.
2. `test_visual_equivalence_does_not_imply_authority_equivalence` —
   `E(x_{A=0}) == E(x_{A=1})`, therefore `D(x) ⊬ A(x)`: the Universal
   Anti-Collapse Signature expressed directly in the codec.

Plus: full round-trip sweep over every *legal* visual tuple, arity
enforcement, near-miss symbol rejection (🟩 is not 🟢), determinism.

## Scope of the earned claim

For the tested WUL-Core state space, the codec preserves the declared
visual projection and rejects the enumerated semantic collisions. It does
**not** claim universal Unicode transport safety, impossibility of all
WUL-Garden injections, or kernel safety — that is E-WUL-008 and the
runtime capability layer, which remain separate and unbuilt.

```text
🧬 τ φ w a p → 🎨 φ|τ|w → 🔁 τ φ w
✨ ⊬ 👑 · 🟢⚖️ ⊬ 🔑 · 🌿 ↛ ⬡
STATUS: CODEC WITNESSED · AUTHORITY: DENY · LEDGER_EFFECT: NONE
```
