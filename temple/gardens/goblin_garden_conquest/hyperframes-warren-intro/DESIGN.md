# DESIGN.md — Goblin Warren Intro Asset

authority: false · canon: false · ledger_effect: none · final: HOLD_FOR_OPERATOR

## Style Prompt

Night-grid Goblin Warren title card: deep moss-black HUD field, purple Akashic
tree glow, warm lantern gold, mouthless flat-geometric goblin silhouettes,
storybook-pixel hybrid matching the LIVE-NPC warren home plate. Soft squash-
and-settle motion, parchment grain on dark, no SaaS chrome.

## Colors

| Role | Hex | Use |
|------|-----|-----|
| bg | `#06140e` | night grid field |
| bg-lift | `#0c2218` | panels / soft plates |
| fg | `#e8f5e9` | primary titles |
| muted | `#8fb89a` | secondary copy |
| accent-gold | `#e8c84a` | labels, START energy |
| accent-purple | `#c084fc` | Akashic tree / triad box |
| accent-magenta | `#e879f9` | triad border pulse |
| goblin | `#5a9e4a` | mouthless figures |
| danger-soft | `#8a5a4a` | HOLD tone only (never claim green) |
| grain | `rgba(232,200,74,0.04)` | paper flecks |

## Typography

- Display + body: `"Outfit", "Helvetica Neue", sans-serif` — titles / tagline (HyperFrames auto-resolved)
- Mono / HUD: `"JetBrains Mono", "Courier New", monospace` — triad, stamps, meta

## Motion

- Entrance offset 0.15–0.3s from beat start
- Eases: `power3.out`, `back.out(1.2)`, `sine.inOut` (ambient only)
- Ambient: lantern scale pulse, tree particle drift, grain flicker (finite repeats)
- Soft squash-and-settle on title hit (scale 0.92 → 1.04 → 1.0)

## What NOT to Do

1. No mouths on goblins (eyes only; geometric heads)
2. No cyan/purple SaaS gradients, no pure `#000`/`#fff`
3. No green-as-ADMITTED governance claim colors for decoration
4. No narration, no stock photography, no modern macOS chrome
5. No infinite `repeat: -1` on GSAP timelines
6. No "CONQUEST IS ADMITTED" / false-green language
