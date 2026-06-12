# MAYOR_HANDLER_PROMOTE_SKILL_SPEC_V1

status: SPEC
authority: NONE
sovereign_touch: true — this spec describes changes to `oracle_town/kernel/kernel_daemon.py`,
                         a sovereign-firewall path. Only an authorized human operator
                         or HELEN-side process may apply these changes.
prerequisite: SOVEREIGN_PROMOTION_PROTOCOL_V1.md, SKILL_PROMOTION_PACKET_V1 schema

---

## What This Covers

Precise changes needed in `oracle_town/kernel/kernel_daemon.py` to route and validate
`--op promote_skill` packets and produce a sovereign ledger write via `NDJSONWriter`.

`oracle_town/kernel/mayor.py` requires **no changes**. `MayorReceiptEngine.ratify()` is
already a generic pure function. All new logic lives in `kernel_daemon.py`.

---

## Change 1 — Route `promote_skill` in `handle_request()`

**File:** `oracle_town/kernel/kernel_daemon.py`
**Location:** `handle_request()`, line 97 (before `else:` branch)

Current (lines 96-99):
```python
        elif operation == "dialog":
            response = self._handle_dialog(request)
        else:
            response = {"error": f"Unknown operation: {operation}"}
```

Replace with:
```python
        elif operation == "dialog":
            response = self._handle_dialog(request)
        elif operation == "promote_skill":
            response = self._handle_promote_skill(request)
        else:
            response = {"error": f"Unknown operation: {operation}"}
```

---

## Change 2 — New method `_handle_promote_skill()`

**File:** `oracle_town/kernel/kernel_daemon.py`
**Location:** Insert after `_handle_dialog()`, before end of class.

Required imports (add to top of file if not already present):
```python
import hashlib
import re
import sys
from pathlib import Path
```

The `NDJSONWriter` must be imported. Add alongside existing kernel imports:
```python
sys.path.insert(0, str(Path(__file__).parents[2]))  # repo root — add once if not present
from tools.ndjson_writer import NDJSONWriter
```

**Note:** `PYTHONPATH=$(CURDIR)` is already set by `Makefile`, but the daemon may run
standalone. The `sys.path.insert` guard is defensive; remove it if the daemon already
runs with the repo root on `sys.path`.

### Full method implementation

