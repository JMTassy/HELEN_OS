---
id: research_brief
label: Research
icon: 🧠
domain: intelligence
status: ready
ledger_enabled: true
---

Load this skill when the user asks for research, competitive intelligence, strategic synthesis, benchmark analysis, market scan, or any knowledge-gathering mission.

## Actions
- run_scan — gather information on a topic or competitor
- synthesize_brief — compress findings into a structured brief
- build_benchmark — compare options across defined criteria
- extract_signals — identify key trends or risks from a corpus
- write_report — produce a formatted research report

## Reads
- oracle_town/skills/ops/research_brief/references/synthesis_format.md
- helen_os/knowledge/

## Writes
- artifacts/research/<brief-id>/

## Gotchas
- Research output is NON_SOVEREIGN until MAYOR reviews
- Always cite sources; never synthesize from GOBLIN epochs without HAL gate
- Symbolic text (sacred, mythic) must route through voice_transcript_ingestion skill first
