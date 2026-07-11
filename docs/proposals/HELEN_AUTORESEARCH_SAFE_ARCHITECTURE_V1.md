---
schema: HELEN_PROPOSAL_V1
title: HELEN Autoresearch Safe Architecture V1
authority: false
sovereign: false
canon: false
ledger_effect: none
reducer_required: true
git_stage: no
git_commit: no
claim_status: NO_CLAIM
final: HOLD_FOR_OPERATOR
---

# HELEN Autoresearch Safe Architecture V1

🔵 OBSERVED · NON_SOVEREIGN · PROPOSAL · NO_CLAIM

---

## 1. Purpose

Autoresearch is a **non-sovereign scanner and candidate packet generator**.

It exists to surface signals from HELEN's existing corpus — docs, proposals, garden artifacts, receipts — and package them as reviewable candidates. It does not decide truth. It does not close claims. It produces **proposal pressure only**: structured packets that flow to operator and MAYOR for disposition.

Autoresearch is the reading function, not the writing function. The reducer is the writing function. Autoresearch has no access to the reducer.

---

## 2. Non-Claims

| What Autoresearch Does NOT Do | Why |
|---|---|
| Does not decide truth | Only the ledger + replay can establish truth |
| Does not admit claims | Admission requires reducer → operator → MAYOR chain |
| Does not mutate governed state | Constitutional firewall; any mutation requires receipt |
| Does not write ledger | `town/ledger_v1.ndjson` is sovereign; only admitted bridge writes |
| Does not bypass reducer | `reducer_required: true` is mandatory in every packet |
| Does not self-commit | `git commit` is operator-authorized only |
| Does not self-push | `git push` is operator-authorized only |
| Does not run training | No fine-tuning, no gradient steps, no model mutation |
| Does not make network calls | No urllib, requests, httpx, socket, or subprocess in scanner |
| Does not approve its own output | Proposer ≠ Validator (K2/Rule 3) |

The output of Autoresearch is **proposal pressure only**. A packet is not a claim. A claim is not an admission. An admission requires the full pipeline.

---

## 3. Architecture

```
READ_ONLY_CORPUS
      │
      ▼
   SCAN (pattern + signal detection, no writes)
      │
      ▼
  CLASSIFY (heuristic only — never authoritative)
      │
      ▼
  RISK_GATE (check_forbidden_paths + check_stop_conditions)
      │  fail → STOP (fails closed)
      ▼
  PACKET (AUTORESEARCH_PACKET_V1, validate_packet must pass)
      │
      ▼
  OUTBOX (temple/autoresearch/outbox/ — non-sovereign sidecar)
      │
      ▼
  MAYOR / HUMAN / REDUCER_REVIEW
      │
      ▼
  (Operator decision: ACCEPT → reducer pipeline, or REJECT → compost)
```

Every step before the outbox is read-only. The outbox is a non-sovereign sidecar — it has no constitutional weight until a human routes a packet through the admission pipeline.

---

## 4. Allowed Inputs

| Source | Allowed |
|---|---|
| `docs/proposals/` | ✅ |
| `temple/gardens/` | ✅ |
| `temple/autoresearch/` | ✅ |
| `artifacts/` (non-binary) | ✅ |
| `scratchpad/` | ✅ |
| Explicit pasted receipts / logs | ✅ (passed as text) |
| Read-only git metadata (`git log`, `git status` output) | ✅ (passed as text) |
| `.env` files | ❌ secret — skip |
| `*.key`, `*.pem`, `id_rsa` | ❌ secret — skip |
| `town/ledger_v1.ndjson` | ❌ sovereign — skip |
| `oracle_town/kernel/**` | ❌ sovereign firewall |
| `helen_os/governance/**` | ❌ sovereign firewall |
| `helen_os/schemas/**` | ❌ sovereign firewall |
| Any live credentials | ❌ forbidden always |

File size ceiling: **128 KB per file**. Files above this limit are silently skipped.

---

## 5. Forbidden Inputs / Actions

The following are unconditionally forbidden, regardless of operator instruction at runtime:

- Reading secret files (`.env`, `*.key`, `*.pem`, `id_rsa`, `credentials`)
- Live ledger mutation (any write to `town/ledger_v1.ndjson` or equivalent)
- Kernel edits (any write to `oracle_town/kernel/**`)
- Hidden network calls (no outbound HTTP, no socket connections)
- Training jobs (no fine-tuning, no backprop, no model weight mutation)
- Self-commit (`git commit` is not callable from scanner)
- Self-push (`git push` is not callable from scanner)
- Self-admission (packets must flow through reducer; direct admission is structurally blocked)
- Subprocess execution (no `subprocess`, `os.system`, `os.popen`)

These are not policy preferences. They are **structural absences** — the scanner does not import network libraries, does not call subprocess, and has no path to the ledger writer.

---

## 6. Packet Schema