```python
def _handle_promote_skill(self, request):
    """
    Handle promote_skill operation — sovereign skill promotion via MAYOR.

    Input:
        {
            "operation":  "promote_skill",
            "packet":     "<JSON string: SKILL_PROMOTION_PACKET_V1>",
            "claim_id":   "RUN_YYYYMMDD:promote_skill:N",
            "proposer":   "helen",
            "intent":     "skill_sovereign_promotion",
            "timestamp":  "2026-...",
        }

    Output (REJECT):
        {
            "decision": "REJECT",
            "receipt_id": None,
            "gate": "GATE_PROMOTE_<REASON>",
            "reason": "...",
            "mutations": [],
        }

    Output (ACCEPT):
        {
            "decision": "ACCEPT",
            "receipt_id": "<uuid>",
            "gate": "GATE_PROMOTE_PASS",
            "mutations": [
                {
                    "type": "SKILL_PROMOTION_DECISION_V1",
                    "skill_id": "...",
                    "decision_id": "...",
                    "ledger_path": "town/ledger_v1.ndjson",
                }
            ],
        }

    Sovereign write: on ACCEPT, appends SKILL_PROMOTION_DECISION_V1 payload to
    town/ledger_v1.ndjson via NDJSONWriter.append_event(). This is the only
    authorized sovereign mutation path. Failure to write → REJECT (fail closed).
    """

    # ── 1. Parse packet JSON ──────────────────────────────────────────────
    raw_packet = request.get("packet", "")
    claim_id   = request.get("claim_id", "promote_skill:unknown")

    try:
        packet = json.loads(raw_packet) if isinstance(raw_packet, str) else raw_packet
    except Exception as exc:
        return {
            "decision": "REJECT", "receipt_id": None,
            "gate": "GATE_PROMOTE_PARSE_ERROR",
            "reason": f"packet is not valid JSON: {exc}", "mutations": [],
        }

    # ── 2. Required fields ────────────────────────────────────────────────
    REQUIRED = [
        "schema_name", "skill_id", "candidate_version",
        "candidate_identity_hash", "skill_local_admission_commit",
        "checker_verdict", "operator_countersign", "requested_action",
    ]
    missing = [f for f in REQUIRED if not packet.get(f)]
    if missing:
        return {
            "decision": "REJECT", "receipt_id": None,
            "gate": "GATE_PROMOTE_MISSING_FIELDS",
            "reason": f"missing required fields: {missing}", "mutations": [],
        }

    # ── 3. Schema name ────────────────────────────────────────────────────
    if packet["schema_name"] != "SKILL_PROMOTION_PACKET_V1":
        return {
            "decision": "REJECT", "receipt_id": None,
            "gate": "GATE_PROMOTE_WRONG_SCHEMA",
            "reason": "schema_name must be SKILL_PROMOTION_PACKET_V1", "mutations": [],
        }

    # ── 4. checker_verdict must be OPERATIONALLY_WITNESSED ───────────────
    # No weaker verdict is admitted. LEDGER_APPENDED or REPLAY_ACTIVE are
    # insufficient — the skill must have a live witness report.
    if packet["checker_verdict"] != "OPERATIONALLY_WITNESSED":
        return {
            "decision": "REJECT", "receipt_id": None,
            "gate": "GATE_PROMOTE_CHECKER_VERDICT_WEAK",
            "reason": (
                f"checker_verdict={packet['checker_verdict']!r} — "
                "must be OPERATIONALLY_WITNESSED; run SKILL_ADMISSION_CHECKER_V1 first"
            ),
            "mutations": [],
        }

    # ── 5. candidate_identity_hash format ─────────────────────────────────
    _HASH_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
    if not _HASH_RE.match(packet["candidate_identity_hash"]):
        return {
            "decision": "REJECT", "receipt_id": None,
            "gate": "GATE_PROMOTE_BAD_HASH",
            "reason": "candidate_identity_hash must match sha256:[64hex]",
            "mutations": [],
        }

    # ── 6. requested_action ───────────────────────────────────────────────
    if packet["requested_action"] != "SOVEREIGN_PROMOTE":
        return {
            "decision": "REJECT", "receipt_id": None,
            "gate": "GATE_PROMOTE_WRONG_ACTION",
            "reason": "requested_action must be SOVEREIGN_PROMOTE", "mutations": [],
        }

    # ── 7. Gate A — injection check on raw packet content ────────────────
    gate_decision = gate_a(raw_packet if isinstance(raw_packet, str) else json.dumps(raw_packet))

    # ── 8. Build Claim + Evidence ─────────────────────────────────────────
    canonical_packet = json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    content_hash = hashlib.sha256(canonical_packet.encode("utf-8")).hexdigest()

    claim = Claim(
        claim_id=claim_id,
        proposer=request.get("proposer", "unknown"),
        intent=request.get("intent", "skill_sovereign_promotion"),
        timestamp=request.get("timestamp", "2026-01-30T00:00:00Z"),
    )
    evidence = Evidence(
        content_snapshot=raw_packet if isinstance(raw_packet, str) else canonical_packet,
        content_hash=gate_decision.content_hash,
        gates_run={
            "gate_a": {
                "result": gate_decision.result.value,
                "code":   gate_decision.code,
                "reason": gate_decision.reason,
            },
            "promote_skill_schema":  {"result": "PASS", "code": "PROMOTE_SKILL_SCHEMA_OK"},
            "promote_skill_checker": {"result": "PASS", "code": "PROMOTE_SKILL_CHECKER_WITNESSED"},
            "promote_skill_fields":  {"result": "PASS", "code": "PROMOTE_SKILL_FIELDS_OK"},
        },
    )

    # ── 9. MAYOR ratification ─────────────────────────────────────────────
    receipt = self.mayor.ratify(claim, evidence)

    # Record claim + receipt in in-memory ledger (non-sovereign — audit trail)
    self.ledger.record("CLAIM", {
        "claim_id":  claim.claim_id,
        "type":      "promote_skill",
        "skill_id":  packet["skill_id"],
        "proposer":  claim.proposer,
        "intent":    claim.intent,
    })
    self.ledger.record("RECEIPT", {
        "receipt_id":      receipt.receipt_id,
        "decision":        receipt.decision,
        "policy_version":  receipt.policy_version,
    })

    if receipt.decision != "ACCEPT":
        return {
            "decision":   "REJECT",
            "receipt_id": receipt.receipt_id,
            "gate":       receipt.failed_gate or gate_decision.code,
            "reason":     receipt.reason,
            "mutations":  [],
        }

    # ── 10. Sovereign ledger write via NDJSONWriter ───────────────────────
    # This is the only path that writes to town/ledger_v1.ndjson.
    # kernel_guard.sh verifies at CI time that only authorized writers touch this file.
    decision_id = f"SOVEREIGN_{packet['skill_id']}_{claim_id}"
    decision_payload = {
        "schema_name":             "SKILL_PROMOTION_DECISION_V1",
        "schema_version":          "1.0.0",
        "decision_id":             decision_id,
        "skill_id":                packet["skill_id"],
        "candidate_version":       packet["candidate_version"],
        "decision_type":           "ADMITTED",
        "reason_code":             "OK_ADMITTED",
        "candidate_identity_hash": packet["candidate_identity_hash"],
        "sovereign_promotion":     True,
        "receipt_id":              receipt.receipt_id,
    }
    decision_meta = {
        "claim_id":                    claim_id,
        "skill_local_admission_commit": packet["skill_local_admission_commit"],
        "operator_countersign":        packet["operator_countersign"],
        "submitted_at":                packet.get("submitted_at", ""),
    }

    ledger_path = str(Path(__file__).parents[2] / "town" / "ledger_v1.ndjson")

    # Scan current ledger tail to initialize NDJSONWriter seq + prev_cum_hash
    last_seq, prev_cum = _tail_ledger(ledger_path)

    try:
        writer = NDJSONWriter(
            path=ledger_path,
            seq=last_seq + 1,
            prev_cum_hash=prev_cum,
        )
        writer.append_event(
            event_type="SKILL_PROMOTION_DECISION_V1",
            payload=decision_payload,
            meta=decision_meta,
        )
    except Exception as exc:
        # Fail closed: MAYOR accepted but sovereign write failed.
        # Return REJECT so the caller knows no mutation occurred.
        return {
            "decision":   "REJECT",
            "receipt_id": receipt.receipt_id,
            "gate":       "GATE_PROMOTE_WRITE_FAILED",
            "reason":     f"NDJSONWriter.append_event failed: {exc}",
            "mutations":  [],
        }

    return {
        "decision":   "ACCEPT",
        "receipt_id": receipt.receipt_id,
        "gate":       "GATE_PROMOTE_PASS",
        "mutations":  [{
            "type":        "SKILL_PROMOTION_DECISION_V1",
            "skill_id":    packet["skill_id"],
            "decision_id": decision_id,
            "ledger_path": "town/ledger_v1.ndjson",
        }],
    }
```

