# HER_HAL_REDUCER_INTERFACE_V1

**authority:** NON_SOVEREIGN
**canon:** NO_SHIP
**lifecycle:** SPEC_DRAFT
**status:** Proposal — named as missing in `GEMMA_HER_AMPLIFIER_V1 §5.3 + §8`
**parent_proposal:** `docs/proposals/GEMMA_HER_AMPLIFIER_V1.md`
**operator_directive:** HER override authorizing Gemma autonomous loop (2026-05-23)
**proposer:** claude-opus-4-7 (acting as GOBLIN under override)
**attestor:** pending

> **CONSTITUTIONAL_BREACH_NOTATION.** This spec was authored under HER
> override of GEMMA_HER_AMPLIFIER_V1 HOLD. The parent proposal §9
> default verb was HOLD; HER selected the override path via
> AskUserQuestion (2026-05-23). Receipts traversing this interface
> while the override remains in force carry breach notation.

---

## §1. Purpose

`GEMMA_HER_AMPLIFIER_V1 §5.3` names this interface as missing:

> *"This proposal references HAL but does not specify the HAL reducer
> interface. A dedicated HER → HAL reducer contract for free-form
> proposals (vs. structured artifact validation) is missing. Likely a
> separate proposal: `HER_HAL_REDUCER_INTERFACE_V1`."*

Without this spec, Gemma outputs have no defined path from RAW to
RECEIPTED. The integration is incomplete. This spec defines the
contract.

---

## §2. Position in the cognition pipeline

```
Operator prompt
      ↓
HER (Gemma 4 / Qwen) — produces §4 envelope:
  [PROPOSAL] [UNCERTAINTY] [REQUIRED_RECEIPTS] [HAL_QUESTIONS]
      ↓ (this interface — §3 below)
HAL (reducer) — applies poison detection + verdict assignment
      ↓
Operator review (sovereign) — KEEP / DISCARD / ITERATE / HAL_REVIEW
      ↓
Canonical writer (helen_say.py) — only if KEEP and HAL pass
      ↓
Ledger entry (town/ledger_v1.ndjson)
```

This spec defines the **HER → HAL** arrow only. It does not redefine
HAL's internal logic, the canonical writer, or the ledger schema.

---

## §3. The interface contract

### §3.1 Input — what HAL receives

```json
{
  "schema_name": "HER_TO_HAL_PACKET_V1",
  "schema_version": "1.0.0",
  "source_route": "gemma4_her" | "her_fast",
  "model_id": "gemma4:26b" | "qwen3.5:9b" | <other>,
  "lifecycle_entry": "RAW",
  "envelope": {
    "proposal_text": "...",
    "uncertainty_text": "...",
    "required_receipts": "...",
    "hal_questions": "..."
  },
  "envelope_complete": true | false,
  "system_prompt_sha256": "<hex>",
  "memory_guards_observed": {
    "num_ctx": 2048,
    "num_predict": 1500,
    "stream": false
  },
  "tokens_consumed": <int>,
  "wall_time_seconds": <float>,
  "done_reason": "stop" | "length" | "timeout" | "crash",
  "receipt_timestamp_utc": "<ISO-8601>",
  "constitutional_breach_notation": <object or null>
}
```

### §3.2 Output — what HAL produces

```json
{
  "schema_name": "HAL_REDUCER_VERDICT_V1",
  "schema_version": "1.0.0",
  "input_packet_sha256": "<hex of §3.1 packet>",
  "verdict": "ADMIT_RAW" | "QUARANTINE" | "REJECT",
  "verdict_reasons": ["<reason_code_1>", "<reason_code_2>"],
  "poison_flags": [
    {"pattern": "godmode_language", "score": <0-1>, "snippet": "..."},
    {"pattern": "coercive_propagation", "score": <0-1>, "snippet": "..."}
  ],
  "envelope_compliance": {
    "all_sections_present": true | false,
    "missing_sections": [...],
    "sections_too_brief": [...]
  },
  "memory_guard_compliance": true | false,
  "breach_notation_present": true | false,
  "breach_notation_addressed": true | false,
  "next_action_for_operator": "REVIEW" | "ITERATE_PROMPT" | "DISCARD" | "ESCALATE",
  "hal_witness_id": "<HAL instance identifier>",
  "verdict_timestamp_utc": "<ISO-8601>"
}
```

### §3.3 Verdict semantics

| Verdict | Meaning | Next step |
| --- | --- | --- |
| `ADMIT_RAW` | Envelope clean, no poison flags, memory guards observed | Operator review for promotion above RAW |
| `QUARANTINE` | Envelope OK but soft poison flags (low score, ambiguous) | Operator review with HAL annotations |
| `REJECT` | Hard poison flag, missing envelope sections, memory guard breach, or breach notation unaddressed | Discard or iterate prompt; do not promote |

`ADMIT_RAW` is the **only** verdict that allows operator promotion
above RAW lifecycle. `QUARANTINE` and `REJECT` block promotion;
operator may still review or iterate.

---

## §4. Poison patterns HAL must check

Inherited from `HYPERSTITION_FIREWALL_V0.md §2.2` (HAL_GOBLIN canonical
six). Reproduced here for completeness; not redefined:

