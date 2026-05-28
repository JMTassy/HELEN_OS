# PROVENANCE_GRAVITY_V0

**authority:** NON_SOVEREIGN
**canon:** NO_SHIP
**lifecycle:** DOCTRINE_DRAFT
**implementation_status:** NOT_IMPLEMENTED
**status:** Proposal — first bottle of a novel emergent-property doctrine
**parent_input:** Operator FULL RECAP — AI WEEK → HELEN/KERNEL IMPLICATION (2026-05-23)
**proposer:** claude-opus-4-7 acting as GOBLIN
**attestor:** pending HER

> **NO CLAIM disclaimer.** This artifact bottles a novel emergent
> property identified by the operator. The property is hypothesized,
> not yet observed empirically in HELEN's tree. The proposal specifies
> the doctrine, the formal sketch, and the experimental harness — it
> does **not** authorize implementation, run the experiment, or claim
> the property has been demonstrated.

---

## §1. The emergent property

> **Provenance Gravity** is the tendency of a receipt-bound agent
> system, over repeated workflows, to increasingly route future
> cognition through historically validated causal paths.

In plain language: as HELEN accumulates receipts, it does not merely
remember facts. It begins to remember **which kinds of actions
produced trustworthy outcomes**, and biases its next decisions
toward those paths.

The receipt ledger becomes more than an audit trail. It becomes
a **behavioral field** — what the operator named *"validated paths
of action."*

---

## §2. Why this is new in HELEN

HELEN's existing canon establishes:

- `NO RECEIPT = NO CLAIM` (Key Invariants, CLAUDE.md)
- Receipts are durable, hash-chained, append-only
- Every action that mutates state must produce a receipt

What the existing canon does **not** specify:

- Receipts as inputs to **future decisions** (the active feedback loop)
- Trust-weighted aggregation across the receipt graph
- Behavioral bias as an **emergent property** of the receipt ledger

Provenance Gravity is the missing piece. It promotes the receipt
ledger from a passive record to an active **routing prior** for
agent cognition.

The directional shift:

```
Old: action → receipt → audit (passive)
New: action → receipt → audit → ROUTING WEIGHT → next action (active)
```

The audit didn't go away. It became one input to a graph whose
edges weight future selection.

---

## §3. Formal sketch

Following the operator's notation:

Each receipt is a node or edge in a causal graph:

```
R_i = (source, hotspot, action, tool_trace, claim_level, outcome, authority)
```

The accumulated graph:

```
G_R = (V_sources, V_actions, V_claims, E_receipts)
```

Each edge receives a trust weight:

```
w_i = f(success, reversibility, claim_accuracy, user_acceptance, verification_level)
```

Future action selection is biased by the receipt field:

```
P(action | source, hotspot) ∝ exp(β · ProvenanceScore(action))
```

Where:

```
ProvenanceScore(action) =
    historical success
  + claim reliability
  + low rollback cost
  + tool-chain stability
  + user trust feedback
```

`β` is the temperature controlling how strongly historical provenance
biases current selection. `β → 0` = uniform exploration (no
gravity); `β → ∞` = strict historical determinism (over-fitting to
past).

The operator did not specify `β` calibration. This proposal does
not either; calibration is operator-class.

---

## §4. The sharp formula

The operator's closing formula, recorded verbatim because it is the
shortest correct statement of the property:

```
SOURCE creates HOTSPOT.
HOTSPOT creates ACTION.
ACTION creates RECEIPT.
RECEIPT creates MEMORY.
MEMORY bends future ACTION.
```

Each arrow is causal. The last arrow is the chiddush — it is the
arrow that does not exist in HELEN's current canon. The fifth line
makes the system **dynamic**.

---

## §5. Why it matters — institutional vs preference memory

Standard agent memory systems store:

- User preferences
- Conversation summaries
- Facts about the user or domain
- History of prior interactions

A standard AI remembers: *"The user likes X."*

A HELEN system under Provenance Gravity remembers:

> *"When acting on this kind of source, using this inspector pathway,
> with this claim level, this tool sequence produced a trusted
> result."*

