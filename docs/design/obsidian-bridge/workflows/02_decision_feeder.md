# Workflow: Active Decision Feeder

**Stage:** Active → (synthesis, no output yet)
**Trigger:** on demand — operator names a decision
**Halt discipline:** produces a brief, never a decision

---

## Prompt

```text
I am working on this decision: <DECISION>

1. SCAN
   Read every note in 01_ACTIVE/permanent/.
   Find every note relevant to this decision — not just tagged ones.
   Relevance = a thoughtful operator would consider it.

2. CLASSIFY each relevant note as one of:
   - SUPPORTS  — note's claim/evidence supports a direction
   - CHALLENGES — note complicates or refutes a direction
   - NUANCES   — note adds distinction without choosing a side
   - DEFINES   — note clarifies a term or boundary in the decision

3. SYNTHESIZE — produce a decision brief with:
   - The decision restated in operator's terms
   - SUPPORTS bullets, each with note title + 1-sentence relevance
   - CHALLENGES bullets, same format
   - NUANCES + DEFINES bullets, same format
   - WHAT YOUR NOTES KNOW: the synthesis position your accumulated notes
     would arrive at, stated as a claim — not a recommendation
   - WHAT YOUR NOTES DO NOT KNOW: the gaps that would need external input

4. SAVE
   - 01_ACTIVE/decisions/<slug>.brief.md (overwrite OK; it's a working doc)

5. CONSTRAINT
   - Use only notes in this vault. Do NOT introduce information from outside.
   - Do NOT recommend a decision. The brief is for the operator to decide from.
```

---

## Boundaries

- This workflow never writes to `03_OUTPUT/`. Briefs are not outputs.
- This workflow never emits a receipt. No output, no receipt.
- The brief is overwriteable — it's a snapshot, not a sealed artifact.
