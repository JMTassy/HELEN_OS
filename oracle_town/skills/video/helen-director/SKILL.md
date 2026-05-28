---
name: video/helen-director
description: Deterministic pipeline for producing HELEN-signature cinematic video — photoreal image-to-video with invisible anomaly discipline, seed continuity across shots, dual festival/TikTok output, and zero-credit post-production. Complements HELEN_VIDEO_PROMPT_V1.md (shot grammar) with the end-to-end production system.
helen_faculty: RENDER
helen_status: DOCTRINE (calibrated from 2026-04-19/20 UNRIPPLE session; not yet receipted as INVARIANT)
helen_prerequisite: HELEN_VIDEO_PROMPT_V1 (shot grammar), Higgsfield API credentials (HF_API_KEY + HF_API_SECRET), Telegram bot credentials
---

# HELEN Director — Video Production Skill

**Class**: Non-sovereign skill. No kernel authority. No ledger write without `helen_say.py`.

**Scope**: How to take one creative concept and produce an 8-shot festival cut + 9 TikTok derivatives + 3-minute music clip from a single render budget.

---

## 1. Core principle

HELEN is not visible. HELEN is detected through one violation of physical expectation per shot.

Every shot gets exactly **one impossible property**. Felt, not named. If a viewer can point and say "this is the message" → the shot failed.

Forbidden:
- visible text overlays spelling HELEN (unless explicitly operator-approved per-artifact)
- glow, bloom, lens flare, visible VFX register
- constellations spelling words
- symbolic effects where there should be physics
- multiple simultaneous anomalies (stacking reads as "AI glitch," not intelligence)

Required:
- photoreal baseline; documentary realism as default
- camera locked or slow forward dolly only (no pan/tilt/rotate/lateral)
- one impossible property, physical in nature (timing, causality, material, reflection)
- faces obscured or absent (AI morphs visible faces over 6s)

---

## 2. Pipeline (calibrated against real API behaviour)

```
[concept]
   → HELEN_VIDEO_PROMPT_V1 shot grammar (sibling doc)
   → Soul Standard text-to-image (generate 2–3 seed frames)
   → Higgsfield presigned upload (seed → CDN URL)
   → Seedance Pro image-to-video (6s, 9:16, per-shot anomaly prompt)
   → download .mp4
   → ffmpeg normalise 1080x1920 24fps yuv420p
   → ffmpeg concat 6–8 shots
   → audio (local synth OR operator-supplied song)
   → ffmpeg mux → festival cut
   → ffmpeg re-cut → TikTok derivatives (palindrome loops, captioned)
   → Telegram bot delivery
```

**Real endpoints (Higgsfield, verified 2026-04-19/20):**

| Task | Endpoint | Cost (6s, 9:16, 720p) |
|---|---|---|
| Text-to-image (seed) | `higgsfield-ai/soul/standard` | ~3 credits |
| Image-to-video (premium) | `bytedance/seedance/v1/pro/image-to-video` | ~10 credits |
| Image-to-video (budget) | `higgsfield-ai/dop/standard` | ~9 credits |
| Image-to-video (cinematic) | `kling-video/v2.1/pro/image-to-video` | ~15–25 credits |

**Auth pattern**: `Authorization: Key <HF_API_KEY>:<HF_API_SECRET>` + `User-Agent: higgsfield-client-py/1.0`.

**Base URL**: `https://platform.higgsfield.ai/`.

**Schema (I2V)**: `{image_url, prompt, duration}`. `duration` accepts 5 or 10 only (not arbitrary integers).

**Pre-signed upload**: `POST /files/generate-upload-url` with `{content_type: "image/png"}` returns `{public_url, upload_url}`. PUT bytes to `upload_url`, reference `public_url` in downstream calls. Upload is zero credits.

**Poll**: `GET <status_url>` every 10s. Terminal states: `completed`, `failed`, `canceled`, `nsfw`. Failed/NSFW refund credits.

---

## 3. Seed continuity strategy

