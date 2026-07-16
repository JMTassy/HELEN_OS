# SECOND_BLOOM_LEGACY_DIGEST

```
mission: GOBLIN_WARREN_SECOND_BLOOM_V0
phase: 0 (Legacy Digest)
authority: false
canon: false
ledger_effect: none
claim_status: NO_CLAIM
final: HOLD_FOR_OPERATOR
ground: git @ origin/main 97bec2d (2026-07-16) + branch claude/init-helen-os-K6LcJ @ 888316a
method: 2 independent repo readers (surface layer / doctrine layer) + keyword archaeology;
        claims below cite files, not transcripts, except where marked PROVENANCE:EXTERNAL
```

The past work is a research brief, not an implementation mandate. This digest
separates what the six Warrens discovered from what they happened to build.

---

## 1. REPOSITORY REALITY

- `main` @ `97bec2d` (today): σ-gate organ-separation tests; `6f7d6bc` (today):
  Warren Home + combat slice + graphism + `/warren` skill + metabolism doctrine.
- Existing Warren surfaces (all preserved, none touched by Second Bloom):
  `apps/goblin-warren/` (HOME + TOWN + combat + graphism),
  `temple/gardens/goblin_garden_conquest/` (garden loop, live_npc, memory grove,
  two more `warren-town.html` sketches).
- 21 branches; relevant siblings: `claude/goblin-swarm-loop-v1`,
  `DAN_RALPH_TEMPLE_SANDBOX`, two `feature/helen-dashboard-*`.
- Second Bloom lives at `apps/goblin-warren-second-bloom/` — new, isolated,
  no dependency on the old runtime.

## 2. WHAT SURVIVED (durable design truth — category A)

1. **DREAMT ≠ CLAIMED.** A goblin's dream/proposal is never world truth until a
   deliberate act consumes it. Enforced today by the operator pen
   (`temple/autoresearch/operator_pen.py`, hash-chained log) and σ₅
   (`src/separation_gate.py`). *Game translation:* delegated action must pass
   through a visible noticing step; nothing resolves by wish.
2. **Delegated agency needs a visible causal bridge.** The entire consumption
   pipeline (scanner → outbox → triage-eye → pen-hand) is "MARK" at
   constitutional scale: the trace changes first, the actor notices second,
   only the actor's act resolves. *This is the product core of Level 1.*
3. **Memory can bloom, but truth is still earned.** Memory Grove v0
   (`goblin_garden_conquest/memory_grove_v0/`) already designed visible memory
   objects — seed · lantern · moss mark · bug label · tiny shrine — each bound
   to a source event, never to truth. Direct ancestor of Level 4.
4. **Grounding-gated NPC speech works.** `live_npc.py` blocks the Stanford
   "Isabella drift": a reflection is admitted only if its evidence exists and
   shares real content with an observation. Deterministic, seeded, no LLM.
   *Game translation:* goblin beliefs must trace to witnessed events.
5. **ZOL — play-value never converts to authority.** Defined in
   `warren_town.html:296`. The game's rewards stay inside the game.
6. **One idea per epoch/level.** Auto-eval garden epochs, tranche discipline,
   and the seven-level campaign all share this law. It survived every rewrite.
7. **Believability ⊬ admissibility** (`GENERATIVE_AGENTS_VS_HELEN_V1.md`).
   The game-facing version: animation ≠ causality unless a state transition
   proves it.

## 3. WHAT FAILED (category D — do not rebuild)

1. **Inspector-as-game.** TOWN's core interaction is click-NPC → read JSON
   card. Correct for a cockpit, dead as play.
2. **Decorative world.** HOME's Canvas village (8 buildings, wandering
   goblins, campfire) renders **zero live data** — a screensaver behind
   meters. The world must BE the interface, not wallpaper next to it.
3. **Two disjoint casts.** HOME's hardcoded roster (MOG/PIP/GRIB/SNAG/ZOOK/
   LURPA/BOGGLE/KRAG, `warren_home.html:246`) shares nothing with the tested
   sprite cast (GOBLIN/HER/CHIDDUSH/…/HAL in `warren_cast_sprites.js`). No
   single source of cast truth ever existed.
4. **Ad-hoc meters.** confiance/humeur/danger are arbitrary formulas over mark
   counts; "bounded [0,100]" was the only invariant.
5. **Orphan slices.** Combat v0 (902 lines, ~27 tests, genuinely good pure-sim
   core) and the graphism gallery were never wired into any loop.
6. **Single-file growth.** 863→936-line HTML files; the mission's "infinitely
   expanding single HTML file" failure is real and repeated.
7. **Broken launcher.** `local_helen_warren.sh` serves the garden dir and
   points at the wrong (non-canonical) `warren-town.html`.

## 4. WHAT CONFLICTED (operator must arbitrate — see Gate 1)

1. **Two successor visions exist in the operator's brief material:**
   - **SECOND BLOOM** (operative mission): web build, verbs MARK/INTERVENE,
     7 levels, Bram/Lulu/Pip, ADHD-first, deterministic agents.
   - **"Tactile new version"** (pasted from another session): mobile-first,
     Level 0 "Touch Hook", blow-into-microphone / shake / tilt sensors, fire
     revival opening, "Wake the dark with your hands."
   These are different products at the input layer. Shared core: the MARK
   causal chain and embodied delegation. **Recommendation:** build Second
   Bloom's causal core with input abstracted behind an event layer
   (`src/core/events`), so tap today can become blow/shake later without
   rearchitecting. Do not attempt microphone/accelerometer in V0.
