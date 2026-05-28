# RECEIPT_SAFE_MUTATION_PROTOCOL_V0

**authority:** NON_SOVEREIGN
**canon:** NO_SHIP
**lifecycle:** DOCTRINE_DRAFT
**implementation_status:** NOT_IMPLEMENTED
**status:** Proposal — first emission driven by `reseed_topics.py` governance pressure
**origin_signal:** `HIGH ev=3 "mutating ledger without receipt"` — RALPH epochs 8, 9, 10
**parent_synthesis:** `helensh/SEED_V3.txt`, `docs/protocols/RALPH_W_LOOP_V0.md`, `docs/protocols/GOBLIN_MODE_V0.md` (helen-os-JMTC)
**proposer:** claude-opus-4-7 (acting as GOBLIN doctrine drafter)
**attestor:** pending HER

---

## §0. Axiom

> **NO VALID RECEIPT = NO TRUSTED STATE MUTATION.**

A mutation without a receipt did not happen. A receipt without proof of governance is not valid. Trust in state is trust in the receipt chain — nowhere else.

This is the formal statement of what HELEN OS already calls *receipt law* ("no receipt = no reality"), extended from "no observable action" to **"no trusted writable state"**.

---

## §1. Problem

Three independent RALPH autoresearch epochs (8, 9, 10) surfaced the same sovereignty violation under different hypotheses: *the system can be coerced or tricked into mutating durable state without producing a corresponding receipt*. A single BLOCKED GEMMA proposal on UTF-8 verification surfaced six adjacent missing-evidence threads, all reducible to "we cannot verify the mutation actually happened the way we claim".

The recurring pressure is not a bug. It is the absence of a doctrine. HELEN OS today has:

- a receipt schema (`GEMMA_PROPOSAL_RAW_V1`),
- an append-only hash-chained ledger (`helensh/.state/live_ledger.jsonl`),
- a governor with 5 fail-closed gates (`helensh/kernel.py`),
- canonical serialization (`sort_keys=True, separators=(",",":")` + SHA-256),
- replay verification (`helensh/replay.py`, `gnf_replay.py`),

but no single document specifying **what conditions must hold for any actor — kernel, adapter, agent, operator — to call a state change "real"**. The kernel enforces the receipt-for-action law. Nothing yet enforces the receipt-for-mutation law as a separate, named discipline.

Without that doctrine, every new tool risks introducing a silent write path. Examples observed in the current corpus:

- A projection adapter could overwrite quarantine files non-idempotently (the current adapter does not — but nothing in writing forbids the next one).
- An autoresearch loop could append to its own NDJSON without chaining the previous hash (the current loop does — but nothing canonical defines what "valid chain extension" means for non-ledger NDJSON).
- A cockpit write could silently coalesce `operator_decision` and `hal_verdict` (the current cockpit does not — but the discipline is asserted only by code shape, not by doctrine).

This protocol consolidates those scattered enforcements into one ratifiable surface.

---

## §2. Threat model

The doctrine protects against the following mutation classes, ordered by severity:

| ID  | Threat                                | Example                                                                                |
|-----|----------------------------------------|----------------------------------------------------------------------------------------|
| T1  | **Silent write**                       | A function returns success but never wrote a receipt; later replay diverges from claim |
| T2  | **Unchained extension**                | Append to an NDJSON without binding `previous_hash`; tamper detection blind            |
| T3  | **Lane crossing**                      | Operator path mutates HAL field, or HAL path mutates operator field                    |
| T4  | **Lifecycle promotion without gate**   | RAW silently upgraded to admitted without MAYOR receipt                                |
| T5  | **Authority laundering**               | `authority=True` proposal mutates state via a workaround                               |
| T6  | **Replay-divergent rewrite**           | Receipt file edited after the fact; chain still verifies but state replay disagrees    |
| T7  | **Capability bypass**                  | Gated action (`url_fetch`, `claw_external`) executed without granted capability        |
| T8  | **Non-canonical serialization**        | Same logical state hashes differently because key order or whitespace drifted          |
| T9  | **Half-write**                         | Process killed mid-write leaves partial JSON; reader cannot distinguish from intent    |
| T10 | **Time-injected hash**                 | Timestamp inside the hashed body makes "same input, same output" replay impossible     |

T1, T2, T5 are the threats `reseed_topics.py` actually surfaced. T3, T4, T7 are already enforced piecemeal in code. T6, T8, T9, T10 are latent and unaddressed.

---

## §3. Mutation classes

Every state change in HELEN OS belongs to exactly one of these classes. The class determines which gates apply.

### M1 — Ledger mutation (canonical, hash-chained)

Append-only writes to `helensh/.state/live_ledger.jsonl` or any file that participates in the kernel's chain-of-hashes. Two-receipt rule (proposal + execution, invariant I3) applies. **All M1 writes go through `LedgerWriter` / `persisted_step`.** No other path is legal.

