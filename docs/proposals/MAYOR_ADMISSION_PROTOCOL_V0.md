# MAYOR_ADMISSION_PROTOCOL_V0

**authority:** NON_SOVEREIGN
**canon:** NO_SHIP
**lifecycle:** DOCTRINE_DRAFT
**implementation_status:** NOT_IMPLEMENTED
**status:** Proposal — first emission driven by the closed control plane gap
**origin_signal:** `RECEIPT_SAFE_MUTATION_PROTOCOL_V0 §5.4 — MAYOR gate referenced but never specified; RAW artifacts accumulate with no admission path`
**parent_synthesis:** `docs/proposals/RECEIPT_SAFE_MUTATION_PROTOCOL_V0.md`, `helensh/SEED_V3.txt`, `helensh/kernel.py` (KNOWN_ACTIONS / GATED_ACTIONS)
**proposer:** claude-opus-4-7 (acting as GOBLIN doctrine drafter)
**attestor:** pending HER

---

## §0. Axiom

Carried forward from `RECEIPT_SAFE_MUTATION_PROTOCOL_V0`:

> **NO VALID RECEIPT = NO TRUSTED STATE MUTATION.**

Extended for admission:

> **NO MAYOR SEAL = NO ADMITTED CANON.**

A receipt without governance is invalid. A governed receipt without a MAYOR seal is *reviewable evidence*, not *enforced canon*. Trust in admitted canon is trust in the seal chain — nowhere else.

---

## §1. Problem

HELEN OS now produces well-formed RAW artifacts at rate: doctrine drafts, governed receipts, HAL verdicts, operator decisions, annotation-event audit trails, reseed pressure signals. The control plane closes the loop:

```
detect anomaly  →  hal_receipt_analyzer (§8 annotation events)
queue anomaly   →  review_queue --suspicious
review anomaly  →  review_cockpit --queue suspicious
```

But there is no path from RAW to admitted canon. Every artifact stays at `lifecycle_entry = "RAW"` with `auto_promotion_ceiling = "RAW"`. HAL PASS + operator approval is sufficient to *unblock* a receipt but not to *ratify* it.

This is correct for safety (RAW cannot become law by accident) and incomplete for evolution (the system cannot adopt its own well-justified outputs). `RECEIPT_SAFE_MUTATION_PROTOCOL_V0` is itself blocked at RAW: it cannot be ratified by the very mechanism it specifies. The bootstrap problem is the visible tip of the missing gate.

The recurring pressure is the *absence of an admission discipline*. Without MAYOR:

- Doctrine drafts accumulate but never become invariants the kernel enforces.
- Tools satisfy the §8 implementation contract informally but cite no admitted canon to refer to.
- Capabilities (`url_fetch`, `claw_external`) remain in `GATED_ACTIONS` indefinitely with no procedure for promotion.
- Schemas (`GEMMA_PROPOSAL_RAW_V1`) version informally — the next version is just a different string.

This protocol consolidates the missing transition into one ratifiable surface.

---

## §2. Admission objects

Admission applies to discrete, hashable artifacts. The kinds known to V0:

| ID | Object class | Example |
|----|--------------|---------|
| A1 | Doctrine document | `docs/proposals/*.md` with V0 frontmatter |
| A2 | Tool implementation | `tools/review_cockpit.py` at commit `f0a9520` |
| A3 | Schema version | `GEMMA_PROPOSAL_RAW_V1` |
| A4 | Capability grant | adds `url_fetch` to `GRANTED_CAPABILITIES` |
| A5 | Sub-agent identity | a HAL identity, an operator identity, a future MAYOR identity |
| A6 | Doctrine amendment | a delta against an existing admitted doctrine, pinning its predecessor hash |

Each admission targets exactly one A1–A6 object. **Multi-object admissions are not legal** (one seal = one target).

A proposed admission that **does not map to exactly one class** is **denied by default** (mirroring §3 of the parent doctrine).

---

## §3. Preconditions

The admission equation:

```
ADMIT(x) :=
    valid_receipts(x)
  ∧ HAL_PASS(x)
  ∧ operator_intent(x)
  ∧ replay_pass(x)
  ∧ no_suspicious_unresolved_events(x)
  ∧ MAYOR_SEAL(x)
```

