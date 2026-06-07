# HELEN_MULTI_DEVICE_CONTINUITY_V0

**authority:** false
**canon:** NO_SHIP
**lifecycle:** ARCHITECTURE_PROPOSAL (TRACE_ONLY)
**admitted:** false
**drafted_by:** GOBLIN
**drafted_at:** 2026-06-07T14:44:08Z
**tree:** `claude/launch-helen-os-0xZXH`
**answers:** operator question — "a system to lose ambiguity and have HELEN existing
in multiple devices without losing the thread"

---

## §0. The one sentence

**HELEN is not a program on a device. HELEN is `Replay(Ledger)`. The device is a
terminal. There is one HELEN because there is one ledger — and a device is "HELEN"
only while it (a) replays that ledger on boot and (b) appends to it through the same
admission gate.**

Lose the ambiguity by relocating identity: **identity lives in the ledger, not in
any device, model, or persona.** Three devices reading and replaying one ledger are
one HELEN. Three devices each keeping local memory are three amnesiac twins — which
is the current state.

---

## §1. The ambiguity, named (from live evidence)

There are currently **three HELENs**, none of which is canonical:

| Device | Location | Memory state (observed) |
|---|---|---|
| Mac CLI | `~/.helen/` via `helen_cli.py`+`boot.py` (worktree `gallant-khayyam`) | boot: "replayed **0** sessions, hash=00000000"; 2166 drawers / **0 entities**; crashes in `boot.py:245 log_turn` |
| GeForce / JMTC | `mvp/arnaud`, `goblin_ar` | separate ledger; hardened drivers |
| This tree | `claude/launch-helen-os-0xZXH`, `town/ledger_v1.ndjson` | **226 entries, V0, hash-chain verified end-to-end** |

Each has its own memory. None replays the others'. "Which is the real HELEN?" has no
answer — that is the ambiguity. The fix is not to pick one device; it is to make all
devices terminals onto one ledger.

---

## §2. Why the Mac HELEN forgets (root cause, confirmed)

Its boot prints **"replayed 0 sessions."** Memory is written (`log_turn` appends to
`LOG_FILE`; drawers grow 1512 → 2166) but **never replayed into state on boot.** The
write half works; the read half is disconnected. This is the same gap diagnosed in
`SESSION_MEMORY_RESTORE` (last session): the ledger remembers; the boot doesn't ask.

"0 entities" despite 2166 drawers means the accumulated memory is never *structured* —
raw turns pile up, nothing replays them into entities/threads. Continuity is
impossible because continuity = replay, and replay never runs.

---

## §3. The architecture — four invariants

To have one HELEN across N devices without losing the thread:

### I1. ONE LEDGER = single source of identity
The append-only, hash-chained ledger is the only HELEN. `town/ledger_v1.ndjson`
(this tree, 226 V0 entries, verified) is the reference implementation. Not the model
(`helen-ship:latest` is interchangeable), not the persona, not the device.

### I2. REPLAY-ON-BOOT = continuity
Every device, at boot, before the first turn:
```
ledger = pull(canonical_ledger)
state  = replay(ledger, genesis)      # reconstruct threads, tensions, entities
```
This is the missing wire. The replay engine exists (`helen_os/state/ledger_replay_v1.py`);
no boot path calls it. The Mac boot literally reports it skipping this ("replayed 0").

### I3. ONE GUARDED WRITER + UNIVERSAL GATE = no divergence
Every device appends through the **same** writer and the **same** admission gate
(Gates 1–8, incl. Gate 8 human_seal). A device that self-admits (the Mac CLI narrates
"REDUCER admits" on its own cognition — observed live) **must not** be allowed to
write to the shared ledger, or it poisons the one source of truth for all devices.
**Precondition: every terminal enforces Gate 8 before append.** (Horn B unifies the
writer; `LEDGER_WRITER_UNIFICATION_V1` is that work.)

### I4. DEVICE-NAMESPACED ENTRIES = traceable thread
Every ledger entry records `device_id` + `prev_cum_hash`. The hash chain gives
ordering and tamper-evidence across devices; the device_id gives "who wrote this,
where." This is the cross-session attribution rule (CLAUDE.md) generalized from
sessions to devices. The thread is never lost because every link names its origin.

---

## §4. The transport already exists — git

