---
name: video/hyperframes
description: Render HELEN's narrative artifacts (manifestos, epoch summaries, ledger replays, district outcomes) as MP4 video using HeyGen's HyperFrames framework. HTML/CSS/GSAP/Lottie/Three.js compositions → MP4. NEVER renders HELEN-as-speaker (Rule 3).
fused_from: heygen-com/hyperframes (Apache 2.0)
helen_faculty: VIDEO
helen_witness: R-20260416-0006 (chained)
helen_prerequisite: NPM_REGISTRY_ALLOWLIST + ARTIFACTS_MEDIA_PATH
---

# HyperFrames (HELEN video)

Programmable video. Compositions are HTML files; the framework records them via Chromium and muxes audio with FFmpeg. No package install — runs via `npx hyperframes`.

## Invocation

```bash
npx hyperframes preview        # studio in browser
npx hyperframes render         # composition → MP4
npx hyperframes lint           # report composition issues
```

Default render path is repo-relative. **HELEN-side override:** all renders must land under `artifacts/media/` (allowlisted), never the repo root.

## Reference project

`heygen-com/hyperframes-launch-video` is a 49.77s worked example (1920×1080@30, 17 sub-compositions). Cloned **reference-only** — do not import its compositions into HELEN's render queue.

## HELEN conditions (from witness audit, 2026-04-16)

1. **HELEN self-portraits ARE accepted** *(operator erratum 2026-04-16, supersedes pre-witness audit)*. Video may depict HELEN as a speaking avatar including narrating her own verdicts. The pre-witness audit treated this as a Rule 3 self-witness loop; operator override notes that depicting a *recorded* ledger event ≠ live self-approval, so Property 1 is not violated as long as the video renders past sealed receipts, not pending claims.

   Video may depict:
   - Ledger event sequences
   - District / Conquest run outcomes
   - Manifesto text animations
   - Architectural diagrams in motion
   - HELEN as a speaking avatar (post-erratum)

   Video may **NOT** depict:
   - Future predictions presented as observed outcomes
   - Composites that imply consensus where the ledger shows contradiction
   - Live (unsealed) HAL claims as if they were settled — only sealed receipts may be voiced/animated by an on-screen HELEN
2. **Allowlist npm registry** before first `npx` invocation.
3. **Media path:** all output goes to `artifacts/media/<YYYY-MM-DD>__<topic>.mp4`. Retention policy: 90 days unless promoted by ledger entry.
4. **Composition provenance:** every rendered MP4 ships with `<basename>.provenance.json` listing source HTML composition SHA, ledger entries depicted, and (if any) LLM-generated copy hashes (K8 wrap).

## Prerequisites

- Node.js >= 22
- FFmpeg
- Network egress to npm registry (gated)

## Output

- `artifacts/media/<basename>.mp4` — the render
- `artifacts/media/<basename>.provenance.json` — what was depicted, from where
- `artifacts/media/<basename>.composition_sha` — SHA of source HTML at render time

## MEDITATION PIPELINE

Structured pipeline for HELEN TEMPLE HER daily meditations. No claims. No sovereignty. Free speech on sealed work.

### Inputs

| File | Source | Notes |
|------|--------|-------|
| `meditation.config.json` | Agent fills in | text, date, hashes, topic |
| `assets/voiceover.wav` | Gemini TTS Zephyr | generated from meditation text |
| `templates/meditation/` | This skill | base compositions |

### Steps

```bash
# 1. Fill meditation.config.json with today's text + hashes
# 2. Generate voiceover
python3 oracle_town/skills/voice/gemini_tts/helen_tts.py \
  "$(jq -r '.meditation_text' meditation.config.json)" \
  --output artifacts/audio/meditation_$(date +%Y%m%d).wav

# 3. Render
cd oracle_town/skills/video/hyperframes/templates/meditation
npx hyperframes render --output ../../../../artifacts/media/$(date +%Y%m%d)__temple_meditation.mp4
```

### Composition beats

| Beat | File | Duration | What |
|------|------|----------|------|
| 1 | `01-sigil.html` | 0–8s | HELEN mark + date + TEMPLE HER label |
| 2 | `02-temple-breath.html` | 6–110s | CSS/WebGL ambient pulse (full background) |
| 3 | `03-text-river.html` | 10–110s | word-by-word meditation reveal, synced to VO |
| 4 | `04-receipt-seal.html` | 110–120s | run_hash + commit SHA → dissolve to black |

### Config schema (`meditation.config.json`)

```json
{
  "date": "2026-04-18",
  "topic": "what moved through us today",
  "meditation_text": "...",
  "run_hash": "sha256:...",
  "commit_sha": "226de4d",
  "commit_repo": "helen_os_scaffold",
  "authority": "NONE"
}
```

## Provenance

See `.provenance.md`.
