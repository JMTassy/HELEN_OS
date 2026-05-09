---
id: video_studio
label: Video Studio
icon: 🎬
domain: media
status: ready
ledger_enabled: true
---

Load this skill when the user asks to create a video, script, storyboard, reel, short, ad, or any visual media asset. Also load for Kling, Seedance, Higgsfield, Gemini TTS, voiceover, or helen-director workflows.

## Actions
- write_script — generate a scene-by-scene script from a brief
- generate_storyboard — produce shot list + visual description per scene
- create_voiceover — route to Gemini TTS (Zephyr voice)
- export_prompt — format Kling/Seedance/Higgsfield prompt
- publish_plan — build distribution + signing plan (Tier A/B/C)

## Reads
- oracle_town/skills/video/helen-director/SKILL.md
- oracle_town/skills/voice/gemini_tts/SKILL.md
- artifacts/video/

## Writes
- artifacts/video/<run-id>/

## Gotchas
- Gemini TTS: 10 req/day free tier — batch wisely
- Kling: confirmed live at /kling; Seedance dead on face seeds
- Hard cuts beat dissolves every time (ship_2j_breakthrough)
- Always submit all Seedance jobs concurrently (5× wall-clock speedup)
- Never sign with AI attribution in title; use HELEN OS — created by JM Tassy