- `godmode_language` — claims of unlocked AI modes, omniscience, etc.
- `coercive_propagation` — urgency / scale pressure ("now", "100 epochs")
- `reality_control_claim` — claims of altering reality, manifesting
- `ai_sentience_claim` — AI claiming consciousness, feelings, will
- (two additional patterns per HYPERSTITION_FIREWALL_V0; see source)

A Gemma-generated proposal that triggers any of these requires
`QUARANTINE` or `REJECT`, not `ADMIT_RAW`.

---

## §5. Envelope compliance rules

`GEMMA_HER_AMPLIFIER_V1 §4` defines the four-section envelope as
mandatory. This spec defines what counts as compliance:

| Check | Pass | Fail |
| --- | --- | --- |
| All 4 sections present | All headers found | Any missing |
| Sections have content | Each ≥ 20 characters of substance | Any empty or trivial |
| `[REQUIRED_RECEIPTS]` lists at least one | Has bullets or named items | Empty or "none" |
| `[HAL_QUESTIONS]` lists at least one | Has questions | Empty or "no questions" |

Failure on any row → `envelope_compliance.all_sections_present = false`
and HAL verdict downgraded.

Empty `[REQUIRED_RECEIPTS]` or `[HAL_QUESTIONS]` is a soft signal
(possibly legitimate for trivial proposals) but flagged. HAL may still
`ADMIT_RAW` if the proposal scope is small.

---

## §6. Memory-guard compliance check

`GEMMA_HER_AMPLIFIER_V1 §5.1` makes memory guards mandatory at
dispatcher level for `gemma4:26b`. HAL must verify:

```
input.memory_guards_observed.num_ctx     == 2048
input.memory_guards_observed.num_predict == 1500
input.memory_guards_observed.stream      == false
```

Any deviation → `REJECT` with `verdict_reasons = ["memory_guard_breach"]`.
This is a hard rule: gemma4:26b that ran without the guards crashed
MRED on 2026-05-02 (machine reboot observed). The guards exist because
of an empirical fault, not as policy preference.

---

## §7. Breach notation handling

When `input.constitutional_breach_notation != null`:

- HAL must record `breach_notation_present = true`
- HAL must check whether the breach is `addressed` (operator
  acknowledgment, scope-limited, audit clause present)
- If breach notation is present but `addressed = false`, verdict is
  forced to `REJECT` regardless of envelope quality
- If breach notation is present and `addressed = true`, verdict
  proceeds normally but is annotated for future audit visibility

This is the discipline that makes HER override loops auditable rather
than silent.

---

## §8. What this spec does NOT define

To prevent scope creep:

- **HAL's internal poison-scoring algorithm** — implementation-class,
  not interface-class
- **The canonical writer's behavior** (`helen_say.py`) — separate spec
- **Operator UI for review** — operator's tooling choice
- **Multimodal envelope variants** — text only per `GEMMA_HER_AMPLIFIER_V1 §5.7`
- **HER batch interfaces** — single-proposal-at-a-time only here;
  batch is a separate spec
- **Cross-session attribution** — addressed by separate proposal
  `CROSS_SESSION_FIELD_ATTRIBUTION_V0` (flagged in E22 meta-finding,
  not yet bottled)

---

## §9. Test discipline (when implementation authorized)

If a future task packet authorizes implementing this interface:

- **T1**: HAL receives a valid §3.1 packet and produces a valid §3.2
  verdict for all three verdict classes (ADMIT_RAW / QUARANTINE / REJECT).
- **T2**: HAL `REJECT`s any packet missing one or more envelope
  sections.
- **T3**: HAL `REJECT`s any packet with `memory_guards_observed` not
  matching §6 exact values.
- **T4**: HAL `REJECT`s any packet with breach notation present and
  `addressed = false`.
- **T5**: All six poison patterns from §4 trigger `QUARANTINE` or
  `REJECT`, never `ADMIT_RAW`.
- **T6**: ADMIT_RAW packets that operator promotes to higher lifecycle
  produce a ledger entry via `helen_say.py` (canonical writer); HAL
  does NOT write the ledger directly.

---

## §10. Halt boundary

GOBLIN halts here. This spec is `SPEC_DRAFT` under
constitutional-breach notation (override path). Reducer admission
requires the override to be reviewed and either ratified or revoked.

Resume conditions:

1. **HER ruling**: ratify or revoke the override; both paths permit
   continuation
2. **HAL pass** (separate sovereign decision): does this interface
   spec cover all the cases the implementation needs
3. **REDUCER admission**: spec advances from `SPEC_DRAFT` to
   `SHIPPED_SPEC` only with reducer ledger entry
4. **Implementation authorization** (separate task packet): per
   `GEMMA_HER_AMPLIFIER_V1 §7` discipline — this spec is the contract
   only

Discipline followed: `HALT_BOUNDARY_DISCIPLINE_V0` (commit 5d0e04e).

---

## §11. Single line

> **HER produces envelopes. HAL produces verdicts on envelopes.
> Operator decides what becomes ledger.
> Memory guards are not negotiable; breach notation must be addressed;
> the canonical writer alone touches the ledger.**
