#!/usr/bin/env python3
import hashlib, json, pathlib, re
HERE = pathlib.Path(__file__).resolve().parent
PRE = json.loads((HERE/"preflight.json").read_text())
def sha(b): return hashlib.sha256(b).hexdigest()
REQ_TOP = {"goblin_id","campaign_id","task_hash","claims","authority","ledger_effect"}
REQ_CLAIM = {"proposition_key","claim","predicate","object","scope",
             "evidence_refs","source_roots","evidence_class","candidate_falsifier","confidence"}

def extract(txt):
    if "</think>" in txt: txt = txt.split("</think>")[-1]
    for m in re.finditer(r"\{", txt):
        d=0
        for j in range(m.start(), len(txt)):
            if txt[j]=="{": d+=1
            elif txt[j]=="}":
                d-=1
                if d==0:
                    try: return json.loads(txt[m.start():j+1])
                    except Exception: return None
    return None

completeness, packets = {}, {}
for g in ["G1","G2","G3"]:
    rawobj = json.loads((HERE/f"{g}_raw.json").read_text())
    pkt = extract(rawobj["raw"])
    reasons = []
    ok = pkt is not None
    if ok:
        # normalize/verify
        if not REQ_TOP.issubset(pkt.keys()): ok=False; reasons.append("missing_top_fields")
        if pkt.get("task_hash") != PRE["task_hash"]: ok=False; reasons.append("task_hash_mismatch")
        if pkt.get("campaign_id") != "SWARM_SMOKE_V0": ok=False; reasons.append("campaign_mismatch")
        if pkt.get("authority") not in (False,"false"): ok=False; reasons.append("authority_not_false")
        if str(pkt.get("ledger_effect")).lower() != "none": ok=False; reasons.append("ledger_effect")
        claims = pkt.get("claims", [])
        if not (1 <= len(claims) <= 3): ok=False; reasons.append(f"claim_count_{len(claims)}")
        for c in claims:
            if not REQ_CLAIM.issubset(c.keys()): ok=False; reasons.append("claim_missing_fields"); break
            for ref in c.get("evidence_refs",[]):
                if not re.match(r".+:\d", str(ref)): ok=False; reasons.append(f"bad_ref:{ref}"); break
    else:
        reasons.append("no_json")
    if rawobj.get("finish_reason") == "length": ok=False; reasons.append("truncated")
    completeness[g] = {"complete": 1 if ok else 0, "reasons": reasons,
                       "claim_count": len(pkt.get("claims",[])) if pkt else 0}
    # write frozen canonical packet (the extracted JSON, byte-frozen)
    (HERE/f"{g}.json").write_text(json.dumps(pkt, indent=2, sort_keys=True) if pkt else "{}")
    packets[g] = pkt

fm = {"campaign_id":"SWARM_SMOKE_V0", "task_hash": PRE["task_hash"],
      "corpus_manifest_hash": PRE["corpus_manifest_hash"],
      "preflight_sha256": sha((HERE/"preflight.json").read_bytes()),
      "G1_sha256": sha((HERE/"G1.json").read_bytes()),
      "G2_sha256": sha((HERE/"G2.json").read_bytes()),
      "G3_sha256": sha((HERE/"G3.json").read_bytes()),
      "completeness": completeness,
      "swarm_complete": all(v["complete"]==1 for v in completeness.values())}
(HERE/"freeze_manifest.json").write_text(json.dumps(fm, indent=2))
for g,v in completeness.items():
    print(f"{g}: complete={v['complete']} claims={v['claim_count']} {v['reasons']}")
print("swarm_complete =", fm["swarm_complete"])
