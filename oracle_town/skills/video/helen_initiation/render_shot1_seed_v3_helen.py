#!/usr/bin/env python3
"""
Shot 1 seed V3 — HELEN character integration.
Loads V2 (archway + figures) and adds:
  - HELEN's orange-red hair on the seeker (lit by left torch at 3200K amber)
  - Freckle suggestion on forehead/cheek above blindfold
  - Hair tie/clip detail
  - Tightens blindfold to match HELEN's proportions
Output: shot1_initiation_seed_v3.png
"""
import math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

OUT  = Path("/tmp/helen_initiation")
SRC  = OUT / "shot1_initiation_seed_v2.png"
DEST = OUT / "shot1_initiation_seed_v3.png"

img  = Image.open(SRC).convert("RGB")
draw = ImageDraw.Draw(img, "RGBA")
W, H = img.size

# ── Known seeker geometry (mirrored from V2 render constants) ──────────────
SEEKER_X   = W // 2 - 40          # 500
FIG_BASE_Y = int(H * 0.91)        # 1747
FH         = 430
SEEK_TOP   = FIG_BASE_Y - FH      # 1317

HEAD_W  = 52
HEAD_H  = 66
HEAD_CY = SEEK_TOP + int(HEAD_H * 0.54)    # ~1353

BF_Y    = HEAD_CY - 2             # blindfold centre y ~1351
BF_W    = HEAD_W + 6              # blindfold width  ~58

# Left torch is the key light source for HELEN
TORCH_L_X = 248    # ARCH_L - 10 from V2 (approx)
TORCH_L_Y = int(H * 0.28 + (H - H * 0.28) * 0.28)   # same formula as V2

# ── Orange hair palette (3200K amber room) ──────────────────────────────────
HAIR_BASE     = (195,  90,  14)   # main orange, torchlit
HAIR_LIGHT    = (235, 130,  22)   # highlight strand (left-lit)
HAIR_SHADOW   = (135,  52,   8)   # shadow side / depth
HAIR_DEEP     = (100,  38,   6)   # darkest roots under hood
HAIR_STRAND   = (215, 108,  16)   # mid strands

FRECKLE_COL   = (165,  88,  40)   # warm freckles lit by torchlight

# ─── 1. Hair mass — layered ellipses for volume ───────────────────────────
# Crown extends ~50px above head top; hair spreads wider than head
CROWN_Y = HEAD_CY - HEAD_H // 2 - 10    # ~1310

# Base volume (large warm ellipse, slightly off-centre for natural fall)
draw.ellipse([
    SEEKER_X - 42, CROWN_Y - 48,
    SEEKER_X + 44, CROWN_Y + 60,
], fill=(*HAIR_BASE, 240))

# Lit left lobe (closer to left torch)
draw.ellipse([
    SEEKER_X - 48, CROWN_Y - 38,
    SEEKER_X + 8,  CROWN_Y + 52,
], fill=(*HAIR_LIGHT, 180))

# Shadow right lobe
draw.ellipse([
    SEEKER_X - 10, CROWN_Y - 30,
    SEEKER_X + 50, CROWN_Y + 48,
], fill=(*HAIR_SHADOW, 160))

# Deep root darkness at parting
draw.ellipse([
    SEEKER_X - 14, CROWN_Y - 10,
    SEEKER_X + 14, CROWN_Y + 24,
], fill=(*HAIR_DEEP, 130))

# Top highlight — single brighter ellipse (key light hit on crown)
draw.ellipse([
    SEEKER_X - 22, CROWN_Y - 44,
    SEEKER_X + 20, CROWN_Y - 10,
], fill=(*HAIR_LIGHT, 150))

# ─── 2. Hair strands — individual painted wisps ───────────────────────────
rng = random.Random(55)

# Strands falling on left shoulder (lit side — brighter orange)
for i in range(22):
    sx  = SEEKER_X - 30 + rng.randint(-8, 4)
    sy  = CROWN_Y + rng.randint(10, 42)
    ex  = sx - rng.randint(12, 35)
    ey  = sy + rng.randint(20, 60)
    col = HAIR_LIGHT if rng.random() > 0.4 else HAIR_STRAND
    a   = rng.randint(140, 210)
    draw.line([(sx, sy), (ex, ey)], fill=(*col, a), width=rng.randint(1, 3))

# Strands falling on right shoulder (shadow side — deeper orange)
for i in range(16):
    sx  = SEEKER_X + 20 + rng.randint(-4, 12)
    sy  = CROWN_Y + rng.randint(8, 38)
    ex  = sx + rng.randint(10, 28)
    ey  = sy + rng.randint(18, 50)
    col = HAIR_SHADOW if rng.random() > 0.4 else HAIR_BASE
    a   = rng.randint(110, 180)
    draw.line([(sx, sy), (ex, ey)], fill=(*col, a), width=rng.randint(1, 2))

# A few wisps across forehead (above blindfold — visible band of face)
for i in range(10):
    sx = SEEKER_X - 25 + rng.randint(0, 50)
    sy = CROWN_Y + rng.randint(30, 48)
    ex = sx + rng.randint(-18, 18)
    ey = sy + rng.randint(10, 22)
    if ey < BF_Y - 8:   # only above blindfold
        draw.line([(sx, sy), (ex, ey)], fill=(*HAIR_STRAND, rng.randint(90, 160)), width=1)

# ─── 3. Wavy texture — curved stroke suggestion ───────────────────────────
for i in range(8):
    cx_ = SEEKER_X - 36 + i * 4
    for dy in range(0, 30, 6):
        wave_x = int(cx_ + 4 * math.sin(dy / 6.0))
        wave_y = CROWN_Y - 30 + dy
        a = int(120 * (1 - dy / 30))
        draw.ellipse([wave_x - 2, wave_y - 1, wave_x + 2, wave_y + 1],
                     fill=(*HAIR_LIGHT, a))

