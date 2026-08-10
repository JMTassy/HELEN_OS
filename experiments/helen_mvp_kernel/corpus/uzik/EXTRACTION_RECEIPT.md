# UZIK CORPUS EXTRACTION — RECEIPT (V1)

🔵 OBSERVED · NON_SOVEREIGN · authority=0 · not admitted · no ledger effect
Operator directive "START A DEEP UZIK CORPUS EXTRACTION FOR HELEN OS UPGRADE" @ 7c0ff88

## What was done
Deep sweep of the SOT for UZIK / brand-voice material, then a consolidated,
deduplicated extraction into one machine-consumable corpus:
`experiments/helen_mvp_kernel/corpus/uzik/UZIK_CORPUS_V1.json`
(sha256 `d60c6deac40fc9ae455f86f9bff40eb2b47d78b4a534a70911d098fab2581fde`, valid JSON, 17 top-level keys).

The corpus is the single source of truth a HELEN `brand_voice` skill/gate can read to enforce
UZIK register on HELEN-generated copy — the "upgrade" utility. It carries: essence, DNA, the two
registers (SYSTEM terse / BRAND editorial), 7 core rules (each with a check), use/ban vocabulary,
production verbs, phase/status/ownership markers, structures (short / long / deck rhythm / timeline /
approval / escalation), slide pacing, FR-EN mixing + glossary, headline logic, the verbatim brand
tagline family + DNA four-beat + culture-pop naming law, design tokens (palette / type / layout /
motion / imagery), the governance stamp, 11 anti-patterns, and a 10-item lint checklist.

## Sources extracted (sha256, current frame)
- `docs/style/uzik-writing-style.md`        `bfb757841ebfb890579ff22ef2caa159b892e98c74d6ec85246c0c8773180dcd`
- `docs/style/uzik-structure-patterns.md`   `5f8168ec6f54108dcff750e1c6721d4c9e97b35bcababf18a2b977cc5989aac4`
- `docs/style/uzik-copy-examples.md`         `443ce9d6928790ad9a87127d925cd37be5b388e3ebf58483bf2819ea2204a4fa`
- `experiments/uzik_design_system/DESIGN.md` `2ec8f4835700c5f35a443c1b9a4a7af3a97b1b54489e56571648e167b584aa4b`

## Discipline applied
- Client entity names genericized to CLIENT / BRAND (never-name discipline for pushed artifacts).
  UZIK retained — it is the operator's own studio (uzik.com), not on the never-name list.
- Taglines reused VERBATIM from the sourced UZIK Communication Guidelines (2018). No new taglines invented.
- Palette / typography values carried as session-keyed placeholders — flagged for reconciliation
  with UZIK's official brand book before any promotion.
- Negative parallelism recorded as a hard-ban anti-pattern (operator style rule).

## Honest residuals / not done
- **Not yet enriched from external sources.** The source docs are marked DRAFT with "enrich from
  Drive / Gmail." This extraction consolidates only what is physically in the SOT @ 7c0ff88 —
  it does NOT reach Drive, Gmail, or `~/helen_kernel/campaign_0002/UZIK_CORPUS_V1.md` (referenced
  but outside this checkout). Pulling those is a separate, network/authorized step.
- **No brand_voice gate built yet.** The `lint_checklist` is data, not an executable linter. Turning
  it into a HELEN gate (fail-closed on banned vocabulary / negative parallelism / unsourced metrics)
  is the natural next tranche if you want enforcement, not just reference.
- **Palette/type are placeholders**, not the official brand book — do not treat as canonical color/type.
- NON_SOVEREIGN, uncommitted, not pushed. Held for a COMMIT / PUSH verb.
