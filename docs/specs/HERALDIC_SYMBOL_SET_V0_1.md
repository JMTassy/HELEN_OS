---
name: HERALDIC_SYMBOL_SET_V0_1
version: "0.1"
status: LOCKED
classification: CANONICAL_OVERLAY
authority: false
sovereign: false
executive: false
layer: TEMPLE / CONQUEST / EMOWUL
proof_required: true
max_glyphs_per_line: 9
random_sigil_noise: FORBIDDEN
date_locked: 2026-06-15
related:
  - docs/specs/WULMOJI_LEXICON_V0_1.json
  - docs/specs/WUL_PACKET_SPEC_V0_1.md
  - helen_os/knowledge/symbolic_sources/SYNCHRETIC_SYMBOLIC_SOURCE_01_EMOWUL_V1_DOCTRINE_DRAFT.md
---

# Heraldic Symbol Set V0.1

Overlay language for CONQUEST / EMOWUL / DREAM_OF_CONQUEST rendering.
This is a **non-executive overlay**: symbols may depict sovereignty, veto,
and governance, but cannot imply the render shell has authority.

> Semantic continuity may be cross-device. Authority is not.

---

## 1. Canonical Symbol Set

| Glyph | Name | Semantic Domain |
|---|---|---|
| ✝️ | TEMPLIER | oath / veto / frontier / duel |
| 🌹 | ROSICRUCIAN | transmutation / inner work / initiation |
| ⟂◯⟂ | MASONIC | measure / architecture / governance |
| 🌀 | CHAOS | risk / drift / friction / entropy |
| 🜃 | ground | anchor / matter / base |
| 🜄 | dissolve | ego-loss / flow / release |
| 🜁 | lift | abstraction / clarity / air |
| 🜂 | cut | ignition / pressure / severance |
| 🜍 | engine | tension / impulse / drive |
| 🜔 | body | fixity / embodiment / form |

All glyphs are semantically typed. Usage outside their domain is INVALID.

---

## 2. Heraldic 5-Layer Format

```
[BANNER] [SIGIL] [ALCHEMY] [ACTE] [PROOF] [RIBBON]
```

Strict slot semantics:

| Slot | Class | Semantic |
|---|---|---|
| BANNER | affect / state | severity or mood color: 🟣 🔴 🟢 ⚫ 🟡 |
| SIGIL | faction / archetype | ✝️ 🌹 ⟂◯⟂ 🌀 |
| ALCHEMY | transformation | operator pair: 🜍⚗️ 🜂⚔️ 🜃🏰 🜁🜄 |
| ACTE | action class | 📜 🔒 🛡️ ⚠️ — the act performed |
| PROOF | receipt / anchor | 🔗#TAG — the chain anchor |
| RIBBON | final seal / mood | closing tag: ✨🜍 🔒⚰️ 🏰📜 ⚠️🌀 |

No slot may be omitted in a canonical line. A line missing PROOF is INVALID.

---

## 3. Hard Laws

```
1. NO RECEIPT = NO CLAIM
2. NO PROOF = NO MAGIC
3. NO RANDOM SIGIL NOISE
4. MAX 9 GLYPHS PER LINE
5. NO AUTHORITY GLYPH WITHOUT ROLE BOUNDARY
```

**Law 5 explained:** A line may depict sovereignty, veto, or governance
as narrative/game content. It cannot imply the render shell or agent
emitting the line has executive authority. The Heraldic layer is an
OVERLAY — it describes events, not verdicts. Verdicts belong to the
sovereign layer (MAYOR → Reducer → Ledger).

---

## 4. Valid Examples

```
🟣 🌹 🜍⚗️ 📜 🔗#INIT ✨🜍
```
Rosicrucian initiation; engine/transmutation operative; document act;
initiation proof anchor; completion seal.

```
🔴 ✝️ 🜂⚔️ 🔒📜 🔗#VETO 🔒⚰️
```
Templar veto; pressure/cut operative; locked document act;
veto receipt anchor; closure/death seal.