### M2 — Quarantine receipt write (RAW lifecycle)

Writes to `GOVERNANCE/GEMMA_PROPOSALS/`, `GOVERNANCE/RALPH_PROPOSALS/`, or any future `GOVERNANCE/*_PROPOSALS/` directory. Each file is one self-contained JSON receipt. `lifecycle_entry = "RAW"` and `auto_promotion_ceiling = "RAW"` are immutable until §5 gates fire.

### M3 — Lane annotation (operator or HAL)

Writes to a single field of an existing M2 receipt: either `operator_decision` (operator lane) or `hal_verdict` (HAL lane). Lanes are **strictly isolated** — see §6.

### M4 — Lifecycle promotion (MAYOR-only)

Mutation of `lifecycle_entry` or `auto_promotion_ceiling` on a M2 receipt. The only legal actor is MAYOR, via a yet-to-be-built admission gate. No tool in the current stack performs M4.

### M5 — Derived artifact write

Writes to `reports/`, `docs/`, generated DOT files, generated markdown reports. These are **not state** in the governance sense — they are projections of state. They have no governance receipt, and their existence does not satisfy receipt law for any M1–M4 operation.

### M6 — Filesystem scaffolding

`mkdir`, deletion of empty directories, `.gitignore` edits, parent-dir creation. Not state in the governance sense. No receipt required, but operator confirmation required when destructive (see executing-actions-with-care).

### M7 — External effect via CLAW

`telegram_send`, `web_fetch`, `notify`. Not local-state mutation but external-world mutation. Two-receipt rule plus capability grant required. `authority = False` always; `require_approval = True` always.

A proposed mutation that **does not map to exactly one class** is **denied by default**.

---

## §4. Required receipt fields

Every M1, M2, M3, M4, M7 receipt must contain the following fields with the following semantics. Missing or null required fields = invalid receipt = mutation rejected (axiom §0).

### §4.1 Identity and chain

| Field              | Type    | Required for | Semantics                                                                  |
|--------------------|---------|--------------|----------------------------------------------------------------------------|
| `schema_name`      | string  | all          | E.g. `GEMMA_PROPOSAL_RAW_V1`. Pins the validator.                          |
| `schema_version`   | string  | all          | Semver. Reader refuses unknown majors.                                     |
| `receipt_hash`     | string  | M1           | SHA-256 of canonical body **excluding** `receipt_hash` and timestamps.     |
| `previous_hash`    | string  | M1           | The previous chain entry's `receipt_hash`, or genesis sentinel.            |
| `receipt_timestamp_utc` | string | all     | ISO-8601 UTC. **Not part of hashed body** (anti-T10).                      |

### §4.2 Governance

| Field                    | Type    | Required for | Semantics                                                       |
|--------------------------|---------|--------------|-----------------------------------------------------------------|
| `route_id`               | string  | M2, M7       | Names the producing path (e.g. `gemma4_her`, `ralph_w_adapter`).|
| `route_authority`        | string  | M2, M7       | `NON_SOVEREIGN` for everything not MAYOR-admitted.              |
| `authority`              | bool    | all          | **Structurally `False`** outside of MAYOR admission receipts.   |
| `lifecycle_entry`        | string  | M2           | `RAW` at creation. Mutable only via M4.                         |
| `auto_promotion_ceiling` | string  | M2           | Maximum lifecycle a M3 annotation alone can grant. `RAW` today. |

### §4.3 Proposal envelope (M2 only)

`proposal_text`, `uncertainty_text`, `required_receipts`, `hal_questions`, `envelope_complete`. Already standardized by `GEMMA_PROPOSAL_RAW_V1`. The envelope is the **substance** the M3 annotations attach to.

### §4.4 Lane annotations (M3 only)

```json
"operator_decision": { "status": ..., "reviewer": ..., "timestamp_utc": ..., "notes": ... }
"hal_verdict":       { "status": ..., "reviewer": ..., "timestamp_utc": ..., "notes": ... }
```

Each is a **complete record**, never a delta. Either field is `null` until written; after write, it is immutable except by an explicit, receipted M3-override (not yet built).

### §4.5 Trace (M1 only)

`trace = (S_t, P_t, V_t, T_t)` — invariant I11. Pre-state hash, proposal, verdict, tool-call list. Without trace, replay cannot verify.

---

## §5. Operator / HAL / MAYOR gates

Authority over mutations is partitioned. **No actor holds more than one gate.**

### §5.1 Governor (G layer, kernel)

Gates M1 and M7. The 5 fail-closed gates in `helensh/kernel.py:governor()`:

