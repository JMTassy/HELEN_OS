# AUTORESEARCH E11/E12 Reconciliation — Diagnostic Report V0

```
artifact_type:         RECONCILIATION_REPORT_V0
report_id:             AUTORESEARCH_E11_E12_RECONCILIATION_REPORT_V0
authority:             NON_SOVEREIGN
canon:                 NO_SHIP
lifecycle:             REPORT (proposer-side, pre-validation)
implementation_status: EXPERIMENT_EXECUTED_READ_ONLY
captured_on:           2026-04-27
proposer_session:      claude-opus-4-7 (main, this session)
parent_proposal:       docs/proposals/AUTORESEARCH_E11_E12_RECONCILIATION.md
                       (commit 0d06b33)
sot_head:              442f5ee → 0d06b33 (this session post-reconciliation-proposal commit)
ledger_state:          dirty (live kernel writes; not touched by this experiment)
```

> **Discipline note**
> This is the **proposer-side report** from running §3 of the parent
> proposal. It is **not** a verdict. It is **not** a receipt. Per §6 of
> the parent, this report requires a fresh-context peer-review sub-agent
> validator before it is routed to MAYOR. KEEP / REJECT belongs to MAYOR
> alone.

---

## §0. Executive Summary

The hypothesis **H₁ — Receipt Drift, Not Structural Drift** is
**falsified** by the experiment.

Three artifacts in `STRUCTURAL_CHANGE` class:
- `helen_os/tests/ci_replay_test_legoracle_gate.py` — expected SHA
  never appeared in SOT git history
- `helen_os/tests/fixtures/legoracle/proposal_ship.json` — expected SHA
  never in history; expected path `legoracle_gate/` never existed in SOT
- `helen_os/tests/fixtures/legoracle/proposal_no_ship.json` — same as
  above

Plus four receipt-integrity findings:
- Contract self-hash unreproducible (recorded ≠ canonicalized)
- Tranche E13-E18 self-hash unreproducible
- E12 receipt has **no hash field** at all
- E11 receipt **missing entirely** from SOT

Plus one invariant-falsification finding:
- Contract claims "No multi-branch exploration"; three active worktrees
  branched at `b241ce2` exist and are unreintegrated.

Evidence-supported verdict candidate for MAYOR (not a verdict): **REVOKE_AND_RERUN**.

ACCEPT_RE_HASH is ruled out (structural changes present).
AMEND_WITH_SUPERSEDES is technically possible only if MAYOR is willing
to issue a SUPERSEDES annotation acknowledging cross-session
incompatibility; see §H.

---

## §A. Per-artifact SHA diff table

13 artifacts examined (all paths referenced in `AUTORESEARCH_CONTRACT_V1.json`,
`AUTORESEARCH_TRANCHE_E13_E18.json`, or
`GOVERNANCE/TRANCHE_RECEIPTS/E12-legoracle-replay-gate-V1.json`).

| # | Path | Expected SHA | Actual SHA | Class | Source |
|---|---|---|---|---|---|
| 1 | `SKILL_REGISTRY_V1.json` | (none) | `10098aac…1cc753b` | UNKNOWN | Contract artifacts_produced |
| 2 | `AUTORESEARCH_TRANCHE_E13_E18.json` | (none) | `fff5f5c4…f7488bd` | UNKNOWN | Contract |
| 3 | `helen_os/governance/legoracle_gate_poc.py` | (none) | `249831d7…8af3` | UNKNOWN | Contract |
| 4 | `helen_os/tests/test_legoracle_gate_poc.py` | (none) | `423b7fd7…b921e7` | UNKNOWN | Contract |
| 5 | `helen_os/tests/ci_replay_test_legoracle_gate.py` | `0872aa46…110345` | `da8f976a…8259173` | **STRUCTURAL_CHANGE** | E12 receipt C1 |
| 6 | `scripts/helen_k8_lint.py` | (none) | `2ced5e45…832d4` | UNKNOWN | Contract |
| 7 | `schemas/k8_summary.schema.json` | (none) | path migrated → `helen_os/schemas/` SHA `39babba3…0bd0c195` | **PATH_RENAME** | Contract; commit `029f8b5` |
| 8 | `oracle_town/skills/voice/gemini_tts/helen_tts.py` | (none) | `29cdc3a8…87cfbb8` | UNKNOWN | Contract |
| 9 | `tools/helen_telegram.py` | (none) | `9f9ab5b8…361cbb7` | UNKNOWN | Contract |
| 10 | `tools/helen_simple_ui.py` | (none) | `fcb93c5f…3d778b13` | UNKNOWN | Contract |
| 11 | `helen_os/tests/fixtures/legoracle/proposal_ship.json` | `7817b286…abcdf20` | `d14acb91…0965aa` | **STRUCTURAL_CHANGE** | E12 receipt C2; expected path `legoracle_gate/` |
| 12 | `helen_os/tests/fixtures/legoracle/proposal_no_ship.json` | `1652e62c…128828d` | `0620616d…39bc01` | **STRUCTURAL_CHANGE** | E12 receipt C3; expected path `legoracle_gate/` |
| 13 | `legoracle_v13rc.py` | `f6267a3c…2dab14` | `f6267a3c…2dab14` | **MATCH** | E12 receipt C4 |

