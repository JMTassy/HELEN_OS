"""HELEN Video OS — HeyGen video backend.

NON_SOVEREIGN. TEMPLE_SUBSANDBOX scope. LIVE rental path.

Generates one video via HeyGen API, polls for completion, downloads mp4,
emits HEYGEN_CALL_RECEIPT_V1.

Auth: X-Api-Key header from HEYGEN_API_KEY env var.
Endpoint: https://api.heygen.com/v2/video/generate
Status:   https://api.heygen.com/v1/video_status.get
"""

from __future__ import annotations

import datetime
import hashlib
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional

try:
    import httpx
except ImportError:
    print("httpx not installed. Run: pip install httpx", file=sys.stderr)
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parents[4]
SUBSANDBOX_HEYGEN = REPO_ROOT / "temple" / "subsandbox" / "director" / "heygen"

API_BASE = "https://api.heygen.com"
GENERATE_URL = f"{API_BASE}/v2/video/generate"
STATUS_URL = f"{API_BASE}/v1/video_status.get"
UPLOAD_URL = "https://upload.heygen.com/v1/talking_photo"

# HeyGen public default avatar + voice (English female) — free-tier friendly
DEFAULT_AVATAR_ID = "Daisy-inskirt-20220818"
DEFAULT_VOICE_ID = "2d5b0e6cf36f460aa7fc47e3eee4ba54"
DEFAULT_DIMENSION = {"width": 720, "height": 1280}  # 9:16 vertical


def canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_obj(obj: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_json(obj).encode("utf-8")).hexdigest()


def sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def now_utc_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")


def _load_env_file(env_path: Path) -> None:
    """Minimal stdlib .env loader. Sets vars in os.environ if not already set."""
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        k = k.strip()
        v = v.strip().strip('"').strip("'")
        if k and k not in os.environ:
            os.environ[k] = v


def _api_key() -> str:
    _load_env_file(Path.home() / ".helen_os" / ".env")
    key = os.environ.get("HEYGEN_API_KEY")
    if not key:
        raise RuntimeError("HEYGEN_API_KEY not set in env or ~/.helen_os/.env")
    return key


def upload_talking_photo(
    image_source: str,
    timeout_s: float = 60.0,
) -> str:
    """Upload a photo to HeyGen, return talking_photo_id.

    image_source: local path (existing file) OR http(s) URL.
    """
    headers = {"X-Api-Key": _api_key()}

    if image_source.startswith("http://") or image_source.startswith("https://"):
        print(f"[heygen] fetching photo from URL: {image_source}", flush=True)
        with httpx.Client(timeout=timeout_s, follow_redirects=True) as client:
            r = client.get(image_source)
            r.raise_for_status()
            image_bytes = r.content
            content_type = r.headers.get("content-type", "image/jpeg").split(";")[0]
    else:
        p = Path(image_source).expanduser()
        if not p.exists():
            raise FileNotFoundError(image_source)
        image_bytes = p.read_bytes()
        ext = p.suffix.lower().lstrip(".")
        content_type = f"image/{'jpeg' if ext == 'jpg' else ext or 'jpeg'}"

    print(f"[heygen] upload_talking_photo bytes={len(image_bytes)} type={content_type}", flush=True)
    headers["Content-Type"] = content_type
    with httpx.Client(timeout=timeout_s) as client:
        r = client.post(UPLOAD_URL, headers=headers, content=image_bytes)
        r.raise_for_status()
        data = r.json()
    tp_id = (data.get("data") or {}).get("talking_photo_id")
    if not tp_id:
        raise RuntimeError(f"HeyGen upload response missing talking_photo_id: {data}")
    print(f"[heygen] talking_photo_id={tp_id}", flush=True)
    return tp_id


