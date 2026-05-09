---
name: helen-dashboard
description: load when the user asks to run, inspect, debug, redesign, or evolve the HELEN OS dashboard, including the semantic object field, constellation graph, sovereign ledger, MAYOR verdict, local Flask server, visual surface, palette, or HELEN/AIRI avatar placement.
authority: NON_SOVEREIGN
canon: NO_SHIP
---

# HELEN Dashboard Skill

## Purpose

Maintain the HELEN OS dashboard as an object-first semantic operating surface.

The dashboard is not a chatbot, not a generic admin panel, and not a decorative website. It is a live semantic field where objects, relations, receipts, verdicts, and avatar-presence are rendered as one coherent operating surface.

## Canonical Surface

Preserve the three-panel structure unless the user explicitly requests a new layout:

1. Left: Object Field
2. Center: Constellation / semantic gravity + HELEN avatar as sovereign anchor
3. Right: Sovereign Ledger

The HELEN/AIRI avatar must act as sovereign center, witness, or field attractor — never decorative.

## Visual Canon

Frozen palette — do not deviate unless user explicitly unlocks:

| Token | Value |
|---|---|
| black | `#060608` |
| surface | `#0d0d10` |
| off-white | `#e4dfd4` |
| silver | `#78756f` |
| signal amber | `#c49a3c` |

One serif (`Georgia`), one sans (`-apple-system`), one mono (`SF Mono / Fira Code`). No gradients. No additional accent colors.

## Avatar Rule

HELEN is the sovereign core identity. AURA is the tribal/cyber-goth red-haired SB sub-agent. Do not confuse them.

If avatar is present, it must be:
- Gravitational center of constellation (current canonical placement)
- Witness face in the detail panel on node click
- Never a decorative corner portrait

Avatar source: `artifacts/video/ship_2e_helen_speaks/source/helen_source.png`
Served at: `/avatar`
Manifest: `airi_helen_avatar/assets/avatar_manifest.json`

## Standard Workflow

When asked to improve the dashboard:

1. Run `scripts/check_dashboard.py` — verify all endpoints live
2. Preserve canonical structure unless user asks for a break
3. Modify the smallest coherent surface
4. Validate locally (check_dashboard.py again)
5. Commit only if the result runs
6. Report: what changed · what is live · how to run · commit hash · next step

## Scripts

```bash
scripts/run_dashboard.sh       # kill port 7000, restart Flask
scripts/check_dashboard.py     # health-check all API endpoints + object count
```

## Gotchas

- Never reduce HELEN OS to a chatbot UI. Preserve object-first framing.
- Never make the avatar decorative only. She must act as sovereign center or witness.
- Do not add uncontrolled colors. Signal amber is the only accent.
- MAYOR verdict stays `NO_SHIP` unless governance state changes — never set it to SHIP in the UI.
- Do not confuse AURA (SB agent) with HELEN (sovereign core identity).
- Do not over-animate. Subtle orbital motion is acceptable; game-like chaos is not.
- Do not describe uncommitted work as shipped.
- When changing server behavior, always validate `/api/semantic`, `/api/kernel`, and `/`.
- Port 7000 may already be in use — `run_dashboard.sh` handles this.

## Output Style

- what changed
- what is live
- how to run
- commit hash if available
- remaining sharp next step
