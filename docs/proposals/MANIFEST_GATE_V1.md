# MANIFEST_GATE_V1

**Status:** PENDING_MAYOR_REVIEW  
**Classification:** GOVERNANCE_PATCH · SOVEREIGN_PATH  
**Authority:** NONE (Claude Code non-sovereign proposal)  
**Proposed by:** Claude Code session 374c3d5  
**Validator:** peer_review required (Proposer ≠ Validator, Rule 3)

---

## What this is

Gate 7 in the skill promotion reducer — manifest registry enforcement.

The `SKILL_PROMOTION_PACKET_V1` schema already carries `capability_manifest_sha256`.
The reducer enforces 6 gates but has no Gate 7 to validate this field against an
active manifest registry. This proposal closes that gap.

---

## Failing tests (red until this patch is applied)

```
helen_os/tests/test_skill_promotion_manifest_gate.py
  FAIL  test_manifest_sha_not_in_registry_rejected
  FAIL  test_skill_not_in_manifest_allowed_skills_rejected
  FAIL  test_empty_allowed_skills_rejects_any_skill
```

Run with:
```bash
.venv/bin/pytest helen_os/tests/test_skill_promotion_manifest_gate.py -v
```

---

## Exact diff: `helen_os/governance/reason_codes.py`

In the "Governance / promotion failures" section, after `ERR_ROLLBACK_TRIGGER`:

```python
    # Manifest / capability registry failures
    ERR_MANIFEST_NOT_FOUND = "ERR_MANIFEST_NOT_FOUND"
    ERR_MANIFEST_SKILL_UNAUTHORIZED = "ERR_MANIFEST_SKILL_UNAUTHORIZED"
```

---

## Exact diff: `helen_os/governance/skill_promotion_reducer.py`

In `reduce_promotion_packet`, docstring update and new gate after Gate 6 (before
the bonus transfer gate):

**Docstring:**
```python
    """
    Pure reduction function: packet + state → decision.

    Enforces exactly 7 gates in order:
    1. Schema validity
    2. Receipt presence
    3. Receipt integrity
    4. Parent capability
    5. Doctrine match
    6. Evaluation pass threshold
    7. Manifest registry (if manifests present in active_state)
    """
```

**Gate 7 body** (insert after Gate 6 evaluation check, before bonus transfer gate):

```python
    # Gate 7: Manifest registry
    manifests = active_state.get("manifests")
    if manifests is not None:
        manifest_sha = packet.get("capability_manifest_sha256", "")
        if manifest_sha not in manifests:
            return ReductionResult(
                "REJECTED", ReasonCode.ERR_MANIFEST_NOT_FOUND.value
            )
        allowed = manifests[manifest_sha].get("allowed_skills", [])
        if packet["skill_id"] not in allowed:
            return ReductionResult(
                "REJECTED", ReasonCode.ERR_MANIFEST_SKILL_UNAUTHORIZED.value
            )
```

---

## Semantics

- **Backward compatibility:** Gate 7 only fires when `active_state` contains a
  `manifests` key. Absence of the key = no enforcement. Existing states without
  `manifests` continue to pass unmodified.
- **Registry structure:** `active_state["manifests"]` is a dict mapping
  `capability_manifest_sha256` → `{"allowed_skills": [...]}`.
- **Fail closed on unknown SHA:** a SHA not in the registry is always REJECTED
  (`ERR_MANIFEST_NOT_FOUND`).
- **Fail closed on unauthorized skill:** correct SHA but `skill_id` absent from
  `allowed_skills` → REJECTED (`ERR_MANIFEST_SKILL_UNAUTHORIZED`).
- **Gate ordering:** manifest gate runs after evaluation (Gate 6) — evaluation
  failures surface first.

---

## Test coverage after patch

All 6 tests in `test_skill_promotion_manifest_gate.py` must pass green:

| Test | Expected after patch |
|---|---|
| `test_no_manifest_registry_passes` | ADMITTED (already green) |
| `test_manifest_sha_not_in_registry_rejected` | REJECTED ERR_MANIFEST_NOT_FOUND |
| `test_skill_not_in_manifest_allowed_skills_rejected` | REJECTED ERR_MANIFEST_SKILL_UNAUTHORIZED |
| `test_manifest_valid_and_skill_allowed_admitted` | ADMITTED (already green) |
| `test_empty_allowed_skills_rejects_any_skill` | REJECTED ERR_MANIFEST_SKILL_UNAUTHORIZED |
| `test_gate_ordering_evaluation_fails_before_manifest_checked` | REJECTED ERR_THRESHOLD_NOT_MET (already green) |

---

## Sovereign path confirmation

Files requiring MAYOR-authorized edit:

| File | Path class |
|---|---|
| `helen_os/governance/reason_codes.py` | SOVEREIGN (governance/) |
| `helen_os/governance/skill_promotion_reducer.py` | SOVEREIGN (governance/) |

Files written by Claude Code (non-sovereign):

| File | Path class |
|---|---|
| `helen_os/tests/test_skill_promotion_manifest_gate.py` | NON-SOVEREIGN |
| `docs/proposals/MANIFEST_GATE_V1.md` | NON-SOVEREIGN |

---

## Admissible bridge

Route via:
```bash
.venv/bin/python tools/helen_say.py "MANIFEST_GATE_V1 proposal: add Gate 7 to skill_promotion_reducer + ERR_MANIFEST_NOT_FOUND + ERR_MANIFEST_SKILL_UNAUTHORIZED to reason_codes. Tests at helen_os/tests/test_skill_promotion_manifest_gate.py — 3 red until patch applied. Diff in docs/proposals/MANIFEST_GATE_V1.md." --op governance_patch
```
