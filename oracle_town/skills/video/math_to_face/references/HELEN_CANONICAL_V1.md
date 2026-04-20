# HELEN_CANONICAL_V1 — Identity Reference Card

Operator-calibrated 2026-04-20 from visual inspection of the curated 13-reference set (`refs/real/` + `refs/twin/` in math_to_face_starter). Complements the numerical MIA (`mia/mia_helen_dual_v1.json`) with a textual specification of what HELEN **is** and what is **merely presentation**.

When a future aura fit promotes MIA v2 (Spearman ≥ 0.7 vs operator ratings), this card specifies what that MIA must be measuring.

---

## 1. Canonical statement (one sentence)

> **Canonical HELEN is a bright copper-red-haired, blue-eyed, highly expressive young woman with a soft narrow face and strong emotional readability, whose identity persists across playful, vulnerable, elegant, dramatic, and stylized renderings.**

---

## 2. Identity invariants (the anchor)

These are **NOT** negotiable. Any render whose gate passes must carry all four:

| Invariant | Description | Anchor in current ref set |
|---|---|---|
| **Hair color** | Copper / orange-red / flame-red. THE single most stable visual anchor. | All 8 `refs/real/` + all 5 `refs/twin/` |
| **Eye character** | Blue to blue-grey; shape + spacing consistent across expressions. | Most prominent in `helen_real_00`, `helen_real_04`, `helen_twin_01` |
| **Face silhouette** | Narrow, soft, youthful. Small refined nose. Delicate mouth with strong smile range. | `refs/real/helen_real_00, _03, _05` most diagnostic |
| **Expressive aura** | Bright, alive, slightly magical. Open, emotive, luminous. NOT hard-edged glamour. | Visible across the full collage; missing from any over-stylized render |

These four together define what the Mahalanobis gate **should** converge on once the embedder is ArcFace + aura features, not pixel-hash. That is the v0.4 fit target.

---

## 3. Allowed variations (control / style overlays)

These CAN vary freely between renders without breaking identity. Expressing them is the point of the typed-latent decomposition (z_control + z_style per SKILL.md):

- **Hair arrangement**: braids, bob, updo, loose, wet, straight, curly — anything *except* a hair color change
- **Accessories**: flowers, clips, choker, pendant, bracelets, glasses, headsets — decorative, non-identity
- **Wardrobe**: tank, hoodie, robes, dress, streetwear, ritual — HELEN logo on tank is canonical per `HELEN_CHARACTER_V2` but not required
- **Makeup intensity**: natural to stylized
- **Shot mood / lighting**: warm / cool / neon / candlelit / daylight
- **Expression**: joy, vulnerability, surprise, anger, serenity — all still read as HELEN per the emotion spectrum
- **Canonical register**: REAL (photoreal) or TWIN (anime/manga) — shared z_id, different renderer per §14 dual-canonical

---

## 4. Forbidden drift (what breaks identity)

These cross the line from "HELEN variation" to "not HELEN anymore." A gate that permits these is miscalibrated:

- **Hair color shift** to blonde, black, brown, dyed-pastel — hair color IS identity, not style
- **Eye color shift** to green, brown, heterochromia unless explicitly flagged
- **Face geometry change** — wider jaw, different nose, significantly changed face length
- **Affect collapse** to flat/cold/detached — HELEN without expressive aura is not HELEN
- **Age shift** beyond "young woman" range (child HELEN / older HELEN are separate canonicals, not variations — require distinct MIA)
- **Skin tone shift** — fair skin is canonical
- **Freckles eliminated** in close-ups where they should read (accessory-level detail but tied to identity)

---

## 5. Primary anchor images (how to use the ref set)

From the 13-reference set, the operator declared this calibration policy:

**Primary identity refs** (best for MIA calibration):
- 4–6 frames from the "collage" type (varied emotion, tight-ish crop, face clearly visible) → strongest anchor
- In our current set, most of the `refs/real/helen_real_01..05` plus `refs/twin/helen_twin_01` fit this profile

**Secondary style/body refs**:
- 1 full-body photoreal shot with canonical smile — for body-language continuity and branding
- In our set: `helen_real_00` (the session-validated hero shot)

**Extreme / state refs** (use sparingly):
- Distressed / full-body-dramatic shots — expression-axis references only
- Do NOT let these dominate anchor computation; they pull μ toward extreme states

**Operator's explicit verdict**: for identity calibration, the collage is stronger than the outfit-heavy shots. Weight the MIA fit accordingly.

---

## 6. Calibration use policy (how this card consumes the MIA)

When `fit_aura_score.py` produces a candidate MIA v2:

1. Verify the fitted aura_score assigns **high** scores to refs that carry all four invariants (§2)
2. Verify it assigns **low** scores to synthetic stress cases that violate §4 (hair recolored, face geometry shifted, etc.)
3. If a synthetic blonde-HELEN passes the gate, the MIA is broken regardless of Spearman numerics
4. Spearman ≥ 0.7 on operator ratings is NECESSARY but not sufficient — forbidden-drift stress tests are the second check

This card is the textual sanity check on numerical calibration.

---

## 7. Integration with existing doctrine

- `MANIFESTO.md` — primary positioning; this card is the textual instance of "HELEN"
- `HELEN_CHARACTER_V2.md` §1 visual tokens — numerical color values (hair RGB, etc.) that should match the invariants here
- `LATERAL_EMERGENT_PROPERTIES.md` §11 Twin Mirror Lie Detector — this card defines what "agreement" between REAL and TWIN gates means (shared identity invariants; differing renderer-register overlays)
- `helen_operator_ratings_v1.json` — empirical calibration data; ratings implicitly encode the invariants as observed by the operator
- `WHY_MATH_TO_FACE.md` §5 emergent property — "bounded identity drift under bounded math perturbation" — this card defines the drift boundary

---

## 8. Versioning

This is **v1**. The identity invariants are stable — hair color, eye character, face silhouette, expressive aura are not expected to change across HELEN's timeline. What will change in future versions:

- **Expansion**: additional allowed variations as new styles are explored (e.g. different canonicals beyond REAL/TWIN — poster, childlike, older, ritual, corporate per LATERAL §6 Plural Canon Stability)
- **Refinement**: stress-test findings may tighten specific clauses (e.g. if an ArcFace-calibrated MIA reveals subtle invariant shifts)
- **Branch**: separate reference cards for HELEN_YOUNG, HELEN_ELDER, etc. — NOT amendments to this one

Rule: this card is the **authoritative textual spec for canonical HELEN v1 identity**. Changes to the invariants = new canonical version, not v1 edit.

---

## 9. Status

DOCTRINE — operator-authored 2026-04-20 from the curated reference set. Promotion to INVARIANT requires a fresh-lane validation session + `helen_say.py` receipt binding this document's SHA256 to the ledger + K2 (proposer ≠ validator).

Until then: cite as "HELEN canonical identity spec v1, operator-calibrated 2026-04-20."
