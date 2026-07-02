# Executor Burn-on-Failure + Registry TOCTOU — Proposal

```yaml
schema: REVIEW_FINDING_PROPOSAL_V1
authority: false
canon: false
ledger_effect: none
status: PROPOSED
owner: unassigned -- needs operator confirmation
review_date: 2026-07-16
kill_criterion: superseded by an operator decision (fix / accept-as-is / defer) or deleted if not reviewed by review_date
source: docs/proposals -- previously a two-line report-only note in CLAUDE.md
        (2026-07-01 snapshot), verified against live code this pass, not
        re-stated from memory
verified_against: helen_os/executor/bounded_executor_v1.py, read directly this session
```

## What was previously known

CLAUDE.md's 2026-07-01 snapshot noted, in one clause: *"executor
burn-on-failure + registry TOCTOU (`bounded_executor_v1.py:311`)"* —
flagged report-only, operator decision pending, no further detail.

## What this pass verified on the actual code

Two distinct, related bugs in `helen_os/executor/bounded_executor_v1.py`:

### 1. Burn-on-failure (confirmed, `BoundedExecutor.execute`, lines 375-404)

```python
if not self.registry.register(execution_identity):   # line 375 -- burns the identity
    ...
    return decision, result, None

decision = self._allow_decision(...)
artifact, output, failure_code, post_state_hash = handler.execute(...)   # line 382 -- may fail
...
if failure_code:                                       # line 401
    ...
    return decision, result, None    # identity already burned, no way back
```

`registry.register(execution_identity)` runs and permanently persists the
identity to disk **before** the handler runs at all. If `handler.execute()`
subsequently returns a `failure_code` — for any reason, including a
transient one — the execution identity is already consumed. Any
legitimate retry attempt with the same identity is rejected as
`duplicate_execution` at line 375-378, even though nothing actually
succeeded and nothing was actually written.

**Failure scenario**: an operator (or an automated caller) submits a
WRITE request that computes a deterministic `execution_identity` from
its inputs. The handler fails for a transient, retryable reason (e.g. a
lock contention, a temporary I/O error inside `handler.execute()` — the
specific handler implementations weren't audited this pass, see "what's
still open" below). The operator fixes nothing, retries with the same
inputs (same identity), and is told `duplicate_execution` — permanently,
since the persisted registry file (`registry_path`) never expires an
entry. The only workaround is changing the input in some way that
changes the computed identity, which may not be possible or may be
semantically wrong (the operator wants to retry the *same* operation,
not a different one).

### 2. Registry TOCTOU (confirmed, `ExecutionRegistry.register`, lines 311-325)

```python
def register(self, execution_identity: str) -> bool:
    if execution_identity in self._seen:        # line 312 -- UNLOCKED read
        return False
    self._seen.add(execution_identity)          # line 314 -- UNLOCKED write
    if self._persist_path is not None:
        ...
        with open(self._persist_path, "a", ...) as f:
            fcntl.flock(f, fcntl.LOCK_EX)        # line 319 -- ONLY the disk write is locked
            ...
```

`self._seen` is an in-memory Python `set`, populated once at `__init__`
from whatever was on disk at that moment (lines 296-309), and never
re-synced from disk afterward. The check-and-add on `_seen` (lines
312-314) has no lock around it at all — only the subsequent disk append
is `flock`-protected.

**Failure scenario**: two `BoundedExecutor` instances in two separate
processes, both constructed with the same `registry_path`. Both start
with an in-memory `_seen` reflecting the file's state at their own
`__init__` time. A caller submits the same `execution_identity` to both
processes at nearly the same time. Both processes independently check
`execution_identity in self._seen` (each sees "not present," since
neither has the other's in-flight write), both add it to their own
in-memory set, and both proceed to execute — the dedup guarantee the
registry exists to provide is defeated. The disk file ends up with two
entries for the same `execution_identity` (the `flock` prevents
*corrupted* writes, but does not prevent *duplicate* ones), and two
handler executions ran for what was supposed to be exactly one.

This matters specifically because `BoundedExecutor` is describable as
running under multiple concurrent callers (the whole point of an
execution *registry* is dedup across more than one caller) — a
single-process, single-caller deployment would never exercise this path.

## What's still open (not verified this pass, scope for a follow-up)

- Whether any `HANDLERS` implementation (`WriteHandler`, `EditHandler`,
  `AnalyzeHandler`, `RouteHandler`) can fail for a **retryable** reason
  in practice, or whether all their failure modes are actually
  permanent/non-retryable (in which case burn-on-failure might be
  intentional, not a bug) — this pass read `RouteHandler.execute` only
  (lines 275-283, which cannot fail — it has no failure path at all),
  not the other three handlers.
- Whether `BoundedExecutor` is actually deployed with more than one
  process sharing a `registry_path` anywhere in the current system, or
  whether the TOCTOU is a live risk vs. a latent one given current
  deployment topology.

## Candidate fixes (not applied — proposal only)

1. **Burn-on-failure**: move `registry.register(execution_identity)` to
   after a successful `handler.execute()`, or add an explicit
   "provisional reservation, confirm on success / release on failure"
   two-phase registration. The second is more correct for the TOCTOU
   fix too (see below) but is a larger change.
2. **TOCTOU**: guard the `_seen` check-and-add with the same lock that
   guards the disk write — e.g. hold `fcntl.flock` for the whole
   check-and-add-and-persist sequence, not just the file write. This
   also requires re-reading the on-disk tail under the lock before the
   check (the same TOCTOU-closing pattern already used elsewhere in
   this repo — `tools/ndjson_writer.py`'s fix for the original seq=287
   fork, per CLAUDE.md's Layer 2 section) rather than trusting a
   possibly-stale in-memory `_seen`.

Both fixes are additive/surgical — neither requires a schema change or
touches the sovereign firewall. Neither has been applied; this document
is the proposal, not the fix.

---
authority=false · canon=false · ledger_effect=none · PROPOSED
owner: unassigned -- needs operator confirmation
review_date: 2026-07-16
kill_criterion: superseded by an operator decision or deleted if not reviewed by review_date
