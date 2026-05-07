# SHIP 2D — HELEN SPEAKS: Storyboard v2 (AUTORESEARCH Edition)
# authority: NON_SOVEREIGN | canon: NO_SHIP | lifecycle: STORYBOARD_LOCKED_V2

```
artifact_type:  DIRECTOR_STORYBOARD
version:        V2 — AUTORESEARCH rewrite
status:         LOCKED_FOR_REVIEW
render_status:  NOT_RENDERED
captured_on:    2026-05-08
research_basis: HELEN_CHARACTER_V2.md (DOCTRINE), HELEN_VIDEO_PROMPT_V1.md (DOCTRINE),
                helen-director/references/README.md, helen_demo_prep.py TURNS list,
                artifacts/demo/audio/ (8 voice clips), /tmp/helen_oracle/ (existing renders)
predecessor:    SHIP_2C — audio/music/subtitles pipeline VALIDATED; identity FAILED
next_verb:      SHIP_2E — render from locked assets
```

---

## §0. Critical finding from research

**Two canonical HELEN identities exist — they MUST NOT be mixed in one montage.**

| Identity | Hair | Eyes | Era | Reference file | Validated? |
|---|---|---|---|---|---|
| **HELEN Photoreal** (canonical modern) | Flame-orange / copper-red, tousled | Blue / teal-blue | Cyberpunk / street / modern | `helen-director/references/helen_photoreal_front.jpg` | YES — T3, 95% identity hold (2026-04-20) |
| **Oracle Portrait** (era: ancient/fantasy) | Dark brown-black, wet, gold particles | Deep blue-grey | Fantasy / ancient city / oracle | `Desktop/Capture d'écran 2026-05-07 à 22.58.04.png` | NOT validated for I2V consistency |

**SHIP 2C failure root cause**: The oracle portrait was used as seed, but Kling reinterprets the face on every independent render. With no validated identity-lock method for that portrait, each shot generated a different face.

**Decision required before SHIP 2E**: Which HELEN are we filming?
- Option A: Canonical photoreal HELEN (red hair) — validated Seedance method, 95% identity hold
- Option B: Oracle era HELEN (dark hair, fantasy) — Ken Burns only (stills), zero generation drift

Both storyboard paths are designed below.

---

## §1. Storyboard — Path A: Canonical HELEN Photoreal

**Seed**: `oracle_town/skills/video/helen-director/references/helen_photoreal_front.jpg`
**Engine**: Seedance Pro I2V (`bytedance/seedance/v1/pro/image-to-video`)
**Rule**: Motion-only prompts. Zero identity description in prompt text. The seed IS the identity.
**Format**: 5–6s clips × 5 shots + end card = ~34s

| # | Time | Dur | Camera Type | Motion Prompt (motion ONLY) | Transition → | Voice / Subtitle | Drift Risk |
|---|------|-----|-------------|----------------------------|-----------|--------------------|------------|
| 1 | 0–6s | 6s | FULL BODY — locked camera | slow forward camera drift, locked camera, atmosphere, candles flicker, dark background | xfade dissolve 0.5s | *(silence)* | LOW — Seedance validated |
| 2 | 6–12s | 6s | CU — 85mm | slow breath movement, hair very slightly stirs, minimal motion, eyes open to viewer | xfade dissolve 0.5s | "Hello. I am HELEN, a governed AI companion." | LOW — same seed |
| 3 | 12–18s | 6s | LOW ANGLE — upward tilt | very slow upward camera tilt impression, atmosphere builds, held frame | xfade dissolve 0.5s | "Every word I speak is hash-chained into an append-only ledger." | LOW — same seed |
| 4 | 18–24s | 6s | MCU — face level | eyes track slowly left to right, subtle head tilt, held frame | xfade dissolve 0.5s | "To suggest. To propose. To remember. Never to decide for you." | LOW — same seed |
| 5 | 24–30s | 6s | SILHOUETTE — wide backlit | slow forward walk toward camera, backlight halo, no face detail | fade to black 1s | "The decision is yours; the record is ours together." | NONE — face not visible |
| EC | 30–34s | 4s | END CARD | static black | — | "HELEN suggests. You decide. Everything is recorded." (t08) | N/A |

