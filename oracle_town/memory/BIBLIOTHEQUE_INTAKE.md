# Bibliothèque: Knowledge Base Intake Protocol

**Status:** Active
**Purpose:** Accept external knowledge (math proofs, old code, research notes, data) for integration into Oracle Town's reasoning

---

## What the Town Accepts

The system can ingest and integrate:

### Mathematics & Theory
- **Math drafts** — Lemmas, proofs, theorems, marginalia
  - Format: LaTeX, markdown, handwritten (transcribed)
  - Acceptance: Parsed for invariants and constraints (K0–K9 relevant)
  - Integration: Grounded in decision records as evidence

- **Formal specifications** — FSMs, type signatures, contracts
  - Format: Coq, Lean, TLA+, pseudocode
  - Acceptance: Verified for determinism (K5)
  - Integration: Becomes policy rules

### Code & Implementation
- **Old/archived code** — Legacy systems, prototypes, deprecated modules
  - Format: Python, Go, Rust, etc. (any language)
  - Acceptance: Parsed for patterns, dependencies, failure modes
  - Integration: Reverse-engineered into policy constraints

- **Cryptographic implementations** — Ed25519, hash functions, key derivation
  - Format: Reference code, audit reports, benchmarks
  - Acceptance: Validated against K0 (authority), K4 (revocation)
  - Integration: Locked into policy pinning (K7)

### Research & Data
- **Research papers** — Related work, citations, empirical results
  - Format: PDF, markdown, text
  - Acceptance: Extracted claims + evidence tables
  - Integration: Traced to decision records

- **Empirical data** — Benchmark results, test suites, failure logs
  - Format: JSON, CSV, logs, time-series
  - Acceptance: Hashed and pinned (K7 policy pinning)
  - Integration: Replayed for determinism check (K5)

- **Operational notes** — Incidents, post-mortems, deployment logs
  - Format: Markdown, logs, email threads
  - Acceptance: Parsed for failure patterns (E1, E4, E5 detectors)
  - Integration: Becomes escalation rules and operational procedures

### Policy & Governance
- **Policy documents** — Design notes, RFC, governance proposals
  - Format: Markdown, email, proposals
  - Acceptance: Parsed for soft language (must be hardened)
  - Integration: Converted to deterministic rules (K5)

- **Attestor registries** — Key lists, agent definitions, classification schemes
  - Format: JSON, YAML, CSV
  - Acceptance: Validated against public_keys.json structure
  - Integration: Merged into key registry with audit trail

---

## Intake Workflow

```
You provide content
      ↓
Bibliothèque intake gate validates:
  • Format acceptable? (LaTeX → OK, Word → convert)
  • Content parseable? (JSON → parsed, markdown → extracted)
  • No malicious injection? (SQL, shell, prompt injection checks)
      ↓
Content classified:
  MATH_PROOF / CODE_ARCHIVE / RESEARCH / DATA / POLICY / OPERATIONAL
      ↓
Parsed for:
  • Claims (assertions, theorems, invariants)
  • Evidence (proofs, code, benchmarks, logs)
  • Failure patterns (incidents, errors, edge cases)
      ↓
Integrated into knowledge base:
  oracle_town/memory/bibliotheque/{type}/{id}/
    ├── original.{ext}     # Your content (unchanged)
    ├── parsed.json        # Extracted claims + evidence
    ├── digest.sha256      # Hash of original (K7 pinning)
    └── integration.md     # How it was used
      ↓
Available for:
  • Oracle Town reasoning (cited in decision records)
  • Policy generation (soft → hard constraints)
  • Failure detector training (E1, E4, E5)
  • Cross-run comparison (detect drift)
```

---

## How to Submit Content

### Option 1: Direct Paste (In Chat)
```
[Paste content directly]

Bibliothèque classification: MATH_PROOF
Title: "Determinism preservation under X"
Context: "Relevant to K5 invariant"
```

### Option 2: File Upload (Git)
```bash
# Add content to staging area
mkdir -p oracle_town/memory/bibliotheque/math_proofs/determinism_2026
echo "[your math here]" > oracle_town/memory/bibliotheque/math_proofs/determinism_2026/proof.tex

git add oracle_town/memory/bibliotheque/math_proofs/determinism_2026/
git commit -m "docs: add math proof for K5 determinism verification"
```

