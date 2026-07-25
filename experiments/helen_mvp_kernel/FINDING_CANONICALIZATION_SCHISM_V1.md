# FINDING — Canonicalization Schism (payload_hash is not well-defined repo-wide)

```yaml
artifact:   FINDING_CANONICALIZATION_SCHISM_V1
class:      forensic finding (measured, re-derivable) — not a theorem
born_from:  pointing the FRICTION-1 instrument at the 32 ledgers it had
            never been aimed at. 16 of 19 chained ledgers failed. The
            failure was not corruption — it was a convention fork.
authority:  false · canon: false · NO_CLAIM
status:     reported · operator seal pending
```

## 1. The headline

    payload_hash = sha256(canon(payload))

is stated in `tools/helen_say.py` and echoed across the corpus as *the*
canonical rule. But `canon` has **two incompatible implementations living
in this repository right now**, and they are used in roughly equal measure.

    A.  json.dumps(o, sort_keys=True, separators=(",",":"), ensure_ascii=False)
    B.  json.dumps(o, sort_keys=True, separators=(",",":"))      # ensure_ascii defaults TRUE

A emits UTF-8. B emits `\uXXXX` escapes. On pure-ASCII payloads they are
byte-identical. On any payload containing an accent, an emoji, or a
WULmoji glyph they produce **different bytes and therefore different
hashes**.

## 2. Measurements (AST-parsed, 1030 python files)

Canonicalizer-shaped `json.dumps` calls (`sort_keys` + `separators` both set):

| form | call sites |
|---|---|
| explicit `ensure_ascii=False` (A) | **64** |
| omitted → defaults True (B) | **61** |
| explicit `ensure_ascii=True` (B) | **16** |

**64 vs 77.** Not a stray legacy call — a near-even split.

Against real ledger data (349 payloads across 32 `.ndjson` files):

    payloads where A and B produce different hashes:  42 / 349  (12.0%)

Against the sovereign ledger specifically (`town/ledger_v1.ndjson`, 264 rows):

    validates under A (ensure_ascii=False):  264 / 264
    validates under B (ensure_ascii=True):   225 / 264
    events a wrong-convention validator would REJECT:  39  (14.8%)
    first rejected seqs: 8, 19, 21, 23, 33, 37, 39, 41, 115, 117, 121, 123

The sovereign ledger is **internally consistent** — it was written with A
and validates perfectly under A. The hazard is not corruption. It is that
a validator written on side B is *also* self-consistent, and would declare
39 valid sovereign events invalid.

## 3. Why this hid for so long

The divergence is **silent and data-dependent**. Any test fixture written
in plain ASCII passes under both conventions. The bug only appears on
payloads containing non-ASCII — which in this system means the payloads
carrying French text, emoji status markers, and WULmoji glyphs. The
project's own symbolic vocabulary is the trigger condition.

That is the inverse of a normal flaky test: it is a **stable pass on
synthetic data, stable fail on real data**.

## 4. Second finding, same scan: three cum_hash schemes

While resolving the above, the same sweep found the chain rule is also
forked. Empirically identified across all 19 hash-chained ledgers:

| scheme | rule | ledgers |
|---|---|---|
| **V0** (no prefix) | `sha256(prev_bytes ‖ payload_bytes)` | `town/ledger_v1.ndjson` (264), `town/ledger_v1_SESSION_20260223.ndjson` (15), `town/ledger.ndjson` |
| **HELEN_CUM_V1** | `sha256(b"HELEN_CUM_V1" ‖ prev_bytes ‖ payload_bytes)` | `genesis_ledger_v1_0_1` (3), `synthetic_ledger_v1_0_1` (5), `town/ledger_v1_HELEN_CUM_V1_GENESIS` (3), `town/test_env_sovereign_writer` (1) |
| **ledger_v2** | UNRESOLVED — schema has **no `prev_cum_hash` field**; chain is implicit | 12 files under `helen_os_scaffold/storage/` |

`HELEN_CUM_V1` is self-documenting — its genesis row carries
`hash_scheme_spec: "SHA256(b'HELEN_CUM_V1' || prev_bytes || payload_bytes)"`
and `total_input_bytes: 76` (= 12 + 32 + 32), which is how it was cracked.
That is good practice and the other two schemes lack it.

The `ledger_v2` rule resisted ~30 candidate reconstructions and remains
**open** — an honest UNRESOLVED, not a guess.

## 5. Consequence

There is no single validator in this repository that can verify every
ledger in it. Each existing checker is correct for its own family and
would report false ANOMALY on the others. That was demonstrated directly:
the FRICTION-1 instrument, committed one hour before this scan, knows only
V0 + convention A, and reported **16 of 19 chained ledgers as anomalous** —
a false-alarm rate of 84%, from a tool whose own test suite was 6/6 green.

The tool was not wrong about the bytes. It was wrong about how many laws
this corpus has.

## 6. What this does NOT claim

- No claim that any ledger is corrupt. Every family is self-consistent.
- No claim about which convention is "correct" — that is an operator/MAYOR
  decision, not a forensic one.
- No claim that `ledger_v2`'s rule is unsound; only that it was not
  recovered here.
- N = one repository, one snapshot. Re-derivable, not generalized.

## 7. Recommended next moves (operator's call, not taken here)

1. **Declare the canon.** One `canon()` in one module; every other call
   site imports it. The choice matters less than the singularity.
2. **Self-describing headers.** Adopt `HELEN_CUM_V1`'s practice repo-wide:
   every ledger's row 0 states its own `hash_scheme_spec`. Then no future
   validator has to guess, and this finding cannot recur.
3. **Non-ASCII fixtures.** Every hash test should include one emoji and one
   accented payload. That single fixture would have caught this years ago.
4. Recover or retire the `ledger_v2` chain rule.

## 8. Witness

`test_canonicalization_schism.py` — re-derives every number above from
live repo state (AST parse for call-site counts, live ledger reads for
divergence rates). Decays to a red test if the schism is ever repaired,
which is the correct behavior: **the test failing means the problem is
fixed**, and it says so in its own assertion messages.

## 9. Ledger line

```
[FINDING] CANONICALIZATION_SCHISM_V1
measured   : 64 call sites ensure_ascii=False vs 77 effectively True (AST, 1030 files)
             42/349 corpus payloads hash differently under the two
             39/264 sovereign events rejected by a wrong-convention validator (14.8%)
             3 cum_hash schemes across 19 chained ledgers; 1 unresolved
mechanism  : aimed the FRICTION-1 instrument at 32 never-checked ledgers
consequence: no single validator in the repo can verify every ledger in it;
             the instrument's own 84% false-alarm rate is the proof
trigger    : non-ASCII payloads — the project's own symbolic vocabulary
status     : reported · N=1 · re-derivable · operator seal pending
```

*The rule was one line long and everyone implemented it correctly. Twice.*
