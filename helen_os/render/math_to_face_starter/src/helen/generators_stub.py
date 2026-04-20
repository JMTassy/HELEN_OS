"""Latent-dependent stub generators — v0.3 behavioral testbed.

Per operator 2026-04-20 v0.3 patch:
  - z_id     controls stable identity cues (freckle seed, eye spacing, palette anchor)
  - z_control controls pose shift + expression intensity
  - z_style  controls rendering cues (contrast, line weight, grain)

Stubs now actually produce different pixels for different latents, so the
downstream identity pipeline is testable end-to-end before real generators
are wired.
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from .types import ImageOut
from .latent import StructuredLatent


def _sigmoid(x: float) -> float:
    return 1.0 / (1.0 + np.exp(-x))


def _unit(x: np.ndarray) -> np.ndarray:
    return x / (np.linalg.norm(x) + 1e-8)


def _latent_to_palette(z_id: np.ndarray) -> tuple:
    v = _unit(z_id[:3].astype(np.float32))
    rgb = (np.clip((v * 0.5 + 0.5) * 255, 0, 255)).astype(np.int32)
    return int(rgb[0]), int(rgb[1]), int(rgb[2])


def _draw_face(draw, cx, cy, s, freckle_seed, accent=(255, 180, 180)):
    draw.ellipse([cx - s, cy - s * 1.25, cx + s, cy + s * 1.25], outline=(240, 240, 240), width=4)
    rng = np.random.default_rng(freckle_seed)
    for _ in range(60):
        fx = cx + rng.normal(scale=s * 0.35)
        fy = cy + rng.normal(scale=s * 0.25)
        r = max(1, int(abs(rng.normal()) * 2))
        draw.ellipse([fx - r, fy - r, fx + r, fy + r], fill=accent)


def _pose_shift(z_control: np.ndarray, max_px: int = 60):
    dx = int(np.clip(z_control[0] * max_px, -max_px, max_px))
    dy = int(np.clip(z_control[1] * max_px, -max_px, max_px))
    expr = float(_sigmoid(z_control[2] * 2.0))
    return dx, dy, expr


def _style_params(z_style: np.ndarray) -> dict:
    line = int(2 + 6 * _sigmoid(z_style[0] * 2.0))
    contrast = float(0.8 + 0.8 * _sigmoid(z_style[1] * 2.0))
    grain = float(_sigmoid(z_style[2] * 2.0))
    return {"line": line, "contrast": contrast, "grain": grain}


class GRealStub:
    """Photoreal-ish latent-dependent stub."""
    def __call__(self, z: StructuredLatent) -> ImageOut:
        W, H = 768, 1024
        base = Image.new("RGB", (W, H), (12, 12, 18))
        d = ImageDraw.Draw(base)
        pal = _latent_to_palette(z.z_id)
        dx, dy, expr = _pose_shift(z.z_control)
        st = _style_params(z.z_style)

        # background gradient
        for y in range(H):
            v = int(np.clip((y / H) * 80 + pal[2] * 0.1, 0, 255))
            d.line([(0, y), (W, y)], fill=(v // 3, v // 3, v))

        cx, cy = W // 2 + dx, H // 2 + dy - 80
        size = int(180 + 40 * (expr - 0.5))
        skin = (min(255, pal[0] + 80), min(255, pal[1] + 60), min(255, pal[2] + 60))
        d.ellipse([cx - size, cy - size * 1.25, cx + size, cy + size * 1.25], fill=skin)

        # freckles seeded by identity slice
        freckle_seed = int(abs(z.z_id[10]) * 1e6) % (2**31 - 1)
        _draw_face(d, cx, cy, size, freckle_seed, accent=(120, 80, 80))

        # eyes positions from z_id
        eye_sep = int(60 + 30 * _sigmoid(z.z_id[3] * 2.0))
        eye_y = cy - int(40 + 20 * _sigmoid(z.z_id[4] * 2.0))
        d.ellipse([cx - eye_sep - 20, eye_y - 10, cx - eye_sep + 20, eye_y + 10], fill=(20, 20, 30))
        d.ellipse([cx + eye_sep - 20, eye_y - 10, cx + eye_sep + 20, eye_y + 10], fill=(20, 20, 30))

        # contrast proxy
        base = base.point(lambda p: int(np.clip((p - 128) * st["contrast"] + 128, 0, 255)))

        # grain from z_style
        if st["grain"] > 0.1 and z.z_style.shape[0] > 5:
            grain_seed = int(abs(z.z_style[5]) * 1e6) % (2**31 - 1)
            rng = np.random.default_rng(grain_seed)
            noise = (rng.normal(scale=10 * st["grain"], size=(H, W, 1)) + 128).astype(np.uint8)
            noise_img = Image.fromarray(np.repeat(noise, 3, axis=2), mode="RGB").filter(ImageFilter.GaussianBlur(1))
            base = Image.blend(base, noise_img, alpha=0.12 * st["grain"])

        d = ImageDraw.Draw(base)
        d.text((24, 24), "HELEN_REAL (LATENT-DEPENDENT STUB)", fill=(255, 255, 255))
        return ImageOut(base)


class GTwinStub:
    """Manga-ish latent-dependent stub. Same z_id → same identity cues; different style register."""
    def __call__(self, z: StructuredLatent) -> ImageOut:
        W, H = 768, 1024
        base = Image.new("RGB", (W, H), (245, 245, 248))
        d = ImageDraw.Draw(base)
        dx, dy, expr = _pose_shift(z.z_control, max_px=50)
        st = _style_params(z.z_style)

        cx, cy = W // 2 + dx, H // 2 + dy - 80
        size = int(190 + 30 * (expr - 0.5))

        outline = (30, 30, 35)
        d.ellipse([cx - size, cy - size * 1.25, cx + size, cy + size * 1.25], outline=outline, width=st["line"])

        # freckles (same seed as REAL — shared identity signature across renderers)
        freckle_seed = int(abs(z.z_id[10]) * 1e6) % (2**31 - 1)
        rng = np.random.default_rng(freckle_seed)
        for _ in range(40):
            fx = cx + rng.normal(scale=size * 0.35)
            fy = cy + rng.normal(scale=size * 0.25)
            r = 2
            d.ellipse([fx - r, fy - r, fx + r, fy + r], fill=(90, 60, 60))

        # anime eyes derived from same z_id as REAL
        eye_sep = int(62 + 28 * _sigmoid(z.z_id[3] * 2.0))
        eye_y = cy - int(45 + 18 * _sigmoid(z.z_id[4] * 2.0))
        d.ellipse([cx - eye_sep - 28, eye_y - 18, cx - eye_sep + 28, eye_y + 18], fill=(10, 10, 15))
        d.ellipse([cx + eye_sep - 28, eye_y - 18, cx + eye_sep + 28, eye_y + 18], fill=(10, 10, 15))

        # comic shading controlled by style
        if z.z_style.shape[0] > 7:
            shade = int(230 - 80 * _sigmoid(z.z_style[7] * 2.0))
            d.pieslice([cx - size, cy - size * 1.25, cx + size, cy + size * 1.25], start=200, end=340,
                       fill=(shade, shade, shade))

        d.text((24, 24), "HELEN_TWIN (LATENT-DEPENDENT STUB)", fill=(20, 20, 20))
        return ImageOut(base)
