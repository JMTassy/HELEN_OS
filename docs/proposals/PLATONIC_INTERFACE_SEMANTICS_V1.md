# PLATONIC_INTERFACE_SEMANTICS_V1

**Status**: DRAFT_V0
**Authority**: NON_SOVEREIGN
**Canon**: NO_SHIP
**Discipline**: APPEND_ONLY
**Date**: 2026-05-15
**Bound to**: `temple/platonic_solids.html`

---

## §1. Intent

The five Platonic solids are not decoration. They are a constitutional control
cosmogram for HELEN OS — a visible grammar that says, in geometry, what each
layer of the runtime is, what authority it holds, and what it must never
impersonate.

This doctrine fixes the mapping so that the visual surface cannot drift from
the constitution.

---

## §2. The Five Solids

| Solid          | Faces | Module                          | Role                                   |
| -------------- | ----- | ------------------------------- | -------------------------------------- |
| Tetrahedron    | 4     | **KERNEL**                      | Sovereign law (truth/identity/ledger)  |
| Cube           | 6     | **MEMORY FABRIC**               | Continuity without authority           |
| Octahedron     | 8     | **HAL / EVALUATOR**             | Admissibility through balance          |
| Icosahedron    | 20    | **CONQUEST / SWARM**            | Bounded exploration                    |
| Dodecahedron   | 12    | **AURA / SYMBOLIC SHELL**       | Symbolic coherence (no authority)      |

Each solid says three things:
- **what kind of thing this layer is**
- **what authority it has**
- **what it must never impersonate**

---

## §3. The Inversion Principle

> **The Kernel has the smallest solid and the highest authority.
> AURA has the most ornamental solid and the lowest authority.**

This reversal is the entire doctrine in visual form:

```
authority ↑  ←—————————————————————————  ornament ↓
KERNEL (4F)   MEMORY (6F)   HAL (8F)   AURA (12F)   CONQUEST (20F)
```

The eye reads this immediately: **austerity carries law, ornament carries
meaning, and the two must never trade places.**

If AURA's beauty ever signs a verdict, the doctrine is broken.
If the Kernel ever decorates itself, the doctrine is broken.

---

## §4. Color Language

Each solid has a hue tuned to its authority class:

| Module      | Color           | Hex       | Reason                                     |
| ----------- | --------------- | --------- | ------------------------------------------ |
| KERNEL      | sovereign gold  | `#e8c870` | law radiates; smallest body, brightest hue |
| MEMORY      | archival blue   | `#4a8fcc` | calm, deep, storage hue                    |
| HAL         | verdict red     | `#d04040` | opposition, judgment, gate-fire            |
| CONQUEST    | growth green    | `#5fa872` | living exploration, adaptive reach         |
| AURA        | cosmic violet   | `#9c70d4` | symbolic mystery, ceremonial               |

The KERNEL's gold is doctrinally distinct from AURA's violet: gold is the
**law-color of sovereignty**; violet is the **shell-color of meaning**. They
must not be confused on any surface.

---

## §5. Motion Language

### Rotation (drag or auto-spin)

Rotation means: **the same constitutional object can be inspected from
multiple perspectives without changing its identity**.

- perspective may change
- invariant remains

Rotation is not play. It is the visible promise of replay determinism: rotate
the tetrahedron 1000 times and it is still the tetrahedron. The Kernel does
not become something else under inspection.

### Transition (switching solids)

Solids **do not morph into each other**. A vertex-interpolation between
non-homologous solids would lie: it would suggest the Kernel can become
Memory, or HAL can become AURA. **This is false.**

Transitions are **crossfades only**: one solid fades out, the next fades in.
The user is not transforming the runtime; the user is shifting attention.

### Keys 1–5

The number keys do not switch shapes. They switch **constitutional
attention**:

- `1` KERNEL — attend to law
- `2` MEMORY — attend to continuity
- `3` HAL — attend to admissibility
- `4` CONQUEST — attend to exploration
- `5` AURA — attend to meaning

---

## §6. Hover Contracts

Each solid carries a one-line constitutional contract, surfaced on hover:

