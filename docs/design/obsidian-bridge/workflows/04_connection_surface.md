# Workflow: Connection Surface

**Stage:** Connect
**Trigger:** weekly (one fixed day)
**Halt discipline:** proposes links; never auto-links without approval

This is the CHIDDUSH analog. Latent structure recovery.

---

## Prompt

```text
Read every permanent note created or modified in the last 7 days.

For each new note:

1. SCAN
   Read all of 01_ACTIVE/permanent/ to find existing notes that share a
   MEANINGFUL connection.

2. MEANINGFUL CONNECTION TYPES (only these count):
   - SAME PRINCIPLE, DIFFERENT DOMAIN
     (the same underlying idea applied in two contexts)
   - CONTRADICTION
     (two notes make incompatible claims worth examining together)
   - EVIDENCE LINK
     (one note provides evidence for or against another)
   - LATENT PATTERN
     (a structure visible across 3+ notes that no single note names)

3. SKIP
   - Already-linked pairs.
   - Surface-tag matches (e.g. both tagged "AI" with no deeper link).
   - Trivial restatements.

4. PROPOSE
   For each non-obvious connection found:
   - Name both notes
   - Describe the specific connection in one sentence
   - Explain why connecting them makes BOTH notes more useful

5. HALT
   - Save proposals to 01_ACTIVE/connection-surfaces/<date>.md
   - Do NOT add wikilinks to existing notes without operator approval.

6. ON APPROVAL
   - Add the wikilink to both notes
   - Append a one-line entry to 04_SYSTEM/logs/connections.log:
     <date> <note-a> ↔ <note-b> [<connection-type>]
```

---

## Boundaries

- Only non-obvious connections. If the link is already implied by tags, skip.
- Never modify a permanent note without operator approval per link.
- Connection density is not the metric. Generative density is.
