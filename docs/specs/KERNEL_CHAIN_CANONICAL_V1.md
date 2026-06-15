---
authority: NON_SOVEREIGN
canon: REFERENCE
lifecycle: CANONICAL_SPEC
source: JM_TASSY_2026-06-15
status: KERNEL_CHAIN_CANONICAL_V1
---

# Kernel Chain — Canonical V1

Minimum complete admission pipeline for HELEN OS.
Authored by JM Tassy, 2026-06-15.
Supersedes partial descriptions in KERNEL_TO_AGENTIC_OS_DEEP_DIVE_V0.md.

---

## Flowchart

```
flowchart TD
  A[Raw Idea / Paste / Artifact] --> B[CLASSIFY]
  B --> C[EXTRACT CLAIMS]
  C --> D[CRITIC]
  D --> E[OBLIGATIONS]
  E --> F[RECEIPTS]
  F --> G[REDUCER]
  G -->|ADMIT| H[LEDGER]
  G -->|NO_SHIP| X[REJECT / SANDBOX]
  H --> I[REPLAY]
  I --> J[WITNESS]
  J --> K[UI SHELL]
  K --> L[AGENTS / PRODUCT]
  M[Headroom] -->|compresses context only| L
  N[Control Room] -->|visualizes only| K
  O[Marketing Street] -->|drafts only| L
  K -. cannot admit .-> G
  L -. cannot decide .-> G
  N -. demo_state only .-> X
```

---

## WUL Expression

```
🧠 idea
→ 🔍 classify
→ 🧾 claim
→ ⚔️ critic
→ 📋 obligation
→ 🧾 receipt
→ ⚖️ reducer
→ 📜 ledger
→ 🔁 replay
→ 👁️ witness
→ 🖥️ UI
→ 🤖 agents
```

---

## Central Law

```
UI shows.
Agents propose.
Receipts prove.
Reducer admits.
Ledger remembers.
Replay verifies.
```

---

## Node Responsibilities

| Node            | Can do                             | Cannot do                        |
|-----------------|------------------------------------|----------------------------------|
| CLASSIFY        | label artifact class               | decide admission                 |
| EXTRACT CLAIMS  | structure assertions               | assert truth                     |
| CRITIC          | detect vague/unfalsifiable claims  | reject without reason            |
| OBLIGATIONS     | define proof criteria per claim    | satisfy themselves               |
| RECEIPTS        | bind evidence to obligation_name   | create authority                 |
| REDUCER         | ADMIT or NO_SHIP                   | negotiate, feel, narrate         |
| LEDGER          | append admitted events             | revise, delete, decide           |
| REPLAY          | prove state from ordered events    | decide, correct, replace reducer |
| WITNESS         | compare runtime vs replayed truth  | override ledger                  |
| UI SHELL        | display, request, animate, export  | admit, certify, mutate ledger    |
| AGENTS          | propose, draft, compress, route    | decide, admit, govern            |
| Headroom        | compress context before LLM call   | certify truth, reach kernel      |
| Control Room    | visualize agent state              | promote demo_state to canon      |
| Marketing Street| draft artifacts                    | ship institutional reality       |
| SANDBOX / X     | hold rejected/unverified material  | feed back to reducer without reclassification |

---

## Forbidden Shortcuts

```
dialogue   → ledger       BLOCKED (kernel_guard.sh)
UI         → reducer      BLOCKED (UI cannot admit)
agents     → reducer      BLOCKED (agents cannot decide)
demo_state → canon        BLOCKED (requires receipt chain)
Headroom   → kernel       BLOCKED (servitor layer only)
```

---

## CRITIC — The Missing Node

Prior descriptions of the HELEN pipeline often collapsed CLASSIFY → OBLIGATIONS
(skipping CRITIC). CRITIC is the node that fires between CLAIM and OBLIGATION to:

1. Reject unfalsifiable claims (`Watch the Global Brain think`)
2. Reject marketing claims masquerading as architecture
3. Require falsifiable rewrites before obligation generation
4. Detect sovereignty drift in language (`Zero Bugs`, `Award-Winning`)

Without CRITIC, the obligation layer receives polluted claims and generates
obligations that cannot be satisfied — or worse, obligations that feel satisfied
by demo_state animation.

```
CRITIC law:
  A claim that cannot be falsified cannot generate an obligation.
  A claim that cannot generate an obligation cannot reach the reducer.
  A claim that cannot reach the reducer cannot be admitted.
  An unadmitted claim is not HELEN reality.
```

---

## HELEN Locations

| Node            | HELEN file(s)                                        |
|-----------------|------------------------------------------------------|
| REDUCER         | `oracle_town/kernel/kernel_daemon.py`                |
| LEDGER          | `town/ledger_v1.ndjson` + `tools/helen_say.py`       |
| REPLAY          | `helen_os/governance/legoracle_gate_poc.py`          |
| WITNESS         | `GOVERNANCE/CLOSURES/` + ghost closure detector      |
| CRITIC          | `oracle_town/skills/feynman/peer_review.py` (K2/R3)  |
| UI SHELL        | `apps/helen-surface/`                                |
| AGENTS          | `oracle_town/skills/` + `tools/hal_driver.py`        |

---

## Authority

```
authority: false
sovereign: false
ledger_mutation: false
status: CANONICAL_REFERENCE — not a ledger event, not a schema change
```
