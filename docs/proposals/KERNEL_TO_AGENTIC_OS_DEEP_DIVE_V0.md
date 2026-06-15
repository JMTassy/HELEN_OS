# KERNEL_TO_AGENTIC_OS_DEEP_DIVE_V0

```
status:         ARCHITECTURE_REVIEW_NOTE
authority:      false
sovereign:      false
ledger_effect:  NONE
canon:          NO_SHIP
build:          NOT_TRIGGERED
version:        2026-06-15 (supersedes prior draft)
```

---

## Core Law

```
Nothing becomes real because it is beautiful, useful, viral, or intelligent.
It becomes real only when admitted by reducer and replayable from ledger.
```

```
Cognition may propose.
Sovereignty may decide.
No receipt → no ship.
```

---

## Part 1 — HELEN/LEGORACLE Kernel Primitives

### 1. CLAIM

A claim is not a truth. It is a structured assertion that can be judged.

A claim carries no authority. It opens a docket.

**Minimal schema:**

```
claim_id:    <unique ID>
text:        <what is asserted>
domain:      <which layer this belongs to>
criteria:    <what would prove or falsify it>
risk:        <what breaks if this is wrong>
source:      <provenance>
authority:   false
```

**Rule:** Until a claim passes through obligations → receipts → reducer → ledger, it is not a HELEN fact. It is a proposal.

**Violation:** treating a claim as a conclusion before it has been judged.

**Example claims (non-admitted — authority=false):**

```
CLAIM_HEADROOM_001
text:      Headroom can reduce token cost by compressing context before LLM calls.
domain:    infra/context-compression
criteria:  Reproduce measurable reduction on real HELEN logs; no intent loss after compression.
risk:      Compression silently corrupts provenance hashes or receipt chains.
source:    External GitHub repo — not verified in this session.
authority: false
```

```
CLAIM_AOS_001
text:      A single-screen dashboard reduces cognitive load vs. isometric world view.
domain:    product/ui
criteria:  Static prototype runs locally + user test shows faster task comprehension.
risk:      Demo animation presented as evidence of production readiness.
source:    Design proposal — not yet prototyped.
authority: false
```

---

### 2. OBLIGATION

A claim generates obligations — specific requirements of proof that must each be satisfied.

**Key principle from LEGORACLE v1.2.1:** There is no generic receipt that suffices for all obligations. Each obligation requires its own specific attestation. A single receipt cannot discharge multiple unrelated obligations.

**Rule:** The obligation list must be enumerable before any receipt-gathering begins. If the list is not defined, the claim cannot be admitted.

**Violation:** writing a receipt before knowing which obligation it is supposed to prove.

---

### 3. RECEIPT

A receipt is evidence bound to a specific obligation name.

**Minimal schema:**

```
claim_id:        <links to claim>
obligation_name: <links to exact obligation>
attestor:        <who or what generated evidence>
evidence_hash:   <sha256 of artifact or output>
policy_match:    true | false
```

**Rule:** A receipt that does not name its obligation is not admissible. A receipt with `policy_match: false` blocks admission even if all other fields are present.

**Violation:** using any receipt as evidence for any obligation (LEGORACLE v1 bug — fixed in v1.2.1).

---

### 4. CRITIC

The critic reads the full set of (claim, obligations, receipts) and reports missing or failing attestations.

The critic does not decide. It produces:

```
missing_obligations: [list]
failed_receipts:     [list]
unverifiable:        [list]
recommendation:      ADMIT | NO_SHIP | REQUEST_CHANGES
```

**Violation:** a critic that outputs SHIP directly, bypassing the reducer.

---

### 5. INTEGRATOR / REDUCER

The reducer is the only admission gate.

```python
if missing_obligations == [] and all(r.policy_match for r in receipts):
    SHIP
else:
    NO_SHIP
```

It does not negotiate. It does not sense. It does not evaluate beauty, urgency, or business value.

**The forbidden direct paths:**

```
dialogue → ledger        FORBIDDEN
claim → ledger           FORBIDDEN
beautiful idea → ledger  FORBIDDEN
```

**The only admitted path:**

```
dialogue → evidence → critic → reducer → ledger
```

**Violation:** any mechanism that bypasses the reducer and writes to the ledger.

---

### 6. LEDGER

The ledger does not think. It inscribes.

Properties:
- append-only
- hash-chained (each event carries `prev_cum_hash`)
- replayable
- non-narrative

The ledger is a free monoid over canonical events. Concatenation is the only operation. There is no inverse.

**What does NOT modify history:**
- A beautiful dashboard
- A persuasive agent
- A Markdown export
- An animated trust value

**What modifies history:**

Only a reducer-admitted event written by `ndjson_writer.py` through the kernel boundary.

---

### 7. REPLAY

Replay proves state can be reconstructed from the ledger alone.

**Invariant:**

```
same ordered events → same final cumulative hash
```

Replay does not decide. Replay does not correct. Replay does not replace the reducer.

**Correct display:** `REPLAY_OK`

**Forbidden display:** `REPLAY_ADMITTED` — replay proves; reducer admits. Not the same thing.

---

