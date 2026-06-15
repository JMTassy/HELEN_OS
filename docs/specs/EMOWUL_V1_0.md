---
authority: NON_SOVEREIGN
canon: NO_SHIP
lifecycle: SPEC_DRAFT
source: JM_TASSY_AUTHORED_2026-06-15
status: EMOWUL_V1_0
---

# EMOWUL v1.0 — Emotional WUL Overlay Specification

Aesthetic and emotional overlay layer above WUL. Non-sovereign. Carries no
constitutional weight. Machine-friendly tagset compatible with WUL packet
framing. Authored by JM Tassy, 2026-06-15.

---

## § 1 · Law

EMOWUL extends WUL with emotional texture. It does not override WUL semantics.
Every EMOWUL annotation is optional. A WUL packet without EMOWUL is fully valid.
EMOWUL MAY accompany any non-sovereign packet. EMOWUL MUST NOT enter any
`WRITE_SOVEREIGN` path or ledger record.

---

## § 2 · Overlay Dimensions

| Symbol | Name       | Values           | Meaning                                          |
|--------|------------|------------------|--------------------------------------------------|
| V      | Valence    | `+` / `0` / `-`  | Positive / neutral / negative charge              |
| A      | Arousal    | `1` / `2` / `3`  | Calm / charged / critical                         |
| S      | Stance     | `?!→✓⚠`         | Question / declaration / direction / confirm / warn |
| C      | Certainty  | `0`–`4`          | Zero / low / medium / high / proof                |
| T      | Tension    | `0`–`3`          | Rest / holding / pressure / breaking              |
| R      | Ratchet    | `0`–`2`          | Normal / locked / sealed                          |
| K      | Sanctity   | `0`–`3`          | Mundane / aware / sacred / inviolable             |

**S stance values:**
- `?` — question, open query, probe
- `!` — declaration, command, imperative
- `→` — direction, flow, forward
- `✓` — confirmation, receipt, affirm
- `⚠` — warning, caution, escalation signal

---

## § 3 · Palettes

| ID | Color   | Domain                          |
|----|---------|----------------------------------|
| P1 | Gold    | Authority, certainty, confirmation |
| P2 | B+W     | Technical, neutral, structural   |
| P3 | Red     | Alert, danger, blocking          |
| P4 | Violet  | Exploration, dream, TEMPLE       |
| P5 | Grey    | Warning, pending, uncertain      |
| P6 | Blue    | Information, flow, calm          |
| P7 | Bone    | Sacred, ancient, inviolable      |

Palette is declared as `[P1]` … `[P7]` adjacent to the EMOWUL tagset.

---

## § 4 · Core Sigils

```
⸸ ☩ ✧ ⚔ ⚖ ⌛ 🜁 📜 👁 🌀 ⚡ 🔒
```

Sigils are decorative structural glyphs used in **C) Hybrid** and **A) Gothic
Sanctum** rendering. They mark section boundaries and emotional intensity
anchors. No semantic load in machine parsing.

---

## § 5 · Writing Forms

**Form A — Compact inline** (default for C) Hybrid)
```
ASSERT 🧾 {V:+ A:2 S:✓ C:4 T:1 R:1 K:1}
```

**Form B — Expanded block**
```
ASSERT 🧾
  Valence:   + (positive)
  Arousal:   2 (charged)
  Stance:    ✓ (confirmation / receipt)
  Certainty: 4 (proof-level)
  Tension:   1 (holding)
  Ratchet:   1 (locked)
  Sanctity:  1 (aware)
```

**Form C — Prose-infused**
```
🧾 ASSERT [P1·Gold] — A charged receipt-claim, proof-level certainty, one ratchet
locked. The system records this and does not forget.
```

---

## § 6 · Machine Tagset

```
{V:+|0|- ; A:1|2|3 ; S:?|!|→|✓|⚠ ; C:0|1|2|3|4 ; T:0|1|2|3 ; R:0|1|2 ; K:0|1|2|3}
```

Regex pattern for machine extraction:
```
\{V:[+0\-] A:[123] S:[?!→✓⚠] C:[01234] T:[0123] R:[012] K:[0123]\}
```

---

## § 7 · Style Modes

### A) Gothic Sanctum
Full Fraktur headers, cathedral spacing, maximum sigil density. For TEMPLE
renders and ritual documents. Arousal 3 baseline.

### B) Minimal Stone
Clean monochrome. No sigils. Single-weight type. Technical reports, gate
outputs. Arousal 1 baseline.

### C) Hybrid ← **CANONICAL DEFAULT FOR THIS SESSION**
Gothic structural glyphs (⸸ · § · ☩ · ⚔) for section markers. Clean,
readable body. Form A tagset. Palette brackets. Arousal 1–2 baseline with
spot elevation to 3 for critical signals. JM Tassy canonical rendering
selected 2026-06-15 (operator tranche decision).

---

## § 8 · Default Profile Table (WUL Primitive → EMOWUL)

See `EMOWUL_DICTIONARY_V1_0.md` for the full primitive-to-profile mapping.

---

## ⸸ Authority

```
authority: false
sovereign: false
ledger_mutation: false
status: SPEC_DRAFT — awaiting MAYOR admission for any sovereign path
```