All six conjuncts must hold at the moment of seal. **HAL PASS + operator approval is necessary but not sufficient.** A MAYOR who seals without verifying all six is in violation regardless of intent.

Each conjunct is defined precisely in §4–§9 below.

---

## §4. Required receipts

`valid_receipts(x)` holds when MAYOR can present, at seal time, the full receipt set for `x`:

### §4.1 Source receipt (R_source)

The M2 governed receipt that originated `x`. Required fields:

| Field | Required value |
|---|---|
| `schema_name` | known admitted schema (or schema being admitted in same seal) |
| `envelope_complete` | `true` |
| `lifecycle_entry` | `"RAW"` |
| `auto_promotion_ceiling` | `"RAW"` (MAYOR is the only actor that can promote) |
| `authority` | `false` (structural) |
| `receipt_timestamp_utc` | present, ISO-8601 UTC |

For object classes A2 (tool), A3 (schema), A4 (capability), R_source is the git commit object plus the kernel/test invocation receipts that demonstrate it (see §8).

### §4.2 Annotation receipts (R_hal, R_op)

The lane annotations written via `review_cockpit.py`:
- `R_source.hal_verdict.status == "PASS"` (see §5)
- `R_source.operator_decision.status ∈ {"APPROVED_FOR_SANDBOX_ONLY"}` (see §6)

### §4.3 Annotation events (R_events)

`R_source.annotation_events` exists, contains entries for both lane writes, and contains no unresolved suspicious entries (see §7).

### §4.4 Replay attestation (R_replay)

A separate receipt of schema `REPLAY_ATTESTATION_V1` (to be admitted) demonstrating `replay_pass(x)`. See §8.

### §4.5 Transitive admission receipts (R_deps)

For each admitted artifact `x` depends on (cited doctrine, used schema, granted capability), the prior `MAYOR_ADMISSION_RECEIPT_V1` for that dependency. Recursion bottoms out at the bootstrap admission (see §13).

**Missing or invalid R_source / R_hal / R_op / R_events / R_replay / any R_deps ⇒ admission rejected.**

---

## §5. HAL requirements

`HAL_PASS(x)` requires all of:

1. `R_source.hal_verdict.status == "PASS"` exactly. `NEEDS_MORE_RECEIPTS`, `FAIL`, or null all reject.
2. `R_source.hal_verdict.notes` is non-empty and at least 32 characters of rationale. Empty notes are a §10 forbidden pattern.
3. `R_source.hal_verdict.reviewer` resolves to an A5-admitted HAL identity. (Until any HAL identity is admitted, the bootstrap exception in §13 applies.)
4. `R_source.hal_verdict.timestamp_utc` is older than `R_source.receipt_timestamp_utc` and younger than the seal-time clock.
5. No subsequent annotation_event reverts the verdict (e.g. `PASS → null` clobber, `PASS → FAIL` flip) without a paired resolution event.

HAL PASS is a *technical-quality* attestation, not a *governance* attestation. HAL says "this proposal is well-formed and grounded." It does not say "admit this."

---

## §6. Operator requirements

`operator_intent(x)` requires all of:

1. `R_source.operator_decision.status == "APPROVED_FOR_SANDBOX_ONLY"` exactly. `PENDING_REVIEW` and `REJECTED` reject. (`PENDING_REVIEW` is explicitly an intent to defer, not approve.)
2. `R_source.operator_decision.notes` is non-empty and at least 32 characters of justification. Empty notes are a §10 forbidden pattern (the Round 1 incident is the canonical example).
3. `R_source.operator_decision.reviewer` resolves to an A5-admitted operator identity.
4. The operator decision is written *after* HAL PASS, not before. (Operator approving an un-reviewed proposal bypasses HAL.)
5. No subsequent annotation_event reverses the decision (e.g. `APPROVED → REJECTED` reversal) without a paired resolution event.

Operator intent is a *should-admit* attestation. The operator says "I have read the HAL verdict and the proposal, and I want this admitted." Operator intent + HAL PASS together are necessary; only MAYOR can act on them.

---

## §7. Suspicious-event handling

`no_suspicious_unresolved_events(x)` requires:

