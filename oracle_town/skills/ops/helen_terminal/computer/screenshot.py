"""
HELEN Terminal — screenshot capture.
Captures screen as artifact. No autonomous action on captured content.
Requires: Pillow (pip install Pillow)
"""
from __future__ import annotations

import hashlib
import io
from datetime import datetime, timezone
from pathlib import Path

from ..receipts.action_receipts import build_receipt

SCREENSHOTS_DIR = Path(__file__).resolve().parent.parent / "data" / "screenshots"


def capture_screen(region: tuple | None = None) -> dict:
    try:
        from PIL import ImageGrab
    except ImportError:
        raise ImportError("Screenshot requires: pip install Pillow")

    img = ImageGrab.grab(bbox=region)

    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    path = SCREENSHOTS_DIR / f"screenshot_{ts}.png"
    img.save(str(path), "PNG")

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    img_hash = hashlib.sha256(buf.getvalue()).hexdigest()[:24]

    artifact = {
        "type": "SCREENSHOT",
        "path": str(path),
        "size": {"width": img.width, "height": img.height},
        "image_hash": img_hash,
        "region": region,
        "content_preview": f"Screenshot {img.width}x{img.height} saved to {path.name}",
    }
    receipt = build_receipt("CAPTURE_SCREENSHOT", {"region": region}, artifact)
    return {"artifact": artifact, "receipt_id": receipt["receipt_id"], "path": str(path)}