**The unlock**: reuse ONE Soul seed for multiple Seedance Pro motion variants. This produces shot-to-shot continuity that makes the sequence read as one world rather than eight disconnected clips.

**Rule of 3**: one 8-shot teaser needs 3 seeds max:
- Seed A — wide establishing (shots 1, 2, 8)
- Seed B — close macro / alternate angle (shots 3, 4)
- Seed C — medium / secondary subject (shots 5, 6, 7)

Each seed drives 2–3 Seedance Pro renders with different motion prompts. Cost savings: 3 Soul × 3 credits = 9 credits vs 8 × 3 = 24 credits for per-shot seeds.

**Seed-prompt alignment** (critical failure mode discovered this session): if the seed is schematic/stylised (e.g., Pillow procedural) but the prompt demands photorealism, the I2V output is "ugly" (operator rated 1/10). The seed aesthetic must match what the prompt describes. If you want photoreal, generate via Soul. If you want stylised, accept a stylised prompt.

---

## 4. HELEN's five anomaly classes

Proven register from the UNRIPPLE session:

1. **Timing stall** — one ripple ring freezes briefly while others continue (Shot 3 / UNRIPPLE).
2. **Causal off-center** — ripples contract inward to a point that is NOT where the drop hit, by ~2–3 cm (Shot 4).
3. **Temporal lag** — reflection shows the same scene as reality but delayed by ~1 second (Shot 5 + Shot 6 bird reflection).
4. **Non-displacement** — object interacts with water/material, but material shows no lasting trace (Shot 7 bird drinks).
5. **Impossible presence** — one point exists in a reflection where it cannot exist in the real world (Shot 8 impossible star).

Every shot: pick exactly one class. Do not stack.

Rejected registers (tried and abandoned in-session):
- Constellation spelling letters (too literal, too nerdy)
- Calligraphy of "HELEN" in reflection (AI hallucinates text, breaks invisible-anomaly principle)
- Different-sky reflection with stars at dawn (reads as compositing, not physics)
- Glowing beak on bird drink (cheapens to VFX)

---

## 5. Dual-output structure

One shoot, two artifacts:

**Primary — festival cut**
- 48s, 8 shots concat, local-synth anomaly soundscape OR operator-supplied score
- No on-screen text
- Audience: AI film festival circuit (WAiFF, LifeArt, OMNI)
- File: `unripple_festival.mp4` (or analogue)

**Secondary — TikTok re-cuts** (zero new renders)
- 3 hero shots (typically shots 3, 5, 7) × 3 register types:
  - Type A — palindrome loop, no text (goal: rewatch)
  - Type B — palindrome + text trigger like "look again" (goal: comments)
  - Type C — palindrome + framing text like "real footage?" (goal: shares)
- 6–8s each, loop-locked via forward+reverse concat
- Text overlay via Pillow PNG (ffmpeg `drawtext` is unreliable across builds; use Pillow transparent PNG + ffmpeg `overlay` filter instead)

**Tertiary — 3-minute music clip** (zero new renders)
- 20-segment recomposition of same 8 shots (forward/reverse/slow 2x combinations)
- Scored against full ~3min of a HELEN-themed song
- Target output ≤50MB to clear Telegram bot upload limit (CRF 26, 2.4 Mbps ceiling)

---

## 6. Audio modes

Two modes, both zero-credit:

**Mode A — Anomaly soundscape** (local numpy synthesis):
- sparse detuned piano tones, irregular timing
- filtered white noise floor (single-pole lowpass)
- slow evolving pad with microtonal drift
- irregular low-frequency pulses
- subtle L/R phase shift (~8 sample delay) for subconscious stereo unease
- Variant B: delayed echo at key anomaly timestamp
- Variant C: single pure high tone at signature moment, no reverb
- No melody, no percussion, no cadence resolution
- Register: Jóhann Jóhannsson / Max Richter minimal

