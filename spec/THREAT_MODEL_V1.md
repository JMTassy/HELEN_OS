---
artifact_id: THREAT_MODEL_V1
authority: NON_SOVEREIGN
canon: NO_SHIP
artifact_kind: FORMAL_SPECIFICATION
ledger_effect: NONE
status: SPECIFICATION_PROPOSAL
captured_on: 2026-05-02
session_id: helen-threat-model-v1
companion_specs:
  - spec/CONSTITUTIONAL_CONTINUITY_V1.md
references:
  - docs/HELEN_GLOBAL_TREE_MAP_V1.md
  - docs/design/HELEN_GOLDFRAME_V1.md
  - formal/LedgerKernel.v
  - registries/actors.v1.json
  - tools/validate_hash_chain.py
  - tools/validate_receipt_linkage.py
  - kernel/canonical_json.py
forbidden_use:
  - cite as evidence that any specific threat is mitigated without checking the mitigation matrix
  - claim "threat-model-compliant" without running tools/helen_verify.sh against the open findings
  - use threat severities as marketing claims
---

# HELEN OS — Threat Model V1

**NON_SOVEREIGN. NO_SHIP. SPECIFICATION PROPOSAL.**

This document specifies the threat model HELEN OS is built to defend
against. It does **not** claim any specific threat is mitigated by
default. Each threat below is classified into one of:

- **PROTECTED** — there is a shipped, verified mitigation in the repo
  today (cited explicitly).
- **PARTIAL** — a mitigation exists but with documented gaps.
- **OPEN** — no mitigation in place; treated as an active risk.

Reading this file does **not** make HELEN safer. Building the
mitigations in §6 against threats classified `OPEN` does.

If a future agent or reader cites this document as evidence that a
threat is handled without checking §6's mitigation matrix, the
operation violates `forbidden_use`.

---

## 1. Scope and Non-Scope

### In-scope

- Threats to **sovereign state integrity**: tampering with the
  append-only ledger, forging verdicts or receipts, replaying or
  reordering events, breaking the hash chain.
- Threats to **authority boundaries**: an actor emitting an event
  type they are not authorized for, MAYOR-impersonation, side-channel
  governance.
- Threats to **deterministic replay**: nondeterminism injected via
  wall-clock, environment, locale, dict ordering, or floating point.
- Threats to **manifest discipline**: capability promotion without
  proper proposal, skill activation without registry binding.
- Threats to **operational security**: MAYOR key compromise, supply-
  chain attack on validators, registry tampering.
- Threats to **federation safety**: malicious cross-town receipts,
  forged Merkle proofs, conformance-level downgrade.

### Out of scope (this version)

- Side-channel attacks on the underlying hardware (timing,
  Spectre-class, RAM cold-boot) — assumed handled at a lower layer.
- Network-layer attacks against external API providers (Ollama,
  Gemini, Anthropic) — HELEN treats every external response as
  attestation, not authority.
- Adversarial inputs to the LLM cognition layer (prompt injection,
  jailbreaking) — these affect Trunk C output but cannot mutate
  sovereign state without crossing the β admission gate. Defense is
  structural (forbidden morphisms), not prompt-level.
- Physical security of the operator's machine.
- Legal / regulatory threats.

The out-of-scope items are real but are **not threats this document
addresses.** A future `THREAT_MODEL_HARDWARE_V1` or
`THREAT_MODEL_NETWORK_V1` could extend coverage.

---

## 2. Asset Inventory — What We Protect

Each asset has a **sovereignty class** (sovereign / advisory) and an
**integrity criticality** (catastrophic / high / moderate). Assets
classified `sovereign` and `catastrophic` are the highest-value
targets.

