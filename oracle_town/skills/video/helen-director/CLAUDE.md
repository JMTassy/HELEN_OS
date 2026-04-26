# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Scope

This file governs sessions whose primary working directory is the `helen-director` skill (`oracle_town/skills/video/helen-director/`). It is operating guidance for the production shell — *not* the doctrine. The doctrine lives in `SKILL.md` (§1–§16) and is authoritative; if this file and `SKILL.md` disagree, `SKILL.md` wins.

This skill is **non-sovereign** under HELEN's constitution. It writes mp4/png/wav into `/tmp/helen_temple/`, never into the kernel, governance, ledger, mayor, or closure paths. See `~/.claude/CLAUDE.md` § "Sovereign-path firewall".

## Authoritative documents (read before acting)

| Doc | Status | Purpose |
|---|---|---|
| `SKILL.md` | DOCTRINE (§13) | End-to-end production system: pipeline, anomaly classes, seed continuity, dual-output, budget, parallel + single-seed fallback, full-song recomposition, signing tiers |
| `HELEN_CHARACTER_V2.md` | LIVE | HELEN-as-character method: identity tokens, T3 alive method, voice-beat placement, drift mitigation |
| `SKILL_V2_DRAFT.md` | DRAFT, NOT CANON | "Context Kernel Extension" staged for MAYOR review. Do not cite as authority. Do not overwrite or amend without operator routing. |
| `references/README.md` | LIVE | Three character seeds; identity tokens; "do not regenerate via soul/reference" rule |
| `../HELEN_VIDEO_PROMPT_V1.md` (sibling) | LIVE | Shot grammar (subject/camera/lighting/constraints) — pair with this skill |

## What this skill does

Take one creative concept and produce, from a single render budget:
- one festival cut (~48s, 8 shots, no on-screen text), and
- nine TikTok derivatives (3 hero shots × A/B/C palindrome registers), and
- optionally a 3-minute music clip (~25-segment recomposition of the same shots, +10 credits for one variety shot).

Pipeline (canon `SKILL.md` §2):

```
concept → shot grammar (HELEN_VIDEO_PROMPT_V1) → Soul T2I (seeds) → Higgsfield
upload → Seedance Pro I2V (parallel) → ffmpeg normalise/concat → audio (local
synth or operator song) → ffmpeg mux → Telegram bot delivery
```

## Commands

Credentials load from `~/.helen_env` (mode 600). Required keys: `HIGGSFIELD_ID`/`HIGGSFIELD_SECRET` (or `HF_API_KEY`/`HF_API_SECRET`), `TELEGRAM_BOT_TOKEN`, `GEMINI_API_KEY`. Never echo values.

```bash
# 30s masterpiece runner — dry-run by default, prints plan + estimated credit burn
.venv/bin/python oracle_town/skills/video/helen-director/run_30s_v1.py

# Live execution requires explicit credit guard
.venv/bin/python oracle_town/skills/video/helen-director/run_30s_v1.py --live --spend-ok 90

# Zephyr TTS (voice beats over the cut)
GEMINI_API_KEY=... .venv/bin/python oracle_town/skills/voice/gemini_tts/helen_tts.py "I am here."
# Output filename pattern: YYYY-MM-DD_HHMMSS__zephyr.wav  (NOT helen_tts_*.wav — see SKILL.md §8)

# ffmpeg normalisation (canonical per-shot)
ffmpeg -i in.mp4 -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,fps=24" -c:v libx264 -crf 20 -pix_fmt yuv420p -an out.mp4

# Concat (no re-encode) once shots are normalised
ffmpeg -f concat -safe 0 -i list.txt -c copy concat.mp4

# Telegram delivery (>50MB will be rejected — compress to CRF 26 / maxrate 2.4M)
.venv/bin/python tools/helen_telegram.py send_video /tmp/helen_temple/<artifact>.mp4
```

There is no test suite, lint target, or build for this skill. Validation is operator-rated (1–10) on Telegram delivery.

## Architecture notes that are not obvious from the code