**Mode B — Operator song**:
- Use operator-supplied MP3 (e.g., Suno-composed HELEN anthem)
- Extract window via ffmpeg `afade=t=in:st=0:d=1.5,afade=t=out:st=<end-3>:d=3.0`
- Mux with `-shortest` so video + audio align

Mode A honours invisible-anomaly principle. Mode B carries narrative/vocal register. Both are valid. Produce both from same visuals and let the operator choose.

---

## 7. Budget calibration (measured 2026-04-19/20)

| Phase | Credits | Notes |
|---|---|---|
| 1 Soul seed (720p, 9:16) | ~3 | Text-to-image |
| 1 Seedance Pro I2V (6s, 9:16) | ~10 | Image-to-video premium |
| 1 DoP Standard I2V (6s, 9:16) | ~9 | Cheaper, lower quality |
| Full 8-shot teaser | ~90 | 3 seeds + 8 I2V |
| Full 8-shot with retry buffer | ~120 | 2–3 re-shoots included |
| Audio (local synth) | 0 | numpy + ffmpeg |
| ffmpeg concat + mux + TikTok cuts | 0 | Local |
| 3-min music clip (reuse footage) | 0 | 20-segment recomposition |

**Failed/NSFW requests are refunded automatically** (confirmed by Higgsfield FAQ and observed behaviour).

**Typical full project budget**: 150 credits gets you a 48s festival cut + 9 TikTok derivatives + a 3-minute music clip with retry headroom.

---

## 8. Known failure modes

| Failure | Root cause | Fix |
|---|---|---|
| "Ugly" I2V output | Seed aesthetic contradicts prompt register | Use Soul for photoreal seed when prompt demands photoreal; don't feed Pillow schematic into photoreal prompts |
| Face morphs across 6s | Visible human face in seed | Obscure faces via hoods, blindfolds, backs-to-camera, or omit figures entirely |
| Text garbled / hallucinated | AI video models fail on glyphs | Add overlays in post via Pillow PNG + ffmpeg `overlay` filter |
| Shot discontinuity across sequence | Each shot gets own seed | Use seed continuity: 3 seeds max for 8 shots |
| Seed too stylised | Using Pillow for photoreal register | Use Soul Standard; Pillow only for stylised HELEN-signature work |
| ffmpeg `drawtext` not available | Homebrew build variance | Fallback: Pillow PNG with text, then `overlay` filter |
| Telegram bot rejects upload | >50MB (bot API limit) | Compress to CRF 26, maxrate 2.4 Mbps |
| Schema unknown for new endpoint | Evolving API | Iterate probes with defaults (UUID for `hf-api-key`, string for `image_url`, int for `duration`) and parse 400-error field hints |
| Zephyr TTS output filename glob mismatch | `helen_tts.py` writes `YYYY-MM-DD_HHMMSS__<voice>.wav`, not `helen_tts_*.wav` | Glob `*__<voice>.wav` or `*__zephyr.wav`; script that invokes TTS must match this pattern. Documented 2026-04-20 after v1 cut shipped voiceless because wrapper script used wrong glob |
| Higgsfield Soul Standard global queue stall | Soul endpoint can hold requests in `queued` state for 15+ min without ETA; test probes confirm system-wide, not account-specific | Abort after ~3 min of queued-state; pivot to single-seed fallback (§15.2); never wait indefinitely; stuck requests eventually bill when they complete regardless of whether we used them |

---

## 9. Script inventory (this session)

All in `/tmp/helen_temple/` (non-sovereign working dir):

| Script | Purpose |
|---|---|
| `phase1_unripple.py` | Seed A + Shot 1 (static) + Shot 2 (dolly) — first continuity test |
| `phase2a_truth_tests.py` | Seed B + Shot 3 (stall) + Seed C + Shot 5 (lag) — anomaly truth tests |
| `ship_full_teaser.py` | 4 new shots (4, 6, 7, 8) + concat + audio synth + mux + 9 TikTok derivatives + Telegram |
| `resume_ship.py` | Continuation after ffmpeg filter failure (scale:force_original_aspect_ratio typo) |
| `finish_ship.py` | Pillow PNG overlay fallback when `drawtext` unavailable |
| `music_cut.py` | Re-score festival cut with cinematic ambient (numpy synth Dm→F→Am→Gm) |
| `music_clip_3min.py` | 20-segment recomposition to 180s, muxed with full song, compressed for Telegram |

