# HELEN_OS_METAVERSE_DUO — paired scene template

Canonical "duo poster" prompt for HELEN + her digital twin in the metaverse scene.
Used by `paired_render()` as one of `HelenDualIdentity.paired_scene_templates`.

Operator-authored 2026-04-20. Use as the first validation target for dual-canonical
(§14 of math_to_face/SKILL.md) before extending to video.

---

## Canonical prompt

```
Ultra-realistic cinematic key art poster, vertical 4:5.

SCENE:
Inside a neon cyber corridor / metaverse control room, holographic circuitry,
teal + purple glow, high-end sci-fi.

CHARACTERS (two versions of the same identity):
LEFT: HELEN_REAL — photorealistic young woman, red/orange hair, freckles,
bright eyes, friendly smile.
Outfit: white fitted tank with big readable text "HELEN", orange/blue shorts,
subtle jewelry.

RIGHT: HELEN_TWIN — her anime/manga digital twin, same identity cues (matching
hair color, eye color, freckles pattern stylized), cute confident smile.
Outfit: black hoodie with readable text "HELEN OS", short skirt, cat-ear hoodie
or headset (optional).

BACKGROUND CENTER:
A large glowing holographic android/AI silhouette with chest text "HELEN OS"
(readable).

Bottom caption strip: "inside HELEN OS METAVERSE" (readable, no typos).

CRITICAL:
Identity pairing must be obvious: both are the same person in different render
modes.
No face distortion, no extra fingers, no brand logos, no corrupted text.
High detail, sharp focus, cinematic lighting, clean composition.
```

## Negative prompt (generator-dependent)

```
no misspelled text, no warped faces, no extra limbs, no nudity, no gore,
no real brand logos, no blurry faces
```

## Acceptance criteria (gates per §14.3)

- Left crop face passes REAL anchor gate: `passes_identity_gate(I_real_crop, dual.real, arcface_real)`
- Right crop face passes TWIN anchor gate: `passes_identity_gate(I_twin_crop, dual.twin, arcface_twin_or_clip)`
- Hair color + freckles presence verifiable via simple detectors (color histogram, feature-point detector)
- Text "HELEN" (left tank), "HELEN OS" (right hoodie + silhouette chest), "inside HELEN OS METAVERSE" (caption) all readable — no corrupted glyphs
- Composition: balanced duo with center silhouette, not three-shot chaos

## 3×3 grid extension (9-mood variant)

For a poster that shows the pair across the full Ekman-7 + 2 bonus emotions:

- 3 rows × 3 cols = 9 panels
- Each panel: same scene template, same two characters, one emotion per panel
- Candidate mood list: `{neutral, joy, surprise, wonder, melancholy, determination, fear, anger, serenity}`
- Per panel: both REAL + TWIN express the same emotion consistently

Useful as:
- Launch poster
- Identity stability benchmark across emotional axis (cheap alternative to full video test §13 for a first-pass check)
- Failure map indicator — if one mood panel fails identity gate on either side, that's a drift hotspot to debug

## Operational notes

- When using helen-director (Seedance rental) as the backend: generate two separate renders with operator-curated prompts per side, composite post-hoc. Not truly dual-canonical (no shared z) but an acceptable prototype.
- When using math_to_face (sovereign): `paired_render()` with shared `z = H(m)` + two generator profiles. This is the real dual-canonical — identity invariance guaranteed at latent level, not via prompt matching.
- First validation: produce ONE still poster at acceptable quality per both gates. THEN extend to 3×3 grid. THEN extend to video per §13.
