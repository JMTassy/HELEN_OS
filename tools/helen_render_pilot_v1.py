#!/usr/bin/env python3
"""
HELEN render pilot v1 — DALL-E 3 seed + Higgsfield Kling I2V + Telegram delivery.

Non-sovereign tool. No ledger write (route via tools/helen_say.py separately).
Pipeline:
  1. DALL-E 3 generates a single photoreal seed frame (1024x1792, portrait, hd, natural)
  2. Download seed bytes locally
  3. Higgsfield /files/generate-upload-url → PUT bytes → public_url
  4. Higgsfield /kling I2V (5s, 1080p, 9:16) with the public_url + locked-camera prompt
  5. Poll until COMPLETED (max 5 min)
  6. Download mp4
  7. Telegram sendVideo to chat 6624890918
Cost: ~$0.08 (DALL-E) + ~15-25 credits (Higgsfield Kling) per run.
"""
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

# ── Credentials ──────────────────────────────────────────────────────────────
env: dict[str, str] = {}
helen_env = Path.home() / ".helen_env"
for ln in helen_env.read_text().splitlines():
    ln = ln.strip()
    if ln.startswith("export "):
        ln = ln[7:]
    if "=" in ln and not ln.startswith("#"):
        k, v = ln.split("=", 1)
        env[k.strip()] = v.strip().strip('"').strip("'")

OPENAI_API_KEY = env.get("OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY", "")
HF_ID = env.get("HIGGSFIELD_ID") or env.get("HF_API_KEY") or os.environ.get("HF_API_KEY", "")
HF_SECRET = env.get("HIGGSFIELD_SECRET") or env.get("HF_API_SECRET") or os.environ.get("HF_API_SECRET", "")
TELEGRAM_BOT_TOKEN = env.get("TELEGRAM_BOT_TOKEN") or os.environ.get("TELEGRAM_BOT_TOKEN", "")

if not OPENAI_API_KEY:
    sys.exit("FAIL: OPENAI_API_KEY not set in ~/.helen_env or env")
if not (HF_ID and HF_SECRET):
    sys.exit("FAIL: Higgsfield credentials missing in ~/.helen_env or env")
if not TELEGRAM_BOT_TOKEN:
    sys.exit("FAIL: TELEGRAM_BOT_TOKEN missing in ~/.helen_env or env")

OUT = Path("/tmp/helen_render_pilot_v1")
OUT.mkdir(parents=True, exist_ok=True)
CHAT_ID = 6624890918

# ── Prompts (canon-aligned: helen_initiation Egyptian mystery temple) ────────
SEED_PROMPT = (
    "photoreal documentary still, 9:16 portrait, cinematic 35mm anamorphic film, ISO 3200, slight grain. "
    "Two robed figures at the threshold of a massive limestone Egyptian mystery-temple archway. "
    "Seeker (centered, slightly left): young woman with vibrant orange-red wavy hair medium length, "
    "white linen blindfold band across eyes, dark near-black coarse linen robe, hands clasped at waist, "
    "head bowed 10 degrees, fair skin with freckles. "
    "Guide (slightly right and behind seeker): darker charcoal robe, right hand resting on seeker's left upper arm. "
    "Both face into the arch. "
    "Underground temple: limestone block archway, dressed stone columns with shallow bas-relief hieroglyph cartouches. "
    "Two iron-cage torches at column height 160cm casting amber 3200K directional light, "
    "floor warm spill in 80cm radius, central zone dim, no overhead source. Deep amber-to-black colour grade. "
    "Low ground mist 2cm at ankle height in torch spill zones. "
    "Coarse linen weave robes, real human skin texture with pores. "
    "Cinematic live-action film still. Photographic — not illustrated, not rendered. "
    "No CGI, no digital art, no anime, no game-engine look, no plastic textures, no smooth AI skin. "
    "No supernatural glow, no blue-violet tones, no extra figures, no text, no modern objects."
)

ANIMATION_PROMPT = (
    "1080px, 9:16, 24fps, 5s. "
    "Camera: locked tripod, zero movement, zero drift, zero push. 35mm anamorphic, f/2.4. "
    "Both figures completely motionless — no swaying, no breathing, no robe flutter. "
    "Torch flames flicker irregularly. Low ground mist drifts 2cm/sec leftward at floor level only — visible in torch spill zones. "
    "These are the only motion sources in the frame. "
    "Identity locked: seeker hair stays deep crimson-red wavy across all 5s, blindfold position fixed, robe folds preserved. "
    "Archway geometry and torch positions fixed throughout. "
    "No camera movement, no zoom, no figure movement, no supernatural glow, no extra figures."
)

# ── DALL-E 3 ─────────────────────────────────────────────────────────────────
print("[1/7] DALL-E 3 generating seed frame (1024x1792 hd natural)...")
oai_body = json.dumps({
    "model": "dall-e-3",
    "prompt": SEED_PROMPT,
    "n": 1,
    "size": "1024x1792",
    "quality": "hd",
    "style": "natural",
}).encode()
req = urllib.request.Request(
    "https://api.openai.com/v1/images/generations",
    data=oai_body,
    headers={
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    },
    method="POST",
)
try:
    with urllib.request.urlopen(req, timeout=120) as r:
        oai_data = json.loads(r.read())
except urllib.error.HTTPError as e:
    sys.exit(f"FAIL DALL-E: {e.code} {e.read().decode()[:300]}")

seed_url = oai_data["data"][0]["url"]
print(f"      seed url: {seed_url[:80]}...")

