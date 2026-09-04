# WARREN VOX — Sprite / Cutout Spec

authority: false · claim: NO_CLAIM · paid_generation_calls: 0

Sprites in VOX are **paper cutouts**, not engine spritesheets (unless a level already ships sheets). Prefer free tiers.

## Tier ladder (stop at first that ships beauty)

| Tier | Medium | Cost |
|---|---|---|
| 0 | HTML/CSS layout classes from `tokens.css` | $0 |
| 1 | Emoji cutouts + `drop-shadow` | $0 |
| 2 | Pure CSS pixel box-shadow figures | $0 |
| 3 | Local SVG silhouettes (`helen-free-graphics` script) | $0 |
| 4 | Local PNG collage stills already on disk | $0 |
| 5 | Paid generation | **forbidden for VOX apply** |

`paid_generation_calls: 0` is product position. Apply tooling must not call image APIs.

## Emoji prop vocabulary (canonical free cast)

| Emoji | Prop | Semantic (Garden only) |
|---|---|---|
| 🍄 | mushroom court | growth / soft trial |
| 🗼 | suspicious tower | chaos / watch joke |
| 🕳️ | laugh-hole | humor infrastructure |
| 🌙 | tax moon | ritual / weird accounting |
| 🪑 | plotting bench | scheme seating |
| 🔥 | compost disaster | chaos + future soil |
| 📜 | receipt scroll | claim comedy — not ledger |
| 🏮 | watch-lantern | lie-glow prop — not HAL |
| 🐛 | Gerald / bug spa | name bugs kindly |
| 🍃 | leaf ferry | tiny trade |
| 🍂 | compost residue | after COMPOST |
| 😴 | civic nap | rest as infrastructure |
| 🌱 | seedling | begin / dry→bloom |
| 🪨 | heavy rock | needs help / MARK, not only FIX |

## CSS cutout contract

```css
.vox-cutout {
  position: absolute;
  font-size: 2rem;
  filter: drop-shadow(2px 3px 2px var(--vox-shadow-deep));
  animation: vox-popin 0.45s cubic-bezier(0.34, 1.4, 0.64, 1) both;
}
```

Placement: percentage `left` / `bottom` inside `.vox-stage`.  
Admit → new cutout. Deny → no cutout. Compost → optional 🍂 residue.

## Local PNG atlas (if present — free reuse)

```
~/Documents/GitHub/goblin-warren/assets/collage_stills/cut/
  bram.png  lulu.png  seedlings_dry.png  seedlings_bloomed.png
  rock_cracked.png  mark_pulse.png  scroll_fading.png
```

```
helen_os_v1/apps/goblin-warren/assets/free/*.svg   # free silhouettes
```

Never hotlink remote paid CDNs for VOX skins.

## Agent figures

- Prefer 2–3 named agents on stage (Grub / Snort / Lurk… or Bram / Lulu).
- Talking agent: extra gold drop-shadow (`.talking` / filter glow).
- Speech bubble: paper card, max ~180px, fades in/out — flavor only.

## What is not a VOX sprite

- Kernel seal icons used as decoration without law text
- Green "ADMITTED" badges on unsealed experiments
- Three.js meshes required for first paint
