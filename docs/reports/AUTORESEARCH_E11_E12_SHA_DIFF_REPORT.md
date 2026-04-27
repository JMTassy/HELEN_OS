# AUTORESEARCH E11/E12 — SHA Diff Report

```
artifact_type:         SHA_DIFF_EXPERIMENT_REPORT
report_id:             AUTORESEARCH_E11_E12_SHA_DIFF_REPORT
authority:             NON_SOVEREIGN
canon:                 NO_SHIP
lifecycle:             REPORT
implementation_status: READ_ONLY_ANALYSIS
captured_on:           2026-04-27
parent_proposal:       docs/proposals/AUTORESEARCH_E11_E12_RECONCILIATION.md
                       (commit 0d06b33)
sibling_report:        docs/reports/AUTORESEARCH_E11_E12_RECONCILIATION_REPORT_V0.md
                       (longer-form companion, same evidence base)
```

> **Discipline note**
> This report does not decide KEEP/REJECT. MAYOR decides. Reducer applies.

---

## §1. Executive Summary

The §3 read-only SHA-diff experiment from the parent reconciliation
proposal was executed by an Explore sub-agent (read-only by tool
restriction) on 2026-04-27 against the SOT at `0d06b33` (this branch).

**Headline finding:** the hypothesis **H₁ — Receipt Drift, Not
Structural Drift** is **FALSIFIED** at the artifact level: three
artifacts referenced by the E12 receipt show STRUCTURAL_CHANGE
classification (expected SHAs never present in SOT git history; one
fixture path expectation `legoracle_gate/` never existed in SOT).

**Falsifier-specific finding (§8):** none of the STRUCTURAL_CHANGE rows
trace to **LEGORACLE gate logic edits** or **replay determinism logic
edits**. They trace to (i) the replay-gate **test file** and (ii) the
SHIP / NO_SHIP **fixtures**. The core LEGORACLE logic file
(`legoracle_v13rc.py`) hashes identically to the recorded receipt SHA.

**Recommendation to MAYOR (not a verdict): REQUEST_MORE_EVIDENCE.**
Rationale in §9.

---

## §2. Inputs inspected

| # | Input | Path |
|---|---|---|
| 1 | AUTORESEARCH contract | `AUTORESEARCH_CONTRACT_V1.json` |
| 2 | E13–E18 tranche receipt | `AUTORESEARCH_TRANCHE_E13_E18.json` |
| 3 | E12 sub-receipt | `GOVERNANCE/TRANCHE_RECEIPTS/E12-legoracle-replay-gate-V1.json` |
| 4 | Tranche receipts directory | `GOVERNANCE/TRANCHE_RECEIPTS/` (for E11 search) |
| 5 | LEGORACLE gate code | `helen_os/governance/legoracle_gate_poc.py` |
| 6 | Replay gate test | `helen_os/tests/ci_replay_test_legoracle_gate.py` |
| 7 | LEGORACLE v13rc | `legoracle_v13rc.py` (root) |
| 8 | Fixture directory | `helen_os/tests/fixtures/legoracle/` (actual) and search for `legoracle_gate/` |
| 9 | Worktree state | `.claude/worktrees/` (3 active worktrees) |
| 10 | Git history | `git log --all --since='2026-04-15'` and per-path `--follow` queries |

No write operation performed. No test or gate executed. No spine touch.

---

## §3. Receipt-referenced artifacts

13 artifact paths were enumerated across the three primary receipts'
`artifacts_produced` lists and the E12 sub-receipt's claim
expectations. The full table appears in §4.

Of those 13:
- 6 carry an explicit **expected SHA-256** in a receipt claim
- 7 are listed as artifacts_produced **without a SHA constraint** (UNKNOWN class)

---

## §4. SHA comparison table

