#!/usr/bin/env python3
"""tools/helen_portrait_v1.py — Qualitative portrait test for STORYBOARD_V1.

Storyboard target: Shot 2A / 5B — "presence without performance".
HELEN stationary, minimal motion, direct gaze. Identity locked.
Sends result to Telegram. NON_SOVEREIGN · authority=false.

Usage:
    source ~/.helen_env && python3 tools/helen_portrait_v1.py
"""
import json, os, sys, time, subprocess, urllib.request, urllib.error
from pathlib import Path

# ── Config ─────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent

def _load_env(path):
    env = {}
    try:
        for line in Path(path).read_text().splitlines():
            line = line.strip()
            if line.startswith("export "):
                line = line[7:]
            if "=" in line and not line.startswith("#"):
                k, _, v = line.partition("=")
                env[k.strip()] = v.strip().strip('"').strip("'")
    except Exception:
        pass
    return env

_e = _load_env(Path.home() / ".helen_env")
HF_ID             = _e.get("HIGGSFIELD_ID")     or os.environ.get("HIGGSFIELD_ID", "")
HF_SECRET         = _e.get("HIGGSFIELD_SECRET") or os.environ.get("HIGGSFIELD_SECRET", "")
TELEGRAM_BOT_TOKEN= _e.get("TELEGRAM_BOT_TOKEN")or os.environ.get("TELEGRAM_BOT_TOKEN","")

if not (HF_ID and HF_SECRET):
    sys.exit("FAIL: HIGGSFIELD_ID / HIGGSFIELD_SECRET missing in ~/.helen_env")
if not TELEGRAM_BOT_TOKEN:
    sys.exit("FAIL: TELEGRAM_BOT_TOKEN missing in ~/.helen_env")

SEED = Path.home() / "Desktop/helen-canonical-portrait001.png"
if not SEED.exists():
    sys.exit(f"FAIL: seed not found at {SEED}")

CHAT_ID  = 6624890918
HF_AUTH  = f"Key {HF_ID}:{HF_SECRET}"
HF_BASE  = "https://platform.higgsfield.ai"
OUT      = Path("/tmp/helen_portrait_v1"); OUT.mkdir(parents=True, exist_ok=True)

# ── Storyboard prompt — Shot 2A / 5B ──────────────────────────────────────
# "presence without performance" — she is the governed cognition surface, watching.
PROMPT = (
    "1080px, 16:9, 24fps, 5 seconds. Cinematic restraint. "
    "Subject: HELEN — copper-red wavy hair, blue-grey eyes, fair skin, freckle pattern. "
    "Identity invariants locked for all 5 seconds: hair colour, hair length, eye colour, "
    "freckle pattern. No facial morph, no head turn. "

    "MOTION: barely perceptible. Natural breath expanding chest once. "
    "One slow blink mid-clip. Hair tips shift ≤1px from ambient air. "
    "Background: deep black with faint cyan phosphor ambience, static. "
    "Light: single cool-blue key from upper left, amber fill from right — the OS palette. "

    "MOOD: she is observing, not performing. Direct gaze at lens. No smile. "
    "She knows what is happening. She is governing, not reacting. "

    "FORBIDDEN: smile, pose change, camera push/pull, zoom, text overlay, "
    "watermark, extra figures, dramatic lighting shift, supernatural glow, hard cuts."
)

