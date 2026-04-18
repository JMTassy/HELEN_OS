#!/usr/bin/env python3
"""
HELEN Telegram Bot — Two-way dialogue with voice
Polls for messages, runs them through helen_say + kernel,
generates Zephyr TTS, sends back voice + text.

Usage:
    GEMINI_API_KEY=... python3 tools/helen_telegram.py

Requires: kernel daemon running (oracle_town/kernel/kernel_daemon.py)
"""
import json
import os
import re
import subprocess
import sys
import time
import tempfile
from pathlib import Path

import datetime as _dt

ROOT = Path(__file__).resolve().parent.parent
HELEN_SAY = ROOT / "tools" / "helen_say.py"
HELEN_TTS = ROOT / "oracle_town" / "skills" / "voice" / "gemini_tts" / "helen_tts.py"
VENV_PYTHON = ROOT / ".venv" / "bin" / "python"
LEDGER = ROOT / "town" / "ledger_v1.ndjson"
INTENTS = ROOT / "town" / "intents_v1.ndjson"

# Config from openclaw.json
OPENCLAW_CFG = Path.home() / ".openclaw" / "openclaw.json"
with open(OPENCLAW_CFG) as f:
    cfg = json.load(f)
BOT_TOKEN = cfg["channels"]["telegram"]["botToken"]

GEMINI_KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or ""
POLL_INTERVAL = 2  # seconds
OFFSET_FILE = Path.home() / ".openclaw" / "telegram" / "helen-bot-offset.json"

ANSI_RE = re.compile(r'\x1b\[[0-9;]*m')


def load_offset() -> int:
    if OFFSET_FILE.exists():
        try:
            return json.loads(OFFSET_FILE.read_text()).get("offset", 0)
        except Exception:
            pass
    return 0


def save_offset(offset: int):
    OFFSET_FILE.parent.mkdir(parents=True, exist_ok=True)
    OFFSET_FILE.write_text(json.dumps({"offset": offset}))


def tg_api(method: str, **kwargs):
    """Call Telegram Bot API."""
    import urllib.request
    import urllib.parse
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"

    # Handle file uploads separately
    files = {}
    data = {}
    for k, v in kwargs.items():
        if isinstance(v, Path) or (isinstance(v, str) and os.path.isfile(v)):
            files[k] = v
        else:
            data[k] = str(v)

    if files:
        # Use curl for multipart (simpler than urllib multipart)
        cmd = ["curl", "-s", "-X", "POST", url]
        for k, v in data.items():
            cmd += ["-F", f"{k}={v}"]
        for k, v in files.items():
            cmd += ["-F", f"{k}=@{v}"]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return json.loads(r.stdout)
    else:
        payload = urllib.parse.urlencode(data).encode()
        req = urllib.request.Request(url, data=payload)
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())


def get_updates(offset: int):
    return tg_api("getUpdates", offset=offset, timeout=20)


def send_text(chat_id, text):
    # Telegram max message length is 4096
    text = text[:4000]
    return tg_api("sendMessage", chat_id=chat_id, text=text)


def send_voice(chat_id, ogg_path, caption=""):
    return tg_api("sendVoice", chat_id=chat_id, voice=ogg_path, caption=caption[:1024])


def helen_say(msg: str) -> tuple[str, str]:
    """Run helen_say, return (her_text, verdict)."""
    try:
        r = subprocess.run(
            ["python3", str(HELEN_SAY), msg, "--ledger", str(LEDGER)],
            capture_output=True, text=True, timeout=10, cwd=str(ROOT)
        )
        clean = ANSI_RE.sub('', r.stdout + r.stderr)
        her_text = ""
        verdict = "?"
        lines = clean.split("\n")
        in_her = False
        her_lines = []
        for line in lines:
            if "[HER]" in line:
                in_her = True
                continue
            if "[HAL]" in line:
                in_her = False
                if "PASS" in line: verdict = "PASS"
                elif "BLOCK" in line: verdict = "BLOCK"
                elif "WARN" in line: verdict = "WARN"
                continue
            if in_her and line.strip():
                her_lines.append(line.strip())
        her_text = "\n".join(her_lines)
        return (her_text or msg, verdict)
    except Exception as e:
        return (f"[kernel error: {e}]", "BLOCK")


