# HELEN OS — Canonical Surface V1

authority=NON_SOVEREIGN  canon=NO_SHIP

## Operating Language

HELEN OS is an **object-first** semantic operating environment, not a chatbot, not a workflow tool.

The interaction model:

```
semantic object field → pull → compose → validate → persist
```

Not sequence-first (chat). Object-first (semantic gravity).

---

## Color System (locked)

| Token        | Value     | Use |
|---|---|---|
| BLACK        | `#080808` | Background, canvas |
| SURFACE      | `#0e0e0e` | Panel backgrounds |
| GRAPHITE     | `#161616` | Hover states |
| BORDER       | `#202020` | Dividers |
| OFF-WHITE    | `#e6e1d6` | Primary text (warm, archival) |
| SILVER       | `#7a7874` | Secondary text, dim labels |
| SILVER-HI    | `#a09c96` | Mid-weight metadata |
| SIGNAL       | `#c49a3c` | **One signal color — amber.** Kernel, sovereign, receipts, selection |

No other colors. No gradients. No animations beyond physics simulation.

---

## Typography System (locked)

| Role | Stack |
|---|---|
| Title / label | `Georgia, 'Times New Roman', serif` |
| UI / body | `-apple-system, 'Helvetica Neue', sans-serif` |
| Data / hash / code | `'SF Mono', 'Fira Code', monospace` |

Weights: normal and 600 only. Letter-spacing on labels: 0.2em minimum.

---

## Object Schema

Every semantic object in the field:

```json
{
  "id": "string",
  "type": "EVENT | EPOCH | ACTION | RECEIPT",
  "subject": "string (≤70 chars)",
  "relations": ["string"],
  "confidence": 0.0–1.0,
  "receipts": "integer (0 = unverified)",
  "timestamp": "ISO UTC",
  "provenance": "kernel | goblin | terminal",
  "sovereign": "boolean",
  "hash": "string (12 chars)"
}
```

---

## Visual Primitives

| Element | Rule |
|---|---|
| **Object card** | Type badge (mono, 8px, all-caps) + subject (10px) + provenance + receipt count |
| **Receipt card** | Hash (signal amber) + event type + timestamp (mono) |
| **Semantic edge** | Thin line, `rgba(196,154,60, 0.07–0.18)` — brighter for cross-provenance high-weight |
| **Sovereign badge** | `border: 1px solid signal; color: signal; padding: 2px 7px` |
| **Confidence field** | Numeric only (`0.765`). No bars, no icons. |
| **Provenance field** | Plain text: `kernel`, `goblin`, `terminal` |
| **Receipt count** | `4R` — signal color when > 0 |

---

## Constellation Rules

- Node size: `2.5 + confidence × 5` px radius
- Kernel nodes: signal amber fill
- GOBLIN nodes: silver fill, opacity proportional to confidence
- Terminal nodes: dim silver
- Selected node: outer ring (signal, 1px) + halo glow
- Grid underlay: `rgba(255,255,255,0.018)` — classified terminal feel
- No axes. No legends. Semantic gravity speaks for itself.

---

## Surface Geometry

```
[ Object Field 220px ] [ Constellation 1fr ] [ Sovereign Ledger 220px ]
```

Header strip: 40px — title (serif) left, density + badge + clock right.
Node detail: bottom-anchored overlay on center panel, signal border top.

---

## The Killer Differentiator

Right panel shows **only receipted, validated objects** entering persistent state.

This is not a filter. It is the constitutional boundary:

> NO RECEIPT · NO SHIP · EVERY CLAIM · EVERY ACTION · EVERY TIME

The left panel shows the field. The right panel shows what survives it.

---

## Aesthetic Reference

Palantir calm × Hermès archive × classified aerospace UI × medieval manuscript × semantic graph.

UZIK principles applied: editorial restraint, premium whitespace, high signal density with low clutter.

Never: gradients, decorative animations, color beyond the locked system, emojis, icons.
