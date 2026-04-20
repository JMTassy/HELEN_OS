"""First-class duo compositor — shared framing + background + text.

Per operator 2026-04-20 revision: compositor is a first-class output mode,
not a downstream afterthought. Both renders share seed / framing policy /
background plate / pose alignment so they are compositionally synchronized.
"""
from PIL import Image, ImageDraw


def compose_duo_poster(
    img_real: Image.Image,
    img_twin: Image.Image,
    title: str = "HELEN / CONQUEST",
    subtitle: str = "HELEN OS METAVERSE",
) -> Image.Image:
    W, H = 1536, 1024
    canvas = Image.new("RGB", (W, H), (10, 10, 14))
    r = img_real.resize((768, 1024))
    t = img_twin.resize((768, 1024))
    canvas.paste(r, (0, 0))
    canvas.paste(t, (768, 0))
    d = ImageDraw.Draw(canvas)
    d.rectangle([0, 0, W, 90], fill=(0, 0, 0))
    d.text((30, 20), title, fill=(255, 255, 255))
    d.text((30, 55), subtitle, fill=(180, 180, 200))
    return canvas
