# HELEN_OS_API_DOMAIN_MODEL_V0

```yaml
schema: HELEN_OS_API_DOMAIN_MODEL_V0
status: PROPOSAL
banner: 🟣 CLAIM
kind: continuity_update
authority: false
sovereign: false
canon: false
claim_status: NO_CLAIM
ledger_effect: none
implementation: BLOCKED
human_admission_required: true
final: HOLD_FOR_OPERATOR
git_stage: no
git_commit: no
source: |
  Operator continuity update 2026-07-18: domain-model API spine
  (not a loose endpoint list). Filed as proposal for synthesis.
  Memory may hold a copy for advisory continuity; memory ≠ truth.
  Empirical membrane note (cross-seat, 2026-07-18): false-completion
  events (crack-swarm exit-0, MoE "completions", void probe) instantiate
  R_R read as R_T without packet→receipt→admission — see §1.2.
purpose: |
  Define one coherent HELEN OS API spine as domains, core entities,
  key endpoints, and invariants — without authorizing implementation
  or sovereign mutation.
companions:
  - docs/HELEN_OS_CTO_GUIDE_V1_1.md
  - docs/proposals/HELEN_AUTORESEARCH_SAFE_ARCHITECTURE_V1.md
  - docs/proposals/HELEN_MEMBRANE_THEOREM_V0.md
  - docs/proposals/WARREN_SOVEREIGNTY_CONSTITUTION_V0.md
  - docs/proposals/MARK_INTERVENE_SURFACE_CONTRACT_V0.md
  - helen_os/api/do_next_v1.py
```

🟣 CLAIM · NON_SOVEREIGN · PROPOSAL · continuity update · NO_CLAIM · HOLD_FOR_OPERATOR  
**authority=false** · **ledger_effect=none** · **implementation: BLOCKED**

---

## 0. Position

This document organizes the HELEN OS API as a **domain model**, not a
grab-bag of routes. It is a continuity update for operator synthesis.

It does **not**:

- admit a public HTTP surface;
- authorize ledger writes;
- replace the admissible bridge (`tools/helen_say.py`);
- make framework memory into Trust Reality.

```
Kernel defines truth.
Shell renders truth.
Tools and skills propose.
Memory supports continuity, not sovereignty.
```

---

## 1. Core shape

One coherent API spine:

```
User
  → Session / Context
  → Governance
  → Runtime Observation
  → Evidence Packet
  → Proposal
  → Action
  → Receipt
  → Admission
  → Replay
  → Render
```

### 1.1 Membrane (load-bearing)

| Symbol | Meaning | Authority |
|---|---|---|
| \(R_R = \mathrm{Probe}(\mathrm{now})\) | Volatile **Runtime Reality** | NONE · candidate only |
| \(R_T = \mathrm{Replay}(L)\) | Sovereign **Trust Reality** | only via admitted ledger \(L\) |

**Only lawful bridge:**

```
RuntimeObservation
  → CandidateEvidencePacket
  → Receipt
  → Admission
  → Ledger
  → Replay
```

Any shortcut that treats probe, render, memory, or evaluation as \(R_T\)
is a membrane breach.

### 1.2 Empirical note (continuity — not a ship claim)

Cross-seat observation (2026-07-18 session): several **false-completion**
events caught the same night — including crack-swarm exit-0, MoE-style
“completions,” and a void probe — were each an instance of the same failure:

```
RuntimeObservation (R_R) was read as Trust Reality (R_T)
without passing through:
  CandidateEvidencePacket → Receipt → Admission → Ledger → Replay
```

The membrane in §1.1 is therefore not only architectural doctrine. It is the
**general law those incidents instantiate**. This note is advisory continuity
for future synthesis; it does not admit the API, certify the incident set, or
authorize remediation code.

---

## 2. Domains

### 2.1 Operator Session

Handles `/init`, user context, scope, preview mode, and attention boundaries.

Owns: session identity (ephemeral), assembled context packet, preview flags.

Does **not** own: kernel truth, identity authority, ledger append.

### 2.2 Governance

Owns constitution shards, authority classes, governance manifests, effect
ceilings, and gate decisions.

Owns: what work is *allowed to mean*.

Does **not** own: who is *capable* of doing the work (that is routing).

### 2.3 Runtime Reality

Produces live probes: process state, repo state, queue state, tool state,
freshness, active run status.

Output class: `RuntimeObservation` only. **Not truth claims.**

### 2.4 Evidence And Witness

Stages evidence packets, local witnesses, provenance, claim status, and
grounding checks.

Promotion to ledger requires the receipt → admission path. Packetization
alone mutates **nothing** sovereign.

### 2.5 Proposal And Action

