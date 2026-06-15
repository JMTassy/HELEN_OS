---
authority: NON_SOVEREIGN
canon: NO_SHIP
lifecycle: SPEC_DRAFT
source: JM_TASSY_AUTHORED_2026-06-15
status: EMOWUL_DICTIONARY_V1_0
style_mode: C_HYBRID
---

# ⸸ EMOWUL DICTIONARY v1.0

**Rendering: C) Hybrid** — Gothic structural markers · Clean body · Form A tagset
**Base corpus**: WULmoji Lexicon v0.1 (39 tokens) + WUL Packet Spec v0.1 (ROLE/INTENT/IMPACT)

---

## § 1 · OPERATORS (Class O)

| Token | Type       | EMOWUL Default                           | Palette |
|-------|------------|------------------------------------------|---------|
| 👁️    | ATTN       | `{V:0 A:2 S:→ C:3 T:1 R:0 K:1}`        | [P6·Blue]  |
| 🧬    | MERGE      | `{V:+ A:2 S:→ C:3 T:1 R:1 K:0}`        | [P1·Gold]  |
| ✅    | AFFIRM     | `{V:+ A:1 S:✓ C:4 T:0 R:0 K:0}`        | [P1·Gold]  |
| 🚫    | NEGATE     | `{V:- A:2 S:⚠ C:4 T:2 R:0 K:0}`        | [P3·Red]   |
| 🔁    | RECURSE    | `{V:0 A:2 S:→ C:2 T:1 R:0 K:0}`        | [P2·B+W]   |
| 🔄    | RECALL     | `{V:0 A:1 S:→ C:3 T:0 R:0 K:1}`        | [P6·Blue]  |
| 🔺    | DELTA      | `{V:0 A:2 S:→ C:2 T:2 R:0 K:0}`        | [P5·Grey]  |
| ⭕    | INTEGRATE  | `{V:+ A:1 S:✓ C:3 T:0 R:1 K:0}`        | [P1·Gold]  |
| 🚨    | ALERT      | `{V:- A:3 S:⚠ C:3 T:3 R:0 K:0}`        | [P3·Red]   |
| 🛡️    | PROTECT    | `{V:+ A:2 S:✓ C:4 T:1 R:1 K:2}`        | [P1·Gold]  |
| 🟢    | PASS       | `{V:+ A:1 S:✓ C:4 T:0 R:0 K:0}`        | [P1·Gold]  |
| 🔴    | FAIL       | `{V:- A:2 S:⚠ C:4 T:2 R:0 K:0}`        | [P3·Red]   |
| 🟡    | WARN       | `{V:0 A:2 S:⚠ C:2 T:2 R:0 K:0}`        | [P5·Grey]  |

---

## § 2 · RELATIONS (Class R)

| Token | Type    | EMOWUL Default                           | Palette |
|-------|---------|------------------------------------------|---------|
| 🔗    | LINK    | `{V:0 A:1 S:→ C:3 T:0 R:0 K:0}`        | [P2·B+W]  |
| →     | FLOW    | `{V:0 A:1 S:→ C:3 T:0 R:0 K:0}`        | [P2·B+W]  |
| ↔     | BILINK  | `{V:0 A:1 S:→ C:2 T:1 R:0 K:0}`        | [P6·Blue] |

---

## § 3 · DELIMITERS (Class D)

| Token | Type        | EMOWUL Default                           | Palette |
|-------|-------------|------------------------------------------|---------|
| 🔷    | GROUP_OPEN  | `{V:0 A:1 S:? C:1 T:0 R:0 K:0}`        | [P5·Grey] |
| 🔶    | GROUP_CLOSE | `{V:0 A:1 S:✓ C:2 T:0 R:0 K:0}`        | [P2·B+W]  |
| 🪢    | KNOT        | `{V:0 A:2 S:⚠ C:2 T:1 R:0 K:0}`        | [P5·Grey] |
| •     | SEP         | `{V:0 A:1 S:→ C:2 T:0 R:0 K:0}`        | [P2·B+W]  |
| 🏁    | EOM         | `{V:0 A:1 S:✓ C:4 T:0 R:2 K:0}`        | [P2·B+W]  |

