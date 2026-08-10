# AUTORESEARCH EPOCH E005 — RECEIPT

🔵 OBSERVED · NON_SOVEREIGN · authority=0 · not admitted · no ledger effect
Loop: HELEN°FABLE vision+supervision · gemma4-12b local goblin ($0)
Target: atomicity / ghost execution (doctrine §12, "the largest new issue") @ 29527bd

## 7-field receipt

- **carry_forward_state**: κ enumerated scorecard 10/10, but invoke does
  check→consume→effect→receipt sequentially. A crash BETWEEN effect and receipt yields
  ΔG≠0 with no receipt — ghost execution, no attacker. New anti-collapse distinction
  needed: execution ≠ committed governed state (§13).
- **hypothesis**: a smallest write-ahead mechanism lets recovery DETECT a ghost.
- **experiment**: gemma4-12b proposed PREPARED-before-effect + recovery scan +
  ghost = PREPARED-without-receipt. Fable built the smallest detection form.
- **metric**: does a recovery scan flag a txn whose effect ran but receipt never committed?
- **result — WRITE-AHEAD ORDERING DEMONSTRATION (ghost-detection logic, non-durable)**:
  `intent_log.py` — PREPARE(txn, effect_hash) recorded BEFORE the effect; COMMIT only after
  receipt; `detect_ghosts()` returns PREPARED-not-COMMITTED. Crash simulated by skipping
  commit: effect ran (state changed), txn left PREPARED, recovery flags it. Write-ahead
  ORDER witnessed as load-bearing (intent after effect would be crash-invisible). 140→145 tests.
  NOT yet an "atomicity primitive" — that noun waits for the durable WAL (peer-review flag).
- **keep/reject rule**: KEEP. Real seam (§12), smallest detection form, ΔG-witnessed.
- **upgrade_path / DOCUMENTED RESIDUAL**: this is DETECTION, not PREVENTION, and the
  intent log is IN-MEMORY — a real crash would lose it. **The load-bearing consequence
  (peer-review flag, stated explicitly): the passing tests prove write-ahead ORDERING is
  correct, NOT that this artifact detects a real crash. `crash_before_commit=True` skips
  the commit call while the in-memory log survives in the same live process; a real process
  death would take the dict with it and `detect_ghosts()` would return [] — the witness dies
  with the crime.** Green here = ordering theorem, not real-crash evidence. Production form:
  an fsync'd WAL file whose entries survive the crash they witness, plus a boot-time recovery
  scan wired into the kernel — only THEN is it an atomicity primitive. Also open: automatic
  REMEDIATION of a detected ghost (compensate/replay). Named, not claimed solved.

## Fable supervision note
Different contribution class than E001–E004 (optional-field bindings on capability.py):
E005 is a write-ahead ordering demonstration (non-durable), kept OUT of capability.py per
doctrine ("do not overload κ with atomicity"). The honest boundary: in-memory detection
witnesses the LOGIC (write-ahead makes ghosts detectable IF the log survives); durable-WAL
persistence is the production step that earns the noun "primitive". Peer review shipped 6/6
literal criteria and raised two honesty flags (noun over-claim; test proves ordering not
real-crash detection) — BOTH applied to this receipt before commit rather than pocketed.
Goblin designed; Fable built smallest honest form; validator sharpened the claim; neither admitted.
