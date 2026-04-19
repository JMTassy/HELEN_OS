#!/usr/bin/env python3
"""
HELEN — Shot 1 "Mystery Initiation" — Kling I2V 3s test
1. Upload shot1_initiation_seed.png to Higgsfield CDN
2. Submit Kling I2V (3s, 1080p) with Egyptian temple entrance prompt
3. Poll until done
4. Download to /tmp/helen_initiation/kling_shots/
"""
import json, os, time, urllib.request, urllib.error
from pathlib import Path

# ── Credentials from ~/.helen_env ────────────────────────────────────────────
env = {}
for ln in (Path.home() / ".helen_env").read_text().splitlines():
    ln = ln.strip()
    if ln.startswith("export "): ln = ln[7:]
    if "=" in ln:
        k, v = ln.split("=", 1)
        env[k.strip()] = v.strip().strip('"').strip("'")

HF_ID     = env.get("HIGGSFIELD_ID", env.get("HF_API_KEY", ""))
HF_SECRET = env.get("HIGGSFIELD_SECRET", env.get("HF_API_SECRET", ""))
AUTH      = f"Key {HF_ID}:{HF_SECRET}"
BASE      = "https://platform.higgsfield.ai"
UA        = "higgsfield-client-py/1.0"

SEED      = Path("/tmp/helen_initiation/shot1_initiation_seed_v4.png")
OUT       = Path("/tmp/helen_initiation/kling_shots")
OUT.mkdir(parents=True, exist_ok=True)

PROMPT_3S = """1080px, 9:16, 24fps, 5s

[SHOT]
Full shot — camera locked on tripod, zero movement, zero drift, zero push.
35mm anamorphic, f/2.4 — foreground figures sharp, archway depth softens naturally.

[SUBJECT]
Two robed figures at the threshold of a massive limestone archway.
SEEKER: young woman, centered, slightly left. Vibrant orange-red wavy hair,
medium length, visible above and around the blindfold — lit amber-orange by torchlight
on left side, deeper burnt-orange in shadow on right. Fair skin, freckles on forehead
and cheeks. White linen blindfold band across eyes. Dark near-black linen robe,
hands clasped at waist. Head bowed 10 degrees.
GUIDE: slightly right and behind seeker, darker charcoal robe,
right hand resting on seeker's left upper arm. Both face into the arch.

[ACTION]
[0s-5s] Both figures completely motionless. No swaying. No breathing visible.
No robe flutter. Torch flames flicker irregularly. Low mist drifts 2cm/sec leftward
at floor level. These are the only two motion sources in the frame.

[ENVIRONMENT]
Underground Egyptian mystery-school temple. Massive limestone block archway,
dressed stone columns with shallow bas-relief hieroglyph cartouches carved into face.
Stone floor continues into near-total darkness beyond the threshold. Ceiling not visible.
Space feels subterranean, ancient, and immense.

[LIGHTING]
Two wall-mounted iron-cage torches on each inner column face, height 160cm from floor.
Left torch: 3200K amber, casts directional fill across left face of seeker's robe
and left column surface. Right torch: symmetric, fills guide's robe and right column.
Floor warm spill in 80cm radius from each torch base. Central zone dim, no ambient fill.
No overhead source. No cool tones. No reflected sky. Pure amber-black contrast.

[ATMOSPHERE]
Very low ground mist drifting slowly leftward at ankle height only,
visible in torch spill zones.

[STYLE]
Cinematic live-action film still. Shot on 35mm anamorphic film.
Photographic — not illustrated, not rendered, not drawn.
Natural film grain, ISO 3200. Slight lens imperfection.
Limestone: rough-hewn, cold to touch, chisel marks visible.
Robes: coarse linen weave, folds catching amber light naturally.
Skin: real human skin — pores, subtle texture, not smoothed.
Deep amber-to-black colour grade. No digital post-processing look.

[CONSTRAINTS]
Seeker hair: deep crimson-red, medium length, wavy — identical across all 5 seconds.
Blue teardrop hair clip visible near crown throughout.
Both figures: position and proportions locked — no drift, no morph.
Archway geometry and torch positions: fixed throughout.

[NEGATIVE]
No 3D render. No CGI. No digital art. No anime. No cartoon.
No game engine lighting. No Unreal Engine look. No plastic textures.
No smooth AI skin. No artificial smoothness on any surface.
No camera movement. No zoom. No figure movement.
No supernatural glow. No blue-violet tones. No extra figures.
No text overlay. No modern objects."""