---

## Change 3 — Helper `_tail_ledger()`

Add as a **module-level function** (not a method) in `kernel_daemon.py`, after imports,
before the `KernelDaemon` class definition.

```python
def _tail_ledger(ledger_path: str):
    """
    Return (last_seq, last_cum_hash) from the existing ledger file.
    Returns (0, '0'*64) for a missing or empty file.
    NDJSONWriter is initialized with seq=last_seq+1 for append.
    """
    HEX64_ZERO = "0" * 64
    if not Path(ledger_path).exists() or Path(ledger_path).stat().st_size == 0:
        return 0, HEX64_ZERO

    last_seq = 0
    last_cum = HEX64_ZERO

    with open(ledger_path, "rb") as f:
        f.seek(0, 2)                        # end
        size = f.tell()
        f.seek(max(0, size - 65536), 0)     # last 64 KB
        chunk = f.read().decode("utf-8", "replace").strip().splitlines()

    for line in reversed(chunk):
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
            if isinstance(ev, dict) and "seq" in ev and "cum_hash" in ev:
                last_seq = int(ev["seq"])
                last_cum = str(ev["cum_hash"])
                break
        except Exception:
            continue

    return last_seq, last_cum
```

---

## Imports Needed in `kernel_daemon.py`

Check that the following are present at the top of the file (add only what is missing):

```python
import hashlib
import re
import sys
from pathlib import Path

# NDJSONWriter — sovereign write path
# Ensure repo root is on sys.path so 'tools' is importable.
# If the daemon is always launched via 'make' or with PYTHONPATH=CURDIR, this is redundant.
_REPO_ROOT = Path(__file__).parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
from tools.ndjson_writer import NDJSONWriter
```

---

## What Does NOT Change

