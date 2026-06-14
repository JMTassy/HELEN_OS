# HELEN Autoresearch — 200 Epochs Report

**authority: NONE · NON_SOVEREIGN · NO_SHIP · SANDBOX_ONLY**

epochs_run     : 200
head_sha       : 3c9e88fd2eb5d3d8...
elapsed        : 1018.39s
sovereign_safe : True

## Obsidian Mirror — Attractor Map

| Rank | Concept | Confirmed | Weak | Absent | Lineage Pressure | Top Sources |
|---|---|---|---|---|---|---|
| 1 | 🟡 **REPLAY** | 13 | 0 | 7 | 0.6500 |  |
| 2 | 🟡 **DETERMINISM** | 13 | 0 | 7 | 0.6500 |  |
| 3 | 🟡 **PROVENANCE** | 11 | 1 | 8 | 0.5750 |  |
| 4 | 🟡 **GOVERNANCE** | 11 | 1 | 8 | 0.5750 |  |
| 5 | 🟡 **ADMISSION** | 10 | 3 | 7 | 0.5750 |  |
| 6 | 🟡 **IDENTITY** | 9 | 4 | 7 | 0.5500 |  |
| 7 | 🟡 **WITNESS** | 9 | 2 | 9 | 0.5000 |  |
| 8 | ⚪ **COUPLING** | 8 | 1 | 11 | 0.4250 |  |
| 9 | ⚪ **RECONSTRUCTION** | 4 | 4 | 12 | 0.3000 |  |
| 10 | ⚪ **COMPRESSION** | 3 | 3 | 14 | 0.2250 |  |

## Interpretation

**Lineage pressure** = (confirmed + 0.5 × weak) / total_probes
- ≥ 0.80: Strong attractor — concept recurs across multiple corpus dimensions
- 0.50–0.79: Moderate attractor — present but unevenly distributed
- < 0.50: Weak or context-specific — not a corpus-level attractor

## Gate Performance

Receipts with gate_total = 1.0: 200 / 200
Receipts with gate failure:     0

## Honest Boundary

1. **Frequency ≠ importance.** High lineage_pressure means the concept appears
   often in the corpus — not that it is philosophically primary.
2. **Coupling probes are shallow.** Co-occurrence in the same file ≠ causal link.
3. **ABSENT does not mean irrelevant.** A concept may be real but named differently.
4. **This map is NON_SOVEREIGN.** It is a candidate input for doctrine delta,
   not doctrine itself. MAYOR routing required before any doctrine update.
5. **Gate K5 (contradiction scan) is structural only.** Semantic contradictions
   are not detected — requires reducer/human oracle (same gap as T5).

## Doctrine Delta Candidates

The following concepts have lineage_pressure ≥ 0.80 and are candidate inputs
for doctrine delta (subject to MAYOR routing and receipt admission):


## Next Frontier (T7)

T6 established temporal opacity as the dominant provenance gap.
T7 candidate: content-hash staleness — verify artifact SHA on disk
matches the SHA recorded in the provenance sidecar.
epistemic_taxonomy_probe.py already walks paths; SHA check is one field away.