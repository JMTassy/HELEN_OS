# BEAD-TEMPLE-CONSERVED-FORM-001

```
type:           BEAD (local experiment)
authority:      false
canon:          false
ledger_effect:  none
claim_status:   LOCAL_OBSERVATION
parent:         docs/proposals/TEMPLE_CONSERVED_FORM_V0.md ·
                docs/proposals/SIGIL_FORM_COMPILER_V0.md
date:           2026-08-04
location:       temple/subsandbox/ — never sovereign, never auto-promoted
```

HELEN OS — created by JM Tassy.

Source phrase: `SHAPE IS SOUND` under `MAPPING_V1` (5×5 grid, J→I merge,
Chebyshev-interval rhythm). All mapping choices are declared modern
interpretation.

## Files

- `bead_compiler.py` — deterministic compiler: source → S=(M,N,C,G,R,P) →
  trace2D / voxel / rhythm projections, all sha256-fingerprinted, emitted
  as a TEMPLE replay packet (NOT a kernel receipt)
- `test_bead_001.py` — the four conservation laws + independent
  reproduction + ambiguity-log + constitutional-flag checks
- `renders/BEAD-TEMPLE-CONSERVED-FORM-001.replay.json` — generated packet

## Run

```bash
.venv/bin/pytest temple/subsandbox/conserved_form/ -v
.venv/bin/python temple/subsandbox/conserved_form/bead_compiler.py "SHAPE IS SOUND"
```

## What a green run proves — and does not

Proves: the transformation chain conserves structure across the three
projections; a single altered symbol produces a localized, not smeared,
downstream difference; the pipeline is deterministic (byte-identical
packets, no wall-clock, no randomness).

Does not prove: historical intention, cross-tradition transmission, any
cosmology, or admissibility. Intermodal agreement = projection fidelity,
not metaphysical truth.
