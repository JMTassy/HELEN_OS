# HELEN_FEDERATED_EDGE_PROTOCOL_V1

```
AUTHORITY      = false
CANON          = false
STATE_MUTATION = none
STATUS         = spec / proposal
VERSION        = 1.0
```

---

## Objective

Define the operational protocol by which many devices and agents collaborate on a single HELEN instance without creating unauthorized sovereign forks. Every edge is a client. Only one HELEN decides.

---

## 1. Core Law

There is only one HELEN with sovereign effect:

- one reducer
- one append-only ledger
- one replay truth
- one governed state

Everything else is upstream, non-sovereign, and typed.

> Only reducer-emitted decisions may mutate governed state.
> No ledger append exists without reducer decision.
> Legitimate state is replay-reconstructible.
> Provider / skill / UI output is never sovereign.

**Architectural sentence:**

> Many agents may think with HELEN. Only one HELEN may decide.

Formal operator chain:

```
Φ = Λ_L ∘ β ∘ HAL ∘ RALPH ∘ Agent
```

Agent proposes → RALPH structures typed artifacts → HAL verifies/falsifies → Reducer admits or rejects → Ledger appends if admitted. Failed proposals remain traceable but non-mutating.

---

## 2. Federation Model

### Layer A — Edge Nodes (one per device)

Each device is an edge:

- iPhone, iPad, Mac
- local Ollama shell
- AIRI frontend
- OpenClaw-like gateway
- browser UI
- automation runner

Each edge **may**:
- capture input
- run local UI and local helper models
- cache session state
- package typed proposals
- upload artifacts

Each edge **may not**:
- append to sovereign ledger
- admit truth
- promote canon
- mutate governed state directly

### Layer B — Shared Collaboration Bus

Each edge emits typed packets only. All carry `authority: NONE`.

Packet classes admitted on the bus:

- `proposal` — intent, hypothesis, candidate skill
- `observation` — directly attested signal
- `artifact` — rendered output, eval receipt, trace
- `memory_delta` — non-sovereign session/epoch update
- `review_ready_packet` — HAL-ready structured submission

No raw dialogue. No raw model output. No direct state claim.

### Layer C — Shared Middle Fabric

Central shared services (upstream of sovereignty):

- packet normalization
- skill router
- HAL validator
- evidence compiler
- session memory service
- epoch memory service
- artifact store
- projection builder
- capability registry

### Layer D — Single Sovereign Core

Only here:

- reducer decides
- ledger appends
- replay reconstructs

### Layer E — Fan-out

All devices receive from the single sovereign core:

- same admitted state
- same projection stream
- same canonical identity context
- device-specific presentation only (rendering, not truth)

---

## 3. Three Channels

### Channel A — Sovereign Ledger

- append-only, hash-chained, receipt-bound, replayable
- single write-gate: only `GovernanceVM` / `TownAdapter` may append
- no raw dialogue, no raw memory, no direct device write

### Channel B — Memory

- non-sovereign, informative, continuity-supporting
- authority lexicon banned
- informs behavior, cannot authorize

### Channel C — Trace

- `authority: false`, hash-chained, diagnostic, replay-adjacent
- never sovereign

**Channel invariant:**

```
Dialogue  ↛ Ledger
Memory    ↛ Ledger
Trace     ↛ Ledger
Admitted evidence →(β=1)→ Ledger
```

---

## 4. Packet Envelope

Every agent on every device emits the same envelope:

```json
{
  "packet_id": "string",
  "edge_id": "string",
  "agent_id": "string",
  "session_id": "string",
  "epoch_id": "string",
  "authority": "NONE",
  "packet_type": "proposal | observation | artifact | memory_delta | review_ready_packet",
  "capability_ref": "string",
  "payload": {},
  "payload_hash": "sha256(...)",
  "refs": [
    "artifact_id",
    "prior_packet_id",
    "session_pointer"
  ],
  "disclosure": "PUBLIC | PARTNER | INTERNAL | SEALED"
}
```

**Hard rules:**

- `authority` must always be `NONE` for edge-origin packets
- no edge packet may claim `REDUCER_DECISION`
- no edge packet may imply ledger mutation
- edge packets terminate only in `NON_SOVEREIGN_RESULT` or `REVIEW_READY_PACKET` — never reducer decision or ledger append

---

## 5. Edge Node Schema

```json
{
  "device_id": "string",
  "owner_profile": "string",
  "adapter_type": "ios | macos | browser | local_llm | gateway",
  "session_scope": "local | shared",
  "capabilities": [
    "capture_audio",
    "render_ui",
    "run_local_model",
    "send_packet",
    "fetch_projection"
  ],
  "authority": "NONE"
}
```

**Pairing principle:** A paired device is an edge node, not a second HELEN.

---

## 6. Memory Sync

**Shared memory objects (continuity spine):**

- `PERSON_PROFILE` — persistent identity
- `SESSION_LOG` — per-session record
- `EPOCH_STATE` — bounded epoch state
- `COMPANION_STATE` — runtime companion context
- `LIVE_CONTEXT` — active session window
- `RUNTIME_BOOT_CONTEXT` — boot continuity seed

**Sync law:**

- local device may cache session state
- local device may submit `memory_delta`
- `memory_delta` is non-sovereign
- persisted continuity must come from typed memory, not provider improvisation
- on reboot, continuity is reconstructed from persisted memory — not invented by the model

**Practical split:**

| Scope | Owner |
|---|---|
| local short-term cache | device-owned |
| shared session memory | central service |
| institutional memory | ledger/replay only |

---

## 7. Bounded Execution Hierarchy

Every action in the federation has a place in one hierarchy. No agent may act above its tier.

