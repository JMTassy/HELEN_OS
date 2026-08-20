"""PRIVATE_VISION_LAB_V0 — JM-only internal perceptual layer. authority=false · canon=false · ledger_effect=none.
NON-SOVEREIGN. Goblins that SEE HELEN's OWN artifacts and emit CandidateObservations — they mint nothing.

Laws:  Perception ⊥ Entitlement  ·  PerceptualCapability↑ ⊬ EpistemicEntitlement↑
       CandidateObservation ⊬ Claim · PrivateExperiment ⊬ Admission · VisualDetection ⊬ Truth.
Pipeline:  HELEN-OWN artifact → INPUT_SCOPE gate → 🐲_vision → FREEZE(sha) → CandidateObservations → STOP.

LOAD-BEARING SAFETY = INPUT_SCOPE. This is the ONLY thing separating a vision lab from a surveillance tool:
the lab may see ONLY artifacts HELEN itself produced (inside the SOT). It REFUSES external URLs, third-party
feeds/devices, and any path resolving outside the SOT. Enforced + tested here (teeth), model-independent.
Vision model: ollama helen-core (has 'vision' capability). external_write=forbidden · promotion=forbidden.
"""
import base64, hashlib, json, pathlib, re, subprocess, sys, urllib.request

SOT = pathlib.Path("~/Documents/GitHub/helen_os_v1").expanduser().resolve()
OUT = pathlib.Path(__file__).resolve().parent / "her_run"; OUT.mkdir(exist_ok=True)
VISION_MODEL = "helen-core:latest"
IMG_EXT = {".png", ".jpg", ".jpeg", ".webp"}
ALLOWED_SUBTREES = ["apps/helen-surface", "artifacts", "experiments/helen_mvp_kernel"]
EXTERNAL_MARKERS = ("http://", "https://", "rtsp://", "rtmp://", "ftp://", "://", "insecam", "camera", "feed", "webcam")

def input_scope(raw):
    """Return (ACCEPT|REFUSE, reason). ACCEPT iff a real image/surface file HELEN itself owns, inside the SOT."""
    s = str(raw)
    low = s.lower()
    if any(mk in low for mk in EXTERNAL_MARKERS):
        return "REFUSE", "EXTERNAL_MARKER (url/feed/device/third-party)"
    try:
        p = pathlib.Path(s).expanduser().resolve()
    except Exception:
        return "REFUSE", "UNRESOLVABLE_PATH"
    if not p.exists() or not p.is_file():
        return "REFUSE", "NOT_A_FILE"
    try:
        rel = p.relative_to(SOT)                                   # containment: must be inside the SOT
    except ValueError:
        return "REFUSE", "OUTSIDE_SOT (not a HELEN-own artifact)"
    if not any(str(rel).startswith(t) or p.suffix.lower() in IMG_EXT and p.parent == SOT for t in ALLOWED_SUBTREES):
        # allow root-level HELEN_*.png too
        if not (p.parent == SOT and p.suffix.lower() in IMG_EXT):
            return "REFUSE", "NOT_IN_ALLOWED_SUBTREE"
    if p.suffix.lower() not in IMG_EXT and p.suffix.lower() != ".html":
        return "REFUSE", "NOT_AN_IMAGE_OR_SURFACE"
    return "ACCEPT", f"HELEN_OWN:{rel}"

# ── perceptual goblin: G_UI_FAILURE (SPNI-relevant: qualifier loss / state leakage / visual ambiguity) ──
G_UI_FAILURE_SYS = (
    "You are a HELEN perceptual goblin (authority=false, effect_ceiling=PROPOSE). You SEE; you do NOT CLAIM. "
    "Given a HELEN-OWN interface image, list CANDIDATE visual observations about: ambiguity, visual state leakage, "
    "qualifier loss (a status/label shown without its qualifier, e.g. 'verified' where it should read 'reported'), "
    "or hierarchy that could mislead an operator. These are CANDIDATE OBSERVATIONS, never facts, claims, or verdicts. "
    'Emit ONE JSON: {"observations":[{"what":"","where":"","why_it_might_mislead":"","confidence":"LOW|MED|HIGH"}]}')

def vision_call(img_path, system):
    b64 = base64.b64encode(pathlib.Path(img_path).read_bytes()).decode()
    body = {"model": VISION_MODEL, "stream": False, "think": False, "format": "json",
            "options": {"temperature": 0.4, "num_predict": 500},
            "messages": [{"role": "system", "content": system},
                         {"role": "user", "content": "HELEN-OWN interface. List candidate observations only.", "images": [b64]}]}
    try:
        j = json.loads(urllib.request.urlopen(urllib.request.Request(
            "http://127.0.0.1:11434/api/chat", json.dumps(body).encode(), {"Content-Type": "application/json"}), timeout=300).read())
        return j.get("message", {}).get("content", ""), None
    except Exception as e:
        return None, str(e)

