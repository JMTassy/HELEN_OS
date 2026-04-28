#!/usr/bin/env python3
"""
HELEN Director — Pilot 8D: 3-shot Kling cinematic cut, 30s.
NON_SOVEREIGN. ~45-75 credits (3 × Kling Pro I2V 5s).

3 distinct images → 3 parallel Kling jobs → cinematic cut + music.
No palindrome. Edit arc: close → medium → atmospheric → medium_slow → close.

Sources:
  A: April 23 close-up portrait (extreme face / eyes)
  B: helen_conquest_adcopy1.png (dynamic 3/4 portrait, gold)
  C: helen_cyberpunk.jpg (dark mood, city atmosphere)

Edit structure (30s):
  A_fwd  (5s) — close eyes, micro-expression
  B_fwd  (5s) — medium, hair moves, particles
  C_slow (10s) — dark atmospheric, neon depth
  B_slow (5s)  — medium, slow settle
  A_fwd  (5s)  — close return, end on eyes
"""
from __future__ import annotations

import datetime, hashlib, json, subprocess, sys, time, urllib.request, urllib.error
import os as _os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# ── Spectral admissibility gate ───────────────────────────────────────────────
import numpy as np
_SOT = Path(__file__).resolve().parents[4]   # helen_os_v1/
sys.path.insert(0, str(_SOT / "experiments" / "helen_mvp_kernel"))
from helen_os.certificates.spectral_certificate import SpectralCertificate, build_receipt as _build_spectral_receipt

_avatar = Path(_os.path.expanduser("~/Desktop/HELEN_OS_PICS/HELEN_AVATAR"))
MUSIC   = Path(_os.path.expanduser("~/Desktop/HELEN_OS_PICS/unripple_3min_music_clip.mp4"))

IMG_A = _avatar / "Capture d\u2019\u00e9cran 2026-04-23 \u00e0 18.55.36.png"   # close-up face
IMG_B = _avatar / "helen_conquest_adcopy1.png"                                   # 3/4 gold portrait
IMG_C = _avatar / "helen_cyberpunk.jpg"                                           # cyberpunk dark

OUT_DIR = Path("/tmp/helen_temple")
OUT_DIR.mkdir(parents=True, exist_ok=True)

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

SHOTS = [
    {
        "id": "A",
        "img": IMG_A,
        "prompt": (
            "Extreme close-up cinematic portrait. Young woman, copper-red hair, "
            "blue-grey eyes. 9:16, 24fps, 5s. Camera locked. "
            "Subject: eyes slowly shift from downcast to direct gaze at camera. "
            "Subtle parting of lips. A single tear forms but does not fall. "
            "Shallow DOF, cinematic bokeh. Warm golden-violet rim light. "
            "Film grain. No speaking. Sacred stillness broken only by the gaze shift."
        ),
        "content_type": "image/png",
    },
    {
        "id": "B",
        "img": IMG_B,
        "prompt": (
            "Cinematic medium portrait. Young woman, copper-red wavy hair, "
            "black and gold outfit, blue-grey eyes. 9:16, 24fps, 5s. "
            "Camera very slow push-in (zoom 1.0 to 1.05). "
            "Hair moves gently as if light wind. Golden light particles drift "
            "upward in background. Subject: slight confident chin lift, "
            "half-smile forms slowly. Warm amber-gold atmosphere. "
            "Film grain, cinematic color grade. Alive, powerful, present."
        ),
        "content_type": "image/png",
    },
    {
        "id": "C",
        "img": IMG_C,
        "prompt": (
            "Cinematic atmospheric portrait. Young woman, copper-red hair, "
            "black outfit. 9:16, 24fps, 5s. Camera locked. "
            "Subject: turns very slowly from 3/4 angle toward camera. "
            "Neon city bokeh background — teal and magenta light bleed. "
            "Rain-wet environment, light reflections on skin. "
            "Subject expression: intense, knowing, slight danger. "
            "Deep shadow with selective neon rim lighting. Cyberpunk-noir mood. "
            "Film grain ISO 3200. No speaking. Pure presence."
        ),
        "content_type": "image/jpeg",
    },
]


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")

def hf_req(path: str, method: str = "POST", body=None, timeout: int = 30, raw_url: str | None = None):
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


def upload(img: Path, content_type: str) -> str:
    code, text = hf_req("/files/generate-upload-url", body={"content_type": content_type})
    if code != 200:
        raise RuntimeError(f"upload-url {code}: {text[:150]}")
    info = json.loads(text)
    put_req = urllib.request.Request(
        info["upload_url"], data=img.read_bytes(),
        headers={"Content-Type": content_type}, method="PUT"
    )
    with urllib.request.urlopen(put_req, timeout=90) as r:
        pass
    return info["public_url"]


