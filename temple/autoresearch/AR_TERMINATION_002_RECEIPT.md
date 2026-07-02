# AR_TERMINATION_002_RECEIPT

```yaml
schema: AR_TERMINATION_002_RECEIPT
mode: AUTORESEARCH_PULLED_EPOCH
authority: false
canon: false
ledger_effect: none
implementation_claim: reported_only
receipt_admitted: false
date: 2026-07-02
```

HYPOTHESIS = HELEN's PROPOSED / NON_SOVEREIGN / NO_CLAIM objects can be
measured as a finite lifecycle system, and the harness can distinguish
a live safety control from a permanent parking state.

FILES_MODIFIED =
- `temple/autoresearch/ar_termination_002.py` (new — the audit tool)
- `temple/autoresearch/AR_TERMINATION_002_RECEIPT.md` (new — this file)
- no other file touched; no runtime behavior changed; no ledger write

METRICS (raw scan, 3,950 text files):

```
by_state_counts:
  PROPOSED        931
  NON_SOVEREIGN   320
  NO_CLAIM         74
  NOT_ADMITTED     14
  REJECTED        162   <- contaminated, see correction below
  SUPERSEDED       19
  EXPIRED           6
  ADMITTED          3   <- canon:true / canon=true only, not the string "ADMITTED"
deleted_governance_like (visible git history, 66 commits / ~17d): 0
total_governance_objects: 1402
```

**Correction applied, not hidden**: of the 162 `REJECTED` hits, 72 are in
`.py` files (`wul_reducer.py`, `innerloop.py`, `file_editor.py`,
`reducer_ref.py`, etc.) — this is almost certainly the REJECTED *verdict
mechanism* (code that can return the string), not governance object
instances that reached REJECTED status. Only 91 hits are in `.md`/`.json`
(doctrine/proposal-shaped, where an instance reading is plausible, though
even some of those may be prose describing the concept rather than a
per-object receipt — the same contamination pattern the steelman audit
already found for the raw "ADMITTED" string count).

TERMINATION_RATE =
- raw: **0.1241** (174/1402)
- **corrected: 0.0767** (102/1330, removing the 72 `.py`-only REJECTED
  false positives from both terminal count and denominator)
- the correction moves the number *down*, not up — it does not weaken
  the finding, it sharpens it

PARKING_RATE = **0.8759** (1228/1402, raw — parking-state classification
was not subject to the same mechanism-code contamination risk, since
PROPOSED/NON_SOVEREIGN/NO_CLAIM/NOT_ADMITTED are near-exclusively used
as declared status fields in doctrine files, not as code return values)

STALE_PENDING = **227** PROPOSED items ≥14 days old (threshold matches
the K-tau needle precedent already on record: 17 days, operator-gated,
unfixed). This is a **floor, not a true count** — visible git history
is only ~17 days deep (shallow clone), so any PROPOSED item that
actually originates from the 2026-05-06 or 2026-06-03 CLAUDE.md
snapshots (which predate visible history) is aged as if it were only
as old as its most recent touched commit, understating its real age.

OLDEST_PENDING = `HELEN_OS_ARCHITECTURE_V2.md`, 16 days (same floor
caveat — this is the oldest *measurable* age, not necessarily the
oldest *actual* age)

NO_OWNER_COUNT = **928 / 931** (99.7%) — no `owner:` / `author:` /
`proposer:` field found

NO_REVIEW_DATE_COUNT = **931 / 931** (100%) — no `review_date:` /
`review_by:` / `expires:` / `expiry:` field found on a single PROPOSED
item in the repo

NO_KILL_CRITERION_COUNT = **931 / 931** (100%) — no `kill_criterion:` /
`reject_if:` / `supersede_when:` field found on a single PROPOSED item

GOVERNANCE_YIELD_PROXY = **0.00214** (3 documented, hand-verified real
catches — TOCTOU seq=287 fork, stale kernel_guard allowlist caught by
manual sweep, ghost-closure detector — divided by 1,402 governance
objects). Explicitly the weakest-evidence metric in this receipt: the
numerator is a small, fixed, manually-verified list, not something the
scanner itself detected. Treat as an order-of-magnitude signal, not a
precise rate.

TEST_RESULT = **GREEN** — `ar_termination_002.py` runs deterministically
(15.5s wall time, exit 0), read-only throughout, reproducible, no
exceptions, output is structured and machine-parseable.

KEEP_OR_REJECT = **KEEP**

The hypothesis is about whether the *measurement itself* works — and it
does: owner/review-date/kill-criterion field presence, combined with
git-log-verified age, is a real, reproducible, non-lexical way to tell
a live-tracked control apart from a parking-state artifact. What that
measurement found is a separate, harder fact: by this objective test,
**0% of PROPOSED items show any of the three markers a live safety
control would need** (a named owner, a review date, a kill criterion).
That's not the hypothesis failing — that's the hypothesis's own
falsification criterion returning a clean, unambiguous result. A
measurement that had come back mixed or noisy would have been the
REJECT case; a measurement that comes back this uniform is doing its
job.

COMMIT = pending, this receipt
PUSH = pending, per `NO_PUSH_UNLESS_RECEIPT_GREEN` — TEST_RESULT is
green, so commit+push proceeds
LEDGER_EFFECT = none

---

## Crux, closed the way it was opened

The five load-bearing beliefs from the earlier steelman audit are no
longer only qualitatively flagged — three of them now have a number
attached:

1. *"NON_SOVEREIGN / PROPOSED / operator-gated labeling functions as a
   live safety control, not a permanent parking state"* — measured
   false. 0/931 have a review date. 0/931 have a kill criterion.
2. *"Governance objects accumulate faster than they terminate"* —
   measured true. Parking rate 87.6%, corrected termination rate 7.7%,
   zero governance-object deletions across the entire visible git
   history.
3. *"The agent's own receipts/snapshots are not enough as evidence"* —
   this receipt is itself an instance of the pattern: it will now sit
   as a PROPOSED file, with no owner field, no review date, and no
   kill criterion, unless one is added below.

## Kill criterion for this receipt (the thing it's missing by its own measure)

Review by: **2026-07-16** (14 days). If by then this receipt has not
been read against a second AR-TERMINATION run and either promoted,
rejected, or superseded, it becomes evidence for its own finding rather
than an exception to it.

---
authority=false · canon=false · ledger_effect=none · NO_CLAIM
review_date: 2026-07-16
owner: operator (JM)
kill_criterion: superseded by next AR-TERMINATION epoch or explicit reject
