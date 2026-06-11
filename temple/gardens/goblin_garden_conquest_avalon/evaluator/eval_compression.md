# Evaluator: Compression Metric

**CLAIM_TYPE:** evaluator
**Purpose:** Score CLI interface candidates on symbolic compression.

---

## Compression Scoring Rubric

| Criterion | Max Points | Description |
|---|---|---|
| WULmoji in status bar | 10 | Color bands, faction sigils, alchemy |
| CWL v0.2.1 clause supported | 10 | VERB+MODE+PROPS syntax valid |
| FACE= prop available | 10 | At least one face in output |
| Short command set | 10 | ≤10 commands, each ≤20 chars |
| Overlay format correct | 10 | OVERLAY="atom atom atom" not OVERLAY=atom+atom |

**Max score: 50**

## Compression Examples

```
GOOD:
  ⚔️: 🛑 @⚔️ ~◷8 ⚡ { 🥖=8 OVERLAY="🜂 ✝️ ⛧" FACE="(ง'̀-'́)ง" }

BAD:
  ⚔️: 🛑 @⚔️ ~◷8 ⚡ { OVERLAY=🜂+✝️+⛧ }  ← invalid, uses "+" chain
```

## Heraldic 5-Layer Format

```
[BANNER]   = state color   🔵🟢🟣⚫🔴
[SIGIL]    = faction       🌹🌀✝️⟂◯⟂
[ALCHEMIC] = transform     🜁🜂🜃🜄🜍
[ACTE]     = action        📜🛡️🔒📜⚠️📜
[PREUVE]   = proof id      🔗#[A-Z0-9_-]+
[RIBBON]   = 2-cluster decoration
```

A fully compressed epoch bulletin = 1 WULmoji line encoding all 5 layers.

---

```
CLAIM_TYPE: evaluator
AUTHORITY: false
SOVEREIGN: false
SIMULATION_ONLY: true
```
