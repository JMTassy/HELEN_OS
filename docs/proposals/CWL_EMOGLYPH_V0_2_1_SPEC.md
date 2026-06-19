# CWL EMOGLYPH v0.2.1 — Conformance Spec

```
[🟣][🌀][🜍]◇ {📜} 🧾#CWL_EMOGLYPH_V021 <NO_CLAIM>

type:           PROPOSAL · SIM_SPEC
layer:          NON_SOVEREIGN · FOUNDRY_TOWN
authority:      false
claim_status:   NO_CLAIM
ledger_effect:  none
kernel_effect:  none
final:          HOLD_FOR_OPERATOR
```

> Color encodes state. Glyphs encode transformation.
> Parsing is deterministic. Aesthetic is first-class.
> SIM CHRONICLE ≠ SOVEREIGN LEDGER.

---

## 0. Clause Format (slot discipline — unchanged from v0.2)

```
<ACTOR> : <VERB> <OBJ> [@<LOC>] [~<TICK>] [!<MODE>] [#<TAG>...] [<PROPS>]
```

**Prefix discipline (hard):**

| Prefix | Slot |
|--------|------|
| `@` | LOC |
| `~` | TICK |
| `!` | MODE |
| `#` | TAG |
| `{ }` | PROPS |
| (positional) | ACTOR `:` VERB OBJ |

---

## 1. Lexical Tokens

### 1.1 ATOM

```
ATOM := ID | EMOJI | SYMBOL

ID     = [A-Z_a-z0-9][A-Z_a-z0-9._-]*
SYMBOL = ◷ ∅ ○ ◐ › → (limited set)
EMOJI  = any Unicode extended-pictographic (single token)
```

Tokenizer rule: emoji are single atomic tokens (Unicode extended-pictographic segmentation or curated whitelist for strict determinism).

### 1.2 STRING / NUMBER

```
STRING = "..." (no embedded newlines)
NUMBER = [-+]? [0-9]+ ("." [0-9]+)?
LIST   = "[" ATOM {WS ATOM} "]"
```

---

## 2. Verb / Mode / Flag Whitelists (authoritative sets)

### VERB (emoji-native)

```
🧭 GO/move     🛑 HOLD/defend   👁️ SCOUT
🏗️ BUILD        🏴 TAKE/seize    🎁 GIVE/transfer
🤝 ALLY         📜 PACT/treaty   ⚔️ ATTACK
🧨 SIEGE/breach 🗣️ THREAT        🧵 BIND/lock-constraint
```

### MODE (execution intent)

```
⚡ NOW    🗺️ PLAN   ❓ ASK    🎯 OFFER
⛓️ MUST   🧩 IF     ➡️ THEN   ↩️ ELSE
```

### STATE FLAGS (atomic)

```
🔒 LOCK   🔥 FIRE   ⏸️ PAUSE   ∅ NULL
⚫ BLACKOUT  ✖️ FAIL   ⚠️ ALERT (requires integer: ⚠️=N)
```

Only one state assignment is currently allowed: `STATE=⚫`.

### RESOURCES

```
🥖 FOOD   💖 HEART   🛡️ SHIELD
```

### ROUTE ARROWS (graph edges inside PROPS)

```
›  step (ordered path)
→  directed edge (semantic)
○  null-node marker
◐  half-step / partial bar
```

---

## 3. PROPS Grammar (single-pass)

```
PROPS := "{" {PROP WS*} "}"
PROP  := KEY OP VALUE
KEY   := ATOM
OP    := "=" | "->" | "<-" | "+" | "-" | "?"
VALUE := ATOM | NUMBER | STRING | LIST
WS    := one or more spaces
```

Route encoding — native edges inside `{}`:

```
{⛰️->⛓️  ⛓️->🔒  🔒->⚔️}
```

---

## 4. Overlay Rule — v0.2.1 (CRITICAL FIX)

