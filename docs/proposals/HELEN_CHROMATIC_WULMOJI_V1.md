# HELEN CHROMATIC WULMOJI V1

```
type:           PROPOSAL
authority:      false
claim_status:   NO_CLAIM
parent:         HELEN_WULMOJI_MATHS.md  ·  HELEN_LANGUAGE_V1.md
final:          HOLD_FOR_OPERATOR
```

> Color is valid only when it carries a deterministic axis of meaning.
> One color = one primary meaning. No improvisation. No substitution.
> Color must be **parsed**, not felt.

---

## Extended World-Object

Three new typed fields extend the base tuple:

```
𝕎  = (S, τ, E, Π, Χ)
𝕎⁺ = (S, τ, E, Π, Χ, κ, α, σ)
```

| Field | Name | Tier |
|-------|------|------|
| κ | banner color — governance state | PRIMARY · strict |
| α | alchemical mode — transformation | SECONDARY · expressive |
| σ | sigil — domain / faction | SECONDARY · contextual |

κ governs. α and σ refine. Neither α nor σ may override κ.

---

## 1. Banner Colors — Governance State (TIER 1 · STRICT)

The primary axis. Closed palette. One meaning per color.

| κ | State | Ladder rung |
|---|-------|-------------|
| ⚫ | UNKNOWN | not yet processed |
| 🔵 | OBSERVED | surfaced · OBS |
| 🟣 | CLAIM | proposed · CLAIM |
| 🟠 | REVIEW | in tension · under review · REV |
| 🟢 | ADMITTED | pass · ADM · ◆ |
| 🟡 | SEALED | stable · hash-bound · SEAL · ⬢ |
| ⚪ | REPLAYABLE | canonical · survives ↻ · REP · ∞ |
| 🔴 | BLOCKED | invariant breach · FAIL · rejected |

**Ladder in color:**

```
⚫ → 🔵 → 🟣 → 🟠 → 🟢 → 🟡 → ⚪
                              ↑
                         🔴 at any rung = BLOCK
```

SPEC has no banner color. It lives in the Garden, before the ladder begins.

---

## 2. Sigil Registry — Domain (TIER 2 · CONTEXTUAL)

σ identifies the domain or faction. Optional. Does not affect τ.

| σ | Domain |
|---|--------|
| ✝️ | order / law-keeper / templar |
| 🌹 | heart / HER / affect / rose |
| ⟂ | neutral / structural / base |
| ◯ | void / zero / unbound |
| 🌀 | cycle / recursion / replay |
| ⸸ | compost / terminated / rejected |
| ⚜ | sovereign · MAYOR · operator-authorized |
| ⚔ | conflict / forge / active pressure |
| ✧ | elevated / passed membrane |

---

## 3. Alchemical Overlay — Transformation Mode (TIER 2 · EXPRESSIVE)

α describes *what kind of work is occurring*, not the admission state.
The color says **where the thing is**. The alchemic says **what type of work is active**.

| α | Element | Mode |
|---|---------|------|
| 🜁 | AETHER · Air | analysis / abstraction / transmission |
| 🜂 | IGNIS · Fire | force / cut / pressure / judgment |
| 🜃 | TERRA · Earth | stabilization / law / persistence |
| 🜄 | AQUA · Water | memory / flow / adaptation |
| 🜍 | IMPETUS | drive / motor / transition / F_Χ |
| 🜔 | CORPUS | fixed form / sealed body |
| ⚗️ | TRANSMUTATION | active reduction / in-progress crossing |

Examples:

```
[🟣][🜄]◇   = claim in memory/flow phase
[🟢][🜃]◆   = admitted and stabilized
[⚪][🜍]∞   = replayable and integrated
```

---

## 4. Syntax Grammar

```
[κ] [σ] [α]  OBJECT  {ACT}  🧾#HASH  <RIBBON>
```

**Parse order — always left to right:**

| Position | Slot | Required | Read as |
|----------|------|----------|---------|
| 1 | [κ] Banner | YES | governance state |
| 2 | [σ] Sigil | optional | domain / faction |
| 3 | [α] Alchemic | optional | transformation mode |
| 4 | OBJECT | YES | glyph (◌◇◆⬢∞) or WUL token |
| 5 | {ACT} | optional | action verb (📜🛡️🔒⚠️👁️⚖️🔁) |
| 6 | 🧾#HASH | conditional | mandatory when κ ∈ {🟢 🟡 ⚪} |
| 7 | <RIBBON> | optional | meta-markers (✨⚠️🌀⚰️🔒) |

**Hard rule:** an admitted, sealed, or replayable object without a proof hash
is malformed. Color 🟢/🟡/⚪ requires 🧾.

---

## 5. Canonical Examples — 10 Lines (2 per state)

### OBSERVED (🔵)

```
[🔵][✝️][🜁]◌  {👁️}  🧾#O101
[🔵][🌹][🜄]◌  {👁️}  🧾#O102
```

### CLAIM (🟣)

```
[🟣][🌹][🜄]◇  {📜}  🧾#C204
[🟣][⟂][🜁]◇  {🔍}  🧾#C205
```

### ADMITTED (🟢)

```
[🟢][✝️][🜃]◆  {⚖️}  🧾#A311
[🟢][🌹][🜄]◆  {📜}  🧾#A312
```

### SEALED (🟡)

```
[🟡][◯][🜂]⬢  {🔒}  🧾#S402
[🟡][⚜][🜔]⬢  {🔒}  🧾#S403
```

### REPLAYABLE (⚪)

```
[⚪][🌀][🜍]∞  {🔁}  🧾#R550
[⚪][⚜][🜁]∞  {🔁}  🧾#R551
```

### BLOCKED (🔴 — no proof required)

```
[🔴][⸸][🜂]◇  {⚠️}
```

---

## Note on Chakra Encoding

Chakra colors map to the same color palette as Tier 1 by coincidence of pigment,
but they describe a *different axis* (energetic / cognitive layer, not governance
state). Chakra encoding is **Tier 3 — optional, expressive, worldbuilding only**.

Rule: never use chakra readings to determine admission status.
The governance banner (κ) governs. Chakra is commentary, not authority.

When Tier 3 is active, mark the tier explicitly to avoid ambiguity:

```
[κ=🟢][T3=🟢·heart]◆   — governance admitted · heart-layer resonance noted
```

---

## Receipt Footer

```
HELEN_CHROMATIC_WULMOJI_V1

file           = docs/proposals/HELEN_CHROMATIC_WULMOJI_V1.md
claim_status   = NO_CLAIM · authority = false
ledger_effect  = none · kernel_effect = none
git_stage = no · git_commit = no · git_push = no
final          = HOLD_FOR_OPERATOR
```
