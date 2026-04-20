---
name: conquest/magick_kernel_v1/RUNTIME_SPEC
description: CONQUEST MAGICK runtime doctrine. Tick flow, gate enforcement, contestation rules, TERRENOIR defense, chronicle writer. Consumes the kernel grammar; does not amend it. Separated from grammar so the kernel stays minimal.
helen_faculty: KERNEL / RUNTIME
helen_status: DOCTRINE (calibrated 2026-04-20; not yet INVARIANT)
helen_prerequisite: conquest/magick_kernel_v1/KERNEL_SPEC (this file consumes that grammar)
---

# CONQUEST MAGICK — Runtime Spec v1

**Class**: Runtime loop. Consumes `KERNEL_SPEC.md` grammar. Enforces gates. Writes chronicle. Never edits grammar; never introduces new symbols.

---

## 1. Tick — the 7-step loop

One tick = one acte. Deterministic.

1. **READ** — accept raw acte string (UTF-8, stripped)
2. **PARSE** — delegate to `parser.parse(line)` → `(valid, parsed, reason)`
3. **GATE_NULL** — if `valid=False`, halt; emit `NULL(reason)` chronicle line, no state change
4. **GATE_SPIRALE** — if MANDAT is 🌀 and `state.TENSION ≥ 8`, halt; emit `NULL(spiral_cap)`, no state change
5. **APPLY** — compute deltas per `KERNEL_SPEC §3`, enforce OUTIL/SEAL modifiers, clamp each axis to [0, 10]
6. **CHRONICLE** — write one line: `tick={n} acte={line} valid={bool} deltas={dict} state={dict}`
7. **RETURN** — new state dict

No I/O hidden in any step. No randomness. No network. Pure function of (state, line) → state'.

---

## 2. Gate enforcement rules

### 2.1 Grammar gate (step 3)
Any violation of the canonical production rule → NULL. Examples:
- Missing `/` separator
- Non-whitelisted symbol in any position
- OPUS count outside [1, 2]
- Multiple MANDATs, multiple RESULTs

### 2.2 Spiral cap gate (step 4)
`🌀 SPIRALE` is chaos — it cannot compound beyond a ceiling. If entry TENSION ≥ 8, the spiral move is null-and-void. State does not change. Chronicle logs the attempted-but-capped acte.

Rationale: chaos is an accelerant, not a superpower. Without a ceiling, a single spiral chain collapses the whole state.

### 2.3 Blood-oath gate (enforced in step 5, via parser)
`⸸ CROIX-SANG` without `⚰ CERCUEIL` → parser rejects at grammar level. You cannot swear blood without accepting irreversibility.

### 2.4 Parchment tax (enforced in step 5)
`📜 PARCHEMIN` halves positive deltas (floor 1) but always yields KNOW +1. Speaking is cheap in magnitude but always produces some understanding.

### 2.5 State clamping
After deltas, each axis clamped to `[0, 10]`. A move that would push COH below 0 pushes it to 0, not negative. Overflow is silent; the chronicle still shows the raw attempted delta.

---

## 3. TERRENOIR — the defense clause

`🜃 TERRE` (earth) is the stabilizer. When used as OPUS:

- Nullifies `🌀 SPIRALE` TENSION +1 (ground cancels chaos)
- But does **not** nullify spiral cap check — if TENSION is already ≥ 8, the spiral move still cannot fire

This is the only cross-axis interaction in v1. All other OPUS symbols have neutral interaction with MANDAT.

---

## 4. Contestation

There is no contestation protocol in v1. The tick is pure, deterministic, and one-sided (single-agent).

Multi-agent acte resolution, simultaneous tick, turn ordering — all are **future extensions**, not v1 semantics. If two agents want to act on the same state, the runtime linearizes them by external timestamp; no rollback, no merging.

---

## 5. Chronicle format

One line per tick. Plain text. No emoji in the mechanical fields (emoji allowed inside `acte=...` as the acte content itself):

```
tick=<int> acte=<str> valid=<bool> deltas=<json> state=<json>
```

Example:
```
tick=1 acte=✝️ 🜃 🛡️ ⚰ / 🧱 valid=True deltas={"COH":1} state={"COH":6,"KNOW":5,"SEC":5,"TENSION":1}
```

Per WULmoji enhancer doctrine: chronicle is byte-canonical mechanical text. **No color-grading glyphs** in chronicle. Those are for narrative render only.

---

## 6. Starting state (canonical)

For demo / test / deterministic tick:

```python
{"COH": 5, "KNOW": 5, "SEC": 5, "TENSION": 1}
```

This is not enforced by the kernel — any starting state is valid. But the 12-move canonical corpus is evaluated against this starting state for reproducibility.

---

## 7. What this file is NOT

- Not a renderer — no PNG, no video, no Telegram send
- Not a chronicle persister — it defines the line format; where it lands (stdout, file, ledger) is a separate concern
- Not an overlay — no cathedral, no sigils, no color
- Not an authority — NO RECEIPT = NO CLAIM still applies; this spec does not grant sovereign weight to tick output

Tick output is a **non-sovereign sidecar** until a HELEN-side process routes it through `helen_say.py` and binds a receipt.

---

## 8. One-line summary

> Tick = parse → gate NULL → gate SPIRALE → apply deltas → clamp → chronicle. Pure function. No overlay leaks in.