**Shot 5 is the safety valve**: silhouette means face not visible = zero drift risk even if generation is inconsistent.

---

## §2. Storyboard — Path B: Oracle Era (Ken Burns — zero generation)

**Seed**: `Desktop/Capture d'écran 2026-05-07 à 22.58.04.png` (oracle portrait, 8.2MB)
**Engine**: ffmpeg `zoompan` filter — zero AI generation, zero identity drift
**Rule**: The image never changes. The camera moves. She holds still.
**Format**: 4 Ken Burns clips + end card = ~34s

| # | Time | Dur | Crop Region | Ken Burns Movement | xfade → | Voice / Subtitle | Drift Risk |
|---|------|-----|-------------|-------------------|---------|-----------------|------------|
| 1 | 0–8s | 8s | Full image — wide | Slow push in: zoom 1.00 → 1.25, center anchor | dissolve 0.5s | *(silence — 4s)* → "Hello. I am HELEN," | **NONE** |
| 2 | 8–16s | 8s | Face crop — MCU | Slow zoom in: 1.25 → 1.45, center hold | dissolve 0.5s | "a governed AI companion. Every word I speak is hash-chained into an append-only ledger." | **NONE** |
| 3 | 16–24s | 8s | Eyes crop — ECU | Very slow zoom in: 1.00 → 1.35, center | dissolve 0.5s | "A constitutional gate authorizes each turn. To suggest. To propose. To remember." | **NONE** |
| 4 | 24–30s | 6s | Pull back — wide offset | Slow pan right + zoom out: 1.4 → 1.0 | fade to black 1s | "Never to decide for you. The decision is yours; the record is ours together." | **NONE** |
| EC | 30–34s | 4s | Black end card | Static | — | "HELEN suggests. You decide. Everything is recorded." (t08) | N/A |

**ffmpeg zoompan commands for Path B**:
```bash
# Shot 1 — ESTABLISH: full image, slow push in (8s = 192 frames @ 24fps)
# Scale to large canvas first (zoompan needs room to move)
ffmpeg -loop 1 -i oracle_portrait.png \
  -vf "scale=6000:-1,zoompan=z='min(zoom+0.0013,1.25)':d=192:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x702,fps=24" \
  -t 8 -c:v libx264 -crf 18 shot_1_establish.mp4

# Shot 2 — MCU: face crop with PIL first, then slow zoom in
# Use PIL to crop face region (approx center-upper of oracle portrait)
# Then zoompan: zoom 1.0→1.40 over 8s
ffmpeg -loop 1 -i oracle_face_crop.png \
  -vf "scale=6000:-1,zoompan=z='min(zoom+0.0016,1.40)':d=192:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x702,fps=24" \
  -t 8 -c:v libx264 -crf 18 shot_2_mcu.mp4

# Shot 3 — ECU eyes: tight eyes crop, very slow zoom
ffmpeg -loop 1 -i oracle_eyes_crop.png \
  -vf "scale=6000:-1,zoompan=z='min(zoom+0.0010,1.35)':d=192:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x702,fps=24" \
  -t 8 -c:v libx264 -crf 18 shot_3_ecu.mp4

# Shot 4 — REVEAL: wide offset crop, pan right + zoom out
ffmpeg -loop 1 -i oracle_portrait.png \
  -vf "scale=6000:-1,zoompan=z='if(eq(on\\,1)\\,1.4\\,max(zoom-0.0033\\,1.0))':d=144:x='iw/2-(iw/zoom/2)+10':y='ih/2-(ih/zoom/2)':s=1080x702,fps=24" \
  -t 6 -c:v libx264 -crf 18 shot_4_reveal.mp4
```

**xfade chain (dissolve between shots)**:
```bash
# Chain shots 1+2 → 3 → 4 with 0.5s crossfades
# xfade offset = (duration of first clip) - 0.5s
ffmpeg -i s1.mp4 -i s2.mp4 \
  -filter_complex "[0:v][1:v]xfade=transition=dissolve:duration=0.5:offset=7.5[v12]" \
  -map "[v12]" s12.mp4

ffmpeg -i s12.mp4 -i s3.mp4 \
  -filter_complex "[0:v][1:v]xfade=transition=dissolve:duration=0.5:offset=15.0[v123]" \
  -map "[v123]" s123.mp4

ffmpeg -i s123.mp4 -i s4.mp4 \
  -filter_complex "[0:v][1:v]xfade=transition=dissolve:duration=0.5:offset=22.5[vfull]" \
  -map "[vfull]" shots_1_4.mp4
```

