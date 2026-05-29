# Workflow: Output Generator

**Stage:** Produce → Receipt
**Trigger:** when a piece is ready to be drafted from accumulated notes
**Halt discipline:** drafts + receipt skeleton; operator seals

This is the only workflow that writes to `03_OUTPUT/`.

---

## Prompt

```text
I need to produce: <OUTPUT TYPE AND DESCRIPTION>
Topic / scope: <TOPIC>

1. SCAN
   - Read all 01_ACTIVE/permanent/ notes tagged with <TOPIC> or surfaced by
     the most recent Connection Surface for this topic.
   - List the notes you will use. Halt if fewer than 3 — the vault does not
     yet support this output.

2. SYNTHESIZE — not summarize
   - Produce an output that uses ONLY information from the listed notes.
   - The output's claim should be one no single source note makes, but that
     the combination supports.
   - Write in the operator's voice as described in CLAUDE.md.

3. SAVE
   - Draft → 03_OUTPUT/<type>/<date>_<slug>.md

4. PRODUCE RECEIPT SKELETON
   - Compute sha256 of the draft file.
   - Compute sha256 of each source note.
   - Write 03_OUTPUT/.receipts/<date>_<slug>.receipt.json:

     {
       "receipt_type": "OUTPUT_RECEIPT_V1",
       "output_id": "<date>_<slug>",
       "output_path": "...",
       "output_hash": "sha256:...",
       "produced_at": "<UTC>",
       "source_notes": [
         {"path": "...", "hash": "sha256:..."},
         ...
       ],
       "synthesis_notes": "<one-sentence: what this output claims that no single source claims>",
       "contribution_count": <number of source notes>,
       "authority": "operator",
       "sealed_by": null,
       "override": false
     }

5. HALT
   - Report draft path and receipt path.
   - Wait for operator review.

6. ON OPERATOR SEAL
   - Set "sealed_by": "<initials>" in the receipt
   - Append one line to 04_SYSTEM/logs/outputs.log:
     <date> <slug> sources=N hash=<short> sealed_by=<initials>
   - Increment contribution_count for each source note (track in
     01_ACTIVE/permanent/.contributions.json — or wherever you store the counter).
```

---

## Boundaries

- Never seal a receipt. Only the operator sets `sealed_by`.
- Never write to `03_OUTPUT/` without producing the receipt skeleton in the
  same pass.
- Never edit a sealed receipt. Supersede with a new one if needed.
- If `synthesis_notes` cannot be filled with a real synthesis claim, the piece
  is not synthesis — it is summary. Send back to drafting.
