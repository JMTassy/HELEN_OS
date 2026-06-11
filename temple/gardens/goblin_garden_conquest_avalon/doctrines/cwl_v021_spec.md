# CWL v0.2.1 — EMOGLYPH (FREEZE HEADER)

**CLAIM_TYPE:** draft_doctrine
**Purpose:** Canonical language spec for CONQUESTLAND CLI in GARDEN_CONQUEST_AVALON.

```
STATUS: FROZEN / CONFORMANCE-GRADED
DELTA FROM v0.2: ADD_BARS + ADD_MOOD (COMMENTS) + OVERLAY CANON (NO "+" CHAINS)
AUTHORITY: false
SOVEREIGN: false
NOTE: stored as non-sovereign Temple artifact — requires receipt before any promotion
```

---

## 0) Scope

- Deterministic, single-pass parse.
- Emoji are first-class ATOMs.
- Slot discipline via prefixes: `@` `~` `!` `#` `{ }`.
- Canonical overlays MUST be encoded as a single prop `OVERLAY=...`.
- Bars are UI-only; they MUST NOT influence computation.
- Mood comments are ignored by the parser; they MUST NOT appear mid-clause.

---

## Authoritative Whitelists (Minimum Core)

### 3.1 VERB (emoji-native)

```
VERB ∈ { 🧭, 🛑, 👁️, 🏗️, 🏴, 🎁, 🤝, 📜, ⚔️, 🧨, 🗣️, 🧵 }
```

### 3.2 MODE (intent)

```
MODE ∈ { ⚡, 🗺️, ❓, 🎯, ⛓️, 🧩, ➡️, ↩️ }
```

### 3.3 STATE FLAGS (atomic)

```
FLAGS ∈ { 🔒, 🔥, ⏸️, ∅, ⚫, ✖️, ⚠️ }
```

Constraints:
- `⚠️` MUST appear only as a key with integer value in PROPS: `{ ⚠️=N }`
- STATE assignment is restricted to `{ STATE=⚫ }` in v0.2.1.

### 3.4 RESOURCES (common keys)

```
{ 🥖, 💖, 🛡️ } are allowed as KEYS in PROPS.
```

---

## 4) PROPS (Single-Pass)

```
PROPS := "{" (WS* PROP (WS+ PROP))? WS "}"
PROP  := KEY OP VALUE
KEY   := ATOM
OP    := "=" | "->" | "<-" | "+" | "-" | "?"
VALUE := ATOM | NUMBER | STRING
WS    := one or more ASCII spaces (U+0020)
```

Route encoding (native edges):
```
{⛰️->⛓️  ⛓️->🔒  🔒->⚔️}
```

---

## 5) Overlay Canon (Ambiguity Kill)

**FORBIDDEN:**
- Chained overlay atoms with `+` outside prop structure: `🜄+✧+🜍`

**REQUIRED** (STRING default):
- `OVERLAY="🜄 ✧ 🜍"` — space-separated atoms inside a STRING

Overlay cap rule: at most 3 overlay atoms in OVERLAY string, after splitting on spaces.

---

## 6) ADD_BARS (UI-Only, Dual Encoding)

Bars are display-only and MUST NOT affect computation.

```
{🥖=7  🥖BAR="■■■■■■■□□□"
 💖=3.0  💖BAR="■■■□□□□□□□"
 🛡️=4.5  🛡️BAR="■■■■◐□□□□□"}
```

Rules:
- Keys ending with BAR are UI-only
- BAR values MUST be STRING
- Allowed bar glyphs: `■` `□` `◐`
- Engine must ignore all `*BAR` keys for state updates

---

## 7) ADD_MOOD Comments (Ignored by Parser)

```
COMMENT := ";;" (any characters except newline)
```

Example:
```
;; 🎭="AWE"  🎨="#60A5FA"  NOTE="cathedral hush"
```

---

## 8) Mandatory Validation Rules

### K0) Blackout Aggression Clamp

If a clause contains `{ STATE=⚫ }` then `VERB ∉ { ⚔️, 🧨, 🗣️ }` unless a binder clause permits it:
```
X: 🧵 "SAFETY_LOCK" @⚫ ~◷9 ⛓️ {BAN="⚔️ 🧨 🗣️"  ALLOW="🛑 🎁 👁️"}
```

### K1) Prefix-slot order

`@` then `~` then `!` then `#` then `{ }` — reject otherwise.

### K2) ⚠ Usage

Key `⚠️` → VALUE must be integer NUMBER. `⚠️` MUST NOT appear in OVERLAY or comments.

### K3) Deterministic Tokenization

Reject tabs; only ASCII spaces separate tokens. Strings preserve all characters verbatim.

---

## 9) Reference Example (Valid v0.2.1)

```
⚔️: 🛑 @⚔️ ~◷8 ⚡ {
  🥖=8 🥖BAR="■■■■■■■■□□"
  💖=1.5 💖BAR="■◐□□□□□□□□"
  🛡️=4.5 🛡️BAR="■■■■◐□□□□□"
  ⚠️=2
  OVERLAY="🜂 ✝️ ⛧"
  ⛰️->⛓️  ⛓️->🔥  🔥->⚒️  ⚒️->⚡  ⚡->✖️
  FACE="(ง'̀-'́)ง" }

;; 🎭="CRISIS"  🎨="#EF4444"
```

---

```
CLAIM_TYPE: draft_doctrine
AUTHORITY: false
SOVEREIGN: false
SIMULATION_ONLY: true
```
