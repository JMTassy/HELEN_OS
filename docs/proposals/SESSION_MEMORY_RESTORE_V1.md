# SESSION_MEMORY_RESTORE_V1

**authority:** false
**canon:** NO_SHIP
**lifecycle:** PROPOSAL (boot-wiring awaits seal; read-only demonstrator already landed)
**admitted:** false
**drafted_by:** GOBLIN
**drafted_at:** 2026-06-07T14:44:08Z
**tree:** `claude/launch-helen-os-0xZXH`
**fixes:** operator report "HELEN loses memory between 2 sessions"
**parent:** `docs/architecture/HELEN_MULTI_DEVICE_CONTINUITY_V0.md` §I2 (replay-on-boot)

---

## §1. The bug (confirmed from live evidence)

Interactive HELEN boots report **"replayed 0 sessions, hash=00000000."** Memory is
written to the ledger every turn but **never replayed into state on boot.** Every
session starts cold (session #0). Verified in this tree:

```
tools/helen_cli.py       → replay/restore calls: 0
tools/helen_simple_ui.py → replay/restore calls: 0
tools/helen_telegram.py  → replay/restore calls: 0
tools/helen_ui.py        → replay/restore calls: 0
```

The write half works; the read half is disconnected. The ledger remembers; the boot
doesn't ask.

## §2. Proof the memory is recoverable (already landed, read-only)

`tools/helen_session_restore.py` (committed with this proposal) reads the live
`town/ledger_v1.ndjson`, verifies the V0 chain, and reconstructs the thread. Run
against the real ledger:

```
chain integrity: OK (226 entries, V0)
restorable turns: 112
seals: 1
>>> A correct boot replays 112 turns, NOT 'session #0'.
>>> Memory IS in the ledger. The boot just never asked.
```

**112 turns of conversation are in the ledger right now.** The boot ignores all of
them. The demonstrator is read-only — it proves the mechanism without touching any
boot path.

## §3. The fix (boot-wiring — awaits seal)

Add a restore step to the interactive boot, before the first prompt:

```python
# at interactive boot:
entries = load_entries(LEDGER_PATH)
ok, n, _ = verify_chain(entries)          # integrity gate — refuse on break
if ok:
    state = reconstruct_thread(entries)   # threads, last-k turns, head cum_hash
    # seed the chat context with restored state instead of session #0
```

The reader/verifier/reconstructor already exist in `helen_session_restore.py`. The
wiring is: call them at boot, seed context from the result.

## §4. Constraints

- **Integrity gate:** if the chain is broken, restore REFUSES (no partial/garbled
  restore). Better a clean cold start than a corrupted memory.
- **Read-only on the ledger:** restore never writes. Writing remains the
  helen_say/ndjson_writer path (see `LEDGER_WRITER_UNIFICATION_V1`).
- **Scheme:** V0, matching the verified ledger. Do not assume V1.
- **Format note:** the say-ledger holds `user_msg`/`turn` events, not the
  decision-ledger `{"entries":[{decision}]}` shape. `reconstruct_thread` maps the
  former; do NOT call `ledger_replay_v1.replay_ledger_to_state` on the say-ledger
  (different format — would mis-read).

## §5. Why this is the keystone for multi-device

Per `HELEN_MULTI_DEVICE_CONTINUITY_V0` §I2: replay-on-boot is what makes every device
the same HELEN. Without it, every device is session #0 — three amnesiac twins. With
it (plus one shared ledger via git, plus Gate 8 on every terminal), the twins become
one mind. This proposal is the read half; `LEDGER_WRITER_UNIFICATION_V1` is the write
half.

## §6. What landed vs what awaits

- **Landed (read-only, no seal needed):** `tools/helen_session_restore.py` —
  demonstrator, verified against the 226-entry ledger.
- **Awaits seal (boot-path edit):** wiring restore into the interactive boot
  (`tools/helen_cli.py` and/or the Mac `boot.py` once relayed).

---

## Halt boundary

**Status:** HALTED — demonstrator landed; boot-wiring awaits operator seal.

**Required to resume:**
1. Operator seal to wire restore into `tools/helen_cli.py` boot.
2. For the Mac CLI: relay `boot.py` + `helen_cli.py` so the same wire (restore +
   integrity gate) can be ported there — it is the device reporting "session #0."

**The demonstrator already proves it: 112 turns are recoverable from the ledger today.
The fix is to make boot call what this script just called.**
