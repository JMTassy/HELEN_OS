#!/usr/bin/env python3
"""
HELEN render pilot v2 — Existing HELEN avatar seed + Higgsfield Kling I2V + Telegram.

Differs from v1: skips DALL-E (OpenAI billing wall), uses an existing canon HELEN
portrait from ~/Desktop/HELEN_OS_PICS/HELEN_AVATAR/ as the seed.

Pipeline:
  1. Load existing seed PNG from disk
  2. Higgsfield /files/generate-upload-url → PUT bytes → public_url
  3. Higgsfield /kling I2V (5s, 1080p, 9:16) with motion-only prompt
  4. Poll until COMPLETED
  5. Download mp4
  6. Telegram sendVideo to chat 6624890918
Cost: ~15-25 credits (Higgsfield Kling only). No DALL-E spend.
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

_parser = argparse.ArgumentParser(description="HELEN render pilot v2")
_parser.add_argument(
    "--pipeline-score",
    type=int,
    default=None,
    help="Pipeline score 1-10: did the rails work correctly (seed→model→delivery→receipt)? Required non-interactive.",
)
_parser.add_argument(
    "--output-score",
    type=int,
    default=None,
    help="Output score 1-10: is the video actually cinematic HELEN performance? Required non-interactive.",
)
_parser.add_argument(
    "--operator-decision",
    choices=["KEEP", "REJECT"],
    default=None,
    help="Operator decision (KEEP or REJECT). Required non-interactive. Decision is independent of scores: KEEP requires both scores, REJECT can stand even with high scores when the clip is not canon-worthy.",
)
_parser.add_argument(
    "--failure-class",
    type=str,
    default=None,
    help="Optional failure class label when REJECT (free string, e.g. IDENTITY_DRIFT, MOTION_TOO_MUCH, OUTPUT_WEAK). Null on KEEP unless explicitly set.",
)
_ARGS = _parser.parse_args()


def _check_score(name: str, value: int | None) -> None:
    if value is not None and not (1 <= value <= 10):
        raise RuntimeError(
            f"NO_RATING = INVALID_RENDER_RECEIPT — --{name} {value} out of range 1-10"
        )


# Fail-fast: NO_RATING = INVALID_RENDER_RECEIPT. Validate before spending Higgsfield credits.
_check_score("pipeline-score", _ARGS.pipeline_score)
_check_score("output-score", _ARGS.output_score)
_missing = [
    flag
    for flag, val in (
        ("--pipeline-score", _ARGS.pipeline_score),
        ("--output-score", _ARGS.output_score),
        ("--operator-decision", _ARGS.operator_decision),
    )
    if val is None
]
if _missing and not sys.stdin.isatty():
    raise RuntimeError(
        "NO_RATING = INVALID_RENDER_RECEIPT — non-interactive run requires "
        + " AND ".join(_missing)
        + " (scores 1-10, decision KEEP|REJECT)"
    )


def _sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def _sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

env: dict[str, str] = {}
helen_env = Path.home() / ".helen_env"
for ln in helen_env.read_text().splitlines():
    ln = ln.strip()
    if ln.startswith("export "):
        ln = ln[7:]
    if "=" in ln and not ln.startswith("#"):
        k, v = ln.split("=", 1)
        env[k.strip()] = v.strip().strip('"').strip("'")

HF_ID = env.get("HIGGSFIELD_ID") or env.get("HF_API_KEY") or os.environ.get("HF_API_KEY", "")
HF_SECRET = env.get("HIGGSFIELD_SECRET") or env.get("HF_API_SECRET") or os.environ.get("HF_API_SECRET", "")
TELEGRAM_BOT_TOKEN = env.get("TELEGRAM_BOT_TOKEN") or os.environ.get("TELEGRAM_BOT_TOKEN", "")

if not (HF_ID and HF_SECRET):
    sys.exit("FAIL: Higgsfield credentials missing")
if not TELEGRAM_BOT_TOKEN:
    sys.exit("FAIL: TELEGRAM_BOT_TOKEN missing")

OUT = Path("/tmp/helen_render_pilot_v2")
OUT.mkdir(parents=True, exist_ok=True)
CHAT_ID = 6624890918

SEED_PATH = Path(
    "/Users/jean-marietassy/Desktop/HELEN_OS_PICS/HELEN_AVATAR/"
    "hf_20260411_225542_5f020418-d6e6-4716-b8bb-169f6c12bf53.png"
)
if not SEED_PATH.exists():
    sys.exit(f"FAIL: seed not found at {SEED_PATH}")

# Motion-only prompt — locks identity, allows micro-motion only
ANIMATION_PROMPT = (
    "1080px, 9:16, 24fps, 5s. "
    "Camera: locked tripod, zero movement, zero drift, zero push. 35mm cinematic. "
    "Subject (HELEN, copper-red wavy hair, blue-grey eyes, fair skin) holds her position. "
    "Allowed motion: subtle natural breathing rise/fall, slow soft eye-blink once or twice, "
    "very faint hair micro-movement at strand tips, gentle ambient light shift. "
    "Identity locked: hair colour, hair length, eye colour, freckle pattern, garment folds — "
    "all preserved exactly across all 5 seconds. No facial morph, no head turn, no pose change. "
    "No camera movement, no zoom, no supernatural glow, no extra figures, no text overlay."
)

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


print(f"[1/6] Using existing seed: {SEED_PATH.name}")
print(f"      size: {SEED_PATH.stat().st_size/1024/1024:.2f} MB")

print("[2/6] Higgsfield CDN upload URL...")
code, text = hf_req("/files/generate-upload-url", body={"content_type": "image/png"})
if code != 200:
    sys.exit(f"FAIL upload-url: {code}: {text[:300]}")
info = json.loads(text)
public_url = info["public_url"]
upload_url = info["upload_url"]
print(f"      public_url: {public_url[:80]}...")

print("[3/6] PUT seed to CDN...")
put_req = urllib.request.Request(
    upload_url,
    data=SEED_PATH.read_bytes(),
    headers={"Content-Type": "image/png"},
    method="PUT",
)
try:
    with urllib.request.urlopen(put_req, timeout=120) as r:
        print(f"      PUT {r.status} OK")
except urllib.error.HTTPError as e:
    sys.exit(f"FAIL PUT: {e.code} {e.read().decode()[:300]}")

print("[4/6] Submit Kling I2V (5s, 1080p, 9:16)...")
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

print("[5/6] Polling until completed (max 5 min)...")
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
            sys.exit(f"FAIL no output URL: {json.dumps(data, indent=2)[:600]}")
        out_path = OUT / "pilot_v2.mp4"
        urllib.request.urlretrieve(output_url, out_path)
        print(f"      ✓ COMPLETED → {out_path} ({out_path.stat().st_size/1024:.0f} KB)")
        break
    if status in ("FAILED", "failed", "NSFW", "CANCELED", "cancelled"):
        sys.exit(f"FAIL Kling {status}: {json.dumps(data, indent=2)[:600]}")
    time.sleep(5)

if not out_path:
    sys.exit(f"TIMEOUT 5 min — manual check: {status_url}")

print("[6/6] Telegram sendVideo...")
caption = (
    "HELEN render pilot v2 — Higgsfield Kling I2V (5s, 1080p, 9:16). "
    "Seed: existing canon HELEN avatar (Higgsfield-generated 2026-04-11). "
    "Motion: locked camera, identity-preserving micro-motion only (breathing, blink, hair tips). "
    "Pipeline: PNG → CDN upload → Kling I2V → direct download → Telegram."
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

# ── Render receipt (NON_SOVEREIGN, sidecar — never touches town/ledger_v1.ndjson) ──
# Schema v3 (HAL-mandated, MERGE SCHEMAS): three independent signals
#   operator_decision : KEEP | REJECT  — the binding judgment
#   pipeline_score    : 1-10           — did the rails work
#   output_score      : 1-10           — is the clip canon-worthy
# Plus optional failure_class for REJECTs. The decision is independent of the
# scores: a clip can have pipeline=10/output=5 and still be REJECT, which solves
# the inflation problem (machine worked, film not good enough).
receipt_path = OUT / "render_receipt.json"
receipt = {
    "authority_status": "NON_SOVEREIGN_RENDER_RECEIPT",
    "schema_version": 3,  # v1 = single operator_rating; v2 = pipeline_rating+output_rating; v3 = +operator_decision +failure_class
    "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z") or time.strftime("%Y-%m-%dT%H:%M:%S"),
    "seed_path": str(SEED_PATH),
    "seed_sha256": _sha256_file(SEED_PATH),
    "prompt_text": ANIMATION_PROMPT,
    "prompt_sha256": _sha256_text(ANIMATION_PROMPT),
    "model_endpoint": "/kling",
    "provider_model": "kling",
    "model_version": sub_data.get("model_version") or sub_data.get("version"),
    "higgsfield_request_id": request_id,
    "higgsfield_status_url": status_url,
    "output_path": str(out_path),
    "output_sha256": _sha256_file(out_path),
    "output_size_bytes": out_path.stat().st_size,
    "output_duration_seconds": duration,
    "telegram_chat_id": CHAT_ID,
    "telegram_msg_id": msg_id,
    "operator_decision": None,  # filled below before disk write
    "pipeline_score": None,     # filled below before disk write
    "output_score": None,       # filled below before disk write
    "failure_class": None,      # optional; populated on REJECT or when operator passes --failure-class
}

# ── Operator capture (mandatory; NO_RATING = INVALID_RENDER_RECEIPT) ──
# Receipt is NOT written to disk until decision + both scores are bound.

def _capture_score(flag_value: int | None, axis_name: str, prompt: str) -> int:
    if flag_value is not None:
        print(f"      ✓ {axis_name} from flag: {flag_value}/10")
        return flag_value  # already validated 1-10 at parse time
    if sys.stdin.isatty():
        try:
            raw = input(prompt).strip()
            n = int(raw)
            if not (1 <= n <= 10):
                raise ValueError(f"{axis_name} {n} out of range 1-10")
            return n
        except (ValueError, EOFError, KeyboardInterrupt) as e:
            raise RuntimeError(
                f"NO_RATING = INVALID_RENDER_RECEIPT — interactive {axis_name} capture failed: {e}"
            )
    raise RuntimeError(
        f"NO_RATING = INVALID_RENDER_RECEIPT — non-interactive run requires --{axis_name.replace('_', '-')} 1-10"
    )


def _capture_decision(flag_value: str | None) -> str:
    if flag_value is not None:
        print(f"      ✓ operator_decision from flag: {flag_value}")
        return flag_value  # argparse already constrained to {KEEP, REJECT}
    if sys.stdin.isatty():
        try:
            raw = input("Operator decision (KEEP or REJECT): ").strip().upper()
            if raw not in ("KEEP", "REJECT"):
                raise ValueError(f"operator_decision {raw!r} not in {{KEEP, REJECT}}")
            return raw
        except (ValueError, EOFError, KeyboardInterrupt) as e:
            raise RuntimeError(
                f"NO_RATING = INVALID_RENDER_RECEIPT — interactive operator_decision capture failed: {e}"
            )
    raise RuntimeError(
        "NO_RATING = INVALID_RENDER_RECEIPT — non-interactive run requires --operator-decision KEEP|REJECT"
    )


def _capture_failure_class(flag_value: str | None, decision: str) -> str | None:
    if flag_value:
        return flag_value
    if decision == "REJECT" and sys.stdin.isatty():
        try:
            raw = input("Failure class (free string, blank = unspecified): ").strip()
            return raw or None
        except (EOFError, KeyboardInterrupt):
            return None
    return None


operator_decision = _capture_decision(_ARGS.operator_decision)
pipeline_score = _capture_score(
    _ARGS.pipeline_score,
    "pipeline_score",
    "Pipeline score (1-10, did rails work correctly?): ",
)
output_score = _capture_score(
    _ARGS.output_score,
    "output_score",
    "Output score (1-10, is video cinematic HELEN performance?): ",
)
failure_class = _capture_failure_class(_ARGS.failure_class, operator_decision)

receipt["operator_decision"] = operator_decision
receipt["pipeline_score"] = pipeline_score
receipt["output_score"] = output_score
receipt["failure_class"] = failure_class
receipt_path.write_text(json.dumps(receipt, indent=2))
print(
    f"      ✓ receipt finalized → {receipt_path} "
    f"(decision={operator_decision}, pipeline={pipeline_score}, output={output_score}, failure_class={failure_class})"
)

print()
print("=== HELEN RENDER PILOT v2 — RESULT ===")
print(f"Seed:           {SEED_PATH}")
print(f"Higgsfield CDN: {public_url}")
print(f"Kling output:   {out_path} ({out_path.stat().st_size/1024:.0f} KB)")
print(f"Telegram msg:   {msg_id} (chat={CHAT_ID}, duration={duration}s)")
print(f"Receipt:        {receipt_path}")