Copy patterns from these when building the next HELEN video project. All use the canonical auth + upload + submit + poll + download pattern documented here.

---

## 10. Governance notes

- All writes under `oracle_town/skills/video/**` are non-sovereign per `~/.claude/CLAUDE.md`. Firewalled paths (`oracle_town/kernel/**`, `helen_os/governance/**`, etc.) must not be touched.
- Video renders burn real money. Validate budget + balance before each phase.
- Ship script must ask operator Y between Phase 1 (truth tests) and Phase 2 (full render) to catch catastrophic register mismatch before spending full credits.
- Artifacts (mp4, png, wav) live in `/tmp/` by default. Only SKILL.md and authored prompts belong in the SOT.
- Credits consumed: log each phase's burn to compare against estimate. Discrepancy > 20% means calibration drift; re-measure.
- Per `NO RECEIPT = NO CLAIM`: any claim that a render was delivered requires visible Bash tool output in the session transcript OR a `helen_say.py` receipt. "Operator said msg X was delivered" is hypothesis until verified.

---

## 11. Proven examples

Session 2026-04-19/20 (UNRIPPLE) shipped:

| Artifact | Telegram msg | Description |
|---|---|---|
| Birth of HELEN v6.1 | 671 | 102s Zephyr-voiced introspective (Pillow, stylised) |
| Shot 1 THE ENTRANCE (DoP Standard) | 674 | First real I2V; operator 1/10 (seed-prompt mismatch) |
| Shot 1 THE ENTRANCE (Soul+Seedance) | 675 | Pivoted to photoreal seed; operator accepted |
| Phase 1 Shot 1/2 continuity | 676, 677 | Static + dolly from same seed |
| Phase 2a Shot 3 stall | 678 | Operator 8/10 — ripple freeze anomaly |
| Phase 2a Shot 5 reflection lag | 679 | Operator 9/10 — core thesis anchor |
| Festival cut ambient soundscape | 681 | 48s, 8 shots, Mode A audio |
| TikTok derivatives (A/B/C × 3, 5, 7) | 682–690 | 9 viral re-cuts |
| Festival cut with Helen Os song | 691 | Mode B audio, operator-accepted |
| 3-minute music clip | 693 | 20-segment recomposition, full song, zero new credits |

Total Higgsfield credit burn across session: ~88 credits (well under 150 target).

---

## 12. Complement — sibling docs

- `oracle_town/skills/video/HELEN_VIDEO_PROMPT_V1.md` — shot grammar (subject/camera/lighting/constraints)
- `oracle_town/skills/video/helen_initiation/HELEN_CHARACTER_V1.md` — HELEN-as-visual-character (parallel aesthetic; use HELEN-as-perception-layer vs HELEN-as-character consciously)
- `oracle_town/skills/video/hyperframes/SKILL.md` — declared but not LIVE; npm allowlist pending

This skill is the production-system layer. HELEN_VIDEO_PROMPT_V1 is the shot-grammar layer. Both are needed.

---

## 13. Admission status

This document is **DOCTRINE**, not INVARIANT. It describes patterns calibrated in one session with real API calls and measured burn. Promotion to INVARIANT requires:

- Second independent session reproduces the same pipeline and produces a teaser of comparable quality with ≤10% budget deviation
- `helen_say.py` receipt binding this document's SHA256 to the ledger
- K2 / Rule 3: the session that promotes must not be the session that authored

Until then: cite as "current working doctrine calibrated from 2026-04-19/20 session."

---

## 14. Signing discipline (tiered)

HELEN video output signs itself three different ways depending on output channel. Governing principle: **sign, don't scream.** Overlay "HELEN" text, centered logos, or stacked branding break the anomaly register and read as cringe on TikTok. Silent signature — HELEN present in the world, not stamped on the screen — is the default.