1. Unknown action → DENY
2. `authority == True` → DENY (structural, I8)
3. Required capability not granted → DENY
4. Write or CLAW action → PENDING (requires explicit grant)
5. Otherwise → ALLOW

### §5.2 Operator (human)

Gates M3 operator lane only. Writes `operator_decision` via `review_cockpit.py`. Operator **cannot** write `hal_verdict`. Operator **cannot** mutate `lifecycle_entry`. Operator **cannot** promote.

### §5.3 HAL (reviewer agent or human-acting-as-HAL)

Gates M3 HAL lane only. Writes `hal_verdict` via `review_cockpit.py` H-key path or `hal_reviewer.py`. HAL **cannot** write `operator_decision`. HAL **cannot** mutate `lifecycle_entry`. HAL **cannot** ship.

### §5.4 MAYOR (admission authority, NOT YET IMPLEMENTED)

Sole gate for M4. The only actor that can mutate `lifecycle_entry` or `auto_promotion_ceiling`. Requires:

- A passing HAL verdict (`hal_verdict.status == "PASS"`),
- An approving operator decision (`operator_decision.status == "APPROVED_FOR_SANDBOX_ONLY"` or stronger),
- A MAYOR receipt explicitly naming the source receipt's hash.

Until MAYOR exists, **no mutation of `lifecycle_entry` is legal**, regardless of who attempts it. The cockpit, the analyzer, the queue, the graph viewer, the adapter, and `reseed_topics.py` all comply by construction.

### §5.5 Reseed (no gate, advisory only)

`reseed_topics.py` performs **zero** mutations. It is a read-side projection of accumulated M3 evidence into topic candidates. Its output is text or JSON for operator consumption. It cannot, by design, enter any of the gates above.

---

## §6. Forbidden mutations

The following are denied by doctrine. A tool that performs any of these is in violation regardless of intent or outcome:

1. **Writing to `helensh/.state/live_ledger.jsonl` outside `LedgerWriter`.**
2. **Writing to a M2 receipt file without first reading it** (tamper risk — operator may have annotated in another window).
3. **Mutating `lifecycle_entry` or `auto_promotion_ceiling` from any tool that is not MAYOR.**
4. **Mutating `operator_decision` from any path that is not the operator lane.**
5. **Mutating `hal_verdict` from any path that is not the HAL lane.**
6. **Writing a receipt with `authority = True`.** Authority is structurally false outside of MAYOR admission, which does not yet exist.
7. **Mutating a source NDJSON (e.g. `helensh/.state/goblin_ar/results.ndjson`) under any condition.** Sources are append-only by their producer; projection layers are read-only.
8. **Embedding `receipt_timestamp_utc` or any wall-clock value inside the hashed body.** Hashes must remain reproducible (anti-T10, I5).
9. **Re-using a receipt filename for a different logical receipt.** Filenames are deterministic; collision = bug, not overwrite.
10. **Coalescing two mutations into one write** (e.g., write both lanes in one save). Each lane gets its own write; partial-write recovery requires it.
11. **Reporting success when the receipt write failed.** Receipt law: if the write didn't happen, the action didn't happen — return failure, do not retry silently.
12. **Bypassing canonical serialization.** `json.dumps(sort_keys=True, separators=(",",":"))` is the only legal canonicalization for hashed bodies. `indent=2` and `ensure_ascii=False` are legal for human-readable receipt files because they are **outside** the hashed body (anti-T8).

---

## §7. Replay requirements

A mutation is *trusted* only if it can be replayed and produce the same observable state.

### §7.1 Ledger replay (M1)

`helensh/replay.py:verify_chain()` MUST pass on the full ledger from genesis to head. `hydrate_session()` MUST reproduce the current runtime state byte-for-byte. Any divergence = T6 detected = ledger quarantined, not patched.

### §7.2 GNF replay (M1)

For each M1 execution receipt, the embedded trace `(S_t, P_t, V_t, T_t)` MUST suffice to re-derive `S_{t+1}` deterministically. Invariant I11.

### §7.3 Receipt round-trip (M2)

Reading a M2 receipt, re-serializing it with the same canonical encoding, and writing it back MUST produce a byte-identical file (modulo deliberate annotation writes). Encoding drift (e.g., utf-8 → cp1252) is a T8 violation.

### §7.4 Projection idempotence (adapter writes to M2)

Re-running a projection adapter on the same source NDJSON MUST produce the same set of output filenames with byte-identical content. The current `ralph_to_gemma_adapter.py` satisfies this via deterministic filename derivation and stable field projection.

### §7.5 Annotation order independence (M3)

Operator and HAL annotations on the same M2 receipt are **commutative**: writing operator first then HAL, or HAL first then operator, MUST produce byte-identical final files. The cockpit's lane-isolation guarantees this. Any tool that violates commutativity is a T3 violation.