def generate_voice(text: str) -> str | None:
    """Generate TTS, convert to OGG for Telegram voice note. Returns path or None."""
    if not GEMINI_KEY:
        return None
    try:
        with tempfile.TemporaryDirectory() as tmp:
            env = os.environ.copy()
            env["GEMINI_API_KEY"] = GEMINI_KEY
            r = subprocess.run(
                [str(VENV_PYTHON), str(HELEN_TTS), "--output-dir", tmp, text],
                capture_output=True, text=True, timeout=30, env=env, cwd=str(ROOT)
            )
            wav_path = None
            for line in r.stdout.split("\n"):
                if line.startswith("Audio:"):
                    wav_path = line.split("Audio:")[-1].strip()
                    break
            if not wav_path or not os.path.exists(wav_path):
                return None
            # Convert WAV to OGG (Telegram voice notes need opus/ogg)
            ogg_path = wav_path.replace(".wav", ".ogg")
            subprocess.run(
                ["ffmpeg", "-y", "-i", wav_path, "-c:a", "libopus", "-b:a", "64k", ogg_path],
                capture_output=True, timeout=15
            )
            if os.path.exists(ogg_path):
                # Copy to a stable tmp path (the tempdir will be cleaned)
                stable = f"/tmp/helen_voice_{int(time.time())}.ogg"
                subprocess.run(["cp", ogg_path, stable])
                return stable
    except Exception as e:
        print(f"  [TTS error] {e}")
    return None


# ─── Accountability Engine (/commit, /witness, /done) ─────────────────────────

def _now_utc() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat().replace("+00:00", "Z")


def _load_intents() -> list[dict]:
    if not INTENTS.exists():
        return []
    entries = []
    for line in INTENTS.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            try:
                entries.append(json.loads(line))
            except Exception:
                pass
    return entries


def _next_seq() -> int:
    entries = _load_intents()
    return max((e.get("seq", 0) for e in entries), default=0) + 1


def _append_intent(entry: dict):
    INTENTS.parent.mkdir(parents=True, exist_ok=True)
    with INTENTS.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def cmd_commit(chat_id: int, args: str) -> str:
    """Parse '/commit <action> by <deadline>' and record intent."""
    parts = args.rsplit(" by ", 1)
    if len(parts) != 2 or not parts[0].strip() or not parts[1].strip():
        return "Format: /commit <action> by <deadline>\nExample: /commit finish the README by 2026-04-18"
    action = parts[0].strip()
    deadline = parts[1].strip()
    seq = _next_seq()
    entry = {
        "seq": seq,
        "action": action,
        "deadline": deadline,
        "status": "OPEN",
        "created_utc": _now_utc(),
    }
    _append_intent(entry)
    return f"Witnessed. You said:\n\"{action}\"\nby {deadline}.\n[seq={seq}]"


def cmd_witness(chat_id: int) -> str:
    """List all OPEN intents with age."""
    entries = _load_intents()
    open_entries = [e for e in entries if e.get("status") == "OPEN"]
    if not open_entries:
        return "No open commits. Clean slate."
    now = _dt.datetime.now(_dt.timezone.utc)
    lines = [f"{len(open_entries)} open commit(s):\n"]
    for e in open_entries:
        created = e.get("created_utc", "")
        try:
            created_dt = _dt.datetime.fromisoformat(created.replace("Z", "+00:00"))
            age = (now - created_dt).days
        except Exception:
            age = "?"
        lines.append(f"  [{e['seq']}] \"{e['action']}\" by {e['deadline']} ({age}d ago)")
    return "\n".join(lines)


