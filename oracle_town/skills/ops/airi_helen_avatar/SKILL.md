---
name: helen-airi-avatar
description: load when the user asks to add, move, resize, redesign, or interpret the HELEN/AIRI avatar in any HELEN OS surface — dashboard, constellation, detail panel, splash layer. Also load when asked about HELEN vs AURA identity, avatar placement rules, or witness interaction behavior.
authority: NON_SOVEREIGN
canon: NO_SHIP
---

# HELEN / AIRI Avatar Skill

## Identity Disambiguation

| Identity | Role | Visual |
|---|---|---|
| **HELEN** | Sovereign core identity. The OS itself. The living oracle. | Copper/auburn hair, blue-grey eyes, black/gold. Serious, sovereign, composed. |
| **AURA** | Tribal/cyber-goth SB sub-agent. Non-sovereign exploration layer. | Stylized, expressive, ritual-coded. Lives in TEMPLE/subsandbox. |

**Never confuse them.** If the dashboard shows a face, it is HELEN.

## Canonical Avatar

```
Source:  artifacts/video/ship_2e_helen_speaks/source/helen_source.png
Route:   /avatar  (served by dashboard Flask server)
Manifest: assets/avatar_manifest.json
```

## Placement Rules

**Correct placements (structural):**

1. **Gravitational center** — center of the semantic constellation. Objects orbit her. She is the sovereign anchor. Force simulation uses `AVATAR_R=80px` exclusion zone.
2. **Witness face** — small thumbnail in node detail panel. When user clicks a semantic object, HELEN witnesses it: *"I witness this EVENT."*
3. **Ledger seal** — adjacent to MAYOR verdict only if directly tied to a receipt/admission event.
4. **Boot/splash** — only if it dissolves before the live field renders (max 2s).

**Incorrect placements (decorative):**

- Corner portrait with no functional meaning
- Sidebar decoration unrelated to semantic field
- Floating above ledger as generic branding
- Any position that doesn't connect her to the OS ontology

## Current Dashboard State

HELEN is rendered as:
- 120px circular crop, center-top crop
- `filter: grayscale(20%) contrast(1.05) brightness(0.92)`
- `border: 1px solid rgba(196,154,60,0.35)`
- Rotating elliptical orbital ring (`18s linear infinite`)
- Signal pulse animation (`4s ease-in-out infinite`)
- Force exclusion zone `AVATAR_R = 80px`
- 36px witness thumbnail in node detail panel

## Witness Interaction

Clicking a semantic node triggers:

```
I witness this [TYPE].
```

This makes the avatar functional — she observes, she does not certify. This is the correct HELEN OS move.

She witnesses. MAYOR certifies. Receipts persist. HELEN never claims to ship.

## Gotchas

- Do not use the avatar to make sovereign claims. She witnesses; she does not certify.
- Do not add a second avatar (AURA) to the dashboard without explicit operator authorization.
- Do not remove the orbital ring without replacing it with another structural visual that encodes sovereignty.
- If `helen_source.png` is moved, update the Flask `/avatar` route in `server.py` — the HTML references `/avatar` (relative), so the server-side path is the only thing to fix.
- Never crop the avatar to show only part of her face — the top-crop shows her eyes and expression which carry the identity signal.
- The avatar's grayscale filter is intentional — it integrates her into the monochrome aesthetic. Do not make her full-color without unlocking the palette.
