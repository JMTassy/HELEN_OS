# OUTSIDE_WORK_FRONTIER_V0

**authority:** NON_SOVEREIGN
**canon:** NO_SHIP
**lifecycle:** FRONTIER_ISSUE
**status:** Named — not yet bottled
**proposer:** claude-sonnet-4-6 (GOBLIN, acting non-sovereign)
**attestor:** pending HAL
**origin_finding:** helen-os-JMTC session 2026-05-28 — two independent
  Claude Code runs reached identical diagnosis
**parent_context:** `CHIDDUSH_BOTTLE_V0.md` (Tier 5 unlocked)

---

## §1. The finding

> **HELEN has never metabolized a single piece of real outside work.**

Every action in every session has been HELEN-about-HELEN:

- `/init helen-os` → documents HELEN
- Provenance traces → trace HELEN's own artifacts
- Ralph smoke test → writes to a HELEN file
- Dataset curation → curates HELEN receipts
- Governance proposals → govern HELEN's own governance
- Fine-tuning roadmap → trains HELEN on HELEN's own output

The system generates, governs, documents, and tests itself with
real sophistication — truth/, skills/, recurrence, the egregor mesh,
persona doctrine — and has never once been pointed at a task from the
operator's actual work and made to produce a receipt for it.

---

## §2. Why this is the frontier, not a feature gap

This is not a missing subsystem. All required subsystems exist:

| Subsystem | Status |
|---|---|
| Receipt chain (ledger, hal, mayor) | LIVE |
| Routing (Claude/Hermes/Ollama) | LIVE |
| Claim workflow | LIVE |
| Governance gate | LIVE |
| Refusal examples | LIVE |
| Replay | LIVE |

The pipe exists. It has never been loaded with real cargo.

The gap is not technical — it is operational. The system has been
building infrastructure for eventually doing outside work. The
infrastructure is sufficient. The first use hasn't happened.

---

## §3. The gravitational failure mode

Every session generates a pull toward building more HELEN rather than
using it. The named attractor:

```text
HELEN-about-HELEN loop:
  audit HELEN → find gap → propose fix → build fix → audit fix →
  find new gap → repeat
```

This loop is self-sustaining because each iteration produces real
artifacts (receipts, docs, commits) that look like progress.
It is the constitutional equivalent of a HAL firewall that only
fires at itself.

The Ralph loop is the purest expression of this: recursion that
feels like progress while touching nothing real.

---

## §4. The tractable discipline

**One outside task per session, before any HELEN-internal work.**

A task qualifies as "outside" if all three hold:

1. **Input originates outside the HELEN repos** — not a HELEN file,
   not a HELEN receipt, not HELEN documentation
2. **Output has value to the operator independent of HELEN** — a
   real email triaged, a real document processed, a real decision
   logged — value that would exist even if HELEN didn't
3. **A receipt is produced** — the task goes through `C → G → E`
   and leaves a `CLOSURE_RECEIPT_V1` with the output artifact hash

If no outside task is named at session start, HELEN-internal work
is still permitted — but the absence is recorded in the session
receipt as `outside_task: null`.

---

## §5. What "success" looks like

```text
FIRST CONTACT RECEIPT (target state):
  input_origin:   outside HELEN repos
  task:           [real operator task]
  artifact_sha:   [sha256 of output]
  hal_verdict:    PASS
  operator_rating: [KEEP / REJECT]
  pipe:           C → G → E → receipt
  outside_value:  TRUE (would exist without HELEN)
```

One passing receipt of this form closes the frontier issue.

---

## §6. What does not close it

- Another dataset curation run
- Another governance proposal
- Another ralph smoke test
- Another HELEN subsystem doc
- A provenance trace of a HELEN artifact
- Training HER on HELEN's own output

None of these carry outside cargo. All are valid HELEN-internal
work. None constitute first contact.

---

## §7. Candidate first tasks (operator names one)

The operator is the only valid source of the outside task.
These are structural candidates only — the actual task belongs to
the operator's real work context:

| Class | Example form |
|---|---|
| Document processing | "Analyze / summarize / reformat [this doc]" |
| Decision logging | "I need to decide [X] — route through HAL, produce a receipt" |
| Communication drafting | "Draft [this message], HAL-review it, receipt the send" |
| Research synthesis | "Synthesize [these sources] into a structured brief" |
| Code review (external) | "Review [this PR / external codebase], produce a HAL-scored report" |

---

## §8. Halt boundary

This frontier issue cannot advance without operator input.

**Required to resume:**
- Operator names one outside task (see §7 candidates)
- Task input is provided (file, URL, paste, or description)
- Session opens with outside task before HELEN-internal work

**Not required:**
- Any code change
- Any new subsystem
- Any governance proposal
- MAYOR review (this is a frontier issue, not a doctrine proposal)

---

## §9. Relationship to CHIDDUSH_BOTTLE_V0

This is not a chiddush (novel insight). The insight existed latent
in the Phase 3 daily-usefulness lock. This document makes it
explicit and gives it a stable name so future sessions can reference
it without rediscovering it.

It does not yet propose a formal discipline for the roadmap.
That bottle opens when the operator names the first outside task
and the pipe carries it. The bottle's content is the receipt, not
this document.

---

*Status as of 2026-05-28: named, not yet acted on.*
*First contact has not yet happened.*
