# LEDGER_WRITER_UNIFICATION_V1

**authority:** false
**canon:** NO_SHIP
**lifecycle:** PROPOSAL (awaiting operator seal before any implementation)
**admitted:** false
**proposer:** GOBLIN (non-sovereign operational persona)
**drafted_at:** 2026-06-07T05:06:55Z
**tree:** `claude/launch-helen-os-0xZXH`
**closes:** `docs/frontiers/NEXT_FRONTIER_ISSUE_V1.md` §3 — `LedgerAppend` + `ReplayOK`
**supersedes_recommendation_in:** `docs/frontiers/HORN_B_LEDGER_CHOKEPOINT_AUDIT_V1.md` §5 option 2(a)

---

## §0. Correction notice (read first)

Throughout this session GOBLIN recommended "route `helen_say.py` through
`ndjson_writer.py` to get HELEN_CUM_V1 for free." **That recommendation
was wrong, and this proposal corrects it.**

The correction came from an artifact-grounded check, not memory:
computing the genesis cum_hash of the live ledger and verifying the full
chain. Result:

```
genesis payload_hash: ef6e2f8387204c17...
actual cum_hash:      8cc12f5148d60ffd6a7dc63947bdeec6fb1f46b70f605ab451372f8cf3945d53
V0 computes:          8cc12f5148d60ffd... ✓ MATCH
V1 computes:          a0854f21cf302029... ✗
chain check:          ALL 226 ENTRIES CONSISTENT under V0
```

**The live ledger `town/ledger_v1.ndjson` is V0 (`CUM_SCHEME_V0`),
end-to-end, all 226 entries.** The environment declaration of
`HELEN_CUM_V1` is drift that was **never actually applied** to this
ledger. Switching the writer to V1 would compute V1 over a V0 chain and
**orphan every existing entry.** This is itself a STATE_AUTHORITY_GAP
instance: the registry *declares* V1; the ledger *is* V0; the prior
recommendation trusted the declaration over the artifact.

---

## §1. The three defects (all verified, one cluster)

Per `HORN_B_LEDGER_CHOKEPOINT_AUDIT_V1` (`92b1915`) plus the §0 finding:

1. **Scheme declaration ≠ ledger reality.** `registries/environment.v1.json`
   declares `hash_scheme: HELEN_CUM_V1`; the ledger and `helen_say.py:71-84`
   are `CUM_SCHEME_V0`. `ndjson_writer.py`, reading the environment, would
   write V1 — breaking the chain if it ever wrote to this ledger.

2. **Doctrine drift.** CLAUDE.md Layer 2: "`helen_say.py` → `ndjson_writer.py`
   is the only admitted path." False — `helen_say.py:281` writes directly
   with its own `open(ledger_path, "a")` and its own V0 hash
   (`helen_say.py:75`); it does not import `ndjson_writer`.

3. **GUARD_BLIND.** `kernel_guard.sh` RULE 1 requires the literal
   `.ndjson` on the `open()` line. Every real append site uses a variable
   path, so the guard matches none and passes vacuously (0 violations).

---

## §2. The constitutional constraint that decides the fix

`town/ledger_v1.ndjson` is the **append-only sovereign ledger.** Its 226
entries are V0 and chain-consistent. **Re-hashing them (to migrate to V1)
would mutate the append-only ledger — a constitutional violation.** The
ledger's existing scheme is therefore not a free variable. Any fix must
preserve all 226 entries byte-for-byte.

This eliminates the naive "migrate to V1" path. Three options remain.

---

## §3. Options

### Option A — Reconcile to truth: declare V0 (RECOMMENDED)

1. Change `registries/environment.v1.json` `hash_scheme` from
   `HELEN_CUM_V1` to `CUM_SCHEME_V0`. The environment now declares what
   the ledger actually is. `ndjson_writer` (which already supports
   `CUM_SCHEME_V0` via `get_hash_fn`) will write V0, matching the 226
   entries.
2. Refactor `helen_say.py` to write via `NDJSONWriter.append_event`
   instead of its inline `open()`+V0-hash. Since the environment now
   declares V0, the chain stays consistent. Delete `helen_say.py`'s
   `make_event` V0 hash (lines 71-84) — hashing becomes ndjson_writer's
   sole job.
3. Doctrine becomes TRUE: helen_say now genuinely routes through
   ndjson_writer. Update CLAUDE.md Layer 2 — no longer drift.
