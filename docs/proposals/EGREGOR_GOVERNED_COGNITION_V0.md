---
title: EGREGOR_GOVERNED_COGNITION_V0
status: 🟣 CLAIM
authority: false
claim_status: NO_CLAIM
canon_effect: false
ledger_effect: none
final: HOLD_FOR_OPERATOR
git_commit: no
date: 2026-07-21
governed_by: WITNESSED_LOOP_GRAPH_SEAM_V0
related:
  - experiments/witnessed_loop_graph_seam_v0/
  - temple/subsandbox/egregor_superteam/
  - docs/proposals/INSIGHT_COMPOST_SELECTION_FUNNEL_V0.md
  - project_egregor_superteam_algorithm
  - project_helen_hermes_split
---

# EGREGOR_GOVERNED_COGNITION_V0

🟣 **CLAIM · NON_SOVEREIGN · NO_CLAIM.** Freezes a distinction; authorizes nothing.

## Thesis

> Egregor is a **governed ChatDev-like framework for collective cognition, not
> collective authority.** Collaboration is only the cognition layer. It cannot
> authorize truth or admission.

ChatDev-style frameworks optimize for *producing a result through agent
collaboration* — the deliverable is the endpoint. HELEN inverts the endpoint:
the deliverable is a **candidate** that must survive the anchor cut and the
reducer before it is anything. Agreement is cognition; it is never authority.

```
ChatDev:  specialized agents → role discussion → sequential collab → deliverable (END)
Egregor:  goblins/agents → shared task packet → parallel/staged reasoning
          → synthesis packet → independent witness → reducer → Mayor/operator
```

## The equation

```
ChatDev
  + lineage tracking          (same-lineage agreement carries no evidentiary weight)
  + independent witnessing    (an anchor generated outside the producing lineage)
  + receipt generation        (NO RECEIPT = NO CLAIM)
  + deterministic reducer     (WITNESSED_LOOP_GRAPH_SEAM_V0)
  + no-vote authority         (votes never ship; receipts ship)
  = HELEN Egregor
```

## Layer stack (do not conflate)

| Layer | Role | Ceiling |
|---|---|---|
| **EGREGOR** | collective cognition | `PROPOSAL / INSIGHT / CANDIDATE` |
| **HAL** | evidence qualification (anchor cut) | `ADMITTABLE` |
| **MAYOR** | deterministic governance decision | decision record |
| **JM / operator** | sovereign admission | canon |

## The comparison, frozen

| ChatDev-like system | HELEN Egregor |
|---|---|
| agents simulate a company/team | goblins embody bounded cognitive roles |
| conversation drives task completion | structured packets drive proposal generation |
| final synthesizer produces output | synthesizer produces a **candidate only** |
| agreement increases confidence | **same-lineage agreement adds no evidentiary weight** |
| deliverable is the endpoint | deliverable must pass anchor-cut + reducer |
| no necessary independent witness | **independent anchor required for promotion** |
| framework may execute directly | egregor remains **non-sovereign** |

## Hard output constraint

```
EGREGOR_OUTPUT  →  PROPOSAL | INSIGHT | CANDIDATE
EGREGOR_OUTPUT  ↛  CANON | SHIP | ADMIT     (never, by construction)
```

## Component registry — built vs deferred (honest status)

The "minimal framework" is ~half already instantiated. Do **not** re-scaffold
what exists; do **not** prematurely build what is deferred (growth-sequence
discipline from `WITNESSED_LOOP_GRAPH_SEAM_V0`).

| Component | Status | Where |
|---|---|---|
| Role Registry | ⚪ partial | roles hard-coded in `orchestrator.py` (grok/claude/codex) & `egregor_seam_run.py`; no first-class registry yet |
| Task Packet | 🟢 built | shared packet in `egregor_seam_run.py` (single source, hashed) |
| Agent Runner | 🟢 built | `egregor_seam_run.py` (gemma swarm), `orchestrator.py` (CLI bridge) |
| Shared Context | 🟢 built | the doctored corpus packet / intent string |
| Lineage Descriptor | 🟠 minimal | `source_packet_hash` + `producer_id` on claims; not yet a full descriptor |
| Contribution Packet | 🟢 built | per-goblin review records |
| Synthesis Packet | 🟢 built | Sonnet executor's `egregor_promotion_packet.json` |
| Anchor Request | 🔴 deferred | anchors are hand-invoked (git/`/api/ps`), no request protocol yet |
| Witness Packet | 🟢 built | `witness_*` shape (`seam.py`, `spec.md`) |
| Reducer Result | 🟢 built | `seam.py::reduce_claim` — the anchor cut |
| Receipt Bundle | 🟢 built | `EGREGOR_SUPERTEAM_RECEIPT_V0.json`, `receipt.json` |

