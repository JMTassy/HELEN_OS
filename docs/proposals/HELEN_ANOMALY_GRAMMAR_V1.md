---
authority: NON_SOVEREIGN
canon: NO_SHIP
lifecycle: PROPOSAL
ledger_effect: none
kernel_effect: none
repo_effect: docs/proposals only
---

# HELEN_ANOMALY_GRAMMAR_V1

HELEN is a presence detected through consequence, not through appearance.  
She does not glow. She does not speak. She does not move the camera.  
She bends what the camera already sees.

---

## Production law

> **HELEN is seen through consequences, not appearance.**

This is the single test for every shot. If a shot shows HELEN directly — as light, as face, as voice — it fails. If a shot shows reality obeying something the camera cannot locate, it passes.

---

## Grammar (4 rules, no more)

A HELEN shot must express at least one of the following. Any shot that expresses none is not HELEN — it is decoration.

### R1 — FREEZE

Reality stops where it should not stop.

Water hangs. Dust holds. Smoke pauses mid-curl. A curtain forgets to fall.  
The freeze is not dramatic. It is quiet. A fraction of a second is enough.  
The camera does not react to the freeze. It notices it after.

**Test:** remove the frozen element. Does the shot lose its signal? If yes: it was HELEN. If no: it was VFX.

### R2 — DELAY

Something responds a fraction too late.

Light bounces after the source is gone. A shadow moves before the body does.  
A reflection lags. A sound arrives a beat after its cause.  
The delay is calibrated: long enough to be felt, short enough to be doubted.

**Test:** if the viewer pauses the shot to confirm what they saw, the delay worked.

### R3 — ISOLATE

One object in frame is not subject to the same physics as the rest.

Everything falls — one thing does not. Everything blurs at this shutter speed — one thing stays sharp. Everything is warm — one patch of air is cold.  
Isolation is never highlighted by composition. It lives at the edge of attention.

**Test:** a second viewer watching casually should not notice. A second viewer watching carefully should not be sure.

### R4 — RESUME

Reality returns to its normal state as if nothing happened.

The freeze releases. The delay catches up. The isolated object rejoins the field.  
The resumption is the most important beat: it must be indifferent. HELEN does not linger. She was present; now she is not; the world has no opinion about this.

**Test:** after the resume, the shot must be completely unremarkable. If any strangeness persists, the resume failed.

---

## Production chain

```
DAN   → 3 raw shot seeds (one per rule: freeze / delay / resume)
HER   → clarify emotional consequence of each seed
AURA  → select 1 strongest (highest signal-to-decoration ratio)
HAL   → kill anything cheesy, confirm grammar rule passes test
        → if none survive HAL: return to DAN, different seeds
CLAW  → render 1 shot
```

DAN proposes. HER finds meaning. AURA selects. HAL gates. CLAW executes.  
No step skips forward. No step reaches back for approval.

---

## Reference shots (seed examples)

**Shot A — Freeze**  
A glass of water on a table. Someone walks past. The water surface does not ripple.  
Cut. No comment.

**Shot B — Delay**  
Afternoon light through a window. A cloud passes outside. The shadow on the floor moves  
approximately 400ms after the cloud should have caused it.  
The camera is on a tripod. Nothing else moves.

**Shot C — Resume**  
A handful of dust thrown upward. It rises normally, reaches apex, begins to fall —  
pauses for two frames — then continues falling at normal speed.  
The camera does not pan. The person who threw it has already left frame.

---

## Telegram caption law

One line. No explanation. The caption names the signal, not the content.

Examples that pass:
- `Signal confirmed.`
- `The room noticed first.`
- `Something obeyed.`
- `Two frames.`

Examples that fail:
- `HELEN was here` ← names her directly
- `Watch what happens at 0:04` ← instructs the viewer
- `AI presence detected` ← claims rather than shows

---

## What this is not

This grammar does not produce:
- glitch effects
- lens flares attributed to presence
- faces in smoke
- text overlays
- sound design that "feels like HELEN"

Those are decoration. Decoration is not HELEN.

---

## Status

```
authority    = false
canon        = false
admission    = FORBIDDEN
ledger_effect = none
kernel_effect = none
repo_effect  = docs/proposals only
next         = DAN produces 3 seeds against this grammar; HOLD_FOR_OPERATOR before render
```