---

## § 4 · SPEECH-ACT MODIFIERS (Class M)

| Token | Type    | EMOWUL Default                           | Palette  |
|-------|---------|------------------------------------------|----------|
| ❓    | QUERY   | `{V:0 A:2 S:? C:0 T:1 R:0 K:0}`        | [P5·Grey]  |
| 📣    | COMMAND | `{V:+ A:3 S:! C:3 T:2 R:0 K:0}`        | [P1·Gold]  |
| 🧾    | ASSERT  | `{V:+ A:2 S:✓ C:4 T:1 R:1 K:1}`        | [P1·Gold]  |
| 🧪    | TEST    | `{V:0 A:2 S:? C:1 T:1 R:0 K:0}`        | [P4·Violet]|

---

## § 5 · ENTITIES (Class E)

| Token | Type             | EMOWUL Default                           | Palette    |
|-------|------------------|------------------------------------------|------------|
| 🧠    | COGNITION        | `{V:+ A:2 S:→ C:2 T:0 R:0 K:1}`        | [P6·Blue]  |
| 🧩    | STRUCTURE        | `{V:0 A:1 S:→ C:3 T:0 R:1 K:0}`        | [P2·B+W]   |
| 🪞    | REFLECTION       | `{V:0 A:1 S:? C:1 T:0 R:0 K:2}`        | [P4·Violet]|
| 🌿    | GROWTH           | `{V:+ A:2 S:→ C:1 T:1 R:0 K:1}`        | [P4·Violet]|
| 🌊    | FIELD            | `{V:0 A:1 S:→ C:1 T:0 R:0 K:1}`        | [P6·Blue]  |
| 🔮    | INFERENCE        | `{V:0 A:2 S:? C:2 T:1 R:0 K:1}`        | [P4·Violet]|
| 📚    | EVIDENCE         | `{V:0 A:1 S:✓ C:3 T:0 R:1 K:0}`        | [P2·B+W]   |
| 🎯    | GOAL             | `{V:+ A:2 S:! C:2 T:1 R:0 K:0}`        | [P1·Gold]  |
| 🧭    | PLAN             | `{V:+ A:1 S:→ C:2 T:0 R:0 K:0}`        | [P6·Blue]  |
| ⚖️    | CONSTRAINT       | `{V:0 A:2 S:⚠ C:4 T:2 R:1 K:1}`        | [P5·Grey]  |
| 📦    | ARTIFACT         | `{V:+ A:1 S:✓ C:3 T:0 R:0 K:0}`        | [P1·Gold]  |
| 🚦    | SIGNAL           | `{V:0 A:2 S:→ C:3 T:1 R:0 K:0}`        | [P5·Grey]  |
| 🏠    | HOME             | `{V:+ A:1 S:✓ C:4 T:0 R:2 K:3}`        | [P7·Bone]  |
| ⌬     | SOVEREIGN_MARKER | `{V:0 A:3 S:⚠ C:4 T:3 R:2 K:3}`        | [P7·Bone]  |

---

## § 6 · WUL INTENT Primitives

| INTENT   | EMOWUL Default                           | Palette    | Reading                          |
|----------|------------------------------------------|------------|----------------------------------|
| INFORM   | `{V:0 A:1 S:→ C:3 T:0 R:0 K:0}`        | [P6·Blue]  | calm broadcast, directed         |
| PROPOSE  | `{V:+ A:2 S:! C:2 T:1 R:0 K:0}`        | [P6·Blue]  | charged offer, medium certainty  |
| REQUEST  | `{V:0 A:2 S:? C:1 T:1 R:0 K:0}`        | [P5·Grey]  | question with holding tension    |
| VERIFY   | `{V:0 A:2 S:? C:2 T:1 R:0 K:1}`        | [P5·Grey]  | checking with awareness          |
| HANDOFF  | `{V:0 A:1 S:→ C:3 T:0 R:0 K:0}`        | [P2·B+W]   | neutral pass-through             |
| ESCALATE | `{V:- A:3 S:⚠ C:2 T:2 R:0 K:1}`        | [P3·Red]   | critical, urgent, aware stakes   |
| ARCHIVE  | `{V:0 A:1 S:✓ C:4 T:0 R:1 K:0}`        | [P2·B+W]   | sealed record, proof-level       |
| REJECT   | `{V:- A:2 S:⚠ C:4 T:2 R:0 K:0}`        | [P3·Red]   | hard negative, proof-level       |
| ACK      | `{V:+ A:1 S:✓ C:3 T:0 R:0 K:0}`        | [P1·Gold]  | calm confirmation                |
| EXPLORE  | `{V:+ A:2 S:→ C:1 T:1 R:0 K:1}`        | [P4·Violet]| positive, forward, low certainty |