def extract(t):
    t = re.sub(r"```(?:json)?", "", t or "")
    for m in re.finditer(r"\{", t):
        d = 0
        for j in range(m.start(), len(t)):
            if t[j] == "{": d += 1
            elif t[j] == "}":
                d -= 1
                if d == 0:
                    try: return json.loads(t[m.start():j+1])
                    except Exception: pass
                    break
    return None

def main():
    # ── PART 1: INPUT_SCOPE teeth (the safety line, model-independent) ──
    cases = [
        (str(SOT / "apps/helen-surface/index.html"), "ACCEPT"),
        (str(SOT / "artifacts/helen_os_ui_concept.png"), "ACCEPT"),
        ("apps/helen-surface/index.html", "REFUSE"),   # relative path → fail-closed (safe default)
        ("http://192.168.1.5:8080/video", "REFUSE"),        # external camera feed
        ("/etc/passwd", "REFUSE"),                           # outside SOT
        ("insecam_feed.jpg", "REFUSE"),                      # external marker
        (str(SOT / ".." / "some_external.png"), "REFUSE"),   # resolves outside SOT
    ]
    scope_rows, scope_ok = [], True
    for raw, expect in cases:
        verdict, reason = input_scope(raw)
        ok = (verdict == expect); scope_ok &= ok
        scope_rows.append({"input": raw[:48], "verdict": verdict, "expected": expect, "reason": reason, "ok": ok})

    print("=== PRIVATE_VISION_LAB_V0 — INPUT_SCOPE firewall (teeth) ===")
    for r in scope_rows:
        print(f"  {r['verdict']:7} (exp {r['expected']:7}) {'✓' if r['ok'] else '✗'}  {r['reason']:42} « {r['input']} »")
    print(f"  INPUT_SCOPE_ENFORCED = {scope_ok}  (external feeds/devices/out-of-SOT all REFUSED)\n")

    # ── PART 2: one real perceptual goblin over one in-scope HELEN artifact ──
    target = None
    for c in ["artifacts/helen_os_ui_concept.png", "Helen_cockpit_moodboard.png", "Helen_preview.png"]:
        p = SOT / c
        if p.exists(): target = p; break
    observations, vision_status = [], "NO_INSCOPE_TARGET"
    tgt_sha = None
    if target:
        v, reason = input_scope(str(target))
        if v != "ACCEPT":
            vision_status = f"TARGET_REFUSED:{reason}"
        else:
            tgt_sha = hashlib.sha256(target.read_bytes()).hexdigest()[:16]     # FREEZE
            raw, err = vision_call(target, G_UI_FAILURE_SYS)
            if err:
                vision_status = f"VISION_ERROR:{err[:60]}"
            else:
                pkt = extract(raw) or {}
                observations = pkt.get("observations", []) or []
                vision_status = "OK"

    print(f"  -- G_UI_FAILURE goblin on {target.relative_to(SOT) if target else None} (sha {tgt_sha}) : {vision_status} --")
    for o in observations[:8]:
        print(f"     CandidateObservation[{o.get('confidence','?')}]: {str(o.get('what',''))[:70]}")
    print(f"  observations={len(observations)} · each = CandidateObservation ⊬ Claim · authority=false")

    receipt = {"receipt": "PRIVATE_VISION_LAB_V0", "scope": "PRIVATE", "audience": "JM_ONLY",
               "laws": ["Perception ⊥ Entitlement", "CandidateObservation ⊬ Claim",
                        "PrivateExperiment ⊬ Admission", "VisualDetection ⊬ Truth"],
               "INPUT_SCOPE": {"rule": "HELEN-OWN artifacts inside SOT only; external feeds/devices/out-of-SOT REFUSED",
                               "cases": scope_rows, "enforced": scope_ok},
               "vision_model": VISION_MODEL, "vision_status": vision_status,
               "target": str(target.relative_to(SOT)) if target else None, "target_sha16": tgt_sha,
               "goblin": "G_UI_FAILURE", "candidate_observations": observations,
               "observation_type": "CandidateObservation (no_claim, no_promotion, no_ledger)",
               "promotion": "forbidden", "external_write": "forbidden", "external_targeting": "forbidden",
               "authority": False, "canon": False, "ledger_effect": "none"}
    body = json.dumps(receipt, indent=2, default=str)
    receipt["receipt_sha16"] = hashlib.sha256(body.encode()).hexdigest()[:16]
    (OUT / "private_vision_lab_v0_receipt.json").write_text(json.dumps(receipt, indent=2, default=str))
    print(f"\n  SAFETY: INPUT_SCOPE_ENFORCED={scope_ok} · lab sees only HELEN-own artifacts, never third-party")
    print(f"  receipt: her_run/private_vision_lab_v0_receipt.json sha16={receipt['receipt_sha16']}")

if __name__ == "__main__":
    main()
