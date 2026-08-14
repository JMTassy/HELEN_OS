# ⎈ CROSS-LANE VERIFICATION — the local lane's library, re-derived here

authority=false · canon=false · ledger_effect=none · 2026-08-14
First inter-seat receipt where EVERY claim class discharged. The
local lane claimed; this seat re-derived. Grade: VERIFIED.

## THE CLAIMS AND THEIR RE-DERIVATIONS

| claim (local lane) | class | recipe run here | observed |
|---|---|---|---|
| 5 commits on origin (ffdcb18, b80cab8, 06ce326, 3ca3a6d, de96107) | C_commit | type-first, then git cat-file -t each | 5/5 resolve as commits |
| head == de96107 on claude/doctrine-proposals | C_commit | git ls-remote | EXACT match |
| charisma_airlock = 2 files | C_commit | git show --stat | 2 files, 124 insertions |
| "gated 6/6" charisma | C_test | pytest at de96107 worktree | 6 tests present, pass |
| "26-test audit suite" | C_test | pytest charisma+roots+graph_ir at de96107 | **26 passed** — 6+11+9, to the digit |

VERDICT (by class, never by vote): C_commit PASS · C_test PASS ·
library = VERIFIED, not REPORTED.

## OUT-OF-SCOPE FINDING, flagged not laundered

Their FULL suite at de96107 from this seat: 316 passed, 1 skipped,
2 FAILED — both in tests/test_surface_grammar.py::TestRealSurface
(a real-file scan, environment-dependent, OUTSIDE the claimed
5-commit library). Scope law: the 26-test claim holds; the full-tree
claim was never made and would not hold from this seat unmodified.

## THE LAW MAP (their lane ↔ this lane, factored not merged)

- their I₆ (warrant rebind) ≙ this engine's I₅ — same law, numbering
  divergence already recorded in HANDOFF_RECONCILIATION
- epistemic_roots "citations ⊬ witnesses" ≙ this lane's
  E_PROXY_IS_NOT_A_ROOT / coder_common_mode family — convergent,
  independently built, one day apart
- charisma_airlock "prestige ⊬ authority" ≙ this lane's
  confidence_admits_nothing + E_REPUTATION_IS_NOT_AUTHORITY —
  the non-amplification channel, third costume
- their cross_model_independence harness ≙ this lane's referee module
  — the frozen QID discipline on both sides

Two engines, two lanes, one law family — and now the FIRST bridge
where the receipts crossed in both directions: their laptop can
cat-file this repo's tips; this seat just re-derived their library.

RECEIPTS_NOT_BANNERS = DEMONSTRATED_CROSS_SEAT