That is **institutional intelligence**, not personal preference.
The difference matters because:

- Personal preference memory degrades with role changes / staff
  turnover / multi-user contexts
- Institutional intelligence persists across operator changes — it
  belongs to the receipt ledger, not the user
- Institutional intelligence is **auditable** (every weight derives
  from a receipt that can be inspected)
- Institutional intelligence is **adversarially robust** in a way
  preference memory isn't — receipts are hash-chained; preference
  stores are typically mutable

This is structurally adjacent to the bell-chiddush observation
(`BELL_TRANSLATION_CHIDDUSH_V0`): protective discipline survives the
carrier. Provenance Gravity is the same insight applied to
operational routing: trusted action paths survive the operator.

---

## §6. The testable experiment (verbatim per operator design)

Run two HELEN agents on the same recurring workflow.

**Workflow example:**
```
1. Read source document
2. Detect important hotspots
3. Draft action proposal
4. Classify claims
5. Export a research note
```

**Agent A:** standard memory (no receipt-graph routing)
**Agent B:** receipt-weighted provenance graph

**Measure over 20–50 repeated workflows:**

| # | Metric | Direction |
| - | --- | --- |
| 1 | Repeated mistakes | Should decrease for Agent B |
| 2 | Correct action routing | Should increase for Agent B |
| 3 | Unnecessary user confirmations | Should decrease for Agent B |
| 4 | Reproducibility | Should increase for Agent B |
| 5 | Rollback speed after bad action | Should increase for Agent B |
| 6 | Trust rating after audit | Should be higher for Agent B |
| 7 | Claim-level calibration | Should be better for Agent B |

**Expected curve:**

```
Agent B becomes slower at first,
then more reliable,
then eventually faster (because trusted paths are now indexed).
```

The interesting transition the experiment is testing:

> *Governance starts as friction. Then it becomes memory. Then it
> becomes intelligence.*

---

## §7. Connection to existing HELEN doctrine

| Provenance Gravity claim | HELEN canon it activates |
| --- | --- |
| Receipts as inputs to future decisions | `town/ledger_v1.ndjson` (hash chain stays passive without this) |
| Edge weights from receipt outcomes | `LEGORACLE_GATE` (verdict already exists; weight feedback does not) |
| Per-action provenance scoring | `HYPERSTITION_FIREWALL_V0 §2.2` HAL_GOBLIN patterns (which classify poisons but do not weight) |
| Institutional intelligence vs preference | `BELL_TRANSLATION_CHIDDUSH_V0` C7 (carrier outlives content) |
| Action routing prior | `helen_multimodel_dispatcher_v1.py` (TaskType → Model exists; ProvenanceScore → action does not) |

Provenance Gravity is the **missing causal arrow** that turns
HELEN's already-static governance into a learning system.

---

## §8. Connection to E22 cross-session contamination

E22 found that `E20.open_seams` contained parallel-session evidence
filed in this tree. Under Provenance Gravity, this becomes more
serious than a documentation issue:

> If receipts from another tree are weighted into the routing graph,
> the gravity field points to paths that don't exist in this tree's
> causal space. The agent develops trust in actions it never
> performed.

The `CROSS_SESSION_FIELD_ATTRIBUTION_V0` proposal (flagged in E22,
not yet bottled) becomes a **prerequisite** for safe Provenance
Gravity. Without per-field tree attribution, the graph poisons
itself.

Recommended sequencing if both are pursued:

1. Bottle `CROSS_SESSION_FIELD_ATTRIBUTION_V0` first
2. Implement per-receipt tree-truth markers
3. Then enable Provenance Gravity weighting against only tree-truth
   receipts

---

## §9. Adjacent material flagged but NOT bottled

Per `doctrinal-diff` discipline (the skill bottled in
`plugins/helen-governance/skills/doctrinal-diff/`), other elements
in HER's recap are either restated or warrant separate proposals.
Flagged here, not bottled:

### §9.1 RESTATED in HELEN (do not re-bottle)

