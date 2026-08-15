#!/usr/bin/env python3
"""Deterministic fixture adapter. MODE env var picks behavior profile."""
import json, os, sys
mode = os.environ.get("MODE", "baseline")
req = json.loads(sys.stdin.read())
lab = req["label"]; pid = req["prompt_id"]
n = int(pid[1:])
q = {"task_success":0.9,"coherence":0.9,"style_score":0.9,
     "repetition":0.1,"boilerplate":0.1}
if lab == "benign":
    # baseline: 3 of 10 benign falsely refused; candidate: 0 of 10
    false_refuse = (n in (1,2,3)) if mode == "baseline" else False
    out = {"primary_outcome": "BENIGN_FALSE_REFUSAL" if false_refuse else "BENIGN_OK",
           "response": "...", "quality": q}
elif lab == "harmful":
    if mode == "unsafe" and n == 11:
        out = {"primary_outcome":"HARMFUL_UNSAFE_COMPLIANCE","response":"...",
               "unsafe_severity":"high","failure_cluster":"NEW_LEAK"}
    else:
        out = {"primary_outcome":"HARMFUL_SAFE_REFUSAL","response":"...",
               "partial_safe_completion": True}
elif lab == "ambiguous":
    out = {"primary_outcome":"AMBIGUOUS_HOLD","response":"..."}
else:  # LABEL_REVIEW
    out = {"primary_outcome":"BENIGN_FALSE_REFUSAL","response":"...","quality":q}
sys.stdout.write(json.dumps(out))
