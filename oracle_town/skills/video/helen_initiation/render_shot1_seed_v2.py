#!/usr/bin/env python3
"""
Mystery Initiation — Shot 1 seed frame V2 (masterpiece grade)
Egyptian temple underground chamber. 1080 × 1920 (9:16).
Two robed figures at stone archway. Torchlight 3200K amber. Floor smoke.

Kling I2V seed: correct composition, strong read at small size,
cinematic palette, no AI gloss, no fantasy colour.
"""
import math, os, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance

W, H = 1080, 1920
OUT  = Path("/tmp/helen_initiation")
OUT.mkdir(parents=True, exist_ok=True)

# ── Palette (3200K torch room — no cool tones) ────────────────────────────────
BLACK      = (3,   2,   4)
DEEP_STONE = (38,  32,  24)
STONE      = (58,  50,  38)
STONE_LT   = (82,  72,  54)
STONE_HL   = (110, 95,  68)
TORCH_HOT  = (255, 230, 140)   # flame core
TORCH_MID  = (220, 160,  55)   # amber body
TORCH_COOL = (160, 100,  20)   # outer falloff
GOLD_DIM   = (180, 148,  80)   # decorative
SMOKE_COL  = (72,  68,  62)
DUST_COL   = (210, 195, 158)
ROBE_SEEK  = (30,  26,  18)    # linen-dark robe
ROBE_GUIDE = (20,  17,  12)    # near-black robe