- **Higgsfield endpoints** (`SKILL.md` §2): `bytedance/seedance/v1/pro/image-to-video` is the I2V workhorse; `higgsfield-ai/soul/standard` is the seed T2I. Auth header is `Authorization: Key <ID>:<SECRET>` plus `User-Agent: higgsfield-client-py/1.0`. `duration` accepts only 5 or 10 — not arbitrary integers.
- **Pre-signed upload is zero credits**. `POST /files/generate-upload-url` → PUT bytes to `upload_url` → reference returned `public_url`. Do not embed image bytes in the I2V request.
- **Parallel submission is mandatory** for ≥4 shots (`SKILL.md` §15.1). Serial = sum(per-shot time); parallel = max. Measured 5–6× speedup at zero extra credit cost. ≥10 concurrent submissions per account observed safe.
- **Single-seed fallback** when Soul T2I queue stalls >5 min (`SKILL.md` §15.2). Reuse one seed across all anomaly shots; accept ~2 pts of monotony cost. Do not wait Soul out indefinitely — stuck requests still bill if they later complete.
- **Seed continuity = Rule of 3** (`SKILL.md` §3): one 8-shot teaser uses ≤3 seeds, each driving 2–3 motion variants. Seed aesthetic must match prompt register; Pillow-schematic seeds into photoreal prompts produce the "ugly 1/10" failure mode.
- **One impossible property per shot, never stacked** (`SKILL.md` §1, §4). Five proven anomaly classes: timing stall, causal off-center, temporal lag, non-displacement, impossible presence. Visible "HELEN" text, glow, bloom, and constellation-letter tricks are forbidden registers.
- **HELEN-as-character vs HELEN-as-perception-layer** are two different modes. When HELEN is not visible (water/reflection/causal shots), Tier A signing applies automatically regardless of channel — wardrobe logos cannot be placed on water (`SKILL.md` §14).
- **Voice beats must end ≥4s before video duration** (`SKILL.md` §16.5). ffprobe the concat first, filter beats past `duration - 4s`, otherwise `-shortest` truncates them silently.
- **Telegram bot upload cap is 50MB**. Compress final to CRF 26 / maxrate 2.4 Mbps if over.
- **All artifacts go to `/tmp/helen_temple/`**. Only `SKILL.md`, `HELEN_CHARACTER_V2.md`, `references/`, `run_30s_v1.py`, this file, and any future authored prompts belong in the SOT.

## Boundaries

- **Sovereign firewall** (per `~/.claude/CLAUDE.md`): never write under `oracle_town/kernel/**`, `helen_os/governance/**`, `helen_os/schemas/**`, `town/ledger_v1*.ndjson`, `mayor_*.json`, `GOVERNANCE/CLOSURES/**`, `GOVERNANCE/TRANCHE_RECEIPTS/**`. Reading is allowed.
- **Admissible bridge**: the only way for this skill to enter the sovereign layer is `python3 tools/helen_say.py "<message>" --op <op>`. Do not append to `town/ledger_v1.ndjson` directly. Do not call `tools/ndjson_writer.py` directly.
- **NO RECEIPT = NO CLAIM**. A render is "delivered" only when (a) Bash tool output in the session shows the Telegram send response, or (b) a `helen_say.py` receipt binds it. "Operator said it arrived" is hypothesis until verified.
- **Promotion to INVARIANT** requires a second independent session reproducing the pipeline within 10% budget deviation, plus a `helen_say.py` receipt binding `SKILL.md`'s SHA256, plus K2/Rule 3 (the promoting session ≠ the authoring session). Until then, cite as "current working doctrine calibrated from 2026-04-19/20 session."

## Calibrated budget reference

| Phase | Credits | Notes |
|---|---|---|
| 1 Soul seed (720p, 9:16) | ~3 | T2I |
| 1 Seedance Pro I2V (6s, 9:16) | ~10 | I2V premium |
| Full 8-shot teaser | ~90 | 3 seeds + 8 I2V |
| With retry buffer | ~120 | 2–3 re-shoots |
| 3-min music clip on top | +10 | one variety shot only |
| Audio (local synth) / ffmpeg / TikTok cuts | 0 | local |

Failed/NSFW Higgsfield jobs refund automatically. Log per-phase burn — discrepancy >20% means calibration drift; re-measure rather than scaling.