## Known gap — the honest architecture (V0.1)

The architecture is **not** "EGREGOR = governed framework." It is:

> Egregor cognition exists **+** governance seam exists **−** integration between
> them is still pending.

Stated plainly: **the existing Egregor can deliberate and synthesize, but it is
not yet a governed Egregor. The anchor-cut seam is the missing constitutional
boundary between group agreement and claim promotion.**

### The frozen rule — demote, do not delete

`orchestrator.py:158` aggregates by "majority presence + role notes." That logic
is **not automatically wrong for synthesis.** It becomes wrong only when its
aggregate is treated as evidence, confidence, or promotion authority.

> **Majority may summarize a conversation. Majority may not satisfy an evidence
> obligation.**

So majority aggregation is **demoted, not deleted:**

```
majority_result:
  allowed_use:   [ SUMMARY, CLUSTERING, ROLE_NOTE_SYNTHESIS, CANDIDATE_GENERATION ]
  forbidden_use: [ EVIDENCE_WEIGHT, CONFIDENCE_SCORE, PROOF, ADMISSION, CANON_MUTATION ]
```

### Precise status block

```
egregor_orchestrator:
  state: BUILT
  function: COLLECTIVE_SYNTHESIS
  governance_status: UNGOVERNED
  known_risk: MAJORITY_PRESENCE_CAN_BE_MISREAD_AS_EVIDENCE
anchor_cut_seam:
  state: BUILT_AND_TESTED
  function: INDEPENDENT_EVIDENCE_GATE
  authority: false
  maximum_result: ADMITTABLE
integration:
  state: DEFERRED
  required_change:
    - prevent vote count from entering promotion evidence
    - attach lineage descriptors to contributions
    - route promotion candidates through the seam
    - preserve majority summaries as non-sovereign diagnostics
```

### The exact next engineering cut

```
orchestrator output → candidate packet → lineage inspection
  → independent witness requirement → seam reducer → ADMITTABLE | HOLD | REJECT
```

This turns the discovery into a clean implementation target, not a contradiction.

## WULmoji doctrine (compressed)

```
👺⊗👺⊗👺 → 🗣️Σ → 📦
📦 + 🧬 + 🔍 → ⚖️
🗣️Σ ⊬ 🧾      (synthesis is not evidence)
🗣️Σ ⊬ ✅      (synthesis is not admission)
🟡 ⊬ ✅        (ADMITTABLE is not admission)
🪞×N < 🪟×1    (ten mirrors weigh less than one window)
🏁
```

Compiled graph — the forbidden edge is explicit:

```
👺 → 🗣️Σ   PRODUCES
🗣️Σ → 📦   PROPOSES
📦 → 🧬     REQUIRES_LINEAGE
🧬 → 🔍     REQUIRES_INDEPENDENCE
🔍 → ⚖️     FEEDS_EVIDENCE
⚖️ → 🟡     MAY_RETURN
🟡 ⊬ ✅     NO_AUTOMATIC_ADMISSION
🗣️Σ ─X→ ✅  FORBIDDEN: VOTE_COUNT_AS_EVIDENCE
```

Core law: `SAME_DIGEST ⊬ INDEPENDENCE` = 🪞⊗🪞⊗🪞 ≠ 🪟. Ten mirrors remain
mirrors; one independent window is a different epistemic source.

> Operator-supplied WLR-0.3 receipts + checksums for the four status lines
> (EGREGOR_ORCHESTRATOR_V0 · ANCHOR_CUT_INTEGRATION_V0 · VOTE_COUNT_AS_EVIDENCE_V0 ·
> MAJORITY_AS_SUMMARY_V0) were provided with this refinement. They are recorded
> as **operator WLR compilation, not independently re-hashed here** (NO HASH = NO
> VOICE — Claude Code does not mint sovereign hashes).

## The product question worth building around

- ChatDev asks: *"Can a team of agents produce something useful?"*
- Egregor asks: *"Can a team of agents produce something useful **while proving
  that agreement did not become authority**?"*

## What this note is not

Not an authorization to build the full 11-component framework, not a wiring of
`orchestrator.py` into the seam, not canon. `final: HOLD_FOR_OPERATOR`. The only
governed mechanism today is the seam; everything above `ADMITTABLE` remains the
operator's.
