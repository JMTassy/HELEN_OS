# AUTORESEARCH EPOCH E010 — RECEIPT (commit is the sole head-advance point)

🔵 OBSERVED · NON_SOVEREIGN · authority=0 · not admitted · no ledger effect
Loop: HELEN°FABLE supervision · relayed meditation → ONE verifiable bug in committed code @ d2a6beb

## 7-field receipt

- **carry_forward_state**: E008 established Committed(τ) as a derived predicate; E009 added a
  single GovernedStore head. Both advanced the head inside execute() via _advance().
- **hypothesis (relayed, then falsified)**: execute() advancing the head is a real bug —
  EXECUTED ⊬ COMMITTED, so the head must not move to a computed-but-uncommitted post-state.
- **experiment**: Fable probed committed code directly — prepare→execute (no evidence/commit),
  then read store.head() and is_committed().
- **metric**: after execute-without-commit, is the authoritative head at the pending post (G1)
  while nothing is committed?
- **result — BUG CONFIRMED, FIXED**: probe showed head=G1 while is_committed=False and
  replay_committed=[] — the ambiguous half-state E008 forbids (G_head=G_post yet ¬Committed).
  Fix: execute() computes tx.post_state_hash ONLY (pending); commit() advances the head, exactly
  once, guarded by a compare-and-swap (head must still equal tx.pre_state_hash, else STALE_PRE_STATE).
  Now: before commit head=pre, after commit head=post; G_head=G_post ⇒ Committed. Interleaved
  txs serialize at commit (first wins, second refused stale). 168→174 tests; legacy no-store path
  fixed identically.
- **keep/reject rule**: KEEP. Real defect in shipped code, invariant-restoring fix, all layers green.
- **HONEST NOTE — the process caught its own miss**: E009 shipped a test
  (test_e009_head_advances_only_via_execute) that ASSERTED the buggy behavior as correct — it
  encoded "execute advances the head." Nine epochs of peer review passed it because the tests and
  the code agreed on the wrong invariant. It took an external meditation naming EXECUTED ⊬ COMMITTED
  to expose it. E010 corrects BOTH the code and that test. Lesson: a green test that encodes the
  wrong law is a vacuous witness — the exact hazard the HAL Witness Law warns about, here realized
  in the transaction layer's own test. Documented, not hidden.
- **upgrade_path / RESIDUAL**: in-memory CAS; the durable atomic state+receipt+marker boundary
  (one transactional storage commit) is the production form — E008's deferred substrate, unchanged.
  External-effect (ΔW) mutation still needs reconciliation, not this internal head discipline.

## Fable supervision note — "keep meditating until you found ONE"
The operator asked for ONE genuine thing from a vast relayed meditation. The ONE was not a new
doctrine — it was a real defect in already-committed, already-peer-reviewed code, plus a test that
had blessed it. Falsified against the runtime, fixed, and the self-blessing test corrected. Neither
the meditation's claim nor E009's own green test was trusted until recomputed against the kernel.