---

## §3. Identity Lock

### Path A — Canonical HELEN Photoreal

| Attribute | Value |
|---|---|
| Hair | Flame-orange / copper-red, medium-length, tousled/wavy |
| Eyes | Blue / teal-blue |
| Skin | Fair with freckles on nose and cheeks |
| Accessories | Two small blue teardrop hair clips · black studded choker with blue gem · silver chain + blue pendant · silver bracelets |
| Outfit | White ribbed tank with HELEN glitch-font logo (blue-purple + orange trim) |
| Style range | Photoreal ↔ anime-cyberpunk; same identity holds across both |
| Reference | `helen-director/references/helen_photoreal_front.jpg` (175K, JPEG 85, 1024px) |

**FORBIDDEN in prompts**: Any mention of hair color, eye color, clothing, accessories, freckles, logo. The seed IS the identity. Prompting identity = inviting drift.

**FORBIDDEN substitutions**: generic AI hologram · robot · different character appearing as camera pulls back · cold blue light dominant · aggressive expression.

### Path B — Oracle Era

| Attribute | Value |
|---|---|
| Hair | Dark brown-black, wet/damp, loose with gold particles woven through |
| Eyes | Deep blue-grey |
| Facial marks | Gold sacred geometry tattoos — forehead + cheeks (must be visible in any face shot) |
| Skin | Warm olive, freckles, subtle bioluminescent glow |
| Clothing | Dark metallic-organic armor, bronze-gold details, coin earrings |
| Background | Fantasy city — waterfalls, baroque towers, twin moons, orange-gold sky |
| Lighting | Golden hour left, warm backlight, no cold/blue dominant |
| Reference | `Desktop/Capture d'écran 2026-05-07 à 22.58.04.png` (8.2MB, oracle portrait) |

**FORBIDDEN**: Red/copper hair (canonical modern era only) · blue AI hologram overlay · generic sci-fi frame · wide smiling expression · missing facial marks.

---

## §4. Voice Arc — Full 8-Line Canon Available

All 8 lines rendered as Gemini 2.5 Flash TTS, voice Zephyr, 24kHz mono WAV.
Located at: `artifacts/demo/audio/t01_open_identity.wav` … `t08_motto.wav`

| Slug | Duration | Text | Recommended shot |
|---|---|---|---|
| t01 | 13.7s | "Hello. I am HELEN, a governed AI companion. Every word I speak is hash-chained into an append-only ledger. A constitutional gate authorizes each turn before I respond." | Shots 1+2 (identity declaration) |
| t02 | 13.3s | "Those models forget. I cannot. They produce text. I produce text plus a verifiable receipt. A gate authorizes my answers; without authorization, I do not speak." | Shot 2 alt |
| t03 | 10.6s | "I remember every turn we have shared in this session — each one receipted. The full context is on the strip above. Nothing is hidden, nothing is forgotten." | Shot 3 (memory/vision) |
| t06 | 10.8s | "Because trust is not a feature. It is structure. An AI without an audit trail is a vendor's promise. An AI with one is an institution's instrument." | Shot 3 alt |
| t07 | 9.5s | "To suggest. To propose. To remember. Never to decide for you. The decision is yours; the record is ours together." | Shot 4 (command/reveal) |
| t08 | 4.9s | "HELEN suggests. You decide. Everything is recorded." | End card |

**Recommended sequence for 34s arc**:
```
0–4s    silence
4–17.7s t01 (identity declaration — 13.7s)
18.3s   t07 begins (vision/philosophy — 9.5s, ends 27.8s)
30–34s  t08 over end card (motto — 4.9s)
```

**Music**: `Helen Os.mp3` (`~/Downloads/Helen Os.mp3`) — *L'Hymne d'Helen*, 3:56, at 22% bed volume, fade out last 3s. Validated in SHIP 2C.

---

## §5. Render Engine Comparison (updated with validated data)

