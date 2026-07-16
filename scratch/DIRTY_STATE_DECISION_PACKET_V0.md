# DIRTY_STATE_DECISION_PACKET_V0

NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none · NO_CLAIM
L5 receipt candidate · EGREGOR loop 2026-07-06 · replay: `git status --short` at 572c35b
Receipt-only: this packet mutates nothing. Every disposition below is a JM menu item.

## Paste-vs-disk contradictions (why this packet exists)

| Swarm belief (loop paste) | Disk truth at 572c35b |
|---|---|
| repo 2 commits ahead of origin | ahead = 0, synced |
| CLAUDE.md deletions-only, unauthorized | clean; compression committed+pushed under explicit JM GO (572c35b) |
| generate_meditation.py patched uncommitted | not in dirty set; no such local diff |
| HIVEMIND_TERRARIUM E1–E10 active candidate | zero artifacts in repo (grep temple/ docs/ scratch/ = empty) |

Swarm state-fog is live: agents are reasoning from another machine's tree or a
stale transcript. Verify git, not paste.

## The 64 dirty files, by lane, with proposed dispositions

| # | Lane | Paths (representative) | Proposed disposition |
|---|---|---|---|
| 1 | FIREWALL — live daemon | `town/ledger_v1.ndjson` (M) | LEAVE. Never stash/commit/edit (standing law) |
| 2 | Guard ruling (JM-GO'd, this session) | `tools/kernel_guard.sh` (M), `temple/autoresearch/consumption_log.ndjson` (??) | COMMIT_APPROVED candidate: `fix(guard): operator-ruled CONSUMER_ALLOWLIST +3` — flips Kernel Guard CI green, unfreezes GAS Prop 7.1(b) status flip |
| 3 | Autoresearch consumption organ | `temple/autoresearch/{README,ci_outbox_guard.py,trace_only_autoresearch_loop.py,loops/,triage/}`, outbox `AR-*.json` ×7, `tests/test_outbox_mark.py`, `tests/test_triage_cannot_consume.py` | COMMIT candidate (one lane commit); tests exist — run before commit |
| 4 | Knowledge / vector index | `helen_os/knowledge/ingest.py` (M), `faiss_index.bin`, `helen_os/tests/test_knowledge_vector_*.py`, `docs/reports/{P2_FAISS_HNSW_REPORT.md,VECTOR_INDEX_*.json,BENCHMARK_REPORT.md}` | COMMIT candidate, but JM must rule on `faiss_index.bin` (binary artifact: commit vs .gitignore + rebuild recipe) |
| 5 | Chiddush / metabolism | `tools/{chiddush_compost,chiddush_compressor,fable_jmt_collapse,helen_metabolism}.py`, `prompts/*`, `artifacts/chiddush_compost_demo/`, `scratch/*_ledger.jsonl`, **`schemas/chiddush_receipt_v0.json`** | COMMIT candidate EXCEPT the schema: root `schemas/` placement trips `test_legacy_schemas_directory_is_purged` (the 1 red test in `make test`). NEEDS_JM: relocate to `helen_os/schemas/` via governance path, or exception |
| 6 | Sandbox / GA-adapter | `tools/helen_sandbox_agent_adapter.py`, `docs/proposals/{HELEN_SANDBOX_*,GENERATIVE_AGENTS_VS_HELEN_V1}.md`, `fixtures/sandbox_harvest/`, `artifacts/sandbox_harvest/`, `scratch/Klaus_*.jsonl` | COMMIT candidate (one lane commit) |
| 7 | Garden / Warren | `temple/gardens/goblin_garden_conquest/{conquest_manifest.json(M),js/,warren_loop.py,receipts/,scratch/,test_sprite_lineup.html}`, `oracle_town/skills/conquest/goblin_warren/`, `apps/conquest-rain/`, `artifacts/garden-notes/` | COMMIT candidate; run garden's fail-closed validator first (standing garden law) |
| 8 | Operator surfaces | `apps/helen-surface/{helen2027,temple}.html` (M) | NEEDS_JM: diff unseen by this loop — review before commit |
| 9 | Misc docs / local-first / scaffold state | `TRANSPORT_WUL_RULES_V0.md`, `docs/specs/COLORED_WULMATH_LOGIC_SYSTEM_V0.md`, `docs/reports/DONE_GATE_RECEIPT.md`, `artifacts/{HELEN_PUBLIC_DEMO_DEPLOY_RECEIPT_V0.md,local_first/}`, `prompts/local_first_autoresearch.prompt`, `fixtures/jmt_consulting/`, `helen_os_scaffold/{helen_memory.json,helen_wisdom.ndjson,artifacts/helen_decisions.ndjson}` | Split: docs → COMMIT candidate; scaffold runtime state files → .gitignore candidates (they are session state, not source) |
| — | This loop's own outputs | `scratch/DIRTY_STATE_DECISION_PACKET_V0.md`, `scratch/claude_md_compressed_state.md` (committed) | rides with whichever commit pass JM approves |

## Objection tried (strongest NO)
"This packet duplicates `git status` and wastes a bead." — Refuted: git status
shows 64 undifferentiated lines; the packet adds lane boundaries, per-lane
dispositions, the two live blockers (schema-placement red test, binary index
ruling), and the paste-vs-disk contradiction table that no git command emits.
The swarm demonstrably lacks exactly this: it believed three false state claims.

## Forbidden-path scan
Touched by this loop: `scratch/` only. Ledger/reducer/kernel/canon/doctrine/
CLAUDE.md/deploy: untouched. `town/ledger_v1.ndjson` dirt is daemon-owned,
flagged LEAVE.

FINAL: HOLD_FOR_OPERATOR — every disposition awaits a JM mark.
GPU locals metabolize · FABLE checks receipts · JM admits · 📜 ledger sleeps
