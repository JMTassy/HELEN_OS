#!/usr/bin/env python3
import hashlib, json, pathlib
HERE = pathlib.Path(__file__).resolve().parent
def norm(s): return " ".join(str(s).lower().split())
def canon_key(c):
    return hashlib.sha256(json.dumps(
        [norm(c.get("predicate")), norm(c.get("object")), norm(c.get("scope"))],
        sort_keys=True).encode()).hexdigest()[:12]

raw = []
for g in ["G1","G2","G3"]:
    pkt = json.loads((HERE/f"{g}.json").read_text())
    for i,c in enumerate(pkt.get("claims",[])):
        raw.append({"goblin": g, "raw_key": f"{g}#{i}", "canon_key": canon_key(c),
                    "predicate": c.get("predicate"), "object": c.get("object"),
                    "scope": c.get("scope"), "claim": c.get("claim"),
                    "evidence_refs": c.get("evidence_refs"),
                    "source_roots": c.get("source_roots"),
                    "candidate_falsifier": c.get("candidate_falsifier"),
                    "evidence_class": c.get("evidence_class")})
groups = {}
for r in raw: groups.setdefault(r["canon_key"], []).append(r)
# independent evidence roots (structural fan-out control)
roots = set()
for r in raw:
    for rt in (r["source_roots"] or []): roots.add(norm(rt))
lineage = {"N_raw": len(raw), "N_P": len(groups), "N_E": len(roots),
  "duplicate_groups": {k:[r["raw_key"] for r in v] for k,v in groups.items() if len(v)>1},
  "canonical_propositions": [
     {"canon_key": k, "raw_keys": [r["raw_key"] for r in v],
      "predicate": v[0]["predicate"], "object": v[0]["object"], "scope": v[0]["scope"],
      "claim": v[0]["claim"], "evidence_refs": v[0]["evidence_refs"],
      "source_roots": v[0]["source_roots"], "candidate_falsifier": v[0]["candidate_falsifier"],
      "merge_status": "STRUCTURAL" if len(v)>1 else "SINGLETON"}
     for k,v in groups.items()],
  "independent_roots": sorted(roots),
  "method": "structural (predicate,object,scope) only; no LLM similarity"}
(HERE/"lineage_map.json").write_text(json.dumps(lineage, indent=2))
print(f"N_raw={lineage['N_raw']} N_P={lineage['N_P']} N_E={lineage['N_E']}")
for cp in lineage["canonical_propositions"]:
    print(f"  [{cp['canon_key']}] {cp['merge_status']:10} refs={cp['evidence_refs']}")
    print(f"     {cp['claim'][:110]}")
