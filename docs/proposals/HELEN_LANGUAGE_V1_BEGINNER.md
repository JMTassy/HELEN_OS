# HELEN Language V1 — Beginner Guide

```
type:           PROPOSAL
authority:      false
claim_status:   NO_CLAIM
parent:         HELEN_LANGUAGE_V1.md
final:          HOLD_FOR_OPERATOR
```

---

## What HELEN Prevents

HELEN solves one central confusion:

```
what appears      ≠  what is true
what impresses    ≠  what is admitted
what speaks loudly ≠  what has authority
```

An idea, an image, a symbol, or a phrase can exist in the Garden.
Everything grows there freely: myths, drawings, intuitions, dreams, hypotheses.

But to enter the Ledger, it must pass through the membrane π.

```
🌿 Garden  ──π──▶  📜 Ledger
   dream              received / replayed / proven
```

---

## The Five Questions

HELEN always asks five questions about any object:

| Field | Question | Meaning |
|-------|----------|---------|
| S | What do we see? | form, image, phrase, glyph |
| τ | What is its truth status? | observed, claim, evidence, speculation |
| E | What supports it? | source, log, receipt, trace |
| Π | How can it be read? | image, myth, code, governance |
| Χ | What must remain true? | invariants, rules, guardrails |

This is the HELEN object:

```
𝕎 = (S, τ, E, Π, Χ)
```

---

## An Example

"HELEN dreams."

HELEN does not say directly: "that's true."
She translates:

```
S   = the phrase "HELEN dreams"
τ   = SPEC or CLAIM
E   = ∅  (nothing supports it yet)
Π   = poetic reading / system reading / interface reading
Χ   = HELEN does not self-authorize

Result: Garden render · NO_CLAIM · not yet Ledger
```

---

## The Truth-Status Ladder

An object moves up this ladder — **never by itself, always by passage**:

```
SPEC   →  speculative, Garden-only. Can inspire a claim.
           It cannot cross the membrane alone.
OBS    →  directly observed
CLAIM  →  proposed, not yet supported
EVID   →  supported by evidence
REV    →  reviewed by an independent party
ADM    →  admitted (operator-authorized)
SEAL   →  sealed and hash-bound
REP    →  replayable from the ledger
```

The jump is forbidden:

```
SPEC  ↛  ADM
SPEC  ↛  SEAL
SPEC  ↛  REP
```

---

## How Things Move

```
next state = current state + action + context
```

But in HELEN, this equation alone means nothing.
What matters is the constraint on how things move.

The transition must be:

```
pure          — no hidden state
replayable    — same inputs → same output, always
receipt-gated — nothing admitted without evidence
non-self-sealing — the transition cannot authorize itself
invariant-preserving — Χ must survive every tick
```

With the constraint written in:

```
x_{t+1} = F_Χ(x_t, u_t, c_t)
```

`F_Χ` = a transition already filtered by the invariants.

---

## The Core Rule

```
A thing can be beautiful in the Garden.
It becomes governed only when it is:
  qualified  (τ ≠ SPEC)
  supported  (E ≠ ∅)
  reviewed   (proposer ≠ validator)
  admitted   (operator-authorized)
  replayable (survives ↻)
```

---

## Three Things to Remember

```
𝕎 = what a thing is
F_Χ = how it moves (already constrained)
Χ = what must never break
π = the membrane that decides what crosses
```

---

## Compression

```
S without τ        =  poetry
τ without E        =  claim
E without replay   =  fragile
replay without Χ   =  mechanics
Χ preserved by F_Χ =  governance
```