# ─── 4. Hood beneath hair — dark fabric showing at nape and sides ─────────
# Dark robe hood peeks below and behind the hair volume
draw.ellipse([
    SEEKER_X - 44, CROWN_Y + 20,
    SEEKER_X + 46, HEAD_CY + HEAD_H // 2 + 8,
], fill=(28, 22, 16, 180))

# ─── 5. Small hair clips / pins (HELEN's signature detail) ────────────────
# Two tiny blue-purple clips visible near crown (one left, one right)
CLIP_COL  = (80, 90, 200)
CLIP_COL2 = (60, 70, 175)

for clip_x, clip_y, col in [
    (SEEKER_X - 28, CROWN_Y - 18, CLIP_COL),
    (SEEKER_X + 14, CROWN_Y - 8,  CLIP_COL2),
]:
    draw.ellipse([clip_x - 4, clip_y - 3, clip_x + 4, clip_y + 3],
                 fill=(*col, 210))
    draw.line([(clip_x - 3, clip_y), (clip_x + 3, clip_y)],
              fill=(100, 110, 220, 180), width=1)

# ─── 6. Freckles — forehead strip + cheeks ────────────────────────────────
rng_f = random.Random(88)
# Forehead: between hair end and blindfold top
FRECKLE_ZONE_TOP = max(CROWN_Y + 18, BF_Y - 22)
FRECKLE_ZONE_BOT = BF_Y - 9
if FRECKLE_ZONE_TOP < FRECKLE_ZONE_BOT:
    for _ in range(28):
        fx = rng_f.randint(SEEKER_X - 22, SEEKER_X + 22)
        fy = rng_f.randint(FRECKLE_ZONE_TOP, FRECKLE_ZONE_BOT)
        dist_bf = max(0, FRECKLE_ZONE_BOT - fy) / max(1, FRECKLE_ZONE_BOT - FRECKLE_ZONE_TOP)
        a = int(rng_f.randint(55, 110) * (0.4 + 0.6 * dist_bf))
        sz = rng_f.randint(1, 2)
        draw.ellipse([fx - sz, fy - sz, fx + sz, fy + sz],
                     fill=(*FRECKLE_COL, min(255, a)))
else:
    rng_f.random()  # advance state so later calls are consistent

# Cheek freckles — below blindfold edge, visible on cheek curves
CHEEK_BOT = BF_Y + 26
for _ in range(20):
    fx = rng_f.randint(SEEKER_X - 22, SEEKER_X + 22)
    fy = rng_f.randint(BF_Y + 9, CHEEK_BOT)
    a  = rng_f.randint(28, 68)
    sz = 1
    draw.ellipse([fx - sz, fy - sz, fx + sz, fy + sz],
                 fill=(*FRECKLE_COL, a))

# ─── 7. Re-draw blindfold cleanly over the hair (crisp band) ─────────────
BF_W2 = HEAD_W + 4
# Main blindfold band
draw.rectangle([
    SEEKER_X - BF_W2 // 2, BF_Y - 8,
    SEEKER_X + BF_W2 // 2, BF_Y + 8,
], fill=(12, 9, 6, 252))
# Top edge — faint lighter line (linen weave catch)
draw.line([
    (SEEKER_X - BF_W2 // 2, BF_Y - 8),
    (SEEKER_X + BF_W2 // 2, BF_Y - 8),
], fill=(38, 30, 18, 120), width=1)
# Tie knot (right side — visible beside hair)
draw.ellipse([
    SEEKER_X + BF_W2 // 2 - 3, BF_Y - 5,
    SEEKER_X + BF_W2 // 2 + 12, BF_Y + 9,
], fill=(15, 11, 7, 220))

# ─── 8. Torchlight kiss on hair — left torch warm key light ──────────────
# Subtle amber gradient on left portion of hair (physically correct — torch is left)
for r in range(55, 5, -4):
    t    = r / 55
    a    = int(45 * (1 - t) ** 1.3)
    cr   = min(255, HAIR_LIGHT[0] + 30)
    cg   = min(255, HAIR_LIGHT[1] + 10)
    cb   = 5
    draw.ellipse([
        SEEKER_X - 50 - r // 2, CROWN_Y - 42 - r // 2,
        SEEKER_X - 50 + r // 2, CROWN_Y - 42 + r // 2,
    ], fill=(cr, cg, cb, a))

# Broad torch-fill wash on left side of hair
for y in range(CROWN_Y - 50, CROWN_Y + 50):
    for x in range(SEEKER_X - 50, SEEKER_X + 5):
        dist_l = math.sqrt((x - TORCH_L_X)**2 + (y - TORCH_L_Y)**2)
        a = int(35 * max(0, 1 - dist_l / 500))
        if a > 1:
            draw.point((x, y), fill=(245, 145, 10, a))

# ─── 9. Save ─────────────────────────────────────────────────────────────
img.save(DEST, "PNG")
print(f"V3 seed frame: {DEST}")

pixels = list(img.getdata())
luma   = sum(0.299 * r + 0.587 * g + 0.114 * b for r, g, b in pixels) / len(pixels)
print(f"Mean luma: {luma:.2f}/255  (target 35-55)")

if luma < 35:
    factor = 42 / max(luma, 1)
    img    = ImageEnhance.Brightness(img).enhance(factor)
    img.save(DEST, "PNG")
    pixels = list(img.getdata())
    luma2  = sum(0.299 * r + 0.587 * g + 0.114 * b for r, g, b in pixels) / len(pixels)
    print(f"After boost: {luma2:.2f}/255")

print("SHIP: shot1_initiation_seed_v3.png")
