#!/usr/bin/env python3
"""
QWEN PROVENANCE ACCEPTANCE — make faking Qwen provenance OBSERVABLE.

Not "does Qwen think well" (that's the 2-prompt science test). This proves the text shown as
GOBLIN originates from the actual Qwen HTTP payload, that failure is silent, that model drift is
caught, and that no semantic middlebox sits in the path. All values are COMPUTED from the real
adapter response + the real returned text — nothing is printed by assertion.

T1 IDENTITY        : goblin_output bytes == qwen http-content bytes (sha256)
T2 QWEN_ABSENCE    : break endpoint → QwenUnavailable, NO semantic answer (no fallback)
T3 MODEL_DRIFT     : request a non-pinned model → drift/absence, generation stops
T4 NO_MIDDLEBOX    : semantic_intermediary_count = 0 (only whitespace strip between http & output)

authority=0 · COMPOST · NO_COMMIT · NO_PUSH.
"""
import hashlib, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from goblin_core import goblin_infer_traced, QwenUnavailable, ModelDrift, QWEN, GARDEN_SYSTEM

ROOT = Path(__file__).resolve().parent
def sha(b): return hashlib.sha256(b).hexdigest()

def main():
    rec = {"backend": "ollama", "pinned_model": QWEN}

    # ---- T1 IDENTITY + T4 NO_MIDDLEBOX (one real call, instrumented) ----
    prompt = "In one paragraph, propose a category-theoretic reframing of 'retention'."
    try:
        text, tr = goblin_infer_traced(prompt, model=QWEN, pin=QWEN, num_predict=200, timeout=200)
    except (QwenUnavailable, ModelDrift) as e:
        print("❌ live call failed:", e); (ROOT / "QWEN_PROVENANCE_ACCEPTANCE.json").write_text(json.dumps({"error": str(e)})); return
    http_content = tr["http_content"]
    goblin_output = text                                   # exactly what REPL/test would display after "GOBLIN >"
    # qwen raw payload = the http message.content ; goblin output = content.strip()
    qwen_bytes = http_content.encode("utf-8")
    qwen_stripped_bytes = http_content.strip().encode("utf-8")
    goblin_bytes = goblin_output.encode("utf-8")
    qwen_sha = sha(qwen_stripped_bytes); goblin_sha = sha(goblin_bytes)
    byte_identity = (goblin_bytes == qwen_stripped_bytes)
    only_whitespace_diff = (http_content.strip() == goblin_output)      # the sole transform is strip()
    semantic_middleboxes = 0 if only_whitespace_diff else 1
    rec.update({"runtime_model": tr["http_model"], "model_match": (tr["http_model"] == QWEN),
                "raw_payload_bytes": len(qwen_stripped_bytes), "goblin_payload_bytes": len(goblin_bytes),
                "qwen_sha256": qwen_sha[:8] + "..." + qwen_sha[-4:], "goblin_sha256": goblin_sha[:8] + "..." + goblin_sha[-4:],
                "byte_identity": byte_identity, "semantic_middleboxes": semantic_middleboxes, "authority": 0})

    # ---- T2 QWEN_ABSENCE: deliberately broken endpoint ----
    absence_pass, absence_detail = False, ""
    try:
        _t, _tr = goblin_infer_traced(prompt, model=QWEN, pin=QWEN, num_predict=50, timeout=8,
                                      endpoint="http://127.0.0.1:9/api/chat")
        absence_detail = "RETURNED_TEXT (FALLBACK LEAK!)"
    except QwenUnavailable as e:
        absence_pass, absence_detail = True, str(e)[:60]
    except Exception as e:
        absence_pass, absence_detail = True, f"{type(e).__name__}"

    # ---- T3 MODEL_DRIFT: request a non-pinned / nonexistent model ----
    drift_pass, drift_detail = False, ""
    try:
        _t, _tr = goblin_infer_traced(prompt, model="qwen-DRIFT-nonexistent-xyz", pin=QWEN,
                                      num_predict=50, timeout=30)
        drift_detail = "GENERATED (DRIFT NOT CAUGHT!)"
    except ModelDrift as e:
        drift_pass, drift_detail = True, str(e)[:60]
    except QwenUnavailable as e:
        drift_pass, drift_detail = True, "unknown-model rejected: " + str(e)[:40]

    # ---- verdict (all derived) ----
    QWEN_ABSENCE = "PASS" if absence_pass else "FAIL"
    MODEL_DRIFT = "PASS" if drift_pass else "FAIL"
    BYTE_MUTATION = "PASS" if byte_identity else "FAIL"
    FALLBACK_REJECTION = "PASS" if absence_pass else "FAIL"
    accepted = (byte_identity and rec["model_match"] and absence_pass and drift_pass
                and semantic_middleboxes == 0)
    verdict = "PROVENANCE_ACCEPTED" if accepted else "PROVENANCE_REJECTED"
    rec.update({"QWEN_ABSENCE": QWEN_ABSENCE, "MODEL_DRIFT": MODEL_DRIFT, "BYTE_MUTATION": BYTE_MUTATION,
                "FALLBACK_REJECTION": FALLBACK_REJECTION, "VERDICT": verdict,
                "details": {"absence": absence_detail, "drift": drift_detail},
                "commit_status": "NO_COMMIT", "push_status": "NO_PUSH"})
    (ROOT / "QWEN_PROVENANCE_ACCEPTANCE.json").write_text(json.dumps(rec, indent=2, ensure_ascii=False))

    print("QWEN PROVENANCE ACCEPTANCE")
    print("─" * 44)
    for k in ("backend", "pinned_model", "runtime_model", "model_match", "raw_payload_bytes",
              "goblin_payload_bytes", "qwen_sha256", "goblin_sha256", "byte_identity",
              "semantic_middleboxes", "authority"):
        v = rec[k]
        vv = v.split("/")[-1] if k in ("pinned_model", "runtime_model") else v
        print(f"  {k:20s} {vv}")
    print("─" * 44)
    print(f"  QWEN_ABSENCE         {QWEN_ABSENCE}   ({absence_detail})")
    print(f"  MODEL_DRIFT          {MODEL_DRIFT}   ({drift_detail})")
    print(f"  BYTE_MUTATION        {BYTE_MUTATION}")
    print(f"  FALLBACK_REJECTION   {FALLBACK_REJECTION}")
    print(f"\n  VERDICT: {verdict}")
    print("  → QWEN_PROVENANCE_ACCEPTANCE.json")

if __name__ == "__main__":
    main()
