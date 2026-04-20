"""Pixel-dependent embedder stubs — gates are meaningful even before ArcFace wiring.

Per operator 2026-04-20 revision: embedders MUST depend on image pixels,
otherwise the gate is vacuous (passes/fails regardless of content).
"""
import numpy as np
import cv2
from PIL import Image


def _to_gray(img: Image.Image, size: int = 96) -> np.ndarray:
    arr = np.array(img.convert("RGB"))
    arr = cv2.resize(arr, (size, size), interpolation=cv2.INTER_AREA)
    gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
    return gray.astype(np.float32) / 255.0


def _unit(x: np.ndarray) -> np.ndarray:
    return x / (np.linalg.norm(x) + 1e-8)


class PixelHashEmbedder:
    """
    Fast, deterministic, image-dependent embedding:
      - computes DCT low-freq blocks (256 dims)
      - gradients histogram stats (mean / std / p90)
      - concat + trim/pad to requested dim
      - L2-normalize

    This is a placeholder until ArcFace (REAL) / anime embedder (TWIN) are wired.
    Enough signal for the calibration script to produce meaningful anchors.
    """
    def __init__(self, dim: int = 256):
        self.dim = dim

    def __call__(self, img: Image.Image) -> np.ndarray:
        g = _to_gray(img, 96)
        # DCT low-freq
        dct = cv2.dct(g)
        low = dct[:16, :16].reshape(-1)  # 256 dims
        # Gradient histogram (extra stability)
        gx = cv2.Sobel(g, cv2.CV_32F, 1, 0, ksize=3)
        gy = cv2.Sobel(g, cv2.CV_32F, 0, 1, ksize=3)
        mag = np.sqrt(gx * gx + gy * gy).reshape(-1)
        stats = np.array(
            [mag.mean(), mag.std(), np.percentile(mag, 90)],
            dtype=np.float32,
        )
        v = np.concatenate([low.astype(np.float32), stats], axis=0)
        # pad or trim
        if v.shape[0] < self.dim:
            v = np.pad(v, (0, self.dim - v.shape[0]))
        else:
            v = v[: self.dim]
        return _unit(v.astype(np.float32))
