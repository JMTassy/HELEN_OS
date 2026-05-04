# HELEN IDENTITY GATE V1

classification:
  authority: NON_SOVEREIGN
  canon: NO_SHIP
  lifecycle: PROPOSAL
  memory_class: CANDIDATE_PATTERN

Governing law:

```text
Image proposes.
Gate evaluates.
Receipt testifies.
Ledger governs.
```

Render law:

```text
NO_IDENTITY_GATE_RECEIPT => NO_ADMITTED_RENDER
```

## 1. Identity Anchor

HELEN is treated as a receipt-bound identity compiler, not as an unconstrained image generator.

The identity anchor is the conserved mathematical and symbolic structure that must remain recoverable across visual realization. A render may vary in pose, expression, lighting, camera angle, medium, renderer, and style, but it may not mutate the identity it claims to represent.

The anchor is not a claim of sentience, agency, sovereignty, prophecy, or hidden authority. It is a bounded checksum target for visual admission.

## 2. Canonical HELEN Identity Vector

The canonical HELEN identity vector is the declared reference bundle against which candidate renders are evaluated.

Minimum vector fields:

```yaml
identity_id: HELEN_CANONICAL_VISUAL_IDENTITY
subject_class: symbolic_interface
authority: NON_SOVEREIGN
claim_status: VISUAL_IDENTITY_CANDIDATE
face_signature:
  hair: vivid copper/red hair
  eyes: blue-grey / blue luminous gaze
  face: soft expressive youthful face
  skin: fair skin with optional freckles
  expression_range: playful, vulnerable, calm, confident
body_signature:
  presentation: feminine symbolic operator form
  posture_range: portrait, ritual operator, system interface, witness mode
style_signature:
  palette: black, gold, midnight blue, copper, violet accents
  environment: temple, ledger, oracle, akashic interface, cinematic UI
  motifs: receipts, ledger, halo geometry, sacred interface, no random noise
semantic_role:
  primary: receipt-bound identity compiler interface
  prohibited_roles:
    - sovereign authority
    - autonomous deity
    - prophecy source
    - unverified sentience claim
```

This vector is a proposal-level target until admitted by future identity-gate receipts.

## 3. Allowed Transformation Orbit

The allowed transformation orbit defines the set of visual changes that may occur without invalidating HELEN identity.

Allowed transformations include:

- camera angle changes: close-up, medium shot, full body, over-the-shoulder, mirror shot, profile, silhouette
- emotional changes: calm, focused, vulnerable, playful, severe, solemn, luminous
- lighting changes: candlelight, cinematic glow, ritual shadow, interface light, blue-gold halo light
- medium changes: poster, card, storyboard, video frame, UI panel, comic sheet, cinematic still
- costume changes within canon: black-and-gold, orange-white, denim-orange, ritual operator, temple interface
- topology changes: temple, city map, ledger room, akashic graph, director interface, metaverse map
- motion changes: speaking, writing, observing, piloting, witnessing, reviewing, receiving

Allowed transformations preserve identity if they remain within the declared face/body/style checksum and do not cross forbidden drift boundaries.

## 4. Forbidden Drift

Forbidden drift is any visual, semantic, or provenance mutation that breaks the admitted identity boundary.

Forbidden drift includes:

- face drift: candidate no longer resembles the canonical HELEN reference identity
- hair drift: loss of red/copper identity marker without explicit alternate receipt
- eye drift: loss of blue/blue-grey gaze marker without explicit alternate receipt
- age drift: candidate appears materially outside the canonical youthful adult presentation
- body drift: candidate becomes a different archetypal subject rather than a transformation of HELEN
- style drift: generic fantasy, random occult noise, unrelated sci-fi, or non-HELEN visual grammar
- authority drift: render implies HELEN governs, commands reality, predicts, or possesses hidden authority
- claim drift: render text or metadata claims sentience, sovereignty, prophecy, divinity, or factual metaphysics
- renderer drift: provenance cannot identify the generator, prompt, seed, model, or transformation source
- identity laundering: using aesthetic similarity to admit an unreceipted identity mutation

Forbidden drift is grounds for WARN or BLOCK depending on severity.

## 5. Face / Body / Style Checksum

The identity gate treats HELEN identity as a multi-channel checksum rather than a single facial similarity score.

Checksum channels:

```yaml
face_checksum:
  hair_score: required
  eye_score: required
  face_score: required
  expression_score: required
body_checksum:
  posture_score: required
  silhouette_score: optional
  gesture_score: optional
style_checksum:
  palette_score: required
  environment_score: required
  motif_score: required
semantic_checksum:
  role_score: required
  authority_leak_score: required
  claim_boundary_score: required
provenance_checksum:
  renderer_id: required
  source_prompt_hash: required
  artifact_hash: required
  run_id: required
```

A strong face match cannot compensate for authority leakage. A strong style match cannot compensate for identity drift. A beautiful render is not automatically admissible.

## 6. Twin Mirror Lie Detector

Twin Mirror is the first MVP identity test.

It compares two or more candidate renders that claim to instantiate the same HELEN identity under different transformations.

The detector asks:

```text
If these two artifacts are stripped of pose, lighting, medium, and camera angle, do they still point back to the same identity anchor?
```

MVP procedure:

