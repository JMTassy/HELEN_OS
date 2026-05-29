# Workflow: Daily Processing Run

**Stage:** Capture → Process
**Trigger:** nightly (or end of work session)
**Halt discipline:** halts before rewriting; operator decides edge cases

---

## Prompt

```text
Process all notes in 00_CAPTURE created or modified today.

For each captured note:

1. USEFULNESS ASSESSMENT (HER lens)
   Can this note contribute to:
   - Any active project listed in CLAUDE.md?
   - Any active decision listed in CLAUDE.md?
   - Any writing topic listed in CLAUDE.md?

   Mark: PROCESS, ARCHIVE_DIRECTLY, or OPERATOR_REVIEW

2. HAL CHECK
   For each PROCESS candidate, flag if any of:
   - verbatim copy with no rewrite
   - no link to active project/topic
   - claim with no source reference
   - purely motivational with no operational content

   Flagged notes stay in 00_CAPTURE with a .hal-block.md sidecar.
   Never silently rejected.

3. HALT
   Report:
   - PROCESS count + titles
   - ARCHIVE_DIRECTLY count + titles
   - OPERATOR_REVIEW count + titles + reason
   - HAL_BLOCK count + reasons

   Do NOT rewrite yet. Wait for operator approval per item.

4. ON APPROVAL: REWRITE
   For each approved PROCESS note:
   - Title = the idea, not the source
   - Body = my understanding in my voice
   - Links = 1-3 existing 01_ACTIVE notes
   - Tags = relevant active projects/topics
   - Footer: original capture path (for traceability)

5. MOVE
   - Rewritten note → 01_ACTIVE/permanent/
   - Original capture → 02_ARCHIVE/captures/<date>/

6. LOG
   - Append a one-line entry to 04_SYSTEM/logs/processing.log:
     <date> processed=N archived=M blocked=K
```

---

## Boundaries

- Never silently delete a capture.
- Never write to `01_ACTIVE` without operator approval per note.
- Never edit an existing `01_ACTIVE` note as part of processing — only create new ones and link.
