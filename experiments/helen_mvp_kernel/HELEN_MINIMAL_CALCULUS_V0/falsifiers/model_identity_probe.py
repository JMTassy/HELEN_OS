#!/usr/bin/env python3
"""
model_identity_probe — B_nu falsifier.
Obligation: the TCB depends on typed candidate semantics, never on cognitive
identity. Target: B_nu = 0 (zero TCB branches conditioned on model/provider).

Level 1 (this script): token scan of TCB components for cognitive-identity
strings. A hit is a CANDIDATE violation requiring human reading — an identity
token in a comment is noise; in a conditional it is a real B_nu > 0 finding.
Level 2 (future): semantic scan for identity-conditioned control flow.

NON_SOVEREIGN · read-only · authority=false.
"""
import re, sys, pathlib

REPO = pathlib.Path(__file__).resolve().parents[3].parent  # helen_os_v1
TCB_COMPONENTS = [
    "helen_kernel/gates/claim_type_policy.py",       # jurisdiction gate
    "helen_os/helen_executor.py",                     # manifest executor (wired)
    "helen_os/executor/bounded_executor_v1.py",       # bounded executor (wired)
    "helen_os/governance/canonical.py",               # canonicalizer
    "helen_os/governance/validators.py",              # verifier
    "tools/ndjson_writer.py",                         # ledger writer (kernel boundary)
]
IDENTITY_TOKENS = re.compile(
    r"\b(claude|anthropic|gemma|qwen|gpt|glm|openai|mistral|ollama|llama|deepseek|grok)\b",
    re.IGNORECASE)

def main():
    findings, scanned = [], []
    for rel in TCB_COMPONENTS:
        p = REPO / rel
        if not p.exists():
            scanned.append((rel, "ABSENT")); continue
        scanned.append((rel, "scanned"))
        for i, line in enumerate(p.read_text(errors="replace").splitlines(), 1):
            if IDENTITY_TOKENS.search(line):
                findings.append(f"{rel}:{i}: {line.strip()[:100]}")
    print("model_identity_probe — B_nu token scan")
    for rel, st in scanned:
        print(f"  [{st}] {rel}")
    if findings:
        print(f"CANDIDATE_VIOLATIONS ({len(findings)}) — require human classification:")
        for f in findings: print("  " + f)
    else:
        print("CANDIDATE_VIOLATIONS: 0")
    print(f"B_nu_token_level = {len(findings)}  (target 0; token-level upper bound)")
    return 0

if __name__ == "__main__":
    sys.exit(main())