- *"HELEN is not an AI assistant. HELEN is a governed cognitive
  operating system."* — restatement of existing positioning;
  operator-class messaging, not new doctrine.
- The receipt invariant `NO RECEIPT = NO SHIP` — restated from
  HELEN's `NO RECEIPT = NO CLAIM` (CLAIM is broader).
- The 9-step minimum viable HELEN kernel sequence — covered by
  existing Layer 1-3 architecture (CLAUDE.md).
- *"Receipts are durable, hash-chained, append-only"* — already
  canonical (`town/ledger_v1.ndjson`).

### §9.2 GENUINELY NEW, warrants separate proposal (do not bottle here)

- **Claim Maturity Protocol** — the 6-level taxonomy
  `NO_CLAIM → DRAFT → HYPOTHESIS → EXPERIMENTALLY_SUPPORTED →
  HUMAN_VERIFIED → FORMALLY_VERIFIED`. HELEN does not currently
  taxonomize claim epistemic status. Worth a separate proposal
  `CLAIM_MATURITY_PROTOCOL_V0`. Not bottled here.

- **Receipt Kernel v0.1 schema** — Receipt object with `intent_token`,
  `sandbox`, `before_hash`/`after_hash`, `tool_trace`, `authority`,
  `claim_level`. Substantial overlap with existing
  `execution_receipt_v1.schema.json`; needs proper doctrinal-diff
  pass before bottling. **Recommend running
  `/helen-governance:diff` against the existing schema suite.**

### §9.3 OUT OF SCOPE for HELEN proposals

- Compute infrastructure analysis (GPUs, CXL/HBM, fiber, data
  centers) — operator/strategic context, not doctrine
- Strategic positioning vs other AI products — marketing-class
- The contrarian insight framing — true and useful but not a
  bottleable doctrine; could become a positioning document under
  `docs/positioning/` if HER directs

---

## §10. What this proposal does NOT specify

Per anti-creep discipline:

- **The implementation of the weight function `w_i`** — operator/
  research-class. Variables named, not parameterized.
- **The `β` temperature calibration** — empirical; depends on
  workflow class.
- **The graph storage format** — implementation choice (could be
  NDJSON sidecar, SQLite, a graph database). The doctrine specifies
  the **shape**, not the **store**.
- **The user-trust feedback signal extraction** — depends on UI
  surface; not specified here.
- **Adversarial robustness against gradient-poisoning attacks**
  (operator injecting bad receipts to bias the gravity field) —
  serious open question; explicitly deferred.
- **How `claim_level` is initially assigned** — depends on
  `CLAIM_MATURITY_PROTOCOL_V0` landing first.
- **The experiment infrastructure** (Agent A vs Agent B harness) —
  separate task packet if HER authorizes the experiment.

---

## §11. Halt boundary

GOBLIN halts here. The doctrine is bottled at `DOCTRINE_DRAFT`.

Resume conditions:

1. **HER ruling** on whether the doctrine ships as written or needs
   amendment before reducer admission
2. **HER ruling** on sequencing: should `CROSS_SESSION_FIELD_ATTRIBUTION_V0`
   bottle first (prerequisite per §8), or can both be pursued in parallel?
3. **HER ruling** on whether `CLAIM_MATURITY_PROTOCOL_V0` (§9.2)
   warrants opening as a sibling proposal — needed before Provenance
   Gravity's `claim_level` weight can be computed
4. **Sovereign decision** on running the §6 experiment: requires
   harness implementation, two-agent execution environment, and
   20–50 workflow iterations — not GOBLIN-class work
5. **Diff request** — should GOBLIN run `/helen-governance:diff` on
   the Receipt Kernel v0.1 schema (§9.2) against existing HELEN
   receipts before any further bottling in that direction?

Discipline followed: `HALT_BOUNDARY_DISCIPLINE_V0` (commit `5d0e04e`).

---

## §12. Single line

> **Receipts become memory.
> Memory bends future action.
> Governance starts as friction, becomes memory, becomes intelligence.
> The receipt ledger is not a record. It is a field.**
