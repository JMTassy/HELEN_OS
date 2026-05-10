#!/usr/bin/env python3
"""
gravure_video.py — GOBLIN GRAVURE pipeline
DALL-E 3 → Higgsfield Kling I2V → Telegram

authority=false  canon=NO_SHIP  class=EPHEMERAL
"""
from __future__ import annotations
import json, os, sys, time, urllib.request, urllib.parse, pathlib, io

# ── Load env ──────────────────────────────────────────────
def _load_env():
    p = pathlib.Path.home() / ".helen_env"
    env = {}
    if p.exists():
        for line in p.read_text().splitlines():
            line = line.strip()
            if line.startswith("export "):
                line = line[7:]
            if "=" in line and not line.startswith("#"):
                k, _, v = line.partition("=")
                env[k.strip()] = v.strip().strip('"').strip("'")
    return env

_env = _load_env()
OPENAI_KEY   = _env.get("OPENAI_API_KEY", os.environ.get("OPENAI_API_KEY", ""))
HF_ID        = _env.get("HIGGSFIELD_ID", "")
HF_SECRET    = _env.get("HIGGSFIELD_SECRET", "")
TG_TOKEN     = _env.get("TELEGRAM_BOT_TOKEN", "")
TG_CHAT_ID   = "6624890918"
HF_BASE      = "https://platform.higgsfield.ai"
HF_AUTH      = f"{HF_ID}:{HF_SECRET}"
UA           = "HELEN-GOBLIN/1.0"

PROMPT_IMAGE = """Medieval illuminated manuscript folio, single central figure,
gold leaf on dark parchment, hyper-detailed engraving style.
The figure is a superposition of: Sri Yantra nine-triangle mountain,
Metatron's Cube 13-circle structure, Tibetan Kalachakra mandala,
Rosicrucian cosmic diagram, 16-petal lotus. The face belongs to no gender,
no race — pure geometric symmetry that suggests a face. Concentric rings
of sacred geometry emanate outward. Outer border: single continuous
Celtic-Arabic knotwork line, never crossing, 72 divisions containing
Hebrew, Sanskrit, and alchemical glyphs simultaneously. Color palette:
iron oxide / raw umber base, gold leaf at every geometric apex, electric
cobalt at bindu point. No narrative. No story. Pure topological information.
Hyperdetailed. Printmaking. William Blake meets the Voynich Manuscript meets
Ernst Haeckel meets Tibetan thangka. Ultra-high-res, masterwork."""

PROMPT_VIDEO = (
    "The sacred mandala breathes. Gold leaf geometry slowly rotates. "
    "Sri Yantra triangles pulse with inner light. The bindu point glows electric cobalt. "
    "Concentric rings expand outward infinitely. Ancient. Timeless. No camera shake."
)

OUT_DIR = pathlib.Path(__file__).parent / "output"
OUT_DIR.mkdir(exist_ok=True)

# ─────────────────────────────────────────────────────────
def step(n, msg): print(f"\n[{n}] {msg}")
def ok(msg):      print(f"    ✓ {msg}")
def info(msg):    print(f"    · {msg}")

