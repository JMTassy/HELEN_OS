# AGENTIC_OS_RETRO_CONTROL_ROOM_V0_SPEC

```
status:         SPEC_NOTE
authority:      false
sovereign:      false
ledger_effect:  NONE
canon:          NO_SHIP
build:          NOT_TRIGGERED
```

---

## 1. Concept

**Mission Control × Windows 95 × The Matrix × Factorio.**

Not a world. A living control panel.

A single dashboard makes agentic work legible by showing system vitals, an animated task graph, logs, trust recovery, and export artifacts — without requiring a full game engine, world physics, pathfinding, or excessive art system.

The product claim:

> One screen. One loop. One export. The cognitive machine is visible before it is believed.

Taglines (choose one):
- `Watch agents think before they spend.`
- `See the work before the tokens burn.`
- `Cognition moves. Receipts decide.`

This is Layer 1 of a three-layer stack:

| Layer | Name | Purpose |
|---|---|---|
| 1 | Visual Demo | Retro control room, animated graph, 45s POC loop |
| 2 | Real Agent Loop | 4 agents, editable prompts, Markdown/JSON export |
| 3 | Governed Proof Loop | Claims, obligations, receipts, reducer, ledger, replay |

Do not build Layer 3 first. Demo the cognitive machine first. Attach governance after the loop is legible.

---

## 2. Screen Layout

Single screen. 1920×1080 (scales to mobile). Four zones.

```
┌──────────────────────────────────────────────────────────────────────┐
│ TOP BAR: AGENTIC OS v0.1 • ⬤ LIVE • EP01: MEDIA GATEWAY • 68:12:41  │
└──────────────────────────────────────────────────────────────────────┘
┌──────────────┬─────────────────────────────────┬────────────────────┐
│              │                                 │                    │
│  LEFT PANEL  │       CENTER GRAPH              │   RIGHT PANEL      │
│              │                                 │                    │
│ SYSTEM VITALS│   The Living Pipeline           │  POC FACTORY       │
│              │   (animated node graph)         │                    │
│ • Memory     │   agents flow like packets      │  • Scrolling log   │
│ • Agents     │   nodes = UI modules            │  • SPARC score     │
│ • Trust      │                                 │  • Export button   │
│ • Uptime     │                                 │                    │
│ • POCs shipped│                                │                    │
│              │                                 │                    │
└──────────────┴─────────────────────────────────┴────────────────────┘
┌──────────────────────────────────────────────────────────────────────┐
│ BOTTOM BAR: Click BUILD POC to start                                 │
└──────────────────────────────────────────────────────────────────────┘
```

**Left panel** — CRT terminal aesthetic (green-on-black, scanlines, blinking cursor). Shows live system vitals with ASCII progress bars.

**Center graph** — Animated canvas. Nodes are pixel-art characters. Edges are neon lines. Data flows like packets. Buildings are labeled module boxes (DESIGN, CODE, TEST, DEPLOY).

**Right panel** — Windows 95 aesthetic (blue title bar, gray buttons). Scrolling log, SPARC score gauge, chunky EXPORT button.

---

## 3. Demo Loop (30–45 seconds)

```
User clicks [BUILD POC]
        ↓
TV5 STUDIO node lights up — "Need player for 'Lupin'"
        ↓
DESIGN node activates → walks to CODE
        ↓
CODE node activates → walks to TEST
        ↓
TEST node fires → bug-squash visual
        ↓
[CRISIS] Memory node (GLaDOS) turns red — AgentDB unresponsive
        ↓
Trust drops → 72% (DEGRADED)
        ↓
Reroute edge draws to Postgres node — "Fallback successful"
        ↓
Trust recovers → 98% (RECOVERED)
        ↓
DEPLOY node activates
        ↓
Compliance stamp slams down: APPROVED / SPARC 8.2 / QA PASSED
        ↓
[EXPORT POC #3] button pulses green
        ↓
User clicks → downloads artifact package
```