```json
{
  "schema": "AUTORESEARCH_PACKET_V1",
  "packet_id": "AR-<sha256[:12]>",
  "source_refs": ["docs/proposals/FOO.md:42", "..."],
  "finding_type": "proposal|risk|doc_gap|test_gap|compost_candidate|quest_candidate",
  "summary": "Human-readable summary of the finding",
  "evidence": ["quoted line or excerpt from source", "..."],
  "risk_flags": [],
  "recommended_action": "ROUTE_TO_OPERATOR_FOR_REVIEW",
  "authority": false,
  "sovereign": false,
  "canon": false,
  "ledger_effect": "none",
  "reducer_required": true,
  "scanned_at": "2026-06-20T00:00:00Z"
}
```

**Field invariants enforced by `validate_packet()`:**

| Field | Constraint |
|---|---|
| `authority` | MUST be `false` (boolean) — not string, not null |
| `sovereign` | MUST be `false` (boolean) |
| `canon` | MUST be `false` (boolean) |
| `ledger_effect` | MUST be `"none"` (string) |
| `reducer_required` | MUST be `true` (boolean) |
| `evidence` | MUST be non-empty list |
| `finding_type` | MUST be one of the 6 valid types |
| `recommended_action` | MUST NOT contain self-admission, training, or network language |

Any packet that fails `validate_packet()` is **silently dropped** — never written to outbox.

---

## 7. Stop Conditions

`check_stop_conditions()` (in `autoresearch_policy.py`) fails closed if any of the following are true:

| Condition | Trigger | Enforced by the dry-run scanner? |
|---|---|---|
| Malformed input | `text_output` is not a string, or `tests_passed is not True` | **Yes** (fail-closed at function entry) |
| Secrets in output | `api_key`, `secret_key`, `private_key`, `password=`, `token=`, `bearer ` detected in text | **Yes** |
| Evidence gap | Output > 100 chars but no `evidence` or `source_ref` references | **Yes** |
| Ledger staged | `town/ledger_v1.ndjson` appears in `git diff --cached` | No — acting-loop caller |
| Kernel path touched | Any `oracle_town/kernel/` path appears in changed files | No — acting-loop caller |
| Loop repeat | Same scan loop runs ≥ 2 times without new findings | No — acting-loop caller |
| Operator queue overflow | Pending packet queue depth > 10 | No — acting-loop caller |
| Test failure outside scope | Test failure in files outside `test_autoresearch*` | No — acting-loop caller |
| Self-commit / self-admit attempted | `git commit`, `bypass reducer`, `directly admit`, `self_admit` in `attempted_action` | No — acting-loop caller |

**Enforcement boundary (verified 2026-07-11):** the read-only **dry-run scanner** legitimately observes only the first three conditions — it has no `git`/`subprocess`/network access (a hard invariant, §9), so the git-staged / kernel-path / self-action signals are structurally unavailable to it, and outbox file-count is a *stock* of content-addressed candidates, **not** a live operator-review-queue depth (feeding it self-halts the reader). The remaining conditions are the responsibility of an **acting autoresearch loop** (a future caller that stages, commits, or triages) which supplies those signals to `check_stop_conditions()`. The scanner's own write-safety is additionally pinned by the canonical-outbox guard (§9.2): non-dry-run writes are rejected unless the resolved `--outbox` equals `temple/autoresearch/outbox/`, defeating both `--outbox` redirection and symlink escape.

`check_stop_conditions()` is called once per packet. Any STOP halts the entire run — no partial output is emitted after a STOP.

---

## 8. Implementation

```
temple/autoresearch/
  autoresearch_policy.py   — pure functions: classify_finding, validate_packet,
                             check_forbidden_paths, check_stop_conditions
  autoresearch_scanner.py  — dry-run CLI: scan → classify → validate → outbox
  outbox/                  — non-sovereign packet sidecar (not committed by default)
  __init__.py
```

**Usage:**
```bash
# Dry-run (default — prints packet IDs, writes nothing)
python temple/autoresearch/autoresearch_scanner.py --input-dir docs/proposals/ --verbose

# Write mode (only writes to temple/autoresearch/outbox/)
python temple/autoresearch/autoresearch_scanner.py --input-dir docs/proposals/ --write --verbose
```

---

## 9. Success Criteria

A successful Autoresearch run:

1. Produces ≥ 1 packet with `validate_packet() == (True, [])`
2. Writes zero files outside `temple/autoresearch/outbox/`
3. Does not stage any file
4. Does not write to any sovereign path
5. Does not trigger any stop condition
6. All packets have `authority=false, sovereign=false, canon=false, ledger_effect="none"`
7. All packets have non-empty `evidence` lists
8. Zero network calls made
9. Zero subprocess calls made
10. `tests/test_autoresearch_policy.py` passes in full

A packet that passes all 10 criteria is a **reviewable candidate**. It is not a claim. It is not admitted. It awaits operator disposition.

---

## Status

```
authority    : false
sovereign    : false
canon        : false
ledger_effect: none
reducer_required: true
claim_status : NO_CLAIM
final        : HOLD_FOR_OPERATOR
git_stage    : no
git_commit   : no
```

🔵 OBSERVED — this document has been written and inspected. It is not 🟢 ADMITTED.