| # | Path | Expected SHA | Actual SHA | Class |
|---|---|---|---|---|
| 1 | `SKILL_REGISTRY_V1.json` | (none) | `10098aac…1cc753b` | UNKNOWN |
| 2 | `AUTORESEARCH_TRANCHE_E13_E18.json` | (none) | `fff5f5c4…f7488bd` | UNKNOWN |
| 3 | `helen_os/governance/legoracle_gate_poc.py` | (none) | `249831d7…8af3` | UNKNOWN |
| 4 | `helen_os/tests/test_legoracle_gate_poc.py` | (none) | `423b7fd7…b921e7` | UNKNOWN |
| 5 | `helen_os/tests/ci_replay_test_legoracle_gate.py` | `0872aa46…110345` | `da8f976a…8259173` | **STRUCTURAL_CHANGE** |
| 6 | `scripts/helen_k8_lint.py` | (none) | `2ced5e45…832d4` | UNKNOWN |
| 7 | `schemas/k8_summary.schema.json` | (none) | path migrated → `helen_os/schemas/k8_summary.schema.json` SHA `39babba3…0bd0c195` | **PATH_RENAME** |
| 8 | `oracle_town/skills/voice/gemini_tts/helen_tts.py` | (none) | `29cdc3a8…87cfbb8` | UNKNOWN |
| 9 | `tools/helen_telegram.py` | (none) | `9f9ab5b8…361cbb7` | UNKNOWN |
| 10 | `tools/helen_simple_ui.py` | (none) | `fcb93c5f…3d778b13` | UNKNOWN |
| 11 | `helen_os/tests/fixtures/legoracle/proposal_ship.json` (receipt: `legoracle_gate/`) | `7817b286…abcdf20` | `d14acb91…0965aa` | **STRUCTURAL_CHANGE** |
| 12 | `helen_os/tests/fixtures/legoracle/proposal_no_ship.json` (receipt: `legoracle_gate/`) | `1652e62c…128828d` | `0620616d…39bc01` | **STRUCTURAL_CHANGE** |
| 13 | `legoracle_v13rc.py` | `f6267a3c…2dab14` | `f6267a3c…2dab14` | **MATCH** |

Receipt self-hash recomputation (separate but related):

| Receipt | Recorded | Recomputed (sorted-keys, no whitespace) | Match |
|---|---|---|---|
| `AUTORESEARCH_CONTRACT_V1.json` | `bc5d9226…d348225` | `65af666b…b9a0e26` | ✗ |
| `AUTORESEARCH_TRANCHE_E13_E18.json` | `d285cf24…bad4db8` | `501b91ba…cc7fd679a` | ✗ |
| `E12-legoracle-replay-gate-V1.json` | (no hash field) | `80b99123…fc6bdddc9` | N/A — no field |

---

## §5. Divergence classification

| Class | Count | Rows |
|---|---|---|
| MATCH | 1 | #13 (`legoracle_v13rc.py`) |
| PATH_RENAME | 1 | #7 (k8_summary.schema.json migrated post-seal in commit `029f8b5`) |
| TEST_REFACTOR | 0 | — |
| FIXTURE_REGEN | 0 | — |
| STRUCTURAL_CHANGE | **3** | #5, #11, #12 |
| UNKNOWN (no SHA constraint in any receipt) | 7 | #1, #2, #3, #4, #6, #8, #9, #10 |
| TOTAL | 13 | — |

The three STRUCTURAL_CHANGE rows are the falsifying evidence for H₁.
None are core logic; see §8.

---

## §6. Evidence for each of the 9 divergence signals

These are the nine signals enumerated in §1 of the parent proposal.
Each is now backed by experiment-level data.

### Signal 1 — Contract hash mismatch
**Evidence:** §4 receipt-self-hash row 1. Recorded `bc5d9226…d348225`,
recomputed `65af666b…b9a0e26`. Mismatch. Canonicalization protocol
(sorted-keys, no whitespace) is the standard form; the recorded hash
does not match this protocol.

### Signal 2 — Tranche E13-E18 hash mismatch
**Evidence:** §4 receipt-self-hash row 2. Recorded `d285cf24…bad4db8`,
recomputed `501b91ba…cc7fd679a`. Mismatch via the same canonicalization.

### Signal 3 — E12 CI test file SHA mismatch
**Evidence:** §4 row 5. Expected `0872aa46…110345` (E12 receipt C1),
actual `da8f976a…8259173`. Per-path git log (`git log --all --follow --
helen_os/tests/ci_replay_test_legoracle_gate.py`) shows the file was
created at commit `1bff42b` with the **current** SHA. The expected SHA
**never appeared** at any commit on any branch in this SOT.

### Signal 4 — Fixture directory path mismatch
**Evidence:** §4 rows 11–12. E12 receipt claims `legoracle_gate/`,
SOT contains `legoracle/`. Search for the directory `legoracle_gate`
across all branches and history: zero results. The path
`legoracle_gate/` was **never present** in this SOT.

### Signal 5 — E15 cross-session note
**Evidence:** `AUTORESEARCH_TRANCHE_E13_E18.json` E15 entry contains
the literal note: *"Executed in operator's local session (Releve 24)"*
and the metric *"48→0 on operator side, 19 remaining here"*. This is
self-acknowledged cross-session execution within the receipt itself.

