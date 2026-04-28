#!/usr/bin/env python3
"""
HELEN Director — Pilot 8C: Kling palindrome presence film, 30s.
NON_SOVEREIGN. ~15-25 credits (1 Kling Pro I2V × 5s).

Source: most recent canonical portrait (2026-04-23 close-up).

Pipeline:
  1. Upload portrait to Higgsfield CDN
  2. Kling Pro I2V → 5s living portrait clip
  3. ffmpeg palindrome: fwd(5s) → slow_fwd(10s) → rev(5s) → slow_rev(10s) = 30s
  4. Post-grade: vignette + grain + pulse
  5. Compress <49MB → Telegram
"""
from __future__ import annotations

import datetime, hashlib, json, subprocess, sys, time, urllib.request, urllib.error
from pathlib import Path

# ── Source image ─────────────────────────────────────────────────────────────
import os as _os
_avatar = Path(_os.path.expanduser("~/Desktop/HELEN_OS_PICS/HELEN_AVATAR"))
SOURCE = _avatar / "Capture d\u2019\u00e9cran 2026-04-23 \u00e0 18.55.36.png"

OUT_DIR = Path("/tmp/helen_temple")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Credentials ───────────────────────────────────────────────────────────────
_env: dict[str, str] = {}
for _ln in (Path(_os.path.expanduser("~")) / ".helen_env").read_text().splitlines():
    _ln = _ln.strip()
    if _ln.startswith("export "): _ln = _ln[7:]
    if "=" in _ln and not _ln.startswith("#"):
        k, v = _ln.split("=", 1); _env[k.strip()] = v.strip().strip('"').strip("'")

HF_ID     = _env.get("HIGGSFIELD_ID", _env.get("HF_API_KEY", ""))
HF_SECRET = _env.get("HIGGSFIELD_SECRET", _env.get("HF_API_SECRET", ""))
AUTH      = f"Key {HF_ID}:{HF_SECRET}"
BASE      = "https://platform.higgsfield.ai"
UA        = "higgsfield-client-py/1.0"
TG_TOKEN  = _env.get("TELEGRAM_BOT_TOKEN", "")

W, H, FPS = 1080, 1920, 24

PRESENCE_PROMPT = (
    "Cinematic portrait. Young woman, copper-red hair, blue-grey eyes, "
    "black outfit with gold details. Extreme close-up face, 9:16, 24fps. "
    "Camera locked. Subject alive: very subtle breath, eyes blink once slowly. "
    "No head movement, no body movement, no speaking. "
    "Shallow depth of field, cinematic bokeh background. "
    "Warm-violet ambient light, slight film grain. "
    "Sacred, still, present. No text. No action."
)


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")

def hf_req(path: str, method: str = "POST", body=None, timeout: int = 30,
           raw_url: str | None = None):
    url = raw_url or (path if path.startswith("http") else f"{BASE}/{path.lstrip('/')}")
    h = {"Authorization": AUTH, "User-Agent": UA, "Accept": "application/json"}
    data = None
    if body is not None:
        data = json.dumps(body).encode()
        h["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=h, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")


def upload_image(img: Path) -> str:
    content_type = "image/png" if img.suffix.lower() == ".png" else "image/jpeg"
    code, text = hf_req("/files/generate-upload-url", body={"content_type": content_type})
    if code != 200:
        raise SystemExit(f"ABORT: upload-url failed {code}: {text[:200]}")
    info = json.loads(text)
    public_url = info["public_url"]
    upload_url = info["upload_url"]
    put_req = urllib.request.Request(
        upload_url, data=img.read_bytes(),
        headers={"Content-Type": content_type}, method="PUT"
    )
    try:
        with urllib.request.urlopen(put_req, timeout=60) as r:
            print(f"      PUT {r.status} OK  CDN: {public_url[:80]}…")
    except urllib.error.HTTPError as e:
        raise SystemExit(f"ABORT: PUT {e.code}: {e.read().decode()[:200]}")
    return public_url


def submit_kling(public_url: str) -> tuple[str, str]:
    payloads = [
        {"prompt": PRESENCE_PROMPT,
         "input_image": {"type": "image_url", "image_url": public_url},
         "duration": 5, "resolution": "1080", "aspect_ratio": "9:16"},
        {"prompt": PRESENCE_PROMPT,
         "input_image": {"type": "image_url", "image_url": public_url},
         "duration": 5},
        {"prompt": PRESENCE_PROMPT, "image_url": public_url, "duration": 5},
    ]
    for i, payload in enumerate(payloads):
        code, text = hf_req("/kling", body=payload)
        print(f"      attempt {i+1}: {code} — {text[:180]}")
        if code in (200, 201, 202):
            data = json.loads(text)
            rid = data.get("request_id")
            surl = data.get("status_url", f"{BASE}/requests/{rid}/status")
            print(f"      request_id: {rid}")
            return rid, surl
        if code == 403:
            raise SystemExit("ABORT: 403 — insufficient credits")
    raise SystemExit(f"ABORT: Kling submit failed. Last: {code} {text[:200]}")