```
🟢 ⟂◯⟂ 🜃🏰 🛡️ 🔗#WALL 🏰📜
```
Masonic governance; grounded fortress operative; protection act;
wall receipt anchor; fortress-document seal.

```
⚫ 🌀 🜁🜄 ⚠️📜 🔗#DRIFT ⚠️🌀
```
Chaos/drift event; abstraction-dissolving operative; warning document act;
drift receipt anchor; entropy tag.

---

## 5. Invalid Examples

```
🌹🌀✝️🜂🜄🜁✨🔥🏰⚔️👁️
```
**REJECT:** sigil noise exceeds 9 glyphs; no proof; no clear act; mixed domains.

```
✝️ 🔥 SHIP
```
**REJECT:** authority claim without receipt; prose not glyphs.

```
🌀 ✨ MAGIC DONE
```
**REJECT:** no proof, no act, no receipt, prose contamination.

```
👑 SOVEREIGN LEDGER ✅
```
**REJECT in render-shell/UI context:** authority leakage (Law 5).
Depiction of governance is allowed; claim to be the governance authority is not.

---

## 6. CONQUEST / EMOWUL Integration

For DREAM_OF_CONQUEST game-state heraldic receipts, map to:

```
[MOOD] [FACTION] [OPERATOR] [ACTION] [ANCHOR] [SEAL]
```

**Border duel:**
```
🔴 ✝️ 🜂⚔️ 🛡️ 🔗#BORDER 🔒
```
Red alert · Templar frontier · cut/pressure · defense · border receipt · locked.

**Inner transformation:**
```
🟣 🌹 🜄🜔 📜 🔗#EGO 🕯️
```
Rosicrucian · dissolution into form · documented ego-loss · candle receipt.

**Governance architecture:**
```
🟢 ⟂◯⟂ 🜃📐 🏛️ 🔗#MEASURE ✅
```
Masonic · grounded architecture · institution act · measured receipt · validated.

**Drift warning:**
```
⚫ 🌀 🜍⚠️ 📜 🔗#DRIFT 🛑
```
Chaos drift · engine tension · warning document · drift receipt · stop seal.

---

## 7. Relation to WULmoji

The Heraldic set and WULmoji v0.1 are **orthogonal systems**:

| System | Layer | Purpose |
|---|---|---|
| WULmoji v0.1 | inter-agent semantic communication | token class/arity/AST/hash |
| Heraldic V0.1 | narrative / visual overlay | mood/faction/action/proof rendering |

Heraldic lines are NOT WUL packets and are NOT hashed as payload_hash.
A Heraldic line may CONTAIN a WUL receipt reference (the PROOF slot `🔗#TAG`)
but the line itself is visual language, not machine-validated grammar.

To emit a receipted Heraldic event, the proof anchor must reference a
real receipt hash or WUL packet hash — not a decorative tag.

---

## 8. Relation to EMOWUL Doctrine

`SYNCHRETIC_SYMBOLIC_SOURCE_01_EMOWUL_V1_DOCTRINE_DRAFT.md` is the
upstream emotional WUL extension (DRAFT, symbolic_sources).
The Heraldic V0.1 set is a **downstream overlay spec**: it formalizes
the visual grammar for CONQUEST/DREAM use without promoting the EMOWUL
draft to canon. If EMOWUL V1 is promoted via MAYOR receipt, the Heraldic
set will be reconciled at that time.

---

## 9. Lock Declaration

```
HERALDIC_SYMBOL_SET_V0_1 = LOCKED
STATUS                    = CANONICAL_OVERLAY
AUTHORITY                 = NON_EXECUTIVE
PROOF_REQUIRED            = TRUE
MAX_GLYPHS_PER_LINE       = 9
RANDOM_SIGIL_NOISE        = FORBIDDEN
AUTHORITY_GLYPH_WITHOUT_ROLE_BOUNDARY = FORBIDDEN
LEDGER_MUTATION           = forbidden
CANON_MUTATION            = forbidden
SOVEREIGN                 = false
```

---

```
CLAIM_TYPE: spec
AUTHORITY: false
SOVEREIGN: false
CANON: false
LAYER: TEMPLE / CONQUEST
```
