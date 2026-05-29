# Workflow: Writing Activator

**Stage:** Active → Produce (pre-draft)
**Trigger:** before writing — operator names topic/title
**Halt discipline:** produces a writing brief; operator writes the piece

This is the workflow HELEN does not have natively. Retrieval-first, generation-second.

---

## Prompt

```text
I am about to write about: <TOPIC/TITLE>

1. SCAN
   Read every note in 01_ACTIVE/permanent/ relevant to this topic.

2. PRODUCE WRITING BRIEF

   STRONGEST ARGUMENT
   - The most defensible claim my notes support on this topic.
   - State it as one sentence.

   EVIDENCE (3-7 entries)
   - For each: note title + the specific quote or claim that backs the argument.

   COUNTERARGUMENTS (1-3 entries)
   - Notes that challenge or complicate the argument.
   - For each: note title + the challenge it raises.

   SPECIFIC DETAILS
   - Statistics, examples, distinctions, or quotes already in my notes that
     belong in this piece.

   GAPS
   - What my notes do not yet know that this piece would need.
   - Each gap = one explicit research question.

   STRUCTURE PROPOSAL
   - Based on what my notes contain, what arrangement makes the strongest piece?
   - Title proposals: 3 options.
   - Opening proposals: 3 options.

3. SAVE
   - 01_ACTIVE/writing-briefs/<slug>.brief.md

4. CONSTRAINT
   - Do NOT write the piece. The brief surfaces what my notes already know.
   - Do NOT introduce material from outside the vault.
   - Do NOT recommend angles. Show what the notes support.
```

---

## Boundaries

- Briefs are working documents, not sealed outputs.
- The operator writes the piece. Claude produces the inventory.
- If a brief generates no `EVIDENCE` entries, the vault does not yet know
  enough to support this piece — fix capture, not writing.