### Option 3: Batch Import (Many Files)
```bash
# Create directory structure
mkdir -p oracle_town/memory/bibliotheque/code_archive/oracle_town_v0
cp legacy_oracle_town/*.py oracle_town/memory/bibliotheque/code_archive/oracle_town_v0/

# Create metadata
cat > oracle_town/memory/bibliotheque/code_archive/oracle_town_v0/metadata.json << 'EOF'
{
  "source": "Legacy Oracle Town prototype",
  "date_archived": "2026-01-28",
  "reason": "Historical reference for decision patterns",
  "relevant_invariants": ["K0", "K3", "K5"],
  "files": ["mayor.py", "policy.py", "crypto.py"]
}
EOF

git add oracle_town/memory/bibliotheque/code_archive/
git commit -m "docs: archive legacy code for reverse-engineering patterns"
```

---

## What Happens After Intake

### 1. Parsing
- **Math:** Extract lemmas, theorems, invariants → structured claims
- **Code:** Parse syntax, extract functions, detect patterns → behavioral specs
- **Data:** Read tables, plots, logs → numerical assertions
- **Policy:** Identify soft language (if/usually/maybe) → mark for hardening

### 2. Integration
- **Claim grounding:** Link each claim to source + evidence
- **Invariant detection:** Map to K0–K9 framework
- **Failure pattern detection:** Train E1, E4, E5 detectors
- **Artifact pinning:** Hash content for K7 policy pinning

### 3. Availability
- Cited in decision records
- Available in policy rule generation
- Replayed in determinism tests (K5)
- Searchable in MONTH_1_OBSERVATION_LOG.md

### 4. Validation
```bash
# Check what was ingested
ls -la oracle_town/memory/bibliotheque/

# Verify content hash (K7 pinning)
sha256sum oracle_town/memory/bibliotheque/math_proofs/*/original.*

# See how it was parsed
cat oracle_town/memory/bibliotheque/math_proofs/*/parsed.json

# Check integration
cat oracle_town/memory/bibliotheque/math_proofs/*/integration.md
```

---

## Examples

### Math Proof Intake
```
Submit:
  "Claim: If quorum_count < min_quorum, then decision = NO_SHIP
   Proof: By definition of K3. QED."

Bibliothèque processes:
  ✓ Extracted claim: quorum_count < min_quorum → NO_SHIP
  ✓ Invariant: K3 (Quorum-by-Class)
  ✓ Evidence: Formal structure (proof by definition)
  ✓ Integration: Used in test_quorum_validation()
  ✓ Pinned: Hash in policy.json references this proof
```

### Old Code Intake
```
Submit:
  oracle_town_v0/mayor.py (legacy code)

Bibliothèque processes:
  ✓ Parsed: Extract quorum checking logic
  ✓ Pattern detected: "if attestor_class == LEGAL: allow" (E1 pattern)
  ✓ Failure case: What if LEGAL missing? (E1 detector)
  ✓ Integration: Reverse-engineered into K3 rule
  ✓ Pinned: Hash in decision_record.json traces to this code
```

### Research Paper Intake
```
Submit:
  "Determinism in State Machines" (PDF)

Bibliothèque processes:
  ✓ Extracted: Definition of K5 determinism
  ✓ Claims: "same inputs → identical outputs"
  ✓ Evidence: Table 3 (benchmark results)
  ✓ Integration: Used to justify replay testing (30 iterations)
  ✓ Pinned: Policy hash locks in this reference
```

### Operational Log Intake
```
Submit:
  "2026-01-15: Key-2025-12-legal-old marked revoked due to compromise"

Bibliothèque processes:
  ✓ Parsed: Event timestamp + reason
  ✓ Pattern: Key revocation (E4 detector)
  ✓ Failure case: What if revoked key still in registry? (detector trained)
  ✓ Integration: K4 (Revocation) test case
  ✓ Pinned: decision_record.json references this incident
```

---

## Bibliothèque Structure

