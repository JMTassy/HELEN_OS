"""HELEN Video OS — Telegram delivery wrapper.

Posts a local mp4 to a Telegram chat via the Bot API.
Emits TELEGRAM_DELIVERY_RECEIPT_V1.

Auth:    TELEGRAM_BOT_TOKEN env (loaded from ~/.helen_os/.env)
Target:  TELEGRAM_CHAT_ID env
Endpoint: https://api.telegram.org/bot<TOKEN>/sendVideo
"""

from __future__ import annotations

import datetime
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

try:
    import httpx
except ImportError:
    print("httpx not installed. Run: pip install httpx", file=sys.stderr)
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parents[4]
SUBSANDBOX_TG = REPO_ROOT / "temple" / "subsandbox" / "director" / "telegram"


def canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_obj(obj: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_json(obj).encode("utf-8")).hexdigest()


def sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def now_utc_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")


def _load_env_file(env_path: Path) -> None:
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


def _bot_token() -> str:
    _load_env_file(Path.home() / ".helen_os" / ".env")
    tok = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not tok:
        raise RuntimeError("TELEGRAM_BOT_TOKEN not set")
    return tok


def _chat_id() -> str:
    cid = os.environ.get("TELEGRAM_CHAT_ID")
    if not cid:
        raise RuntimeError("TELEGRAM_CHAT_ID not set in env")
    return cid


def send_video(
    mp4_path: Path,
    caption: Optional[str] = None,
    task_id: Optional[str] = None,
    timeout_s: float = 120.0,
) -> Dict[str, Any]:
    """Post the mp4 to the configured Telegram chat. Returns the receipt."""
    mp4_path = Path(mp4_path)
    if not mp4_path.exists():
        raise FileNotFoundError(mp4_path)
    task_id = task_id or mp4_path.parent.name

    token = _bot_token()
    chat_id = _chat_id()

    mp4_bytes = mp4_path.read_bytes()
    mp4_sha256 = sha256_bytes(mp4_bytes)

    url = f"https://api.telegram.org/bot{token}/sendVideo"
    data = {"chat_id": chat_id}
    if caption:
        data["caption"] = caption[:1024]  # Telegram caption limit

    files = {"video": (mp4_path.name, mp4_bytes, "video/mp4")}

    print(f"[telegram] POST sendVideo chat_id={chat_id} bytes={len(mp4_bytes)}", flush=True)
    started = now_utc_iso()
    with httpx.Client(timeout=timeout_s) as client:
        r = client.post(url, data=data, files=files)
    completed = now_utc_iso()

    try:
        resp_json = r.json()
    except Exception:
        resp_json = {"raw": r.text}

    out_dir = SUBSANDBOX_TG / task_id
    out_dir.mkdir(parents=True, exist_ok=True)

    if r.status_code == 200 and resp_json.get("ok"):
        message_id = (resp_json.get("result") or {}).get("message_id")
        receipt = {
            "schema": "TELEGRAM_DELIVERY_RECEIPT_V1",
            "task_id": task_id,
            "chat_id": str(chat_id),
            "message_id": message_id,
            "mp4_path": str(mp4_path),
            "mp4_sha256": mp4_sha256,
            "mp4_bytes": len(mp4_bytes),
            "caption": caption,
            "status": "delivered",
            "http_status": r.status_code,
            "started_utc": started,
            "completed_utc": completed,
            "scope": "TEMPLE_SUBSANDBOX",
            "sovereign_admitted": False,
        }
        print(f"[telegram] OK message_id={message_id}", flush=True)
    else:
        receipt = {
            "schema": "TELEGRAM_DELIVERY_RECEIPT_V1",
            "task_id": task_id,
            "chat_id": str(chat_id),
            "mp4_path": str(mp4_path),
            "mp4_sha256": mp4_sha256,
            "status": "failed",
            "http_status": r.status_code,
            "error": resp_json,
            "started_utc": started,
            "completed_utc": completed,
            "scope": "TEMPLE_SUBSANDBOX",
            "sovereign_admitted": False,
        }
        print(f"[telegram] FAILED http={r.status_code} resp={resp_json}", flush=True)

    receipt_path = out_dir / "TELEGRAM_DELIVERY_RECEIPT_V1.json"
    receipt_path.write_text(canonical_json(receipt) + "\n", encoding="utf-8")
    print(f"[telegram] receipt: {receipt_path}", flush=True)
    return receipt


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description="Telegram video delivery")
    parser.add_argument("--mp4", required=True, help="Path to mp4 to send")
    parser.add_argument("--caption", default=None)
    parser.add_argument("--task-id", default=None)
    args = parser.parse_args()
    receipt = send_video(Path(args.mp4), caption=args.caption, task_id=args.task_id)
    return 0 if receipt.get("status") == "delivered" else 1


if __name__ == "__main__":
    raise SystemExit(main())