Turns intent into explicit proposals, executes only approved bounded
actions, and returns **execution receipts** (operator/runtime class —
not automatically Kernel-admitted).

### 2.6 Kernel Truth

Owns receipts (sovereign class), admission, ledger, replay, supersession,
and Trust Reality reconstruction.

Only domain that may define \(R_T\).

### 2.7 Memory Fabric

Stores **advisory** continuity: framework notes, learned workflows,
synthesis deltas, retrieval memory.

```
Memory ⊬ Truth
Memory ⊬ Admission
```

### 2.8 Evaluator

Scores claims/artifacts on multiple dimensions: accuracy, coherence,
stability, grounding, disagreement.

Multi-axis only — no single scalar that becomes authority.

### 2.9 Render Shell

User-facing cockpit, diagrams, WULMOJI, dashboards, projections.

```
Render ⊬ state
Render ⊬ admission
```

All projections carry explicit `authority=false` unless Kernel supplies
an admitted view for display.

### 2.10 Autoresearch

Bounded optimization over **non-sovereign** layers only: `/init` ranking,
prompts, skill routing, compression, repair targets.

```
Autoresearch ⊬ Kernel mutation
Autoresearch ⊬ ledger_append without helen_say + admission
```

---

## 3. Core entities

### 3.1 `UserContextEnvelope`

```json
{
  "local_datetime": "2026-07-18T20:02:00+02:00",
  "timezone": "Europe/Paris",
  "account_label": "Jean-Marie Tassy",
  "preferred_name": null,
  "provenance": "user_context",
  "confidence": "reported",
  "identity_authority": false
}
```

`identity_authority: false` is mandatory on reported user context. Labels
are not identity objects.

### 3.2 `OperationBoundary`

```json
{
  "boundary_id": "op_...",
  "goal": "synthesize API proposal",
  "scope": ["framework", "api", "memory"],
  "authority_class": "non_sovereign",
  "allowed_tools": ["read_memory", "write_framework_memory"],
  "forbidden_effects": ["kernel_mutation", "ledger_append", "identity_write"],
  "freshness_ttl": "session",
  "evidence_requirement": "local_read_or_explicit_source"
}
```

Boundaries declare **ceilings**, not grants. Forbidden effects are fail-closed.

### 3.3 `RuntimeObservation`

```json
{
  "observation_id": "obs_...",
  "probe_type": "repo_status",
  "raw_observation": "...",
  "observed_at": "2026-07-18T18:02:00Z",
  "source_surface": "runtime_probe",
  "freshness": "current_session",
  "authority": "NONE",
  "claim_status": "candidate"
}
```

### 3.4 `CandidateEvidencePacket`

```json
{
  "packet_id": "pkt_...",
  "source_observation_id": "obs_...",
  "raw_payload_ref": "exact_raw_output_or_bytes",
  "provenance": ["local_witness"],
  "canonical_hash": "sha256:...",
  "promotion_allowed": false,
  "authority": "NONE"
}
```

`promotion_allowed: false` by default. Hash-valid ⊬ admissible.

### 3.5 `Proposal`

```json
{
  "proposal_id": "prop_...",
  "intent": "update HELEN API memory",
  "requested_effect": "advisory_memory_update",
  "target_refs": ["helen_api_memory"],
  "evidence_refs": ["current_memory_read"],
  "authority_request": "non_sovereign",
  "risk_class": "low",
  "status": "proposed"
}
```

No meaningful effect without a prior explicit proposal in this model.

### 3.6 `AdmissionDecision`

```json
{
  "admission_id": "adm_...",
  "proposal_receipt_id": "receipt_...",
  "gate_results": {
    "claim": "pass",
    "evidence": "pass",
    "receipt": "pass",
    "chronos": "pass"
  },
  "reducer_result": "admit_or_hold",
  "admitted": false,
  "reason": "no sovereign admission path invoked"
}
```

Gates pass **conjunctively** or nothing moves. Example above is HOLD-shaped
(no sovereign path invoked).

---

## 4. Key endpoints

Endpoint paths are **proposal surface names**. They are not deployed
contracts until admitted and implemented under a separate GO.