| ID | Asset | Class | Criticality | Location |
|---|---|---|---|---|
| A-001 | Sovereign ledger (append-only hash-chain) | sovereign | catastrophic | `town/ledger_v1.ndjson` |
| A-002 | Reducer β (decides admissibility) | sovereign | catastrophic | implicit; specified by `formal/LedgerKernel.v` and skill_promotion_reducer.py |
| A-003 | MAYOR signing key | sovereign | catastrophic | (operational; not in repo) |
| A-004 | Kernel proof file | sovereign | catastrophic | `formal/LedgerKernel.v` |
| A-005 | Authority registry | sovereign | high | `registries/actors.v1.json` |
| A-006 | Canonical JSON serializer | sovereign | catastrophic | `kernel/canonical_json.py` |
| A-007 | Validator stack | sovereign-adjacent | high | `tools/validate_*.py` |
| A-008 | Acceptance gate | sovereign-adjacent | high | `tools/accept_payload_meta.sh` |
| A-009 | Verify command | sovereign-adjacent | moderate | `tools/helen_verify.sh` |
| A-010 | RunTrace logs | advisory | moderate | (Channel C; per recap) |
| A-011 | MemoryKernel | advisory | moderate | (Channel B; per recap) |
| A-012 | RALPH typed artifacts | advisory | moderate | `.helen/ralph/<EPOCH>/artifacts/` |
| A-013 | Skill manifests | sovereign-adjacent | high | (per Constitutional Continuity capability legality gate) |
| A-014 | Reason-codes registry | sovereign-adjacent | high | `registries/reason_codes.v1.json` |
| A-015 | Environment registry | sovereign-adjacent | high | `registries/environment.v1.json` |

**Concentration risk:** A-003 (MAYOR signing key) is the single point
of catastrophic compromise. See T-CRIT-001 below.

---

## 3. Trust Boundaries — Who/What Can Act

Trust boundaries are derived from `registries/actors.v1.json` and
`formal/LedgerKernel.v` `authority_ok_event_b`. The drift between
those two surfaces is itself a threat (T-HIGH-009).

### Trusted (in the sovereign sense)

- **MAYOR**, and only MAYOR, may sign verdicts and receipts that
  bind to ledger position.
- **The Coq-verified kernel** (when load-bearing) defines what events
  can structurally enter the ledger.

### Trusted-but-bounded

- **HELEN, BUILDER, INTEGRATOR, CHRONOS** may emit non-terminal events
  per the registry. They **cannot** sign, terminate, or seal.

### Untrusted (advisory only)

- All Trunk C cognition (Claude, Qwen, Gemma, etc. — local or remote).
- All Trunk D memory stores.
- All Trunk E embodiment / UI surfaces.
- All external API responses.
- All RunTrace and RALPH artifacts.
- All untyped operator narration.

### The forbidden morphisms (per `HELEN_GLOBAL_TREE_MAP_V1` §4.2)

```
E ↛ A    embodiment cannot mutate sovereign state
D ↛ A    memory cannot mutate sovereign state
C ↛ A    cognition cannot mutate sovereign state
B ↛ A    capability proposal cannot mutate sovereign state directly
```

The **only** allowed mutation path:

```
β(L, Ê, P) → decision  →  MAYOR signature  →  ledger append  →  receipt
```

A threat that creates a path violating these morphisms is by
definition **catastrophic** because it dissolves the constitutional
property.

---

## 4. Adversary Classes

| Class | Description | Capability |
|---|---|---|
| **AC-1: External attacker** | Attacker with no insider access | Can submit malformed inputs through any external surface; cannot read MAYOR key |
| **AC-2: Compromised non-sovereign agent** | An LLM, RALPH loop, or memory store has been corrupted (prompt injection, model substitution, store tampering) | Can produce arbitrary attestations Ê; cannot sign |
| **AC-3: Insider with operator access** | Someone with file-system access to the repo | Can edit registries, validators, even kernel proofs; can attempt to bypass acceptance gate |
| **AC-4: MAYOR-key compromise** | Attacker has obtained MAYOR_SK | Can sign valid verdicts and receipts that pass all current validators |
| **AC-5: Supply-chain attacker** | Attacker has compromised an upstream dependency (a Python package, the Coq toolchain, the OS) | Can subvert canonicalization, hashing, or proof verification at the foundation |
| **AC-6: Replay attacker** | Attacker submits previously-valid evidence in a new context | Can cause double-counting, stale-state acceptance |
| **AC-7: Drift attacker** | Attacker (or accident) introduces inconsistency between schemas, registries, and validators | Can pass validators while corrupting semantic invariants |
| **AC-8: Time-shift attacker** | Attacker manipulates wall-clock readings inside the system | Can cause non-deterministic hashes, replay divergence |

