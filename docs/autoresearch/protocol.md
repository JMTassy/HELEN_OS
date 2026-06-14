# HELEN Autoresearch Protocol

## Research Loop (9 Steps)

```
1. INTENT
   Define the research question as a falsifiable hypothesis.
   A hypothesis that cannot be falsified is not research — it is assertion.

2. PROBE
   Gather evidence from admissible corpus:
     - Code files (grep, AST scan, sha256)
     - Documentation (frequency, co-occurrence, context)
     - Git history (evolution, drift events, commit messages)
     - Gate artifacts (K8 traces, K-τ manifests, witness probes)
     - Receipts (ledger entries, tranche receipts, closure receipts)
   Every probe result is logged with source path and method.

3. CLAIM EXTRACTION
   Convert raw probe output into explicit claims:
     "Concept X appears in N files with context Y"
     "Concept X co-occurs with concept Z in M contexts"
   Claims are typed: OBSERVED / INFERRED / RECEIPT / REJECTED

4. EVIDENCE BINDING
   Attach to every claim:
     - source_path: the file(s) probed
     - source_hash: sha256 of source at probe time
     - method: grep | ast_scan | git_log | corpus_walk
     - timestamp_utc: probe time (utcnow, not local)
     - context: excerpt or count

5. VALIDATION
   Run gate stack (see gates.md):
     K0  syntax valid
     K1  source bound
     K2  claim explicit (not "it seems" or "probably")
     K3  evidence attached
     K4  method declared
     K5  contradiction scan (does claim conflict with prior receipts?)
     K6  provenance stable (source file sha unchanged since binding)
     K7  replay path exists (can claim be reconstructed from bindings alone?)
     K8  deterministic artifact (no ND output in claim chain)
     Kτ  temporal coherence (timestamp plausible for claimed corpus state)
     W   witness coupling (Δ_R = 0 between claimed and observed ledger)

6. RECEIPT
   Emit AUTORESEARCH_RECEIPT_V1:
     epoch, hypothesis, verdict, evidence_count, claim, source_hashes,
     gate_scores, lineage_pressure

7. LEDGER
   Append to sandbox receipt log only (non-sovereign).
   NON_SOVEREIGN receipts do NOT enter town/ledger_v1.ndjson directly.
   They are candidate claims awaiting MAYOR routing.

8. REPLAY
   Reconstruct the conclusion from receipts alone.
   If reconstruction fails → claim is inadmissible → do not promote.

9. DOCTRINE DELTA
   If replay succeeds and MAYOR routes the claim:
     Emit Doctrine_new = Diff(Doctrine_candidate, Doctrine_SOT)
   Never regenerate doctrine from memory. Diff only.
```

## Probe Types

| Type | Method | When to use |
|---|---|---|
| FREQUENCY | grep -r -c | How often does concept X appear in corpus? |
| COUPLING | grep -r -l A ∩ B | Do X and Y co-occur? |
| EVOLUTION | git log --grep | Did frequency change over time? |
| CONTRADICTION | grep + receipt scan | Is X claimed without evidence? |
| COVERAGE | filesystem walk | Are all expected artifacts present? |
| STALENESS | T6 taxonomy probe | Is provenance current? |

## Epoch Budget

One epoch = one hypothesis probe.
Bounded run: N epochs defined at start.
No open-ended loops. No recursive spawning.
Each epoch terminates with CONFIRMED / WEAK / ABSENT / ERROR.

## What Autoresearch May NOT Do

- Write to sovereign paths (oracle_town/kernel/, governance/, schemas/, ledger)
- Emit verdicts (SHIP/NO_SHIP/BLOCK) — that belongs to gates and MAYOR
- Self-certify claims ("this is true because the model says so")
- Promote doctrine deltas without a receipt and MAYOR ruling
- Access external networks
