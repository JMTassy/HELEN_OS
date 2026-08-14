# ⎈ CLAIM AUDIT — HAIKU SWARM RECEIPT — 2026-08-14

authority=false · canon=false · ledger_effect=none
VISION: no banner without a re-derivable receipt.
SWARM: 4 × Haiku, mechanical single-purpose auditors, parallel.

## G1 — SUITE + GATE vs TIP CLAIMS → MATCH

actual_tests=917 · probes 82/82 · CONSTITUTION_HELD · receipt
65e58753… IDENTICAL on two consecutive runs (determinism witnessed).
Every numeric claim in the tip commit message re-derived and matched.

## G2 — COMMIT REFERENCES IN research/*.md → 0 FABRICATED

One true git hash cited (66836cb) — RESOLVES(commit). Seven other
hex candidates are all 16-char Gmail thread IDs from the UZIK
receipts (three of them opened first-hand in this session), correctly
typed LIKELY_GMAIL_ID rather than MISSING-as-fraud. No fabricated
commit banner exists in this repo's research lane.

## G3 — PII SWEEP OF research/ → CLEAN

0 emails · 0 phone numbers · 0 person names near client context ·
2 money figures, both non-confidential (one labeled ILLUSTRATIVE in
DOCTRINE_V1, one a token budget). Zone law held.

## G4 — V0 CANON (goblin-warren) → INTACT

node selftest.js index.html: exit 0, 29/29 assertions. Both REDUCER
markers present. Worktree clean at tip 00824f3.

## VERDICT

Four claim classes re-derived from the system itself; zero
discrepancies. The fabricated-banner incident reported from the
local lane has NO counterpart in this repo. Honest census note: the
suite defines 882 test functions which parametrize to 917 collected
passing tests — both numbers are real, they count different things.

Cost: 4 Haiku agents, ~138k subagent tokens total, ~1.5 min wall.

## AMENDMENT — TYPED PER-CLAIM TABLE (operator ruling: receipt
integrity becomes kernel-level; encoded in receipt_integrity.py)

Aggregation is BY CLASS, never by vote. Timeline note: the operator's
"G3 PENDING / PARTIALLY_DISCHARGED" grading was correct at writing
time; G3 landed clean afterwards, closing the last class.

| claim | type | derivation recipe | observed | scope | status |
|---|---|---|---|---|---|
| "917 tests green" | C_test | `python -m pytest helen_os/kernel/constitution -q` | 917 passed | suite=constitution · checkout=helen-conquest · commit=tip at run · env=py3.11 container · gate=v82 | PASS |
| "gate 82/82 · receipt 65e58753" | C_gate | `python -m helen_os.kernel.constitution` ×2 | 82/82 CONSTITUTION_HELD · receipt byte-identical | same as above | PASS |
| "commit refs in research/ resolve" | C_commit | type first, then `git cat-file -t` on GIT_HASH-typed only | 66836cb→commit · 7 hexes typed GMAIL_THREAD_ID, not run through git | repo=helen-conquest · research/*.md | PASS |
| "NO_PII in research/" | C_pii | 4-class pattern sweep | 0 email · 0 phone · 2 figures (ILLUSTRATIVE/technical) · 0 names | research/ only; vault & chat out of scope | PASS |
| "V0 canon intact" | C_canon | `node selftest.js index.html` + marker grep | exit 0 · 29/29 · 2 markers · clean worktree | repo=goblin-warren · tip=00824f3 | PASS |

    per-class: C_test PASS · C_gate PASS · C_commit PASS ·
               C_pii PASS · C_canon PASS
    verdict:   DISCHARGED (by class, not by vote)

ReDerivable !=> UniversallyValid: every PASS above is scoped to the
checkout and environment named in its row, at run time only.

## STANDING LAW (from the incident)

Any "sealed/committed" sentence from any lane is graded
FABRICATED_UNTIL_WITNESSED unless accompanied by:
    git log -1 --format='%h %s'   AND   git status --short (empty)
A hash you can `git cat-file` is a receipt; a banner is typography.
