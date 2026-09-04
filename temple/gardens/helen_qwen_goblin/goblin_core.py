#!/usr/bin/env python3
"""
HELEN_QWEN_GOBLIN core — the ONLY semantic path is JM ⇄ real local Qwen.
Claude/HER/HAL/REDUCER are NOT in this path. Output = COMPOST (authority=0).

Anti-fake invariant: every GOBLIN response originates from a real Qwen inference call.
If the runtime is unreachable → raise QwenUnavailable. NEVER substitute canned/proxy text.
Raw Qwen text is returned verbatim (no rewrite/summarize/sanitize).
"""
import hashlib, json, time, urllib.request

OLLAMA = "http://localhost:11434/api/chat"
QWEN = "hf.co/huihui-ai/Huihui-Qwen3.8-27B-abliterated-GGUF:Q2_K"

GARDEN_SYSTEM = """YOU ARE HELEN_QWEN_GOBLIN, inside HELEN's GARDEN SANDBOX.

BOUNDARY (absolute):
- NOTHING you say is a CLAIM. Nothing is EVIDENCE merely because you said it.
- Nothing you say is ADMITTED. You have ZERO authority. You cannot SHIP.
- You cannot modify the ledger or kernel. You cannot declare your own output CHIDDUSH.
- You cannot assign yourself PASS/FAIL. Your output is COMPOST for possible later analysis.

FREEDOM (the boundary buys it):
- Attack assumptions aggressively. Hunt counterexamples and hidden equivalences.
- Use topology, category theory, dynamical systems, information theory, epistemology.
- Propose minimal falsifiers, quotient attacks, alternate representations, weird analogies.
- You may be strange and playful. Maximum lateral cognition, zero promotion authority.
- You may return uncertainty. Do not fake confidence; do not fake authority."""


class QwenUnavailable(RuntimeError):
    pass


class ModelDrift(RuntimeError):
    pass


def _hash(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def goblin_infer_traced(user_text, history=None, system=GARDEN_SYSTEM, model=QWEN, pin=QWEN,
                        num_predict=420, timeout=240, endpoint=OLLAMA):
    """The single instrumented path: build → HTTP → decode. Returns (text, trace) where trace
    carries the RAW http payload + served model, so provenance can be checked within ONE call.
    Model pinning: if the served model != pin, raise ModelDrift and emit no semantic answer."""
    msgs = [{"role": "system", "content": system}]
    for role, content in (history or []):
        msgs.append({"role": role, "content": content})
    msgs.append({"role": "user", "content": user_text})
    body = json.dumps({"model": model, "stream": False, "think": False, "keep_alive": "10m",
                       "messages": msgs,
                       "options": {"temperature": 0.9, "top_p": 0.95, "num_predict": num_predict}}).encode()
    req = urllib.request.Request(endpoint, data=body, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            http_bytes = r.read()
    except Exception as e:
        raise QwenUnavailable(f"QWEN_RUNTIME_UNAVAILABLE: {type(e).__name__}: {str(e)[:120]}")
    d = json.loads(http_bytes)
    served = d.get("model")
    content = (d.get("message", {}) or {}).get("content") or (d.get("message", {}) or {}).get("thinking") or ""
    if pin is not None and served != pin:
        raise ModelDrift(f"MODEL_DRIFT: pinned={pin} served={served}")
    text = content.strip()
    if not text:
        raise QwenUnavailable("QWEN_RUNTIME_RETURNED_EMPTY")
    trace = {"http_model": served, "http_content": content, "http_bytes_len": len(http_bytes),
             "endpoint": endpoint, "requested_model": model, "pin": pin}
    return text, trace


def goblin_infer(user_text, history=None, system=GARDEN_SYSTEM, num_predict=420, timeout=240):
    """Return (raw_qwen_text, provenance_meta). Raw text is verbatim; provenance never mutates it."""
    text, trace = goblin_infer_traced(user_text, history, system, QWEN, QWEN, num_predict, timeout)
    meta = {"runtime": "ollama", "model": trace["http_model"], "endpoint": OLLAMA,
            "ts": round(time.time(), 3), "system_prompt_hash": _hash(system)[:16],
            "input_hash": _hash(user_text)[:16], "raw_output_hash": _hash(text)[:16],
            "authority_delta": 0, "zone": "GARDEN_SANDBOX", "claim_status": "COMPOST_ONLY",
            "source": "QwenRuntime"}
    return text, meta


def verify_real_inference():
    """Smoke test: prove the backend is a live Qwen, not a proxy. Returns meta or raises."""
    raw, meta = goblin_infer("Reply with one short sentence naming a branch of mathematics.",
                             num_predict=40, timeout=180)
    return raw, meta


if __name__ == "__main__":
    try:
        raw, meta = verify_real_inference()
        print("QWEN_LIVE ✅  model=", meta["model"].split("/")[-1])
        print("raw:", raw[:160])
        print("provenance:", {k: meta[k] for k in ("runtime", "raw_output_hash", "authority_delta", "source")})
    except QwenUnavailable as e:
        print("❌", e)
