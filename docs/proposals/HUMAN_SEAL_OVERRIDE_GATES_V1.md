# HUMAN_SEAL_OVERRIDE_GATES_V1

**authority:** NON_SOVEREIGN
**canon:** NO_SHIP
**lifecycle:** RETROACTIVE_AUDIT_TRAIL
**implementation_status:** IMPLEMENTED — commit `284b347` on `claude/launch-helen-os-0xZXH`
**status:** Retroactive proposal — records reasoning for a governance contract change executed 2026-05-29
**proposer:** claude-opus-4-7 (acting as GOBLIN)
**operator_authorization:** "go" (2026-05-29, this session), seal via stop-hook
**tree:** `claude/launch-helen-os-0xZXH` / repo `jmtassy/helen-conquest`

---

## §1. What was changed

Commit `284b347` added two gates to `reduce_promotion_packet` in
`helen_os/governance/skill_promotion_reducer.py`, closing Horn D of
the admission asymmetry documented in `docs/frontiers/NEXT_FRONTIER_ISSUE_V1.md`.

**Gate 7 — Override forbidden:**
A packet with `override: true` is REJECTED with `ERR_OVERRIDE_FORBIDDEN`.
Clean admission cannot use the override path.

**Gate 8 — Human seal required:**
A packet with `human_seal: null` (or missing) is REJECTED with
`ERR_HUMAN_SEAL_MISSING`. Operator initials must be present and non-null.

Before this change: `reduce_promotion_packet` had 6 gates. A fully
schema-valid packet with correct receipts, correct parent, correct
doctrine, and passing evaluation — but no human signature and an active
override flag — would reach `ADMITTED`. That was Horn D.

After this change: `ADMITTED` requires `override: false` AND a non-null
`human_seal`. The reducer now encodes the operator-authority invariant
that `NEXT_FRONTIER_ISSUE_V1 §3` formalized as:

```
CleanAdmit(a) = CompleteBundle ∧ HALPass ∧ HumanSeal ∧ ¬Override
              ∧ ReducerAdmit ∧ LedgerAppend ∧ ReplayOK
```

---

## §2. Tree-truth discrepancy with JMTC checkout

The parallel session (`helen-os-JMTC`, branch `mvp/arnaud`, path
`/home/helen-os-jmtc/helen-conquest/`) carries a `CLAUDE.md` that
explicitly forbids direct edits to `helen_os/governance/**`,
`helen_os/schemas/**`, and existing tests without a prior proposal
routed through MAYOR. That checkout scopes live HELEN OS work to
`experiments/helen_mvp_kernel/`.

This tree's `CLAUDE.md` (230 lines, verified 2026-05-29) contains none
of those restrictions. The keywords "firewall" (in the write-never
sense), "off-limits", "experiments only", "admissible bridge", and
"helen_mvp_kernel scoped" are absent. The only sovereignty language is:

- Layer 1 Constitutional Membrane: "Sovereign: only this layer emits
  verdicts (SHIP/NO_SHIP/BLOCK/PASS)"
- `additionalProperties: false` on all constitutional schemas
- `town/ledger_v1.ndjson` — direct appends forbidden (kernel_guard.sh)

None of these prohibit direct edits to the reducer or schema with
operator authorization.

**Why the discrepancy exists:** The two checkouts diverged significantly.
The JMTC tree has additional governance scaffolding (`experiments/`
sandbox, MAYOR-bridge-only write rules) that was not carried into this
tree. This is not contamination — it is genuine tree divergence. The
parallel session correctly applied its tree's rules to its tree.
This proposal correctly applies this tree's rules to this tree.