Raw concatenation of overlay glyphs (`🜄✧🜍`) is **FORBIDDEN** — tokenizers cannot segment it deterministically without full Unicode support.

**Canon form — explicit fenced list, cap=3:**

```
OV=[🜄 ✧ 🜍]
BAN=[⚔️ 🧨 🗣️]
ALLOW=[🛑 🎁 👁️]
```

Alternative string form (equivalent):

```
OV="🜄 ✧ 🜍"
```

**Before (invalid):** `🜄+✧+🜍` or `🜄✧🜍`
**After (valid):** `OV=[🜄 ✧ 🜍]`

If more than 3 overlays are supplied, validator returns: `REJECT_OVERLAY_CAP_EXCEEDED`

Exception: diagnostic display may show more overlays only if the executable `OV` field remains cap-compliant.

---

## 5. Bar Literals — ADD_BARS (display-only)

Dual encoding: numeric for computation, bar string for display.

```
{🥖=7  🥖BAR="■■■■■■■□□□"}
{💖=3.0  💖BAR="■■■□□□□□□□"}
{🛡️=4.5  🛡️BAR="■■■■◐□□□□□"}
```

Hard rule: `XBAR` keys never affect computation. Numeric `X=N` is the canonical value.

Half-step `◐` represents 0.5 in bar rendering.

---

## 6. Mood Comment Lines — ADD_MOOD (parser-ignored)

Lines beginning with `;;` are standalone comments, parser-ignored:

```
;; 🎭⚔️="RAGE"  🎨="RED"  OVERLAY="🜂 🜂 ✝️"
;; ctx(0)="EPO1_SCOPE"
```

Hard rules:
- Comment lines are **standalone** — never mid-clause.
- Never alter canonical ledger lines.
- Use for human anchors, semantic context, mood tags.

---

## 7. Blackout Kill-Switch — Rule K0 (mandatory)

If a props block contains `STATE=⚫` at tick `~◷t`, then for that actor at tick `~◷t`:

```
VERB ∉ {⚔️, 🧨, 🗣️}
```

unless a `🧵` binder clause at the same tick explicitly permits via `ALLOW`:

```
⚔️: 🧵 "SAFETY_LOCK" @⚫ ~◷9 ⛓️ {BAN=[⚔️ 🧨 🗣️]  ALLOW=[🛑 🎁 👁️]}
```

`ALLOW` is bounded to `{🛑, 🎁, 👁️}` (v0.2.1). Extension requires explicit operator approval.

If `STATE=⚫` appears without a compatible safety lock, validator returns: `REJECT_BLACKOUT_WITHOUT_CLAMP`

---

## 8. 7-Token Canonical Ledger

```ebnf
entry   := "(" index ")" SP state SP faction SP pair SP act SP proof SP ribbon
index   := DIGIT {DIGIT}
state   := "🔵" | "🟢" | "🟣" | "⚫" | "🔴"
faction := "⟂◯⟂" | "🌹" | "🌀" | "✝️"
pair    := atom atom             -- exactly 2 ATOMs, no spaces
act     := "📜" | "🛡️" | "🔒📜" | "⚠️📜"
proof   := "🔗#" HEX4
ribbon  := atom atom             -- exactly 2 ATOMs, no spaces
SP      := " "
HEX4    := HEX HEX HEX HEX
HEX     := "0".."9" | "A".."F"
```

### State → Meaning

| State | Meaning |
|-------|---------|
| 🔵 | LAW / observed / tick |
| 🟢 | BUILD / prosperity |
| 🟣 | ARCANE / claim |
| ⚫ | SEAL / dormancy |
| 🔴 | VETO / siege alert |

### Faction → Domain

| Faction | Domain |
|---------|--------|
| ⟂◯⟂ | MASON — neutral / structural |
| 🌹 | ROSICRUCIAN — archive / shrine |
| 🌀 | CHAOS — hazard / anomaly |
| ✝️ | TEMPLAR — order / law |

