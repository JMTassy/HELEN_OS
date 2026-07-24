# FRICTION 1 RUNBOOK — two-device ledger diff

```yaml
artifact:   LEDGER_FORENSICS_RUNBOOK_V1
friction:   #1 of FRICTION_PROTOCOL_V1 (the one that can still say no)
authority:  false · canon: false · ledger_effect: none
tool_state: built, self-tested 6/6 against planted divergences
run_state:  ONE OF THREE DEVICES CAPTURED (this container). Two remain.
```

## What is already done

A clean-room reference exists: `fingerprints/CONTAINER_CLEANROOM.json`,
captured from a fresh container clone of the repo.

    rows            264
    seq             0..263, monotone, unique
    final_cum_hash  d4569e442f7fdf40…
    content_sha256  b43fa33e668e7728…
    integrity       264/264 payload hashes recompute
                    264/264 cum hashes recompute
                    0 linkage breaks

This is not the operator's iMac or MacBook — it is a third, independent
checkout. That makes it useful as a neutral referee: if iMac and MacBook
disagree, this fingerprint says which one drifted from a clean clone.

## What you run (two commands, one per device)

From the repo root **on the iMac**:

    python3 experiments/helen_mvp_kernel/ledger_forensics/ledger_fingerprint.py \
        --label IMAC > /tmp/imac.fingerprint.json

From the repo root **on the MacBook**:

    python3 experiments/helen_mvp_kernel/ledger_forensics/ledger_fingerprint.py \
        --label MACBOOK > /tmp/macbook.fingerprint.json

Both are **read-only**. Neither writes to `town/` or any sovereign path —
that is asserted by a test, not a promise.

## What you run to see the answer

Bring both JSON files to one machine, then:

    python3 experiments/helen_mvp_kernel/ledger_forensics/ledger_diff.py \
        /tmp/imac.fingerprint.json /tmp/macbook.fingerprint.json

Add the referee to the comparison:

    python3 experiments/helen_mvp_kernel/ledger_forensics/ledger_diff.py \
        experiments/helen_mvp_kernel/ledger_forensics/fingerprints/CONTAINER_CLEANROOM.json \
        /tmp/imac.fingerprint.json

## What the report will tell you

The differ prints, per ledger: row counts, raw/content/final-cum hashes,
**the first divergent seq**, and a classified suspicion. The classifier is
conservative — it names the narrowest explanation the evidence supports
and says UNKNOWN rather than guessing.

Verified classifications (each one planted and caught in the test suite):

| Planted | Reported |
|---|---|
| identical copy | `NO_DIVERGENCE_DETECTED` |
| payload edited at seq N | `FIRST DIVERGENT SEQ: N (payload_hash, exact)` + `PAYLOAD_DRIFT` + `TAMPER_FLAG` |
| 3 events truncated | `ROW_COUNT_DIFFERS` + first missing seq named |
| CRLF line endings | `BYTES_DIFFER_CONTENT_IDENTICAL` — "not a ledger fork" |

The device block also diffs platform, python version, float repr, file
encoding, TZ, git HEAD and dirty state — the usual suspects when two
"identical" clones stop agreeing.

## A bug this instrument had, and what it taught

First version shipped the **stored** `payload_hash` in the per-seq map. A
payload edited *without* updating its hash field was then invisible to the
cross-device diff — it only showed up as a vague local self-inconsistency,
with no seq named. Found by planting the mutation and watching the differ
fail to locate it.

Fixed by shipping the **recomputed** hash, plus a `tamper` flag where
stored and computed disagree. That change is what makes the difference
between "something is wrong somewhere on device B" and "seq 100, payload
edited after its hash was written."

Recorded because it is the friction law again, one level down: the
instrument was wrong, and only running it against a known answer said so.

## Correction to FRICTION_PROTOCOL_V1

That artifact stated `ledger_replay.py` does not exist on this lineage.
It does — as `helen_os/state/ledger_replay_v1.py`, versioned, in a
different directory. The claim was made from a `find` on the exact name.
Corrected here per Law 5; the protocol file's note stands as written with
this correction attached.

## What is still unknown

Whether the two real devices agree. Nobody knows yet — including the
operator. That is the entire point of friction #1, and it is still
outstanding until those two commands run on hardware that is not this
container.
