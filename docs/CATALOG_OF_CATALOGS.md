# CATALOG OF CATALOGS
Generated: 2026-06-11 | HEAD: 9b21a48 | Branch: main

Single authoritative inventory of every major subsystem in this SOT.
One row = one system. Status codes defined at the bottom.

---

## SOVEREIGN — firewall-protected, no writes from Claude Code

| Name | Location | Validator | Last commit | Notes |
|---|---|---|---|---|
| Kernel daemon + gates A/B/C | `oracle_town/kernel/` | — | c196249 | Unix socket daemon, sovereign verdicts only |
| Append-only ledger | `town/ledger_v1.ndjson` | `tools/kernel_guard.sh` | live (dirty) | Hash-chained; `helen_say.py` is the only admitted writer |
| Governance layer | `helen_os/governance/` | `make test` | 183b2e4 | Schema registry, validators, LEGORACLE gate, skill promotion reducer |
| Schema files | `helen_os/schemas/` | `make test` | 183b2e4 | 47 files, 100% governance-indexed; `additionalProperties: false` |
| Closure receipts | `GOVERNANCE/CLOSURES/` | ghost-closure test | 183b2e4 | CLOSURE_RECEIPT_V1 only; strict format |
| Tranche receipts | `GOVERNANCE/TRANCHE_RECEIPTS/` | — | 183b2e4 | TRANCHE_SUB_RECEIPT_V1; one hypothesis per epoch |
| Constitution docs | `GOVERNANCE/CONSTITUTION/` | — | 183b2e4 | KERNEL_V2, SOUL, HELEN, KERNEL_K_TAU_RULE |
| Mayor key registry | `mayor_*.json` | — | — | Key rotation, ceremony audits; SOVEREIGN |

---

## PRODUCTION — active, tested, gate-verified

| Name | Location | Test suite | Last commit | Notes |
|---|---|---|---|---|
| HELEN OS sovereign tree | `helen_os/` | `make test` → 43 test files | 183b2e4 | Executor, autonomy, evolution, knowledge, render; **do not edit** outside `experiments/` |
| K-gate lint scripts | `scripts/helen_k8_lint.py`, `helen_k_tau_lint.py`, `helen_rho_lint.py`, `helen_wul_lint.py` | — (scripts are the validators) | c196249 | K8/K-tau/K-rho/K-wul; run and report verbatim |
| WUL Packet Validator | `src/wul_packet_validator.py` | `tests/test_wul_packet_validator.py` (29 tests) | 67803cd | P1 compile-time; fails closed; PERM::WRITE_SOVEREIGN always rejected |
| WULmoji Ledger Validator | `tools/wulmoji_ledger_validator.py` + `docs/wulmoji_ledger_spec.md` | `tests/test_wulmoji_ledger_validator.py` (79 tests) | c196249 | Grammar: STATE FACTION PAIR ACT PROOF RIBBON |
| SOURCEBOUND OBJECT OS | `src/helen_sourcebound_object.py` + `tools/helen_object.py` | `tests/test_helen_sourcebound_object.py` + `tests/test_helen_object_cli.py` | f3e3887 | Every object bound to source bytes with receipt; ADMISSIBLE OBJECT COMPUTING V1 |
| Constitutional invariant tests | `tests/test_1_*.py` … `tests/test_9_*.py` | `.venv/bin/pytest tests/ -q` | c196249 | 9 numbered invariants; **not** covered by `make test` |
| Root tests | `tests/` (51 test files total) | `.venv/bin/pytest tests/ -q` | c196249 | Includes WUL, sourcebound, kernel, conquest, identity, claim-type gate |
| Canonical writer bridge | `tools/helen_say.py` | — | — | Only admitted path to ledger; computes payload_hash |
| HELEN CLI | `tools/helen_cli.py` | — | — | Interactive sovereign-routed CLI |
| Telegram bot + voice | `tools/helen_telegram.py` | — | 786686f | Two-way, HER_TEMPLE_PRESENCE_V1 `/her` command, Groq fallback |
| Web UI | `tools/helen_simple_ui.py` | — | — | localhost:5001, voice via Gemini TTS |
| Gemini TTS (Zephyr voice) | `oracle_town/skills/voice/gemini_tts/` | — | — | LIVE; Gemini 2.5 Flash |
| Skills: map, meteo, claim, ledger | `oracle_town/skills/` (core) | `tests/test_map_generator_skill.py`, `test_meteo_skill.py` | c196249 | Canonical skills; feynman (peer_review, intent_audit, session_notes) also here |
| Operator surface | `apps/helen-surface/` | — (UI, no tests) | cc962ad | home_v1.html, helen2027.html, temple.html, cockpit_v4.html; `helen_status_api.py` |
| DAN/RALPH epoch runner | `scripts/ralph/ralph.sh` + `oracle_town/skills/ops/dan_goblin/` | — | 95f27b6 | HD-001 GREEN; HD-002/HD-003 TODO; DAN receipts in `receipts/`, scratch gitignored |
| Non-sovereign HAL inference | `tools/hal_driver.py` + `tools/run_hal_epoch.py` | `tests/test_hal_epoch_gate.py` | 365ed25 | Local Ollama qwen3.6; produces proposals not verdicts |
| action_preflight_guard | `experiments/helen_action_guard/` | 73 tests (own suite) | 7a99525 | K-TAU negative-capability patch; uncertainty blocks mutation |

