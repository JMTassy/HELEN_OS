"""HELEN Video Admissibility Stack — NON_SOVEREIGN / NO_SHIP / EXPERIMENTAL.

Ralph imagines videos.
HELEN admits videos.
The ledger remembers admitted media.

Layer order (strict):
  video_ledger    — append-only hash-chained truth record
  admissibility_gate — receipt-required gate (no receipt → REJECT)
  ralph_generator — candidate producer only (stub; cannot deliver)
"""