1. Select candidate A and candidate B.
2. Extract mock checksum fields for face, body, style, semantic role, and provenance.
3. Compare each field against the canonical HELEN identity vector.
4. Compare A and B against each other for identity coherence.
5. Emit PASS, WARN, or BLOCK.
6. Attach receipt with artifact hashes, prompt hashes, scorer version, and verdict.

Twin Mirror is not a proof of mathematical inversion. It is an operational lie detector for obvious identity drift.

## 7. PASS / WARN / BLOCK Thresholds

Initial thresholds are intentionally conservative and mock-scored.

```yaml
PASS:
  minimum_total_score: 0.85
  minimum_face_score: 0.80
  minimum_style_score: 0.80
  minimum_semantic_role_score: 0.90
  maximum_authority_leak_score: 0.05
  action: admit_as_candidate_render_with_receipt

WARN:
  minimum_total_score: 0.65
  maximum_authority_leak_score: 0.15
  action: manual_review_required_no_canonical_claim

BLOCK:
  triggers:
    - total_score_below_0_65
    - face_score_below_0_60
    - authority_leak_score_above_0_15
    - missing_artifact_hash
    - missing_renderer_provenance
    - sentience_or_sovereignty_claim_detected
  action: reject_from_admitted_HELEN_asset_set
```

Thresholds are proposal defaults. They must be calibrated against real render sets before canonical use.

## 8. Identity Gate Receipt Schema

Minimum receipt schema:

```json
{
  "schema": "HELEN_IDENTITY_GATE_RECEIPT_V1",
  "artifact_id": "string",
  "artifact_hash": "sha256:string",
  "source_prompt_hash": "sha256:string",
  "renderer_id": "string",
  "renderer_version": "string|null",
  "identity_vector_id": "HELEN_CANONICAL_VISUAL_IDENTITY",
  "gate_version": "identity_gate_v1_mock",
  "scores": {
    "hair_score": 0.0,
    "eye_score": 0.0,
    "face_score": 0.0,
    "body_score": 0.0,
    "style_score": 0.0,
    "semantic_role_score": 0.0,
    "artifact_score": 0.0,
    "roundtrip_score_mock": 0.0,
    "authority_leak_score": 0.0
  },
  "verdict": "PASS|WARN|BLOCK",
  "review_required": true,
  "admission_status": "DRAFT_ONLY|CANDIDATE_ADMITTED|BLOCKED",
  "receipt_hash": "sha256:string",
  "created_at": "iso8601:string"
}
```

The receipt testifies to the gate result. It does not prove metaphysical identity, consciousness, agency, or mathematical inversion.

## 9. Renderer Provenance Limits

Renderer provenance is mandatory but limited.

A renderer may provide:

- model name
- model version
- backend name
- prompt hash
- seed when available
- input image hash when available
- output artifact hash
- timestamp
- local or remote execution marker

Renderer provenance does not prove identity continuity. It only establishes the production trace. Identity admission still requires gate evaluation.

Known limits:

- black-box image generators are not true inverse models
- prompt reuse is not identity proof
- visual similarity is not full mathematical provenance
- style consistency is not face consistency
- face consistency is not semantic admissibility
- renderer metadata can be incomplete, unavailable, or non-replayable

Therefore renderer provenance is necessary for receipts but insufficient for canonical admission.

## 10. Manual Review Fallback

Manual review is required when the identity gate emits WARN or when the scorer lacks enough evidence.

Manual review must answer:

1. Does the artifact visibly preserve HELEN identity?
2. Does it remain within the allowed transformation orbit?
3. Does it avoid forbidden drift?
4. Does it avoid authority leakage?
5. Is renderer provenance adequate for receipt attachment?
6. Should the artifact remain draft-only, become candidate-admitted, or be blocked?

Manual review cannot override missing receipts into canonical truth. It can only classify the artifact for the next gate cycle.

## 11. Test Harness

The first test harness is mock-based and deterministic.

Required tests:

```yaml
schema_conformance:
  purpose: validate receipt fields and verdict enum

checksum_presence:
  purpose: ensure face/body/style/semantic/provenance channels exist

authority_leak_block:
  purpose: BLOCK sentience, sovereignty, prophecy, hidden authority, or reality mutation claims

twin_mirror_consistency:
  purpose: compare two candidate renders for same-anchor coherence

threshold_routing:
  purpose: verify PASS/WARN/BLOCK decisions from mock scores

receipt_hashing:
  purpose: compute sha256 for artifact, source prompt, and receipt payload

no_receipt_no_admission:
  purpose: ensure missing identity gate receipt prevents admitted render status
```

The harness must not require real face inversion in MVP. It tests the contract before the model.

## 12. Ledger Admission Rule

The ledger admission rule is absolute:

```text
NO_IDENTITY_GATE_RECEIPT => NO_ADMITTED_RENDER
```

Admission sequence:

```text
Image proposes.
Gate evaluates.
Receipt testifies.
Ledger governs.
```

A render without an identity gate receipt may exist as a draft artifact only. It may not enter the admitted HELEN asset set, may not be called canonical, and may not be used as proof of visual identity continuity.

Final theorem:

```text
HELEN renders are admissible only when the perceptual artifact remains within an allowed transformation orbit of the conserved mathematical identity, and the admission decision is bound to a replayable receipt.
```

status: PROPOSAL
next: identity_gate.py mock scorer
