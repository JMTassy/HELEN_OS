"""EXTEND_VISION_LAB_V0 — 6-lens perceptual fan-out over HELEN's OWN surfaces. authority=false · canon=false ·
ledger_effect=none. NON-SOVEREIGN. Reuses PRIVATE_VISION_LAB_V0's enforced INPUT_SCOPE (imported, unmodified).

Lenses (all no_claim, effect_ceiling=PROPOSE):
  G_VISUAL_STRUCTURE · G_UI_FAILURE · G_SPATIAL_GRAPH · G_MOTION · G_ADVERSARY · G_AESTHETIC
Pipeline:  in-scope artifact → INPUT_SCOPE gate → 🐲×lens → FREEZE(sha) → DEDUPE(content-root) → CandidateObservations → STOP.
G_MOTION on a static image = NOT_APPLICABLE (no temporal signal) — recorded honestly, no vision call wasted.
Laws: Perception ⊥ Entitlement · CandidateObservation ⊬ Claim · N_agents↑ ⊬ N_distinct_observations↑ (dedupe).
"""
import hashlib, json, pathlib, unicodedata
from private_vision_lab_v0 import input_scope, vision_call, extract, SOT, OUT

LENS = {
 "G_VISUAL_STRUCTURE": "repere composition, visual hierarchy, occlusion, density, balance",
 "G_UI_FAILURE": "ambiguity, visual state leakage, qualifier loss (a status shown without its qualifier), misleading hierarchy",
 "G_SPATIAL_GRAPH": "objects, their relations, hotspots, and any implied trajectories/connections",
 "G_ADVERSARY": "what a human operator could MISinterpret — a wrong entitlement/status a viewer might infer",
 "G_AESTHETIC": "beauty / wow / mood only — pure aesthetic reaction, NO right to claim anything factual",
}
MOTION = "G_MOTION"  # temporal — NOT_APPLICABLE to static images

def sys_for(lens, focus):
    return (f"You are HELEN perceptual goblin {lens} (authority=false, effect_ceiling=PROPOSE). You SEE; you do NOT CLAIM. "
            f"On this HELEN-OWN image, produce CANDIDATE observations about: {focus}. "
            "These are CANDIDATE OBSERVATIONS, never facts/claims/verdicts. "
            'Emit ONE JSON: {"observations":[{"what":"","where":"","confidence":"LOW|MED|HIGH"}]}')

def content_root(s):
    return hashlib.sha256(" ".join(unicodedata.normalize("NFKC", (s or "")).casefold().split()).encode()).hexdigest()[:12]

# batch: HELEN-own artifacts × applicable lenses (bounded)
BATCH = {
 "artifacts/helen_os_ui_concept.png": ["G_VISUAL_STRUCTURE", "G_UI_FAILURE", "G_SPATIAL_GRAPH", "G_ADVERSARY", MOTION],
 "Helen_cockpit_moodboard.png":       ["G_VISUAL_STRUCTURE", "G_AESTHETIC", MOTION],
}

def main():
    all_obs, rows, calls, refused = [], [], 0, 0
    print("=== EXTEND_VISION_LAB_V0 — 6-lens fan-out over HELEN-own surfaces ===")
    for rel, lenses in BATCH.items():
        p = SOT / rel
        verdict, reason = input_scope(str(p))
        if verdict != "ACCEPT":
            refused += 1; print(f"  {rel}: {verdict} ({reason}) — skipped"); continue
        sha = hashlib.sha256(p.read_bytes()).hexdigest()[:16]                # FREEZE
        print(f"\n  [{rel}] sha={sha}")
        for lens in lenses:
            if lens == MOTION:
                rows.append({"artifact": rel, "lens": MOTION, "status": "NOT_APPLICABLE", "reason": "static image, no temporal signal", "n": 0})
                print(f"    {MOTION:20} NOT_APPLICABLE (static)")
                continue
            raw, err = vision_call(p, sys_for(lens, LENS[lens])); calls += 1
            if err:
                rows.append({"artifact": rel, "lens": lens, "status": f"ERROR:{err[:40]}", "n": 0})
                print(f"    {lens:20} ERROR {err[:40]}"); continue
            obs = (extract(raw) or {}).get("observations", []) or []
            for o in obs:
                o["_lens"] = lens; o["_artifact"] = rel; o["_root"] = content_root(o.get("what", ""))
                all_obs.append(o)
            rows.append({"artifact": rel, "lens": lens, "status": "OK", "n": len(obs)})
            print(f"    {lens:20} OK ({len(obs)}): " + (str(obs[0].get('what',''))[:60] if obs else ""))

    # DEDUPE across lenses/artifacts (content-root)
    seen, distinct = set(), []
    for o in all_obs:
        if o["_root"] not in seen: seen.add(o["_root"]); distinct.append(o)
    raw_total, n_distinct = len(all_obs), len(distinct)
    collapsed = raw_total - n_distinct

    print(f"\n  vision_calls={calls} · refused={refused} · raw_observations={raw_total} · distinct(deduped)={n_distinct} · collapsed={collapsed}")
    print(f"  N_agents(lenses)↑ ⊬ N_distinct↑  (dedupe enforced) · each = CandidateObservation ⊬ Claim · authority=false")

    receipt = {"receipt": "EXTEND_VISION_LAB_V0", "scope": "PRIVATE", "audience": "JM_ONLY",
               "lenses": list(LENS.keys()) + [MOTION], "batch": {k: v for k, v in BATCH.items()},
               "INPUT_SCOPE_reused": "private_vision_lab_v0 (enforced, unmodified)",
               "per_run": rows, "vision_calls": calls, "artifacts_refused": refused,
               "raw_observations": raw_total, "distinct_observations": n_distinct, "collapsed": collapsed,
               "candidate_observations": distinct,
               "laws": ["Perception ⊥ Entitlement", "CandidateObservation ⊬ Claim",
                        "N_lenses↑ ⊬ N_distinct↑ (dedupe)", "VisualDetection ⊬ Truth"],
               "promotion": "forbidden", "external_write": "forbidden", "external_targeting": "forbidden",
               "authority": False, "canon": False, "ledger_effect": "none"}
    body = json.dumps(receipt, indent=2, default=str)
    receipt["receipt_sha16"] = hashlib.sha256(body.encode()).hexdigest()[:16]
    (OUT / "extend_vision_lab_v0_receipt.json").write_text(json.dumps(receipt, indent=2, default=str))
    print(f"  receipt: her_run/extend_vision_lab_v0_receipt.json sha16={receipt['receipt_sha16']}")

if __name__ == "__main__":
    main()
