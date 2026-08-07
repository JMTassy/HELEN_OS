# Rose decision template

A decision becomes real only as a line in `decision_ledger.jsonl`, appended
via `scripts/append_decision.py`. The ledger is append-only; corrections are
new decisions referencing the old id, never edits.

```bash
python3 HELEN_OS_ROSE/scripts/append_decision.py \
  --decision-id R-001 \
  --date 2026-07-16 \
  --subject "Adopt hospitality decision-twin wedge" \
  --outcome GO \
  --scope "90-day discovery + internal pilot, per strategy/ninety_day_plan.md" \
  --rationale "Rose's stated reasoning, in her words" \
  --authorized-by "ROSE"
```

Field notes:

- `decision_id` — `R-###`, sequential, never reused.
- `outcome` — exactly one of `GO` `HOLD` `REVISE` `REJECT` `RESEARCH`.
- `scope` — what this decision covers; execution packets may not exceed it.
- `rationale` — Rose's reasoning, ideally in her own words.
- `authorized_by` — must explicitly indicate Rose. The script refuses
  anything else; so does the validator.

Before recording, SOVEREIGN_REVIEW must have presented the decision per
`prompts/sovereign_review.md` (plain summary, uncertainty, consequences,
privacy/authority risks, single requested outcome).
