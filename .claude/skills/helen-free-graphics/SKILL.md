---
name: helen-free-graphics
description: >
  Produce HELEN OS / Goblin Warren paper-collage graphics for free — zero paid
  APIs, zero Higgsfield/MaxFusion credits. Use when the user says "free graphics",
  "paper collage UI", "warren skin", "garden surface art", "make graphics free",
  "collage without API", "emoji cutouts", "parchment HUD", "v3-play style",
  or wants reusable HELEN visual assets without generation cost. Slash: /helen-free-graphics.
  Prefer this over paid image tools whenever the brief is UI shells, garden boards,
  stamp cards, meter chrome, or playful cutout scenes. authority=false · NON_SOVEREIGN.
---

# HELEN Free Graphics — Paper Collage for $0

Turn the **v3-play** beauty into a reusable HELEN pipeline that never burns credits.

```
PAID tools (Higgsfield, MaxFusion, Gemini image…)  = optional last resort
FREE stack (this skill)                            = default for HELEN skins
```

**Canon exemplar (playable):**
`~/Documents/GitHub/goblin-warren/v3-play.html`

**Law (always print in the footer of free surfaces):**
```
Garden ADMIT ≠ Kernel ADMISSION · authority=false · this is play / skin
```

Graphics here are **skin**, never sovereignty. Pretty meters ⊬ state. Pretty green ⊬ admitted.

---

## When to use / when not to

| Use this skill | Do NOT use this skill |
|---|---|
| UI shells, HUDs, stamp cards, garden boards | Photoreal product ads |
| Goblin/Warren garden props | Identity-lock HELEN face canon (use `helen-masterpiece`) |
| Rapid prototypes, operator cockpits, Temple toys | Paid B-roll video (use `collage-broll-explainers`) |
| Offline / no-network demos | Anything that must cross the Kernel membrane as proof |

---

## Free stack (priority order)

Always climb this ladder **top-first**. Stop at the first tier that ships beauty.

### Tier 0 — HTML/CSS composition (default, always free)

Single-file HTML. No build. No CDN required (system fonts only).

- Parchment page + moss stage + paper cards
- Big stamp buttons (ADMIT / DENY / COMPOST)
- Coach line that always names the next click
- Drop-shadow cutouts, pop-in buildings

**Scaffold:**
```bash
python3 .claude/skills/helen-free-graphics/scripts/scaffold_free_surface.py \
  --title "My Garden Board" \
  --out apps/goblin-warren/surfaces/<slug>.html
```

Or copy the template:
`templates/surface-shell.html`

### Tier 1 — Emoji cutouts (zero files)

Treat emoji as free die-cut paper:

```css
.build {
  position: absolute;
  font-size: 2rem;
  filter: drop-shadow(2px 3px 2px rgba(0,0,0,0.35));
  animation: popin 0.45s cubic-bezier(0.34,1.4,0.64,1) both;
}
```

HELEN Warren prop vocabulary (reuse freely):

| Emoji | Prop |
|---|---|
| 🍄 | mushroom court |
| 🗼 | suspicious tower |
| 🕳️ | laugh-hole |
| 🌙 | tax moon |
| 🪑 | plotting bench |
| 🔥 | compost disaster |
| 📜 | receipt / claim |
| 🏮 | watch-lantern |
| 🐛 | bug nursery / Gerald |
| 🍃 | ferry / trade leaf |
| 🍂 | compost residue |
| 😴 | sanctioned nap |

### Tier 2 — Pure CSS pixel sprites (zero images)

CSS `box-shadow` pixel grids (see garden `v3.html` goblin NPC). Good for roaming goblins when PNG cutouts are missing.

### Tier 3 — Free SVG cutouts (scripted)

```bash
python3 .claude/skills/helen-free-graphics/scripts/make_svg_cutout.py \
  --shape mushroom --color "#5c7a3a" --out assets/free/mushroom.svg
```

SVGs are first-class cutouts: crisp edges, cream keyline, soft shadow via CSS filter on the `<img>` or inline SVG.

### Tier 4 — Local collage stills already on disk (still free)

Reuse existing approved packs before inventing new art:

```
~/Documents/GitHub/goblin-warren/assets/collage_stills/cut/   # bram, lulu, seedlings, rock…
helen_os_v1/apps/goblin-warren/assets/                       # concept + districts + personas
```

**Rule:** reference local files only. Never hotlink remote paid CDNs for skin art.
Three.js CDN is forbidden in free graphics shells (V2 failure mode).

### Tier 5 — Paid generation (opt-in only)

Only if the operator **explicitly** asks for new painted plates. Then hand off to
`helen-masterpiece` / `higgsfield-generate` / `collage-broll-explainers`.
Do **not** auto-escalate. Free stack failure → simplify the scene, do not open the wallet.

---

## Visual system (locked)

### Palette (parchment garden)

```css
:root {
  --bg: #efe7d8;       /* page parchment */
  --ink: #2a241c;      /* body text */
  --dim: #7a6f5c;      /* secondary */
  --card: #faf6ec;     /* paper card */
  --edge: #d8ceba;     /* paper edge */
  --admit: #2e5940;    /* moss green — grow */
  --deny: #8a3a30;     /* clay red — block */
  --compost: #6b5a2e;  /* soil brown — bury */
  --glow: #c25e28;     /* lantern / focus */
  --gold: #b8860b;     /* coach / day tags */
  --stage-green: #2e5940;
}
```

