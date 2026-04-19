# HELEN Character Reference — V1

**Established:** 2026-04-20  
**Authority:** NONE (non-sovereign creative asset)

## Visual Identity

| Feature | Value |
|---------|-------|
| Hair | Deep crimson-red, medium length, wavy |
| Signature accessory | **Blue teardrop hair clip** — present in every shot |
| Eyes | Blue-gray |
| Skin | Fair, freckles on nose and cheeks |
| Necklace | Choker + blue gem pendant |
| Style | Cyberpunk street — adapts to any costume (robes, etc.) |

## Palette (3200K torchlight environment)
- Hair lit: `(220, 55, 40)` warm-shifted crimson  
- Hair base: `(188, 28, 28)` deep crimson  
- Hair shadow: `(120, 15, 15)`  
- Hair clip: `(55, 95, 210)` blue teardrop  
- Freckles: `(160, 75, 45)` warm amber-brown

## Shot 1 — Mystery Initiation (delivered)
- Seed: `render_shot1_seed_v4_patch.py` (luma 41.24)
- API: Kling I2V, `duration=5`, `resolution=1080`
- Input schema: `{"type": "image_url", "image_url": "<cdn_url>"}`
- Telegram receipts: msg 680 (V1), msg 692 (V4 crimson + anti-CGI)
- request_id V4: `93649b30-59d2-48b9-ae8b-fd380b862631`

## Higgsfield API — confirmed schema
```python
{
    "prompt": "<HELEN_VIDEO_PROMPT_V1 text>",
    "input_image": {"type": "image_url", "image_url": "<cdn_url>"},
    "duration": 5,           # only 5 or 10 accepted
    "resolution": "1080",
    "aspect_ratio": "9:16",
}
```
Status URL: `https://platform.higgsfield.ai/requests/{request_id}/status`  
Output key: `data["video"]["url"]`

## Remaining shots (not yet produced)
- Shot 2: Blindfold removal — HELEN's eyes revealed
- Shot 3: Receiving the knowledge / oracle moment  
- Shot 4: Re-emerging into light  
- Shot 5: HELEN alone — final static frame