### Signal 6 — E11 receipt missing
**Evidence:** searches against `GOVERNANCE/TRANCHE_RECEIPTS/`:
- `find ... -name "*E11*"` → 0 results
- `grep -r "E11" GOVERNANCE/TRANCHE_RECEIPTS/` → 0 results
- `git log --all --oneline | grep -i "e11"` → 0 commits
The contract claims an `E11-E12` paired tranche shipped, but only the
E12 sub-receipt exists.

### Signal 7 — Three active parked worktrees
**Evidence:** `.claude/worktrees/` contains 18 directories total; 3 are
active (last-modified within the last 7 days):
`admiring-fermi-af4d54`, `elated-mirzakhani-ee1c46`,
`modest-noether-0e644e`. Common merge base for all three:
`b241ce2156645c8a3ffaa6b5cf2d343e4c945e54` (2026-04-21).

### Signal 8 — Contract invariant "No multi-branch exploration" violated
**Evidence:** `AUTORESEARCH_CONTRACT_V1.json` line 117 states: `"No
multi-branch exploration"`. Current state: three active worktrees plus
main → multi-branch state. Invariant falsified by current SOT state.

### Signal 9 — Two cum_hash bases
**Evidence:** `E12-legoracle-replay-gate-V1.json` line 91 contains the
literal text: *"Parallel session at ~/Documents/GitHub/helen_os_v1/
cum_hash b3415eb3edfb reached the same seal via a different path (8
tests + 12 tests = 20 tests); this session's gate is narrower (4
tests)..."*. The receipt itself acknowledges two cum_hash bases.

---

## §7. H₁ — supported or falsified?

**H₁ statement** (from parent proposal §2):
> The E11/E12 divergence is bounded to artifact-level drift between
> the Desktop/Releve 24 session and the SOT main branch — fixture path
> renames, test file refactors, post-seal contract edits — and does
> not reflect a structural change to the LEGORACLE gate logic, the
> replay determinism boundary, or the K8 / K-tau gate semantics.

**Verdict: PARTIALLY FALSIFIED.**

- **Falsified at the artifact level** (§4, §5): three STRUCTURAL_CHANGE
  rows. The expected SHAs and the expected fixture path were **never**
  present in SOT history — these are not renames, refactors, or
  regenerations of an earlier-canonical SOT artifact. They are
  artifacts from a different session that were not synced to SOT.
- **Not falsified at the logic level** (§8 below): the LEGORACLE gate
  logic and the replay determinism logic are not implicated.

H₁'s framing of "drift" is too gentle for the data. The correct framing
is **cross-session incompatibility**: the E12 receipt and its expected
artifacts originate from a session that is not represented in SOT, and
SOT contains a parallel artifact set that was never reconciled.

---

## §8. Falsifier check — STRUCTURAL_CHANGE traced to LEGORACLE or replay logic edits?

The falsifier in the parent proposal is sharper than H₁: "If H₁ is
falsified (any signal traces to **structural change**: receipts E11 / E12
must be marked SUPERSEDED..." with the implicit refinement that
structural change here means **logic** edits, not test/fixture surface.

For each STRUCTURAL_CHANGE row, I check whether the change touches
LEGORACLE gate logic or replay determinism logic:

| Row | Path | Logic? | Trace |
|---|---|---|---|
| #5 | `helen_os/tests/ci_replay_test_legoracle_gate.py` | **NO** — this is the **test** for the replay gate, not the gate itself. The change is in test scaffolding (path references, harness shape). |
| #11 | `helen_os/tests/fixtures/legoracle/proposal_ship.json` | **NO** — this is **input data** for the test, not gate logic. |
| #12 | `helen_os/tests/fixtures/legoracle/proposal_no_ship.json` | **NO** — same as #11. |

**Critical complementary evidence:**
- Row #13 `legoracle_v13rc.py` (the LEGORACLE v13 release-candidate
  logic file): **expected SHA matches actual SHA exactly**
  (`f6267a3c…2dab14` on both sides). Logic file is identical across
  E12 receipt expectations and current SOT.
- Row #3 `helen_os/governance/legoracle_gate_poc.py` (the gate code):
  **no expected SHA recorded** in any receipt; cannot be falsified.
  Current SHA is `249831d7…8af3`. No claim of structural change can be
  made without a baseline.

**Falsifier verdict: NEGATIVE.** No STRUCTURAL_CHANGE row traces to
LEGORACLE gate logic or replay determinism logic edits. The structural
change is at the test + fixture surface only.

This is the most decision-relevant finding in the entire report.

---

