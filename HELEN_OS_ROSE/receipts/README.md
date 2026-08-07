# Receipts

Receipts make claims checkable. A receipt records what was done, with what
inputs, producing what artifacts, checked by what tests — so a different
operator can confirm or refute the claim later.

Contents:

- `bootstrap_receipt.json` — what the one-time bootstrap did and did not
  do. Its `status` field stays `IMPLEMENTED_NOT_APPROVED` until Rose
  records decisions covering the strategy.
- Future receipts land here or inside execution packets' `receipts`
  arrays, whichever is closer to the work.

Minimum shape: see `schemas/receipt.schema.json`.

House rule, inherited from the host repository: **NO RECEIPT = NO CLAIM.**
