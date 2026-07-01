# HELEN Math Garden Epoch Generator

Generate bounded mathematical research epochs with deterministic proof hashes.

## Inputs

$ARGUMENTS — theme and epoch range. Example: "drift M081-M090", "fiber M091-M100", "all M081-M160".

## Recipe

1. **Theme selection** from the 9-theme palette:
   - `ledger_algebra` — hash-chain, append-only, seq arithmetic
   - `universal_property` — UMP-style characterization of governance objects
   - `drift` — premetric Δ over projections, guard≡doc checks
   - `projection_category` — category of observation maps, functoriality
   - `fixed_points` — Knaster-Tarski style on governance lattices
   - `closure` — Kuratowski closure on status sets
   - `fiber_bundles` — fiber structure of observation maps
   - `representation` — functorial embeddings of governance into Set
   - `completeness` — directed-completeness, chain conditions

2. **Per epoch** (one hypothesis each, PULL-mode):
   - State the hypothesis as a single falsifiable mathematical claim
   - Write the proof or construction (finite, bounded, no quantifiers over unbounded classes)
   - Compute deterministic proof hash: `sha256(epoch_id | theme | hypothesis)`
   - Record outcome: VERIFIED / FALSIFIED / OPEN
   - If FALSIFIED: state the counterexample explicitly

3. **Batch receipt**: Record total epochs, pass/fail counts, actual errors (never hardcode PASS).

4. **Forbidden terms scan**: Flag any epoch containing "energy", "vibration", "consciousness", "manifest" (pseudoscience guard).

5. **Output**: Write epoch files to `temple/gardens/math_garden/epochs/` with frontmatter:
   ```yaml
   status: PROPOSED
   authority: false
   canon: false
   ```

## Constraints

- NON_SOVEREIGN, NO_SHIP — sandbox only.
- No quantifiers over unbounded classes (structurally doomed per GOBLIN-2 finding).
- Deterministic: no wall-clock time in hashes.
- Bounded: max 20 epochs per loop iteration.

## Loop Engineering (Fable)

```
for theme in themes:
    epochs += math_garden(theme, next_range)
    rank(epochs, by="mechanization_feasibility")
```
Best candidates from each run feed into the next mechanization tranche (AR-DRIFT-001 is the template).