---

## 9. Proof HEX4 — Rule P0 (strict)

```
proof = 🔗# hex4(seed, tick, proof_ctx, index)
```

- `proof_ctx` (e.g., `"CASTLE_01:SIEGE_HIT"`, `"EPO1_SCOPE"`) lives in `;;` comment lines or the state JSON — **never** inside the ledger proof slot.
- `🔗#EPO1_SCOPE` is **INVALID** — violates HEX4.
- Valid: `🔗#A19F`, `🔗#3C7E`, `🔗#0042`

Implementation (Python):

```python
def hex4(*parts: str) -> str:
    m = hashlib.sha256()
    for p in parts:
        m.update(p.encode("utf-8")); m.update(b"|")
    return m.digest()[:2].hex().upper()
```

---

## 10. Ledger Invariants

| Invariant | Rule |
|-----------|------|
| Index monotonicity | `entry[i+1].index == entry[i].index + 1` |
| Anchor uniqueness | no duplicate proof HEX4 within a session |
| Append-only | MODIFY / DELETE / REORDER are forbidden |
| Proof validity | PROOF matches `hex4(seed, tick, ctx, idx)` |
| State coherence | symbol ↔ category matches mapping table |
| VETO reference | VETO entry must reference a prior existing anchor |
| SEAL checkpoint | all entries before SEAL become immutable snapshot |

---

## 11. Tamagotchi JSON — Required Fields (v0.1)

Each **agent** object must contain:

```json
{
  "archetype": "PRINCESS|WARLORD|ARCHITECT",
  "domain": "DIPLOMACY|SECURITY|MATH",
  "castle": "C1|C2|...",
  "hunger": 0.0,
  "morale": 0.0,
  "stability": 0.0,
  "influence": 0.0,
  "plan_tokens": 0,
  "dormant_ticks": 0,
  "face": null,
  "emo": null,
  "rgb": null,
  "overlays": [],
  "cooldowns": {"HOLD": 0, "ADV": 0, "STRK": 0, "PLAN": 0, "BOND": 0}
}
```

Each **castle** object must contain:

```json
{
  "owner": "A|B|C",
  "pos": [x, y],
  "fortress": 2,
  "status": "NORMAL|SIEGE|REBELLION|DORMANT|PROSPERITY|VULNERABLE",
  "tiles": 10,
  "domain": "DIPLOMACY|SECURITY|MATH"
}
```

Root fields: `seed`, `tick`, `epoch`, `pressure`, `map`, `domains`, `agents`, `castles`, `alliances`, `ledger`.

---

## 12. Validation Commands

```
VALIDATE_EMOGLYPH
  ✓ slot order (ACTOR:VERB OBJ @LOC ~TICK !MODE {...})
  ✓ overlays fenced as OV=[...] or OV="..." — raw concat = FAIL
  ✓ BAR values are STRING keys, not numeric
  ✓ ⚠️ appears as ⚠️=N (integer), never bare
  ✓ K0: STATE=⚫ => no forbidden VERB unless 🧵 permits

VALIDATE_LEDGER
  ✓ 7-token format per entry
  ✓ PROOF = 🔗#HEX4 (exactly 4 uppercase hex chars)
  ✓ index monotone (0, 1, 2, ...)
  ✓ append-only (no gaps, no reorder)
  ✓ state ∈ {🔵 🟢 🟣 ⚫ 🔴}
  ✓ faction ∈ {⟂◯⟂ 🌹 🌀 ✝️}

COMPILE_TICK
  tamagotchi.json → avatar_assign → render → ledger_append
  determinism check: same seed => identical ledger_sha256
```

---

## 13. Avatar Engine — Deterministic (FNV-1a 64)

```
key = "CONQUEST|AVATAR|v1|" + seed + "|" + day_index + "|" + agent_id
h   = fnv1a64(key)
emo = EMO_LIST[ h % 12 ]
face = POOL[emo][ (h >> 8) % len(POOL[emo]) ]
overlays[0..2] from DEFAULT_OVERLAYS[emo] (distinct, cap=3)
rgb = RGB[emo]
```