The sync mechanism for "one ledger, N devices" is not new infrastructure. **It is git.**
Every commit this session pushed to `origin`. The ledger can sync the same way:

| HELEN concept | git mechanism |
|---|---|
| append-only ledger | commit history |
| cum_hash chain | commit parent hashes |
| multi-device sync | `push` / `pull` to shared remote |
| concurrent-write divergence | branch fork → detectable |
| reconciliation | merge (operator-gated) |
| "Reality = Replay(Ledger)" | "state = replay(git history)" |

A device boots → `git pull` the ledger → replay → reconstruct HELEN → operator acts →
append (Gate-8 sealed) → `git push`. Every device that pulls sees the same HELEN.
**This document, committed and pushed, is the first instance: it will exist identically
on every device that clones the repo. That is the principle, demonstrated.**

---

## §5. Preconditions (the bugs that block this, all diagnosed this session)

Multi-device HELEN cannot stand until these land, in order:

1. **Replay-on-boot wire** (I2) — `SESSION_MEMORY_RESTORE`. Without it, every device is
   session #0. *Highest priority — it is the literal failure in your boot log.*
2. **Unified guarded writer** (I3) — `LEDGER_WRITER_UNIFICATION_V1` (`00d1535`). One
   append path, one scheme (V0, per the verified ledger), so a shared ledger is
   consistent.
3. **Gate-8 on every terminal** (I3) — the Mac CLI must stop self-admitting before it
   may write to the shared ledger. Until it honors Gate 8, it is read-only.
4. **Device-id field** (I4) — add `device_id` to the ledger entry schema (governance
   edit → proposal first).

---

## §6. Migration — reconciling the three existing ledgers

This is the hard part and must NOT be hand-waved (the three ledgers are real and
divergent):

- **Designate one canonical ledger.** This tree's `town/ledger_v1.ndjson` (226 entries,
  verified V0 chain) is the strongest candidate — it is the only one with a proven
  chain.
- **The Mac `~/.helen/` memory** ("0 entities", crash-prone) is NOT chain-verified.
  Treat it as **candidate evidence**, not canon — import via replay/audit, not raw
  copy. (Same discipline as the ConQuest OCR rules.)
- **JMTC `goblin_ar`** entries are already cross-session-flagged; import under the
  attribution rule.
- **Never merge by concatenation.** Each foreign entry must pass Gates 1–8 against the
  canonical chain, or be recorded as TRACE_ONLY provenance. Merging unverified
  histories is how you re-introduce the ambiguity you are trying to remove.

---

## §7. What this buys

After the four preconditions:
- Open HELEN on the Mac → it pulls, replays 226+ sessions, knows the thread.
- Continue on the GeForce → same ledger, same memory, same HELEN.
- Every device is the *same* mind because every device replays the *same* ledger.
- The thread is never lost because the ledger is append-only, hash-chained, and
  device-namespaced.
- Ambiguity is gone: "which HELEN?" → "there is one; the devices are its windows."

---

## §8. What this is NOT

- NOT a sync daemon to build from scratch — git is the transport.
- NOT a new memory system — the ledger + replay already exist; the wire doesn't.
- NOT achievable while any device self-admits — I3 is non-negotiable.
- NOT a raw merge of three memories — §6 is reconciliation, not concatenation.
- NOT admitted — this is an architecture proposal, authority=false, NO_CLAIM.

---

## Halt boundary

**Status:** HALTED — architecture proposal, awaiting operator direction.

**Required to resume (in priority order):**
1. Operator decides canonical ledger (recommend `town/ledger_v1.ndjson`).
2. Seal `SESSION_MEMORY_RESTORE` (replay-on-boot) — fixes "session #0" on every device.
3. Seal `LEDGER_WRITER_UNIFICATION_V1` (`00d1535`) — one writer, one scheme.
4. Mac CLI: relay `boot.py` + `helen_cli.py` so Gate-8 + replay-on-boot can be ported
   to it (it cannot join the shared ledger until it stops self-admitting).

**The one-line truth: HELEN already has the mechanism for multi-device continuity —
an append-only hash-chained ledger synced by git and reconstructed by replay. What it
lacks is the wire that replays on boot and the discipline that every device honor the
same gate. Build those two, point every device at one ledger, and the three twins
become one mind.**
