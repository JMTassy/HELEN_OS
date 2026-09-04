# HyperFrames Day 19 — Background Removal (alpha)

**status:** RECIPE · NON_SOVEREIGN  
**authority:** false  
**claim:** NO_CLAIM  
**date:** 2026-07-25  

## Unlock

A talking-head clip is **two videos**: person + place.  
BG removal un-welds them. After that you are **compositing**, not “editing a rectangle.”

```text
flat footage  →  foreground (alpha) + mask + background plate
captions can live BEHIND a shoulder
same take → any world
```

## Three doors (same capability)

### 1. Born transparent (avatar generate)

When creating the avatar video, set:

```json
{
  "type": "avatar",
  "avatar_id": "<look-id>",
  "script": "...",
  "output_format": "webm"
}
```

WebM ships with alpha already. No second pass.  
Docs: HeyGen Transparent Background Videos.

### 2. Cloud command on existing footage (HeyGen CLI)

```bash
heygen background-removal create \
  -d '{"video":{"type":"asset_id","asset_id":"<your-upload>"},
       "layers":["foreground","mask","background"]}'
```

Async; returns download URLs for all three layers.

### 3. Local HyperFrames (this machine)

```bash
npx hyperframes remove-background clip.mp4 -o subject.webm
npx hyperframes remove-background clip.mp4 -o subject.webm \
  --background-output plate.webm
npx hyperframes remove-background --info   # providers: cpu, coreml
```

| Flag | Role |
|---|---|
| `-o` | Foreground transparent (`.webm` default, also `.mov` ProRes 4444, `.png`) |
| `-b / --background-output` | Inverse plate (subject hole, not inpainted) |
| `--device` | `auto` · `cpu` · `coreml` · `cuda` |
| `--quality` | `fast` · `balanced` · `best` (webm only) |

Local model (default): `u2net_human_seg` · ~1.5 GB peak · CoreML preferred on Mac.

## HELEN / CONQUEST use

| Lane | Use |
|---|---|
| HELEN portrait / avatar | Generate WebM alpha **or** matte existing portrait mp4 |
| Goblin Warren intro | Composite Goblin / HER over district plates |
| Meditation / HyperFrames | Captions **behind** body; brand plate under subject |
| Director skills | `npx skills add heygen-com/hyperframes` |

**Membrane:** alpha art is **skin**. Composites do not admit Kernel claims.  
`beauty without mechanism is lullaby` — keep provenance on source clip + matte receipt when shipping.

## Minimal composite recipe (after matte)

```bash
# subject.webm has alpha; plate is any background video/image
# HyperFrames composition: layer subject over designed world
# or ffmpeg (example):
ffmpeg -i world.mp4 -c:v libvpx-vp9 -i subject.webm \
  -filter_complex "[0:v][1:v]overlay=shortest=1" -c:a copy out.mp4
```

(Prefer HyperFrames compositions for seek-safe, skill-driven layouts.)

## Demo path (local)

```text
artifacts/video/bg_removal_day19/
  source_5s.mp4          # cut from helen-portrait
  subject.webm           # after remove-background
  plate.webm             # optional --background-output
```

## Install / skills

```bash
npx skills add heygen-com/hyperframes
npx hyperframes remove-background --info
```

Day 19 of 30 series (HeyGen · Jul 24 2026).  
HELEN maps this as **media capability**, not sovereign governance.