FNV-1a 64: `offset=1469598103934665603`, `prime=1099511628211`

Output line: `{agent_id}  EMO:{emo}  RGB:{#RRGGBB}  OV:[{o1}{o2}{o3}]  FACE:{face}`

---

## 14. Canonical Example Block (◷7, v0.2.1 compliant)

```
◷7
;; 🎭⚜="AWE"  🎨="#C0A0FF"  ctx="TICK_7_OPEN"
⚜ : 🛑 @◻ ~◷7 ⚡ {🥖=7 🥖BAR="■■■■■■■□□□" 💖=5 💖BAR="■■■■■□□□□□" 🛡️=6 🛡️BAR="■■■■■■□□□□" OV=[🜄 ✧ 🜍] FACE="(๑>ᴗ<๑)" ⛰️->⛓️ ⛓️->🔒 🔒->⚔️ ⚔️->✎ ✎->🔒 🔒->💖 💖->✎ ✎->🔒}

⚔️ : 🛑 @⚔️ ~◷7 ⚡ {🥖=7 🥖BAR="■■■■■■■□□□" 💖=3.0 💖BAR="■■■□□□□□□□" 🛡️=4.5 🛡️BAR="■■■■◐□□□□□" ⚠️=2 OV=[🜂 ✝️ 💀] FACE="(ง'̀-'́)ง" ⛰️->⛓️ ⛓️->⚔️ ⚔️->⛓️ ⛓️->🔒 🔒->⚒️ ⚒️->⚡ ⚡->⚔️}

🜍 : 🛑 @◻ ~◷7 ⚡ {🥖=6 🥖BAR="■■■■■■□□□□" 💖=5 💖BAR="■■■■■□□□□□" 🛡️=6 🛡️BAR="■■■■■■□□□□" OV=[🜃 🜄 🗝] FACE="(づ｡◕‿‿◕｡)づ" ⛰️->⛓️ ⛓️->🔒 🔒->⚔️ ⚔️->✎ ✎->🔒 🔒->⚒️ ⚒️->⚡ ⚡->⚔️}
```

Blackout (◷9 — K0 enforced):

```
◷9
;; 🎭⚔️="BLACKOUT"  STATE=⚫
⚔️ : 🛑 @⚫ ~◷9 ⛓️ {STATE=⚫ 🥖=9 🥖BAR="■■■■■■■■■□" 💖=0.0 💖BAR="⚫" 🛡️=2.5 🛡️BAR="■■◐□□□□□□□" ⚠️=2 OV=[🜂 ✝️ ⛧] FACE="(ง'̀-'́)ง" ⛰️->⛓️ ⛓️->⚫ ⚔️->○ ○->⏸️ ⚒️->○ ○->∅}
⚔️ : 🧵 "SAFETY_LOCK" @⚫ ~◷9 ⛓️ {BAN=[⚔️ 🧨 🗣️] ALLOW=[🛑 🎁 👁️]}
```

---

## 15. Canonical Ledger Example

```
;; ctx(0)="EPO1_SCOPE"  epoch="MEDIEVAL"
(0) 🔵 ⟂◯⟂ 🜃🏰 📜 🔗#A19F 🏰📜
;; ctx(1)="EPO1_BIND0"
(1) ⚫ ⟂◯⟂ 🜂🜍 🔒📜 🔗#3C7E 🔒⚰️
;; ctx(2)="EPO1_SIEGE"
(2) 🔴 🌀 🜁🜂 ⚠️📜 🔗#F8B2 🌀🗝
```

---

## 16. Compiled Dependency Graph