4. helen_say no longer needs to be in `kernel_guard` ALLOWED_WRITERS —
   it routes through `ndjson_writer.py`, already allowed.

**Cost:** zero migration, 226 entries preserved, append-only respected.
**Trade-off:** V0 has no domain separator. For a single sovereign ledger
this is acceptable; cross-context collision resistance is not currently
relied upon. If domain separation is later wanted, use Option C.

### Option B — Migrate ledger to V1 (REJECTED)

Re-hash all 226 cum_hashes under V1, switch writer to V1. **Rejected:**
rewriting the append-only sovereign ledger violates its core invariant.
Listed only to record that it was considered and refused.

### Option C — Scheme boundary marker (FUTURE OPTION)

Keep entries 0-225 as V0; emit an explicit boundary record at seq 226;
write seq ≥ 226 as V1; teach replay to switch schemes at the boundary.
Preserves history AND moves to domain-separated hashing going forward.
**More complex** (replay must handle the switch). Defer unless domain
separation becomes a requirement. If chosen, it is its own proposal.

---

## §4. Recommended implementation (Option A) — on operator seal only

Per the governance edit rule (CLAUDE.md, `fcd9f12`): this proposal must
be sealed before any of the following edits are made. **Nothing below is
implemented yet.**

1. `registries/environment.v1.json`: `hash_scheme` → `CUM_SCHEME_V0`.
2. `tools/helen_say.py`: replace the inline two-event `open()`+write
   (lines 280-283) and the `make_event` V0 hash (71-84) with
   `NDJSONWriter`-based appends. Preserve the existing event structure
   (user_msg ev1, kernel call, turn ev2) and the `hal` anchoring on
   ev1.cum_hash.
3. `tools/kernel_guard.sh`: harden RULE 1 — drop the literal-`.ndjson`
   requirement; flag any `open(<var>, "a"|"w")` outside ALLOWED_WRITERS
   where the path resolves to `town/`. (The GUARD_BLIND fix.)
4. `CLAUDE.md` Layer 2: confirm "helen_say → ndjson_writer" is now true;
   remove the V0/V1 divergence caveat.
5. **Verification (mandatory before commit):**
   - Re-run the §0 chain check: all 226 entries still consistent.
   - Append one test event via the refactored helen_say; confirm seq 226
     chains correctly under V0.
   - Run `kernel_guard.sh`; confirm it now flags a deliberately-planted
     rogue variable-path append (negative test).
   - Replay validation over the full 227-entry ledger passes.

---

## §5. What this unblocks

```
CleanAdmit = ... ∧ ReducerAdmit ∧ LedgerAppend ∧ ReplayOK
                       ✅            (this)         (this)
```

`ReducerAdmit` proven (`6a7a865`). With Option A:
- **LedgerAppend** — a sealed ADMITTED packet can be written to
  `town/ledger_v1.ndjson` via the single guarded V0 writer, chain-consistent.
- **ReplayOK** — one scheme (V0) across the whole ledger; replay validates.

§3 CleanAdmit closes. The first end-to-end clean admission becomes
possible: Cluster B (`6a7a865`) admitted → written → replayed.

---

## §6. Cross-runtime finding (NOT fixed here — flagged)

The operator's Mac interactive CLI (`/Users/jean-marietassy/.helen/`,
emits `HELEN_ACTION`) is **not in this tree** and has **no Gate-8
equivalent** — observed live narrating "REDUCER admits / LEDGER records /
REPLAY proves" on its own cognition (self-admission), and ingesting
broken terminal fragments as intent (FRAGMENT_AMPLIFICATION). That is the
un-governed carrier. This proposal does NOT fix it (different codebase,
not read). It is recorded here because the same membrane (single guarded
writer + no self-admission) is what the Mac CLI needs. A separate
proposal, requiring the Mac CLI source, is the path for that.

---

## Halt boundary

**Status:** HALTED — PROPOSAL drafted, awaiting operator seal.

**Required to resume (implementation of Option A):**
1. Operator seal on this proposal (selects Option A, B, or C).
2. On Option A: GOBLIN implements §4 steps 1-4, runs §4 step 5
   verification, halts again before commit with results for final seal.

**Nothing is edited until the seal. The 226-entry ledger is not touched
regardless of option — Option A changes the declaration to match it, not
the ledger to match the declaration.**
