#!/usr/bin/env python3
"""
skills_video.py — HELEN OS next-skills showcase → Telegram
Pillow frames → ffmpeg → sendVideo
authority=false  canon=NO_SHIP  class=EPHEMERAL
"""
from __future__ import annotations
import json, os, sys, time, pathlib, subprocess, urllib.request, urllib.error, io
from PIL import Image, ImageDraw

# ── env ──────────────────────────────────────────────────────────────────────
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
TG_TOKEN   = _env.get("TELEGRAM_BOT_TOKEN", os.environ.get("TELEGRAM_BOT_TOKEN", ""))
TG_CHAT_ID = "6624890918"

OUT = pathlib.Path(__file__).parent / "output"
OUT.mkdir(exist_ok=True)

# ── palette ───────────────────────────────────────────────────────────────────
BG      = (5,  5,  8)
DIM     = (255,255,255,30)
WHITE   = (255,255,255,180)
BRIGHT  = (255,255,255,230)
CYAN    = (0,  229,255)
AMBER   = (255,179,  0)
GREEN   = (0,  255, 65)
RED     = (255, 23, 68)
GREY    = (255,255,255,50)

# ── skills data ──────────────────────────────────────────────────────────────
SKILLS = [
    {
        "id": "SOURCE_PILOT",
        "label": "Source Pilot",
        "status": "LIVE",
        "color": CYAN,
        "desc": "Full-screen source mode. HELEN overlays semantic\nhotspots directly on any document, video,\nor email. Click to inspect. Make a receipt.",
        "tags": ["CLAIM","GAP","RECEIPT","ENTITY","RISK"],
    },
    {
        "id": "RECEIPT_WRITER",
        "label": "Receipt Writer",
        "status": "LIVE",
        "color": GREEN,
        "desc": "Every claim gets a receipt. Every receipt\ngets a hash. NO RECEIPT = NO CLAIM.\nMAYOR signs. Chain is sacred.",
        "tags": ["sha256","append-only","MAYOR gate","NO_SHIP guard"],
    },
    {
        "id": "AUTORESEARCH",
        "label": "Autoresearch",
        "status": "E12 SHIPPED",
        "color": AMBER,
        "desc": "Self-inquiry engine. One hypothesis per epoch.\nObservable signals only. HAL gate + tranche\nreceipt between every epoch.",
        "tags": ["LEGORACLE","replay gate","E13 next","HAL gated"],
    },
    {
        "id": "HAL_GATE",
        "label": "HAL Gate",
        "status": "ACTIVE",
        "color": AMBER,
        "desc": "Strict two-block validator. HER proposes.\nHAL scores admissibility before any claim\nenters the ledger. SHIP or NO_SHIP only.",
        "tags": ["Gate A/B/C","MAYOR","non-sovereign","receipt required"],
    },
    {
        "id": "EMAIL_TRIAGE",
        "label": "Email Triage",
        "status": "PROPOSED",
        "color": (255,255,255,120),
        "desc": "Classify incoming email as SIGNAL / NOISE /\nACTION / ARCHIVE. Tag each thread with\nsource + project + receipt status.",
        "tags": ["ENTITY","TASK","RECEIPT","HOLD"],
    },
    {
        "id": "BRAND_VOICE",
        "label": "Brand Voice",
        "status": "PROPOSED",
        "color": (255,255,255,120),
        "desc": "UZIK writing style enforced on all public\ncopy. Negative parallelism banned. Deck tone.\nNever chatbot tone.",
        "tags": ["UZIK style","no AI attribution","HELEN OS only"],
    },
    {
        "id": "INVESTOR_UPDATES",
        "label": "Investor Updates",
        "status": "PROPOSED",
        "color": (255,255,255,120),
        "desc": "Weekly signal digest for Rothschild demo.\nKPI + receipt count + MAYOR verdicts +\nnext milestone. Wow + reliability.",
        "tags": ["€2.8M raise","Rothschild","HELEN OS"],
    },
    {
        "id": "DASHBOARD_DESIGNER",
        "label": "Dashboard Designer",
        "status": "PROPOSED",
        "color": (255,255,255,120),
        "desc": "Operator state deck. 8 moods → HELEN modes.\nCapacity visible. No hidden mutation.\nSingle cockpit. Receipt-first.",
        "tags": ["operator state","ADHD-compatible","sovereign-first"],
    },
]

W, H = 1080, 1080
FPS  = 30

# ── font loader ───────────────────────────────────────────────────────────────
def _font(size: int):
    for path in [
        "/System/Library/Fonts/Menlo.ttc",
        "/System/Library/Fonts/Monaco.ttf",
        "/System/Library/Fonts/Courier New.ttf",
        "/Library/Fonts/Courier New.ttf",
    ]:
        try:
            from PIL import ImageFont
            return ImageFont.truetype(path, size)
        except Exception:
            pass
    from PIL import ImageFont
    return ImageFont.load_default()

