# SOVEREIGN_PROMOTION_PROTOCOL_V1

status: PROPOSAL
authority: NONE
sovereign_touch: false
prerequisite: SKILL_ADMISSION_PROTOCOL_V1.md (skill-local admission must be confirmed first)

---

## Purpose

Defines the lawful path by which a skill-local admitted skill becomes
sovereignly active — meaning its `SKILL_PROMOTION_DECISION_V1` is appended
to `town/ledger_v1.ndjson` and confirmed by sovereign replay.

Skill-local admission (ADMISSION_LEDGER_V1.json + replay) is a prerequisite,
not a substitute.

---

## Core Formula

```
skill_local_admission ≠ sovereign_admission
routing ACK           ≠ sovereign write
MAYOR heard it        ≠ MAYOR wrote it
sovereign write       = ndjson_writer.py + kernel_guard.sh verify + sovereign replay
```

---

## Authorized Writer

One writer only: `tools/ndjson_writer.py`, called by the kernel daemon
(`oracle_town/kernel/kernel_daemon.py`) on behalf of MAYOR.

Claude Code **must not** call `ndjson_writer.py` directly.
Claude Code **must not** append to `town/ledger_v1.ndjson` directly.
`tools/kernel_guard.sh` verifies this at CI time.

---

## Required Pipeline

### 1. Skill-Local Admission Confirmed
All 7 gates of `SKILL_ADMISSION_PROTOCOL_V1.md` must pass:
- `SKILL_ADMISSION_CHECKER_V1` returns `OPERATIONALLY_WITNESSED`
- `ADMISSION_LEDGER_V1.json` exists
- `ADMISSION_STATE_V1.json` exists with `status: ACTIVE`
- `WITNESS_REPORT_*.json` exists

### 2. Sovereign Promotion Packet

A `SKILL_PROMOTION_PACKET_V1` is assembled containing:

```json
{
  "skill_id":                    "<SKILL_ID>",
  "candidate_version":           "V1",
  "candidate_identity_hash":     "sha256:<64 hex>",
  "skill_local_admission_commit": "<git sha>",
  "checker_verdict":             "OPERATIONALLY_WITNESSED",
  "operator_countersign":        "<JM_TASSY seal>",
  "requested_action":            "SOVEREIGN_PROMOTE"
}
```

### 3. Route to MAYOR via Admissible Bridge

```bash
python3 tools/helen_say.py "<packet_json>" --op promote_skill
```

Note: `--op promote_skill` does not yet exist in `helen_say.py`.
This protocol defines the required interface. Implementation is gated on
MAYOR routing the protocol itself through the activation process.

### 4. MAYOR Validation

MAYOR must verify:
- `SKILL_PROMOTION_PACKET_V1` is schema-conformant
- `candidate_identity_hash` matches current `skill.py` SHA
- `skill_local_admission_commit` exists in git history
- `checker_verdict` is `OPERATIONALLY_WITNESSED` (not claimed — verified live)
- `operator_countersign` is present

MAYOR **may not** approve based on text claims alone. Each field is
independently verifiable from the SOT.

### 5. Sovereign Ledger Append

On MAYOR approval, `ndjson_writer.py` appends a `SKILL_PROMOTION_DECISION_V1`
entry to `town/ledger_v1.ndjson` with:

```json
{
  "type":                      "SKILL_PROMOTION_DECISION_V1",
  "skill_id":                  "<SKILL_ID>",
  "decision_type":             "ADMITTED",
  "reason_code":               "OK_ADMITTED",
  "candidate_identity_hash":   "sha256:<64 hex>",
  "sovereign_promotion":       true
}
```

### 6. Sovereign Replay Verification

`replay_ledger_to_state(town/ledger_v1.ndjson, initial_state)` must produce:

```json
{
  "active_skills": {
    "<SKILL_ID>": { "status": "ACTIVE", "sovereign": true }
  }
}
```

Until this replay passes, the skill is `skill_local_admission: CONFIRMED` only.
It is not sovereignly active.

### 7. Sovereign Witness

The skill is run once against live sovereign artifacts after promotion.
Output committed as `SOVEREIGN_WITNESS_REPORT_V1`.

---

## What Does NOT Create Sovereign Admission

- `skill_local_admission: CONFIRMED` in SKILL.md
- `ADMISSION_LEDGER_V1.json` and `ADMISSION_STATE_V1.json`
- Routing receipts from `helen_say.py` with `mutations: []`
- `GATE_FETCH_PASS` or `KERNEL_ACCEPT`
- Operator text saying "promote"
- Claude Code writing to any path

---

## What Claude Code May Do

- Run `SKILL_ADMISSION_CHECKER_V1` to verify 7 gates
- Assemble the `SKILL_PROMOTION_PACKET_V1` as a non-sovereign artifact
- Route the packet via `helen_say.py --op promote_skill` (once op exists)
- Verify sovereign replay state after MAYOR writes it
- Commit sovereign witness report

Claude Code may **not**:
- Call `ndjson_writer.py` directly
- Write to `town/ledger_v1.ndjson`
- Claim sovereign admission from routing receipts

---

## Gap vs Current State

| Step | Status |
|---|---|
| `--op promote_skill` in `helen_say.py` | IMPLEMENTED — commit `73dceaf` |
| MAYOR handler for `promote_skill` op | SPEC WRITTEN — `oracle_town/protocols/MAYOR_HANDLER_PROMOTE_SKILL_SPEC_V1.md` |
| Sovereign replay includes `sovereign: true` field | IMPLEMENTED + TESTED — commit `73dceaf` |
| `SKILL_PROMOTION_PACKET_V1` schema | DEFINED — commit `73dceaf` |

Gap 1 and 3–4 are implemented. Gap 2 has a precise spec but requires a human operator
or HELEN-side authorized process to apply (sovereign firewall: `oracle_town/kernel/` is
off-limits to Claude Code writes).

---

## Doctrine

Skill-local admission proves the skill works and passes governance review.
Sovereign admission proves HELEN's kernel accepted the promotion.
The gap between them is constitutional, not bureaucratic.