| Method · Path | Domain | Effect class |
|---|---|---|
| `POST /session/init` | Operator Session | Creates operator session + assembled context; preview mode allowed |
| `POST /context/open` | Operator Session | Declares goal, scope, authority, tools, forbidden effects, evidence requirements |
| `POST /context/close` | Operator Session | Closes/checkpoints boundary: outputs, unresolved risks, **candidate** memory updates |
| `POST /governance/manifest/compile` | Governance | Hashes loaded governance surface; completeness + drift diagnosis |
| `POST /route/query` | Governance + Runtime | Routes by **capability** and **authority** separately |
| `POST /runtime/probe` | Runtime Reality | Volatile observations only — not truth claims |
| `POST /evidence/packetize` | Evidence | Deterministic candidate packets; **no ledger mutation** |
| `POST /proposal/create` | Proposal | Explicit proposal before meaningful action |
| `POST /action/execute` | Proposal And Action | Bounded execution of approved proposal → execution receipt |
| `POST /kernel/receipt/admit` | Kernel Truth | Reducer/admission; all required gates conjunctive |
| `GET /kernel/ledger/{ledger_id}/replay` | Kernel Truth | Reconstruct \(R_T\); replay status/hash |
| `POST /memory/framework/synthesize` | Memory Fabric | Concepts, module/API deltas, contradictions, open questions — **advisory** |
| `POST /evaluate` | Evaluator | Multi-axis evaluation (not a single scalar) |
| `POST /autoresearch/epoch/select` | Autoresearch | Bounded non-sovereign optimization targets |
| `POST /autoresearch/epoch/report` | Autoresearch | Trace closures, witnesses, tests, debt, ranker feedback |
| `GET /render/projection/{projection_id}` | Render Shell | Cockpit / diagram / WULMOJI / shell views; `authority=false` |

### 4.1 Routing split (normative)

`POST /route/query` must separate:

| Axis | Field role | Question answered |
|---|---|---|
| Capability | `task_type` | Who/what *can* do the work |
| Authority | `governance_context` | What the work is *allowed to mean* |

```
capability route ⊬ authority grant
```

### 4.2 Relation to existing SOT machinery (non-binding map)

| Proposal endpoint class | Existing SOT touchpoint (illustrative) |
|---|---|
| Kernel admit / ledger | `tools/helen_say.py` → `ndjson_writer` · kernel daemon handlers |
| Autoresearch | `temple/autoresearch/` · operator_pen · outbox packets |
| Render | `apps/helen-surface/` · `apps/goblin-warren/` (display-only organs) |
| do_next / policy | `helen_os/api/do_next_v1.py` (executor receipts only via `helen_say`) |

This table is orientation only. It does not claim the proposal routes already exist as HTTP.

---

## 5. Invariants

1. **Kernel defines truth.**
2. **Shell renders truth** (and may render non-truth as labeled non-truth).
3. **Tools and skills propose** changes; they do not admit.
4. **Memory supports continuity, not sovereignty.**
5. **Runtime observation is not Trust Reality** (\(R_R \neq R_T\)).
6. **Capability route does not grant authority.**
7. **Render does not imply state.**
8. **Hash-valid does not imply admissible.**
9. **Admissible does not imply meaningful.**
10. **No receipt means no ship.**
11. **Autoresearch may optimize only non-sovereign layers.**

Additional fail-closed companions:

```
identity_authority: false on reported user context
promotion_allowed: false by default on evidence packets
gates conjunctive on admission
preview mode cannot escalate forbidden_effects
```

---

## 6. Open decisions

Unresolved; do not pretend closed:

| # | Decision |
|---|---|
| 1 | Canonical serialization for manifests and receipts |
| 2 | Exact CHRONOS schema |
| 3 | Shared `claim_status` enum |
| 4 | Whether framework memory updates later receive lightweight synthesis receipts |
| 5 | Whether swarm coordination belongs in core HELEN OS or optional infrastructure |
| 6 | Whether `packet_id` and reported `observation_hash` should be unified |

---

## 7. Explicit non-claims

- This file is **not** an admitted API.
- Filing here is **not** ledger admission.
- Operator “saved to HELEN memory” (if any) is **advisory continuity** only.
- Garden / Warren MARK–INTERVENE teaching verbs are **out of scope** of this spine; see `MARK_INTERVENE_SURFACE_CONTRACT_V0.md` for that experimental projection.
- No endpoint in §4 may be treated as live until a separate implementation tranche with tests and (where required) operator-authorized admission.

---

## 8. Suggested next slices (non-binding)

Only after operator GO:

1. Freeze entity schemas as JSON Schema drafts under a non-sovereign path.
2. Map each domain to one existing module owner (no new dual spine).
3. Implement **read-only** probes + packetize in a sandbox before any admit route.
4. Keep `/kernel/receipt/admit` thin: wrap existing `helen_say` / daemon paths; never open a second ledger writer.

---

## Closing

```
R_R enters. R_T is replayed.
Only receipts bridge them.
Memory remembers; Kernel decides.
Render shows; it does not promote.
```

```
ENTER — SPEC.
authority=false · ledger_effect=none · HOLD_FOR_OPERATOR
```