```
nodes:
  N0 = CONQUEST_EMOWUL_CWL_V0_2_1_LOCK
  N1 = EMOGLYPH_CLAUSE
  N2 = EXPLICIT_OVERLAY_LIST
  N3 = WULMOJI_7_TOKEN_LEDGER
  N4 = STRICT_HEX4_PROOF
  N5 = COMMENT_CTX_CHANNEL
  N6 = TAMAGOTCHI_JSON_WORLD_STATE
  N7 = BLACKOUT_SAFETY_LOCK
  N8 = DETERMINISTIC_TICK_RENDERER
  N9 = APPEND_ONLY_LEDGER

edges:
  N0 -> N1   defines clause grammar
  N1 -> N2   requires fenced overlays
  N0 -> N3   freezes canonical ledger
  N3 -> N4   requires proof = 🔗#HEX4
  N5 -> N4   stores human proof_ctx outside ledger
  N6 -> N8   drives deterministic render
  N8 -> N9   emits ledger append
  N7 -> N8   clamps aggression during blackout
  N7 -> N9   emits safety-lock evidence
```

---

## 17. Canonical Lock JSON

```json
{
  "schema": "CONQUEST_EMOWUL_CWL_V0_2_1_LOCK",
  "status": "SPEC_LOCK_CANDIDATE",
  "authority": false,
  "canon": false,
  "ledger_effect": "none",
  "kernel_effect": "none",
  "locks": {
    "WULMOJI_LEDGER": "7-token canonical: (index) state faction pair act proof ribbon",
    "PROOF": "🔗#HEX4 only, generated by hex4(seed,tick,proof_ctx,index)",
    "COMMENTS": "lines starting ;; ignored by parser; allowed for proof_ctx anchors",
    "OVERLAYS": "explicit OV=[...] or OV=\"...\" only; cap=3; no raw concatenation",
    "TAMAGOTCHI_JSON": "authoritative world state",
    "BLACKOUT": "STATE=⚫ in props; aggression clamp required"
  },
  "emoglyph": {
    "clause": "ACTOR : VERB OBJ [@LOC] [~TICK] [!MODE] [#TAG...] {PROPS}",
    "props": "KEY OP VALUE, OP in = -> <- + - ?, lists explicit with [ATOM...]",
    "kill_switch": "if STATE=⚫ then VERB not in {⚔️,🧨,🗣️} unless SAFETY_LOCK binder present"
  },
  "ledger": {
    "state": ["🔵", "🟢", "🟣", "⚫", "🔴"],
    "faction": ["⟂◯⟂", "🌹", "🌀", "✝️"],
    "act": ["📜", "🛡️", "🔒📜", "⚠️📜"],
    "proof_regex": "^🔗#[0-9A-F]{4}$",
    "monotone_index": true
  },
  "required_ir_fields": {
    "agent": ["face", "emo", "rgb", "overlays"],
    "castle": ["domain"]
  },
  "checksum": "sha256:53e726de06b8e4089867568f6958b0aee09cae43e2ed137a52331d940db78f83"
}
```

---

## Receipt Footer

```
CWL_EMOGLYPH_V0_2_1_SPEC — PATCH V0.1

file           = docs/proposals/CWL_EMOGLYPH_V0_2_1_SPEC.md
claim_status   = NO_CLAIM · authority = false
ledger_effect  = none · kernel_effect = none
runner         = sandbox/foundry_town_mvp.py (NON_SOVEREIGN)
seed_json      = sandbox/conquest_tamagotchi_seed.json

patch_v0_1:
  + §4  REJECT_OVERLAY_CAP_EXCEEDED (validator return code)
  + §7  REJECT_BLACKOUT_WITHOUT_CLAMP (validator return code)
  + §16 Compiled Dependency Graph (N0–N9 nodes + edges)
  + §17 Canonical Lock JSON + operator checksum

verdict        = CONQUEST_ACK=ACCEPTED · SPEC_LOCK_CANDIDATE
git_stage = no · git_commit = no · git_push = no
final          = HOLD_FOR_OPERATOR
```