def generate_video(
    text: str,
    avatar_id: str = DEFAULT_AVATAR_ID,
    voice_id: str = DEFAULT_VOICE_ID,
    dimension: Optional[Dict[str, int]] = None,
    timeout_s: float = 30.0,
    talking_photo_id: Optional[str] = None,
) -> str:
    """Submit a generation request. Returns video_id.

    If talking_photo_id is provided, uses talking_photo character type
    instead of stock avatar — HELEN's actual face speaks.
    """
    dimension = dimension or DEFAULT_DIMENSION
    if talking_photo_id:
        character = {
            "type": "talking_photo",
            "talking_photo_id": talking_photo_id,
        }
    else:
        character = {
            "type": "avatar",
            "avatar_id": avatar_id,
            "avatar_style": "normal",
        }
    body = {
        "video_inputs": [
            {
                "character": character,
                "voice": {
                    "type": "text",
                    "input_text": text,
                    "voice_id": voice_id,
                },
            }
        ],
        "dimension": dimension,
    }
    headers = {
        "X-Api-Key": _api_key(),
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    with httpx.Client(timeout=timeout_s) as client:
        r = client.post(GENERATE_URL, headers=headers, json=body)
        r.raise_for_status()
        data = r.json()
    video_id = (data.get("data") or {}).get("video_id")
    if not video_id:
        raise RuntimeError(f"HeyGen response missing video_id: {data}")
    return video_id


def poll_status(
    video_id: str,
    poll_interval_s: float = 10.0,
    max_wait_s: float = 1200.0,
    request_timeout_s: float = 60.0,
) -> Dict[str, Any]:
    """Poll until status is completed/failed. Returns the final status payload.

    Robust to transient ReadTimeouts: skips and retries next interval.
    """
    headers = {"X-Api-Key": _api_key(), "Accept": "application/json"}
    deadline = time.time() + max_wait_s
    transient_errors = 0
    while time.time() < deadline:
        try:
            with httpx.Client(timeout=request_timeout_s) as client:
                r = client.get(STATUS_URL, headers=headers, params={"video_id": video_id})
                r.raise_for_status()
                payload = r.json().get("data", {})
        except (httpx.ReadTimeout, httpx.ConnectTimeout, httpx.RemoteProtocolError) as e:
            transient_errors += 1
            print(f"  [{int(time.time())%1000:03d}s] transient error #{transient_errors}: {type(e).__name__}; retrying", flush=True)
            time.sleep(poll_interval_s)
            continue
        status = payload.get("status")
        print(f"  [{int(time.time())%1000:03d}s] status={status}", flush=True)
        if status in ("completed", "failed"):
            return payload
        time.sleep(poll_interval_s)
    raise TimeoutError(f"HeyGen video {video_id} did not complete within {max_wait_s}s")


def download_mp4(url: str, out_path: Path, timeout_s: float = 120.0) -> bytes:
    """Download mp4. Returns the bytes (also written to out_path)."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with httpx.Client(timeout=timeout_s, follow_redirects=True) as client:
        r = client.get(url)
        r.raise_for_status()
        out_path.write_bytes(r.content)
    return r.content


def render_one_shot(
    text: str,
    task_id: str,
    avatar_id: str = DEFAULT_AVATAR_ID,
    voice_id: str = DEFAULT_VOICE_ID,
    dimension: Optional[Dict[str, int]] = None,
    photo: Optional[str] = None,
) -> Dict[str, Any]:
    """End-to-end: submit -> poll -> download -> emit receipt. Returns the receipt.

    If `photo` is provided (local path or http(s) URL), uploads to HeyGen
    as a talking_photo and uses that face instead of the stock avatar.
    """
    dimension = dimension or DEFAULT_DIMENSION
    out_dir = SUBSANDBOX_HEYGEN / task_id
    out_dir.mkdir(parents=True, exist_ok=True)
    started = now_utc_iso()

    talking_photo_id: Optional[str] = None
    if photo:
        talking_photo_id = upload_talking_photo(photo)

    request_body = {
        "text": text,
        "avatar_id": avatar_id if not talking_photo_id else None,
        "talking_photo_id": talking_photo_id,
        "voice_id": voice_id,
        "dimension": dimension,
        "photo_source": photo if photo else None,
    }
    request_hash = sha256_obj(request_body)

    if talking_photo_id:
        print(f"[heygen] generate: text={text!r}, talking_photo_id={talking_photo_id}, dim={dimension}", flush=True)
    else:
        print(f"[heygen] generate: text={text!r}, avatar={avatar_id}, dim={dimension}", flush=True)
    video_id = generate_video(
        text, avatar_id, voice_id, dimension,
        talking_photo_id=talking_photo_id,
    )
    print(f"[heygen] video_id={video_id}", flush=True)

    status_payload = poll_status(video_id)
    if status_payload.get("status") != "completed":
        receipt = {
            "schema": "HEYGEN_CALL_RECEIPT_V1",
            "task_id": task_id,
            "video_id": video_id,
            "request_hash": request_hash,
            "status": "failed",
            "error": status_payload.get("error") or status_payload,
            "started_utc": started,
            "completed_utc": now_utc_iso(),
            "scope": "TEMPLE_SUBSANDBOX",
            "sovereign_admitted": False,
        }
        receipt_path = out_dir / "HEYGEN_CALL_RECEIPT_V1.json"
        receipt_path.write_text(canonical_json(receipt) + "\n", encoding="utf-8")
        print(f"[heygen] FAILED. receipt: {receipt_path}", flush=True)
        return receipt

    video_url = status_payload.get("video_url")
    if not video_url:
        raise RuntimeError(f"completed but no video_url: {status_payload}")

    mp4_path = out_dir / "render.mp4"
    print(f"[heygen] downloading mp4 -> {mp4_path}", flush=True)
    mp4_bytes = download_mp4(video_url, mp4_path)
    mp4_sha256 = sha256_bytes(mp4_bytes)

    receipt = {
        "schema": "HEYGEN_CALL_RECEIPT_V1",
        "task_id": task_id,
        "video_id": video_id,
        "request_hash": request_hash,
        "request_body": request_body,
        "status": "completed",
        "video_url": video_url,
        "mp4_path": str(mp4_path),
        "mp4_sha256": mp4_sha256,
        "mp4_bytes": len(mp4_bytes),
        "started_utc": started,
        "completed_utc": now_utc_iso(),
        "scope": "TEMPLE_SUBSANDBOX",
        "sovereign_admitted": False,
    }
    receipt_path = out_dir / "HEYGEN_CALL_RECEIPT_V1.json"
    receipt_path.write_text(canonical_json(receipt) + "\n", encoding="utf-8")
    print(f"[heygen] OK. mp4: {mp4_path} ({len(mp4_bytes)} bytes, {mp4_sha256[:24]}...)", flush=True)
    print(f"[heygen] receipt: {receipt_path}", flush=True)
    return receipt


def resume_render(video_id: str, task_id: str) -> Dict[str, Any]:
    """Resume after a failed/timeout poll. Skips upload+generate; polls,
    downloads, emits receipt for an existing HeyGen video_id."""
    out_dir = SUBSANDBOX_HEYGEN / task_id
    out_dir.mkdir(parents=True, exist_ok=True)
    started = now_utc_iso()

    print(f"[heygen] resume polling video_id={video_id}", flush=True)
    status_payload = poll_status(video_id)

    if status_payload.get("status") != "completed":
        receipt = {
            "schema": "HEYGEN_CALL_RECEIPT_V1",
            "task_id": task_id,
            "video_id": video_id,
            "status": "failed",
            "resumed": True,
            "error": status_payload.get("error") or status_payload,
            "started_utc": started,
            "completed_utc": now_utc_iso(),
            "scope": "TEMPLE_SUBSANDBOX",
            "sovereign_admitted": False,
        }
        receipt_path = out_dir / "HEYGEN_CALL_RECEIPT_V1.json"
        receipt_path.write_text(canonical_json(receipt) + "\n", encoding="utf-8")
        print(f"[heygen] FAILED on resume. receipt: {receipt_path}", flush=True)
        return receipt

    video_url = status_payload.get("video_url")
    if not video_url:
        raise RuntimeError(f"completed but no video_url: {status_payload}")

    mp4_path = out_dir / "render.mp4"
    print(f"[heygen] downloading mp4 -> {mp4_path}", flush=True)
    mp4_bytes = download_mp4(video_url, mp4_path)
    mp4_sha256 = sha256_bytes(mp4_bytes)

    receipt = {
        "schema": "HEYGEN_CALL_RECEIPT_V1",
        "task_id": task_id,
        "video_id": video_id,
        "status": "completed",
        "resumed": True,
        "video_url": video_url,
        "mp4_path": str(mp4_path),
        "mp4_sha256": mp4_sha256,
        "mp4_bytes": len(mp4_bytes),
        "started_utc": started,
        "completed_utc": now_utc_iso(),
        "scope": "TEMPLE_SUBSANDBOX",
        "sovereign_admitted": False,
    }
    receipt_path = out_dir / "HEYGEN_CALL_RECEIPT_V1.json"
    receipt_path.write_text(canonical_json(receipt) + "\n", encoding="utf-8")
    print(f"[heygen] OK (resumed). mp4: {mp4_path} ({len(mp4_bytes)} bytes, {mp4_sha256[:24]}...)", flush=True)
    print(f"[heygen] receipt: {receipt_path}", flush=True)
    return receipt


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description="HeyGen one-shot video render")
    parser.add_argument("--text", required=True, help="Text the avatar will speak")
    parser.add_argument("--task-id", default=None, help="Task id (default: timestamp)")
    parser.add_argument("--avatar", default=DEFAULT_AVATAR_ID)
    parser.add_argument("--voice", default=DEFAULT_VOICE_ID)
    parser.add_argument("--width", type=int, default=DEFAULT_DIMENSION["width"])
    parser.add_argument("--height", type=int, default=DEFAULT_DIMENSION["height"])
    parser.add_argument(
        "--photo",
        default=None,
        help="Local path or http(s) URL to a HELEN reference photo. "
             "When provided, overrides --avatar and uses talking_photo.",
    )
    args = parser.parse_args()

    task_id = args.task_id or f"heygen_test_{int(time.time())}"
    receipt = render_one_shot(
        text=args.text,
        task_id=task_id,
        avatar_id=args.avatar,
        voice_id=args.voice,
        dimension={"width": args.width, "height": args.height},
        photo=args.photo,
    )
    return 0 if receipt.get("status") == "completed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
