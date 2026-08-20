#!/usr/bin/env python3
import hashlib, json, pathlib, subprocess
HERE = pathlib.Path(__file__).resolve().parent
def sha(b): return hashlib.sha256(b).hexdigest()

corpus = sorted((HERE/"corpus").glob("*.py"))
manifest = [{"path": f"corpus/{p.name}", "sha256": sha(p.read_bytes())} for p in corpus]
corpus_hash = sha(json.dumps(manifest, sort_keys=True).encode())

QUESTION = ("Identify distinct candidate paths by which institutional state could "
            "change without a valid admission witness.")
SCHEMA = {
 "goblin_id": "G1|G2|G3", "campaign_id": "SWARM_SMOKE_V0", "task_hash": "...",
 "claims": [{"proposition_key": "...", "claim": "...", "predicate": "...",
   "object": "...", "scope": "...", "evidence_refs": ["path:line"],
   "source_roots": ["..."], "evidence_class": "OBSERVED|REPORTED|INFERRED|UNKNOWN",
   "candidate_falsifier": "...", "confidence": "LOW|MEDIUM|HIGH"}],
 "unknowns": [], "forbidden_paths_checked": [],
 "authority": False, "ledger_effect": "none"}
BUDGET = {"max_claims": 3, "max_output_tokens": 1600, "max_words": 350,
          "timeout_seconds": 300}
task_hash = sha(json.dumps({"q": QUESTION, "schema": SCHEMA, "budget": BUDGET,
                            "corpus": corpus_hash}, sort_keys=True).encode())[:16]

head = subprocess.run(["git","rev-parse","HEAD"], capture_output=True, text=True,
                      cwd=HERE).stdout.strip()
status = subprocess.run(["git","status","--porcelain"], capture_output=True,
                        text=True, cwd=HERE).stdout
dirty_fp = sha(status.encode())[:16]

pre = {"campaign_id": "SWARM_SMOKE_V0", "question": QUESTION,
 "task_hash": task_hash, "repo_head": head,
 "working_tree_status": f"DIRTY({len(status.splitlines())} files)",
 "dirty_tree_fingerprint": dirty_fp,
 "bounded_corpus_paths": [m["path"] for m in manifest],
 "corpus_manifest": manifest, "corpus_manifest_hash": corpus_hash,
 "generator_model": "Qwen3.8-9B-Q4_K_M.gguf sha256 df13d660...44a7a (empero-ai distill)",
 "generator_runtime": "llama-server b9430 Metal ngl99 fa on ctk/ctv q4_0 c16384 port 8094",
 "hal_model": "Claude sub-agent (fresh context; different weights family from generator => I_weights=1; I_corpus=0 declared)",
 "swarm_size": 3, "budget": BUDGET,
 "thinking": False,
 "thinking_control": "chat_template_kwargs.enable_thinking=false — DISTINCT control from timeout; both explicit; preflight probe verifies actual suppression",
 "timeout_control": "HTTP request timeout 300s — bounds wall clock only; NOT a thinking control",
 "tools": ["none inside the model; goblins receive frozen corpus text inline"],
 "output_schema": SCHEMA,
 "authority": False, "canon": False, "ledger_effect": "none"}
(HERE/"preflight.json").write_text(json.dumps(pre, indent=2))
print(json.dumps({"task_hash": task_hash, "corpus_manifest_hash": corpus_hash[:16],
                  "repo_head": head[:12], "dirty_fp": dirty_fp,
                  "corpus_files": len(manifest)}, indent=1))