# ── drawing primitives ────────────────────────────────────────────────────────
def _rgba(color, alpha=None):
    if isinstance(color, tuple):
        if len(color) == 4:
            if alpha is not None:
                return (*color[:3], alpha)
            return color
        return (*color, alpha if alpha is not None else 255)
    return color

def draw_text(d: ImageDraw.Draw, xy, text: str, font, fill):
    d.text(xy, text, font=font, fill=fill)

def draw_grid(img: Image.Image, spacing=90, alpha=8):
    ov = Image.new("RGBA", img.size, (0,0,0,0))
    d = ImageDraw.Draw(ov)
    for x in range(0, W, spacing):
        d.line([(x,0),(x,H)], fill=(0,255,65,alpha), width=1)
    for y in range(0, H, spacing):
        d.line([(0,y),(W,y)], fill=(0,255,65,alpha), width=1)
    img.paste(ov, mask=ov)

def draw_scanline(img: Image.Image, y: int):
    ov = Image.new("RGBA", img.size, (0,0,0,0))
    d = ImageDraw.Draw(ov)
    d.rectangle([(0, y-3),(W, y+3)], fill=(0,255,65,18))
    img.paste(ov, mask=ov)

# ── title card ────────────────────────────────────────────────────────────────
def make_title_frame(scan_y: int) -> Image.Image:
    img = Image.new("RGB", (W,H), BG)
    draw_grid(img)
    draw_scanline(img, scan_y % H)
    d = ImageDraw.Draw(img)

    f_big  = _font(52)
    f_med  = _font(22)
    f_sm   = _font(13)
    f_tiny = _font(10)

    # top line
    d.line([(0,70),(W,70)], fill=(255,255,255,18), width=1)

    # HELEN OS label
    draw_text(d, (54,30), "HELEN OS  ·  SKILL SHOWCASE", f_sm, (255,255,255,80))

    # main title
    draw_text(d, (54,130), "NEXT SKILLS", f_big, (0,229,255,230))
    draw_text(d, (54,198), "What HELEN can do — and what's coming.", f_med, (255,255,255,140))

    # divider
    d.line([(54,250),(W-54,250)], fill=(0,229,255,40), width=1)

    # skill count
    live     = sum(1 for s in SKILLS if "LIVE" in s["status"] or "SHIPPED" in s["status"] or "ACTIVE" in s["status"])
    proposed = sum(1 for s in SKILLS if "PROPOSED" in s["status"])

    draw_text(d, (54,280),  f"✓  {live}  skills  LIVE / SHIPPED", f_sm, (0,255,65,200))
    draw_text(d, (54,304),  f"·  {proposed}  skills  PROPOSED", f_sm, (255,255,255,80))

    # authority footer
    d.line([(0, H-60),(W, H-60)], fill=(255,255,255,14), width=1)
    draw_text(d, (54, H-44), "authority=false  ·  NO_SHIP  ·  HELEN OS  ·  JMT", f_tiny, (255,255,255,50))
    draw_text(d, (W-200, H-44), f"2026-05-10", f_tiny, (255,255,255,35))
    return img


# ── skill card ────────────────────────────────────────────────────────────────
def make_skill_frame(sk: dict, scan_y: int, progress: float) -> Image.Image:
    img = Image.new("RGB", (W,H), BG)
    draw_grid(img)
    draw_scanline(img, scan_y % H)
    d = ImageDraw.Draw(img)

    color = sk["color"]
    if isinstance(color, tuple) and len(color)==4:
        rgb = color[:3]
        al  = color[3]
    else:
        rgb = color
        al  = 230

    f_id   = _font(10)
    f_lbl  = _font(46)
    f_desc = _font(16)
    f_tag  = _font(10)
    f_stat = _font(11)
    f_tiny = _font(10)

    # top rule
    d.line([(0,70),(W,70)], fill=(255,255,255,18), width=1)
    draw_text(d, (54,30), "HELEN OS  ·  SKILL SHOWCASE", f_id, (255,255,255,60))

    # skill number badge
    idx = SKILLS.index(sk) + 1
    draw_text(d, (54,95), f"{idx:02d} / {len(SKILLS):02d}", f_id, (*rgb, 90))

    # status pill
    st_color = (0,255,65,200) if "LIVE" in sk["status"] or "ACTIVE" in sk["status"] or "SHIPPED" in sk["status"] else (255,255,255,60)
    draw_text(d, (W-200, 95), sk["status"], f_stat, st_color)

    # main label
    draw_text(d, (54, 130), sk["label"].upper(), f_lbl, (*rgb, al))

    # skill id small
    draw_text(d, (54, 194), sk["id"], f_id, (255,255,255,45))

    # divider
    d.line([(54,220),(W-54,220)], fill=(*rgb,40), width=1)

    # description
    y = 246
    for line in sk["desc"].split("\n"):
        draw_text(d, (54,y), line, f_desc, (255,255,255,150))
        y += 26

    # tags
    y += 24
    x = 54
    for tag in sk["tags"]:
        tw = len(tag)*7 + 18
        ov = Image.new("RGBA", img.size, (0,0,0,0))
        od = ImageDraw.Draw(ov)
        od.rectangle([(x,y),(x+tw,y+22)], outline=(*rgb,50), fill=(*rgb,14), width=1)
        img.paste(ov, mask=ov)
        draw_text(d, (x+9, y+6), tag, f_tag, (*rgb, 160))
        x += tw + 8
        if x > W - 200:
            x = 54
            y += 30

    # progress bar
    bar_y = H - 90
    bar_w = int((W - 108) * progress)
    ov = Image.new("RGBA", img.size, (0,0,0,0))
    od = ImageDraw.Draw(ov)
    od.rectangle([(54, bar_y),(W-54, bar_y+2)], fill=(255,255,255,14))
    od.rectangle([(54, bar_y),(54+bar_w, bar_y+2)], fill=(*rgb, 120))
    img.paste(ov, mask=ov)

    # footer
    d.line([(0, H-60),(W, H-60)], fill=(255,255,255,14), width=1)
    draw_text(d, (54, H-44), "authority=false  ·  NO_SHIP  ·  HELEN OS  ·  JMT", f_tiny, (255,255,255,50))
    draw_text(d, (W-200, H-44), "NO RECEIPT YET", f_tiny, (255,179,0,80))
    return img