def cmd_done(chat_id: int, args: str) -> str:
    """Mark an intent as CLOSED by seq number."""
    try:
        target_seq = int(args.strip())
    except ValueError:
        return "Format: /done <seq_number>\nExample: /done 1"

    entries = _load_intents()
    found = None
    for e in entries:
        if e.get("seq") == target_seq and e.get("status") == "OPEN":
            found = e
            break
    if not found:
        return f"No open commit with seq={target_seq}."

    closed_utc = _now_utc()
    found["status"] = "CLOSED"
    found["closed_utc"] = closed_utc

    # Compute gap
    gap_str = ""
    try:
        deadline_dt = _dt.datetime.fromisoformat(found["deadline"])
        if deadline_dt.tzinfo is None:
            deadline_dt = deadline_dt.replace(tzinfo=_dt.timezone.utc)
        closed_dt = _dt.datetime.fromisoformat(closed_utc.replace("Z", "+00:00"))
        gap_days = (closed_dt - deadline_dt).days
        if gap_days <= 0:
            gap_str = f"Gap: {gap_days}d (early)"
        else:
            gap_str = f"Gap: +{gap_days}d (late)"
        found["gap_days"] = gap_days
    except Exception:
        gap_str = "Gap: unknown (deadline not ISO format)"

    # Rewrite the file
    INTENTS.write_text(
        "\n".join(json.dumps(e, ensure_ascii=False) for e in entries) + "\n",
        encoding="utf-8",
    )
    return f"Done. \"{found['action']}\"\n{gap_str}"


# ─── Video Generation (/video) ─────────────────────────────────────────────────