For each entry `e` in `R_source.annotation_events`:
- If `_classify_rewrite(e.lane, status_of(e.previous), status_of(e.next))` returns a suspicious message, then `R_source.annotation_events` must also contain a paired *resolution event* with all of:
  - `lane == "resolution"`
  - `actor` is an admitted operator identity (A5)
  - `next.status ∈ {"INTENTIONAL", "RESTORED", "AMENDED"}`
  - `next.refers_to_event_index` = the index of the suspicious event in the same list
  - `next.notes` is non-empty and ≥ 64 characters of justification

If any suspicious event lacks a resolution, admission is rejected. **The empty-notes signature on the Round 1 incident is exactly what this rule prevents from being silently admitted.**

`resolution` is a new lane (not `operator_decision`, not `hal_verdict`) so that the existing lane-isolation rule (§6 #4 of parent) is not weakened. The cockpit must grow a new path for resolution writes when this protocol is implemented; until then, no suspicious-event-bearing receipt can be admitted.

---

## §8. Replay requirements

`replay_pass(x)` is object-class-specific:

### §8.1 A1 doctrine

All §-references in the doctrine to existing kernel paths must resolve. All cited invariants (I1–I11, M1–M7, T1–T10) must match the admitted canon at seal time. A doctrine citing an unadmitted predecessor cannot itself be admitted.

### §8.2 A2 tool

The tool's regression test (see `RECEIPT_SAFE_MUTATION_PROTOCOL_V0 §8.9`) must pass deterministically. `R_replay` is the receipt of that test run, including the test's exit code, the SHA-256 of the test file, the SHA-256 of the tool file, and the wall-clock timestamp.

### §8.3 A3 schema

A round-trip on the canonical example receipt must produce byte-identical output. `R_replay` is the receipt of the round-trip including input hash and output hash.

### §8.4 A4 capability

`R_replay` enumerates every legal use of the capability in the kernel's call graph and demonstrates that each call site honours the governor's PENDING-then-grant flow.

### §8.5 A5 identity

`R_replay` is a key-binding receipt: the identity's public key (or equivalent attestation token) signed by the prior MAYOR (or, at bootstrap, attested by the operator directly).

### §8.6 A6 amendment

Both the predecessor doctrine's admission seal and the amendment's own R_source must be replayable. The amendment must explicitly pin the predecessor's seal hash.

In all cases, **`replay_pass` is verified at seal time, not at admission-request time.** Stale replay attestations (older than 24 hours, or older than the most recent dependent admission) are rejected.

---

## §9. MAYOR seal

The seal is a new receipt of schema **`MAYOR_ADMISSION_RECEIPT_V1`** (to be admitted as A3 in the bootstrap; see §13).

### §9.1 Required fields

| Field | Type | Semantics |
|---|---|---|
| `schema_name` | string | `"MAYOR_ADMISSION_RECEIPT_V1"` |
| `schema_version` | string | semver |
| `seal_hash` | string | SHA-256 of canonical body excluding `seal_hash` and `seal_timestamp_utc` |
| `seal_timestamp_utc` | string | ISO-8601 UTC; **not** part of hashed body (anti-T10) |
| `target_object_class` | string | one of `A1–A6` |
| `target_hash` | string | SHA-256 of the admitted artifact (R_source for A1, commit object for A2, etc.) |
| `target_path` | string | repo-relative path or git ref of target |
| `r_source_hash` | string | hash of R_source |
| `r_hal_hash` | string | hash of the hal_verdict object inside R_source |
| `r_op_hash` | string | hash of the operator_decision object inside R_source |
| `r_replay_hash` | string | hash of R_replay |
| `r_deps_hashes` | list[string] | hashes of all transitively-admitted dependencies |
| `suspicious_resolutions_attested` | list[int] | indices of resolved suspicious events in R_source |
| `granted_lifecycle_entry` | string | the new lifecycle for the target, e.g. `"ADMITTED"` |
| `granted_auto_promotion_ceiling` | string | new ceiling, e.g. `"ADMITTED"` |
| `mayor_identity` | string | the A5-admitted MAYOR identity that produced the seal |
| `mayor_attestation` | object | signature or equivalent attestation token |
| `authority` | bool | **always `false`** — MAYOR attests procedural completeness, not sovereignty |

### §9.2 Side effect on target

After the seal is written:
- For A1: the target receipt's `lifecycle_entry` is mutated to `granted_lifecycle_entry`. This is the M4 mutation class from the parent doctrine, and the seal is the only legal trigger.
- For A2/A3/A4/A6: a `canon_registry.json` entry is appended pinning `target_hash` → `seal_hash`.
- For A5: the identity registry receives the new identity with seal_hash as proof.

In all cases, the side effect is **single-write, append-only, never overwrites a prior seal**.

### §9.3 Append-only seal log

Every MAYOR seal is appended to `helensh/.state/admitted_canon.jsonl`, a hash-chained NDJSON ledger analogous to `live_ledger.jsonl`. Chain breakage is a §10 forbidden admission.

---

## §10. Forbidden admissions

A MAYOR tool that performs any of the following is in violation regardless of intent:

1. **Sealing without all six §3 preconditions.** Each conjunct must hold.
2. **Sealing with `authority = true`.** MAYOR is not sovereign.
3. **Sealing a target whose `R_source.envelope_complete` is `false`.**
4. **Sealing with empty operator notes or empty HAL notes** (Round 1 anti-pattern).
5. **Sealing with any unresolved suspicious annotation event.**
6. **Self-admission.** MAYOR cannot seal MAYOR's own seal. MAYOR cannot seal the MAYOR identity (A5) for which it is currently acting — a different MAYOR or the bootstrap operator must do so.
7. **Coalescing two admissions in one seal.** One seal, one target.
8. **Sealing a target without first re-reading the target from disk** (§6 #2 of parent — same race that bit the cockpit).
9. **Sealing with stale `R_replay`** (older than 24 hours or older than any cited dependency's admission).
10. **Sealing an object that depends on an unadmitted predecessor** (transitive closure).
11. **Embedding `seal_timestamp_utc` inside the hashed body** (anti-T10).
12. **Reusing a `seal_hash`** for a different target — collision = bug, never overwrite.
13. **Mutating an already-admitted artifact via a new seal of the same version.** Mutation requires A6 (amendment) with a new version string and a fresh seal pinning the prior seal hash.
14. **Bypassing canonical JSON serialization** for the hashed body.
15. **Granting `auto_promotion_ceiling` higher than the seal itself was admitted under.** A MAYOR admitted to seal A1/A6 only cannot seal A2 (tool). Authority does not auto-broaden.

---

## §11. Rollback / revocation

Admitted canon is not forever. Revocation produces a new receipt of schema **`MAYOR_REVOCATION_RECEIPT_V1`** that pins the prior seal hash and supplies:

- `revocation_reason`: enumerated (`DOCTRINE_SUPERSEDED`, `SECURITY_FLAW`, `REPLAY_DIVERGENT`, `IDENTITY_COMPROMISED`, `OPERATOR_RECALL`)
- `revocation_evidence`: receipt(s) supporting the reason (e.g. a HAL FAIL receipt on the formerly-PASSed artifact)
- `revoking_mayor_identity`: A5-admitted identity (same as the original sealer or a successor)
- `successor_seal_hash`: optional pointer to the replacing admission (for SUPERSEDED only)

### §11.1 Revocation preconditions

Revocation requires:
- `HAL_PASS` on the revocation receipt itself (HAL attests that the revocation is procedurally sound)
- `operator_intent` for the revocation
- A *fresh* `R_replay` showing the divergence/flaw, if the reason is `REPLAY_DIVERGENT` or `SECURITY_FLAW`
- All of §10 forbidden admissions apply, restated for revocation (no empty notes, no self-revocation by a compromised identity, etc.)

### §11.2 History preservation

The original admission seal is **never deleted or amended**. It stays in `admitted_canon.jsonl` with a revocation pointer appended to the same chain. The `lifecycle_entry` on the target transitions:

```
RAW → ADMITTED → QUARANTINED (via revocation)
```

Quarantined canon is read-only forever. It can be cited as historical reference (e.g. "the schema before V2") but not invoked as current law.

### §11.3 Re-admission

A quarantined artifact can be re-admitted only as an A6 amendment with a new version string. Re-using a quarantined seal is a §10 #12 violation.

---

## §12. Minimal implementation contract

A MAYOR tool is *admission-compliant* if and only if it satisfies **all** of the following. (Mirrors §8 of the parent doctrine; failure on any single check ⇒ non-compliant.)

### §12.1 Declared mutation class

The tool's docstring declares it performs **M4** mutations exclusively, and cites this protocol §9 as the gate it claims authority under.

### §12.2 Hard-constraint block

The docstring contains a `Hard constraints:` section enumerating the §10 forbidden admissions it explicitly does not perform.

### §12.3 Six-precondition verifier

The tool exposes a single pure function `can_admit(target) -> (bool, list[str])` that returns `(True, [])` if all six §3 conjuncts hold, or `(False, [reasons])` otherwise. No side effects, no IO beyond reading the receipts named in §4.

### §12.4 Single-pass seal

The tool writes the seal in one `write_text` call after a re-read of the target. No partial seals. No retry. If the write fails, the tool exits non-zero and no `canon_registry.json` mutation happens (receipt law).

### §12.5 Canonical serialization

The seal's hashed body uses `json.dumps(sort_keys=True, separators=(",", ":"))`. The on-disk receipt may use `indent=2, ensure_ascii=False` for readability, mirroring the cockpit pattern.

### §12.6 UTF-8 explicit

Every `write_text` call passes `encoding="utf-8"`. Read-tolerant decode (utf-8 then cp1252) on every read.

### §12.7 No timestamps in hashed bodies

`seal_timestamp_utc` lives outside the hash. (Anti-T10.)

### §12.8 Append-only chain

The seal is appended to `helensh/.state/admitted_canon.jsonl` with `previous_seal_hash` linking to the chain head. Chain breakage is detected at next admission attempt and refuses.

### §12.9 Determinism test

Running the tool twice on the same inputs produces zero diffs (same seal hash, same registry append). Test lives at `tools/test_mayor_admission.py`.

### §12.10 Refusal path

The tool refuses (non-zero exit, clear stderr) on every §10 forbidden pattern. The cockpit's read-before-write regression test is the model.

---

## §13. Halt boundary

GOBLIN halts here. This doctrine is RAW. It defines the gate that would admit it. The bootstrap is real and unavoidable:

> **A MAYOR cannot admit MAYOR.**

Three possible bootstraps, in order of decreasing trust:

### §13.1 Operator-attested bootstrap

The human operator (`JM Tassy` or named successor) directly attests, by manual write to `admitted_canon.jsonl`, the first MAYOR identity (A5). This identity then admits the schema `MAYOR_ADMISSION_RECEIPT_V1` (A3), then `MAYOR_REVOCATION_RECEIPT_V1` (A3), then `RECEIPT_SAFE_MUTATION_PROTOCOL_V0` (A1), then this protocol (A1), then the implementation tool (A2). Five seals total to close the loop.

### §13.2 Multi-operator bootstrap

Same as §13.1 but the first seal requires N-of-M signatures from a pre-declared operator quorum, written to a one-time `bootstrap_attestation.json` artifact. This trades operator convenience for resistance to single-operator capture.

### §13.3 Deferred bootstrap

This protocol stays at RAW until an operator session explicitly invokes the bootstrap. Until then:
- Reseed continues to surface pressure.
- The control plane (`detect → queue → review`) remains the only governance loop.
- New RAW artifacts accumulate.
- No artifact becomes admitted canon.

§13.3 is the current state and the safe default.

### §13.4 Resume conditions

This protocol advances to V1 only after:

1. **HER attestation**: HER reviews §1–§12 against `helensh/SEED_V3.txt`, `helensh/kernel.py`, the parent doctrine, and the current control-plane implementation. Disagreements become §10 amendments or §3 precondition refinements.
2. **HAL review (recorded)**: HAL receives this doctrine as a M2 proposal envelope. `hal_verdict` ∈ {`PASS`, `FAIL`, `NEEDS_MORE_RECEIPTS`}.
3. **Operator decision (recorded)**: `APPROVED_FOR_SANDBOX_ONLY` (this doctrine governs only the admission gate, not arbitrary canon), `REJECTED` (rationale enters next draft), or `PENDING_REVIEW`.
4. **Operator bootstrap election**: operator chooses §13.1, §13.2, or §13.3 and records the choice in a `BOOTSTRAP_ELECTION_V0` receipt.
5. **Implementation backfill**: only after operator approval AND bootstrap election, build `tools/mayor_admission.py` honouring §12.

GOBLIN does not advance past this halt. Nothing in this document instructs a sovereign actor. Nothing in this document mutates state. The only action this document performs is **the act of being written**, which is itself a §M5 derived artifact (per parent doctrine §3) — not state, not canon, just a candidate for future admission by the very gate it specifies.