2. **Organ-driven vs content-driven world.** Old Warren renders *real* HELEN
   autoresearch packets; Second Bloom is a standalone game with authored
   content. This is an identity shift, already sanctioned by the mission's
   final lock (game telemetry ≠ HELEN receipt; local persistence ≠ replay).
3. **Surface duplication was maintained by prose.** app-vs-garden
   `warren-town.html` twins with a "seam note." Second Bloom must be the only
   Warren with its name; no twin sketches.

## 5. WHAT SHOULD BE PORTED (category B — techniques, not code)

| Technique | Source | Port as |
|---|---|---|
| builder → JS sidecar + digest + `--check` byte-replay | `build_warren_feed.py:103` | level/asset build validation |
| Seeded determinism, no `Math.random`, no wall clock | HOME LCG + tests | `src/core/determinism` seeded scheduler |
| DOM-free pure-sim + selftests | `combat_sidequest_v0.js` | all game logic modules DOM-free |
| Fail-visible (`skipped: BAD_JSON`, `BROKEN chain` surfaced) | both builders | level-schema validation fails loud in dev |
| AST/structure predicates as tests | `src/separation_gate.py` | architecture tests: MARK ⊬ resolveNeed, UI ⊬ state mutation |
| Procedural silhouette sprites, seeded | `warren_cast_sprites.js` | placeholder art ONLY, flagged in manifest |
| Grounded-memory gate | `live_npc.py` | Level 4 memory system (belief needs witnessed source) |
| Level-as-sealed-data | auto-eval `epochs/*.json` | strict level schema, unknown fields fail in dev |

## 6. WHAT SHOULD BE LEFT BEHIND

- Live coupling to `temple/autoresearch/` organs (game reads authored content).
- French-only UI (Second Bloom ships reduced-language mode instead).
- Governance vocabulary on the player surface (metabolism, membranes, σ,
  receipts → dev-inspector only, per mission §2/§12). Category E is preserved
  as HELEN doctrine but exits the player's screen.
- The 10-role cognitive cast (HER/CHIDDUSH/HAL…): they are HELEN's organs, not
  game characters. Second Bloom's cast is Bram, Lulu, Pip.
- The `:8133 PLAYABLE WARREN` link and launcher script (dead ends).

## 7. UNRESOLVED PROVENANCE (category F — claims with no repo ground)

| Referenced artifact | Repo status | Consequence |
|---|---|---|
| `ADHD_GARDEN_DESIGN_RULES_V0.md` | **absent** | mission §8's minimum list becomes the authoritative ADHD spec |
| `CANNOT_SAY_SUPPORT_PACKET_V0.md` | **absent** | mission §9's list becomes the authoritative spec |
| `WARREN_ITEM_LIBRARY_V0.md` / larder / bestiary | **absent** (0 hits) | Level 5 objects must be authored fresh; "6 larder + 8 bestiary" counts are targets, not imports |
| Bram / Pip as characters | **absent** (Pip exists only as a HOME roster string) | full character design from scratch |
| Lulu | partial — `memory_grove_v0` teaching/learning slice | port the memory-object concept with her |
| MARK / INTERVENE as implemented verbs | **absent** — prose only | Level 1 is a first implementation, not a port |
| matcha chain | **absent** | Level 3 designed fresh |
| quiz/ZOL knowledge challenges | ZOL law exists; quiz mechanics absent | Level 7 challenge authored fresh; ZOL law inherited |
| `#pluginHELEN.pdf`, pasted markdown, `Le système vivant….png` | external to repo | not citable as ground; ideas usable, provenance recorded as operator-supplied |

**Rule applied:** none of the above is treated as "shipped" because a
transcript said so. Git is the ground.

## 8. ASSET PROVENANCE STATUS (category C)

- `artifacts/goblin_warren_graphism/refs/ref_01..09.png` + `repo_*.jpg|png`:
  in repo; generated via Higgsfield remix (`generate_graphism_hf.sh` holds the
  prompts). Status: **visual reference only** — concept art ≠ playable asset
  (mission final lock). Usable as palette/mood reference in the Phase 2 board;
  each production asset needs its own `assets/manifest.json` entry with
  source_type + generation_prompt_reference.
- Procedural sprite technique: project-owned, provenance clean, placeholder tier.
- No audio assets exist anywhere. Phase 5 hooks start empty.

## 9. VERDICT TABLE (what the mission asked for, in one place)

| | Item |
|---|---|
| **Port** | causal-bridge law, DREAMT≠CLAIMED as game law, memory-grove objects, grounded-belief gate, determinism kit, sidecar+digest builds, architecture tests, ZOL law, one-idea-per-level |
| **Redesign** | cast (one roster: Bram/Lulu/Pip), world-as-interface rendering, needs/traces as first-class modules, combat energy → maybe a Level 6+ contextual event, knowledge challenge in CONQUEST identity |
| **Leave behind** | organ coupling, inspector-first UI, meters, dual casts, single-file HTML, governance vocabulary on player screen, dead launchers |
| **Unresolved** | tactile/sensor input direction (abstract the event layer, decide post-V0); ADHD/CANNOT_SAY specs absent (mission lists become spec); larder/bestiary content authored fresh |

## 10. NEXT (Phase 1, on operator GO)

Playable Level 1 "The Cracked Root" under this directory: modular web build,
seeded scheduler, MARK chain as explicit state transitions
(`dispatch(MARK) → strengthenTrace → perception → orient → move → repair →
resolve`), INTERVENE isolation, hard invariant tests (MARK never directly
resolves; trace peak precedes orientation), local telemetry distinct from any
HELEN receipt. No old-Warren file touched.
