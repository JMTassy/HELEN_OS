---
name: conquest/magick_kernel_v1/KERNEL_SPEC
description: CONQUEST MAGICK canonical grammar. Whitelisted alphabet, single production rule (ACTE), deterministic delta semantics. Kernel stays smaller than lore — runtime and overlay live in sibling files, never inside the parser.
helen_faculty: KERNEL / GRAMMAR
helen_status: DOCTRINE (calibrated 2026-04-20; not yet INVARIANT)
helen_prerequisite: none (self-contained grammar)
---

# CONQUEST MAGICK — Kernel Spec v1

**Class**: Sovereign grammar layer. This file defines the **only** strings the reference parser accepts. Everything else — tick flow, contestation, chronicle, cathedral visuals, emoji overlay — lives elsewhere.

> *Le parseur n'exécute que la grammaire canonique. Tout le reste est overlay non gouvernant.*

---

## 1. Governing law

```
ACTE := MANDAT OPUS{1,2} OUTIL{0,1} SEAL{0,1} "/" RESULT
```

- Exactly **one** MANDAT (intent)
- **One or two** OPUS (matter)
- **Zero or one** OUTIL (instrument)
- **Zero or one** SEAL (modifier)
- Mandatory `/` separator
- Exactly **one** RESULT (outcome)

Any string that does not match this production is **rejected**. The parser returns `(valid=False, reason=...)`. No ambiguity, no "close enough," no retries.

---

## 2. Canonical alphabet (v1 — locked)

The four positional whitelists. Each symbol maps to one and only one class.

### 2.1 MANDAT — the will (intent vector)

| Glyph | Name | Meaning |
|---|---|---|
| ✝️ | CROIX | duty, guard, protection |
| 🌹 | ROSE | love, persuasion, seduction |
| 🌀 | SPIRALE | chaos, disruption, wild move |

### 2.2 OPUS — the matter (substrate, element)

| Glyph | Name | Meaning |
|---|---|---|
| 🜂 | FEU | fire — attack, burn, break |
| 🜄 | EAU | water — flow, dissolve, heal |
| 🜁 | AIR | air — communicate, reveal, drift |
| 🜃 | TERRE | earth — stabilize, fortify, ground |
| ⚗ | QUINTESSENCE | ether — transmute, synthesize |

### 2.3 OUTIL — the instrument (action verb)

| Glyph | Name | Meaning |
|---|---|---|
| ⚔️ | ÉPÉE | strike, confront |
| 🛡️ | BOUCLIER | defend, absorb |
| 📜 | PARCHEMIN | speak, declare, record |
| ⸸ | CROIX-SANG | sacrifice, bind, blood-oath |

### 2.4 SEAL — the modifier (cost/commitment marker)

| Glyph | Name | Meaning |
|---|---|---|
| ⚰ | CERCUEIL | irreversible, burial, finality |

### 2.5 RESULT — the outcome (delta target)

| Glyph | Name | Meaning |
|---|---|---|
| 🏰 | FORT | security / structure |
| 🧱 | MUR | structure / defense |
| 🌑 | OMBRE | loss / erosion |
| 🧠 | ESPRIT | knowledge / understanding |
| ❤️ | COEUR | bond / love |

Nothing outside these five lists is valid in its position. WULmoji overlay glyphs (🔴🟠🟡🟢🔵🟣⚪⚠️🎬📦📊🔁✍️🚀) are **explicitly not** kernel symbols — they are style grading, not grammar.

---

## 3. Delta semantics

The kernel tracks four scalar state variables:

| Var | Range | Name |
|---|---|---|
| COH | 0–10 | coherence (security, structural integrity) |
| KNOW | 0–10 | knowledge (understanding, clarity) |
| SEC | 0–10 | bond (love, trust, connection) |
| TENSION | 0–10 | chaos pressure (disruption, uncertainty) |

RESULT → delta mapping (applied to initiator's state, deterministic):

| RESULT | Δ |
|---|---|
| 🏰 FORT | COH +2 |
| 🧱 MUR | COH +1 |
| 🌑 OMBRE | COH −2, TENSION +1 |
| 🧠 ESPRIT | KNOW +2 |
| ❤️ COEUR | SEC +2 |

### 3.1 Seal modifier

If `⚰` is present, the cost doubles on the **worst-affected** axis:

- 🏰, 🧱 with ⚰ → COH change unchanged but cost is irreversible (logged: `irreversible=true`)
- 🌑 with ⚰ → COH −2 becomes COH −4 (doubled)
- 🧠 with ⚰ → KNOW +2 becomes KNOW +3 (bounded gain; +1 tax applied to TENSION)
- ❤️ with ⚰ → SEC +2 becomes SEC +3 (bounded gain; +1 tax applied to TENSION)

### 3.2 MANDAT modifier

| MANDAT | Effect |
|---|---|
| ✝️ CROIX | no additional modifier (baseline) |
| 🌹 ROSE | RESULT applied to SEC if ambiguous; +1 SEC bonus if RESULT is ❤️ |
| 🌀 SPIRALE | TENSION +1 always; gate: **if TENSION ≥ 8, acte is NULL** (runtime enforces) |

### 3.3 OUTIL modifier

| OUTIL | Effect |
|---|---|
| ⚔️ ÉPÉE | amplifies negative RESULT (🌑 becomes COH −3) |
| 🛡️ BOUCLIER | dampens negative RESULT (🌑 becomes COH −1) |
| 📜 PARCHEMIN | halves magnitude of positive RESULT (Δ → Δ/2, floor 1); gate: **forces KNOW +1 regardless** |
| ⸸ CROIX-SANG | requires ⚰ (parser rejects if missing); adds TENSION +1 on top of seal cost |

### 3.4 Determinism

Same acte applied to same starting state produces **byte-identical** output. No randomness. No model choice. The parser and tick function are pure.

Per K-tau `mu_DETERMINISM`: identical input → identical state → identical chronicle line.

---

## 4. What is NOT in the kernel

The kernel deliberately excludes:

- Cathedral geometry / visual layout
- Crypto-sigil encoding (`#3A7F...` hashes)
- WULmoji color-grading (🔴🟢 etc.)
- Narrative templating ("HELEN invokes...")
- Character voice / personality rendering

These live in **`oracle_town/skills/ops/wulmoji_enhancer/`** (overlay) or downstream render skills. The parser never sees them.

> *Le kernel doit rester plus petit que le lore.*

---

## 5. Admission status

**DOCTRINE** — calibrated 2026-04-20. Not yet INVARIANT.

Promotion requires:
- Fresh-session parser replay proves determinism on the 12-move canonical corpus
- `helen_say.py` receipt binding this spec's SHA256 to the ledger
- K2 / Rule 3: proposer ≠ validator
- K-tau mu_DETERMINISM gate passes on the reference tick

Until then: cite as "CONQUEST MAGICK kernel spec v1, operator-calibrated 2026-04-20."

---

## 6. One-line summary

> An acte is MANDAT + OPUS(×1–2) + OUTIL(?) + SEAL(?) + "/" + RESULT. Nothing else enters the parser. Deltas are deterministic. Overlay is not grammar.