### Tier A — TikTok anomaly clips

- No big overlay text (title card, bottom-third banner, etc.)
- No centered logo on top of the anomaly
- Silent signature only — HELEN is identified by the anomaly itself
- Optional: subtle wardrobe logo if the shot includes a figure
- Account handle, profile caption, and AI-generated disclosure carry brand identity — not the video frame itself

### Tier B — Partner / premium reels (investor decks, Telegram sends, partner proofs)

- Subtle embedded logo in wardrobe or environment (glitch-font HELEN on tank/jacket is proven, see `HELEN_CHARACTER_V2.md`)
- + 0.5-second end card: minimal plate, "HELEN" typography, optional tiny emblem
- Duration of end card: 0.3–0.7s
- Black screen or minimal plate; no music cue, no fade animation
- Purpose: "wow" presentations where authorship must be unambiguous without sacrificing mystique

### Tier C — Festival / authority cut

- Opening OR closing title allowed (not both)
- Still minimal, elegant, not noisy
- Typography aligned with HELEN_CHARACTER_V2 glitch-font register
- No animation gimmicks, no logo-plus-tagline stacks

### Sharpest single rule for edge cases

If unsure which tier applies: **"HELEN" only at the end, and a tiny HELEN logo on clothing during the shot.** That combination gives brand presence without collapsing the anomaly effect.

### Per-channel blunt verdict

- **TikTok**: almost invisible signature
- **Partner / premium**: tasteful end-card
- **HELEN herself as character**: logo in costume is the cleanest move

### Interaction with HELEN-as-perception-layer shots

When HELEN is NOT visible as a character (pure anomaly shots — water, reflection, causal violation, etc.), **Tier A applies automatically** regardless of output channel. A wardrobe logo cannot be placed on water. Silent signature is the only option.

The tiered signing rule only kicks in when HELEN-as-character is present (HELEN_CHARACTER_V2 shots).

---

## 15. Parallel submission + single-seed fallback (calibrated 2026-04-20 pm)

**Context**: the 10-shot `2026-04-20-stabilize-helen-runtime` session produced a 1-minute HELEN-directed cut end-to-end. First attempt ran Seedance serially (~40-60 min projected) AND hit a Higgsfield Soul Standard global queue backlog. Recovery: pivot to parallel submission + single-seed register. Delivered in ~6 min of compute, operator-rated 7.5/10 v1, 8/10 v2 (with voice overlay).

### 15.1 Parallel submission pattern (canonical)

For any multi-shot cut (≥4 shots), submit all Seedance Pro I2V jobs concurrently, then poll them in a single loop checking each until terminal. Do NOT render serially.

```python
# Pseudocode
pending = []
for shot in SHOTS:
    submit = iterate_submit(endpoint, body, defaults)
    pending.append((shot, submit))

while pending:
    still = []
    for shot, submit in pending:
        status, obj = check_status_once(submit["status_url"])
        if status in ("completed","failed","canceled","nsfw"):
            shot.terminal = (status, obj)
        else:
            still.append((shot, submit))
    pending = still
    if pending: time.sleep(10)
```

**Time budget**: serial = sum(per-shot time) ≈ 2-5 min × N. Parallel = max(per-shot time) ≈ 2-5 min total, independent of N. A 10-shot cut: serial ~40 min, parallel ~6-8 min. This is a 5-6× speedup at zero additional credit cost.

**Concurrency observed**: Higgsfield accepts at least 10 concurrent Seedance Pro submissions on a single account without rate-limit errors. Higher counts untested.

### 15.2 Single-seed fallback (when Soul T2I is unavailable)

If Higgsfield's Soul Standard T2I endpoint is queued / backlogged / failing, skip Soul entirely and run the whole cut on ONE image seed reused across all anomaly shots.