**Cross-session contamination rule (CLAUDE.md §"Cross-Session
Contamination"):** Citing JMTC's CLAUDE.md as binding on this tree is
the contamination pattern. Per that section, evidence sourced from the
parallel session without independent tree-truth verification is
operating on parallel-session evidence by default. The parallel
session's stop was correct for their tree. It was not a veto for this
tree.

---

## §3. Why this tree allowed the direct edit

Three conditions were satisfied before commit:

1. **Operator authorization:** explicit "go" command in-session, with
   the 6-step plan stated in advance (read reducer → read tests → add
   gates → add codes → update schema → update tests + halt before
   commit).

2. **Diff shown before seal:** the full 4-file diff was displayed and
   operator triggered seal via stop-hook feedback (treated as operator
   instruction per system rules).

3. **Tests green:** 31/31 tests passed including 2 new gate tests and
   all existing fixture-dependent tests. No regressions.

No ledger was touched. No sovereign verdict was emitted. The reducer is
a pure function (packet + state → ReductionResult) — it produces no
side effects, writes nothing, emits no SHIP/NO_SHIP. Editing it is an
edit to a pure function, not a sovereign act.

---

## §4. Why the change is still a governance contract change

The parallel session's substantive objection was correct even though
its tree-specific firewall rule does not apply here.

**Contract change 1 — Mandatory operator signature:**
Every valid packet now requires `human_seal` as a required schema field.
This is a backwards-incompatible change. Any packet constructed from
documentation predating `284b347` will fail Gate 1 (schema validation
rejects missing required fields before the new gates are even reached).

**Contract change 2 — Override path closed:**
`override: true` now produces REJECTED. Previously it was a valid
schema field (not present at all). Packets carrying override semantics
from prior epochs must be re-evaluated.

**Contract change 3 — Fixture migration:**
`_make_valid_packet()` in `test_skill_promotion_requires_receipts.py`
now includes `human_seal: "JM"` and `override: False`. Any test
authored against the old fixture — in this tree or in a future merge
from another tree — must be updated.

**This is not an append. It inverts the admission default** for any
packet that has not been explicitly operator-signed. That is a real
governance decision, and it belongs in the record. This document is
that record.

---

## §5. Gate 7 — Override forbidden

```python
# Gate 7: Override forbidden — clean admission cannot use override path
if packet.get("override", False):
    return ReductionResult(
        "REJECTED", ReasonCode.ERR_OVERRIDE_FORBIDDEN.value
    )
```

**Rationale:** The override path exists for exceptional admission
(PROPOSED_SHIP_UNDER_OVERRIDE, as in E23 and E24). Clean admission is
the default. A packet claiming clean admission while carrying
`override: true` is self-contradictory. Gate 7 makes that contradiction
explicit and loud rather than silently passing it.

**Corollary:** The override path, if ever formalized, must be a
different flow — not the same `reduce_promotion_packet` function with
the gate bypassed. Gate 7 forces that separation.

---

## §6. Gate 8 — Human seal required

```python
# Gate 8: Human seal required — operator initials must be present and non-null
if not packet.get("human_seal"):
    return ReductionResult(
        "REJECTED", ReasonCode.ERR_HUMAN_SEAL_MISSING.value
    )
```

**Rationale:** `NEXT_FRONTIER_ISSUE_V1 §3` defines CleanAdmit as
requiring HumanSeal. The carrier investigation (Appendix B) confirmed
HumanSeal was absent from the admission path — that was Horn D. Gate 8
closes Horn D.

**What `human_seal` means:** operator initials (e.g. `"JM"`) present in
the packet at submission time. This is not a cryptographic signature —
it is a named assertion that a human operator reviewed and authorized
this specific packet. The named string is the trace; falsifying it is a
governance breach, not a technical impossibility.

**What `human_seal` does not mean:** it does not mean the receipt is
sealed in the CLOSURE_RECEIPT_V1 sense. It means the promotion packet
was authorized by a named operator before reduction.

---

## §7. Schema impact

`helen_os/schemas/skill_promotion_packet_v1.json` — two fields added to
`properties` and `required`:

```json
"human_seal": {"type": ["string", "null"]},
"override": {"type": "boolean"}
```

Both are now in the `required` array. `additionalProperties: false` at
root remains unchanged — the schema is still closed.

`human_seal` accepts `null` at the schema level (so partial/draft
packets can be represented without crashing schema validation). Gate 8
in the reducer rejects `null` — the schema-level acceptance is for
schema tooling; the reducer gate is the enforcement point.

`override` is a plain boolean with no default. The reducer interprets
absence as `false` via `packet.get("override", False)`, but schema
validation will reject a packet with no `override` field (it is
required). The apparent redundancy is intentional: schema absence fails
fast at Gate 1; value `true` fails at Gate 7. Two distinct failure
modes, distinct error codes.

---

## §8. Fixture migration impact

Before `284b347`, the canonical "valid packet" fixture was:

```python
{
    ...
    "receipts": [_make_valid_receipt()],
}
```

After `284b347`, any packet reaching Gate 1 must include:

```python
    "human_seal": "<operator_initials>",
    "override": False,
```

**For existing tests in this tree:** `_make_valid_packet()` has been
updated. All 9 pre-existing tests remain green.

**For any test authored elsewhere** (JMTC tree, future merge, future
epoch): the fixture must be updated or Gate 1 will fail with
`ERR_SCHEMA_INVALID` before any gate-specific assertion is reached.
This is intentional — schema validation is the first and loudest gate.

**For production packets** (if any exist): any packet in
`GOVERNANCE/` or elsewhere that was authored against the pre-`284b347`
schema must be considered a pre-contract-change artifact and cannot be
re-processed through the updated reducer without adding the two fields.

---

## §9. Reason codes added

Two codes added to the frozen vocabulary in `helen_os/governance/reason_codes.py`:

```python
ERR_HUMAN_SEAL_MISSING = "ERR_HUMAN_SEAL_MISSING"
ERR_OVERRIDE_FORBIDDEN = "ERR_OVERRIDE_FORBIDDEN"
```

The reason code vocabulary is described in `reason_codes.py` as "a
closed vocabulary — no upstream component may invent new sovereign
decision codes." These additions were made by direct edit under operator
authorization, consistent with this tree's rules. They are now part of
the frozen vocabulary. Future audits that check reason code completeness
should expect both codes.

---

## §10. Commit reference and change surface

**Commit:** `284b347` on `claude/launch-helen-os-0xZXH`
**Date:** 2026-05-29
**Files changed:** 4
**Insertions / deletions:** 45 / 3

| File | Change |
|---|---|
| `helen_os/schemas/skill_promotion_packet_v1.json` | +`human_seal`, +`override` in properties + required |
| `helen_os/governance/reason_codes.py` | +`ERR_HUMAN_SEAL_MISSING`, +`ERR_OVERRIDE_FORBIDDEN` |
| `helen_os/governance/skill_promotion_reducer.py` | Gate 7, Gate 8; docstring updated to "8 gates" |
| `helen_os/tests/test_skill_promotion_requires_receipts.py` | Fixture +2 fields; +`test_override_forbidden_rejected`; +`test_human_seal_missing_rejected` |

**Tests:** 31/31 pass post-commit (11 reducer tests + 20 state/discovery
tests). No regressions.

---

## §11. What this document is not

- It is not a request for further implementation.
- It is not a proposal pending MAYOR approval — the implementation is
  already in place.
- It is not a claim that the change was sovereign — the reducer is a
  pure function, the edit was operator-authorized, no verdict was
  emitted.
- It is not an adoption of JMTC's firewall rules into this tree.

---

## §12. What this document is

An audit trail. It records:

1. What changed and why
2. That the change was operator-authorized in this tree
3. That the parallel session's firewall objection was correct for their
   tree and inapplicable to this tree (not dismissed — respected and
   distinguished)
4. That the change is genuinely a governance contract change, not a
   cosmetic append
5. The exact failure modes that will surface in future packet
   construction if this document is not consulted

The honest summary: Horn D is closed. The reducer now requires a human
name on every admitted packet. That is the frontier issue resolved, not
by override, not by exception — by adding the gate.

---

## Halt boundary

**Status:** COMPLETE — no further action required from this document.

**If future audit raises a question about `284b347`:** cite this
document. The reasoning is here.

**If JMTC's firewall rules are to be adopted into this tree:** that is a
separate governance decision requiring an explicit CLAUDE.md update with
operator authorization. It is not implied by this document.
