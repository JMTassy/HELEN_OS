# HELEN Language Layers — Translation Doctrine (v1, DRAFT)

NO CLAIM — NO SHIP — PROPOSAL ONLY — NON_SOVEREIGN TRANSLATION DOCTRINE

```
artifact_type:         PROPOSAL_DOCTRINE
proposal_id:           HELEN_LANGUAGE_LAYERS_V1
status:                DRAFT_V1
authority:             NON_SOVEREIGN
canon:                 NO_SHIP
lifecycle:             PROPOSAL
implementation_status: PRINCIPLE_ONLY
memory_class:          TRANSLATION_DOCTRINE
captured_on:           2026-05-10
captured_by:           operator (Jean-Marie Tassy) via HER witness
provenance:            HER verdict (2026-05-10);
                       9.2/10 render evidence — surface chips show
                       "saved · local draft", "linked · STARSHIP_V3",
                       "auth: false · demo" in human vocabulary;
                       operator language directive in HELEN2027 polish pass.
related_artifacts:     HELEN_SURFACE_DOCTRINE_V1.md (parent doctrine §1)
                       HYPERSTITION_FIREWALL_V0.md (sibling, render-poison)
                       HELEN_LAYERED_CANON_V1.md (sibling)
growth_rule:           APPEND-ONLY. Mappings may be added below §3.
                       Mappings cannot be silently changed — only deprecated
                       (with a successor mapping and migration note).
```

> **HER verdict (2026-05-10), recorded as proposal:**
>
> > Humans live in language. HELEN must speak both registers:
> > the human one ("saved", "linked", "verified") and the
> > constitutional one ("receipt", "claim", "provenance").
> > Both vocabularies are sovereign in their domain.
> > Translation must be lossless.

---

## §1 — Principle

HELEN operates with **two coexistent vocabularies**:

| Layer            | Purpose                                            | Where it surfaces        |
|------------------|----------------------------------------------------|--------------------------|
| Surface (human)  | Reduce cognitive load. Carry meaning, not schema.  | HOME, COCKPIT, TEMPLE    |
| Constitutional   | Encode integrity. Carry provable structure.        | PILOT, LEDGER, kernel    |

The vocabularies **map 1:1**. Every constitutional concept has exactly one canonical human label; every human label refers to exactly one constitutional concept. No information is lost in translation; only register changes.

**Why two layers?** A single layer fails one of two audiences:

- A pure-constitutional surface ("receipt minted, claim unverified, MAYOR NO_SHIP") creates cognitive load for non-technical operators and visitors.
- A pure-human surface ("saved", "waiting") loses provenance information that the kernel, ledger, and gates require.

Both audiences are real. Both layers are required. The 1:1 mapping prevents drift.

---

## §2 — The Mapping Table

This is the canonical mapping. Renderers translate at the surface boundary.

| Surface (human) | Constitutional (kernel)         | Notes                                        |
|-----------------|---------------------------------|----------------------------------------------|
| `saved`         | `receipt:committed`             | Action produced a hash-chained ledger entry  |
| `linked`        | `relation:bound`                | Object references another canonical object  |
| `verified`      | `claim:verified`                | Claim has passed K-tau and HAL checks        |
| `done`          | `task:closed_with_receipt`      | Task terminated cleanly; receipt minted      |
| `waiting`       | `task:awaiting_external_input`  | Bounded executor parked on external signal   |
| `blocked`       | `task:hal_or_mayor_hold`        | HAL flagged or MAYOR ruled HOLD              |
| `draft`         | `proposal:unadmitted`           | Artifact exists; not registered in registry  |

### §2.1 Constitutional-only vocabulary (no surface equivalent)

These constitutional concepts have no human-layer label because they only matter at the kernel boundary. They never appear on HOME.

```
cum_hash · payload_hash · K8 · K-tau · K-rho · K-wul
LEGORACLE · kernel_guard · ndjson_writer · schema_registry
```

If a surface needs to surface these (e.g., debugging view), it must do so explicitly under PILOT or LEDGER mode and label them as constitutional vocabulary.

### §2.2 Surface-only vocabulary (no constitutional equivalent)

These human-layer labels carry affective or ergonomic information that the kernel does not encode. They live entirely in the render layer.

```
calm · focused · alert · best next move · breathing · gentle
```

These never enter the ledger. They are HER's vocabulary — relational, not constitutional.

---

## §3 — Translation Rules

### §3.1 Where translation happens

Translation happens at exactly one boundary: the **render layer**. The kernel speaks constitutional. The surface speaks human. The translator is the render code.