def poll(rid: str, surl: str, deadline_s: int = 600) -> str:
    deadline = time.time() + deadline_s
    t0 = time.time()
    while time.time() < deadline:
        code, text = hf_req(surl, raw_url=surl if surl.startswith("http") else None, method="GET")
        try:
            data = json.loads(text)
            status = data.get("status", "?")
        except Exception:
            status = text[:60]
        elapsed = int(time.time() - t0)
        if elapsed % 30 < 5:
            print(f"      t={elapsed}s  status={status}")
        if status in ("COMPLETED", "completed"):
            output_url = (
                data.get("output_url") or data.get("video_url") or
                (data.get("video") or {}).get("url") or
                (data.get("outputs") or [{}])[0].get("url") or
                data.get("result", {}).get("url")
            )
            if not output_url:
                raise SystemExit(f"ABORT: completed but no output URL: {text[:300]}")
            return output_url
        if status in ("FAILED", "failed", "NSFW", "CANCELED", "cancelled"):
            raise SystemExit(f"ABORT: Kling job {status}: {text[:300]}")
        time.sleep(5)
    raise SystemExit("ABORT: Kling polling timeout (10 min)")


def build_palindrome(raw_clip: Path, out: Path) -> bool:
    """fwd(5s) → slow_fwd(10s) → rev(5s) → slow_rev(10s) = 30s"""
    tmp = OUT_DIR / "p8c_tmp"
    tmp.mkdir(exist_ok=True)

    seg_fwd      = tmp / "seg_fwd.mp4"
    seg_slow_fwd = tmp / "seg_slow_fwd.mp4"
    seg_rev      = tmp / "seg_rev.mp4"
    seg_slow_rev = tmp / "seg_slow_rev.mp4"

    # Normalize source to 1080x1920 first
    normalized = tmp / "normalized.mp4"
    r = subprocess.run([
        "ffmpeg", "-y", "-i", str(raw_clip),
        "-vf", f"scale={W}:{H}:force_original_aspect_ratio=decrease,"
               f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:black,fps={FPS}",
        "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", "-an",
        str(normalized)
    ], capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-500:], file=sys.stderr); return False

    # fwd = normalized as-is (5s)
    r = subprocess.run([
        "ffmpeg", "-y", "-i", str(normalized),
        "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", "-an",
        str(seg_fwd)
    ], capture_output=True, text=True)
    if r.returncode != 0: print(r.stderr[-300:], file=sys.stderr); return False

    # slow_fwd = 2× slow (10s)
    r = subprocess.run([
        "ffmpeg", "-y", "-i", str(normalized),
        "-vf", "setpts=2.0*PTS", "-r", str(FPS),
        "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", "-an",
        str(seg_slow_fwd)
    ], capture_output=True, text=True)
    if r.returncode != 0: print(r.stderr[-300:], file=sys.stderr); return False

    # rev = reversed (5s)
    r = subprocess.run([
        "ffmpeg", "-y", "-i", str(normalized),
        "-vf", "reverse",
        "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", "-an",
        str(seg_rev)
    ], capture_output=True, text=True)
    if r.returncode != 0: print(r.stderr[-300:], file=sys.stderr); return False

    # slow_rev = 2× slow of reversed (10s)
    r = subprocess.run([
        "ffmpeg", "-y", "-i", str(seg_rev),
        "-vf", "setpts=2.0*PTS", "-r", str(FPS),
        "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", "-an",
        str(seg_slow_rev)
    ], capture_output=True, text=True)
    if r.returncode != 0: print(r.stderr[-300:], file=sys.stderr); return False

    # Post-grade concat via filter_complex
    post = (
        "vignette=PI/3.0,"
        "noise=c0s=8:c0f=t+u,"
        "geq=r='clip(r(X,Y)*(1+0.02*sin(2*3.14159*T/4)),0,255)':"
        "g='clip(g(X,Y)*(1+0.02*sin(2*3.14159*T/4)),0,255)':"
        "b='clip(b(X,Y)*(1+0.02*sin(2*3.14159*T/4)),0,255)',"
        "hue=s=1.18,"
        "colorbalance=rh=0.06:gh=0.02:bh=-0.04:rs=0.03:bs=0.04"
    )
    fade_in  = "geq=r='r(X,Y)*min(1,T/1.5)':g='g(X,Y)*min(1,T/1.5)':b='b(X,Y)*min(1,T/1.5)'"
    fade_out = "geq=r='r(X,Y)*min(1,(30-T)/1.5)':g='g(X,Y)*min(1,(30-T)/1.5)':b='b(X,Y)*min(1,(30-T)/1.5)'"

    concat_list = tmp / "concat.txt"
    concat_list.write_text(
        f"file '{seg_fwd}'\n"
        f"file '{seg_slow_fwd}'\n"
        f"file '{seg_rev}'\n"
        f"file '{seg_slow_rev}'\n"
    )
    raw_concat = tmp / "raw_concat.mp4"
    r = subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(concat_list), "-c", "copy", str(raw_concat)
    ], capture_output=True, text=True)
    if r.returncode != 0: print(r.stderr[-300:], file=sys.stderr); return False

    # Apply grade + fade
    r = subprocess.run([
        "ffmpeg", "-y", "-i", str(raw_concat),
        "-filter_complex",
        f"[0:v]{post}[graded];[graded]{fade_in}[fin];[fin]{fade_out}",
        "-t", "30",
        "-c:v", "libx264", "-crf", "22", "-preset", "medium",
        "-pix_fmt", "yuv420p", "-an",
        str(out)
    ], capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-800:], file=sys.stderr); return False

    print(f"        raw: {out.stat().st_size/1024/1024:.1f} MB")
    return True