Do **not** paint governance with decorative green. In HELEN WULMOJI, green means
**admitted**. On free surfaces, green is **moss / Fix / Admit-stamp chrome only**,
never a claim of Kernel admission. Footer law text is mandatory.

### Materials

- Uncoated paper fiber feel (soft flat fields, not glossy 3D)
- Soft physical drop shadows under every cutout
- Rounded paper cards (`border-radius: 12–18px`)
- One stage (garden plate), not a dashboard of six equal panels
- System UI font (no webfont CDN)

### Motion (cheap, free, seek-safe enough for HTML)

- `popin` for new buildings
- 0.3–0.4s meter bar width transitions
- Speech bubble opacity fade
- **Never** require keyboard chords for the primary loop (V2 anti-pattern)

### Layout contract (playable free surface)

```
[ title · day tag ]
[ meters: 3 simple bars ]
[ STAGE — garden plate with cutouts ]
[ COACH — always says next click ]
[ PROPOSAL CARD — one idea, big type ]
[ STAMPS — 3 fat buttons, min-height 64px ]
[ short log ]
[ law footer ]
```

Mobile: max-width ~520px centered. Touch targets ≥ 44px.

---

## Agent workflow (every free graphic job)

1. **Brief** — what is the one feeling? (grow / block / bury / wander / stamp)
2. **Pick tier** — start at Tier 0; climb only if needed
3. **Scaffold** — `scaffold_free_surface.py` or copy template
4. **Props** — emoji first; SVG second; local PNG third
5. **Coach line** — write the one sentence that tells the operator where to click
6. **Witness** (launcher protocol):
   - HTML path exists
   - Every local `src=` / `url()` resolves on disk
   - Open in browser; first screen has **one** obvious primary button
7. **Receipt (non-sovereign)** — report paths + tier used + "authority=false"
8. **Never** claim Kernel admission for skin work

### First-click law (non-negotiable)

If a newcomer cannot find the first click in **2 seconds**, the surface fails.
Fix with a full-screen overlay + one green button. Do not add more panels.

---

## Recipes

### A. New playable stamp board (5 min)

```bash
python3 .claude/skills/helen-free-graphics/scripts/scaffold_free_surface.py \
  --title "Compost Court" \
  --slug compost-court \
  --out apps/goblin-warren/surfaces/compost-court.html
open apps/goblin-warren/surfaces/compost-court.html
```

Fill proposal texts; keep ADMIT/DENY/COMPOST.

### B. Static mood plate (no game loop)

Use the template with `data-mode="still"`. Stage + 3–6 emoji cutouts + title.
Export screenshot via browser if a PNG is needed (still free).

### C. SVG prop pack

```bash
for s in mushroom tower lantern bench leaf bug moon; do
  python3 .claude/skills/helen-free-graphics/scripts/make_svg_cutout.py \
    --shape "$s" --out "apps/goblin-warren/assets/free/${s}.svg"
done
```

### D. Port beauty into an existing HELEN HTML surface

1. Import palette CSS variables from `references/palette.css`
2. Replace dense dashboard grids with **one stage + one card + one coach**
3. Delete keyboard-only controls; promote verbs to buttons
4. Add law footer
5. Witness all asset paths

---

## Forbidden (learned from V2 / dashboard-v3)

- Three.js / WebGL as the *entry* experience
- Keyboard-only primary actions (`Q`/`B`/`P`/`A`/`D`/`H` without on-screen verbs)
- API key walls before first play
- Kernel jargon on the first screen (membrane stress, L6 fruit, signal kinds…)
- Green-as-"successfully written" / green-as-Kernel-admitted
- Remote image hotlinks that die offline
- Auto-calling paid generators "to make it pretty"

---

## Sibling skills / packs

| Skill / pack | Relationship |
|---|---|
| `warren` | Game law + membrane; this skill is the **skin factory** |
| **WARREN VOX** (`experiments/warren-vox/`) | Frozen zero-credit skin pack + one-line apply: `python3 experiments/warren-vox/scripts/apply_warren_vox.py --target <html>` — alter no mechanics, spend no credits |
| `helen-os-doctrine` | Why skin ≠ sovereignty |
| `helen-masterpiece` | Paid / identity-lock plates — only after free stack is insufficient |
| `collage-broll-explainers` | Paid halftone video B-roll — different medium |
| `hyperframes-creative` | Motion video compositions — use after free still shell is solid |

---

## Output checklist (ship only if all true)

- [ ] Opens offline (`file://`) with no console 404s for local assets
- [ ] First screen: one primary button, readable in 2 seconds
- [ ] Palette matches parchment garden tokens
- [ ] Law footer present (`Garden ADMIT ≠ Kernel ADMISSION`)
- [ ] `authority=false` in HTML comment header
- [ ] No paid API call was required to produce the surface
- [ ] Coach / hint names the next action at every step (if interactive)

`beauty without mechanism is lullaby — free beauty with a clear click builds the Garden.`
