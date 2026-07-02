# Fire-and-Forget Ledger Bridge — Proposal

```yaml
schema: REVIEW_FINDING_PROPOSAL_V1
authority: false
canon: false
ledger_effect: none
status: PROPOSED
owner: unassigned -- needs operator confirmation
review_date: 2026-07-16
kill_criterion: superseded by an operator decision (fix / accept-as-is / defer) or deleted if not reviewed by review_date
source: docs/proposals -- previously a one-line report-only note in CLAUDE.md
        (2026-07-01 snapshot), verified against live code this pass, not
        re-stated from memory
verified_against: helen_api_server_v1.py, tools/helen_say.py, tests/test_executor_ledger_bridge.py, read directly this session
```

## What was previously known

CLAUDE.md's 2026-07-01 snapshot noted, in one clause: *"fire-and-forget
ledger bridge (`helen_api_server_v1.py:95`)"* — flagged report-only,
operator decision pending, no further detail.

## What this pass verified on the actual code

One bug with two distinct failure surfaces in
`helen_api_server_v1.py:_route_executor_receipt()` (lines 98-127).

### 1. Silent loss of ledger receipts (confirmed, lines 118-124)

```python
subprocess.Popen(
    [sys.executable, str(_REPO_ROOT / "tools" / "helen_say.py"), envelope, "--op", "dialog"],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
    cwd=str(_REPO_ROOT),
)
return True  # fired; ledger write confirmed asynchronously by the kernel
```

`subprocess.Popen` spawns `helen_say.py` and immediately returns — no
`wait()`, no `poll()`, no callback, no process handle retention. Both
`stdout` and `stderr` are routed to `DEVNULL`. The function returns
`True` ("fired"), but "fired" is not "confirmed."

If `helen_say.py` subsequently exits non-zero — because the kernel
daemon is down (`sys.exit(1)` at `helen_say.py:207`), the message is
empty (`sys.exit(2)` at `helen_say.py:203`), or any runtime error
occurs — there is **zero feedback to the API server**. Not a log line,
not a metric, not an error response. The receipt silently vanishes.

**Failure scenario**: the kernel daemon (`kernel_daemon.py`) is not
running, or the socket file `~/.openclaw/oracle_town.sock` does not
exist. An operator calls `POST /actions/execute` with a valid WRITE
request. The `BoundedExecutor` succeeds — the file is created in the
sandbox, the executor receipt is issued, the HTTP response is `200
SUCCESS`. `_route_executor_receipt` spawns `helen_say.py`, which
immediately detects the missing socket, prints a BLOCK verdict to
`/dev/null`, and exits 1. The executor receipt envelope never reaches
the sovereign ledger. The operator sees a successful action but the
governance layer has no record of it.

This directly violates `NO RECEIPT = NO CLAIM`: the action happened,
but the receipt didn't — and nobody knows.

### 2. Return value is never consumed (confirmed, line 309)

```python
_route_executor_receipt(decision, result, artifact)   # line 309 — return value discarded
```

The function returns `bool`, but the call site (the `/actions/execute`
handler at line 309) discards it as a bare statement. Even when the
function correctly returns `False` (on spawn failure, line 127, or
non-SUCCESS result, line 106), nothing in the system acts on it.

The tests (`test_executor_ledger_bridge.py`) verify that:
- The bridge IS called on success (test line 95: `Popen.assert_called_once()`)
- The bridge is NOT called on failure (test line 128: `Popen.assert_not_called()`)
- Spawn failure doesn't propagate to HTTP (test line 139: status still 200)

But no test verifies that the *child process succeeded* — every test
mocks `subprocess.Popen` and checks only that it was called, never
what happened after.

### 3. Docstring is correctly honest but behaviorally insufficient (confirmed, lines 99-104)

The docstring says "Best-effort" and "Failure is logged and never
propagated." This is accurate for spawn-level failures (the `except` at
line 125 does log). But "best-effort" for a governance receipt bridge is
a design choice that trades reliability for latency — the HTTP response
returns immediately without waiting for the kernel. Whether that
trade-off is acceptable depends on how many executor actions happen per
day and what the consequences of a missed receipt are.

## What's still open (not verified this pass)

- **Actual frequency**: how often is `POST /actions/execute` called in
  production? If the answer is "rarely, always with operator
  supervision," fire-and-forget may be acceptable in practice — the
  operator would notice the missing receipt. If the answer is "by
  automated callers, frequently," it's a real gap.
- **Kernel uptime**: how reliably is the kernel daemon running when the
  API server is running? If they're always co-deployed and co-started,
  the "socket missing" scenario is unlikely. If they're independently
  managed, it's a live risk.
- **Existing monitoring**: whether any external system (log aggregator,
  health check) would surface the `helen_say.py` exit code 1 from
  another angle, making the DEVNULL routing less dangerous than it
  appears in isolation.

## Candidate fixes (not applied — proposal only)

1. **Minimum viable: log the outcome.** Replace `subprocess.Popen`
   (fire-and-forget) with `subprocess.run` (wait for exit code) or
   retain `Popen` but call `.wait(timeout=N)` and log the exit code.
   `stderr` should route to a log handler, not `DEVNULL`. This doesn't
   change the HTTP response latency if done in a background thread, but
   at least makes silent loss visible in server logs.

2. **Reliable bridge: synchronous with timeout.** Use
   `subprocess.run(timeout=5)` and include the bridge outcome in the
   HTTP response body (e.g. `"ledger_bridge": "OK"` or
   `"ledger_bridge": "FAILED: kernel not running"`). The caller then
   knows the receipt status. The HTTP latency increases by the
   `helen_say.py` round-trip time.

3. **Reliable bridge: async with retry.** Spawn a daemon thread or
   asyncio task that calls `helen_say.py`, retries on transient failure
   (up to 2 strikes, per the bounded-retry axiom), and logs the final
   outcome. The HTTP response returns immediately (same latency as now)
   but the retry covers transient kernel unavailability. This is the
   most correct fix but the largest change.

4. **Consume the return value.** Regardless of which bridge fix is
   chosen, the `/actions/execute` handler should use the return value:
   ```python
   bridged = _route_executor_receipt(decision, result, artifact)
   # include in response body:
   "ledger_bridge": "OK" if bridged else "FAILED"
   ```
   This gives the caller visibility without changing the bridge
   mechanism itself.

All fixes are additive/surgical — none requires a schema change or
touches the sovereign firewall. None has been applied; this document
is the proposal, not the fix.

---
authority=false · canon=false · ledger_effect=none · PROPOSED
owner: unassigned -- needs operator confirmation
review_date: 2026-07-16
kill_criterion: superseded by an operator decision or deleted if not reviewed by review_date