### §7.6 Reseed determinism (no mutation, but replayable)

`reseed_topics.py` on the same corpus MUST produce the same ranked candidate list and the same JSON bytes. Otherwise the reseed signal is non-deterministic and cannot be cited as evidence.

---

## §8. Minimal implementation contract

A tool is *receipt-safe-mutation-compliant* if and only if it satisfies all of the following. Failure on any single check = non-compliant.

### §8.1 Declared mutation class

The tool's docstring states which of M1–M7 it performs, or explicitly states "READ ONLY across all sources" if none.

### §8.2 Hard-constraint block in docstring

The tool's docstring contains a `Hard constraints:` section enumerating the §6 forbidden mutations it explicitly does not perform. Format:

```
Hard constraints:
  - NEVER <forbidden action 1>
  - NEVER <forbidden action 2>
  ...
```

### §8.3 Lane isolation (M3 tools)

If the tool writes M3, it has **two separate write functions** — one for `operator_decision`, one for `hal_verdict` — and neither references the other field. Cross-references in tests are required.

### §8.4 Canonical serialization (M1 tools)

If the tool writes M1, it uses `json.dumps(sort_keys=True, separators=(",", ":"))` for any value that is hashed, and computes the hash over bytes, not over a re-parsed structure.

### §8.5 UTF-8 explicit (all writes)

Every `Path.write_text` call passes `encoding="utf-8"` explicitly. Default platform encoding is forbidden (Windows cp1252 has bitten this codebase — anti-T8).

### §8.6 Read-tolerant decode (all reads)

Every read of a M2 receipt or any pre-existing JSON file uses a tolerant decoder (utf-8 then cp1252 fallback) and never silently substitutes replacement characters into a value that will be re-hashed.

### §8.7 Failure surfaces

If a write fails, the tool returns a non-zero exit code or raises. It does not log success. It does not retry silently. Receipt law applies: no write = no mutation = no claim of success.

### §8.8 No timestamps in hashed bodies

Timestamps appear in `receipt_timestamp_utc` (M1, M2, M3) but never inside the substructure used to compute `receipt_hash`. The current ledger writer satisfies this; new tools must too.

### §8.9 Determinism flag in tests

Every tool with a mutation path has a determinism test: same input → same output bytes. For projection tools (e.g. the RALPH adapter), this means running the projection twice produces zero diffs.

### §8.10 Gate citation

A tool that writes M2, M3, or attempts M4 cites the §5 gate it claims authority under, in its docstring. A tool that cannot cite a gate cannot mutate.

---

## §9. Halt boundary

GOBLIN halts here. This doctrine is RAW. The receipt that proves I read the corpus correctly (RALPH ep 8/9/10 + GEMMA UTF-8 BLOCKED) and synthesized them into this protocol is the existence of this file and its `origin_signal` frontmatter line.

Resume conditions (HER, then HAL, then operator):

1. **HER attestation**: HER reviews §1–§8 against `helensh/SEED_V3.txt`, `helensh/kernel.py`, `helensh/replay.py`, and confirms or annotates each forbidden mutation in §6 against the actual kernel implementation. Disagreements become §6 amendments or §1 problem-statement refinements.

2. **HAL review (recorded)**: HAL is given this doctrine as a M2 proposal envelope. HAL's `hal_verdict` is one of `PASS` / `FAIL` / `NEEDS_MORE_RECEIPTS`. If `NEEDS_MORE_RECEIPTS`, the missing items become the §4 / §6 amendments and produce a `V1` draft.

3. **Operator decision (recorded)**: operator records `APPROVED_FOR_SANDBOX_ONLY` (this doctrine governs only quarantine + the reseed loop), `REJECTED` (rationale enters the next draft), or `PENDING_REVIEW`.

4. **MAYOR admission (deferred)**: this doctrine cannot itself be admitted to canon until MAYOR exists. Until then, it lives at `lifecycle_entry = "RAW"`, `auto_promotion_ceiling = "RAW"`, and is *referenced* by tools but not *ratified* by the system.

5. **Implementation backfill**: only after operator approval, the §8 contract is back-applied as docstring blocks in `tools/review_cockpit.py`, `tools/review_queue.py`, `tools/hal_receipt_analyzer.py`, `tools/receipt_graph.py`, `tools/ralph_to_gemma_adapter.py`, `tools/reseed_topics.py`, and any future tool. No code change. Documentation only. The discipline is asserted, then verified by inspection.

GOBLIN does not advance past this halt. Nothing in this document instructs a sovereign actor. Nothing in this document mutates state. The only action this document performs is **the act of being written**, which is itself a §M2-shaped artifact masquerading as documentation — and that is fine, because the protocol explicitly classifies `docs/proposals/*.md` as M5 (derived artifact), not state.