def submit_kling(shot: dict, public_url: str) -> tuple[str, str]:
    payloads = [
        {"prompt": shot["prompt"],
         "input_image": {"type": "image_url", "image_url": public_url},
         "duration": 5, "aspect_ratio": "9:16"},
        {"prompt": shot["prompt"],
         "input_image": {"type": "image_url", "image_url": public_url},
         "duration": 5},
        {"prompt": shot["prompt"], "image_url": public_url, "duration": 5},
    ]
    for i, payload in enumerate(payloads):
        code, text = hf_req("/kling", body=payload)
        if code in (200, 201, 202):
            data = json.loads(text)
            rid = data.get("request_id")
            surl = data.get("status_url", f"{BASE}/requests/{rid}/status")
            return rid, surl
        if code == 403:
            raise RuntimeError("403 insufficient credits")
    raise RuntimeError(f"Kling submit failed: {code} {text[:150]}")


def poll_one(shot_id: str, rid: str, surl: str, deadline_s: int = 600) -> str:
    deadline = time.time() + deadline_s
    t0 = time.time()
    while time.time() < deadline:
        code, text = hf_req(surl, raw_url=surl if surl.startswith("http") else None, method="GET")
        try:
            data = json.loads(text); status = data.get("status", "?")
        except Exception:
            status = text[:40]
        elapsed = int(time.time() - t0)
        if elapsed % 30 < 6:
            print(f"      [{shot_id}] t={elapsed}s  {status}")
        if status in ("COMPLETED", "completed"):
            output_url = (
                data.get("output_url") or data.get("video_url") or
                (data.get("video") or {}).get("url") or
                (data.get("outputs") or [{}])[0].get("url") or
                data.get("result", {}).get("url")
            )
            if not output_url:
                raise RuntimeError(f"completed but no output URL: {text[:200]}")
            return output_url
        if status in ("FAILED", "failed", "NSFW", "CANCELED", "cancelled"):
            raise RuntimeError(f"shot {shot_id} {status}: {text[:200]}")
        time.sleep(5)
    raise RuntimeError(f"shot {shot_id} timeout")


def normalize(src: Path, dst: Path) -> bool:
    r = subprocess.run([
        "ffmpeg", "-y", "-i", str(src),
        "-vf", f"scale={W}:{H}:force_original_aspect_ratio=decrease,"
               f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:black,fps={FPS}",
        "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", "-an", str(dst)
    ], capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-300:], file=sys.stderr)
    return r.returncode == 0


def slow(src: Path, dst: Path, factor: float = 2.0) -> bool:
    r = subprocess.run([
        "ffmpeg", "-y", "-i", str(src),
        "-vf", f"setpts={factor}*PTS", "-r", str(FPS),
        "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", "-an", str(dst)
    ], capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-300:], file=sys.stderr)
    return r.returncode == 0


def assemble(segs: list[Path], music: Path, out: Path) -> bool:
    tmp = OUT_DIR / "p8d_tmp"
    tmp.mkdir(exist_ok=True)

    # Grade filter
    post = (
        "vignette=PI/2.8,"
        "noise=c0s=10:c0f=t+u,"
        "geq=r='clip(r(X,Y)*(1+0.025*sin(2*3.14159*T/4)),0,255)':"
        "g='clip(g(X,Y)*(1+0.025*sin(2*3.14159*T/4)),0,255)':"
        "b='clip(b(X,Y)*(1+0.025*sin(2*3.14159*T/4)),0,255)',"
        "hue=s=1.2,"
        "colorbalance=rh=0.06:gh=0.01:bh=-0.05:rs=0.03:bs=0.05"
    )
    fade_in  = "geq=r='r(X,Y)*min(1,T/2.0)':g='g(X,Y)*min(1,T/2.0)':b='b(X,Y)*min(1,T/2.0)'"
    fade_out = "geq=r='r(X,Y)*min(1,(30-T)/2.0)':g='g(X,Y)*min(1,(30-T)/2.0)':b='b(X,Y)*min(1,(30-T)/2.0)'"

    # Concat video
    concat_list = tmp / "concat.txt"
    concat_list.write_text("".join(f"file '{s}'\n" for s in segs))
    raw_concat = tmp / "raw_concat.mp4"
    r = subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(concat_list), "-c", "copy", str(raw_concat)
    ], capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-400:], file=sys.stderr); return False

    # Grade + fade + mux music
    graded = tmp / "graded.mp4"
    r = subprocess.run([
        "ffmpeg", "-y", "-i", str(raw_concat),
        "-filter_complex",
        f"[0:v]{post}[graded];[graded]{fade_in}[fin];[fin]{fade_out}",
        "-t", "30", "-c:v", "libx264", "-crf", "22", "-preset", "medium",
        "-pix_fmt", "yuv420p", "-an", str(graded)
    ], capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-600:], file=sys.stderr); return False

    # Mux music
    r = subprocess.run([
        "ffmpeg", "-y", "-i", str(graded), "-i", str(music),
        "-map", "0:v", "-map", "1:a",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        "-t", "30", "-shortest", str(out)
    ], capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-400:], file=sys.stderr); return False

    size = out.stat().st_size / 1024 / 1024
    print(f"        assembled: {size:.1f} MB")
    return True


