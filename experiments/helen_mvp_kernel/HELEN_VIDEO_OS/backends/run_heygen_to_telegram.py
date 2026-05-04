"""End-to-end: HeyGen render -> Telegram delivery, in one command.

Usage:
    python -m experiments.helen_mvp_kernel.HELEN_VIDEO_OS.backends.run_heygen_to_telegram \
        --text "HELEN sees. HELEN proposes. The gate authorizes."

Or from inside the backends/ directory:
    python run_heygen_to_telegram.py --text "..."

Required env vars (loaded from ~/.helen_os/.env):
    HEYGEN_API_KEY
    TELEGRAM_BOT_TOKEN
    TELEGRAM_CHAT_ID

Outputs land in:
    temple/subsandbox/director/heygen/<task_id>/render.mp4
    temple/subsandbox/director/heygen/<task_id>/HEYGEN_CALL_RECEIPT_V1.json
    temple/subsandbox/director/telegram/<task_id>/TELEGRAM_DELIVERY_RECEIPT_V1.json
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from backend_heygen import render_one_shot, DEFAULT_AVATAR_ID, DEFAULT_VOICE_ID  # noqa: E402
from telegram_delivery import send_video  # noqa: E402


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(
        description="HeyGen one-shot -> Telegram delivery"
    )
    parser.add_argument("--text", required=True, help="Text the avatar will speak")
    parser.add_argument("--task-id", default=None)
    parser.add_argument("--avatar", default=DEFAULT_AVATAR_ID)
    parser.add_argument("--voice", default=DEFAULT_VOICE_ID)
    parser.add_argument("--width", type=int, default=720)
    parser.add_argument("--height", type=int, default=1280)
    parser.add_argument(
        "--caption",
        default=None,
        help="Telegram caption (default: derived from --text)",
    )
    args = parser.parse_args()

    task_id = args.task_id or f"helen_{int(time.time())}"

    print(f"=== STAGE 1/2: HeyGen render (task_id={task_id}) ===", flush=True)
    heygen_receipt = render_one_shot(
        text=args.text,
        task_id=task_id,
        avatar_id=args.avatar,
        voice_id=args.voice,
        dimension={"width": args.width, "height": args.height},
    )
    if heygen_receipt.get("status") != "completed":
        print("[run] HeyGen render failed; skipping Telegram delivery.", flush=True)
        return 1

    mp4_path = Path(heygen_receipt["mp4_path"])
    caption = args.caption or f'"{args.text}" — HELEN'

    print(f"\n=== STAGE 2/2: Telegram delivery ===", flush=True)
    tg_receipt = send_video(mp4_path, caption=caption, task_id=task_id)
    if tg_receipt.get("status") != "delivered":
        print("[run] Telegram delivery failed.", flush=True)
        return 2

    print(f"\n=== DONE ===", flush=True)
    print(f"task_id:     {task_id}")
    print(f"video_id:    {heygen_receipt['video_id']}")
    print(f"mp4_sha256:  {heygen_receipt['mp4_sha256']}")
    print(f"mp4_bytes:   {heygen_receipt['mp4_bytes']}")
    print(f"chat_id:     {tg_receipt['chat_id']}")
    print(f"message_id:  {tg_receipt['message_id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