print("[2/7] Downloading seed bytes...")
seed_path = OUT / "seed.png"
urllib.request.urlretrieve(seed_url, seed_path)
print(f"      saved: {seed_path} ({seed_path.stat().st_size/1024:.0f} KB)")

# ── Higgsfield helper ────────────────────────────────────────────────────────
HF_AUTH = f"Key {HF_ID}:{HF_SECRET}"
HF_BASE = "https://platform.higgsfield.ai"
HF_UA = "higgsfield-client-py/1.0"


def hf_req(path: str, method: str = "POST", body=None, timeout: int = 30, raw_url: str | None = None):
    url = raw_url or (path if path.startswith("http") else f"{HF_BASE}/{path.lstrip('/')}")
    h = {"Authorization": HF_AUTH, "User-Agent": HF_UA, "Accept": "application/json"}
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


print("[3/7] Higgsfield CDN upload URL...")
code, text = hf_req("/files/generate-upload-url", body={"content_type": "image/png"})
if code != 200:
    sys.exit(f"FAIL upload-url: {code}: {text[:300]}")
info = json.loads(text)
public_url = info["public_url"]
upload_url = info["upload_url"]
print(f"      public_url: {public_url[:80]}...")

print("[4/7] PUT seed to CDN...")
put_req = urllib.request.Request(
    upload_url,
    data=seed_path.read_bytes(),
    headers={"Content-Type": "image/png"},
    method="PUT",
)
try:
    with urllib.request.urlopen(put_req, timeout=60) as r:
        print(f"      PUT {r.status} OK")
except urllib.error.HTTPError as e:
    sys.exit(f"FAIL PUT: {e.code} {e.read().decode()[:300]}")

print("[5/7] Submit Kling I2V (5s, 1080p, 9:16)...")
payload = {
    "prompt": ANIMATION_PROMPT,
    "input_image": {"type": "image_url", "image_url": public_url},
    "duration": 5,
    "resolution": "1080",
    "aspect_ratio": "9:16",
}
code, text = hf_req("/kling", body=payload)
if code not in (200, 201, 202):
    if code == 403:
        sys.exit("FAIL Kling: 403 Not enough credits — top up at platform.higgsfield.ai/billing")
    sys.exit(f"FAIL Kling submit {code}: {text[:400]}")
sub_data = json.loads(text)
request_id = sub_data.get("request_id")
status_url = sub_data.get("status_url")
print(f"      request_id: {request_id}")
print(f"      status_url: {status_url}")

print("[6/7] Polling until completed (max 5 min)...")
deadline = time.time() + 300
out_path = None
last_status = "?"
poll_n = 0
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

    poll_n += 1
    if status != last_status or poll_n % 6 == 0:
        print(f"      poll {poll_n}: status={status}")
    last_status = status

    if status in ("COMPLETED", "completed"):
        output_url = (
            data.get("output_url")
            or data.get("video_url")
            or (data.get("video") or {}).get("url")
            or (data.get("outputs") or [{}])[0].get("url")
            or data.get("result", {}).get("url")
        )
        if not output_url:
            sys.exit(f"FAIL no output URL in completed response: {json.dumps(data, indent=2)[:600]}")
        out_path = OUT / "pilot_v1.mp4"
        urllib.request.urlretrieve(output_url, out_path)
        print(f"      ✓ COMPLETED → {out_path} ({out_path.stat().st_size/1024:.0f} KB)")
        break
    if status in ("FAILED", "failed", "NSFW", "CANCELED", "cancelled"):
        sys.exit(f"FAIL Kling {status}: {json.dumps(data, indent=2)[:600]}")
    time.sleep(5)

if not out_path:
    sys.exit(f"TIMEOUT 5 min — check status_url manually: {status_url}")

# ── Telegram delivery ────────────────────────────────────────────────────────
print("[7/7] Telegram sendVideo...")
caption = (
    "HELEN render pilot v1 — DALL-E 3 seed + Higgsfield Kling I2V (5s, 1080p, 9:16). "
    "Egyptian mystery-temple threshold. Locked camera. Mist-drift only motion. "
    "Pipeline: photoreal seed (DALL-E hd/natural) → CDN upload → Kling I2V → ffmpeg-free direct download → Telegram."
)
result = subprocess.run(
    [
        "curl",
        "-s",
        "-X",
        "POST",
        f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo",
        "-F",
        f"chat_id={CHAT_ID}",
        "-F",
        f"video=@{out_path}",
        "-F",
        f"caption={caption}",
    ],
    capture_output=True,
    text=True,
    timeout=180,
)
try:
    tg_data = json.loads(result.stdout)
except Exception:
    sys.exit(f"FAIL telegram parse: {result.stdout[:400]}")
if not tg_data.get("ok"):
    sys.exit(f"FAIL telegram: {result.stdout[:400]}")
msg_id = tg_data["result"]["message_id"]
duration = tg_data["result"].get("video", {}).get("duration", "?")
print(f"      ✓ telegram msg_id={msg_id} duration={duration}s")

# ── Summary ──────────────────────────────────────────────────────────────────
print()
print("=== HELEN RENDER PILOT v1 — RESULT ===")
print(f"DALL-E seed:    {seed_path} ({seed_path.stat().st_size/1024:.0f} KB)")
print(f"Higgsfield CDN: {public_url}")
print(f"Kling output:   {out_path} ({out_path.stat().st_size/1024:.0f} KB)")
print(f"Telegram msg:   {msg_id} (chat={CHAT_ID}, duration={duration}s)")