def compress(raw: Path, dst: Path) -> bool:
    r = subprocess.run([
        "ffmpeg", "-y", "-i", str(raw),
        "-c:v", "libx264", "-crf", "26", "-maxrate", "2200k",
        "-bufsize", "4400k", "-c:a", "copy", str(dst)
    ], capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-400:], file=sys.stderr); return False
    size = dst.stat().st_size / 1024 / 1024
    print(f"        compressed: {size:.1f} MB")
    return size < 49


def send_telegram(mp4: Path) -> int:
    boundary = b"----boundary1234"
    body = b"--" + boundary + b"\r\nContent-Disposition: form-data; name=\"chat_id\"\r\n\r\n6624890918\r\n"
    body += b"--" + boundary + b"\r\nContent-Disposition: form-data; name=\"video\"; filename=\"PILOT_8D.mp4\"\r\nContent-Type: video/mp4\r\n\r\n"
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


def _extract_frame_energy(video_path: Path, fps: int = 10, max_frames: int = 64) -> np.ndarray:
    """Deterministic scalar signal: mean luminance per frame (64×64 grey)."""
    cmd = ["ffmpeg", "-i", str(video_path),
           "-vf", f"fps={fps},scale=64:64,format=gray",
           "-f", "rawvideo", "-"]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    raw = proc.stdout.read(64 * 64 * max_frames)
    proc.wait()
    if not raw:
        raise RuntimeError(f"No frames extracted from {video_path}")
    frames = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 64 * 64)
    return frames.mean(axis=1)


def _build_coherence_matrix(video_path: Path, size: int = 32) -> np.ndarray:
    """Gram matrix of temporal energy signal — guaranteed PSD, normalised."""
    sig = _extract_frame_energy(video_path)
    if len(sig) < size:
        sig = np.pad(sig, (0, size - len(sig)))
    else:
        sig = sig[:size]
    T = np.outer(sig, sig)
    return T / (np.linalg.norm(T) + 1e-8)


def _build_reference_matrix(size: int = 32) -> np.ndarray:
    """Fixed declared reference — constant across all runs."""
    x = np.linspace(0, 1, size)
    T_ref = np.outer(np.cos(2 * np.pi * x), np.cos(2 * np.pi * x))
    return T_ref / (np.linalg.norm(T_ref) + 1e-8)


def spectral_gate(video_path: Path) -> dict:
    """
    Hard admissibility gate.  Raises RuntimeError if margin ≤ 0.
    Returns a NON_SOVEREIGN spectral receipt (signature=None).
    """
    print("[GATE] building temporal coherence matrix…")
    T_hp  = _build_coherence_matrix(video_path)
    T_ref = _build_reference_matrix(size=T_hp.shape[0])
    cert  = SpectralCertificate(T_ref, tolerance=1e-6)
    result = cert.certify(T_hp)
    receipt = _build_spectral_receipt(
        result,
        object_id=str(video_path),
        params={"type": "temporal_energy_gram", "size": T_hp.shape[0]},
    )
    if not result["is_positive_definite"] or result["margin"] <= 0:
        print(f"[GATE] FAIL  margin={result['margin']:.8f}  aeon={result['aeon']:.8f}",
              file=sys.stderr)
        raise RuntimeError(
            f"Spectral admissibility gate FAILED — margin={result['margin']:.8f}"
        )
    print(f"[GATE] PASS  margin={result['margin']:.6f}  aeon={result['aeon']:.8f}")
    return receipt


def run_shot(shot: dict) -> tuple[str, str]:
    print(f"  [{shot['id']}] uploading {shot['img'].name}…")
    pub = upload(shot["img"], shot["content_type"])
    print(f"  [{shot['id']}] submitting Kling…")
    rid, surl = submit_kling(shot, pub)
    print(f"  [{shot['id']}] queued  rid={rid[:8]}…")
    url = poll_one(shot["id"], rid, surl)
    print(f"  [{shot['id']}] ✓ done  url={url[:60]}…")
    return shot["id"], url