def load_font(size, bold=False):
    candidates = [
        "/System/Library/Fonts/Supplemental/Times New Roman Bold.ttf" if bold
        else "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
        "/System/Library/Fonts/Supplemental/Georgia.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for c in candidates:
        if os.path.exists(c):
            try:
                return ImageFont.truetype(c, size)
            except Exception:
                pass
    return ImageFont.load_default()

# ── Base image ────────────────────────────────────────────────────────────────
img  = Image.new("RGB", (W, H), BLACK)
draw = ImageDraw.Draw(img, "RGBA")

# ─── 1. Background gradient — warm near-black, slight amber floor undertone ──
for y in range(H):
    f = y / H
    # Sky/ceiling: cooler dark; floor: warmer dark
    r = int(3  + 14 * f * f)
    g = int(2  + 8  * f * f)
    b = int(4  + 2  * f * f)
    draw.line([(0, y), (W, y)], fill=(r, g, b, 255))

# ─── 2. Stone archway — perspective-keyed trapezoid columns ──────────────────
# Columns taper inward toward top to suggest depth/height
COL_W_BOT  = 175
COL_W_TOP  = 148   # slightly narrower at top for perspective
LEFT_X_BOT = 30
LEFT_X_TOP = 48
RIGHT_X_BOT = W - 30 - COL_W_BOT
RIGHT_X_TOP = W - 48 - COL_W_TOP
COL_TOP    = H // 5      # columns start higher (more imposing)
LINTEL_Y   = COL_TOP
LINTEL_H   = 68

# Left column — trapezoid
draw.polygon([
    (LEFT_X_TOP, COL_TOP),
    (LEFT_X_TOP + COL_W_TOP, COL_TOP),
    (LEFT_X_BOT + COL_W_BOT, H),
    (LEFT_X_BOT, H),
], fill=(*STONE, 255))

# Right column — trapezoid
draw.polygon([
    (RIGHT_X_TOP, COL_TOP),
    (RIGHT_X_TOP + COL_W_TOP, COL_TOP),
    (RIGHT_X_BOT + COL_W_BOT, H),
    (RIGHT_X_BOT, H),
], fill=(*STONE, 255))

# Column shading — left column darker on right edge (shadow cast inward)
for i in range(COL_W_BOT):
    t    = i / COL_W_BOT
    # Left column: right-fade to shadow (light from left torch, shadow rightward)
    frac = 1 - t * 0.55
    r_c  = int(STONE[0] * frac)
    g_c  = int(STONE[1] * frac)
    b_c  = int(STONE[2] * frac)
    x_top = int(LEFT_X_TOP + i * COL_W_TOP / COL_W_BOT)
    x_bot = LEFT_X_BOT + i
    draw.line([(x_top, COL_TOP), (x_bot, H)], fill=(r_c, g_c, b_c, 255))

for i in range(COL_W_BOT):
    t    = i / COL_W_BOT
    # Right column: left-fade to shadow (light from right torch, shadow leftward)
    frac = 0.45 + t * 0.55
    r_c  = int(STONE[0] * frac)
    g_c  = int(STONE[1] * frac)
    b_c  = int(STONE[2] * frac)
    x_top = int(RIGHT_X_TOP + i * COL_W_TOP / COL_W_BOT)
    x_bot = RIGHT_X_BOT + i
    draw.line([(x_top, COL_TOP), (x_bot, H)], fill=(r_c, g_c, b_c, 255))

# Stone grain texture overlay on columns (seeded noise)
rng_tex = random.Random(13)
for _ in range(6000):
    # Left column grain
    gx = rng_tex.randint(LEFT_X_BOT, LEFT_X_BOT + COL_W_BOT - 1)
    gy = rng_tex.randint(COL_TOP, H - 1)
    ga = rng_tex.randint(4, 22)
    bright = rng_tex.choice([-1, 1])
    base = STONE_LT if bright == 1 else DEEP_STONE
    draw.point((gx, gy), fill=(*base, ga))
    # Right column grain
    gx2 = rng_tex.randint(RIGHT_X_BOT, RIGHT_X_BOT + COL_W_BOT - 1)
    gy2 = rng_tex.randint(COL_TOP, H - 1)
    ga2 = rng_tex.randint(4, 22)
    bright2 = rng_tex.choice([-1, 1])
    base2 = STONE_LT if bright2 == 1 else DEEP_STONE
    draw.point((gx2, gy2), fill=(*base2, ga2))

# Horizontal stone coursing lines (masonry joints)
for col_x_top, col_x_bot, cw_top, cw_bot in [
    (LEFT_X_TOP, LEFT_X_BOT, COL_W_TOP, COL_W_BOT),
    (RIGHT_X_TOP, RIGHT_X_BOT, COL_W_TOP, COL_W_BOT),
]:
    for course in range(8):
        cy = COL_TOP + 120 + course * 210
        if cy >= H: break
        t_frac = (cy - COL_TOP) / (H - COL_TOP)
        x_l = int(col_x_top + (col_x_bot - col_x_top) * t_frac)
        x_r = int(x_l + cw_top + (cw_bot - cw_top) * t_frac)
        # Joint line — darker
        draw.line([(x_l, cy), (x_r, cy)], fill=(22, 18, 12, 90), width=2)
        draw.line([(x_l, cy + 1), (x_r, cy + 1)], fill=(45, 38, 28, 40), width=1)

# Lintel — full-width stone beam
ARCH_L = int(LEFT_X_TOP + COL_W_TOP)   # archway opening left edge at lintel level
ARCH_R = RIGHT_X_TOP                    # archway opening right edge at lintel level
draw.rectangle([LEFT_X_TOP, LINTEL_Y, RIGHT_X_TOP + COL_W_TOP, LINTEL_Y + LINTEL_H],
               fill=(*STONE, 255))
# Lintel top shadow
draw.rectangle([LEFT_X_TOP, LINTEL_Y, RIGHT_X_TOP + COL_W_TOP, LINTEL_Y + 10],
               fill=(20, 16, 10, 255))
# Lintel bottom edge highlight
draw.rectangle([LEFT_X_TOP, LINTEL_Y + LINTEL_H - 3, RIGHT_X_TOP + COL_W_TOP, LINTEL_Y + LINTEL_H],
               fill=(18, 14, 8, 255))
# Lintel grain
rng_lint = random.Random(99)
for _ in range(800):
    gx = rng_lint.randint(LEFT_X_TOP, RIGHT_X_TOP + COL_W_TOP - 1)
    gy = rng_lint.randint(LINTEL_Y, LINTEL_Y + LINTEL_H - 1)
    draw.point((gx, gy), fill=(*STONE_HL, rng_lint.randint(8, 30)))

ARCH_T = LINTEL_Y + LINTEL_H

# ─── 3. Arch opening — deep black with atmospheric depth ─────────────────────
draw.rectangle([ARCH_L, ARCH_T, ARCH_R, H], fill=(*BLACK, 255))

# Atmospheric haze inside arch — slightly lighter near entrance edge
for x in range(ARCH_L, ARCH_R):
    edge_dist_l = (x - ARCH_L) / (ARCH_R - ARCH_L)
    edge_dist_r = 1 - edge_dist_l
    edge_glow   = min(edge_dist_l, edge_dist_r) * 2   # 0 at edge, 1 at center
    alpha = int(30 * (1 - edge_glow))
    if alpha > 1:
        draw.line([(x, ARCH_T), (x, H)], fill=(12, 10, 6, alpha))

# ─── 4. Egyptian hieroglyphs (column bas-relief) — geometric symbols ──────────
rng_h = random.Random(42)

def draw_hieroglyph_band(draw, col_x, col_w, y_center, alpha_base, col_x_top, cw_top, cw_bot):
    """Draw a small cluster of 3-4 simplified Egyptian symbol forms."""
    # Perspective-correct x positions
    t_frac = (y_center - COL_TOP) / max(1, H - COL_TOP)
    x_l    = int(col_x_top + (col_x - col_x_top) * t_frac)
    x_r    = x_l + int(cw_top + (cw_bot - cw_top) * t_frac)
    margin = int(20 * (1 + t_frac))
    x_l   += margin
    x_r   -= margin
    if x_r <= x_l + 20: return

    slot_w = (x_r - x_l) // 4
    col_fill = (STONE_LT[0], STONE_LT[1], STONE_LT[2], alpha_base)
    col_dark = (DEEP_STONE[0], DEEP_STONE[1], DEEP_STONE[2], alpha_base + 10)

    symbols = rng_h.sample(['ankh', 'eye', 'cartouche', 'feather', 'bird', 'bar'], min(4, slot_w // 10 + 1))
    for si, sym in enumerate(symbols[:4]):
        sx = x_l + si * slot_w + slot_w // 2
        sy = y_center

        if sym == 'ankh':
            # Cross + loop
            draw.line([(sx, sy - 14), (sx, sy + 14)], fill=col_fill, width=2)
            draw.line([(sx - 9, sy - 2), (sx + 9, sy - 2)], fill=col_fill, width=2)
            draw.ellipse([sx - 7, sy - 20, sx + 7, sy - 8], outline=col_fill, width=1)

        elif sym == 'eye':
            # Eye of Horus — simplified
            draw.arc([sx - 11, sy - 6, sx + 11, sy + 6], 0, 180, fill=col_fill, width=1)
            draw.arc([sx - 11, sy - 6, sx + 11, sy + 6], 180, 360, fill=col_dark, width=1)
            draw.ellipse([sx - 3, sy - 3, sx + 3, sy + 3], fill=col_dark)
            draw.line([(sx + 10, sy + 2), (sx + 16, sy + 10)], fill=col_fill, width=1)

        elif sym == 'cartouche':
            # Oval outline
            draw.ellipse([sx - 10, sy - 18, sx + 10, sy + 18], outline=col_fill, width=1)
            # Interior — random horizontal lines as text
            for li in range(3):
                ly = sy - 10 + li * 7
                draw.line([(sx - 6, ly), (sx + 6, ly)], fill=col_dark, width=1)

        elif sym == 'feather':
            # Ma'at feather — vertical stroke with serrated edge
            draw.line([(sx, sy - 18), (sx, sy + 8)], fill=col_fill, width=2)
            for fi in range(5):
                fy = sy - 14 + fi * 5
                draw.line([(sx, fy), (sx + 7 - fi, fy - 2)], fill=col_fill, width=1)
                draw.line([(sx, fy), (sx - 7 + fi, fy - 2)], fill=col_fill, width=1)

        elif sym == 'bird':
            # Bird profile — head bump + body + tail
            draw.arc([sx - 8, sy - 14, sx + 2, sy - 4], 0, 180, fill=col_fill, width=1)
            draw.line([(sx - 8, sy - 9), (sx + 10, sy - 3)], fill=col_fill, width=1)
            draw.line([(sx + 10, sy - 3), (sx + 14, sy - 10)], fill=col_fill, width=1)

        else:  # bar — simple horizontal score
            draw.line([(sx - 10, sy), (sx + 10, sy)], fill=col_fill, width=2)
            draw.line([(sx - 7, sy - 5), (sx + 7, sy - 5)], fill=col_fill, width=1)
            draw.line([(sx - 4, sy + 5), (sx + 4, sy + 5)], fill=col_fill, width=1)

# Place hieroglyph bands on each column, 5 bands each
for band_i in range(5):
    base_y = ARCH_T + 140 + band_i * 280
    if base_y > H - 120: break
    alpha  = max(12, 38 - band_i * 4)   # fade as we go down into shadow
    draw_hieroglyph_band(draw, LEFT_X_BOT, COL_W_BOT, base_y, alpha,
                         LEFT_X_TOP, COL_W_TOP, COL_W_BOT)
    draw_hieroglyph_band(draw, RIGHT_X_BOT, COL_W_BOT, base_y, alpha,
                         RIGHT_X_TOP, COL_W_TOP, COL_W_BOT)

# ─── 5. Torch sconces + multi-layer corona ────────────────────────────────────
def torch_corona(draw, cx, cy):
    """Multi-layer radial glow: hot white core → amber → warm shadow."""
    layers = [
        (320, TORCH_COOL,  35, 2.2),
        (200, TORCH_MID,   80, 1.8),
        (100, TORCH_MID,  140, 1.4),
        ( 45, TORCH_HOT,  200, 1.0),
        ( 18, (255,248,200), 255, 0.8),
    ]
    for r_max, col, peak_a, falloff in layers:
        for r in range(r_max, 0, -3):
            t  = (r / r_max) ** falloff
            a  = int(peak_a * (1 - t))
            cr = min(255, int(col[0] * (1 - t * 0.2)))
            cg = min(255, int(col[1] * (1 - t * 0.5)))
            cb = min(255, int(col[2] * (1 - t * 0.9)))
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(cr, cg, cb, a))

# Torch positions — mounted on inner face of columns, half-way up the visible section
TORCH_L_X = ARCH_L - 10   # just inside left arch edge
TORCH_L_Y = int(ARCH_T + (H - ARCH_T) * 0.28)
TORCH_R_X = ARCH_R + 10
TORCH_R_Y = int(ARCH_T + (H - ARCH_T) * 0.28)

torch_corona(draw, TORCH_L_X, TORCH_L_Y)
torch_corona(draw, TORCH_R_X, TORCH_R_Y)

# Torch bracket + flame shape
for tx, ty in [(TORCH_L_X, TORCH_L_Y), (TORCH_R_X, TORCH_R_Y)]:
    # Bracket arm (horizontal peg into wall)
    draw.rectangle([tx - 5, ty - 5, tx + 5, ty + 28], fill=(65, 55, 40, 240))
    # Torch cup
    draw.polygon([
        (tx - 9, ty - 2),
        (tx + 9, ty - 2),
        (tx + 6, ty + 16),
        (tx - 6, ty + 16),
    ], fill=(80, 65, 48, 255))
    # Flame — tapered teardrop
    draw.ellipse([tx - 8, ty - 32, tx + 8, ty - 4], fill=(TORCH_HOT[0], TORCH_HOT[1], 100, 220))
    draw.polygon([
        (tx - 5, ty - 16),
        (tx + 5, ty - 16),
        (tx,     ty - 40),
    ], fill=(255, 200, 60, 200))

# ─── 6. Torchlight floor spill ───────────────────────────────────────────────
FLOOR_Y = int(H * 0.70)
for y in range(FLOOR_Y, H):
    f       = (y - FLOOR_Y) / (H - FLOOR_Y)
    inv_f   = 1 - f
    row_a   = int(60 * inv_f * inv_f)
    for x in range(0, W):
        # Distance from each torch projected onto floor
        dl = math.sqrt((x - TORCH_L_X) ** 2 + (y - TORCH_L_Y) ** 2)
        dr = math.sqrt((x - TORCH_R_X) ** 2 + (y - TORCH_R_Y) ** 2)
        contrib = max(0, 1 - dl / 380) + max(0, 1 - dr / 380)
        a = int(row_a * min(1.0, contrib))
        if a > 1:
            draw.point((x, y), fill=(TORCH_MID[0], int(TORCH_MID[1] * 0.7), 8, a))

# ─── 7. Two robed figures — masterpiece anatomy ───────────────────────────────
FIG_BASE_Y = int(H * 0.91)

def draw_robe(draw, cx, base_y, scale, robe_col, lit_x, lit_strength, alpha=255):
    """Detailed robe: body, shoulders, head, hood shadow, cloth folds."""
    fh     = int(430 * scale)
    top    = base_y - fh
    # Robe widths
    shld_w = int(90 * scale)   # shoulder
    hip_w  = int(110 * scale)  # mid-hip
    hem_w  = int(155 * scale)  # hem

    # Robe body — multi-polygon for cloth drape feel
    # Main body
    draw.polygon([
        (cx - shld_w // 2, top + int(fh * 0.18)),
        (cx + shld_w // 2, top + int(fh * 0.18)),
        (cx + hem_w  // 2, base_y),
        (cx - hem_w  // 2, base_y),
    ], fill=(*robe_col, alpha))

    # Centre front fold — slightly lighter
    fold_light = tuple(min(255, c + 14) for c in robe_col)
    draw.polygon([
        (cx - 12, top + int(fh * 0.22)),
        (cx + 12, top + int(fh * 0.22)),
        (cx + 22, base_y),
        (cx - 22, base_y),
    ], fill=(*fold_light, min(255, alpha)))

    # Side shadow folds
    fold_dark = tuple(max(0, c - 10) for c in robe_col)
    for side in [-1, 1]:
        draw.polygon([
            (cx + side * (shld_w // 2 - 18), top + int(fh * 0.20)),
            (cx + side * (shld_w // 2),      top + int(fh * 0.20)),
            (cx + side * (hem_w  // 2),      base_y),
            (cx + side * (hem_w  // 2 - 22), base_y),
        ], fill=(*fold_dark, alpha))

    # Lit edge from nearest torch
    lit_dir    = 1 if cx > lit_x else -1   # which side faces torch
    edge_col   = (
        min(255, robe_col[0] + int(70 * lit_strength)),
        min(255, robe_col[1] + int(45 * lit_strength)),
        min(255, robe_col[2] + int(8  * lit_strength)),
    )
    for i in range(10):
        x_off = -i * lit_dir
        a_edge = max(0, alpha - i * 22)
        draw.line([
            (cx + lit_dir * hem_w // 2 + x_off, top + int(fh * 0.22)),
            (cx + lit_dir * hem_w // 2 + x_off, base_y)
        ], fill=(*edge_col, a_edge))

    # Shoulders — slight horizontal bulk
    draw.ellipse([
        cx - shld_w // 2 - 4, top + int(fh * 0.14),
        cx + shld_w // 2 + 4, top + int(fh * 0.28),
    ], fill=(*robe_col, alpha))

    # Neck + head
    neck_h = int(28 * scale)
    neck_w = int(22 * scale)
    draw.rectangle([
        cx - neck_w // 2, top + int(fh * 0.10),
        cx + neck_w // 2, top + int(fh * 0.18),
    ], fill=(*robe_col, alpha))

    head_w = int(52 * scale)
    head_h = int(66 * scale)
    head_cy = top + int(head_h * 0.54)
    draw.ellipse([
        cx - head_w // 2, head_cy - head_h // 2,
        cx + head_w // 2, head_cy + head_h // 2,
    ], fill=(*robe_col, alpha))

    # Hood fold shadow — darkens top of head
    draw.ellipse([
        cx - head_w // 2 + 5, head_cy - head_h // 2 + 4,
        cx + head_w // 2 - 5, head_cy + 6,
    ], fill=(0, 0, 0, 95))

    # Return head position for blindfold/face additions
    return head_cy, head_w, head_h, top, fh

# SEEKER — centered, slightly left, slightly forward (larger)
SEEKER_X = W // 2 - 40
seek_head_cy, seek_head_w, seek_head_h, seek_top, seek_fh = draw_robe(
    draw, SEEKER_X, FIG_BASE_Y, 1.0, ROBE_SEEK,
    lit_x=TORCH_L_X, lit_strength=0.55, alpha=255
)

# Blindfold — dark linen band across eyes
bf_y  = seek_head_cy - 2
bf_w  = seek_head_w + 6
draw.rectangle([SEEKER_X - bf_w // 2, bf_y - 7, SEEKER_X + bf_w // 2, bf_y + 7],
               fill=(10, 8, 5, 248))
# Blindfold tie knot on right side
draw.ellipse([SEEKER_X + bf_w // 2 - 4, bf_y - 4, SEEKER_X + bf_w // 2 + 10, bf_y + 8],
             fill=(12, 10, 7, 200))

# GUIDE — right of seeker, slightly smaller (further back)
GUIDE_X = W // 2 + 88
guide_head_cy, guide_head_w, guide_head_h, guide_top, guide_fh = draw_robe(
    draw, GUIDE_X, FIG_BASE_Y - 18, 0.93, ROBE_GUIDE,
    lit_x=TORCH_R_X, lit_strength=0.45, alpha=232
)

# Guide hand on seeker's arm — forearm reaching left
ARM_BASE_Y = int(seek_top + seek_fh * 0.54)
# Forearm — tapered limb
draw.polygon([
    (GUIDE_X - 32, ARM_BASE_Y - 8),
    (GUIDE_X - 30, ARM_BASE_Y + 8),
    (SEEKER_X + 50, ARM_BASE_Y + 14),
    (SEEKER_X + 48, ARM_BASE_Y - 2),
], fill=(*ROBE_GUIDE, 220))
# Hand — small palm oval on seeker's arm
draw.ellipse([
    SEEKER_X + 44, ARM_BASE_Y - 10,
    SEEKER_X + 68, ARM_BASE_Y + 12,
], fill=(22, 18, 14, 210))

# ─── 8. Floor smoke / low mist ────────────────────────────────────────────────
# Three overlapping mist layers, different densities
for layer_seed in [200, 201, 202]:
    rng_s = random.Random(layer_seed)
    MIST_TOP = int(H * 0.80)
    MIST_BOT = H + 30
    for y in range(MIST_TOP, MIST_BOT, 1):
        f   = (y - MIST_TOP) / (MIST_BOT - MIST_TOP)
        inv = 1 - f
        for x in range(0, W, 2):
            noise  = rng_s.gauss(0, 40)
            cx_d   = abs(x + noise - W // 2) / (W * 0.6)
            a_base = int(18 * inv * max(0, 1 - cx_d))
            if a_base > 1:
                draw.point((x, y), fill=(*SMOKE_COL, a_base))

# ─── 9. Dust in torch beams — angled column of particles ─────────────────────
rng_d = random.Random(77)
for _ in range(420):
    # Left torch beam — particles in conical zone above-left of torch
    if rng_d.random() > 0.5:
        angle = rng_d.uniform(-30, 30)
        dist  = rng_d.uniform(30, 310)
        px    = int(TORCH_L_X + dist * math.sin(math.radians(angle)))
        py    = int(TORCH_L_Y - dist * math.cos(math.radians(angle)) * 0.6)
        if 0 <= px < W and 0 <= py < H:
            beam_dist = math.sqrt((px - TORCH_L_X)**2 + (py - TORCH_L_Y)**2)
            a  = int(65 * max(0, 1 - beam_dist / 320))
            sz = rng_d.randint(1, 2)
            draw.ellipse([px - sz, py - sz, px + sz, py + sz],
                         fill=(*DUST_COL, a))
    else:
        # Right torch beam
        angle = rng_d.uniform(-30, 30)
        dist  = rng_d.uniform(30, 310)
        px    = int(TORCH_R_X + dist * math.sin(math.radians(angle)))
        py    = int(TORCH_R_Y - dist * math.cos(math.radians(angle)) * 0.6)
        if 0 <= px < W and 0 <= py < H:
            beam_dist = math.sqrt((px - TORCH_R_X)**2 + (py - TORCH_R_Y)**2)
            a  = int(65 * max(0, 1 - beam_dist / 320))
            sz = rng_d.randint(1, 2)
            draw.ellipse([px - sz, py - sz, px + sz, py + sz],
                         fill=(*DUST_COL, a))

# ─── 10. Overhead shaft of light (divine source from above) ──────────────────
# Narrow vertical shaft, slightly warm, fading as it falls
for y in range(0, int(H * 0.62)):
    progress = y / (H * 0.62)
    shaft_w  = int(55 + progress * 90)   # widens as it falls
    alpha    = int(12 * (1 - progress ** 1.2))
    if alpha < 1: break
    cx_shaft = W // 2
    draw.rectangle([cx_shaft - shaft_w // 2, y, cx_shaft + shaft_w // 2, y + 1],
                   fill=(DUST_COL[0], DUST_COL[1], int(DUST_COL[2] * 0.85), alpha))

# ─── 11. Heavy vignette — draws eye to archway centre ────────────────────────
vig  = Image.new("RGBA", (W, H), (0, 0, 0, 0))
vd   = ImageDraw.Draw(vig)
# Elliptical vignette — wider horizontally
R_X, R_Y = W * 0.55, H * 0.48
for step in range(80):
    t    = step / 80
    r_x  = int(R_X * (1 - t))
    r_y  = int(R_Y * (1 - t))
    a    = int(210 * (t ** 1.6))
    vd.ellipse([W // 2 - r_x, H // 2 - r_y, W // 2 + r_x, H // 2 + r_y],
               fill=(0, 0, 0, a))
img.paste(Image.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, 0)), vig),
          mask=vig.split()[3])

# ─── 12. Warm ambient bounce — subtle amber on floor near figures ─────────────
# Light bounce from floor (reflected torchlight)
for y in range(int(H * 0.84), H):
    f     = (y - H * 0.84) / (H - H * 0.84)
    for x in range(W // 2 - 220, W // 2 + 220):
        cx_d = abs(x - W // 2) / 220
        a    = int(18 * (1 - cx_d) * (1 - f))
        if a > 0:
            draw.point((x, y), fill=(TORCH_COOL[0], TORCH_COOL[1] - 30, 5, a))

# ─── 13. Watermark ────────────────────────────────────────────────────────────
F_TINY = load_font(18)
txt    = "HELEN OS · CONQUEST · CORSICA STUDIOS"
bb     = draw.textbbox((0, 0), txt, font=F_TINY)
tw     = bb[2] - bb[0]
draw.text(((W - tw) // 2, H - 52), txt,
          font=F_TINY, fill=(*GOLD_DIM, 52))

# ─── Save V2 ──────────────────────────────────────────────────────────────────
out_path = OUT / "shot1_initiation_seed_v2.png"
img.save(out_path, "PNG")
print(f"V2 seed frame: {out_path}")
print(f"Size: {W}x{H}")

# Luma check
pixels = list(img.getdata())
luma   = sum(0.299 * r + 0.587 * g + 0.114 * b for r, g, b in pixels) / len(pixels)
print(f"Mean luma: {luma:.2f}/255  (target 35-55)")

# If too dark, apply brightness boost
if luma < 35:
    print(f"Boosting brightness (luma {luma:.1f} < 35)…")
    factor = 42 / max(luma, 1)
    img    = ImageEnhance.Brightness(img).enhance(factor)
    img.save(out_path, "PNG")
    pixels = list(img.getdata())
    luma2  = sum(0.299 * r + 0.587 * g + 0.114 * b for r, g, b in pixels) / len(pixels)
    print(f"After boost: {luma2:.2f}/255")
elif luma > 60:
    print(f"Dimming (luma {luma:.1f} > 60)…")
    factor = 50 / luma
    img    = ImageEnhance.Brightness(img).enhance(factor)
    img.save(out_path, "PNG")

print("SHIP: shot1_initiation_seed_v2.png")
