# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Scope: the **Goblin Warren** subsystem — the playable CONQUEST Garden surface. The
repo-root `CLAUDE.md` (`~/Documents/GitHub/helen_os_v1/CLAUDE.md`) and global policy
(`~/.claude/CLAUDE.md`) still bind here. This file adds only what is specific to the Warren.

## What This Is

The Warren is a **NON_SOVEREIGN Garden surface**: a static, server-less player shell that
*renders* HELEN's live autoresearch organs as a goblin town. It is skin over state — it
displays proposals and operator decisions, it can never make them.

The single law of this subsystem, enforced in code and tests:

> **SURFACE CANNOT MARK.** The surface displays organs; it never writes them.
> `dream shown ⊬ dream admitted` · `meter ⊬ state` · `NPC carries packet ⊬ packet admitted`.

Everything here carries `authority=false · sovereign=false · canon=false · ledger_effect=none`.
Marks happen **only** through `temple/autoresearch/operator_pen.py` — never from any HTML or builder here.

## The Three Parts

The Warren spans three directories. Know which is which:

| Path | Role |
|---|---|
| `apps/goblin-warren/` | **Surface.** Builders (`build_warren_*.py`) + generated JS sidecars + HTML shells. This directory. |
| `temple/gardens/goblin_garden_conquest/` | **Garden.** The CONQUEST world model, `warren_loop.py` game loop, epochs, receipts, `validate_conquest_garden.py` (fail-closed). |
| `oracle_town/skills/conquest/goblin_warren/` | **Skill.** `SKILL.md` + `cli.py` — the `/warren` operating mode encoding (Garden ADMIT ≠ Kernel ADMISSION). |

Two surfaces exist, fed by two builders — they are **not** interchangeable:

- **TOWN** (`warren_town.html` ← `warren_town_feed.js` ← `build_warren_feed.py`): the full proposal
  feed. NPCs (goblin role-bodies) *carry* outbox packets; HAL is a lantern, never a courier.
- **HOME** (`warren_home.html` ← `warren_home_data.js` ← `build_warren_home.py`): the player shell —
  unconsumed proposals as "dreams," operator marks as `carnet`/`histoire`, bounded meters.

## Data Flow (the organs)

Both builders read the **same live organs** and emit a static `window.*` JS sidecar the HTML
loads over `file://` (no server, no fetch, no external assets):

```
temple/autoresearch/outbox/AR-*.json        (AUTORESEARCH_PACKET_V1)  → dreams / feed
temple/autoresearch/consumption_log.ndjson  (operator_pen, hash-chained) → marks / carnet
        │
        ├─ build_warren_feed.py  → warren_town_feed.js  (window.WarrenFeed, WARREN_FEED_V0)
        └─ build_warren_home.py  → warren_home_data.js   (window.WARREN_HOME, WARREN_HOME_DATA_V1)
```

- A packet is a **dream** only if it has **no** effective operator mark (`pen.effective_decisions`).
- `build_warren_home.py` imports `operator_pen` (as `pen`) to read the chain — it calls **read**
  helpers only (`read_log`, `verify_chain`, `effective_decisions`, `load_packets`), never `mark`.
- Meters (`confiance`, `humeur`, `danger`, `ferraille`, `nourriture`) are **bounded [0,100]
  renderings** derived deterministically from mark counts. They are labeled as renders in the UI.

## Invariants the code and tests enforce

1. **Deterministic.** Same organ bytes → same sidecar bytes. No wall clock, no `Math.random`
   (seeded RNG only in HTML). This is a **local replay witness**, not decoration.
2. **Fail-visible.** An unreadable packet → `skipped: [{... BAD_JSON}]`, never silently dropped or
   synthesized. A tampered pen chain → `pen_chain: "BROKEN: ..."`, surfaced not hidden.
3. **No mark controls in HTML.** The home HTML must contain none of `--mark`, `data-decision`,
   `admit(`, `mark(`, `name="decision"`, `reducer_decision`; must contain the literal
   `SURFACE CANNOT MARK`; must carry the French law text (`Les Gobelins rêvent`, `Vous décidez`,
   `rêve affiché ⊬ rêve admis`, `Chaque choix compte`, …). Tests assert these strings verbatim —
   changing UI copy means updating `helen_os/tests/test_warren_home_builder.py`.
4. **No green-as-written.** No sidecar or HTML may render `CONQUEST IS ADMITTED`. Garden ADMIT is
   not kernel admission (see WULMOJI rule in root `CLAUDE.md`).

## Commands

```bash
# Rebuild the sidecars from live organs (run from repo root)
python3 apps/goblin-warren/build_warren_feed.py            # → warren_town_feed.js
python3 apps/goblin-warren/build_warren_home.py            # → warren_home_data.js

# Replay witness — re-derive and diff against on-disk sidecar (CI-shaped gate)
python3 apps/goblin-warren/build_warren_feed.py --check    # CHECK PASS / CHECK FAIL
python3 apps/goblin-warren/build_warren_home.py --check    # ✅ / ❌ REPLAY MISMATCH

# Tests (part of `make test`)
.venv/bin/pytest helen_os/tests/test_warren_feed_builder.py helen_os/tests/test_warren_home_builder.py -v

# View a surface — open the HTML directly, no server needed
open apps/goblin-warren/warren_home.html      # or warren_town.html

# The /warren game loop (Garden simulation only — see the skill)
python3 temple/gardens/goblin_garden_conquest/warren_loop.py --goal "..."
python3 -m oracle_town.skills.conquest.goblin_warren.cli enter --goal "..."

# Fail-closed Garden validator — run before editing garden content
python3 temple/gardens/goblin_garden_conquest/validate_conquest_garden.py
```

**After editing a builder, regenerate its sidecar and run `--check`** — a stale `.js` fails the
replay witness and the tests. The generated sidecars carry a `DO NOT EDIT / DO NOT HAND-EDIT`
banner; edit the builder, never the `.js`.

## Editing rules

- These files are non-sovereign and freely editable, **but** `temple/autoresearch/outbox/*` and
  `consumption_log.ndjson` are the operator's organs — read them, never write them from here.
- The membrane is the point of the whole subsystem. Any change that lets the surface mark, admit,
  or mutate state — or that makes a meter authoritative — breaks the design, not just a test.
- Keep the surface self-contained: no external `http(s)` assets, no network fetch. The HTML must
  load only its co-located generated sidecar.
