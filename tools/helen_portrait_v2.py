#!/usr/bin/env python3
"""tools/helen_portrait_v2.py — Portrait v2: HELEN composited onto OS environment.

Fixes v1: Kling filled gradient background because seed had transparent BG.
v2: Pillow pre-composites HELEN onto #050508 + cyan orbit rings + amber kernel glow,
then submits that as the seed. Kling animates an image that already looks like the cockpit.

Storyboard target: Shot 2A / 5B — "presence without performance."
NON_SOVEREIGN · authority=false

Usage:
    source ~/.helen_env && python3 tools/helen_portrait_v2.py
"""
import json, math, os, sys, time, subprocess, urllib.request, urllib.error
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFilter
except ImportError:
    sys.exit("FAIL: pip install Pillow")

# ── Config ─────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent

def _load_env(path):
    env = {}
    try:
        for line in Path(path).read_text().splitlines():
            line = line.strip()
            if line.startswith("export "): line = line[7:]
            if "=" in line and not line.startswith("#"):
                k, _, v = line.partition("=")
                env[k.strip()] = v.strip().strip('"').strip("'")
    except Exception:
        pass
    return env

_e = _load_env(Path.home() / ".helen_env")
HF_ID             = _e.get("HIGGSFIELD_ID")      or os.environ.get("HIGGSFIELD_ID", "")
HF_SECRET         = _e.get("HIGGSFIELD_SECRET")  or os.environ.get("HIGGSFIELD_SECRET", "")
TELEGRAM_BOT_TOKEN= _e.get("TELEGRAM_BOT_TOKEN") or os.environ.get("TELEGRAM_BOT_TOKEN", "")

if not (HF_ID and HF_SECRET): sys.exit("FAIL: Higgsfield credentials missing")
if not TELEGRAM_BOT_TOKEN:    sys.exit("FAIL: TELEGRAM_BOT_TOKEN missing")

SEED      = Path.home() / "Desktop/helen-canonical-portrait001.png"
CHAT_ID   = 6624890918
HF_AUTH   = f"Key {HF_ID}:{HF_SECRET}"
HF_BASE   = "https://platform.higgsfield.ai"
OUT       = Path("/tmp/helen_portrait_v2"); OUT.mkdir(parents=True, exist_ok=True)
COMP_PATH = OUT / "helen_composite_v2.png"

# ── OS palette ─────────────────────────────────────────────────────────────
BG_COLOR   = (5, 5, 8)           # #050508
CYAN       = (0, 212, 255)
AMBER      = (255, 170, 0)
W, H       = 1920, 1080          # 16:9 output

# ── Build composite ─────────────────────────────────────────────────────────
print("[1/6] Compositing HELEN onto OS environment...")

# Base: deep black canvas
bg = Image.new("RGBA", (W, H), BG_COLOR + (255,))
draw = ImageDraw.Draw(bg)

CX, CY = W // 2, H // 2
R = min(W, H) * 0.34

# Starfield — faint cyan dots
import random; rng = random.Random(42)
for _ in range(20):
    fx, fy = rng.random(), rng.random()
    x, y = int(W * fx), int(H * fy)
    draw.ellipse([x-2, y-2, x+2, y+2], fill=CYAN + (28,))

# Depth rings (very faint)
for i, f in enumerate([1.55, 1.37, 1.18, 0.98, 0.76, 0.56, 0.36, 0.18]):
    a = int((6 + i * 2))
    r = int(R * f)
    draw.ellipse([CX-r, CY-r, CX+r, CY+r], outline=CYAN + (a,), width=1)

# Orbital rings — keyed to HELEN OS rings
RINGS = [
    (0.60, CYAN,           18),
    (0.74, (106, 79, 255), 12),
    (0.88, CYAN,           8),
    (1.02, (0, 255, 136),  8),
    (1.16, AMBER,          14),
    (1.30, (255, 106, 0),  6),
]
for oR, col, alpha in RINGS:
    r = int(R * oR)
    draw.ellipse([CX-r, CY-r, CX+r, CY+r], outline=col + (alpha,), width=1)