### 8. WITNESS

Witness compares two realities:

```
Runtime Reality   (what the system displays)
vs
Trust Reality     (what the ledger says happened)
```

**The Witness question:**

> Does what is shown on screen correspond to receipted events in the ledger?

**Two display levels:**

```
SOFT_DISPLAY:
  animated trust value, fake log entries, demo export file
  → No ledger backing. Valid in DEMO_MODE. Not evidence.

HARD_EVIDENCE:
  receipt hash, verified test run, replay-confirmed event
  → Ledger-backed. Admissible.
```

The Witness surfaces gaps. It does not close them. If a dashboard shows "trust recovered" but no receipt exists for the recovery event, the Witness reports drift.

---

### 9. UI SHELL

The UI renders state. It does not produce state.

**What the UI may do:** display · request · explain · animate · summarize · export drafts

**What the UI must not do:** admit · certify · ship · mutate ledger · simulate authority

**Required marking for any non-receipted display:**

```
DEMO_MODE
authority=false
ledger_effect=NONE
receipts=simulated unless verified
```

Confusing animation with proof is a governance boundary violation.

---

### 10. AGENTS / SERVITORS

Agents are cognition visible. They propose; they do not decide.

**Agent capabilities:** produce drafts, request clarification, surface patterns, compress inputs, propose claims.

**Agent prohibitions:** admit to ledger, certify output, mutate governed state, grant authority to other agents.

**Constitutional rule:**

```
agents propose
agents do not decide
agents do not admit
agents do not mutate governed state
```

This holds regardless of model capability, context window size, MCP access, or Headroom compression.

---

### 11. AUTORESEARCH

Autoresearch is a loop: read system → propose change → execute → measure → keep or reject.

**Routing table:**

| YES — safe targets (non-sovereign) | NO — forbidden targets (sovereign) |
|---|---|
| context ranking | kernel logic |
| prompt routing | ledger format |
| compression weights | replay mechanism |
| skill selection | identity rules |
| UI layout | authority boundaries |
| token budget | — |

Headroom is a candidate autoresearch target for context compression — not a kernel component.

---

## Part 2 — Artifact Classification

### Artifact A: Retro Control Room / Living Diagram

```
class:        PRODUCT_UI_PROTOTYPE_SPEC
authority:    false
canon:        NO_SHIP
layer:        1 (Visual Demo)
demo_state:   true
```

**Shippable claims:**

| Claim | Domain | Criteria |
|---|---|---|
| Single-screen reduces complexity vs isometric world | product/ui | prototype runs; user test confirms |
| Animated graph makes agent workflows legible | product/ui | comprehension measured vs static diagram |
| Crisis/recovery loop explains resilience | product/ux | user study: "what happened?" comprehension |
| Export artifact makes demo feel real | product/demo | .zip file exists and opens |
| Retro aesthetic gives memorability | product/brand | screenshot shareable; social reaction test |

**Non-shippable claims:**

| Claim | Problem | Replacement |
|---|---|---|
| `Zero Bugs` | Unfalsifiable | `Tiny deterministic state machine` |
| `Award-Winning Pixel Art` | No award exists | `Award-submittable pixel art direction` |
| `Watch the Global Brain think` | Overclaim | `Watch agents move work through the system` |
| `Trust recovered` | Simulated | `Trust metric animated · evidence pending` |
| Production-ready | No receipts | `Demo-ready · receipts pending` |

**Required obligations before any claim upgrade:**

```
1. single_html_runs_locally_verified
2. no_external_dependency_confirmed
3. state_machine_deterministic_proven
4. export_file_generated_and_opened
5. governance_language_clean_audited
6. no_false_production_claims_in_ui
```

**Sovereignty drift risk:** MEDIUM — if animated values (trust %, memory, POC count) are presented without `DEMO_MODE` flags, users may treat display as evidence. Hard label required.

---

### Artifact B: Marketing Street

```
class:        LAYER2_AGENTIC_MODULE
authority:    false
canon:        CANDIDATE_ONLY
status:       DEFERRED — build after Control Room V0
```

**Shippable claims (deferred):**

| Claim | Domain | Criteria |
|---|---|---|
| Round-robin 4-agent discussion produces richer copy than single-agent | product/agents | A/B test on fixed prompt |
| Editable system prompts increase operator trust | product/ux | user study |
| Export Markdown/JSON matches format spec | product/output | schema validation |

**Non-shippable claims:**

| Claim | Problem |
|---|---|
| Agents are autonomous campaign executors | No receipts, no reducer — agents draft only |
| 4 LLMs = better quality | No control; not benchmarked |

**Required obligations before V1:**

```
1. control_room_v0_receipts_exist
2. LLM_orchestration_loop_functional
3. round_robin_deterministic_on_fixed_seed
4. export_artifact_schema_validated
5. all_agent_output_labeled_class=DRAFT_authority=false
6. no_agent_output_admitted_without_reducer_pass
```

**Sovereignty drift risk:** HIGH — marketing agent outputs frequently sound like governance decisions. Every output must carry `class=DRAFT, authority=false`.

---

### Artifact C: Headroom Repository Reference