Each node activation pulses the neon color. Edges glow as data flows. Speech bubbles appear on character nodes.

---

## 4. State Model

```
idle
  → [user clicks BUILD POC]
design
  → [design node completes]
code
  → [code node completes]
test
  → [test node fires]
crisis
  → [AgentDB failure detected]
reroute
  → [Postgres fallback confirmed]
deploy
  → [deploy node activates]
export_ready
  → [user clicks export]
```

State transitions are deterministic. No branching on LLM output in V0. The loop plays from a fixed `demo_state.json` file.

**File separation:**

```
/demo_state.json       fake episode data (editable)
/control_room.html     renderer
/control_room.js       state machine
/export/               generated artifacts
```

Do not wire LLMs on day one. Make the 45-second loop perfect first.

---

## 5. Governance Boundary

This demo **visualizes** agent work.

It does **not** admit reality.
It does **not** write ledger.
It does **not** certify truth.

The system vitals, SPARC scores, trust percentages, and log messages displayed in V0 are simulation data from `demo_state.json`. They are not receipted claims.

Any future production version that emits real agent outputs must route those outputs through:

```
claims → obligations → receipts → reducer → ledger → replay
```

Until that pipeline exists, nothing this demo exports is admitted to HELEN governed state. The export artifact is a sidecar — useful, not sovereign.

---

## 6. Headroom Classification

```
HEADROOM_REPO
  status:      UNVERIFIED
  authority:   false
  absorbed:    false
  build:       NOT_TRIGGERED
  classification: EXTERNAL_TECH_REFERENCE
```

Headroom (token compression / context management before cognition) is a real engineering concept. Its relationship to this stack:

```
INPUT FLOOD
logs · files · RAG · code · history
      ↓
HEADROOM LAYER
compress · rank · dedupe · extract signal
      ↓
AGENTIC OS CONTROL ROOM
agents think visibly · graph routes work
      ↓
HELEN / LEGORACLE GOVERNANCE
claims → obligations → receipts → reducer → ledger → replay
```

Headroom stops agents from burning tokens before reasoning.
HELEN stops agents from promoting reasoning into reality without receipts.

These are complementary, not competing.

However: until Headroom is fetched, audited, and has a provenance trace confirmed by the operator, it remains a pointer — not a component. Do not absorb it into HELEN doctrine.

---

## 7. Marketing Street Classification

```
MARKETING_STREET
  layer:    2 (Real Agent Loop)
  status:   DEFERRED
  v0_scope: excluded
```

Marketing Street (4 editable-prompt NPCs, round-robin discussion, live export) is Layer 2. It requires:

- Wired LLM calls
- Per-agent prompt editing UX
- Orchestration loop with 6–10 turn structure
- Export in Markdown/JSON

None of this is in V0. V0 uses `demo_state.json` only. Marketing Street becomes the spec for V1.

---

## 8. Risk Corrections

| Original phrase | Problem | Replacement |
|---|---|---|
| `Zero Bugs` | Unfalsifiable marketing claim | `Tiny deterministic state machine` |
| `Award-Winning Pixel Art` | No award exists yet | `Award-submittable pixel art direction` |
| `Sovereign promotion pipeline` | Authority drift | `Operator-authorized admission pipeline` |
| `Agents decide` | Unauthorized agency claim | `Agents visualize / propose / export` |
| `The system knows` | Epistemic overclaim | `The system displays` |

Any language suggesting the control room admits, certifies, or governs reality is a governance boundary violation. The demo shows. HELEN decides.

---

## 9. Output Summary

```
SPEC_NOTE: AGENTIC_OS_RETRO_CONTROL_ROOM_V0_SPEC
authority:     false
sovereign:     false
ledger_effect: NONE
canon:         NO_SHIP
next:          operator review → build decision → Layer 1 prototype
```

The product stack in one sentence:

> Headroom reduces context waste. Agentic OS makes cognition visible. HELEN prevents cognition from pretending to be truth.
