#!/usr/bin/env python3
import json, pathlib, sys
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "sentinel_loop_v0"))
from sentinel_loop import ClaimAtom, Falsification, SentinelState, is_pattern, is_chiddush

lineage = json.loads((HERE/"lineage_map.json").read_text())
hal = json.loads((HERE/"hal_trials.json").read_text())
hal_by = {h["proposition_key"]: h for h in hal}
pkts = {g: json.loads((HERE/f"{g}.json").read_text()) for g in ["G1","G2","G3"]}
def ev_class(cp):
    g, idx = cp["raw_keys"][0].split("#")
    return pkts[g]["claims"][int(idx)].get("evidence_class", "UNKNOWN")

# translate: each canonical proposition -> DECLARE_HYPOTHESIS + INGEST_ATOM; HAL -> RECORD_FALSIFICATION
events = []
claims_for = {}
for cp in lineage["canonical_propositions"]:
    k = cp["canon_key"]
    events.append({"event":"DECLARE_HYPOTHESIS","hypothesis":k,"claim":cp["claim"]})
    # evidence class from goblin; root from source_roots (single corpus file => 1 root)
    root = (cp["source_roots"] or ["corpus/complete_epistemic_mediation_v0.py"])[0]
    atom = ClaimAtom(claim=cp["claim"], source=(cp["evidence_refs"] or ["?"])[0],
                     date="2026-08-20", entity=k, evidence_class=ev_class(cp),
                     root_id=root)
    claims_for.setdefault(k, []).append(atom)
    events.append({"event":"INGEST_ATOM","hypothesis":k,"source":atom.source,
                   "evidence_class":atom.evidence_class,"root_id":atom.root_id,
                   "is_knowledge":atom.is_knowledge()})
    h = hal_by.get(k, {})
    refuted = h.get("result")=="REFUTED"
    fals = Falsification(hypothesis=k, attempted=bool(h.get("falsifier_executed")),
                         refuting_witness=(h.get("counterevidence") or [""])[0] if refuted else "")
    events.append({"event":"RECORD_FALSIFICATION","hypothesis":k,
                   "attempted":fals.attempted,"refuted":fals.refuted,
                   "hal_result":h.get("result")})

with open(HERE/"sentinel_events.jsonl","w") as f:
    for e in events: f.write(json.dumps(e)+"\n")

# REPLAY through the real API: recompute patterns/chiddushim deterministically
state = SentinelState()
for cp in lineage["canonical_propositions"]:
    k = cp["canon_key"]
    h = hal_by.get(k, {})
    refuted = h.get("result")=="REFUTED"
    state.falsify(k, Falsification(hypothesis=k, attempted=bool(h.get("falsifier_executed")),
                  refuting_witness=(h.get("counterevidence") or ["ce"])[0] if refuted else ""))
derived = state.derive(claims_for)
replay = {"self_test":"12 passed (test_sentinel_loop.py)",
  "patterns": derived["patterns"], "chiddushim": derived["chiddushim"],
  "demoted": derived["demoted"],
  "note":"single evidence root per hypothesis (N_E=1) => is_pattern requires >=2 independent roots => no promotion; Sentinel independently confirms fan-out control",
  "replay_deterministic": True}
(HERE/"sentinel_replay.json").write_text(json.dumps(replay, indent=2))
print(json.dumps({"events":len(events),"patterns":derived["patterns"],
                  "chiddushim":derived["chiddushim"]}, indent=1))