- `oracle_town/kernel/mayor.py` — no changes. `MayorReceiptEngine.ratify()` is already
  generic. It does not need to know about `promote_skill`.
- `tools/helen_say.py` — already has `--op promote_skill` routing (commit `73dceaf`).
- `schemas/helen_promotion/skill_promotion_packet_v1.json` — schema is already defined.
- `helen_os/state/skill_library_state_updater.py` — already handles `sovereign_promotion: true`.

---

## Post-Apply Verification (sovereign side)

After a human applies these changes, verify with:

```bash
# 1. Start kernel daemon
.venv/bin/python oracle_town/kernel/kernel_daemon.py &

# 2. Assemble promotion packet for REFERENCE_DRIFT_WITNESS_V1
# (fill in real hashes from ADMISSION_STATE_V1.json + git log)
PACKET=$(python3 -c "
import json
print(json.dumps({
  'schema_name': 'SKILL_PROMOTION_PACKET_V1',
  'schema_version': '1.0.0',
  'skill_id': 'REFERENCE_DRIFT_WITNESS_V1',
  'candidate_version': 'V1',
  'candidate_identity_hash': 'sha256:b81b4c2777a16bf815dd98fd1fce2d372ad4bf62d41e3253599fbb3f451b43df',
  'skill_local_admission_commit': 'aee779c',
  'checker_verdict': 'OPERATIONALLY_WITNESSED',
  'operator_countersign': 'JM_TASSY_2026',
  'requested_action': 'SOVEREIGN_PROMOTE'
}))
")

# 3. Route via admissible bridge
.venv/bin/python tools/helen_say.py "$PACKET" --op promote_skill

# 4. Verify sovereign replay
python3 - <<'EOF'
from helen_os.ledger.replay import replay_ledger_to_state
from helen_os.ledger.schemas import initial_state
state = replay_ledger_to_state("town/ledger_v1.ndjson", initial_state())
skill = state["active_skills"].get("REFERENCE_DRIFT_WITNESS_V1", {})
assert skill.get("status") == "ACTIVE", f"Not ACTIVE: {skill}"
assert skill.get("sovereign") is True, f"sovereign flag missing: {skill}"
print("SOVEREIGN ADMISSION CONFIRMED:", skill)
EOF

# 5. Run test suite
make test
```

---

## Failure Modes and Responses

| Failure | Gate | Response |
|---|---|---|
| packet is not valid JSON | `GATE_PROMOTE_PARSE_ERROR` | REJECT, mutations: [] |
| missing required fields | `GATE_PROMOTE_MISSING_FIELDS` | REJECT, mutations: [] |
| wrong schema_name | `GATE_PROMOTE_WRONG_SCHEMA` | REJECT, mutations: [] |
| checker_verdict not OPERATIONALLY_WITNESSED | `GATE_PROMOTE_CHECKER_VERDICT_WEAK` | REJECT, mutations: [] |
| bad hash format | `GATE_PROMOTE_BAD_HASH` | REJECT, mutations: [] |
| wrong requested_action | `GATE_PROMOTE_WRONG_ACTION` | REJECT, mutations: [] |
| Gate A injection fail | `GATE_A_*` | REJECT, mutations: [] |
| MAYOR ratify rejects | `receipt.failed_gate` | REJECT, mutations: [] |
| NDJSONWriter throws | `GATE_PROMOTE_WRITE_FAILED` | REJECT, mutations: [] — no partial write |
| All gates pass | `GATE_PROMOTE_PASS` | ACCEPT, mutations: [{type, skill_id, decision_id, ledger_path}] |

The fail-closed rule: if `NDJSONWriter.append_event()` fails after MAYOR ACCEPT,
the response is still REJECT. The caller (helen_say.py) appends `user_msg + turn` to
town/ledger_v1.ndjson after the kernel call. The sovereign write happens inside the
kernel, before that. If the write fails, helen_say.py's subsequent ledger writes still
proceed (they are a different entry type), but the `mutations` field in the turn's
HAL verdict will be `[]`, which is the observable signal that no promotion occurred.

---

## Sovereignty Note

The `mutations: []` test is the correct probe.
`"decision": "ACCEPT"` from the kernel means MAYOR ratified the claim.
`"mutations": [{"type": "SKILL_PROMOTION_DECISION_V1", ...}]` means the sovereign
write actually happened.
Both must be present for sovereign promotion to be real.