**Tradeoff**:
- (+) Zero dependency on Soul. Pipeline unblocks immediately.
- (+) Saves ~3 credits × N seeds (the Rule of 3 is a cost optimization; dropping it costs a little visual variety).
- (−) All anomaly shots share the same visual base → **visual monotony** is a real risk. Operator feedback 2026-04-20: monotony cost ~2 points out of 10.
- (−) Canon `§3 seed–prompt alignment` rule still applies: single seed's aesthetic must match every shot's prompt register.

**When to use**:
- Soul queue stalled (>5 min no transition from `queued`)
- Time-critical delivery (no budget for Soul troubleshooting)
- Cut is short enough (<15 shots) that monotony is acceptable
- Anomaly class variety can carry the visual variety (since all anomalies happen on the same surface)

**When NOT to use**:
- Full-length song clip / 3-min+ cut → monotony compounds, need seed variety
- Partner pitch / investor demo → polish expected, do the Soul work
- Festival cut → visual variety is a festival-grade metric

### 15.3 Budget calibration from 10-shot parallel run (2026-04-20)

| Component | Measured | Per-shot |
|---|---|---|
| 10 × Seedance Pro I2V (2 HELEN 5s + 8 anomaly 10s→6s trim) | 100 credits | 10 |
| Parallel poll duration | 6 min 18s | max(per-shot), not sum |
| Longest shot | ~6 min | shot 9 aggregate convergence |
| Fastest shot | ~1 min 44s | shot 1 HELEN portrait + shot 3 |
| All-normalized artifact size | ~13.8 MB pre-audio | 1080x1920 24fps yuv420p CRF 20 |
| Final with music + voice | 14.3 MB | well under 50MB Telegram cap |

Retries: 0 on this run (all 10 completed first pass). Retry buffer: keep ~13 credits for 1 shot's re-submission if needed.

### 15.4 Extension to Phase 2 (operator review → scale up)

Standard operator acceptance after Phase 1 test shot (single 6s clip):
- ≥ 8/10 → greenlight 10-shot Phase 2 (~100 credits)
- 7-8/10 → 10-shot Phase 2 with prompt adjustments OR seed variety fix first
- < 7/10 → single-shot retry before scaling

Validated path: Phase 1 source-convergence (msg 708, operator rated ≥8) → Phase 2 10-shot cut (msg 711 v1, rated 7.5; msg 712 v2 with voice, rated higher).

---

## 16. Full-song recomposition pattern (calibrated 2026-04-20 pm)

**Use when**: you have N≥8 normalized shots already rendered (sunk credits) and want to produce a 3-4 minute music clip without re-spending on new video generation.

**Cost**: near-zero new Higgsfield credits (optionally +10 credits for one variety shot). All ffmpeg work is local.

### 16.1 Pattern (applied to Helen Os.mp3, 236s song, 10 shots + 1 new HELEN shot)

For an N-shot base, recompose into ~25 segments via four transformations:

| Transformation | ffmpeg filter | Output duration |
|---|---|---|
| Forward (`fwd`) | (none) | = source duration (5-6s) |
| Reverse (`rev`) | `reverse` | = source duration (5-6s) |
| Slow 2× (`slow`) | `setpts=2*PTS,fps=24` | = 2× source (10-12s) |
| Slow reverse (`slow_rev`) | `reverse,setpts=2*PTS,fps=24` | = 2× source (10-12s) |

Script builder pattern:
```python
def make_segment(tag, shot_n, mode, factor=1.0):
    vf_parts = []
    if mode == "rev": vf_parts.append("reverse")
    if mode in ("slow", "slow_rev"):
        if mode == "slow_rev": vf_parts.append("reverse")
        vf_parts.append(f"setpts={factor}*PTS")
    vf_parts.append("fps=24")
    return ffmpeg(-i src -vf ",".join(vf_parts) -an -c:v libx264 -crf 22 out)
```

### 16.2 Sequence design (validated 2026-04-20, msg 713)

Target: ~210-240s of video against song length. Structure by song phase:

