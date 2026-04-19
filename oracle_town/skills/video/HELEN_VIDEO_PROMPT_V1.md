# HELEN_VIDEO_PROMPT_V1

**Class**: Non-sovereign skill specification. No kernel authority.  
**Version**: V1 — 2026-04-19  
**Author**: Operator + HELEN creative session  
**Status**: DOCTRINE (in use; not yet receipted as INVARIANT)

---

## Purpose

A deterministic template for generating video prompts that produce
cinematic, non-AI-glossy output across video generation engines
(Higgsfield minimax-t2v, Kling, Seedance, Runway, Sora).

A prompt is not creative text. It is a control surface over a stochastic renderer.

---

## HELEN_VIDEO_PROMPT_V1 Template

```
[FORMAT]
<resolution_px>, <aspect_ratio>, <fps>fps, <duration>s

[SHOT]
<shot_type> — <camera_motion + direction + speed>
(e.g.: "Medium static shot, slow dolly-in forward")
(e.g.: "Low wide angle, camera locked, no movement")

[SUBJECT]
<precise physical description + position in frame>
(e.g.: "A woman in her 30s wearing a dark coat, centered, facing camera")

[ACTION]
<single continuous action — one movement only>
(e.g.: "She slowly raises her head toward the light above")

[ENVIRONMENT]
<location + time of day + minimal contextual detail>
(e.g.: "Empty brutalist concrete room, midnight, no furniture")

[LIGHTING]
<source position + color temperature + shadow behavior>
(e.g.: "Strong vertical shaft from above, 5500K cold white, sharp hard shadows")

[ATMOSPHERE]  (optional — maximum ONE element)
<one slow-moving environmental element>
(e.g.: "Fine dust particles drifting in the light shaft")

[STYLE]
<rendering register + lens + texture treatment>
(e.g.: "Photorealistic, 35mm anamorphic, visible grain, rough surface imperfections")

[CONSTRAINTS]  (most important block — defines quality floor)
<what must remain stable across every frame>

[NEGATIVE]
No blur, no fake glow, no plastic surfaces, no extra objects,
no text, no flicker, no sudden motion, no AI smoothing artifacts.
```

---

## Key Invariants (non-negotiable)

1. **One shot = one continuous take.** No multi-scene narration in a single prompt.
2. **One main motion.** Either subject moves OR camera moves. Never both aggressively.
3. **Camera always explicit.** If omitted, model guesses → instability.
4. **Lighting = geometry, not mood.**  
   — Bad: `"dramatic lighting"`  
   — Good: `"warm directional light from left at 3000K, soft shadow fill from opposite wall"`
5. **Constraints > adjectives.** The NEGATIVE block is the strongest quality lever.

---

## Technical Ranges (engine-validated)

| Parameter | Recommended |
|-----------|-------------|
| FPS | 24–30 (most stable) |
| Duration | 4–8s optimal per clip |
| Aspect | 9:16 (social/HELEN), 16:9 (cinematic) |
| Resolution | 768 or 1080 (Higgsfield notation) |

---

## Instant Quality Upgrade

Add this line to ALL prompts:

```
visible imperfections, natural material response, no artificial smoothness
```

---

## Example — "No Receipt" Opening Shot

```
1080px, 9:16, 24fps, 6s

Medium static shot — camera locked, zero movement

A single rectangular sheet of white paper lying flat on the floor,
centered at the bottom third of the frame

No action — paper is completely still

Empty brutalist concrete room, high ceiling, no furniture, night

Narrow vertical shaft of cold light (5500K) from directly above,
illuminating only the paper; everything else in deep shadow;
no ambient fill except faint natural bounce from floor

Fine dust particles drifting very slowly in the light shaft

Photorealistic, 35mm lens, shallow depth of field on paper,
rough concrete texture visible, natural grain

Paper stays absolutely stable, no morphing, no rippling,
concrete walls maintain consistent texture throughout

No blur, no fake glow, no plastic surfaces, no extra objects,
no text, no flicker, no sudden motion, no AI smoothing artifacts.
```

---

## Higgsfield Integration

**Live endpoint**: `minimax-t2v` at `https://platform.higgsfield.ai/minimax-t2v`  
**Auth**: `HF_KEY` env var (`ID:SECRET` format)  
**SDK**: `higgsfield_client` (Python 3.11 homebrew)  
**Resolution values**: `"768"` or `"1080"` (not `"1080p"`)  
**Status 2026-04-19**: Credits required — add via cloud.higgsfield.ai before generating

**Submission**:
```python
import higgsfield_client as hf, os
os.environ.setdefault('HF_KEY', os.environ['HF_KEY'])

result = hf.subscribe(
    application='minimax-t2v',
    arguments={
        'prompt': '<HELEN_VIDEO_PROMPT_V1 formatted text>',
        'duration': 6,
        'resolution': '1080',
    }
)
```

---

## Voice Branding Rule

**Public output**: Always `HELEN OS · CONQUEST · CORSICA STUDIOS`  
**Voice engine**: backoffice implementation detail — never cited in captions,
Telegram messages, or public-facing artifacts.  
**Provenance sidecars**: technical model ID is recorded in `.provenance.json`
for receipt-chain integrity — this is correct and required. It is NOT public output.

---

## Companion Files

- `oracle_town/skills/voice/gemini_tts/helen_tts.py` — voice engine
- `oracle_town/skills/video/hyperframes/templates/meditation/generate_meditation.py` — HyperFrames pipeline
- `/tmp/helen_birth_of_helen/render_frames.py` — Pillow pipeline (v6.1 reference)
- `helen_os/render/asset_engine.py` — multi-engine generator registry
