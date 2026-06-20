# CONQUEST WORLD SIM — Beginner Guide

```
authority : false
sovereign : false
canon     : false
layer     : TEMPLE
ledger    : SLEEPING
```

---

## 1. What CONQUEST is

CONQUEST is a simulation world living inside TEMPLE.

It is not HELEN's governance system.
It is not the ledger.
It is not real history.

It is a **training world** — a place where agents (ROSE, CROSS, VEIL, WARDEN) learn
how power actually works: through effort, proof, and receipts — never through desire alone.

One rule governs everything:

> **You do not get power because you want it.**
> **You get power because you completed a quest and produced a receipt.**

The world keeps running. Nothing it produces touches the sovereign ledger.

---

## 2. The Five Core Symbols

| Symbol | Name      | Meaning                                |
|--------|-----------|----------------------------------------|
| 📚     | Knowledge | What you learn — a pattern, a law, a clue |
| 🎯     | Quest     | A task that proves you learned it      |
| 🧾     | Receipt   | Proof that the quest was completed     |
| 🛡️      | Control   | Earned influence over territory or resource |
| 👑     | Power     | Earned capability — score, rank, capacity |

The chain is always left-to-right:

```
📚 → 🎯 → 🧾 → 🛡️ → 👑
```

You cannot skip steps. No receipt, no control. No control, no power.

---

## 3. The Color Ladder

Colors describe the state of an artifact or action — not its importance.

| Color | Meaning                            | Use in CONQUEST                     |
|-------|------------------------------------|-------------------------------------|
| 🔵    | Building / in progress             | Action is being resolved            |
| 🟣    | Proposed / seeded                  | Quest or resource proposed          |
| 🟢    | Local pass / valid                 | Action succeeded this turn          |
| 🟡    | Pending / blocked                  | Resources missing, waiting          |
| 🔴    | Failed / skipped                   | Action could not execute            |
| ⚫    | Void / absent                      | Territory unclaimed, null state     |

**Critical rule:** 🟢 means **local pass**, not admission.
🟢 inside TEMPLE never means "admitted to HELEN canon."

What it means in practice:

```
🟢 🌹 QUEST_STEP → receipt written → score +5
```

This is a local simulation success. The ledger does not know it happened.

---

## 4. The Trust Pipeline

Every action in CONQUEST follows this pipeline:

```
LEARN      →  PROVE     →  RECEIPT   →  CONTROL   →  POWER
📚         →  🎯        →  🧾        →  🛡️         →  👑
(observe)     (attempt)    (confirm)    (territory)   (rank/score)
```

Each step requires the previous one. The pipeline is **one-way**.

No shortcuts:

| Forbidden path           | Why it fails                            |
|--------------------------|-----------------------------------------|
| 👑 without 🧾           | Power without proof — invalid           |
| 🛡️ without 🎯           | Control without attempt — invalid        |
| 🧾 without 📚           | Receipt without learning — invalid       |
| 👑 = HELEN admission     | Simulation score ≠ sovereign authority  |

The pipeline runs **inside the simulation only**. It never crosses into HELEN governance.

---

## 5. One Example Turn

**Faction: ROSE (quest-focused)**

```
Turn 45
────────────────────────────────────────────
PHASE 1  Read world state
         ROSE resources: QUINT_CORE=3

PHASE 2  Choose action
         Personality=QUEST_FOCUSED → QUEST_STEP

PHASE 3  Check resources
         QUEST_STEP costs 1 QUINT_CORE → OK

PHASE 4  Apply action
         quest_progress += 1
         score.quest += 5

PHASE 5  Write session_log
         appended 1 line (non-sovereign, local only)

PHASE 6  Render WULmoji surface
         🟢 🌹 📚->🎯->🧾->🛡️->👑  🔗#SIM-T0045  📜⏸️

PHASE 7  Ledger sleeps
         town/ledger_v1.ndjson — not touched
────────────────────────────────────────────
```

What ROSE learned: completing quests costs QUINT_CORE.
QUINT_CORE comes from holding HOME_KEEP.
HOME_KEEP is the only territory ROSE starts with.
Every 20 turns the elemental cycle shifts, changing what's available.

The world teaches through consequence, not instruction.

---

## 6. What is Forbidden

CONQUEST is a simulation. Certain crossings are permanently blocked:

| Action                          | Status   | Reason                              |
|---------------------------------|----------|-------------------------------------|
| Write to `town/ledger_v1.ndjson` | 🚫 BLOCKED | Sovereign path — HELEN only          |
| Set `authority: true`           | 🚫 BLOCKED | Only MAYOR/operator can authorize   |
| Set `canon: true`               | 🚫 BLOCKED | Only gate passage admits to canon   |
| Call a real LLM API             | 🚫 BLOCKED | Engine is seeded-deterministic only |
| Git commit / push               | 🚫 BLOCKED | Requires explicit operator GO       |
| Claim HELEN approval            | 🚫 BLOCKED | `HELEN_APPROVED` forbidden string   |
| Promote simulation score to rank | 🚫 BLOCKED | Sim rank ≠ HELEN governance rank    |

The containment boundary:

```
🏰 (simulation)  ≠  📜 (sovereign ledger)
```

Everything that happens in CONQUEST stays in CONQUEST's `session_log.ndjson`.
It does not cross the membrane.

---

## 7. Final Beginner WUL

The full CONQUEST law compressed to one chain:

```
🌿 enter the garden
🏰 simulate — do not claim
📚 learn a pattern
🎯 attempt a quest
🧾 produce a receipt
🛡️ earn control
👑 earn power inside the simulation only
📜 ⏸️  ledger sleeps
```

WULmoji surface — one turn, one faction, one pipeline:

```
🟢 🌹 📚->🎯->🧾->🛡️->👑  📜⏸️
AUTH=false  SOV=false  CANON=false
```

The world is alive.
The ledger is sleeping.
Power is earned, not declared.

---

## 8. Higher-Dimensional Map

For the full math/WUL doctrine, see:

```
doctrines/high_dimensional_wul_language.md
```

The beginner version is:

```
HELEN x CONQUEST x WULMOJI
= cognition x memory x gate x reducer x ledger x symbolic surface
```

CONQUEST is allowed to simulate the path:

```
Knowledge -> Quest -> Receipt -> Boundary -> Power
```

But it is not allowed to shortcut into real memory:

```
Symbol -> Ledger  BLOCKED
Knowledge -> Power  BLOCKED
Simulation -> Judgment  BLOCKED
Impulse -> Law  BLOCKED
```

The safe route is always:

```
Symbol -> Pattern -> Validator -> Receipt -> Boundary -> Judgment -> Ledger
```

Inside this garden, that route is practiced only as simulation. The ledger
still sleeps until an external review admits something.

---

*BEGINNER_GUIDE.md — TEMPLE layer — NON_SOVEREIGN — authority: false — canon: false*