```
kernel (constitutional)
   ↓ render translates ↓
surface (human)
   ↑ submit reverses ↑
kernel (constitutional)
```

### §3.2 Translation must be reversible

If a HOME surface shows "saved" and the operator wants to see the receipt hash, the translation back to `receipt:committed:sha256:...` must be deterministic and instant. The mapping is bijective; the render preserves the constitutional identifier in a data attribute, hover tooltip, or detail card field.

### §3.3 Translation must not silently lose context

If a constitutional concept has no human equivalent (§2.1), and a HOME render needs to display the task, the render MUST either:

- (a) Suppress the constitutional concept (acceptable for HOME — keeps cognitive load low)
- (b) Show it explicitly as constitutional vocabulary (acceptable in COCKPIT or PILOT)

What it MUST NOT do: invent a human-layer term that approximates the constitutional one. That breaks 1:1.

### §3.4 New terms require both layers

Introducing a new surface term requires its constitutional counterpart. Introducing a new constitutional term requires its surface counterpart (or explicit §2.1 declaration). Asymmetric introductions are forbidden — they cause exactly the drift this doctrine prevents.

---

## §4 — Schema Implications

Every schema authored under `HELEN_SURFACE_DOCTRINE_V1` must carry both layers:

```json
{
  "id": "constitutional_identifier",
  "surface_label": "human_word",
  ...
}
```

The render reads `surface_label` for HOME/COCKPIT/TEMPLE. The kernel reads `id` for all gate logic. Both are required; neither is decorative.

Concrete examples to be authored in later epochs:

```json
// HELEN_HOTSPOT_TYPES_V1 (proposed in surface doctrine §3.3)
{ "id": "claim",      "surface_label": "claim",     ... }
{ "id": "receipt",    "surface_label": "saved",     ... }
{ "id": "provenance", "surface_label": "source",    ... }
{ "id": "risk",       "surface_label": "concern",   ... }
```

Note the mapping is NOT always identity — `receipt` becomes `saved`, `provenance` becomes `source`. The human layer optimizes for ergonomics, not for matching the constitutional name.

---

## §5 — Open Questions

### §5.Q1 — Color as language

The 9.2/10 render uses subtle color (amber for in-progress, soft red for blocked, mid-gray for waiting). Is color part of the language layer? If so, the mapping needs a color column. If not, color is style-only and varies by surface.

Recommendation: color belongs to the rendering style guide, not the language layer. Different surfaces (light HOME vs dark PILOT) will use different palettes for the same constitutional state. Color is therefore *not* part of the 1:1 mapping.

### §5.Q2 — Internationalization

The current mapping is English-only. Future surface localization (French, given operator Jean-Marie Tassy and the "Dreams of Conquest" landing page in French) needs an N:1 surface-label mapping per constitutional concept. That's a v2 extension, not v1.

### §5.Q3 — Affective vocabulary scope

`§2.2` lists `calm · focused · alert · best next move · breathing · gentle` as surface-only. Are there more? The list should grow as HER's vocabulary surfaces in renders.

---

## §6 — Provenance & Append-Only

### §6.1 Provenance

This mapping was extracted from:

- HELEN2027 polish-pass directive (operator, this conversation): explicit language rule listing `saved · linked · verified · done · waiting · blocked · draft` as the human layer and prohibiting "receipt-heavy" language on HOME
- 9.2/10 render screenshot showing actual chips on HOME (`saved · local draft`, `linked · STARSHIP_V3`)
- CLAUDE.md kernel vocabulary (`receipt`, `claim`, `provenance`, `MAYOR`, `HAL`, `NO_SHIP`)
- HER's witness role (preserves continuity; refuses to let mapping drift)

### §6.2 Append-only

Future mappings append to §2's table. To deprecate a mapping, add a row below with `(deprecated → new_label)` and explain the migration. Never silently change a row — the 1:1 invariant depends on stable references.

### §6.3 Reducer authority

DRAFT_V1. Becomes canon only when REDUCER admits via schema registry.

---

## §7 — Status Summary

```
DOCTRINE:        HELEN_LANGUAGE_LAYERS_V1
STATUS:          DRAFT_V1
AUTHORITY:       NON_SOVEREIGN
SHIP:            NO_SHIP
MAPPINGS:        7 surface↔constitutional pairs (§2)
                 + constitutional-only set (§2.1)
                 + surface-only set (§2.2)
OPEN_QUESTIONS:  3 (color, i18n, affective scope)
NEXT_EPOCH:      HYPERSTITION_FIREWALL_V0.md
NEXT_REDUCER:    operator confirmation or refinement
```