def compress(raw: Path, out: Path) -> bool:
    cmd = [
        "ffmpeg", "-y", "-i", str(raw),
        "-c:v", "libx264", "-crf", "26", "-maxrate", "2200k",
        "-bufsize", "4400k", "-pix_fmt", "yuv420p", "-an", str(out),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stderr[-500:], file=sys.stderr); return False
    size = out.stat().st_size / 1024 / 1024
    print(f"        compressed: {size:.1f} MB")
    return size < 49


def send_telegram(mp4: Path) -> int:
    boundary = b"----boundary1234"
    body = b"--" + boundary + b"\r\nContent-Disposition: form-data; name=\"chat_id\"\r\n\r\n6624890918\r\n"
    body += b"--" + boundary + b"\r\nContent-Disposition: form-data; name=\"video\"; filename=\"PILOT_8C.mp4\"\r\nContent-Type: video/mp4\r\n\r\n"
    body += mp4.read_bytes()
    body += b"\r\n--" + boundary + b"--\r\n"
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{TG_TOKEN}/sendVideo", data=body,
        headers={"Content-Type": "multipart/form-data; boundary=----boundary1234"}, method="POST",
    )
    print(f"[TG]   sending {mp4.stat().st_size // 1024} KB…")
    with urllib.request.urlopen(req, timeout=120) as r:
        resp = json.loads(r.read().decode())
        mid = resp["result"]["message_id"]
        print(f"[TG]   OK msg_id={mid}")
        return mid


def main() -> int:
    if not SOURCE.exists():
        print(f"ABORT: source not found: {SOURCE}", file=sys.stderr)
        return 2

    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    raw_clip   = OUT_DIR / f"PILOT_8C_kling_raw__{ts}.mp4"
    raw_film   = OUT_DIR / f"PILOT_8C_palindrome_raw__{ts}.mp4"
    out        = OUT_DIR / f"PILOT_8C_KLING_PALINDROME_30S__{ts}.mp4"

    print(f"[1/5] Upload portrait → Higgsfield CDN")
    public_url = upload_image(SOURCE)

    print(f"\n[2/5] Submit Kling Pro I2V…")
    rid, surl = submit_kling(public_url)

    print(f"\n[3/5] Polling (up to 10 min)…")
    output_url = poll(rid, surl)
    print(f"      ✓ COMPLETED  url={output_url[:80]}…")

    print(f"\n[4/5] Download…")
    urllib.request.urlretrieve(output_url, raw_clip)
    print(f"      {raw_clip.stat().st_size // 1024} KB raw clip")

    print(f"\n[5/5] Build palindrome (fwd→slow_fwd→rev→slow_rev = 30s)…")
    if not build_palindrome(raw_clip, raw_film):
        print("ABORT: palindrome build failed", file=sys.stderr); return 1
    if not compress(raw_film, out):
        print("ABORT: compress failed", file=sys.stderr); return 1

    mid = send_telegram(out)

    receipt = {
        "schema": "NON_SOVEREIGN_RENDER_RECEIPT_V3",
        "authority_status": "NON_SOVEREIGN_SANDBOX",
        "canon": "NO_SHIP",
        "generated_at": now_iso(),
        "pilot": "director_pilot_v8c",
        "source_image": str(SOURCE),
        "artifact": str(out),
        "artifact_sha256": sha256_file(out),
        "method": "kling_i2v_palindrome_postproduction",
        "duration_s": 30,
        "format": f"{W}x{H}",
        "credits_spent": "~15-25",
        "technique": "kling_pro+fwd+slow_fwd+rev+slow_rev+vignette+grain+pulse+grade",
        "telegram_msg_id": mid,
        "status": "RATING_PENDING",
        "operator_decision": None,
        "pipeline_score": None,
        "output_score": None,
    }
    rp = OUT_DIR / "render_receipt_v8c.json"
    rp.write_text(json.dumps(receipt, indent=2))

    print()
    print("=" * 55)
    print("PILOT 8C — Kling palindrome presence film")
    print(f"  mp4     : {out}")
    print(f"  telegram: msg {mid}")
    print(f"  status  : RATING_PENDING — BLOCKED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
