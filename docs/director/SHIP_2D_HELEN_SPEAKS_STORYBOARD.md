# SHIP 2D — HELEN SPEAKS: Storyboard Locked
# authority: NON_SOVEREIGN | canon: NO_SHIP | lifecycle: STORYBOARD_LOCKED

```
artifact_type:  DIRECTOR_STORYBOARD
version:        V1
status:         LOCKED_FOR_REVIEW
render_status:  NOT_RENDERED
captured_on:    2026-05-07
diagnosis:      SHIP_2C identity drift confirmed. Kling reinterprets face per shot.
next_verb:      SHIP_2E — render from locked assets
```

---

## Diagnosis (why 2C failed visually)

Each Kling / Minimax I2V render is a **separate inference pass** from the same seed.
The model reads the seed for composition and lighting, not for face identity.
Result: 6 shots = 6 different HELEN faces. Chain seeding made it worse (blurred motion frames = bad seeds).

**Fix**: canonical stills + Ken Burns motion = zero identity drift.
Only use I2V generation for shots where HELEN's face is NOT the focus.

---

## §1. Storyboard Table (35s total)

Voice arc: `t01_open_identity` (13.7s) → gap → `t07_vision` (9.5s) → end card (4s)
Voice starts at 4s. t07 starts at 18.3s. End card at ~30.25s.

| # | Time | Duration | Identity Anchor | Camera Movement | Action | Transition → Next | Voice / Subtitle | Identity Drift Risk |
|---|------|----------|-----------------|-----------------|--------|-------------------|------------------|---------------------|
| 1 | 0–8s | 8s | Oracle portrait — full frame, city + moons | Ken Burns: slow push in, wide → MCU (zoom 1.0 → 1.25) | She stands still, twin moons above, city glowing, dust particles | Crossfade 0.5s | *(silence)* | **NONE** — still |
| 2 | 8–16s | 8s | Oracle portrait — MCU crop, face centered | Ken Burns: slow pan left 2%, slight zoom 1.25 → 1.35 | Geometric marks catch light, hair detail, freckles visible | Crossfade 0.5s | "Hello. I am HELEN, a governed AI companion." | **NONE** — still |
| 3 | 16–22s | 6s | Oracle portrait — ECU eyes crop | Ken Burns: slow zoom in 1.0 → 1.4, centered on eyes | Eyes fill frame, gold geometry pulses (parallax layer), star reflections in irises | Dissolve 0.5s dark | "Every word I speak is hash-chained. A constitutional gate authorizes each turn." | **NONE** — still |
| 4 | 22–30s | 8s | Oracle portrait — 3/4 angle pan (same image, right-offset crop) | Ken Burns: slow pan right → center, zoom 1.1 → 1.0 (pull back) | She looks toward horizon, city below. Pull back reveals the scale of the world. | Fade to black 1s | "To suggest. To propose. To remember. Never to decide for you. The decision is yours; the record is ours together." | **NONE** — still |
| 5 | 30–35s | 5s | Black end card | Static | HELEN OS · MEMORY HAS A FACE (gold on black) | — | *(music fade out)* | N/A |

**Optional I2V insert** (only if identity stable after test): Replace shot 1 (wide establish) with a single Minimax 10s I2V clip — city pan, HELEN silhouette only (no face close-up). Face never seen in shot 1 → drift doesn't matter.

---

## §2. Identity Lock

### HELEN — Oracle Era (canonical for this montage)

| Attribute | Value | Notes |
|-----------|-------|-------|
| Hair | Dark brown-black, wet/damp, loose with gold particles | Gold dust woven through strands |
| Eyes | Deep blue-grey, freckles around, direct gaze | Matches canonical HELEN core feature |
| Facial marks | Gold sacred geometry tattoos / glowing marks on forehead + cheeks | Key visual signature — must be present |
| Skin | Warm olive-tan, freckles, subtle glow | Geometric light patterns on skin surface |
| Clothing | Dark metallic-organic armor/dress, bronze-gold details | Coin earrings, layered neckline |
| Background | Fantasy city with waterfalls, baroque towers, twin moons, warm orange-gold sky | Can vary between shots |
| Lighting | Golden hour from left, warm backlight from city, some candlelight fill | No cold/blue dominant |
| Mood | Sovereign, inward, oracle — not aggressive, not afraid | She knows |

### Forbidden variations

