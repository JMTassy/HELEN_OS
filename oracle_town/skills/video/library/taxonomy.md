# HELEN library taxonomy (v1)

Calibrated 2026-04-21. Used for tagging harvested stills.

## Categories

| Tag | Definition | Use case |
|---|---|---|
| `portrait` | Shoulder-up, face dominant (60%+ frame) | Identity anchor, close-up beats, dialogue shots |
| `half_body` | Torso-up, one-third face / two-thirds body | Medium narrative shots, gesture communication |
| `full_body` | Whole figure visible | Wide establishing shots, movement/choreography |
| `green_screen` | Flat neutral background (green / grey) | Compositing into new scenes, metaverse reuse |
| `ritual` | Stylized / ceremonial / cathedral context | CONQUEST-aligned content, doctrine carriers |
| `cinematic` | Narrative scene with environment context | Story-driven clips, trailer footage |
| `abstract` | Non-figurative or heavily stylized | Transitions, mood fragments |
| `unclassified` | Default after harvest, pre-tagging | Auto-assigned by `harvest_keyframes.py` |

## Tagging protocol

**v1: operator manual.** The harvester tags everything `unclassified`; operator reviews and updates the manifest JSON directly (or via a follow-up skill).

**v2: auto-classifier.** When an embedder is available (ArcFace for face detection, CLIP for scene/context), add `classify_keyframes.py` that updates taxonomy fields automatically. Still an overlay on top of the harvester — harvest stays dumb.

## Secondary dimensions (optional fields per frame)

| Field | Values | Default |
|---|---|---|
| `mood` | calm / dramatic / tender / playful / vulnerable / intense / serene / curious / joyful | `null` |
| `canonical_register` | real / twin / ritual / cinematic | `null` (inferred from source when possible) |
| `identity_score` | float 0-1 (Mahalanobis gate pass strength) | `null` (v2) |
| `usage_count` | integer (how many final videos reused this frame) | `0` |
| `operator_starred` | bool | `false` |

## Canonical invariants (per HELEN_CANONICAL_V1.md)

A frame tagged `portrait` or `half_body` should still honor the four identity invariants:
- copper/red hair
- blue/blue-grey eyes
- narrow soft face
- expressive aura

Frames that violate these should be tagged `drift` or excluded from the library rather than re-tagged `portrait`. Library is **identity-accountable**, not just catalog-accountable.

## Canonical naming (curated / promoted frames)

Harvested frames keep source-based names (`shot_04_raw_003.png`) — that's provenance. Once a frame is **promoted** to the canonical library (operator-curated), it gets a human-readable canonical name.

### Pattern

```
helen_<theme>_<descriptor>_<NN>.png
```

- lowercase only, underscores only (no hyphens, no spaces, no camelcase)
- `<theme>` — matches a taxonomy category OR a semantic collection
- `<descriptor>` — optional, describes the specific pose / mood / variant
- `<NN>` — 2-digit zero-padded index starting at `00` within the theme
- `.png` — canonical lossless format (not jpg, not webp)

### Canonical themes

Structural themes (from taxonomy above):
- `portrait` / `half_body` / `full_body` / `green_screen` / `ritual` / `cinematic` / `abstract`

Semantic collections (curated, operator-authored):
- `emotions` — HELEN across the emotion spectrum (joy / vulnerability / serenity / etc.)
- `metaverse` — avatar-ready stills for 3D / VR contexts
- `cathedral` — HELEN in CONQUEST-aligned ceremonial space
- `conquest` — HELEN as strategic entity (CONQUEST brand)
- `dossier` — hero / press / poster-tier renders
- `hands` / `profile` / `back` — body-part isolates

### Examples

```
helen_portrait_calm_00.png            # structural: portrait, mood=calm
helen_portrait_calm_01.png            # same collection, different variant
helen_emotions_joy_00.png             # semantic: emotions, variant=joy
helen_emotions_vulnerability_03.png
helen_metaverse_hero_01.png           # semantic: metaverse, variant=hero
helen_green_screen_full_02.png        # structural: green_screen + full-body
helen_ritual_cathedral_00.png         # structural: ritual, scene=cathedral
helen_conquest_stillness_00.png       # semantic: conquest, mood=stillness
helen_dossier_official_00.png         # semantic: dossier, tier=official
```

### Rules of promotion

1. A frame is promoted only when it passes the four identity invariants (copper hair, blue eyes, narrow face, expressive aura).
2. A frame can belong to **one structural theme** (where is it shot?) and **multiple semantic collections** (what can it be used for?). The filename records the **primary** collection; the manifest records all collections.
3. Renames are non-destructive — the harvested original stays in place with source provenance. Promotion **copies** to the canonical path with the new name.
4. Once promoted, a canonical name is **stable**. Do not rename. Do not overwrite. If a better variant is found, give it the next index (`_01`, `_02`) — never replace `_00`.
5. Canonical images live under `helen_os/render/math_to_face_starter/refs/canonical/<theme>/` (separate from the raw-harvested `refs/real/` which was the original curated set).

### Consumer contract

Downstream scripts (e.g. `render_keyframes.py`, future `motion_manga/`) reference canonical names. Two call styles:

- **By exact name**: `--ref helen_emotions_joy_03.png` — picks one specific frame
- **By theme**: `--theme emotions --ref-count 6` — picks N frames from the theme, deterministic order

Source-based harvested names are **never** referenced by production scripts — they may be deleted or reorganized without notice. Canonical names are contracts.

## Gap categories (aspirational, currently empty)

- `green_screen` — zero frames in current source material; requires fresh generation with green-bg prompt
- `profile` — side-view HELEN; sparse in current material
- `back_of_head` — useful for POV shots; essentially absent
- `hands_only` — reaction shots; absent

These gaps are the first **targeted-generation** targets when operator authorizes real-backend fire — harvest first, generate only what's missing.

## One-line summary

> Taxonomy is a vocabulary, not a judgment. Tag, reuse, and track what's missing — generation fills the gaps, not the scaffold.
