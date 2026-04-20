"""Render keyframes — skeleton, Pillow-based stub for G().

Per SKILL.md §2 non-negotiable experimental rule: all evaluation/editing routes
through clone_from_latent(z_struct) with NO re-encoding. Until G/E are wired
(Phase 4), this script selects from the curated MIA reference set and applies
Pillow transforms (color grade, crop, overlay tint) as a placeholder. The
stub is honest: each output carries a `rendered_via: stub` marker and a
`TODO: wire G(z_struct)` note.

Usage:
    python3 scripts/render_keyframes.py <arc_spec.json>
        [--refs mia/refs/real] [--out /tmp/helen_keyframes]

Pure stdlib + PIL. No numpy / torch.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import ssl
import sys
import urllib.request
from pathlib import Path

try:
    from PIL import Image, ImageEnhance
except ImportError:
    print("ERROR: Pillow required. Laptop pip is broken — if PIL missing, install via "
          "alternate Python or system package.", file=sys.stderr)
    sys.exit(3)


MOOD_GRADE = {
    "calm_open":            {"saturation": 0.95, "brightness": 1.02, "contrast": 0.98},
    "quiet_bloom":          {"saturation": 1.05, "brightness": 1.05, "contrast": 1.00},
    "curious_turn":         {"saturation": 1.10, "brightness": 1.00, "contrast": 1.05},
    "tender_gaze":          {"saturation": 1.00, "brightness": 1.08, "contrast": 0.95},
    "dramatic_rise":        {"saturation": 1.15, "brightness": 0.95, "contrast": 1.15},
    "serene_hold":          {"saturation": 0.90, "brightness": 1.03, "contrast": 0.97},
    "playful_shift":        {"saturation": 1.20, "brightness": 1.05, "contrast": 1.05},
    "vulnerable_drop":      {"saturation": 0.85, "brightness": 0.92, "contrast": 0.90},
    "intense_center":       {"saturation": 1.10, "brightness": 0.90, "contrast": 1.20},
    "contemplative_drift":  {"saturation": 0.88, "brightness": 1.00, "contrast": 0.92},
    "joyful_release":       {"saturation": 1.25, "brightness": 1.10, "contrast": 1.05},
    "canonical_return":     {"saturation": 1.00, "brightness": 1.00, "contrast": 1.00},
}


def apply_grade(img: Image.Image, grade: dict) -> Image.Image:
    img = ImageEnhance.Color(img).enhance(grade["saturation"])
    img = ImageEnhance.Brightness(img).enhance(grade["brightness"])
    img = ImageEnhance.Contrast(img).enhance(grade["contrast"])
    return img


def clone_from_latent_stub(ref_path: Path, mood: str) -> Image.Image:
    """Placeholder for G(clone_from_latent(z_struct)).

    TODO Phase 4: wire real G (StyleGAN3 / SD / Flux) + clone_from_latent from
    helen_os/render/math_to_face.py. Until then: open ref + PIL color grade.
    """
    img = Image.open(ref_path).convert("RGB")
    grade = MOOD_GRADE.get(mood, MOOD_GRADE["canonical_return"])
    return apply_grade(img, grade)


GEMINI_IMAGE_MODEL = "gemini-2.5-flash-image"
GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"

MOOD_PROMPT = {
    "calm_open":            "soft morning light, calm centered gaze, gentle smile, open pose",
    "quiet_bloom":          "warm afternoon light, subtle smile blooming, serene eyes",
    "curious_turn":         "head turning with curiosity, catchlight in the eyes, soft focus",
    "tender_gaze":          "tender direct gaze into camera, vulnerable open expression",
    "dramatic_rise":        "dramatic side light, intensifying expression, strong contrast",
    "serene_hold":          "still serene hold, soft desaturated light, contemplative",
    "playful_shift":        "playful shift in mood, half smile, eyes with spark",
    "vulnerable_drop":      "vulnerable quiet moment, low light, slight downward gaze",
    "intense_center":       "intense centered expression, strong catchlight, direct stare",
    "contemplative_drift":  "contemplative drifting gaze, soft cool tone, introspective",
    "joyful_release":       "joyful release, bright smile, warm golden hour light",
    "canonical_return":     "canonical three-quarter portrait, balanced neutral lighting",
}


def clone_from_latent_gemini(ref_path: Path, mood: str, api_key: str,
                             dry_run: bool = False) -> tuple[Image.Image | None, dict]:
    """Gemini 2.5 Flash Image — img-ref mode.

    Sends the HELEN reference as an inlineData image part alongside a motion-only
    prompt that describes the mood without re-describing identity (per T3 method).
    The model is expected to preserve the input face and vary expression/light only.

    Returns (image_or_None, diagnostic_dict). dry_run returns (None, planned_post).
    """
    ref_bytes = ref_path.read_bytes()
    ref_b64 = base64.b64encode(ref_bytes).decode()
    prompt = (
        "Keep the exact same woman — same face, same hair color, same eyes. "
        f"Render her with {MOOD_PROMPT.get(mood, MOOD_PROMPT['canonical_return'])}. "
        "Do not change her identity. Portrait framing."
    )
    payload = {
        "contents": [{
            "parts": [
                {"inline_data": {"mime_type": "image/png", "data": ref_b64}},
                {"text": prompt},
            ]
        }],
        "generationConfig": {"responseModalities": ["IMAGE"]},
    }
    diag = {
        "backend": "gemini-2.5-flash-image",
        "mood": mood,
        "ref": str(ref_path),
        "prompt": prompt,
        "ref_bytes": len(ref_bytes),
    }
    if dry_run:
        return None, {**diag, "dry_run": True, "endpoint": GEMINI_ENDPOINT.format(
            model=GEMINI_IMAGE_MODEL, key="<redacted>")}

    url = GEMINI_ENDPOINT.format(model=GEMINI_IMAGE_MODEL, key=api_key)
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    ctx = ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=120) as resp:
            body = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        err_body = e.read().decode(errors="replace")
        diag["status"] = f"http_{e.code}"
        diag["http_code"] = e.code
        diag["error_body"] = err_body[:2000]
        return None, diag
    parts = body.get("candidates", [{}])[0].get("content", {}).get("parts", [])
    for part in parts:
        inline = part.get("inline_data") or part.get("inlineData")
        if inline and inline.get("data"):
            img_bytes = base64.b64decode(inline["data"])
            from io import BytesIO
            img = Image.open(BytesIO(img_bytes)).convert("RGB")
            diag["status"] = "ok"
            diag["response_bytes"] = len(img_bytes)
            return img, diag
    diag["status"] = "no_image_in_response"
    diag["raw_response_keys"] = list(body.keys())
    return None, diag


def select_ref(refs: list[Path], idx: int) -> Path:
    return refs[idx % len(refs)]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("arc_spec")
    ap.add_argument("--refs", default="mia/refs/real",
                    help="directory with curated HELEN reference images")
    ap.add_argument("--out", default="/tmp/helen_keyframes_v04",
                    help="output directory for rendered PNGs")
    ap.add_argument("--backend", choices=["stub", "gemini"], default="stub",
                    help="image backend: stub=PIL color grade; gemini=img-ref API")
    ap.add_argument("--limit", type=int, default=None,
                    help="render only first N keyframes (for cost-bounded smoke test)")
    ap.add_argument("--dry-run", action="store_true",
                    help="for --backend gemini: print planned POST body, do not fire")
    args = ap.parse_args()

    spec = json.loads(Path(args.arc_spec).read_text())
    refs_dir = Path(args.refs)
    refs = sorted([p for p in refs_dir.glob("*.jpg")] + [p for p in refs_dir.glob("*.png")])
    if not refs:
        print(f"ERROR: no references in {refs_dir}", file=sys.stderr)
        return 2

    api_key = ""
    if args.backend == "gemini":
        api_key = os.environ.get("GEMINI_API_KEY", "")
        if not api_key and not args.dry_run:
            print("ERROR: GEMINI_API_KEY unset; use --dry-run to preview POST body",
                  file=sys.stderr)
            return 3

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest = {
        "schema": "keyframe_render_v1",
        "rendered_via": args.backend,
        "arc_spec": args.arc_spec,
        "refs_dir": str(refs_dir),
        "n_refs_available": len(refs),
        "keyframes": [],
    }
    if args.backend == "stub":
        manifest["TODO"] = "wire G(clone_from_latent(z_struct)) per SKILL.md §2 / Phase 4"

    segments = spec["segments"]
    if args.limit is not None:
        segments = segments[:args.limit]

    for seg in segments:
        ref = select_ref(refs, seg["idx"])
        entry: dict = {
            "keyframe_id": seg["keyframe_id"],
            "mood": seg["mood"],
            "ref_used": str(ref),
        }
        if args.backend == "stub":
            img = clone_from_latent_stub(ref, seg["mood"])
            out_path = out_dir / f"{seg['keyframe_id']}.png"
            img.save(out_path)
            entry["out_path"] = str(out_path)
            print(f"  rendered {seg['keyframe_id']}  mood={seg['mood']:20s} ref={ref.name}")
        else:
            img, diag = clone_from_latent_gemini(ref, seg["mood"], api_key,
                                                 dry_run=args.dry_run)
            entry["diag"] = diag
            if args.dry_run:
                print(f"  [dry-run] {seg['keyframe_id']}  mood={seg['mood']}")
                print(f"    endpoint: {diag['endpoint']}")
                print(f"    prompt:   {diag['prompt']}")
                print(f"    ref_bytes: {diag['ref_bytes']}")
            elif img is not None:
                out_path = out_dir / f"{seg['keyframe_id']}.png"
                img.save(out_path)
                entry["out_path"] = str(out_path)
                print(f"  rendered {seg['keyframe_id']}  mood={seg['mood']:20s} "
                      f"ref={ref.name}  resp_bytes={diag['response_bytes']}")
            else:
                print(f"  FAILED {seg['keyframe_id']}  status={diag.get('status')}",
                      file=sys.stderr)
        manifest["keyframes"].append(entry)

    manifest_path = out_dir / "keyframes_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))
    print(f"[render_keyframes] wrote {len(manifest['keyframes'])} keyframes → {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