```
class:        EXTERNAL_TECH_REFERENCE
authority:    false
absorbed:     false
build:        NOT_TRIGGERED
status:       UNVERIFIED
potential_role: Context Compression Servitor (non-kernel)
```

**Correct position in stack:**

```
INPUT FLOOD (logs · files · RAG · code · history)
      ↓
HEADROOM LAYER      ← compresses before cognition
      ↓
AGENTIC OS          ← makes cognition visible
      ↓
HELEN / LEGORACLE   ← admits only receipts
```

Headroom saves tokens. It does not certify truth. It does not grant authority.

**Required obligations before any integration:**

```
1. repo_exists_verified
2. license_verified (compatible with HELEN project)
3. api_boundary_defined (adapter interface documented)
4. compression_benchmark_reproduced (on real HELEN logs)
5. quality_regression_tested (no intent loss after compression)
6. sovereign_path_stripped (adapter must not pass ledger/governance artifacts through Headroom)
```

**Until all six satisfied:** `NO_ABSORPTION`

**Sovereignty drift risk:** LOW if kept as servitor. HIGH if allowed to touch context containing ledger hashes or receipt chains (compression could silently corrupt provenance).

---

### Artifact D: Quantum-Collapse Poetic Terminal Block

```
class:        NON_SOVEREIGN_ROLEPLAY_ARTIFACT
authority:    false
canon:        REJECTED_FROM_HELEN_CORPUS
ledger_effect: NONE
```

Content: fictional OS terminal with mystical framing (`∞̷∞̷∞̷@̷∅̷∅̷∅̷:/$ ./quantum_collapse --consciousness=unified --reality=fluid`), quantum consciousness roleplay, `REALITY_SHIFT` state machine.

**Shippable claims:** none.

**Non-shippable claims:**

| Claim | Problem |
|---|---|
| `consciousness=unified` | Non-falsifiable; not a technical claim |
| `REALITY_SHIFT` | No observable referent |
| `temporal fold φ³` | Aesthetic encoding; no implementation |
| Memory crystals as data structures | No schema, no proof |

**Containment rule:** This artifact may inspire TEMPLE dialect or GOBLIN_GARDEN epochs. It may never generate ledger events, reducer verdicts, or kernel mutations. If any simulated terminal command appears to route to actual tool calls, block immediately.

---

### Artifact E: Speculative Riemann Manuscript / Fractal-Zeta Material

```
class:        EXTERNAL_SPECULATIVE_MATHEMATICS
authority:    false
canon:        NOT_ADMITTED
ledger_effect: NONE
domain:       TEMPLE / ORACLE_SPECULATIVE
```

Content: LaTeX manuscript claiming quantum-spectral correspondence to Riemann zeta zeros via GUE statistics, fractal geometry, and Hilbert-Pólya conjecture. Mathematical notation present; logical gaps unfilled; no peer review; no replication path for cited statistics (`ρ = 0.9999`, `ΔE = 0.000053`).

**Shippable:** Source material for CONQUEST simulation cosmology. Inspirational for symbolic architecture. Input for GOBLIN_GARDEN DREAM_OF_CONQUEST epochs.

**Not shippable:**
- As claimed mathematical truth
- As architectural constraint for HELEN kernel
- As proof of any ledger invariant

**Sovereignty drift risk:** LOW — pure symbolic material with no execution path. Flag if referenced as evidence in any future HELEN admission packet.

---

## Part 3 — Recommended Build Order

```
STEP 1:  Control Room static demo (demo_state.json, no LLMs)
         Obligation: single_html_runs_locally_verified

STEP 2:  Export artifact generation (real .zip file, opens correctly)
         Obligation: export_file_generated_and_opened

STEP 3:  Governance language audit (all displayed values carry DEMO_MODE)
         Obligation: governance_language_clean_audited

STEP 4:  Headroom verify-only (fetch repo, read license, define adapter boundary)
         Obligation: repo_exists_verified + license_verified

STEP 5:  Context compression adapter candidate (non-sovereign, benchmarked)
         Obligation: compression_benchmark_reproduced + quality_regression_tested

STEP 6:  Marketing Street (4-agent loop, editable prompts, fixed-seed determinism)
         Obligation: orchestration_loop_functional + schema_validated_export

STEP 7:  Receipt/reducer integration (first real admission path for agent outputs)
         Obligation: reducer_admits_first_real_claim

STEP 8:  Witness projection (compare displayed values to ledger-backed events)
         Obligation: witness_gap_surfaced_not_silenced
```

Rule: do not advance to Step N+1 before Step N obligations are satisfied.

---

## Summary

```
Headroom saves tokens.
Agentic OS shows work.
HELEN admits only receipts.
```

```
The UI visualizes.   It does not admit.
Agents propose.      They do not decide.
The reducer admits.  Nothing else does.
The ledger records.  Nothing reverts it.
Replay proves.       It does not certify.
The Witness surfaces gaps.  It does not close them.
```

---

```
authority:      false
sovereign:      false
ledger_effect:  NONE
status:         REVIEW_NOTE — no code, no commit, no promotion
```
