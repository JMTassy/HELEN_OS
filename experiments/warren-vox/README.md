# WARREN VOX

**Zero-credit skin pack** that makes a governed system feel alive.

```
authority: false
claim: NO_CLAIM
canon: false
sovereign: false
paid_generation_calls: 0
HOLD_FOR_OPERATOR — not default style until you seal it
```

## Vision (FABLE, CEO seat)

> WARREN VOX is the zero-credit skin that makes a governed system feel alive —
> extract the grammar the repo already earned, freeze it, and make
> **"Apply WARREN VOX, alter no mechanics, spend no credits"** a one-line command
> any future level can invoke.

## One-liner

```bash
# from HELEN SOT root
python3 experiments/warren-vox/scripts/apply_warren_vox.py --target path/to/surface.html

# verify (zero paid, zero reducer touch)
python3 experiments/warren-vox/scripts/verify_vox.py
```

## Six artifacts

| # | File | Role |
|---|---|---|
| 1 | `tokens.css` | Frozen design tokens + layout primitives |
| 2 | `scene-grammar.md` | Composition + color + first-click law |
| 3 | `SPRITE_SPEC.md` | Free cutout tiers + prop vocabulary |
| 4 | `TRACE_SYSTEM.md` | Felt feedback without inventing state |
| 5 | `scripts/apply_warren_vox.py` | Inject skin; refuse mechanics |
| 6 | `scripts/verify_vox.py` | Offline proof harness |

Plus: `VOX_MANIFEST.yaml`, `EXTRACTION_LEDGER.md`, `demos/`.

## Terrain honesty

On this host, `v3-play.html` **is present** in the goblin-warren game repo and was folded in as an input. Named files `tokens.css` / `scene-grammar.md` / etc. **did not exist** before this pack — they are the freeze of grammar already earned inside live HTML/CSS/docs.

Remote containers that cannot see `v3-play.html` still ship VOX from this directory; v3-play is an *additional* input when available, never a gate.

## What VOX will not do

- Touch Kernel, ledger, mayor, or REDUCER zones
- Call paid image generators
- Claim Kernel admission via green paint
- Become default style without your human seal

## Demo

```bash
open experiments/warren-vox/demos/bare.html          # unskinned skeleton
python3 experiments/warren-vox/scripts/apply_warren_vox.py \
  --target experiments/warren-vox/demos/bare.html \
  --out experiments/warren-vox/demos/bare+vox.html
open experiments/warren-vox/demos/bare+vox.html
```

Sibling skill for free prop generation: `helen-free-graphics`.