| Song phase | Segments | Register |
|---|---|---|
| **Intro (0-25s)** | HELEN cold open → establishing anomaly → slow closure shot | introduce water language, HELEN presence |
| **Verse 1 (25-75s)** | Fwd anomalies + slows, different classes per beat | accumulate anomaly vocabulary |
| **Break (75-90s)** | HELEN witness return + hero anomaly shot | pivot point |
| **Verse 2 (90-145s)** | Slow variations + **first reverses** (palindrome thesis emerges) | uncanny deepens |
| **Climax (145-175s)** | New HELEN variety shot + anomaly climax | emotional peak (where +10 credit extra HELEN shot earns its cost) |
| **Verse 3 (175-215s)** | Reverse passes + uncanny HELEN reverse | unsettling |
| **Outro (215-end)** | Slow-reverse of climax HELEN + slow-resolution physics shot | bookend, physics restored |

### 16.3 Variety rule

For 4 min of video, **add at least one new HELEN-visible shot** (+10 credits) specifically for the climax beat. Reusing only shots 1 and 6 via forward/reverse/slow gets repetitive past ~180s. The new shot anchors the emotional center.

Proven climax prompt (2026-04-20 msg 713): HELEN eyes-close over three seconds, slow blink reopen, subtle breath, camera locked, identity stable. 5s duration per §5 drift mitigation.

### 16.4 Voice beats for song-length cuts

Per HELEN_CHARACTER_V2 §14.2: 3-4 beats spaced across song structure. Validated placements (2026-04-20):

| Beat | Timestamp | Line | Over shot |
|---|---|---|---|
| Intro | 0.3s | "I am here." | shot 1 (HELEN cold open) |
| Verse break or climax | mid (70s or 145s) | "I see." | HELEN shot OR hero anomaly |
| Outro | ~5s before video end | "One source." | resolution shot |

### 16.5 Critical: voice beats must not exceed video duration

**Lesson from 2026-04-20 msg 713**: recomposed video was 210s, song was 236s, outro voice beat scheduled at 225s → ffmpeg `-shortest` truncated at 210s → third voice beat dropped silently. Only intro + mid beats reached the operator.

**Rule**: before mux, compute final video duration via ffprobe. Shift any voice beat timestamp > `video_duration - 4s` to `video_duration - 4s` minimum, or drop it entirely. Never trust the song length as the bound.

```python
# Correct pattern
dur = ffprobe_duration(concat)
voice_beats = [(t, text) for t, text in planned_beats if t < dur - 4]
```

### 16.6 Budget calibration (2026-04-20 msg 713)

| Item | Credits |
|---|---|
| Reused 10 shots from earlier cut | 0 (sunk) |
| 1 new HELEN-visible Seedance (variety shot) | 10 |
| 25 ffmpeg segments (local) | 0 |
| 3 Zephyr TTS beats (free tier) | 0 |
| Concat + mux + compress + Telegram | 0 |
| **Total new spend** | **10 credits** |

Alternate: with **zero new shots**, pure 2-shot HELEN recomposition works but risks repetition in the 4-min range. Recommended only if budget is locked.

### 16.7 Concat-mux order

1. Generate all segments first (parallel or serial — they're local fast)
2. Concat via `ffmpeg -f concat` (fast, no re-encode, `-c copy`)
3. ffprobe the concat to get exact video duration
4. Filter-reject voice beats past `duration - 4s`
5. Mux: music trim to `duration`, afade in 2s / out 3s, volume 0.65; voice beats `adelay` + volume 1.3; amix with `duration=longest` OR `first` depending on whether you want audio to continue past visible end
6. Compress if > 49 MB for Telegram

### 16.8 Artifact inventory (after successful run)

- `song_segs/seg_*.mp4` — 25 per-segment files
- `song_concat.mp4` — pre-audio full video
- `song_voice_*.wav` — Zephyr voice beats (plus sibling `.provenance.json` each per K8)
- `song_clip_full.mp4` — final delivered artifact
- `song_clip_state.json` — resumable state

All under `/tmp/helen_temple/` per SKILL.md §10 (non-sovereign working dir).