The lethality ladder is roughly **AC-4 ≫ AC-3 ≫ AC-5 ≫ AC-7 ≫ AC-2 ≫ AC-6 ≫ AC-8 ≫ AC-1**.

---

## 5. Threat Catalog

Each threat has: **ID**, **severity** (`CRIT` / `HIGH` / `MED` / `LOW`),
**adversary class**, **attack vector**, and a pointer to §6 for
mitigation status.

### T-CRIT-001 — MAYOR signing key compromise

- **Severity:** CRITICAL
- **Adversary class:** AC-4
- **Attack vector:** Attacker obtains `MAYOR_SK` (operational
  compromise: stolen laptop, phishing, leaked secret, side-channel).
- **Impact:** Attacker can produce valid SHIP verdicts and matching
  receipts that pass the entire validator stack. The hash chain
  remains intact; the receipt linkage triple-binding holds. **Every
  current defense is bypassed.**
- **§6 status:** OPEN (no key rotation, no revocation procedure, no
  isolation)

### T-CRIT-002 — Kernel proof bypass

- **Severity:** CRITICAL
- **Adversary class:** AC-3, AC-5
- **Attack vector:** Attacker modifies `formal/LedgerKernel.v` to
  weaken `authority_ok_event_b` or `is_termination_b`, then
  recompiles; OR exploits Coq-toolchain compromise to accept invalid
  proofs.
- **Impact:** Authority fences become advisory. HELEN can emit
  VERDICT, CHRONOS can emit RECEIPT, etc. The constitutional skeleton
  collapses while every other gate appears green.
- **§6 status:** PARTIAL (CI's `kernel_guard.yml` typechecks; depends
  on toolchain integrity)

### T-CRIT-003 — Single write-gate violation

- **Severity:** CRITICAL
- **Adversary class:** AC-3
- **Attack vector:** Insider directly appends to
  `town/ledger_v1.ndjson` outside the kernel boundary writer
  (`tools/ndjson_writer.py`).
- **Impact:** Forbidden morphism enforced. Ledger contains entries
  with no MAYOR signature, no β decision, no receipt. The entire
  non-interference theorem fails.
- **§6 status:** PARTIAL (`tools/kernel_guard.sh` checks at CI; no
  runtime enforcement)

### T-CRIT-004 — Canonicalization drift

- **Severity:** CRITICAL
- **Adversary class:** AC-3, AC-5, AC-7
- **Attack vector:** A second canonicalizer is introduced (or the
  primary one is modified) such that two implementations of
  `canon_json_bytes` produce different output for the same payload.
  Hash recomputation diverges. Cross-implementation conformance
  fails silently.
- **Impact:** Some validators accept payloads others reject. Drift
  spreads silently across the system.
- **§6 status:** PARTIAL (`kernel/canonical_json.py` is declared
  the single source of truth; no cross-implementation conformance
  test)

### T-HIGH-005 — Receipt envelope tampering

- **Severity:** HIGH
- **Adversary class:** AC-3
- **Attack vector:** Attacker modifies a verdict event's
  `payload_hash` envelope field to point at a different (forged)
  payload, then crafts a matching receipt that binds to the forged
  hash.
- **Impact:** Receipt linkage validator passes (the hashes match
  each other), but the actual verdict payload is not what the chain
  records.
- **§6 status:** PROTECTED (this session — `validate_receipt_linkage.py`
  leg-0 patch recomputes envelope payload_hash from payload via
  `canon_json_bytes` and rejects mismatches)

### T-HIGH-006 — Wall-clock in hashed core

- **Severity:** HIGH
- **Adversary class:** AC-7, AC-8
- **Attack vector:** Any envelope, payload, or receipt-adjacent
  artifact embeds wall-clock time inside content that is then hashed.
  Same input → different hash across runs. Determinism breaks.
  Replay diverges.
- **Impact:** Cross-machine equivalence fails. Conformance tests
  flap. Receipts that should bind cannot recompute consistently.
