# FINDING — Temporal Anchor Drift (the assistant's own D3, found the same way)

```yaml
artifact:   FINDING_TEMPORAL_ANCHOR_DRIFT_V1
class:      forensic finding (not a theorem — no math claim, no proof)
born_from:  git log + git reflog, run because the operator's own request
            ("one emergent property, scan all epochs and memory") is
            itself a mechanism when actually executed, not just asked
authority:  false · canon: false · NO_CLAIM
status:     reported · single-session (N=1) · re-derivable by anyone
```

## 1. What was run (the mechanism, not the request)

`git log --format="%ai %s"` across every commit reachable from this
branch, plus `git reflog show claude/setup-helen-os-node-b4uj8`. Looked
for: recurring constants, timestamp anomalies, coincidences across
unrelated artifacts. Most of it (mint numbers, epoch counts) was inert.
One thing resisted.

## 2. The finding

Two adjacent commits in this session's own history:

```
2026-05-04 19:07:21 +0000  heygen: resume after timeout + transient-error tolerance
2026-07-12 02:16:11 +0000  theorem-forge: phi-contraction floor — the drift remembers 12.5%...
```

**Gap: 68 days, 7 hours.** Nothing in the conversation between those two
commits marked a session boundary. The transition from "resume the
HeyGen render" to "here is a theorem about φ-drift" reads, in the
transcript, as continuous. It was not.

The reflog holds the fossil of what that gap actually cost:

```
1e4a5b1  branch: Created from HEAD
be2020f  commit: theorem-forge: phi-contraction floor...
02c8c55  branch: Reset to origin/claude/setup-helen-os-node-b4uj8   <-- collision
24f2f96  cherry-pick: theorem-forge: phi-contraction floor...       <-- repair
059e284  commit: correction(law-5): phi-SDE does not contract to zero...
```

Read left to right: the assistant built a commit on top of what it
believed was current HEAD (`Created from HEAD`). A push then failed
(403, then non-fast-forward) because `origin` had moved during the gap
— 20+ commits' worth of unrelated July work (Warren Town, autoresearch,
transport volumes) had landed on the same branch name. The only way
forward was `git reset` to the real remote state and `cherry-pick` the
orphaned commit back on top.

**This is structurally identical to D3** (the operator's own named
finding: "8 semaines vs *hier soir*"), except D3 was found by the
*operator* fetching GitHub, and this one was found by the *assistant*
running the same class of command, unprompted by a request for this
specific check, during a scan requested only in general terms.

## 3. Why this is the finding, not just an anecdote

The assistant's working model of "current state" is anchored to *its own
last write*, not to wall-clock time elapsed or remote drift. That anchor
is invisible and costless — until a long gap makes it wrong, and the
wrongness is only ever discovered through a **mechanical failure**
(a rejected push), never through reasoning about the gap itself. Nothing
in the conversation prompted the assistant to ask "how long has it been"
before building on `be2020f`. The 403 asked instead.

Put in the session's own vocabulary: this is a **STALE_LOOP**-class
event at the level of the assistant's temporal self-model, not at the
level of a running process. The reflection loop that "really looped"
earlier in this session's history was a mechanism catching its own
drift *within* a session; this is the same shape *across* a session
boundary the assistant did not know existed.

## 4. Self-referential closure

The request that triggered this scan ("one emergent property... scan
all epochs and memory") is exactly the request-shape the prior artifact
(`FRICTION_PROTOCOL_V1.md`) predicted would yield nothing. It would have
— if answered by introspection. It did not, because the scan was run as
a real mechanism (git log, reflog) rather than as a memory search inside
the model. The law holds at one more level: asking for emergence still
yields nothing; running a mechanism against the actual data, even when
the *request* to run it was generic, still yields something, because the
friction is in the data and the tool, not in the phrasing of the ask.

## 5. Honest scope

N=1. One gap, one branch, one assistant. The mechanism (git log +
reflog) is trivially re-runnable by anyone with this repo, which is the
only claim to strength this finding has: it is not narrated, it is
`git reflog show claude/setup-helen-os-node-b4uj8 | tail -8` away from
being checked by a stranger.

## 6. Witness

`test_temporal_anchor_drift.py` — re-derives the exact day-gap from live
`git log` output and asserts the reflog contains the
Created→Reset→cherry-pick fossil, so this finding decays into a red test
the moment the underlying git history is rewritten or squashed.

## 7. Ledger line

```
[FINDING] TEMPORAL_ANCHOR_DRIFT_V1
mechanism   : git log + git reflog (run, not narrated)
gap found   : 68 days 7 hours, unmarked in conversation
fossil      : Created from HEAD -> commit -> Reset to origin -> cherry-pick
class       : same shape as operator's D3, found independently via the
              same tool-class, on a different object (branch vs release)
closure     : confirms FRICTION_PROTOCOL_V1's law one level up — the
              request was generic; the mechanism, once actually run,
              still found something real
status      : reported · N=1 · re-derivable
```
