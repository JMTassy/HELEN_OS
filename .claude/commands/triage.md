# HELEN Daily Triage

Classify an incoming work packet — a paste, a repo status, a model
output — before acting on it. Do not execute. Do not promote. Do not
mutate the ledger.

Adapted from a pasted asset this session, with one fix: the original
proposed a fresh six-state taxonomy (ACCEPT_AS_OBSERVATION /
KEEP_AS_CANDIDATE / HOLD_FOR_WITNESS / BLOCK_FOR_AUTHORITY_LEAK /
GO_READY / ASK_OPERATOR) running alongside HELEN's locked 8-color
WULmoji palette — which has its own machine-enforced disjointness tests
(`tools/wulmoji_palette.py`, `tests/test_wulmoji_palette_disjointness.py`).
Two status vocabularies answering adjacent questions is exactly the
kind of drift this session's own audits exist to catch, so this skill
maps onto the existing palette instead of adding a second one.

## Inputs

$ARGUMENTS — the packet to classify: a paste, a reported transcript
from another seat, a model output, a repo status snapshot.

## Recipe

Return:

```yaml
HELEN_TRIAGE_RECEIPT:
  authority: false
  canon: false
  ledger_effect: none
  packet_type:
  source:               # this seat, another seat (name it), external paste, model output
  current_state:
  strongest_observation:
  blocked_actions:
  allowed_next_tokens:
  missing_witnesses:
  risk_level:
  wulmoji: "⚫|🔵|🟣|🟠|🔴"   # never 🟢🟡⚪ — those require an actual admission receipt, hash-lock, or replay
  recommended_next_token:
```

## Verdict → WULmoji mapping (the fix)

| Verdict | WULmoji | Meaning |
|---|---|---|
| ACCEPT_AS_OBSERVATION | 🔵 observed | recorded, not yet judged |
| KEEP_AS_CANDIDATE | 🟣 claim | proposed, not admitted |
| HOLD_FOR_WITNESS | 🟠 review | blocked pending evidence |
| GO_READY | 🟠 review | ready for operator to move to 🟢 — the packet never self-promotes |
| BLOCK_FOR_AUTHORITY_LEAK | 🔴 breach | policy violation, stop |
| ASK_OPERATOR | ⚫ unknown | insufficient signal to classify at all — say so, don't guess |

## Decision rules

- Paste is raw retrieval, not verified fact — a reported transcript
  from another seat is evidence about what happened there, not proof
  that it happened, until you can check it against something (a file,
  a receipt, a re-run).
- A reported commit is not metal — "I committed X" in a pasted
  transcript is not the same as `git log` showing X on this repo.
- Green tests are not semantic cleanliness — passing does not mean correct.
- A garden verdict is not canon — NO_CLAIM stays NO_CLAIM regardless of
  how confident the phrasing is.
- A skill existing is not a skill adopted — check `last_used`, not just
  presence, before trusting that a discipline is actually in use.
- External user signal outranks internal coherence — a real user's
  confusion beats an elegant internal argument every time they conflict.
- Missing observation returns `ASK_OPERATOR` / ⚫, not invented state —
  never fill a gap with a plausible guess dressed as a finding.

## Cross-seat specific rule

When the packet is a reported transcript from another seat (a
different repo, a different machine, a different harness convention):
classify it as `source: <seat name>`, and explicitly check whether
anything it proposes (a file path, a convention, a skill name) actually
matches what's verified in *this* repo before treating it as directly
applicable here. Two seats independently building the same thing with
different conventions is not a conflict to silently resolve — name the
divergence in `strongest_observation`.

## Constraints

- Never render 🟢/🟡/⚪ from this skill — it only classifies incoming
  packets, it has no authority to admit, seal, or replay anything.
- If in doubt between two verdicts, pick the more conservative one and
  say why in `strongest_observation`.