# Amber kernel glow (soft radial, below center)
glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
gd = ImageDraw.Draw(glow)
for radius in range(120, 0, -8):
    a = int(30 * (1 - radius / 120))
    gd.ellipse([CX-radius, CY-radius, CX+radius, CY+radius], fill=AMBER + (a,))
bg = Image.alpha_composite(bg, glow)

# Very faint phosphor label — "HELEN" at kernel
draw2 = ImageDraw.Draw(bg)
# small dots at CX, CY
draw2.ellipse([CX-4, CY-4, CX+4, CY+4], fill=AMBER + (120,))

# Load and composite HELEN portrait
helen = Image.open(SEED).convert("RGBA")
# Scale portrait to fill ~65% of height, centered slightly right
target_h = int(H * 0.88)
target_w = int(helen.width * target_h / helen.height)
helen = helen.resize((target_w, target_h), Image.LANCZOS)
# Position: center-right, bottom-anchored
px = (W - target_w) // 2 + int(W * 0.04)
py = H - target_h

bg.paste(helen, (px, py), helen)

# Subtle vignette — darken edges to ground her in the environment
vignette = Image.new("RGBA", (W, H), (0, 0, 0, 0))
vd = ImageDraw.Draw(vignette)
for i in range(80):
    a = int(160 * (i / 80) ** 2)
    vd.rectangle([i, i, W-i, H-i], outline=(0, 0, 0, a) if i < 2 else None)
# simpler: just darken corners with gradient
for i in range(60):
    a = int(90 * (1 - i/60))
    vd.rectangle([0, 0, W, i], fill=(0,0,0,a))          # top
    vd.rectangle([0, H-i, W, H], fill=(0,0,0,a))        # bottom

bg = Image.alpha_composite(bg, vignette)

# Save as RGB (Kling doesn't need alpha)
final = bg.convert("RGB")
final.save(COMP_PATH, "PNG")
print(f"      ✓ composite saved: {COMP_PATH}  ({COMP_PATH.stat().st_size/1024:.0f} KB)")

