"""Single governed-state head — an OPT-IN single-head path. 🔵 OBSERVED · NON_SOVEREIGN.

⚠️ SCOPE (peer-review): this ADDS a safe single-head construction; it does NOT close the
dual-heads gap as a system invariant. A TransactionRuntime built with store=None still keeps
its own head and can diverge from a separate Executor state_provider (see
test_e009_dual_heads_reproduced_without_store — kept green to document the live default-path
bug). Closing the invariant would require making the shared store the ONLY legal construction
(remove the state_provider/current_state_hash degrees of freedom, or gate the wiring). Not done.


E009 (autoresearch, dual-heads finding). Before this, the capability layer (Executor's
state_provider, E006) and the transaction layer (TransactionRuntime.current_state_hash,
E008) each held their OWN notion of "the current governed state." They could diverge:
a committed transition moved one head to G1 while the other still reported G0, so a κ
minted for the stale G0 executed against a moved world. That kept χ_med INCOMPLETE —
two sources of truth is one too many.

GovernedStore is the single authoritative head. Both layers DERIVE from it (same
anti-vacuity discipline as E006: don't hold your own copy, read the one root). The head
advances only through a committed transition; nothing else may set it on the governed path.

In-memory MVP; the durable single-transactional-store substrate (state+receipt+marker in
one atomic boundary) is the production form — the same storage-boundary question E008 defers.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class GovernedStore:
    """One authoritative governed-state head. Read by every layer; advanced only by commit."""
    _head: str

    def head(self) -> str:
        return self._head

    def advance(self, new_head: str) -> None:
        """Move the single head forward. Called by the committed-transition path only."""
        self._head = new_head