def cmd_video(chat_id: int, topic: str) -> None:
    """Generate a short video on <topic> with Zephyr narration and send to Telegram."""
    send_text(chat_id, f"Generating video: \"{topic}\"...")

    # 1. Generate voiceover
    if not GEMINI_KEY:
        send_text(chat_id, "No GEMINI_API_KEY — cannot generate voice.")
        return
    try:
        env = os.environ.copy()
        env["GEMINI_API_KEY"] = GEMINI_KEY
        with tempfile.TemporaryDirectory() as tmp:
            r = subprocess.run(
                [str(VENV_PYTHON), str(HELEN_TTS), "--output-dir", tmp, topic],
                capture_output=True, text=True, timeout=30, env=env, cwd=str(ROOT)
            )
            wav_path = None
            for line in r.stdout.split("\n"):
                if line.startswith("Audio:"):
                    wav_path = line.split("Audio:")[-1].strip()
                    break
            if not wav_path or not os.path.exists(wav_path):
                send_text(chat_id, "TTS failed.")
                return

            # 2. Generate frames with Pillow
            from PIL import Image, ImageDraw, ImageFont
            import math

            W, H = 1080, 1920
            FPS = 30
            dur_r = subprocess.run(
                ["ffprobe", "-i", wav_path, "-show_entries", "format=duration", "-v", "quiet", "-of", "csv=p=0"],
                capture_output=True, text=True
            )
            dur = float(dur_r.stdout.strip()) + 1.0
            total_frames = int(dur * FPS)

            try:
                fn_big = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 64)
                fn_med = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 36)
                fn_sm = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 20)
            except Exception:
                fn_big = fn_med = fn_sm = ImageFont.load_default()

            frames_dir = os.path.join(tmp, "frames")
            os.makedirs(frames_dir)

            # Word-wrap the topic for display
            words = topic.split()
            lines_display = []
            cur = ""
            for w in words:
                test = f"{cur} {w}".strip()
                if len(test) > 28 and cur:
                    lines_display.append(cur)
                    cur = w
                else:
                    cur = test
            if cur:
                lines_display.append(cur)

            for fi in range(total_frames):
                t = fi / FPS
                img = Image.new("RGB", (W, H), (6, 8, 18))
                draw = ImageDraw.Draw(img)

                # Breathing glow
                pulse = 0.3 + 0.2 * math.sin(t * 1.5)
                for r in range(200, 0, -10):
                    op = int(pulse * 40 * (1 - r / 200))
                    c = (int(34 * op / 255), int(211 * op / 255), int(238 * op / 255))
                    draw.ellipse([W//2-r, 500-r, W//2+r, 500+r], fill=c)

                # HELEN title
                a = min(1.0, t / 1.5)
                bbox = draw.textbbox((0, 0), "HELEN", font=fn_big)
                tw = bbox[2] - bbox[0]
                draw.text(((W-tw)//2, 380), "HELEN", fill=(int(201*a), int(169*a), int(97*a)), font=fn_big)

                # Topic text
                a2 = min(1.0, max(0, (t - 1.5) / 1.0))
                for i, line in enumerate(lines_display):
                    bbox = draw.textbbox((0, 0), line, font=fn_med)
                    tw = bbox[2] - bbox[0]
                    y = 700 + i * 50
                    draw.text(((W-tw)//2, y), line, fill=(int(226*a2), int(232*a2), int(240*a2)), font=fn_med)

                # Footer
                a3 = min(1.0, max(0, (t - 3) / 0.8))
                footer = "Voice: Zephyr  |  HELEN OS"
                bbox = draw.textbbox((0, 0), footer, font=fn_sm)
                tw = bbox[2] - bbox[0]
                draw.text(((W-tw)//2, 1800), footer, fill=(int(100*a3), int(116*a3), int(139*a3)), font=fn_sm)

                # Floating particles
                for pi in range(15):
                    px = (80 + pi * 73 + int(t * 10 * (1 + pi % 3))) % W
                    py = (200 + pi * 127 - int(t * 15 * (1 + pi % 2))) % H
                    ps = 1 + (pi % 2)
                    pc = (201, 169, 97) if pi % 3 == 0 else (34, 211, 238)
                    pa = max(0, min(255, int(100 * math.sin(t * 0.5 + pi))))
                    draw.ellipse([px-ps, py-ps, px+ps, py+ps], fill=(*pc, pa))

                img.save(f"{frames_dir}/frame_{fi:05d}.png")

            # 3. Mux frames + audio → MP4
            mp4_path = os.path.join(tmp, "helen_video.mp4")
            subprocess.run([
                "ffmpeg", "-y",
                "-framerate", str(FPS),
                "-i", f"{frames_dir}/frame_%05d.png",
                "-i", wav_path,
                "-c:v", "libx264", "-preset", "fast", "-crf", "23", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "128k",
                "-shortest", mp4_path
            ], capture_output=True, timeout=120)

            if not os.path.exists(mp4_path):
                send_text(chat_id, "Video encoding failed.")
                return

            # 4. Send to Telegram
            result = tg_api("sendVideo",
                chat_id=chat_id,
                video=mp4_path,
                caption=f"HELEN — {topic[:100]}"
            )
            if result.get("ok"):
                print(f"  [VIDEO] sent msg_id={result['result']['message_id']}")
            else:
                send_text(chat_id, f"Video send failed: {result.get('description', '?')}")

    except Exception as e:
        send_text(chat_id, f"Video error: {e}")
        print(f"  [VIDEO ERROR] {e}")


# ─── Message Handler ──────────────────────────────────────────────────────────

def handle_message(msg: dict):
    chat_id = msg["chat"]["id"]
    text = msg.get("text", "")
    user = msg.get("from", {}).get("first_name", "?")

    if not text:
        return

    print(f"  [{user}] {text}")

    # Command routing — video
    if text.startswith("/video "):
        cmd_video(chat_id, text[7:].strip())
        return

    # Command routing — accountability engine
    if text.startswith("/commit "):
        reply = cmd_commit(chat_id, text[8:])
        send_text(chat_id, reply)
        voice_path = generate_voice(reply.split("\n")[0])
        if voice_path:
            send_voice(chat_id, voice_path, caption="Witnessed")
            os.remove(voice_path)
        print(f"  [COMMIT] {reply.split(chr(10))[0]}")
        return

    if text.strip() in ("/witness", "/witness@bot"):
        reply = cmd_witness(chat_id)
        send_text(chat_id, reply)
        voice_path = generate_voice(reply.split("\n")[0])
        if voice_path:
            send_voice(chat_id, voice_path, caption="Witness")
            os.remove(voice_path)
        print(f"  [WITNESS] {reply.split(chr(10))[0]}")
        return

    if text.startswith("/done "):
        reply = cmd_done(chat_id, text[6:])
        send_text(chat_id, reply)
        voice_path = generate_voice(reply.split("\n")[0])
        if voice_path:
            send_voice(chat_id, voice_path, caption="Done")
            os.remove(voice_path)
        print(f"  [DONE] {reply.split(chr(10))[0]}")
        return

    # Knowledge retrieval — search user's corpus for relevant context
    knowledge_context = ""
    try:
        import sys as _sys
        _sys.path.insert(0, str(ROOT))
        from helen_os.knowledge.engine import KnowledgeEngine
        engine = KnowledgeEngine()
        # Extract tags from the message (if user uses #tags)
        user_tags = [m.lower() for m in re.findall(r'#([A-Za-z]\w+)', text)]
        results = engine.retrieve(text, tags=user_tags if user_tags else None, k=3)
        if results:
            parts = []
            for r in results:
                parts.append(f"[{r.source_file.split('/')[-1]}] {r.content[:200]}")
            knowledge_context = "\n".join(parts)
            print(f"  [knowledge] {len(results)} results, tags={user_tags}")
    except Exception as e:
        print(f"  [knowledge] {e}")

    # Default: free text through kernel (with knowledge context appended)
    msg_with_context = text
    if knowledge_context:
        msg_with_context = f"{text}\n\n[HELEN knowledge context from your corpus:]\n{knowledge_context}"
    her_text, verdict = helen_say(msg_with_context)
    print(f"  [HELEN {verdict}] {her_text[:80]}")

    # Send text response immediately
    reply = f"[HAL {verdict}]\n{her_text}"
    if knowledge_context:
        reply += f"\n\n📚 Sources: {', '.join(r.source_file.split('/')[-1] for r in results)}"
    send_text(chat_id, reply)

    # Generate and send voice (async-ish)
    # Speak only the ACK/receipt part, not the full dump
    speak_text = her_text.split("\n")[0] if her_text else text
    voice_path = generate_voice(speak_text)
    if voice_path:
        try:
            send_voice(chat_id, voice_path, caption="Zephyr")
            os.remove(voice_path)
            print(f"  [voice sent]")
        except Exception as e:
            print(f"  [voice send error] {e}")


def main():
    print(f"HELEN Telegram Bot")
    print(f"  Bot: {BOT_TOKEN[:12]}...")
    print(f"  Voice: {'Zephyr (Gemini TTS)' if GEMINI_KEY else 'OFF (no GEMINI_API_KEY)'}")
    print(f"  Kernel: {HELEN_SAY}")
    print(f"  Polling every {POLL_INTERVAL}s...")
    print()

    offset = load_offset()

    while True:
        try:
            updates = get_updates(offset)
            if not updates.get("ok"):
                print(f"  [poll error] {updates}")
                time.sleep(5)
                continue

            for update in updates.get("result", []):
                offset = update["update_id"] + 1
                save_offset(offset)
                if "message" in update:
                    handle_message(update["message"])

        except KeyboardInterrupt:
            print("\nStopped.")
            break
        except Exception as e:
            print(f"  [error] {e}")
            time.sleep(5)

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()


# ─── Knowledge Integration ───────────────────────────────────────────────────

def search_knowledge(question: str, top_k: int = 3) -> str:
    """Search HELEN's knowledge index for context relevant to the question."""
    if not GEMINI_KEY:
        return ""
    try:
        import sys as _sys
        _sys.path.insert(0, str(ROOT))
        from helen_os.knowledge.ingest import query
        results = query(question, GEMINI_KEY, top_k=top_k)
        if not results:
            return ""
        context_parts = []
        for r in results:
            if r["score"] > 0.5:  # only include relevant results
                context_parts.append(f"[From {Path(r['file']).name}, relevance {r['score']}]\n{r['preview']}")
        if context_parts:
            return "\n---\n".join(context_parts)
    except Exception as e:
        print(f"  [knowledge] search error: {e}")
    return ""