def main() -> int:
    for img in [IMG_A, IMG_B, IMG_C]:
        if not img.exists():
            print(f"ABORT: missing {img}", file=sys.stderr); return 2

    ts  = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    tmp = OUT_DIR / "p8d_tmp"
    tmp.mkdir(exist_ok=True)

    # ── Step 1: Submit all 3 Kling jobs in parallel ───────────────────────────
    print("[1/4] Submitting 3 Kling shots in parallel…")
    results: dict[str, str] = {}
    with ThreadPoolExecutor(max_workers=3) as ex:
        futs = {ex.submit(run_shot, s): s["id"] for s in SHOTS}
        for fut in as_completed(futs):
            sid, url = fut.result()
            results[sid] = url

    # ── Step 2: Download + normalize ─────────────────────────────────────────
    print("\n[2/4] Download + normalize…")
    clips: dict[str, Path] = {}
    for sid, url in results.items():
        raw = tmp / f"raw_{sid}.mp4"
        norm = tmp / f"norm_{sid}.mp4"
        print(f"  [{sid}] downloading…")
        urllib.request.urlretrieve(url, raw)
        print(f"  [{sid}] normalizing → 1080x1920…")
        if not normalize(raw, norm):
            print(f"ABORT: normalize failed for {sid}", file=sys.stderr); return 1
        clips[sid] = norm

    # ── Step 3: Build edit ────────────────────────────────────────────────────
    # Arc: A(5s) → B(5s) → C_slow(10s) → B_slow(5s) → A(5s) = 30s
    print("\n[3/4] Building edit arc…")
    c_slow = tmp / "C_slow.mp4"
    b_slow = tmp / "B_slow.mp4"
    if not slow(clips["C"], c_slow, 2.0): return 1  # 5s → 10s
    if not slow(clips["B"], b_slow, 1.0): return 1  # 5s stays 5s (trim point)

    # Actually slow B to fill 5s cleanly
    # B_slow = first 2.5s of B at 2x = 5s
    b_half = tmp / "B_half.mp4"
    r = subprocess.run([
        "ffmpeg", "-y", "-i", str(clips["B"]),
        "-t", "2.5", "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", "-an", str(b_half)
    ], capture_output=True, text=True)
    if r.returncode != 0: print(r.stderr[-200:], file=sys.stderr); return 1
    if not slow(b_half, b_slow, 2.0): return 1  # 2.5s → 5s

    segs = [clips["A"], clips["B"], c_slow, b_slow, clips["A"]]
    print(f"  edit: A(5s) + B(5s) + C_slow(10s) + B_slow(5s) + A(5s) = 30s")

    raw_film = tmp / f"raw_film_{ts}.mp4"
    if not assemble(segs, MUSIC, raw_film): return 1

    # ── Step 4: Compress + gate + send ───────────────────────────────────────
    print("\n[4/4] Compress → spectral gate → Telegram…")
    out = OUT_DIR / f"PILOT_8D_3SHOT_KLING_30S__{ts}.mp4"
    if not compress(raw_film, out): return 1

    # Hard admissibility gate — blocks delivery if temporal coherence fails
    try:
        spectral_receipt = spectral_gate(out)
    except RuntimeError as e:
        print(f"ABORT: {e}", file=sys.stderr)
        return 1

    mid = send_telegram(out)

    receipt = {
        "schema": "NON_SOVEREIGN_RENDER_RECEIPT_V3",
        "authority_status": "NON_SOVEREIGN_SANDBOX",
        "canon": "NO_SHIP",
        "generated_at": now_iso(),
        "pilot": "director_pilot_v8d",
        "sources": [str(IMG_A), str(IMG_B), str(IMG_C)],
        "artifact": str(out),
        "artifact_sha256": sha256_file(out),
        "method": "kling_3shot_parallel_cinematic_cut",
        "duration_s": 30,
        "format": f"{W}x{H}",
        "credits_spent": "~45-75",
        "technique": "3x_kling_pro+cinematic_cut+music+grade+fadeinout",
        "edit_arc": "A_close(5s)+B_medium(5s)+C_atmospheric_slow(10s)+B_slow(5s)+A_close(5s)",
        "telegram_msg_id": mid,
        "status": "RATING_PENDING",
        "operator_decision": None, "pipeline_score": None, "output_score": None,
        "spectral_certificate": {
            "margin": spectral_receipt["margin"],
            "aeon": spectral_receipt["aeon"],
            "lambda_min_ref": spectral_receipt["lambda_min_ref"],
            "status": spectral_receipt["status"],
            "payload_hash": spectral_receipt["payload_hash"],
            "signature": None,
        },
    }
    (OUT_DIR / "render_receipt_v8d.json").write_text(json.dumps(receipt, indent=2))

    print()
    print("=" * 55)
    print("PILOT 8D — 3-shot Kling cinematic cut")
    print(f"  mp4     : {out}")
    print(f"  telegram: msg {mid}")
    print(f"  status  : RATING_PENDING — BLOCKED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