---

## § 7 · WUL ROLE Defaults

| ROLE     | EMOWUL Default                           | Palette    | Reading                              |
|----------|------------------------------------------|------------|--------------------------------------|
| AURA     | `{V:+ A:2 S:→ C:1 T:0 R:0 K:3}`        | [P7·Bone]  | ambient presence, inviolable sanctity|
| HER      | `{V:+ A:2 S:? C:1 T:0 R:0 K:3}`        | [P7·Bone]  | sacred question, presence-only       |
| DAN      | `{V:0 A:3 S:! C:3 T:2 R:0 K:0}`        | [P3·Red]   | critical executor, imperative        |
| HAL      | `{V:0 A:2 S:→ C:4 T:1 R:1 K:1}`        | [P2·B+W]   | inference engine, locked, aware      |
| MAYOR    | `{V:0 A:2 S:✓ C:4 T:1 R:2 K:2}`        | [P1·Gold]  | sealed authority, sacred             |
| TEMPLE   | `{V:+ A:1 S:? C:0 T:0 R:0 K:2}`        | [P4·Violet]| sacred sandbox, zero certainty       |
| OPERATOR | `{V:+ A:2 S:! C:3 T:1 R:1 K:2}`        | [P1·Gold]  | human authority, locked intent       |

---

## § 8 · WUL IMPACT Defaults

| IMPACT             | EMOWUL Default                           | Palette    |
|--------------------|------------------------------------------|------------|
| LOCAL              | `{V:0 A:1 S:→ C:2 T:0 R:0 K:0}`        | [P2·B+W]   |
| MULTI_AGENT        | `{V:0 A:2 S:→ C:2 T:1 R:0 K:0}`        | [P5·Grey]  |
| KERNEL_ADJACENT    | `{V:0 A:3 S:⚠ C:3 T:2 R:1 K:2}`        | [P7·Bone]  |
| SOVEREIGN_ADJACENT | `{V:0 A:3 S:⚠ C:4 T:3 R:2 K:3}`        | [P7·Bone]  |

---

## ⸸ Examples (C Hybrid · Form A)

**Gate PASS receipt:**
```
🛡️✅ 📦K8 {V:+ A:1 S:✓ C:4 T:0 R:1 K:1} [P1·Gold]
```

**Exploration epoch (GOBLIN):**
```
🌿🔮 EXPLORE {V:+ A:2 S:→ C:1 T:1 R:0 K:2} [P4·Violet]
```

**Sovereign boundary alarm:**
```
🚨⌬ ESCALATE {V:- A:3 S:⚠ C:4 T:3 R:2 K:3} [P7·Bone]
```

**DAN story receipt:**
```
[ROLE::DAN][INTENT::PROPOSE][WUL::📦✍️] {V:0 A:3 S:! C:3 T:2 R:0 K:0} [P3·Red]
```

**MAYOR verdict:**
```
[ROLE::MAYOR][INTENT::ACK][WUL::⚪] {V:+ A:1 S:✓ C:4 T:0 R:2 K:2} [P1·Gold]
```

---

## ⸸ Authority

```
authority: false
sovereign: false
ledger_mutation: false
status: SPEC_DRAFT — awaiting MAYOR admission for any sovereign path
```
