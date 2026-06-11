# Face Pool Canon

**CLAIM_TYPE:** world_model
**Purpose:** Canonical "Emotion of the Day" face pool for CONQUESTLAND CWL v0.2.1.

```
DEDUP_RULE: exact string match only (no trimming, no normalization)
DECLARED_COUNT: 32 unique (user-declared)
STORED_COUNT: 33 shown (indices 00-32)
NOTE: (｡•̀ᴗ-)✧ appeared twice in source; second occurrence removed.
```

---

## Canonical Face Index

```
[00] (ﾉ◕ヮ◕)ﾉ*:･ﾟ✧
[01] (｡♥‿♥｡)
[02] (๑>ᴗ<๑)
[03] (≧◡≦)
[04] (｡•́‿•̀｡)
[05] (ू•ᴗ•ू)
[06] (⁄ ⁄>⁄ ▽ ⁄<⁄ ⁄)
[07] (>ω<)
[08] (つ≧▽≦)つ
[09] (づ｡◕‿‿◕｡)づ
[10] (っ˘ڡ˘ς)
[11] (っ´▽`)っ
[12] (｡•̀ᴗ-)✧
[13] (๑˃̵ᴗ˂̵)و
[14] (╯✧▽✧)╯
[15] (✿◕‿◕)
[16] (ᵔᴥᵔ)
[17] (=^･ω･^=)
[18] (=^･ｪ･^=)
[19] (•ㅅ•)
[20] (•ө•)♡
[21] ʕ•ᴥ•ʔ
[22] ʕっ•ᴥ•ʔっ
[23] (っ^_^)っ
[24] (っ˘ω˘ς )
[25] (｡•́︿•̀｡)
[26] (；ω；)
[27] (；´Д｀)
[28] (ง'̀-'́)ง
[29] (╥﹏╥)
[30] (￣▽￣)ノ
[31] (￢‿￢ )
[32] ( ͡° ᴥ ͡°)
```

---

## Usage in CWL v0.2.1

In a CWL clause, faces appear as:

```
FACE="(ง'̀-'́)ง"
FACE="(ﾉ◕ヮ◕)ﾉ*:･ﾟ✧"
```

The FACE prop is a visual/display-only field. It does not affect state computation.
It may appear in any PROPS block. Engine must not use FACE for state transitions.

---

```
CLAIM_TYPE: world_model
AUTHORITY: false
SOVEREIGN: false
SIMULATION_ONLY: true
```