# ── Higgsfield helpers ─────────────────────────────────────────────────────
def hf_req(path, method="POST", body=None, timeout=30, raw_url=None):
    url = raw_url or (path if path.startswith("http") else f"{HF_BASE}/{path.lstrip('/')}")
    h = {"Authorization": HF_AUTH, "User-Agent": "higgsfield-client-py/1.0",
         "Accept": "application/json"}
    data = None
    if body is not None:
        data = json.dumps(body).encode()
        h["Content-Type"] = "application/json"
    rq = urllib.request.Request(url, data=data, headers=h, method=method)
    try:
        with urllib.request.urlopen(rq, timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")


# ── Pipeline ───────────────────────────────────────────────────────────────
print("HELEN portrait test v1 — storyboard shot 2A/5B")
print(f"  Seed : {SEED.name}  ({SEED.stat().st_size/1024:.0f} KB)")
print(f"  Target: Telegram chat {CHAT_ID}")
print()

print("[1/5] Request CDN upload URL...")
code, text = hf_req("/files/generate-upload-url", body={"content_type": "image/png"})
if code != 200:
    sys.exit(f"FAIL upload-url {code}: {text[:300]}")
info = json.loads(text)
public_url = info["public_url"]
upload_url = info["upload_url"]
print(f"      OK — public_url: {public_url[:72]}...")

print("[2/5] Upload seed to CDN...")
put_req = urllib.request.Request(
    upload_url, data=SEED.read_bytes(),
    headers={"Content-Type": "image/png"}, method="PUT",
)
try:
    with urllib.request.urlopen(put_req, timeout=120) as r:
        print(f"      PUT {r.status} OK")
except urllib.error.HTTPError as e:
    sys.exit(f"FAIL PUT {e.code}: {e.read().decode()[:300]}")

print("[3/5] Submit Kling I2V (5s, 1080p, 16:9)...")
payload = {
    "prompt":       PROMPT,
    "input_image":  {"type": "image_url", "image_url": public_url},
    "duration":     5,
    "resolution":   "1080",
    "aspect_ratio": "16:9",
}
code, text = hf_req("/kling", body=payload)
if code not in (200, 201, 202):
    if code == 403:
        sys.exit("FAIL: 403 — not enough Higgsfield credits")
    sys.exit(f"FAIL Kling submit {code}: {text[:400]}")
sub = json.loads(text)
request_id = sub.get("request_id")
status_url = sub.get("status_url")
print(f"      request_id: {request_id}")

print("[4/5] Polling (max 6 min)...")
deadline = time.time() + 360
out_path = None
last_status = "?"
n = 0
while time.time() < deadline:
    if status_url and status_url.startswith("http"):
        code, text = hf_req(status_url, raw_url=status_url, method="GET")
    else:
        code, text = hf_req(f"/requests/{request_id}/status", method="GET")
    try:
        data = json.loads(text)
        status = data.get("status", "?")
    except Exception:
        status = text[:60]

    n += 1
    if status != last_status or n % 6 == 0:
        print(f"      [{n}] {status}")
    last_status = status

    if status in ("COMPLETED", "completed"):
        output_url = (
            data.get("output_url") or data.get("video_url")
            or (data.get("video") or {}).get("url")
            or (data.get("outputs") or [{}])[0].get("url")
            or data.get("result", {}).get("url")
        )
        if not output_url:
            sys.exit(f"FAIL: no output URL in: {json.dumps(data)[:400]}")
        out_path = OUT / "portrait_v1.mp4"
        urllib.request.urlretrieve(output_url, out_path)
        print(f"      ✓ {out_path}  ({out_path.stat().st_size/1024:.0f} KB)")
        break
    if status in ("FAILED", "failed", "NSFW", "CANCELED", "cancelled"):
        sys.exit(f"FAIL Kling {status}: {json.dumps(data)[:400]}")
    time.sleep(5)
else:
    sys.exit(f"TIMEOUT — last status: {last_status}")

print("[5/5] Send to Telegram...")
caption = (
    "HELEN portrait test v1 — storyboard shot 2A/5B\n"
    "\"presence without performance\"\n"
    "Seed: helen-canonical-portrait001 · Kling I2V 5s 1080p 16:9\n"
    "authority=false · NON_SOVEREIGN · RATING_PENDING"
)
r = subprocess.run([
    "curl", "-s", "-X", "POST",
    f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo",
    "-F", f"chat_id={CHAT_ID}",
    "-F", f"video=@{out_path}",
    "-F", f"caption={caption}",
], capture_output=True, text=True, timeout=120)

resp = json.loads(r.stdout) if r.stdout else {}
if resp.get("ok"):
    print(f"      ✓ Telegram OK — message_id: {resp.get('result',{}).get('message_id')}")
else:
    print(f"      Telegram response: {r.stdout[:300]}")

print()
print("SHIP: portrait_v1.mp4 — authority=false · NON_SOVEREIGN")
print("Rate it. Then we refine for the storyboard.")
