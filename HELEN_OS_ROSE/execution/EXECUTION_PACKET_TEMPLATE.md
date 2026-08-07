# Execution packet template

Packets are JSON files in `execution/active/`, created with
`scripts/create_execution_packet.py` (never by hand-editing a copy of a
finished packet). A packet exists only downstream of a ledger `GO`.

Required fields (see `schemas/execution_packet.schema.json`):

```json
{
  "packet_id": "P-001",
  "approved_decision_id": "R-001",
  "outcome": "one sentence: what will be true when this packet is done",
  "scope": "what is inside",
  "non_goals": ["what is explicitly outside"],
  "owner": "who answers for it",
  "inputs": ["files, data, access needed"],
  "steps": ["ordered, bounded steps"],
  "artifacts": ["paths of things this packet produces"],
  "acceptance_tests": ["commands or checks that define done"],
  "stop_conditions": ["conditions that halt work and return to review"],
  "privacy_class": "one of the eight partitions",
  "status": "PLANNED | IN_PROGRESS | BLOCKED | DONE_UNVERIFIED | VERIFIED | ARCHIVED",
  "receipts": ["evidence entries added as work happens"],
  "state_history": []
}
```

Rules:

- `status` may reach `VERIFIED` only with passing acceptance tests recorded
  in `receipts`.
- Scope pressure (work wanting to grow) is a stop condition, not a reason
  to edit `scope`.
- Finished packets move to `execution/archive/` unchanged.