# ── render all frames → mp4 ──────────────────────────────────────────────────
def render_video() -> pathlib.Path:
    frames_dir = OUT / "skill_frames"
    frames_dir.mkdir(exist_ok=True)

    title_dur   = int(FPS * 3.0)   # 3 s title
    card_dur    = int(FPS * 3.5)   # 3.5 s per skill
    fade_dur    = int(FPS * 0.35)  # 0.35 s fade

    frame_idx = 0
    scan_tick = 0

    def save(img, i):
        img.save(frames_dir / f"f{i:05d}.png")

    def fade_between(imgA, imgB, n_frames, start_idx):
        nonlocal frame_idx
        for fi in range(n_frames):
            t   = fi / max(n_frames-1,1)
            blended = Image.blend(imgA.convert("RGBA"), imgB.convert("RGBA"), t).convert("RGB")
            save(blended, start_idx + fi)

    print(f"  Rendering {title_dur + len(SKILLS)*(card_dur+fade_dur)} frames…")

    # title frames
    for i in range(title_dur):
        scan_tick += 2
        f = make_title_frame(scan_tick)
        save(f, frame_idx); frame_idx += 1

    prev_img = make_title_frame(scan_tick)

    # skill cards
    for si, sk in enumerate(SKILLS):
        progress = (si+1) / len(SKILLS)

        # fade in
        first_card = make_skill_frame(sk, scan_tick, progress)
        fade_between(prev_img, first_card, fade_dur, frame_idx)
        frame_idx += fade_dur

        for i in range(card_dur - fade_dur):
            scan_tick += 2
            f = make_skill_frame(sk, scan_tick, progress)
            save(f, frame_idx); frame_idx += 1

        prev_img = make_skill_frame(sk, scan_tick, progress)

    out_mp4 = OUT / f"skills_{int(time.time())}.mp4"
    cmd = [
        "ffmpeg", "-y",
        "-framerate", str(FPS),
        "-i", str(frames_dir / "f%05d.png"),
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "22",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        str(out_mp4),
    ]
    print(f"  ffmpeg encode…")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ✗ ffmpeg: {result.stderr[-400:]}")
        sys.exit(1)
    print(f"  ✓ {out_mp4.name} ({out_mp4.stat().st_size//1024} KB)")

    # cleanup frames
    for f in frames_dir.glob("*.png"):
        f.unlink()
    frames_dir.rmdir()

    return out_mp4


# ── Telegram sendVideo ────────────────────────────────────────────────────────
def send_telegram_video(path: pathlib.Path, caption: str) -> None:
    print(f"  Telegram → chat {TG_CHAT_ID}")
    boundary = "----HELENskills1234"
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
                print(f"  ✓ SENT · message_id={msg_id}")
            else:
                print(f"  ✗ Telegram error: {resp}")
    except urllib.error.HTTPError as e:
        print(f"  ✗ HTTP {e.code}: {e.read()[:300]}")


# ── main ──────────────────────────────────────────────────────────────────────
def main():
    print("\n══ HELEN OS — SKILLS SHOWCASE PIPELINE ══")
    print("   authority=false · NO_SHIP · EPHEMERAL\n")

    print("[1/2] Rendering frames…")
    mp4 = render_video()

    caption = (
        "HELEN OS — NEXT SKILLS\n"
        "\n"
        "✓ Source Pilot · Receipt Writer · Autoresearch · HAL Gate\n"
        "· Email Triage · Brand Voice · Investor Updates · Dashboard Designer\n"
        "\n"
        "authority=false · NO_SHIP\n"
        "HELEN OS · JM Tassy"
    )

    print("[2/2] Sending to Telegram…")
    send_telegram_video(mp4, caption)

    print(f"\nSHIP: {mp4.name} → Telegram chat {TG_CHAT_ID}")


if __name__ == "__main__":
    main()