# ── 1. DALL-E 3 image generation ────────────────────────
def generate_image() -> pathlib.Path:
    step("1/5", "DALL-E 3 — generating gravure image")
    body = json.dumps({
        "model": "dall-e-3",
        "prompt": PROMPT_IMAGE,
        "size": "1024x1024",
        "quality": "hd",
        "style": "vivid",
        "n": 1,
    }).encode()
    req = urllib.request.Request(
        "https://api.openai.com/v1/images/generations",
        data=body,
        headers={
            "Authorization": f"Bearer {OPENAI_KEY}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            data = json.loads(r.read())
    except urllib.error.HTTPError as e:
        print(f"    ✗ DALL-E error: {e.code} {e.read()[:300]}")
        sys.exit(1)

    img_url  = data["data"][0]["url"]
    revised  = data["data"][0].get("revised_prompt", "")[:120]
    ok(f"image URL obtained")
    info(f"revised: {revised}…")

    # Download
    img_path = OUT_DIR / f"gravure_{int(time.time())}.png"
    with urllib.request.urlopen(img_url, timeout=60) as r:
        img_path.write_bytes(r.read())
    ok(f"saved → {img_path.name} ({img_path.stat().st_size//1024} KB)")
    return img_path, img_url

# ── 2. Higgsfield upload ─────────────────────────────────
def hf_req(path, method="POST", body=None, timeout=30, raw_url=None):
    import base64
    url = raw_url or (path if path.startswith("http") else f"{HF_BASE}/{path.lstrip('/')}")
    token = base64.b64encode(HF_AUTH.encode()).decode()
    h = {"Authorization": f"Basic {token}", "User-Agent": UA, "Accept": "application/json"}
    data = None
    if body is not None:
        h["Content-Type"] = "application/json"
        data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, headers=h, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()
    except Exception as e:
        return 0, str(e)

def upload_image(img_path: pathlib.Path) -> str:
    step("2/5", "Higgsfield — uploading image")
    # Get presigned upload URL
    code, text = hf_req("/files/generate-upload-url", body={"content_type": "image/png"})
    if code not in (200, 201):
        print(f"    ✗ presign failed: {code} {text[:200]}")
        sys.exit(1)
    d = json.loads(text)
    upload_url  = d.get("upload_url") or d.get("url", "")
    public_url  = d.get("public_url") or d.get("file_url", "")
    info(f"upload_url obtained · public_url: {public_url[:60]}…")

    # PUT image
    img_bytes = img_path.read_bytes()
    put_req = urllib.request.Request(
        upload_url, data=img_bytes,
        headers={"Content-Type": "image/png"},
        method="PUT",
    )
    with urllib.request.urlopen(put_req, timeout=60): pass
    ok(f"image uploaded ({len(img_bytes)//1024} KB)")
    return public_url

# ── 3. Kling I2V ──────────────────────────────────────────
def submit_kling(public_url: str) -> tuple[str, str]:
    step("3/5", "Higgsfield Kling — submitting I2V")
    payloads = [
        {"prompt": PROMPT_VIDEO,
         "input_image": {"type": "image_url", "image_url": public_url},
         "duration": 5, "resolution": "1080", "aspect_ratio": "1:1"},
        {"prompt": PROMPT_VIDEO,
         "input_image": {"type": "image_url", "image_url": public_url},
         "duration": 5},
        {"prompt": PROMPT_VIDEO, "image_url": public_url, "duration": 5},
    ]
    for i, payload in enumerate(payloads):
        code, text = hf_req("/kling", body=payload)
        info(f"attempt {i+1}: {code} — {text[:160]}")
        if code in (200, 201, 202):
            data = json.loads(text)
            rid  = data.get("request_id") or data.get("id", "")
            surl = data.get("status_url", f"{HF_BASE}/requests/{rid}/status")
            ok(f"request_id={rid}")
            return rid, surl
        if code == 403:
            print("    ✗ 403 — insufficient Higgsfield credits")
            sys.exit(1)
    print(f"    ✗ Kling submit failed")
    sys.exit(1)

def poll_kling(rid: str, surl: str, deadline_s: int = 600) -> str:
    step("3b/5", f"Polling (up to {deadline_s//60} min)…")
    deadline = time.time() + deadline_s
    while time.time() < deadline:
        code, text = hf_req(surl, raw_url=surl, method="GET")
        try:
            d      = json.loads(text)
            status = d.get("status", "?")
            pct    = d.get("progress", "")
            info(f"status={status} {pct}")
            if status in ("completed", "succeeded", "done"):
                vid = (d.get("output") or d.get("video_url") or
                       d.get("result", {}).get("video_url", ""))
                if not vid and isinstance(d.get("result"), list):
                    vid = d["result"][0]
                ok(f"video URL: {str(vid)[:80]}…")
                return str(vid)
            if status in ("failed", "error"):
                print(f"    ✗ Kling failed: {text[:300]}")
                sys.exit(1)
        except Exception as e:
            info(f"parse error: {e}")
        time.sleep(15)
    print("    ✗ timeout")
    sys.exit(1)

# ── 4. Download video ─────────────────────────────────────
def download_video(url: str) -> pathlib.Path:
    step("4/5", "Downloading video")
    out = OUT_DIR / f"gravure_{int(time.time())}.mp4"
    with urllib.request.urlopen(url, timeout=120) as r:
        out.write_bytes(r.read())
    ok(f"saved → {out.name} ({out.stat().st_size//1024} KB)")
    return out

# ── 5. Send to Telegram ───────────────────────────────────
def send_telegram_video(path: pathlib.Path, caption: str) -> None:
    step("5/5", f"Telegram → chat {TG_CHAT_ID}")
    boundary = "----TGboundary1234"
    vid_bytes = path.read_bytes()

    parts  = (f'--{boundary}\r\nContent-Disposition: form-data; name="chat_id"\r\n\r\n{TG_CHAT_ID}\r\n').encode()
    parts += (f'--{boundary}\r\nContent-Disposition: form-data; name="caption"\r\n\r\n{caption}\r\n').encode()
    parts += (f'--{boundary}\r\nContent-Disposition: form-data; name="video"; filename="{path.name}"\r\nContent-Type: video/mp4\r\n\r\n').encode()
    parts += vid_bytes
    parts += (f'\r\n--{boundary}--\r\n').encode()

    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendVideo"
    req = urllib.request.Request(
        url, data=parts,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            resp = json.loads(r.read())
            if resp.get("ok"):
                msg_id = resp["result"]["message_id"]
                ok(f"SENT · message_id={msg_id}")
            else:
                print(f"    ✗ Telegram error: {resp}")
    except urllib.error.HTTPError as e:
        print(f"    ✗ HTTP {e.code}: {e.read()[:300]}")

def send_telegram_photo(path: pathlib.Path, caption: str) -> None:
    """Fallback: send image if video pipeline fails."""
    boundary = "----TGphoto1234"
    img_bytes = path.read_bytes()
    parts  = (f'--{boundary}\r\nContent-Disposition: form-data; name="chat_id"\r\n\r\n{TG_CHAT_ID}\r\n').encode()
    parts += (f'--{boundary}\r\nContent-Disposition: form-data; name="caption"\r\n\r\n{caption}\r\n').encode()
    parts += (f'--{boundary}\r\nContent-Disposition: form-data; name="photo"; filename="{path.name}"\r\nContent-Type: image/png\r\n\r\n').encode()
    parts += img_bytes
    parts += (f'\r\n--{boundary}--\r\n').encode()
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendPhoto"
    req = urllib.request.Request(
        url, data=parts,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        resp = json.loads(r.read())
        if resp.get("ok"):
            ok(f"PHOTO SENT · message_id={resp['result']['message_id']}")

# ── MAIN ──────────────────────────────────────────────────
def main():
    print("\n══ GOBLIN GRAVURE PIPELINE ══")
    print("   authority=false · canon=NO_SHIP · class=EPHEMERAL\n")

    # 1 Image
    img_path, _img_url = generate_image()

    # 2 Upload to Higgsfield
    try:
        public_url = upload_image(img_path)
    except SystemExit:
        # Fallback: send image directly to Telegram
        print("\n  [FALLBACK] Higgsfield unavailable — sending image to Telegram")
        caption = (
            "GOBLIN GRAVURE UNIVERSALIS\n"
            "Medieval illuminated · Sri Yantra · Metatron · Kalachakra\n"
            "authority=false · canon=NO_SHIP\n"
            "HELEN OS · JMT"
        )
        send_telegram_photo(img_path, caption)
        print("\nSHIP: image sent (video pipeline unavailable)")
        return

    # 3 Kling I2V
    rid, surl = submit_kling(public_url)
    video_url  = poll_kling(rid, surl)

    # 4 Download
    vid_path = download_video(video_url)

    # 5 Telegram
    caption = (
        "GOBLIN GRAVURE UNIVERSALIS\n"
        "Medieval illuminated · Sri Yantra · Metatron · Kalachakra\n"
        "The mandala breathes · The bindu glows\n"
        "authority=false · canon=NO_SHIP\n"
        "HELEN OS · JMT"
    )
    send_telegram_video(vid_path, caption)
    print(f"\nSHIP: {vid_path.name} → Telegram chat {TG_CHAT_ID}")

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--use-image", metavar="PATH", help="Skip DALL-E, use existing image")
    ns = ap.parse_args()

    if ns.use_image:
        print("\n══ GOBLIN GRAVURE PIPELINE ══")
        print("   authority=false · canon=NO_SHIP · class=EPHEMERAL\n")
        img_path = pathlib.Path(ns.use_image)
        ok(f"using existing image: {img_path.name} ({img_path.stat().st_size//1024} KB)")

        try:
            public_url = upload_image(img_path)
        except SystemExit:
            print("\n  [FALLBACK] Higgsfield unavailable — sending image to Telegram")
            caption = (
                "GOBLIN GRAVURE UNIVERSALIS\n"
                "Medieval illuminated · Sri Yantra · Metatron · Kalachakra\n"
                "authority=false · canon=NO_SHIP\n"
                "HELEN OS · JMT"
            )
            send_telegram_photo(img_path, caption)
            print("\nSHIP: image sent (video pipeline unavailable)")
            sys.exit(0)

        rid, surl = submit_kling(public_url)
        video_url  = poll_kling(rid, surl)
        vid_path   = download_video(video_url)
        caption = (
            "GOBLIN GRAVURE UNIVERSALIS\n"
            "Medieval illuminated · Sri Yantra · Metatron · Kalachakra\n"
            "The mandala breathes · The bindu glows\n"
            "authority=false · canon=NO_SHIP\n"
            "HELEN OS · JMT"
        )
        send_telegram_video(vid_path, caption)
        print(f"\nSHIP: {vid_path.name} → Telegram chat {TG_CHAT_ID}")
    else:
        main()