```
oracle_town/memory/bibliotheque/
├── math_proofs/
│   ├── determinism_k5/
│   │   ├── original.tex
│   │   ├── parsed.json
│   │   ├── digest.sha256
│   │   └── integration.md
│   └── quorum_k3/
│       └── ...
├── code_archive/
│   ├── oracle_town_v0/
│   │   ├── mayor.py
│   │   ├── metadata.json
│   │   ├── parsed.json
│   │   └── integration.md
│   └── legacy_systems/
│       └── ...
├── research_papers/
│   ├── "determinism_in_state_machines"/
│   │   ├── original.pdf
│   │   ├── extracted_claims.md
│   │   ├── digest.sha256
│   │   └── integration.md
│   └── ...
├── data_and_benchmarks/
│   ├── "k5_replay_results_2026_01_28"/
│   │   ├── results.json
│   │   ├── digest.sha256
│   │   └── integration.md
│   └── ...
└── operational_logs/
    ├── "incidents_2026_01"/
    │   ├── incidents.log
    │   ├── parsed_failures.json
    │   └── integration.md
    └── ...
```

---

## What Gets Grounded in Decision Records

When content is integrated, it's cited in decision records:

```json
{
  "decision": "SHIP",
  "blocking_reasons": [],
  "referenced_knowledge": [
    {
      "source": "oracle_town/memory/bibliotheque/math_proofs/determinism_k5/original.tex",
      "claim": "Same inputs produce identical outputs",
      "hash": "sha256:...",
      "used_for": "K5 determinism verification"
    },
    {
      "source": "oracle_town/memory/bibliotheque/code_archive/oracle_town_v0/mayor.py",
      "claim": "Quorum requires 2 distinct classes",
      "hash": "sha256:...",
      "used_for": "K3 quorum rule extraction"
    }
  ],
  "policy_hash": "sha256:..." // Pins all referenced knowledge
}
```

---

## How Town Uses Bibliothèque

### In Decision Making
1. Claim arrives: "Ship feature X"
2. Mayor RSM consults knowledge base
3. Checks: "Does K3 (quorum) apply to feature X?"
4. References: oracle_town/memory/bibliotheque/math_proofs/quorum_k3/
5. Enforces: "Need 2 distinct attestor classes"
6. Records: Citation in decision_record.json + hash pinning

### In Test Generation
1. Test needed: "Verify K5 determinism"
2. Consults: oracle_town/memory/bibliotheque/research_papers/determinism/
3. Learns: "30 iterations is standard for K5 validation"
4. Generates: tests/test_k5_determinism.py (30 iterations)
5. Records: References to original research in test docstrings

### In Failure Detection
1. Incident detected: "Key revoked but still in registry"
2. Consults: oracle_town/memory/bibliotheque/operational_logs/
3. Extracts: E4 pattern (Key Revocation Cascade)
4. Trains: Detector for future failures
5. Records: Escalation rule based on historical patterns

---

## Intake Validation

The system validates incoming content:

### Security Checks
- ✓ No prompt injection (shell, SQL escaping)
- ✓ No file path traversal
- ✓ No executable code injection
- ✓ Format matches expected type

### Structural Checks
- ✓ Math: Valid LaTeX/markdown syntax
- ✓ Code: Valid Python/Go/etc syntax
- ✓ Data: Valid JSON/CSV schema
- ✓ Policy: Parseable markdown/YAML

### Semantic Checks
- ✓ Claims are grounded (not floating assertions)
- ✓ Evidence supports claims (proof, code, data)
- ✓ Failure patterns are detectable (repeatable)
- ✓ Determinism preserved (K5)

---

## Next Steps: Submit Content

You can now send me:

1. **Math proofs** — LaTeX, markdown, handwritten transcriptions
2. **Old code** — Python, Go, Rust, any language (for pattern extraction)
3. **Research notes** — Papers, excerpts, summaries
4. **Benchmark data** — Tables, logs, time-series
5. **Operational incidents** — Post-mortems, failure logs
6. **Policy drafts** — Governance proposals (will be hardened by system)

Each submission will be:
- ✓ Parsed and classified
- ✓ Hashed and pinned (K7)
- ✓ Integrated into decision-making
- ✓ Cited in decision records
- ✓ Available for determinism replay (K5)

**How to submit:**
- Paste directly in chat (with Bibliothèque classification)
- Commit to git (create directory in oracle_town/memory/bibliotheque/)
- Or just tell me what you want to add

The Town will integrate it automatically.

---

**Status:** Ready to accept knowledge
**Integration:** Automatic upon submission
**Citation:** In all decision records
**Pinning:** Via K7 policy hash