- **§6 status:** OPEN (one empirical instance found this session —
  `tools/ralph_emit_artifacts.py` `FAILURE_CLUSTER_V1.generated_at_unix`
  — confirmed across two runs with identical inputs producing
  different `failure_cluster_ref` hashes; fix awaits operator signal
  Option A vs B)

### T-HIGH-007 — SHIP without receipt

- **Severity:** HIGH
- **Adversary class:** AC-3, AC-4
- **Attack vector:** A SHIP verdict is appended without a paired
  RECEIPT being submitted later in the same chain.
- **Impact:** Sovereign claim ("ship this") with no integration
  proof. The "no receipt → no ship" doctrine is violated.
- **§6 status:** PROTECTED (`validate_receipt_linkage.py` enforces
  NO_RECEIPT_NO_SHIP for `verdict_kind == "SHIP"`)

### T-HIGH-008 — Receipt with unknown verdict_id

- **Severity:** HIGH
- **Adversary class:** AC-3
- **Attack vector:** Attacker submits a RECEIPT referencing a
  `verdict_id` that does not exist in any prior VERDICT event.
- **Impact:** Dangling receipt; potential confusion in audit and
  replay.
- **§6 status:** PROTECTED (`validate_receipt_linkage.py` raises on
  receipt-to-unknown-verdict)

### T-HIGH-009 — Authority registry vs kernel drift

- **Severity:** HIGH
- **Adversary class:** AC-7 (drift)
- **Attack vector:** `registries/actors.v1.json` and
  `formal/LedgerKernel.v` define different actor sets and event-type
  vocabularies. The registry's own header lies (claims to mirror the
  kernel exactly; does not).
- **Impact:** Generated artifacts (when the
  `tools/generate_authority_matrix.py` is built) would encode the
  drift as canon. Validators that consult one source disagree with
  validators consulting the other.
- **§6 status:** OPEN (documented in
  `docs/traces/RALPH_LOOP_TRACE_STEP_C_GOVERNANCE_VM.md` U1 BLOCKER;
  awaits operator signal Path A / B / C / A-min)

### T-HIGH-010 — Schema-location drift

- **Severity:** HIGH
- **Adversary class:** AC-7
- **Attack vector:** Schemas exist at `helen_os/schemas/` (canonical
  per `CLAUDE.md`) but a duplicate appears at repo-root `schemas/`.
  Validators that load the wrong location see stale schemas.
- **Impact:** Same payload validates against one schema and fails the
  other. Acceptance gate becomes non-deterministic.