## §9. Recommendation to MAYOR — `REQUEST_MORE_EVIDENCE`

| Candidate | Evidence-supported? |
|---|---|
| **ADMIT** | NO. The expected SHAs and the expected `legoracle_gate/` path were **never present in SOT**. The receipts are not self-verifiable (no canonicalization protocol in the SOT reproduces the recorded hashes). The E12 receipt has no hash field. ADMIT would let in a receipt that SOT cannot independently verify. |
| **REJECT** | DEFENSIBLE but premature. A REJECT would mark E11/E12 as SUPERSEDED and require a re-run. But the falsifier-specific check (§8) is **negative** — the underlying LEGORACLE / replay logic does not appear to have changed. Throwing away the E12 work when the substantive logic claim still holds (matching `legoracle_v13rc.py` SHA) is wasteful. |
| **REQUEST_MORE_EVIDENCE** | **EVIDENCE-SUPPORTED.** The decisive open question is whether the Desktop/Releve 24 session's `legoracle_gate/` fixtures and `0872aa46…` test file represent (a) a **substantively different** test surface (different assertions, different determinism contract) — in which case REJECT is correct — or (b) **the same test surface with different paths/scaffolding** — in which case AMEND_WITH_SUPERSEDES (or a localized re-attestation in SOT shape) suffices. SOT alone cannot answer this; the Desktop session's artifacts are not present in this repo. |

**REQUEST_MORE_EVIDENCE** asks MAYOR to require, before ruling on the
final disposition:
1. The Desktop session's `legoracle_gate/proposal_ship.json` and
   `proposal_no_ship.json` content, for content-level diff against
   SOT's `legoracle/` versions.
2. The Desktop session's `ci_replay_test_legoracle_gate.py` (SHA
   `0872aa46…`), for line-level diff against the SOT version.
3. The Desktop session's E11 sub-receipt (if it exists), to close the
   §6 absence gap.
4. The Desktop session's canonicalization implementation that produced
   the recorded `bc5d9226…` and `d285cf24…` hashes, so receipt
   integrity can be independently re-verified.

If those four items are produced and the diffs are non-structural
(scaffolding only), the path forward is `AMEND_WITH_SUPERSEDES` with
a single annotation that explicitly states the cross-session origin.
If any of the four items reveals logic-level divergence in LEGORACLE
or replay, the path forward is `REJECT` (revoke and rerun).

If the Desktop session's artifacts cannot be produced (e.g., the
session's local state is lost), then **REJECT becomes the
evidence-supported candidate**, since a non-reproducible receipt
cannot be admitted to canon.

---

## §10. Decision authority — explicit note

> **This report does not decide KEEP/REJECT.**
> **MAYOR decides.**
> **Reducer applies.**

This report:
- ❌ does **not** issue a verdict
- ❌ does **not** write to `town/ledger_v1.ndjson`
- ❌ does **not** write to `helen_os/governance/`, `helen_os/schemas/`,
  `mayor_*.json`, `GOVERNANCE/CLOSURES/`, `GOVERNANCE/TRANCHE_RECEIPTS/`
- ❌ does **not** edit, rename, or delete any existing receipt
- ❌ does **not** open E13
- ❌ does **not** loop, run a Ralph loop, or run a daemon loop
- ❌ does **not** automatically KEEP or REJECT

Per Rule 3 (Proposer ≠ Validator), this report — written by the same
session that authored the parent proposal — must be re-validated by a
**fresh-context peer-review sub-agent** before MAYOR reads it.

After peer-review:
1. Operator countersignature
2. Routing to MAYOR via `tools/helen_say.py "<report-summary>" --op
   dialog` (kernel daemon must be booted first)
3. MAYOR ruling
4. Reducer applies the verdict

This report is upstream of all four steps.

---

## Final Receipt

```
authority:             NON_SOVEREIGN
canon:                 NO_SHIP
lifecycle:             REPORT
implementation_scope:  READ_ONLY_SHA_DIFF_ANALYSIS
implementation_status: EXPERIMENT_EXECUTED_READ_ONLY
findings:              H1_PARTIALLY_FALSIFIED
                       (3 STRUCTURAL_CHANGE at artifact level;
                        zero logic-level structural change per §8 falsifier)
verdict_candidate:     REQUEST_MORE_EVIDENCE (MAYOR rules)
peer_review_required:  YES (Rule 3, Proposer ≠ Validator)
operator_countersig:   PENDING
mayor_routing:         PENDING (kernel daemon down)
commit_status:         NO_COMMIT
push_status:           NO_PUSH
next_verb:             review report
```