```
Reducer            ← sole decision authority; only path to ledger mutation
  MAYOR_sign       ← signs readiness; cannot invent decisions
    HAL_verify     ← verifies / falsifies typed evidence; cannot write ledger
      EGREGOR_execute  ← executes bounded non-sovereign tasks; yields artifacts only
        AURA / HER / UI / symbolic  ← presence, rendering, expression; no state effect
```

**Critical correction:**

> Not "only EGREGOR can act" — but "only EGREGOR may execute bounded non-sovereign tasks."

Any agent on any device may occupy the EGREGOR tier. Execution at this tier:
- yields typed artifacts (`authority: NONE`)
- flows upward: artifact → HAL → evidence compiler → reducer
- never mutates governed state directly
- never bypasses the reducer path

**Anti-fork membrane:**

The hierarchy is the membrane. Any attempt to collapse tiers — to let a device-local agent issue a verdict, admit a claim, or write state — is a fork attempt. The membrane law:

```
EGREGOR_execute   ≠   REDUCER_decide
artifact          ≠   ledger_entry
execution         ≠   authority
edge_model        ≠   sovereign_kernel
```

Failed proposals remain traceable but non-mutating. Non-sovereign variation across devices cannot alter sovereign reality if admitted evidence is the same.

---

## 8. Evidence and Artifact Upload Rules

Every artifact produced at the EGREGOR tier must be typed before entering Layer C:

```json
{
  "artifact_id": "string",
  "origin_edge": "device_id",
  "origin_agent": "agent_id",
  "artifact_type": "eval_receipt | skill_proposal | observation | trace | memory_delta",
  "authority": "NONE",
  "payload_hash": "sha256:...",
  "payload": {},
  "linked_session": "session_id",
  "linked_epoch": "epoch_id"
}
```

**Upload rules:**

1. `authority` must be `NONE` — no exceptions
2. `payload_hash` must be computed before upload
3. Artifact is accepted by the fabric as a candidate — not as an admitted fact
4. Only the evidence compiler may forward an artifact to HAL
5. Only HAL may forward to the reducer
6. Only the reducer may cause a ledger entry

**Forbidden upload patterns:**

```
raw_model_output  ↛ ledger
dialogue_fragment ↛ truth
local_cache_delta ↛ state
```

---

## 9. Capability Activation

Every edge capability is inert until lawfully activated.

A capability manifest declares:

- identity
- domain
- provider class
- operational limits

A capability becomes active only if:

1. manifest is valid
2. reducer authorizes activation
3. decision is recorded in ledger

New edge agents (phone, Ollama wrapper, OpenClaw connector, AIRI frontend) enter the system as manifests — not as assumed authority.

---

## 10. External Systems

External systems may describe, transport, or surface capability. They may not install sovereign reality.

| System type | Role | May not |
|---|---|---|
| OpenClaw-like | transport / gateway / frontend | own ledger, claim authority |
| AIRI | presence / rendering / orchestration | mutate governed state |
| Local model | helper shell | act as reducer |
| HELEN kernel | sole truth path | — |

---

## 11. Projection Layer

All devices subscribe to the same projection, derived only from reducer output.

**Raw snapshot:**
- state hash
- last receipt
- ledger tip

**Projection (derived):**
- threads
- tension
- momentum
- next action

**Invariant:** projection must be derived only from reducer output. If derived from any other source, the observer becomes a forbidden second kernel.

```
truth       = centralized  (reducer + ledger + replay)
experience  = federated    (projection per device)
rendering   = device-local (UI/UX)
state       = never device-local
```

---

## 12. Concurrency Rule

If two devices propose concurrently:

1. both packets accepted upstream as non-sovereign proposals
2. both enter trace/memory channels
3. neither changes governed state
4. HAL/evidence compiler normalizes them
5. reducer sees typed admissible packets
6. ledger order is the lawful replay order

**Determinism law:**

> If initial state and admitted evidence sequence are the same, final ledger is the same — even if dialogue, memory, or trace differ across devices.

This is the non-interference theorem. Devices can diverge wildly upstream; if admitted evidence is identical, sovereign reality is identical.

---

## 13. Roles

| Role | May | May not |
|---|---|---|
| Edge agent | propose, observe, emit artifacts | decide, write ledger, claim authority |
| HAL | verify / falsify | write ledger directly |
| MAYOR_sign | sign readiness | invent decision, read raw memory sovereignly |
| Reducer | sole decision authority | be bypassed |
| Ledger / Replay | institutional memory, legitimacy, audit | admit truth outside reducer path |

---

## 14. Security Invariants

```
NO_RECEIPT  = NO_CLAIM
NO_HASH     = NO_VOICE
PROPOSER    ≠ VALIDATOR         (K2 / Rule 3)
EDGE        ≠ SOVEREIGN
MANIFEST    ≠ ACTIVATED_CAPABILITY
PROJECTION  ≠ REDUCER_OUTPUT    (derived from, not equal to)
MEMORY      ≠ AUTHORITY
DIALOGUE    ≠ STATE
```

---

## 15. Minimal Boot Sequence

1. Device authenticates
2. Device fetches current projection
3. Device fetches session / epoch continuity
4. Device advertises edge capabilities via manifest
5. Device receives allowed adapter manifest (reducer-authorized)
6. Device may emit non-sovereign packets
7. Shared middle fabric validates and routes
8. Reducer alone may change governed state
9. Ledger appends
10. Replay / projection fan out to all devices

---

## 16. Final Compression

```
one kernel  ·  one reducer  ·  one ledger  ·  one replay
many edges  ·  many agents  ·  zero extra sovereignty
```

All devices may collaborate on one HELEN only by sharing projection, memory discipline, typed packets, and one reducer-bound truth path.