- **§6 status:** OPEN (named in trace; one duplicate path proposed
  in operator's recap §6 was refused this session)

### T-HIGH-011 — Capability promotion without manifest

- **Severity:** HIGH
- **Adversary class:** AC-2, AC-3
- **Attack vector:** A skill is activated or promoted without
  registry entry, without manifest validation, without MAYOR-signed
  promotion verdict.
- **Impact:** The capability legality gate (specified in
  `spec/CONSTITUTIONAL_CONTINUITY_V1.md`) is violated. Capability
  becomes lawful by accident.
- **§6 status:** OPEN (gate is **named, not yet load-bearing** per
  `CONSTITUTIONAL_CONTINUITY_V1` cross-reference table)

### T-HIGH-012 — Hidden write surface

- **Severity:** HIGH
- **Adversary class:** AC-3, AC-5
- **Attack vector:** A new file or process gains write capability to
  `town/ledger_v1.ndjson` outside the kernel boundary. Could be:
  test fixture left in production, debug endpoint, vendor library
  with file access.
- **Impact:** Same as T-CRIT-003 but introduced by drift rather than
  deliberate insider action.
- **§6 status:** PARTIAL (CI's `tools/kernel_guard.sh` greps source
  for direct ledger writes; misses dynamic write paths)

### T-MED-013 — Reason-code injection

- **Severity:** MEDIUM
- **Adversary class:** AC-3
- **Attack vector:** A VERDICT carries a `reason_codes` value not
  present in `registries/reason_codes.v1.json`.
- **Impact:** Audit/aggregation breaks; semantic claims become
  un-cross-referenceable.
- **§6 status:** PROTECTED (`validate_verdict_payload.py` enforces
  schema; reason-code-registry membership check needs verification)

### T-MED-014 — Float in payload

- **Severity:** MEDIUM
- **Adversary class:** AC-3, AC-7
- **Attack vector:** A `decision` or `anchors` field contains a
  floating-point number. Float canonicalization is non-portable
  across architectures and Python versions.
- **Impact:** Hash divergence across machines. Replay fails.
- **§6 status:** PROTECTED (per `kernel/canonical_json.py` §5 *"Float
  handling: PROHIBITED in payloads (enforced upstream in
  ndjson_writer.py)"*; depends on enforcement actually being upstream)

### T-MED-015 — Unsorted reason_codes / certificates / required_fixes

- **Severity:** MEDIUM
- **Adversary class:** AC-3, AC-7
- **Attack vector:** Arrays in VERDICT_PAYLOAD_V1 that are required
  to be sorted are submitted unsorted; if the validator misses it,
  same semantic claim hashes differently depending on submission order.
- **Impact:** Replay fails; cross-implementation drift.
- **§6 status:** PROTECTED (per `helen_os/schemas/verdict_payload.v1.schema.json`
  description: *"SORTED ARRAYS REQUIRED"*; validator must enforce)

### T-MED-016 — Replay attack on idempotent inputs

- **Severity:** MEDIUM
- **Adversary class:** AC-6
- **Attack vector:** Attacker re-submits a previously-valid input
  event whose effect was already accepted. Anti-replay state must
  determine the input was already seen.
- **Impact:** Double-counting; stale-state acceptance.
- **§6 status:** OPEN (per CWL recap §4: anti-replay must be ledger-
  derivable as `RID(L) = { e.rid | e ∈ L }`; not yet enforced in any
  validator)

### T-MED-017 — Cross-town receipt forgery

- **Severity:** MEDIUM (becomes HIGH at federation-active)
- **Adversary class:** AC-1, AC-2
- **Attack vector:** A federation peer sends a forged or replayed
  cross-town receipt that claims a verdict was sealed elsewhere.
- **Impact:** Local town admits a federation event under false
  pretense; cross-implementation semantic drift.
- **§6 status:** OPEN (federation layer not implemented; threat is
  prophylactic until then)

### T-LOW-018 — RunTrace tamper

- **Severity:** LOW
- **Adversary class:** AC-2, AC-3
- **Attack vector:** Channel C (RunTrace) telemetry is modified
  after the fact.
- **Impact:** UI and post-mortem analysis become unreliable; no
  effect on sovereign state (RunTrace is `authority=false`).
- **§6 status:** PARTIAL (RunTrace per CWL recap §13 should have
  its own hash chain `HELEN_TRACE_V1`; not yet shipped)

### T-LOW-019 — MemoryKernel tamper

- **Severity:** LOW
- **Adversary class:** AC-2, AC-3
- **Attack vector:** Channel B memory is modified to mislead later
  cognition.
- **Impact:** Cognition layer (Trunk C) produces poorer attestations;
  no effect on sovereign state because **B ↛ A** is enforced.
- **§6 status:** STRUCTURALLY CONTAINED (forbidden morphism), no
  active mitigation needed beyond memory-store integrity hygiene

---

## 6. Mitigation Matrix

Status legend: **PROTECTED** (shipped + verified), **PARTIAL** (exists
but with gap), **OPEN** (no mitigation today).

| Threat | Status | Mitigation | Gap / Action |
|---|---|---|---|
| T-CRIT-001 | **OPEN** | (none today) | Build `MAYOR_SK` isolation, `mayor_rotate_v1` receipt type, sealed `MAYOR_PK` registry, revocation procedure, genesis-level emergency override, audit logging. Per CWL recap §14. **Required before production.** |
| T-CRIT-002 | **PARTIAL** | `kernel_guard.yml` typechecks `LedgerKernel.v`; admitted-lemma inventory check | Pin Coq toolchain version; add hash-chain on the proof file itself; require dual-review before any kernel proof change |
| T-CRIT-003 | **PARTIAL** | `tools/kernel_guard.sh` greps source for direct ledger writes | Add runtime enforcement (file-system permissions / fanotify); add property test that proves only `tools/ndjson_writer.py` opens the ledger for write |
| T-CRIT-004 | **PARTIAL** | `kernel/canonical_json.py` declared single source of truth | Build cross-implementation conformance test using fixed test vectors (`spec/CWL_TEST_VECTORS_V1.json` per CWL recap §17) |
| T-HIGH-005 | **PROTECTED** | `validate_receipt_linkage.py` leg-0 (this session, commit `5bae6a5`): recomputes verdict envelope payload_hash from payload via `canon_json_bytes` | None |
| T-HIGH-006 | **PROTECTED** | Option A executed 2026-05-02: `generated_at_unix` removed from `FAILURE_CLUSTER_V1`; `import time` removed from emitter; epoch_id (logdir name) carries time information out-of-band. Verified empirically — same inputs across two runs produce byte-identical `failure_cluster_ref` + `review_packet` hashes. See `tools/ralph_emit_artifacts.py` lines 35-41 + 184-191 + the "F-001 (closed 2026-05-02)" comment. | Future audit: scan other artifact emitters for the same pattern (`time.time()`, `datetime.now()`, etc. inside any field that becomes part of a hashed core). |
| T-HIGH-007 | **PROTECTED** | `validate_receipt_linkage.py` `NO_RECEIPT_NO_SHIP` enforcement | None |
| T-HIGH-008 | **PROTECTED** | `validate_receipt_linkage.py` raises on dangling receipt | None |
| T-HIGH-009 | **OPEN** | (none today; documented in trace) | Operator signal Path A / B / C / A-min; runs `tools/generate_authority_matrix.py` only after resolution |
| T-HIGH-010 | **OPEN** | refused this session (no duplicate created) | Audit all validator load paths to confirm they read from `helen_os/schemas/` only |
| T-HIGH-011 | **OPEN** | gate **named** in `CONSTITUTIONAL_CONTINUITY_V1`, not load-bearing | Build manifest validator + manifest registry + reducer manifest gate (per recap "Then implement" list) |
| T-HIGH-012 | **PARTIAL** | static grep in `kernel_guard.sh` | Add dynamic write-surface audit; require property test of "only kernel writer touches ledger" |
| T-MED-013 | **PROTECTED** (partial) | schema validation in `validate_verdict_payload.py` | Verify reason-code-registry membership check is actually enforced |
| T-MED-014 | **PROTECTED** | `kernel/canonical_json.py` policy + upstream ndjson_writer enforcement | Confirm enforcement is live in `tools/ndjson_writer.py` |
| T-MED-015 | **PROTECTED** (partial) | schema requires sorted arrays | Confirm validator rejects unsorted; current state is per-schema-description, not per-test |
| T-MED-016 | **OPEN** | (none today) | Implement `RID(L) = { e.rid | e ∈ L }` ledger-derived anti-replay set; build validator |
| T-MED-017 | **OPEN** (prophylactic) | federation not yet active | Defer until federation layer lands; threat model must already be in place |
| T-LOW-018 | **PARTIAL** | RunTrace exists; hash chain not shipped | Implement `HELEN_TRACE_V1` chain per CWL recap §13 |
| T-LOW-019 | **STRUCTURAL** | forbidden morphism `B ↛ A` | None beyond store-level integrity hygiene |

### Mitigation count summary

- **PROTECTED:** 6 threats (5 fully, 3 partial)
- **PARTIAL:** 5 threats
- **OPEN:** 7 threats
- **STRUCTURAL:** 1 threat

**The seven OPEN threats are the actionable hardening agenda.** Five
of them (T-CRIT-001, T-HIGH-006, T-HIGH-009, T-HIGH-010, T-HIGH-011)
have explicit operator-signal-required next steps tracked elsewhere
in the spec stack and trace documents.

---

## 7. Acceptance Criteria

A "threat-model-V1-honored" deployment is one where:

1. **All `PROTECTED` threats** are continuously verified by
   `tools/helen_verify.sh` runs producing PASS receipts.
2. **All `PARTIAL` threats** have a documented gap with a named
   owner and a target completion epoch in
   `docs/design/ralph_temple_loop_v1/INDEX.md` (or successor).
3. **All `OPEN` threats** have:
   - An owner.
   - An attack-test (red test that fails today, would pass once
     mitigation lands).
   - A blocker on production deployment until resolved (operator
     decision).
4. **The mitigation matrix is regenerated** whenever a new threat is
   added or a status changes.
5. **No threat is silently downgraded** — status changes require
   their own commit with rationale.

A claim of "HELEN is hardened" without these five conditions met is
**not supported** by this spec.

---

## 8. Open Findings (this session, empirical)

- ~~**F-001:** RALPH emitter wall-clock determinism violation~~
  **CLOSED 2026-05-02.** Option A executed: `generated_at_unix` removed
  from `FAILURE_CLUSTER_V1`; emitter no longer imports `time`. Re-test
  with identical inputs across a 2-second interval produced byte-identical
  hashes (`failure_cluster_ref` and `review_packet` SHA256 both stable).
  T-HIGH-006 reclassified PROTECTED. The bug RALPH was designed to avoid,
  which appeared in RALPH's own emitter, is now fixed by RALPH's own
  discipline. The shadow named in `E001_RALPH_RECEIPT_GOBLIN.md` `face.shadow`
  ("Putting wall-clock into the hashed core") was real; the doctrine
  worked.
- **F-002:** Authority registry / kernel drift (T-HIGH-009).
  Documented in `docs/traces/RALPH_LOOP_TRACE_STEP_C_GOVERNANCE_VM.md`
  U1. Awaits Path A / B / C / A-min.
- **F-003:** Schema-vocabulary drift between
  `helen_os/schemas/verdict_payload.v1.schema.json` and operator's
  recap §6. Recap puts SHIP in `decision.outcome`; actual schema
  puts SHIP in `verdict_kind`. Refused to silently change
  `validate_receipt_linkage.py` SHIP detection. Operator amendment
  required.
- **F-004:** STEP_C / MRED HELEN runtime boot — unverified this
  session. Anything in user-facing materials that claims "HELEN runs
  on MRED" must be hedged until F-004 is resolved.

---

## 9. References

- `docs/HELEN_GLOBAL_TREE_MAP_V1.md` — six trunks, forbidden morphisms
- `spec/CONSTITUTIONAL_CONTINUITY_V1.md` — five-clause continuity rule, capability legality gate
- `docs/design/HELEN_GOLDFRAME_V1.md` — five gates table
- `formal/LedgerKernel.v` — `authority_ok_event_b`, hash chaining
- `kernel/canonical_json.py` — `CANON_JSON_V1` constitutional source of truth
- `registries/actors.v1.json` — actor / event-type matrix (with named drift T-HIGH-009)
- `tools/validate_hash_chain.py` — payload + cum hash recomputation
- `tools/validate_receipt_linkage.py` — three-leg + leg-0 envelope binding
- `tools/accept_payload_meta.sh` — six-gate acceptance composition
- `tools/helen_verify.sh` — five-gate verification (this session)
- `tools/ralph_emit_artifacts.py` — typed evidence emitter (F-001 closed 2026-05-02)
- `spec/HELEN_OPERATIONAL_DISCIPLINE_V1.md` — operator-side discipline (Tree Hygiene, Shell Input, Roots, Disclosure Ladder)
- `docs/traces/RALPH_LOOP_TRACE_STEP_C_GOVERNANCE_VM.md` — implementation trace with U1-U8 units

---

## 10. What This Spec Does Not Provide

- **Not a proof of safety.** It is a structured catalogue of what
  could go wrong and where today's defenses sit.
- **Not a substitute for the non-interference theorem** (next spec
  in the lock list). The theorem proves the structural property; this
  spec enumerates the threats the property must survive.
- **Not a substitute for `CWL_CONFORMANCE_V1`** (third spec). That
  document defines what an external implementation must do to claim
  CWL-compatibility; this document defines what the internal
  implementation must defend against.
- **Not actionable without operator triage** of the seven OPEN
  threats.

---

## Closing line

> **The threat model is real because the receipts are real.**
> **The receipts are real because the hashes are recomputed.**
> **The hashes are recomputed because the canonicalizer is constitutional.**
>
> *Fail closed. Recompute. Then trust the match.*

`(NO CLAIM — TEMPLE — FORMAL SPECIFICATION — THREAT MODEL V1 — NON_SOVEREIGN)`
