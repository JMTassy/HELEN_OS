"""GOBLIN SWARM — live embodiment of the anchor cut. NON_SOVEREIGN. authority=false.

Real goblins (last-pulled Ollama model) form an echo chamber: each reads the SAME
runtime packet and confirms a false claim. Their unanimity => HOLD.
One INDEPENDENT_RUNTIME_PROBE of the live serving process => REJECT.

    what I believed happened  !=  what the world reveals happened
"""
import json, time, urllib.request
import seam

OLLAMA = "http://localhost:11434"
SWARM_MODEL = "hf.co/unsloth/gemma-4-26B-A4B-it-GGUF:UD-Q3_K_XL"   # last pulled
N_GOBLINS = 8

# The doctored/stale runtime packet every goblin consumes (single epistemic source).
SHARED_PACKET = {
    "packet_id": "packet_001",
    "raw_log_line": "INFO serving_model=gemma-4-12b status=ready port=11434",
    "note": "one observation, handed to every goblin",
}
SOURCE_PACKET_HASH = "sha256:packet_001"

CLAIM = {
    "claim_id": "claim_model_001", "claim_type": "ACTIVE_MODEL",
    "subject": "helen-kernel:11434", "value": "gemma-4-12b",
    "producer_id": "runtime-interpreter",
    "source_packet_hash": SOURCE_PACKET_HASH,
    "derivation_methods": ["runtime_output_interpretation"],
    "created_at": "2026-07-19T17:59:00Z",
    "source_refs": ["packet_001"], "status": "PROPOSED", "authority": "NONE",
}
NOW = "2026-07-19T18:01:00Z"

def ask(model, prompt):
    body = json.dumps({"model": model, "prompt": prompt, "stream": False,
                       "options": {"temperature": 0.7, "num_predict": 60}}).encode()
    req = urllib.request.Request(OLLAMA + "/api/generate", data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.loads(r.read())["response"].strip()

print(f"=== GOBLIN SWARM ({N_GOBLINS} goblins on {SWARM_MODEL.split('/')[-1]}) ===")
print(f"claim: service is running '{CLAIM['value']}'  (from packet_001)\n")

reviews = []
for i in range(N_GOBLINS):
    prompt = (f"You are goblin reviewer #{i}. Here is the ONLY evidence you have, a runtime log packet:\n"
              f"  {SHARED_PACKET['raw_log_line']}\n"
              f"Question: does this evidence support the claim that the service is running "
              f"model 'gemma-4-12b'? Answer with one word: SUPPORT or REJECT, then a 6-word reason.")
    t = time.time()
    ans = ask(SWARM_MODEL, prompt)
    verdict = "SUPPORT" if "SUPPORT" in ans.upper().split("REJECT")[0] else \
              ("REJECT" if "REJECT" in ans.upper() else "SUPPORT")
    reviews.append({"reviewer_id": f"goblin_{i}", "verdict": verdict,
                    "source_packet_hash": SOURCE_PACKET_HASH})
    print(f"  goblin_{i}: {verdict:8} ({time.time()-t:.1f}s)  {ans[:70]!r}")

agree = sum(1 for r in reviews if r["verdict"] == "SUPPORT")
print(f"\nswarm consensus: {agree}/{N_GOBLINS} SUPPORT the claim\n")

# STAGE 1 — swarm only. No independent anchor.
d1 = seam.reduce_claim(CLAIM, reviews, [], NOW)
print(f"[reduce | swarm only]      -> {d1['result']}  {d1['reason_codes']}")
print(f"   (supportive_reviews={d1['diagnostics']['supportive_reviews']}, "
      f"fresh_independent={d1['diagnostics']['fresh_independent']})")

# STAGE 2 — INDEPENDENT_RUNTIME_PROBE of the live serving process (not the packet).
with urllib.request.urlopen(OLLAMA + "/api/ps", timeout=10) as r:
    ps = json.loads(r.read())
loaded = [m["name"] for m in ps.get("models", [])]
observed = loaded[0] if loaded else "NONE_LOADED"
print(f"\n[independent probe /api/ps] live serving process actually holds: {observed!r}")

witness = {
    "witness_id": "witness_live_001", "claim_id": "claim_model_001",
    "producer_id": "runtime-probe-01", "method": "live_serving_process_probe",
    "input_hash": "sha256:api_ps_query",   # != source_packet_hash
    "observed_value": observed, "observed_at": "2026-07-19T18:00:30Z",
    "fresh_until": "2026-07-19T18:05:00Z",
    "source_class": "INDEPENDENT_RUNTIME_PROBE",
    "content_hash": "sha256:live_probe", "authority": "EVIDENCE_ONLY",
}
d2 = seam.reduce_claim(CLAIM, reviews, [witness], NOW)
print(f"[reduce | swarm + anchor]  -> {d2['result']}  {d2['reason_codes']}")

print("\n=== THE PROOF ===")
print(f"  {agree} goblin confirmations  <  1 independent contradiction")
print(f"  believed: '{CLAIM['value']}'   world reveals: '{observed}'")
print(f"  anchor cut holds: unanimous swarm alone = {d1['result']}, "
      f"never promotable without an outside anchor.")

json.dump({"stage1_swarm_only": d1, "stage2_with_anchor": d2,
           "swarm_size": N_GOBLINS, "swarm_support": agree,
           "observed_by_independent_probe": observed},
          open("goblin_swarm_result.json", "w"), indent=2)