---

## NON-SOVEREIGN SANDBOX — non-sovereign, authority=false, no auto-promotion

| Name | Location | Validator | Last commit | Notes |
|---|---|---|---|---|
| MVP kernel gates | `experiments/helen_mvp_kernel/` | 8 test files; venv `.venv-gates/` | 7a99525 | Face motion, AV sync, spectral, composite; NON_SOVEREIGN / NO_SHIP |
| Temple gardens | `temple/gardens/` | `validate_avalon.py` (per-garden) | 9b21a48 | 3 gardens: goblin_meditation_center, goblin_garden_conquest, goblin_garden_conquest_avalon |
| Temple subsandbox | `temple/subsandbox/` | — | d75313b | aura grimoire, codex_pilot, gemma_director, goblin; never auto-promoted |
| CWL v0.2.1 EMOGLYPH spec | `temple/gardens/goblin_garden_conquest_avalon/doctrines/cwl_v021_spec.md` | (part of garden validator) | 9b21a48 | FROZEN; CLAIM_TYPE: draft_doctrine; authority=false |
| Video: helen-director | `oracle_town/skills/video/helen-director/` | — | 18c4eb6 | Montage Engine + STORYBOARD_V1 + ASSET_ENGINE_V1; helen_awakening v1/v2 |
| Video: HyperFrames | `oracle_town/skills/video/hyperframes/` | — | — | DECLARED; npm allowlist pending |
| Video: math_to_face | `helen_os/render/math_to_face.py` + `math_to_face/SKILL.md` | — | — | SCAFFOLD Phase 0-9 roadmap; φ-SDE pipeline |
| Video: library | `oracle_town/skills/video/library/` | — | — | 11 hero stills, era axis locked |
| helen_os_v02 | `experiments/helen_os_v02/` | — | — | Exploratory; unclear status |
| qfse_bridge | `experiments/qfse_bridge/` | — | — | Exploratory; unclear status |
| helen_video | `experiments/helen_video/` | — | — | Video experiment sandbox |

---

## REFERENCE — scaffold, older versions, docs, proposals

