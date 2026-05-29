# HELEN_OBSIDIAN_CLAUDE.md

The bridge document. Tells Claude how HELEN's governance discipline maps onto
the Obsidian vault — and what that means operationally.

This is not a constitutional document. It is an operational contract.
Authority lives in the operator. HELEN provides the receipt discipline.
Obsidian provides the output velocity. The bridge is the pipeline.

---

## §1. The Pipeline (canonical)

```text
Capture → Process → Connect → Produce → Receipt → Archive
```

Every stage maps to one vault zone and one cognitive operation.

| Stage | Zone | Operation | Role |
|---|---|---|---|
| Capture | `00_CAPTURE` | raw intake | passive — anything can land |
| Process | `00_CAPTURE` → `01_ACTIVE` | rewrite in own words, link | HER + HAL |
| Connect | `01_ACTIVE` (cross-link) | surface latent structure | CHIDDUSH |
| Produce | `01_ACTIVE` → `03_OUTPUT` | synthesize across notes | output generator |
| Receipt | `03_OUTPUT/.receipts/` | hash + manifest the output | REDUCER analog |
| Archive | `02_ARCHIVE` | seal completed work | append-only |

---

## §2. Roles, mapped

HELEN's role separation transfers cleanly. Claude in this vault wears
different hats at different stages.

| HELEN role | Vault stage | What it does |
|---|---|---|
| **HER** (generative) | Capture, Process | Rewrite captures in operator's voice, propose connections |
| **HAL** (poison-check) | Process gate | Flag captures that should not promote to `01_ACTIVE` |
| **CHIDDUSH** | Connect | Find non-obvious cross-links in the weekly connection surface |
| **GOBLIN** | Process, Connect | Inspect, test, log; never decide |
| **REDUCER** | Receipt step | Emit a receipt only when an output is sealed |
| **MAYOR** | The operator | Only the operator decides what enters `03_OUTPUT` as finished |

**Forbidden arrows** (HELEN doctrine, preserved):
- HER → Output (no auto-publish; operator must seal)
- HAL → Output (HAL flags; HAL does not write)
- Capture → Active without Process (no skipping the rewrite-in-own-words step)
- Active → Output without Produce (no shortcut from note to publication)

---

## §3. The Receipt Step (the part Obsidian doesn't have)

Every finished output in `03_OUTPUT/` carries a sidecar receipt at
`03_OUTPUT/.receipts/<slug>.receipt.json`:

```json
{
  "receipt_type": "OUTPUT_RECEIPT_V1",
  "output_id": "2026-05-29_essay-on-admission-asymmetry",
  "output_path": "03_OUTPUT/writing/2026-05-29_essay-on-admission-asymmetry.md",
  "output_hash": "sha256:...",
  "produced_at": "2026-05-29T00:00:00Z",
  "source_notes": [
    {"path": "01_ACTIVE/permanent/admission-asymmetry.md", "hash": "sha256:..."},
    {"path": "01_ACTIVE/permanent/horn-discriminator.md",   "hash": "sha256:..."}
  ],
  "synthesis_notes": "What this output claims that no single source note claims.",
  "contribution_count": 7,
  "authority": "operator",
  "sealed_by": "JM",
  "override": false
}
```

The receipt is what makes Contribution Rate measurable. Each
`source_notes[].path` increments that note's contribution counter.

**Receipts are append-only.** Once written, they are not edited; they are
superseded by a new receipt that references the old.

---

## §4. Contribution Rate (the only metric)

```text
ContributionRate(note) =  (# times note appears in any output receipt)
                          ─────────────────────────────────────────────
                          (months since note entered 01_ACTIVE)
```

```text
ContributionRate(vault)  =  (# notes with contribution_count ≥ 1)
                            ─────────────────────────────────────
                            (total notes in 01_ACTIVE)
```

The quarterly archive audit uses these to decide:
- `contribution_count = 0` and age > 90 days → flag for archive
- `contribution_count ≥ 3` → promote to "reference" subfolder; cite in CLAUDE.md
- `contribution_count = 0` but recently connected → spare for one more quarter

---

## §5. HAL Threshold for Promotion (Capture → Active)

HAL flags a capture as `BLOCK` if any of:
- The note is a verbatim copy with no rewrite
- The note has no plausible link to any active project or topic in CLAUDE.md
- The note makes a claim with no source reference
- The note is purely motivational with no operational content

A `BLOCK` capture does not delete. It stays in `00_CAPTURE/` with a
`.hal-block.md` sidecar explaining why, until the operator either rewrites or
archives it. **No silent rejection.**

---

## §6. Halt Discipline (preserved from HELEN)

Any workflow that requires operator input MUST halt explicitly and enumerate
what is needed to resume. Implicit handoffs are not handoffs.

Examples:
- Daily Processing: halts after assessment, before rewriting, with a list of
  captures flagged for operator decision.
- Output Generator: halts after producing a draft and a receipt skeleton; the
  operator seals.
- Archive Audit: halts after listing candidates; never archives without
  approval.

---

## §7. Five Workflows, named to the pipeline

| Workflow | Pipeline stage | Trigger |
|---|---|---|
| Daily Processing Run | Capture → Process | nightly |
| Active Decision Feeder | Active → (synthesis, no output yet) | on demand |
| Writing Activator | Active → Produce (pre-draft) | before writing |
| Connection Surface | Connect | weekly |
| Output Generator | Produce → Receipt | when output is ready |

Each workflow's prompt lives in `04_SYSTEM/workflows/<name>.md`.

---

## §8. Anti-Patterns (what NOT to do)

```text
1. Process before Capture is ready
   → producing notes in 01_ACTIVE without the raw source in 00_CAPTURE
     loses the relevance-at-capture context.

2. Produce without Connect
   → outputs that draw from only one or two notes are not synthesis;
     they are re-statements. Run Connection Surface first.

3. Receipt without Produce
   → emitting a receipt without an output file is the empty-claim failure mode.
     Receipts must point to artifacts.

4. Archive without contribution review
   → archiving a note that has been used 5 times in outputs is destroying
     leverage. Promote it, don't archive it.

5. Capture as substitute for thinking
   → if every capture is "interesting, will process later," the vault becomes
     a queue, not a metabolism. Process daily or reduce capture rate.

6. Multiple unauthorized voices in 03_OUTPUT
   → only the operator's voice ships. Claude drafts; operator seals.
```

---

## §9. Cross-Reference Discipline (preserved from HELEN)

If a note cites evidence from outside the vault, the citation must include:
- Source identifier (URL, book + page, conversation date)
- Content hash if a file (sha256 of the source bytes)
- Date of capture

Notes that reference external evidence without these fields are
`UNVERIFIED_SOURCE` and cannot promote to `01_ACTIVE/permanent/` until the
fields are filled.

---

## §10. The Lock

```text
Capture is easy. Use is hard.
Generation without admission is compost.
Admission without output is firewall.
Output without receipt is unverifiable.
Receipt without contribution is shelf decoration.

The pipeline closes the loop:
Capture → Process → Connect → Produce → Receipt → Archive
                                            ↑
                                  this is the heartbeat
```

```text
authority: operator-only at the seal
claim:     NO_CLAIM by Claude
admission: by operator review of receipt
metric:    contribution_rate, nothing else
```

---

*This bridge does not replace either system. It tells the Obsidian vault how to*
*carry HELEN's receipt discipline, and tells HELEN-style cognition how to serve*
*output velocity. The strongest part of either system is the pipeline they share.*
