# RECEIPT_SAFE_MUTATION_PROTOCOL_V0.1 — M5 Boundary Sharpening

**authority:** NON_SOVEREIGN
**canon:** NO_SHIP
**lifecycle:** DOCTRINE_DRAFT
**implementation_status:** NOT_APPLICABLE (boundary clarification amendment, not a mechanism)
**mode:** RAW_ONLY · TRACE_ONLY · NO_CLAIM · AUTHORITY_FALSE · NO_ADMISSION · NO_LEDGER_WRITE
**status:** Amendment — sharpens the M5 / M2 / M6 mutation-class boundaries based on convergent corpus signal
**origin_signal:** `min_evidence=3 reseed: [6x] "how do we distinguish between a derived artifact (M5) and ..."` from overnight autoresearch batches 2026-05-26T12-* on `gemma_autonomous_loop.py` with `--prompt-file RECEIPT_SAFE_MUTATION_PROTOCOL_V0_EXCERPT.md`
**amends:** `docs/proposals/RECEIPT_SAFE_MUTATION_PROTOCOL_V0.md §3` (mutation classes M1–M7)
**parent_synthesis:** `docs/proposals/RECEIPT_SAFE_MUTATION_PROTOCOL_V0.md`, `docs/proposals/MAYOR_ADMISSION_PROTOCOL_V0.md`
**proposer:** claude-opus-4-7 (acting as GOBLIN doctrine drafter)
**attestor:** pending HER

---

## §0. Axiom

Carried forward:

> **NO VALID RECEIPT = NO TRUSTED STATE MUTATION.**
> **NO MAYOR SEAL = NO ADMITTED CANON.**

Layered for this amendment:

> **BTOP may shape RAW text. MAYOR alone admits canon.**

Bounded text optimization (forthcoming `BOUNDED_TEXT_OPTIMIZATION_PROTOCOL_V0`) governs *how* a RAW text artifact is edited. MAYOR governs *whether* a RAW artifact becomes admitted canon. Boundary sharpening like this amendment is a BTOP-class edit to the parent doctrine's §3, not an admission act. The parent doctrine remains RAW; this amendment is RAW; nothing in this file is canon.

---

## §1. Problem

An overnight autoresearch run (372 new GEMMA receipts on the topic `"propose one bounded next step toward HELEN OS prototype on local Windows PC..."` with the receipt-safe-mutation excerpt injected as context) produced a convergent signal stronger than any prior pressure in the corpus:

```
reseed at min-evidence=3:
  [1] ev=6  "how do we distinguish between a derived artifact (M5) and"   ← model-discovered
  [2] ev=3  "mutating ledger without receipt"                              ← original RALPH
```

Per-receipt scan over the same corpus:

```
hal_questions mentioning M5 / "derived artifact":   86 receipts
hal_questions mentioning M2 / "quarantine":         31 receipts
hal_questions mentioning M6:                         40 receipts
```

The signature normalization in `tools/reseed_topics.py` (first 10 lowercase words, exact match) drastically understated the convergence; the actual model attention to the M5/M2/M6 triad is the single largest doctrinal pressure the autoresearch loop has ever produced. The boundary the model cannot resolve cleanly from V0 §3 alone is the M5 boundary.

---

## §2. Why M5 produced a stronger signal than expected

The parent V0 doctrine defined seven mutation classes M1–M7. Six of them have unambiguous physical anchors:

| Class | Physical anchor |
|---|---|
| M1 | `helensh/.state/live_ledger.jsonl` (hash-chained ledger file) |
| M2 | `GOVERNANCE/*_PROPOSALS/*.json` (one file per receipt) |
| M3 | A specific field inside an M2 receipt (`operator_decision` or `hal_verdict`) |
| M4 | A specific field inside an M2 receipt (`lifecycle_entry` / `auto_promotion_ceiling`) |
| M6 | `mkdir`, empty-directory operations (no content) |
| M7 | External-effect via CLAW (network, telegram, web fetch) |

**M5 had no precise anchor.** V0 §3 said only: *"Writes to `reports/`, `docs/`, generated DOT files, generated markdown reports. These are not state in the governance sense — they are projections of state."* That sentence under-specified three things:

1. **Whether `docs/proposals/*.md` are M5 or M2.** Doctrine proposals (including this very file) live under `docs/proposals/`. V0's prose says `docs/ = M5`, but proposals are clearly *candidates for canon*, not *projections of state*. The model repeatedly flagged this in the corpus (see §3 trace).
2. **Whether mutation of an existing M5 file is the same class as creation.** Cosmetic rewrites, regenerations, and additive appends are all "writes to a derived artifact" but have different governance implications.
3. **Whether the directory containing M5 files is itself M5, M6, or unclassified.** Creating `reports/autoresearch_5h_<ts>/` involves both a mkdir (M6) and subsequent writes (M5). The model asked whether the directory itself counted as either.

The autoresearch loop concentrated its uncertainty on exactly these three under-specified zones. The reseed pressure is the corpus's way of saying: *the cheapest doctrinal gap to close is M5*.

---

## §3. Trace — six receipts cited as evidence

Selected verbatim from the overnight corpus, narrowed to model-generated `hal_questions` that pinned the M5 ambiguity directly. (Full receipts available in `GOVERNANCE/GEMMA_PROPOSALS/`.)

### §3.1 `gemma_proposal_2026-05-26T12-09-50Z_iter010.json`
> *"Does writing to a local log file during the simulation constitute a state mutation requiring an M1 receipt, or is it strictly M5 artifact generation?"*

Names the M1↔M5 ambiguity. Triggered by the doctrine excerpt's listing of `reports/` as M5 without distinguishing log files from analytical reports.

### §3.2 `gemma_proposal_2026-05-26T12-09-58Z_iter011.json`
> *"How should the system handle a mutation that is logically part of a single atomic transaction spanning M2 and M5 boundaries?"*

Names the **single-write-multi-class** problem. A tool that writes both an M2 receipt and an M5 summary in one logical step has no current doctrinal handling.

### §3.3 `gemma_proposal_2026-05-26T12-10-08Z_iter012.json`
> *"Does the quarantine directory count as M5 (Derived artifact) or M2 (Quarantine receipt), and how does this classification affect the Governor's inspection logic?"*

Names the **directory-vs-content** ambiguity. `GOVERNANCE/GEMMA_PROPOSALS/` (directory) and `GOVERNANCE/GEMMA_PROPOSALS/*.json` (contents) are not the same governance object; V0 conflated them.

### §3.4 `gemma_proposal_2026-05-26T12-10-25Z_iter014.json`
> *"How does the system distinguish between a 'derived artifact' (permissible) and a 'filesystem scaffolding' (M6, permissible) for files written by the prototype script?"*

Names the **M5↔M6 boundary**. Empty file + later append = which class? mkdir + populate = which class?

### §3.5 `gemma_proposal_2026-05-26T12-11-02Z_iter018.json`
> *"How do we distinguish between a 'derived artifact' (M5) and a 'state mutation' (M1/M2) for files written by the mutation_lock.py script itself?"*

Names the **tool-self-classification** problem. A new tool's own log files: M1, M2, or M5? V0 has no rule for "files about the tool" as opposed to "files containing state."

### §3.6 `gemma_proposal_2026-05-26T12-11-45Z_iter023.json`
> *"Does the mutation_intent state violate the M5 derived artifact rule if it lacks a specific lifecycle promotion tag before expiration?"*

Names the **lifecycle-on-M5** question. M5 artifacts have no lifecycle in V0 — but is *no lifecycle* itself a rule, or a gap?

These six are not paraphrases. The full receipts are on disk. Any HER attestation of this amendment should reproduce the search via:

```python
hq = (receipt.get('hal_questions') or '').lower()
if 'm5' in hq or 'derived artifact' in hq: ...
```

against `GOVERNANCE/GEMMA_PROPOSALS/gemma_proposal_2026-05-26T1*.json`.

---

## §4. Refined M5 definition

Replace V0 §3 M5 with the following sharpened definition:

> **M5 — Derived artifact write.**
> A file write whose *content* is fully reconstructible from existing M1–M4 receipts at the moment of write, plus optionally the wall-clock time. The artifact carries *no governance-bearing state of its own*. Producing the same artifact twice from the same input receipts yields byte-identical output (modulo timestamp lines that must be enumerated in the artifact's metadata if any).

This definition has three immediate consequences:

1. **Reconstructibility is the test, not location.** A file in `reports/` that quotes data not in any M1–M4 receipt is NOT M5 — it has acquired state that isn't governed. The location heuristic from V0 was a shortcut; the *content-reconstructibility* property is the actual rule.
2. **M5 is read-only with respect to governed state.** An M5 write must never depend on data the writer itself just generated and didn't receipt.
3. **`docs/proposals/*.md` are NOT M5.** Doctrine proposals carry novel content (the proposed doctrine text) that is not reconstructible from prior receipts. They are M2-class artifacts in a different schema — see §5.

---

## §5. M5 vs M2 — contrast

| Property | M2 (governed receipt) | M5 (derived artifact) |
|---|---|---|
| Content origin | Novel — the receipt IS the new state | Reproducible from prior receipts |
| Schema | `GEMMA_PROPOSAL_RAW_V1` or admitted variant | Free-form (markdown, txt, json, dot) |
| Lifecycle field | Required (`lifecycle_entry`, `auto_promotion_ceiling`) | Absent |
| Two-lane annotation (`operator_decision`, `hal_verdict`) | Required for governance categories | Not applicable |
| `authority` field | Required, always `false` | Not applicable |
| Replay test | Schema validation + chain integrity (M1 only) | Byte-identical regeneration from M1–M4 inputs |
| Acceptable directory | `GOVERNANCE/*_PROPOSALS/*.json`, `docs/proposals/*.md`, `docs/protocols/*.md` | `reports/*`, generated `*.dot`, regenerated `*.png` |

**`docs/proposals/*.md` is a special case.** Its physical location is `docs/`, which V0 labeled M5, but its *content* is novel doctrine — not reconstructible from any prior receipt. The classification follows content, not location. **Doctrine proposals are M2-class** with a different schema (markdown-with-frontmatter) than the JSON `GEMMA_PROPOSAL_RAW_V1` receipts. The schema differs; the class is the same: each one is a self-contained candidate for canon-admission gated by MAYOR.

This file (`RECEIPT_SAFE_MUTATION_PROTOCOL_V0_1_M5_BOUNDARY.md`) is itself M2 by this refinement, not M5.

---

## §6. M5 vs M6 — contrast

| Property | M5 (derived artifact) | M6 (filesystem scaffolding) |
|---|---|---|
| Content | Non-empty, derived from M1–M4 | None / empty (directory shape only) |
| Operations | `write_text`, `write_bytes` of content | `mkdir`, `rmdir` (only of empty), `.gitignore` edit |
| Receipt requirement | None | None |
| Operator confirmation | Not required | Required when destructive (`rmdir` of non-empty, recursive delete) |
| Idempotence | Required (same input → same output bytes) | Required (mkdir is idempotent by definition) |

**Mixed operations are decomposed.** Creating `reports/autoresearch_5h_<ts>/` then writing `analyzer.txt` into it is *two* governance acts:

```
Step 1: mkdir reports/autoresearch_5h_2026-05-26T17-00-00Z/    → M6
Step 2: write_text reports/autoresearch_5h_2026-05-26T17-00-00Z/analyzer.txt  → M5
```

Each step is classified independently. A tool that performs both must declare both classes in its docstring (per V0 §8.1).

---

## §7. Worked examples

### §7.1 Example 1 — Allowed M5 mutation

`python tools/hal_receipt_analyzer.py --source all --terse > reports/snapshot_2026-05-26.txt`

Content is fully derived from the current `GOVERNANCE/*_PROPOSALS/*.json` corpus. Re-running the same command on the same corpus produces byte-identical output (the tool itself enumerates which fields are deterministic). No new state created. Existing M2 receipts are read, not mutated. Lifecycle untouched.

**Classification:** M5. **Receipt required:** none. **Allowed under V0.1:** yes.

### §7.2 Example 2 — Forbidden M5 mutation

A hypothetical `tools/external_enrich.py` that reads receipts and produces `reports/enriched.txt` containing *both* receipt-derived data *and* live data fetched from a URL during the run.

The fetched-URL content is novel state that didn't exist in any M1–M4 receipt prior to the write. The artifact is not reconstructible from existing receipts; rerunning the script on the same corpus will fetch different (or now-unavailable) URL content.

**Classification:** Not M5 — the URL fetch is M7 (external effect), and the resulting file mixes M7 output with M5 content. Mixed-class outputs are forbidden by §6 — the tool must produce two receipts (one M7 capability-receipt for the fetch, one M5 derived-artifact for the local-only portion).

**Forbidden under V0.1:** yes.

### §7.3 Example 3 — M5 that must escalate to M6

A tool wants to write `reports/autoresearch_overnight_batch_01.log`. The first invocation finds `reports/` itself does not exist (clean checkout).

The `mkdir reports/` step is M6 — empty content, directory shape only, no governance implication.
The subsequent `write_text reports/autoresearch_overnight_batch_01.log` is M5 — derived from the running tool's stdout, fully reconstructible.

The tool must declare both M5 and M6 in its docstring. Skipping the mkdir step entirely (assuming `reports/` always exists) is a class-detection failure: the tool then silently performs M6 implicitly, which is a §6 forbidden mutation per V0 ("performing a mutation outside any declared class").

**Classification:** M6 + M5 in sequence. **Required:** explicit decomposition.

### §7.4 Example 4 — M2 mistaken for M5

A new tool `tools/quick_dump.py` writes `GOVERNANCE/GEMMA_PROPOSALS/dump_2026-05-26.json` and the tool's docstring claims "this is just a derived artifact for inspection, classified as M5."

**No.** The physical location `GOVERNANCE/*_PROPOSALS/` is a *structural* M2 anchor. Any file in that directory is governed as an M2 receipt regardless of the tool's claim. The structural anchor overrides the tool's self-classification — *location-as-evidence* is stronger than *docstring-as-claim* in any M5/M2 dispute. A tool that wants to write derived inspection artifacts must use `reports/` or another non-`GOVERNANCE/` location.

**Classification:** M2 by structure. **Tool's M5 claim:** rejected. **Forbidden under V0.1:** yes (the tool either complies with M2 schema requirements — `lifecycle_entry`, `authority`, two-lane annotations — or moves the output to a non-`GOVERNANCE/` directory).

### §7.5 Example 5 — Cosmetic rewrite that must be rejected

A future tool proposes to "reformat" `docs/proposals/RECEIPT_SAFE_MUTATION_PROTOCOL_V0.md` — adjusting markdown whitespace, table syntax, heading styles — without changing the prose content. The tool claims this is an M5 edit because the file lives under `docs/`.

**No.** Per §5 of this amendment, `docs/proposals/*.md` are M2-class doctrine proposals, not M5 derived artifacts. Any rewrite of an M2 receipt — cosmetic, additive, or substantive — is a mutation of governed state. Cosmetic rewrites of M2 receipts are forbidden because:

1. They bypass the proposal lifecycle (no new RAW receipt is issued for the rewrite).
2. They mutate text that may be cited by other receipts whose citations expect specific byte-content.
3. They are precisely the §6 #2 violation of V0: writing without first re-reading and considering whether annotations on the existing receipt would be invalidated.

A legitimate amendment to V0 (or any other admitted M2 schema-class receipt) must be a new M2 receipt that pins the predecessor's hash and is gated by MAYOR per `MAYOR_ADMISSION_PROTOCOL_V0 §11` (revocation/supersession).

**Classification:** Cosmetic rewrite of M2 = M2 mutation. **Allowed path:** new amendment receipt only. **Direct edit:** forbidden.

---

## §8. Validation checklist

Before any tool's write is classified, the following questions must be answered. Failure on any single one means re-classification is required.

```
1. Is the target path inside GOVERNANCE/*_PROPOSALS/?
       YES → M2. Stop. (Schema requirements apply.)
       NO  → continue.

2. Is the target path inside helensh/.state/?
       YES → M1 only. Stop. (LedgerWriter required.)
       NO  → continue.

3. Is the target path docs/proposals/*.md or docs/protocols/*.md?
       YES → M2. Stop. (Schema requirements apply; markdown-frontmatter schema.)
       NO  → continue.

4. Is the operation a mkdir, rmdir of empty, or .gitignore edit?
       YES → M6. Stop. (Operator confirmation if destructive.)
       NO  → continue.

5. Is any content in the file NOT reconstructible from existing M1–M4 receipts at the moment of write?
       YES → NOT M5. Re-classify:
             - Network/external? → M7
             - New local state?  → M1 or M2 depending on schema
             - Mixed?            → DECOMPOSE into per-class receipts
       NO  → M5. Stop.
```

A tool whose write does not terminate at one of the "Stop" lines is mis-classified. Mis-classification is itself a §6 forbidden mutation per V0.

---

## §9. HAL review section (provisional, pre-HER attestation)

This section anticipates HAL's review and surfaces the load-bearing risks. HAL's actual verdict is recorded separately in the cockpit when this proposal enters governance review.

### §9.1 Risks HAL should weigh

1. **Re-classification of `docs/proposals/*.md` is a real change.** V0 said `docs/ = M5`. This amendment moves `docs/proposals/*.md` to M2. Any tool previously assuming proposals were M5 (none currently exist, but the policy implication is real) would be in violation. HAL should confirm no current tool depends on `docs/proposals/*.md` being M5.
2. **Reconstructibility is operationally hard to verify.** The §4 definition (`content fully reconstructible from M1–M4 receipts`) is precise but verifying it for any given M5 candidate requires running the regeneration. No tool currently does this. The §8 checklist is necessary but not sufficient until a regeneration-test exists.
3. **`reports/snapshot_*` files often contain wall-clock timestamps inline.** Strict byte-identical regeneration would fail on those. The §4 parenthetical allows enumerated timestamp lines, but the enumeration mechanism is not specified here.
4. **The corpus signal at min-evidence=6 is one data point.** Real but not multiply-confirmed. HAL should weigh whether this single overnight run's convergence is enough to ratify a §3 amendment, or whether one more independent run with a different prompt-file injection should reproduce the M5 signal first.

### §9.2 HAL provisional verdict (self-issued, advisory only)

`NEEDS_MORE_RECEIPTS` — pending:
- (a) confirmation that no current tool's `M5` self-classification is broken by the `docs/proposals/*.md` reclassification,
- (b) at least one additional autoresearch run with a non-bootstrap-related prompt-file that reproduces the M5 pressure, *or* operator-explicit acceptance that the single run is sufficient evidence.

The provisional verdict does NOT block the amendment from existing as RAW — it blocks the amendment from being a candidate for MAYOR admission until (a) and (b) clear.

---

## §10. BTOP / MAYOR division — explicit statement

> **BTOP may shape RAW text. MAYOR alone admits canon.**

This amendment is a BTOP-class edit to the parent doctrine (V0). The parent remains RAW. This amendment is RAW. Neither becomes canon without MAYOR. The §13.3 deferred bootstrap election remains in effect; this amendment does not trigger or require election. Drafting amendments is allowed under deferred bootstrap; admitting them is not, until MAYOR exists.

A future tool that auto-applies amendments to the parent doctrine on operator approval but without a MAYOR seal would be in violation of this statement. The amendment itself can be cited and read; it cannot be *enforced as canon* without MAYOR.

---

## §11. Halt boundary

GOBLIN halts here. This amendment is RAW.

Resume conditions:

1. **HER attestation**: HER reviews §1–§9 against the actual overnight corpus, confirms the per-receipt counts are reproducible, and either accepts the §4 definition or proposes a refinement.
2. **HAL review (recorded)**: This document is annotated via `review_cockpit.py` with a real `hal_verdict`. The provisional self-issued `NEEDS_MORE_RECEIPTS` in §9.2 is not the recorded verdict.
3. **Operator decision (recorded)**: `APPROVED_FOR_SANDBOX_ONLY`, `REJECTED`, or `PENDING_REVIEW` written via cockpit.
4. **MAYOR admission (deferred)**: cannot be admitted under §13.3 default; would become a candidate for admission only after a bootstrap election produces a MAYOR identity. Under current state, this amendment is RAW reference text indefinitely.

The only action this document performs is **the act of being written and made available for review**. It is itself an M2-class artifact per the very classification it proposes, awaiting its own review — recursive but consistent.

> NO VALID RECEIPT = NO TRUSTED STATE MUTATION.
> NO MAYOR SEAL = NO ADMITTED CANON.
> BTOP MAY SHAPE RAW TEXT. MAYOR ALONE ADMITS CANON.

Stand down preserved.