# ── Higgsfield helpers ──────────────────────────────────────────────────────
def hf_req(path, method="POST", body=None, timeout=30, raw_url=None):
    url = raw_url or (path if path.startswith("http") else f"{HF_BASE}/{path.lstrip('/')}")
    h = {"Authorization": HF_AUTH, "User-Agent": "higgsfield-client-py/1.0",
         "Accept": "application/json"}
    data = None
    if body is not None:
        data = json.dumps(body).encode(); h["Content-Type"] = "application/json"
    rq = urllib.request.Request(url, data=data, headers=h, method=method)
    try:
        with urllib.request.urlopen(rq, timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")

# ── Pipeline ─────────────────────────────────────────────────────────────────
print("[2/6] Request CDN upload URL...")
code, text = hf_req("/files/generate-upload-url", body={"content_type": "image/png"})
if code != 200: sys.exit(f"FAIL upload-url {code}: {text[:300]}")
info = json.loads(text)
public_url, upload_url = info["public_url"], info["upload_url"]
print(f"      OK — {public_url[:72]}...")

print("[3/6] Upload composite to CDN...")
put_req = urllib.request.Request(
    upload_url, data=COMP_PATH.read_bytes(),
    headers={"Content-Type": "image/png"}, method="PUT",
)
try:
    with urllib.request.urlopen(put_req, timeout=120) as r:
        print(f"      PUT {r.status} OK")
except urllib.error.HTTPError as e:
    sys.exit(f"FAIL PUT {e.code}: {e.read().decode()[:300]}")

PROMPT = (
    "5 seconds, 1080p, 16:9, 24fps. Cinematic, restrained. "
    "The background is already correct — dark void, faint cyan orbital rings, amber glow at center. "
    "Do NOT change the background. Keep it exactly as the seed shows. "
    "Subject: the woman — copper-red hair, blue-grey eyes, freckles, fair skin. "
    "Identity locked for all 5 seconds. No facial morph, no head turn, no pose change. "
    "MOTION ONLY: natural breath once, one slow blink, faint hair-tip movement from ambient air. "
    "The ambient orbital rings pulse very faintly. The amber kernel glow breathes once. "
    "MOOD: she is observing, governing. Direct gaze at lens. No smile. Absolute stillness except breath. "
    "FORBIDDEN: background change, gradient fill, colour wash, zoom, push, extra figures, text, watermark."
)

print("[4/6] Submit Kling I2V (5s, 1080p, 16:9)...")
payload = {
    "prompt":      PROMPT,
    "input_image": {"type": "image_url", "image_url": public_url},
    "duration":    5, "resolution": "1080", "aspect_ratio": "16:9",
}
code, text = hf_req("/kling", body=payload)
if code not in (200, 201, 202):
    if code == 403: sys.exit("FAIL: 403 — not enough credits")
    sys.exit(f"FAIL Kling {code}: {text[:400]}")
sub = json.loads(text)
request_id = sub.get("request_id")
status_url  = sub.get("status_url")
print(f"      request_id: {request_id}")

print("[5/6] Polling (max 6 min)...")
deadline = time.time() + 360
out_path = None; last_status = "?"; n = 0
while time.time() < deadline:
    if status_url and status_url.startswith("http"):
        code, text = hf_req(status_url, raw_url=status_url, method="GET")
    else:
        code, text = hf_req(f"/requests/{request_id}/status", method="GET")
    try:    data = json.loads(text); status = data.get("status", "?")
    except: status = text[:60]
    n += 1
    if status != last_status or n % 6 == 0: print(f"      [{n}] {status}")
    last_status = status
    if status in ("COMPLETED", "completed"):
        output_url = (data.get("output_url") or data.get("video_url")
            or (data.get("video") or {}).get("url")
            or (data.get("outputs") or [{}])[0].get("url"))
        if not output_url: sys.exit(f"FAIL: no output URL: {json.dumps(data)[:400]}")
        out_path = OUT / "portrait_v2.mp4"
        urllib.request.urlretrieve(output_url, out_path)
        print(f"      ✓ {out_path}  ({out_path.stat().st_size/1024:.0f} KB)")
        break
    if status in ("FAILED", "failed", "NSFW", "CANCELED", "cancelled"):
        sys.exit(f"FAIL {status}: {json.dumps(data)[:400]}")
    time.sleep(5)
else:
    sys.exit(f"TIMEOUT — last: {last_status}")

print("[6/6] Send to Telegram...")
caption = (
    "HELEN portrait v2 — OS environment composite\n"
    "Seed pre-composited: #050508 + cyan rings + amber kernel\n"
    "Kling I2V 5s 1080p 16:9 — identity locked\n"
    "authority=false · NON_SOVEREIGN · RATING_PENDING"
)
r = subprocess.run([
    "curl", "-s", "-X", "POST",
    f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo",
    "-F", f"chat_id={CHAT_ID}", "-F", f"video=@{out_path}", "-F", f"caption={caption}",
], capture_output=True, text=True, timeout=120)
resp = json.loads(r.stdout) if r.stdout else {}
if resp.get("ok"):
    print(f"      ✓ Telegram OK — message_id: {resp.get('result',{}).get('message_id')}")
else:
    print(f"      {r.stdout[:300]}")

# Save composite for review
import shutil
shutil.copy(COMP_PATH, OUT / "composite_preview.png")
print(f"\nComposite preview: {OUT}/composite_preview.png")
print("SHIP: portrait_v2 — authority=false · NON_SOVEREIGN")
print("Rate: identity hold / background / motion / mood")