def hf_req(path, method="POST", body=None, timeout=30, raw_url=None):
    url = raw_url or (path if path.startswith("http") else f"{BASE}/{path.lstrip('/')}")
    h   = {"Authorization": AUTH, "User-Agent": UA, "Accept": "application/json"}
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

# ─── Step 1: Upload seed frame ───────────────────────────────────────────────
print("[1/3] Requesting upload URL from Higgsfield CDN…")
code, text = hf_req("/files/generate-upload-url", body={"content_type": "image/png"})
print(f"      → {code}: {text[:200]}")
if code != 200:
    raise SystemExit(f"FAIL: upload-url: {text}")

info       = json.loads(text)
public_url = info["public_url"]
upload_url = info["upload_url"]
print(f"      CDN url: {public_url[:80]}…")

print("[1/3] PUT seed frame…")
put_req = urllib.request.Request(
    upload_url, data=SEED.read_bytes(),
    headers={"Content-Type": "image/png"}, method="PUT"
)
try:
    with urllib.request.urlopen(put_req, timeout=60) as r:
        print(f"      PUT {r.status} OK")
except urllib.error.HTTPError as e:
    raise SystemExit(f"FAIL: PUT {e.code}: {e.read().decode()[:200]}")

# ─── Step 2: Submit Kling I2V ────────────────────────────────────────────────
print("\n[2/3] Submitting Kling I2V (3s, 1080p)…")

# Probe argument schema — Kling may need slightly different field names
candidate_payloads = [
    # Attempt 1: confirmed schema — type="image_url", duration 5 or 10
    {
        "prompt":       PROMPT_3S,
        "input_image":  {"type": "image_url", "image_url": public_url},
        "duration":     5,
        "resolution":   "1080",
        "aspect_ratio": "9:16",
    },
    # Attempt 2: drop resolution/aspect
    {
        "prompt":       PROMPT_3S,
        "input_image":  {"type": "image_url", "image_url": public_url},
        "duration":     5,
    },
    # Attempt 3: bare minimum
    {
        "prompt":       PROMPT_3S,
        "input_image":  {"type": "image_url", "image_url": public_url},
    },
]

request_id = None
status_url = None
for i, payload in enumerate(candidate_payloads):
    code, text = hf_req("/kling", body=payload)
    print(f"      attempt {i+1}: {code} — {text[:200]}")
    if code in (200, 201, 202):
        data       = json.loads(text)
        request_id = data.get("request_id")
        status_url = data.get("status_url")
        print(f"      request_id: {request_id}")
        print(f"      status_url: {status_url}")
        break
    if code == 403:
        raise SystemExit("FAIL: 403 Not enough credits — add credit at platform.higgsfield.ai/billing")

if not request_id:
    raise SystemExit(f"FAIL: could not submit Kling job. Last response: {text[:300]}")

# ─── Step 3: Poll until done ─────────────────────────────────────────────────
print(f"\n[3/3] Polling status (request_id={request_id})…")
deadline = time.time() + 300   # 5 min max
dot       = 0
while time.time() < deadline:
    code, text = hf_req(status_url, raw_url=status_url, method="GET") if status_url.startswith("http") \
                 else hf_req(f"/requests/{request_id}/status", method="GET")
    try:
        data   = json.loads(text)
        status = data.get("status", "?")
    except Exception:
        status = text[:60]

    dot += 1
    if dot % 6 == 0:
        print(f"      [{int(time.time() % 10000)}] status: {status}")

    if status in ("COMPLETED", "completed"):
        print("\n      ✓ COMPLETED")
        # Extract output URL
        output_url = (
            data.get("output_url") or
            data.get("video_url") or
            (data.get("video") or {}).get("url") or
            (data.get("outputs") or [{}])[0].get("url") or
            data.get("result", {}).get("url")
        )
        if output_url:
            print(f"      output: {output_url[:100]}")
            out_path = OUT / "shot1_kling_masterpiece.mp4"
            print(f"      downloading → {out_path}")
            urllib.request.urlretrieve(output_url, out_path)
            size = out_path.stat().st_size
            print(f"\nSHIP: {out_path} ({size/1024:.0f} KB)")
        else:
            print(f"      response: {json.dumps(data, indent=2)[:600]}")
        break

    elif status in ("FAILED", "failed", "NSFW", "CANCELED", "cancelled"):
        print(f"\nFAIL: {status} — {json.dumps(data, indent=2)[:400]}")
        break

    time.sleep(5)
else:
    print("\nTIMEOUT: 5 min exceeded — check status manually")
    print(f"status_url: {status_url}")