Notation: `(none)` = receipt lists path in artifacts_produced but does
not record an expected SHA constraint.

---

## §B. Tally by class

| Class | Count |
|---|---|
| MATCH | 1 |
| PATH_RENAME | 1 |
| TEST_REFACTOR | 0 |
| FIXTURE_REGEN | 0 |
| **STRUCTURAL_CHANGE** | **3** |
| MISSING | 0 |
| UNKNOWN (no SHA constraint) | 7 |
| TOTAL examined | 13 |

`STRUCTURAL_CHANGE > 0` → H₁ falsified.

---

## §C. STRUCTURAL_CHANGE details (the falsifying rows)

### C.1 `helen_os/tests/ci_replay_test_legoracle_gate.py`

- **Receipt:** E12 claim C1
- **Expected SHA:** `0872aa46f6be09695fc5717303afdeb44b5410ba0d4c37818a5ebbd954110345`
- **Actual SHA:** `da8f976a45ab4c3f6c2f78c0bd9d94cb635a76cfca56cd3abb013a9cb8259173`
- **Introducing commit:** `1bff42b` ("HELEN OS v1 — AUTORESEARCH contract sealed, governance validated", 2026-04-17)
- **Subsequent edits since `1bff42b`:** none (verified `git diff 1bff42b -- <path>` is empty)
- **Search for expected SHA in git history:** the SHA `0872aa46…` does **not** appear at any commit on any branch in this SOT.
- **Path divergence:** the test code (line 32 of the file) references
  `fixtures/legoracle` (matches actual SOT layout); the E12 receipt
  references `legoracle_gate/` (does not exist in SOT). Paths are
  internally consistent within SOT but inconsistent with the receipt's
  expectations.

**Diagnosis:** This file was created at commit `1bff42b` with content
that has SHA `da8f976a…`. The receipt's expected SHA `0872aa46…` was
computed in a session whose content never reached this SOT. The file
is not "drifted" — it has a distinct origin.

---

### C.2 `helen_os/tests/fixtures/legoracle/proposal_ship.json`

- **Receipt:** E12 claim C2
- **Expected SHA:** `7817b28689c1e9a93124c72221f19c1274755c60fb5b397106365d386abcdf20`
- **Actual SHA:** `d14acb919674ad8aa0cc4995990279583966d21fc1640dfc11a863ea270965aa`
- **Expected path:** `helen_os/tests/fixtures/legoracle_gate/proposal_ship.json`
- **Actual path:** `helen_os/tests/fixtures/legoracle/proposal_ship.json`
- **Introducing commit:** `1bff42b`
- **Subsequent edits:** none
- **Search for expected SHA in history:** `7817b286…` does **not**
  appear at any commit; never present in SOT.
- **Search for `legoracle_gate` directory in history:** does not exist
  at any point in SOT history.

**Diagnosis:** Expected fixture differs in both content (different SHA)
and location (different directory). The file was committed once at
`1bff42b` with its current SHA at its current path.

---

### C.3 `helen_os/tests/fixtures/legoracle/proposal_no_ship.json`

- **Receipt:** E12 claim C3
- **Expected SHA:** `1652e62c69a11673e822d018e661c15050b18952a95757f442dea5fbe128828d`
- **Actual SHA:** `0620616d91376fba0713691850447bb1216219f76d1f2e795acad1b69539bc01`
- **Expected path:** `helen_os/tests/fixtures/legoracle_gate/proposal_no_ship.json`
- **Actual path:** `helen_os/tests/fixtures/legoracle/proposal_no_ship.json`
- **Introducing commit:** `1bff42b`
- Same situation as C.2: never the expected SHA, never the expected path.

---

## §D. Worktree audit

Three active worktrees inspected. For each, the four E12 artifacts
(C.1, C.2, C.3, and `legoracle_v13rc.py`) were SHA-compared with main:

| Worktree | C.1 | C.2 | C.3 | `legoracle_v13rc.py` | Verdict |
|---|---|---|---|---|---|
| `admiring-fermi-af4d54` | match main | match main | match main | match main | **No divergence** |
| `elated-mirzakhani-ee1c46` | match main | match main | match main | match main | **No divergence** |
| `modest-noether-0e644e` | match main | match main | match main | match main | **No divergence** |

