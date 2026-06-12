---
name: skill_admission_checker
skill_id: SKILL_ADMISSION_CHECKER_V1
description: Given a skill_id, determines institutional admission status across 7 levels from MISSING to OPERATIONALLY_WITNESSED. Prevents claim laundering by refusing to return ACTIVE unless replay state explicitly confirms it.
authority: NONE
world_effect: NONE
sovereign_touch: false
domain_category: governance_observability
provider_class: INTERNAL
protocol_ref: oracle_town/protocols/SKILL_ADMISSION_PROTOCOL_V1.md
institutional_admission: PENDING_LAWFUL_APPEND
---

# SKILL_ADMISSION_CHECKER_V1

Anti-claim-laundering checker. Enforces the doctrine from `SKILL_ADMISSION_PROTOCOL_V1.md`:

> conversation ≠ constitution
> artifact ≠ admission
> ADMIT text ≠ ACTIVE state
> ledger event + replay = governed reality

## Admission Levels (ordered)

| Level | Condition |
|---|---|
| `MISSING` | No `skill.py` found |
| `IMPLEMENTED_ONLY` | `skill.py` exists, no tests |
| `TESTED_ONLY` | Tests exist, no reducer artifact |
| `ADMIT_ARTIFACT_ONLY` | Reducer ADMIT artifact exists, no decision ledger |
| `LEDGER_APPENDED` | Ledger exists, replay missing or not ACTIVE |
| `REPLAY_ACTIVE` | Replay state says ACTIVE, no witness |
| `OPERATIONALLY_WITNESSED` | Replay ACTIVE + witness report exists |

`is_active` is True only for `REPLAY_ACTIVE` and `OPERATIONALLY_WITNESSED`.

## Fail-Closed Invariants

- Malformed replay state → `LEDGER_APPENDED` (never ACTIVE)
- Replay status ≠ `"ACTIVE"` (e.g. `QUARANTINED`) → `LEDGER_APPENDED`
- Routing receipts, `mutations: []`, countersigns, test results → do not advance level

## Usage

```python
from oracle_town.skills.skill_admission_checker import SkillAdmissionChecker

checker = SkillAdmissionChecker(sot_root="/path/to/helen_os_v1")
report  = checker.check("REFERENCE_DRIFT_WITNESS_V1")
print(report.status)    # OPERATIONALLY_WITNESSED
print(report.is_active) # True
```

## CLI

```bash
PYTHONPATH=. .venv/bin/python oracle_town/skills/skill_admission_checker/cli.py REFERENCE_DRIFT_WITNESS_V1
```

## Tests

```bash
.venv/bin/pytest oracle_town/skills/skill_admission_checker/tests/ -v
```

13 tests covering all 7 levels, malformed-replay fail-closed, and
`REFERENCE_DRIFT_WITNESS_V1` as the live known-positive case.
