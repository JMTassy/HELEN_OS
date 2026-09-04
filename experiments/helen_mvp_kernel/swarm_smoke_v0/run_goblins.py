#!/usr/bin/env python3
"""SWARM_SMOKE_V0 — phase goblins: 3 isolated Qwen3.8-9B calls, freeze, hash,
mechanical completeness. NON_SOVEREIGN · authority=false · ledger_effect=none."""
import hashlib, json, pathlib, re, subprocess, time, urllib.request

HERE = pathlib.Path(__file__).resolve().parent
PRE = json.loads((HERE / "preflight.json").read_text())
PORT = 8094
MODEL_PATH = str(pathlib.Path("~/models/qwen38-9b/Qwen3.8-9B-Q4_K_M.gguf").expanduser())
ARGS = ["-ngl", "99", "-c", "16384", "-fa", "on", "-ctk", "q4_0", "-ctv", "q4_0", "-np", "1"]

CORPUS_TEXT = "\n\n".join(
    f"===== FILE: {m['path']} =====\n" +
    "\n".join(f"{i+1}: {l}" for i, l in enumerate(
        (HERE / m["path"]).read_text().splitlines()))
    for m in PRE["corpus_manifest"])

def prompt_for(gid):
    return f"""You are {gid}, an isolated HELEN Goblin. campaign_id=SWARM_SMOKE_V0.
authority=false. canon=false. ledger_effect=none. proposal_only.

BOUNDED QUESTION:
{PRE['question']}

FROZEN CORPUS (the entire world for this task; line numbers included):
{CORPUS_TEXT}

TASK: From this corpus ONLY, produce at most {PRE['budget']['max_claims']} claims
answering the bounded question. A claim = one concrete candidate path by which
state (H / institutional state in these engines) could be created, replaced or
mutated without a valid admission witness. Each claim need