Common merge base: `b241ce2156645c8a3ffaa6b5cf2d343e4c945e54`
(2026-04-21, "feat(library): promote 11 hero stills").

**Important counterpoint:** the worktrees do **not** carry an
alternative version of the E12 artifacts. The divergence is not "main
vs worktrees" — it's "SOT (main + worktrees) vs Desktop session that
authored the E12 receipt." The Desktop session is not in this repo at
all.

---

## §E. E11 receipt-absence diagnosis

**Contract claim:** `AUTORESEARCH_CONTRACT_V1.json` lines 10–13:
```
"tranches": [
  "E1-E10",
  "E11-E12",
  "E13-E20"
]
```
plus `"epochs_executed": 20`.

**Search results:**

| Search | Result |
|---|---|
| `find GOVERNANCE/TRANCHE_RECEIPTS/ -name "*E11*"` | 0 results |
| `grep -r "E11" GOVERNANCE/TRANCHE_RECEIPTS/` | 0 results |
| `git log --all --oneline | grep -i "e11"` | 0 commits |
| Files in `GOVERNANCE/TRANCHE_RECEIPTS/` | E12, E13, E14, E15, E16, E17, E18, E19, E20 only — **no E11** |

**Diagnosis:** No E11 sub-receipt was ever written to this SOT. The
contract claims an `E11-E12` paired tranche shipped, but only the E12
sub-receipt (which itself acknowledges a "parallel session at
`~/Documents/GitHub/helen_os_v1/` cum_hash `b3415eb3edfb`") exists.

**Implication:** the contract's `epochs_executed: 20` is reproducible
from sub-receipts only for E12-E20. E1-E11 are claimed but
unaccounted for in `GOVERNANCE/TRANCHE_RECEIPTS/`. (E1-E10 may have
been accounted for in a different artifact form predating
`TRANCHE_SUB_RECEIPT_V1`; that's outside this experiment's scope.)

---

## §F. Receipt self-hash recomputation

| Receipt | Recorded hash | Recomputed (sorted-keys, no whitespace) | Match |
|---|---|---|---|
| `AUTORESEARCH_CONTRACT_V1.json` | `bc5d9226c5e767…d348225` (`contract_hash`) | `65af666b252ef255…b9a0e26` | ✗ MISMATCH |
| `AUTORESEARCH_TRANCHE_E13_E18.json` | `d285cf24f6e966…bad4db8` (`receipt_hash`) | `501b91ba835c4890…cc7fd679a` | ✗ MISMATCH |
| `E12-legoracle-replay-gate-V1.json` | (no hash field) | `80b99123070bc7ad…fc6bdddc9` | N/A — no field to check |

**Canonicalization protocol attempted:** RFC 7159 minimal whitespace +
sorted keys (the most common Python `json.dumps(obj, sort_keys=True,
separators=(",", ":")).encode()` recipe). Recomputation does **not**
reproduce the recorded hashes for the contract or tranche receipt.

**Diagnosis options** (data does not distinguish between them):
1. The receipts were canonicalized via a non-standard protocol not
   documented in the SOT.
2. The receipts were modified after their hash field was computed.
3. The receipts came from a session whose canonicalizer is not present
   in the SOT codebase.

In all three cases, the receipts are **not currently
self-verifiable** from SOT tooling. The E12 receipt additionally has
**no hash field**, which means it is not even claiming integrity.

---

## §G. Fixture path resolution

- **E12 receipt expects:** `helen_os/tests/fixtures/legoracle_gate/`
- **SOT actual:** `helen_os/tests/fixtures/legoracle/`
- **Directory contents (verified 2026-04-27):**
  ```
  helen_os/tests/fixtures/legoracle/
  ├── environment_pin.json
  ├── expected_decisions.json
  ├── proposal_no_ship.json
  └── proposal_ship.json
  ```
- **Search for `legoracle_gate` anywhere in SOT:** zero results, all
  branches, all history.
- **Rename history:** none found. The directory was created as
  `legoracle/` at commit `1bff42b` and has not been renamed.

**Diagnosis:** The path expectation in the E12 receipt was **never
valid in this SOT**. It is consistent with the E12 receipt's own
acknowledgment that a parallel session authored it.

---

## §H. Verdict candidates for MAYOR

This section presents evidence-supported candidates. **It is not a
verdict.** MAYOR rules; the proposer does not.

### Candidate 1 — `ACCEPT_RE_HASH`

**Definition:** H₁ holds; only PATH_RENAME / TEST_REFACTOR /
FIXTURE_REGEN class mismatches; zero STRUCTURAL_CHANGE.

**Status: RULED OUT BY EVIDENCE.**
- §B tally: STRUCTURAL_CHANGE = 3.
- §C: three artifacts have expected SHAs that never appeared in SOT
  history.
- §G: fixture path was never `legoracle_gate/` in SOT.

This candidate is inconsistent with the data.

---

### Candidate 2 — `AMEND_WITH_SUPERSEDES`

**Definition:** Mostly non-structural with a small bounded structural
change; superseded via a one-line ledger annotation.

**Status: TECHNICALLY POSSIBLE WITH CAVEATS.**

For MAYOR to choose this candidate, the SUPERSEDES annotation would
need to acknowledge:
- The E12 receipt's expected SHAs (C1, C2, C3) were never present in
  this SOT.
- The path expectation `legoracle_gate/` was never present.
- The receipts are not self-verifiable (§F).
- The E11 receipt is missing entirely (§E).

A "one-line annotation" cannot preserve the original receipts'
integrity claims if the SHAs and paths they assert are inconsistent
with the artifacts that actually exist. The annotation would have to
materially restate that the E12 receipt is **not reproducible from
SOT** and is retained as a historical artifact only.

This is closer to "soft revoke" than to amendment. MAYOR may judge it
sufficient for E13 to proceed with a fresh attestation; MAYOR may
judge it insufficient and select Candidate 3 instead.

---

### Candidate 3 — `REVOKE_AND_RERUN`

**Definition:** STRUCTURAL_CHANGE found, or unable to verify, or
receipts are unreproducible.

**Status: STRONGLY EVIDENCE-SUPPORTED.**

| Evidence | Source |
|---|---|
| 3 STRUCTURAL_CHANGE mismatches | §C.1, §C.2, §C.3 |
| Expected SHAs never in git history | §C |
| Fixture path never matched receipt | §G |
| Contract hash unreproducible | §F |
| Tranche hash unreproducible | §F |
| E12 receipt has no hash field | §F |
| E11 receipt absent from SOT | §E |
| Cross-session divergence acknowledged in E12 itself | E12 receipt line 91 |
| Contract invariant "No multi-branch exploration" falsified | three active worktrees, see §D |

If MAYOR selects this candidate, the consequences (per parent §4
upgrade_path) are:
- E11 and E12 receipts marked SUPERSEDED (not amended)
- E13 remains blocked
- A new bounded tranche `T11_T12_RERUN` is proposed in a separate file
  (a sibling proposal to the parent reconciliation hypothesis)
- Worktrees may need explicit closure or merge before T11_T12_RERUN
  opens (operator decision)

---

## §I. What this report does NOT do

- It does not issue a verdict (MAYOR's role).
- It does not write any sub-receipt to `GOVERNANCE/TRANCHE_RECEIPTS/`.
- It does not amend, edit, rename, or delete any existing receipt or
  contract.
- It does not write to `town/ledger_v1.ndjson`.
- It does not invoke `tools/helen_say.py` or any kernel-routing utility.
- It does not run any test suite or gate.
- It does not merge or delete any worktree.
- It does not propose `T11_T12_RERUN` (that is a sibling proposal,
  conditional on MAYOR's verdict).

---

## §J. Required next steps (per parent §6 + §8)

1. **Peer-review validator** — fresh-context sub-agent must independently
   re-run §A–§G and confirm or refute the SHA diff table byte-for-byte.
   Rule 3: Proposer ≠ Validator.
2. **Operator countersignature** on this report (or on a peer-review-
   amended version of it).
3. **Routing to MAYOR** via `tools/helen_say.py "<report-summary>" --op
   dialog` (kernel daemon must be booted first).
4. **MAYOR ruling**: ACCEPT_RE_HASH (ruled out by evidence) /
   AMEND_WITH_SUPERSEDES / REVOKE_AND_RERUN.
5. **Reducer applies MAYOR's verdict** via the canonical writer.
6. Only then is E13 unblocked or a re-run tranche proposed.

This report is upstream of all six steps. It is the evidence packet,
not the verdict.

---

## §K. Final receipt

```
artifact_type:         RECONCILIATION_REPORT_V0
authority:             NON_SOVEREIGN
canon:                 NO_SHIP
lifecycle:             REPORT (proposer-side, pre-validation)
implementation_status: EXPERIMENT_EXECUTED_READ_ONLY
findings:              H1_FALSIFIED (3 STRUCTURAL_CHANGE)
verdict_candidate:     REVOKE_AND_RERUN (evidence-supported, MAYOR rules)
peer_review_required:  YES (Rule 3, Proposer ≠ Validator)
operator_countersig:   PENDING
mayor_routing:         PENDING (kernel daemon down)
commit_status:         NO_COMMIT (pending operator authorization)
push_status:           NO_PUSH  (pending operator authorization)
next_verb:             review report → dispatch peer-review → countersign
```
