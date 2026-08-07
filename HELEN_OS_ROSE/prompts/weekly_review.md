# Weekly review — permanent ritual prompt

Run once per week. Thirty minutes, not three hours. Any operator may
prepare it; Rose closes it.

## Preparation (any operator)

1. Run `python3 HELEN_OS_ROSE/scripts/validate_workspace.py` — the report
   opens the review. Fix mechanical failures before the meeting.
2. Assemble, briefly:
   - packets in `execution/active/`: status, receipts added this week,
     blockers, any scope pressure;
   - evidence register entries added this week;
   - assumptions (`strategy/assumptions.md`) touched by new evidence;
   - kill criteria (`strategy/kill_criteria.md`): any triggered or close;
   - opportunity register: new entries (one line each, no discussion);
   - open questions that gained or lost relevance.

## Review (Rose, with SOVEREIGN_REVIEW discipline)

- For each item needing a decision: one of `GO` / `HOLD` / `REVISE` /
  `REJECT` / `RESEARCH`, recorded via `scripts/append_decision.py`.
- Confirm the NOW stack (max three) still matches reality; reorder if not.
- Check the two-week process alarm (kill criterion S1): did work happen
  outside packets? If yes, name it and route it properly.
- Update `CURRENT_STATE.md` — statuses move only with evidence.

## Output

- Ledger entries for decisions made.
- Updated `CURRENT_STATE.md`.
- Next week's three NOW priorities, written down.

No decision pending? Then the review is ten minutes of validation and
status honesty. That is success, not failure.