| Solid       | Hover contract                                                          |
| ----------- | ----------------------------------------------------------------------- |
| KERNEL      | "Irreducible. The kernel signs alone. NO RECEIPT = NO CLAIM."           |
| MEMORY      | "Addressable. Continuity without authority. Recall is not law."         |
| HAL         | "Balanced. Admissibility through opposition. PASS or BLOCK."            |
| CONQUEST    | "Faceted. Bounded exploration. Reach without losing the center."        |
| AURA        | "Cosmic. Symbolic coherence. Feeling without becoming law."             |

---

## §7. Transition Semantics

| From → To           | Meaning                                                  |
| ------------------- | -------------------------------------------------------- |
| AURA → KERNEL       | Symbol surrenders to law                                 |
| KERNEL → MEMORY     | Law writes into continuity                               |
| MEMORY → HAL        | Continuity submits for judgment                          |
| HAL → CONQUEST      | Verdict licenses exploration                             |
| CONQUEST → AURA     | Discovery returns as symbol                              |

The cycle `KERNEL → MEMORY → HAL → CONQUEST → AURA → KERNEL` is the full
constitutional loop: law writes memory, memory faces judgment, verdict
licenses search, search yields symbol, symbol returns to law.

---

## §8. Constraints

- **No solid may sign verdicts.** Only the MAYOR signs (and only through the
  KERNEL solid's authority — never the AURA solid's beauty).
- **No solid may be rendered with the wrong color.** The color language is
  part of the law.
- **No solid may morph (vertex-interpolate) into another.** Only crossfade.
- **AURA is the most beautiful and the least authoritative.** This is
  doctrinal and non-negotiable.
- **The KERNEL solid must never gain visual ornament.** No glow stronger than
  Memory's, no animation richer than HAL's. Austerity is its signature.

---

## §9. Bound Surfaces

- `temple/platonic_solids.html` — canonical visual implementation
- `oracle_town/skills/helen_constitutional_grounding/` — output-side gate
  (analogous to HAL, octahedral)
- `oracle_town/skills/helen_retrieval/` — input-side retrieval
  (analogous to MEMORY, cubic)

---

## §10. Admission Sidecar

When/if REDUCER admits this doctrine, the following sidecar binds it:

```
sha256: <pending>
test_pointer: tests/test_platonic_interface_semantics_v1.py
proposer: HER
attestor: REDUCER (pending)
ledger_receipt: <pending>
```

Until then: DRAFT_V0, NO_SHIP, APPEND_ONLY proposal.

---

## §12. Atlas View

The canonical landing surface is the **atlas**: all five solids visible
simultaneously in fixed positions.

```
       MEMORY              HAL
       (cube)         (octahedron)

                  KERNEL
              (tetrahedron)
              small · centered
                · gold ·

      CONQUEST              AURA
   (icosahedron)       (dodecahedron)
```

- **KERNEL is centered and smallest.** The inversion principle is visible:
  the body with the highest authority occupies the least space.
- All solids share a common rotation. The user rotates the entire
  constitution; each form is seen from the same perspective at all times.
  This is the visible form of replay determinism.
- **Click a solid → enter focus mode.** A single solid expands to fill the
  view; the user inspects one constitutional aspect in depth.
- **ESC or click outside → return to atlas.** The whole constitution
  reappears, intact.

### Canonical taglines

- Header: **"PERSPECTIVE CAN ROTATE. LAW REMAINS INVARIANT."**
- Footer: **"FIVE FORMS. ONE LAW."**

These are doctrinal. They state the motion grammar (§5) and the unity
principle (§2) in one line each.

---

## §13. Why this matters

Most interfaces show **functions**.
This one shows **orders of reality** inside the runtime.

A user looking at HELEN OS does not need to read documentation to know:
- the Kernel is law because it is small and sharp
- AURA is meaning because it is rich and warm
- HAL is judgment because it is balanced and red
- Memory is continuity because it is stackable and blue
- Conquest is search because it has the most facets

The geometry is the grammar. The grammar is the constitution.