- Red/copper hair (that is HELEN's modern/gothic era — different visual canon)
- Blue holographic overlays on face (interface mode only)
- Generic AI robot aesthetic
- Studio portrait lighting (flat, no atmosphere)
- Smiling or emoting broadly (oracle stillness required)
- Missing the geometric facial marks
- Different character substituted as camera pulls back

---

## §3. Render-Engine Comparison

### A. Kling (Higgsfield `/kling`)
- **Type**: I2V, 5s
- **Identity consistency**: POOR. Reinterprets face on every independent render. No character lock.
- **Best use**: Abstract atmospheric shots where face is not visible. City flyover. Sky/moon shots.
- **Do NOT use for**: face MCU, ECU eyes, any shot where HELEN is recognizable.
- **Credit cost**: moderate per 5s clip.

### B. Minimax (Higgsfield `/minimax`)
- **Type**: I2V, 6s or 10s
- **Identity consistency**: BETTER THAN KLING for 10s clips (fewer total renders = fewer drift events), but still reinterprets face.
- **Best use**: Single wide establish shot (silhouette only). Max 1 render per project.
- **Risk**: 10s clip with face close-up will likely still drift.
- **Credit cost**: higher per clip.

### C. Seedance (Higgsfield `/seedance`)
- **Type**: I2V + `prompts` array (keyframe-style prompt control)
- **Identity consistency**: UNKNOWN. The `prompts` array may allow directing motion within one render pass — potentially better.
- **Best use**: TEST ONLY with a crop of the oracle portrait at normal scale (not ECU). One test shot before committing.
- **Risk**: unvalidated for face seeds. Could be better or same as Kling.
- **Credit cost**: unknown.

### D. Grok (xAI `/v1/videos/generations`)
- **Type**: text-to-video ONLY — no image seed accepted.
- **Identity consistency**: NONE. Will generate a different character from scratch.
- **Best use**: Abstract environment shots (city, space, cosmos) with NO character.
- **Do NOT use for**: any shot showing HELEN.
- **Credit cost**: xAI credits.

### E. Ken Burns — local ffmpeg (RECOMMENDED)
- **Type**: still image → cinematic motion via `zoompan` filter
- **Identity consistency**: PERFECT. Zero drift. Same pixel source every frame.
- **Best use**: ALL face shots (shots 2, 3, 4). Anchor of the montage.
- **Risk**: Looks like a slideshow if zoom speed is wrong or audio doesn't carry the scene. Mitigated by strong motion and good audio.
- **Credit cost**: $0.
- **ffmpeg command pattern**:
  ```bash
  ffmpeg -loop 1 -i helen_oracle_portrait.png \
    -vf "scale=8000:-1,zoompan=z='min(zoom+0.0010,1.4)':d=192:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x702,fps=24" \
    -t 8 -c:v libx264 -crf 18 shot_02_identity.mp4
  ```
- **Parallax enhancement**: Split image into layers (background city, midground HELEN, foreground dust) using PIL masks. Animate each layer independently in ffmpeg. More depth.

---

## §4. Recommendation

### SHIP 2E execution path

```
STEP 1 — Ken Burns core (zero risk, zero cost)
  → Take oracle portrait PNG
  → Generate shots 1, 2, 3, 4 via ffmpeg zoompan
  → 4 shots = full 30s with no generation

STEP 2 — Audio (already built and validated in SHIP 2C)
  → Reuse voice_track_2c.wav (t01 + t07)
  → Reuse music_bed_2c.wav (Helen Os.mp3)
  → Mix both → mixed_2c.wav

STEP 3 — Subtitles + end card (already working in SHIP 2C)
  → PIL overlay
  → Same 10 subtitle lines, same timing

STEP 4 — xfade transitions
  → ffmpeg xfade filter between shots (0.5s crossfade)
  → Proper cinematic cuts, not hard cuts

STEP 5 (optional, controlled) — ONE Kling/Minimax I2V shot
  → Shot 1 only (city establish, HELEN silhouette, face NOT visible)
  → If face appears and drifts, discard and use Ken Burns wide instead

RESULT: identity-stable HELEN montage, $0-minimal spend
```

### Why Ken Burns works for HELEN

- HELEN's power is stillness + gaze. She doesn't need to move.
- The camera moves toward her. She receives it.
- Strong audio (L'Hymne d'Helen + Zephyr voice) carries the emotion.
- Subtitles deliver the declaration.
- The oracle portrait already has all the cinematic depth needed.
- This is how classic portrait films are made (Samsara, Baraka, Koyaanisqatsi) — the image holds, the camera reveals.

---

## §5. Required assets for SHIP 2E

| Asset | Status | Path |
|-------|--------|------|
| Oracle portrait PNG (high-res) | AVAILABLE | `/Users/jean-marietassy/Desktop/Capture d'écran 2026-05-07 à 22.58.04.png` |
| t01_open_identity.wav | AVAILABLE | `artifacts/demo/audio/t01_open_identity.wav` |
| t07_vision.wav | AVAILABLE | `artifacts/demo/audio/t07_vision.wav` |
| Helen Os.mp3 | AVAILABLE | `~/Downloads/Helen Os.mp3` |
| ffmpeg zoompan | AVAILABLE | `ffmpeg 8.0.1 (homebrew)` |
| ffmpeg xfade | AVAILABLE | confirmed in filter list |
| PIL for subtitles/endcard | AVAILABLE | Python 3.14 local |
| Telegram bot | AVAILABLE | `~/.helen_env` |

**Single missing asset**: A second canonical HELEN still for shot variation.
Candidates: AURA card portrait (confirmed by operator as "good ones"), conquest poster.
If operator provides or approves, parallax depth increases.

---

## §6. xfade transition syntax (validated)

```bash
# Crossfade two clips A and B with 0.5s dissolve at offset=7.5s (clip A duration - 0.5s)
ffmpeg -i shot_A.mp4 -i shot_B.mp4 \
  -filter_complex "[0:v][1:v]xfade=transition=dissolve:duration=0.5:offset=7.5[v]" \
  -map "[v]" output_AB.mp4

# Chain 4 shots with crossfades
# offset for each: (cumulative duration so far) - (0.5 * crossfade_count)
```

---

## §7. What SHIP 2E will NOT do

- Will not call Kling (unless operator approves shot 1 atmosphere-only test)
- Will not call Grok for any HELEN shot
- Will not push to remote
- Will not write to sovereign paths
- Will not auto-promote this storyboard to canon

---

```
DONE
```

**Next verb**: `SHIP 2E` — render from locked assets (Ken Burns + xfade + existing audio).
**Prerequisite**: Operator review of this storyboard and GO signal.