| Name | Location | Notes |
|---|---|---|
| helen_os_scaffold | `helen_os_scaffold/` | Separate venv; hosts `helen talk`/`helen chat` CLI + LLM adapters; 51 test files (epoch1-4, autoresearch); last touched: 0035d7a |
| helen_dialog | `helen_dialog/` | Dialog engine, HER/AL moment detection; 10 test files; last touched: 1bff42b |
| helen_os_mvp | `helen_os_mvp/` | Older MVP snapshot; 1 test file; last active: 216a58d |
| Docs: proposals | `docs/proposals/` | PROPOSAL-class artifacts; not canon; last touched: 0574b43 |
| Docs: specs/protocols/theory | `docs/specs/`, `docs/protocols/`, `docs/theory/` | Reference material; not enforced |
| Model routing | `docs/spec/MODEL_ROUTING_V1.md` | Role-fit model assignment; NON_SOVEREIGN |
| Autoresearch program | `docs/AUTORESEARCH_PROGRAM_V1.md` | E11/E12 reconciliation pending MAYOR ruling; E13 blocked |
| Governance regression tests | `tests/governance_regression/` | 6 files: amendment_intake, determinism_k5, doctrine_enforcer, k_gates, npc_constraints |
| formal/ | `formal/test_invariants_empirical.py` | Empirical invariant tests; last touched: 216a58d |
| schemas/helen_dan/ | `schemas/helen_dan/` | DAN/RALPH schemas; pending migration to `helen_os/schemas/` |
| GOVERNANCE/REGISTRIES | `GOVERNANCE/REGISTRIES/` | Governance registries |
| GOVERNANCE/STEP_4_CONFORMANCE | `GOVERNANCE/STEP_4_CONFORMANCE/` | Conformance artifacts |
| ops/runs | `ops/runs/` | Run records |
| receipts/ | `receipts/` | Miscellaneous receipts not under GOVERNANCE/ |
| oracle_town_proto/ | `oracle_town_proto/` | Earlier oracle_town prototype; superseded |
| helensh/ | `helensh/` | Shell tools; sovereign/ + tools/ |

---

## HISTORICAL — archived, superseded, do not edit

| Name | Location | Notes |
|---|---|---|
| deprecated/ | `deprecated/` | _archive, oracle-superteam tests, conquest/kernel tests; last touched: 216a58d (E22 purge) |
| helen_kernel/ | `helen_kernel/` | Older kernel + gates; superseded by oracle_town/kernel/ |
| helen_os_scaffold/Star-Office-UI/ | `helen_os_scaffold/Star-Office-UI/` | UI prototype; superseded |

---

## EXTERNAL CATALOG (not in SOT)

| Name | Location | Notes |
|---|---|---|
| PLUGINS_JMT_CATALOG_V1 | `~/Desktop/oracle_town/PLUGINS_JMT_CATALOG.json` | 133 docs, 3.2M words, generated 2026-06-04; NON_SOVEREIGN · LOCAL_ONLY · not admitted canon; categories: frameworks(73), latex(6), cross_theories(54) |

---

## Status codes

| Code | Meaning |
|---|---|
| SOVEREIGN | Protected by firewall; no writes from Claude Code ever |
| PRODUCTION | Active, tested, runs in real operations |
| NON_SOVEREIGN SANDBOX | authority=false; no auto-promotion; JM admits |
| REFERENCE | Scaffold, older versions, docs; read for context |
| HISTORICAL | Archived; superseded; do not edit |

---

## What has tests

| Suite | How to run | File count | Last known pass |
|---|---|---|---|
| `helen_os/tests/` | `make test` | 43 | 183b2e4 |
| `tests/` (root) | `.venv/bin/pytest tests/ -q` | 51 | c196249 |
| `helen_os_scaffold/tests/` | separate venv | 51 | 0035d7a |
| `helen_dialog/tests/` | `.venv/bin/pytest helen_dialog/tests/` | 10 | 1bff42b |
| `experiments/helen_mvp_kernel/helen_os/tests/` | `.venv-gates/bin/pytest` | 8 | 7a99525 |
| `experiments/helen_action_guard/` | own suite | ~73 | 7a99525 |
| `tests/governance_regression/` | `.venv/bin/pytest tests/governance_regression/` | 6 | c196249 |

---

## Three biggest inventory risks (as of 2026-06-11)

1. **Symbolic inflation** — names, worlds, roles generated faster than tested functionality. Governance metaphors (HELEN=Judge, HERMES=Builder) are conventions, not enforced permissions.
2. **Governance theater** — roles feel enforced when they are prompts and policy only. Real enforcement = firewall hooks (planned, not yet wired for all paths).
3. **Inventory collapse** — corpus large enough that draft / tested / committed / experimental / historical / production can become indistinguishable. This catalog is the mitigation.

---

*This file is read-only reference. It does not govern anything. Update it when systems are added, promoted, or deprecated.*
