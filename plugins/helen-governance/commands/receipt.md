# /helen-governance:receipt

Emit a structured receipt for an action just taken. Honors the
`no-receipt-no-claim` invariant.

## Usage

```
/helen-governance:receipt <action-description>
```

## What this command does

When invoked, Claude produces a receipt template prefilled with:

- Actor identification (Claude session model / role)
- Action description (from user input)
- Timestamp (UTC ISO-8601)
- A scaffold for evidence, verdict, and halt-boundary fields

Claude then fills in the scaffold based on the actual work just
performed in this conversation. The receipt is offered as either:

- A markdown block ready to paste into a document or commit message
- A JSON object ready to write as a structured receipt file

## Template (markdown form)

```markdown
## Receipt — <action title>

- **Actor**: <model id, role>
- **Action**: <one-line description>
- **Tool / Command**: <how it was performed>
- **Log**: <observable output, faithfully summarized>
- **Evidence**: <what shows the action completed>
- **Verdict**: ADMIT | QUARANTINE | BLOCK | PENDING
- **Halt boundary**: <if applicable; see /helen-governance:halt>
- **Timestamp**: <UTC ISO-8601>
```

## Template (JSON form)

```json
{
  "actor": {"role": "...", "identity": "..."},
  "action": "...",
  "tool": "...",
  "command": "...",
  "log_summary": "...",
  "evidence": {...},
  "verdict": "ADMIT | QUARANTINE | BLOCK | PENDING",
  "halt_boundary": null,
  "timestamp_utc": "..."
}
```

## When to use which form

- **Markdown** for human-readable documentation (commit messages,
  inline doc receipts, PR descriptions)
- **JSON** for machine-validated structured receipts (when a downstream
  parser or governance gate will consume the receipt)

## What this command does NOT do

- Does not write the receipt to disk (Claude offers the text; user
  decides where to persist)
- Does not assign a verdict — the verdict field is the proposer's
  declaration of intent; final verdict comes from a validator
- Does not auto-fill the halt-boundary section — use
  `/helen-governance:halt` separately if a sovereign handoff is needed

## See also

- `no-receipt-no-claim` skill (the invariant this command supports)
- `/helen-governance:halt` (for sovereign deferrals)
- `/helen-governance:diff` (for adopting external doctrine)