| Engine | Identity hold | Duration | Method | Cost | Verdict |
|---|---|---|---|---|---|
| **Ken Burns (ffmpeg zoompan)** | PERFECT — zero drift, zero generation | Any | Still → animated camera | $0 | RECOMMENDED for face shots |
| **Seedance Pro I2V** (`bytedance/seedance/v1/pro/image-to-video`) | HIGH — ~95% with canonical reference + motion-only prompt | 5-6s | I2V | Credits | RECOMMENDED for atmosphere shots |
| **Kling** (`/kling`) | LOW — reinterprets face per render, no lock | 5s | I2V | Credits | AVOID for any face shot |
| **Minimax** (`/minimax`) | UNKNOWN — not validated, duration 6s/10s | 6-10s | I2V | Credits | TEST only if Seedance unavailable |
| **Grok video** (`/v1/videos/generations`) | NONE — text-to-video only, no seed | Varies | T2V | xAI credits | AVOID for HELEN shots; OK for abstract BG |

**Why Seedance Pro over Kling**: The validated hero reference (2026-04-20 session) used `bytedance/seedance/v1/pro/image-to-video` specifically. Kling was never validated at T3 for identity hold. The motion-only prompt rule is critical — any identity description in the prompt causes the model to override the seed.

**Note on Higgsfield `/seedance` endpoint**: The Higgsfield platform's `/seedance` endpoint with `prompts` array may route to Seedance. Needs a single test shot to confirm identity hold before full render.

---

## §6. Recommendation

### SHIP 2E execution path (approved method)

```
DECISION 0 — Operator chooses: Path A (canonical red-hair HELEN) or Path B (oracle era dark-hair)?
  └─ Path A → use helen_photoreal_front.jpg → Seedance Pro for atmosphere + Ken Burns for close-ups
  └─ Path B → use oracle portrait → Ken Burns ONLY for all shots (100% identity safe)

STEP 1 — Ken Burns clips (Paths A + B face shots, $0)
  Input: chosen canonical still
  PIL: extract 3 crops (full, face, eyes)
  ffmpeg zoompan: 4 clips × 6-8s
  Output: shot_1_establish.mp4, shot_2_mcu.mp4, shot_3_ecu.mp4, shot_4_reveal.mp4

STEP 2 — xfade chain (ffmpeg xfade dissolve, $0)
  0.5s crossfade between each clip
  Output: shots_1_4_chained.mp4

STEP 3 — End card (PIL, $0)
  Black · "HELEN OS" gold · "MEMORY HAS A FACE" white
  Output: endcard_2e.mp4 (4s)

STEP 4 — Audio (already built, $0)
  Reuse mixed_2c.wav (voice_track_2c + music_bed_2c)
  OR rebuild with t01 + t07 + t08 sequence

STEP 5 — Subtitle PIL overlay (already validated, $0)
  10 lines, same timing as SHIP 2C

STEP 6 — Final mix (ffmpeg, $0)
  Concat shots + endcard → mix audio → burn subtitles → send Telegram

OPTIONAL STEP 7 — ONE Seedance test shot (Path A only, controlled spend)
  Shot 1 (FULL BODY, locked camera) — HELEN face distant, atmosphere dominant
  Prompt: "locked camera, slow atmospheric drift, dark background, candles flicker"
  If face drifts → discard, use Ken Burns shot 1 instead
  If face holds → consider replacing Ken Burns shots 2-3 as well
```

### Why this works

The HELEN OS philosophy: she is present, sovereign, still. She does not need to move. The camera moves *toward* her. The audio carries the declaration. The subtitles deliver the text. The still + Ken Burns is how Baraka, Samsara, and every great portrait film works. Motion is the camera's language, not HELEN's.

---

## §7. What SHIP 2E will NOT do

- Will not call Kling
- Will not call Grok for any HELEN shot
- Will not mix the two HELEN eras in one montage
- Will not push to remote
- Will not write to sovereign paths
- Will not self-decide Path A vs Path B (operator decides)

---

```
DONE
```

**Prerequisite for SHIP 2E**: Operator confirms Path A (canonical red hair) or Path B (oracle dark hair).
**Then**: Ken Burns renders immediately at $0. Optional Seedance test shot if Path A is chosen.
