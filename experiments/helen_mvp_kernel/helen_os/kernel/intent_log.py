"""Write-ahead intent log — ghost-execution detection. 🔵 OBSERVED · NON_SOVEREIGN.

E005 atomicity seam: capability invoke does check → consume → effect → receipt. A crash
BETWEEN effect and receipt yields ΔG≠0 with no receipt — a "ghost execution", no attacker
required. You cannot PREVENT a crash; you record intent BEFORE the effect so recovery can
DETECT the resulting ghost. This is the smallest write-ahead form:

    PREPARE(txn, effect_hash)   ← persisted BEFORE the effect runs
    effect()
    COMMIT(txn)                 ← recorded only after the receipt persists

Recovery scan: any txn PREPARED but not COMMITTED is a ghost candidate. The write-ahead
order is load-bearing — recording intent AFTER the effect would make a crash-between
invisible. New anti-collapse distinction (doctrine §13): execution ≠ committed governed state.

Detection, not prevention. Not a full transaction engine; a recoverable evidence trail.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Optional

from helen_os.ledger.hash_chain import canonical_json, sha256_hex


PREPARED, COMMITTED = "PREPARED", "COMMITTED"


@dataclass
class IntentLog:
    """Append-only intent trail. In this MVP it is in-memory; the production form
    is an fsync'd WAL file whose entries survive the crash they witness."""
    _entries: dict = field(default_factory=dict)  # txn_id -> {"status", "effect_hash"}

    def prepare(self, txn_id: str, effect_hash: str) -> None:
        # idempotent: re-preparing an existing txn does not erase its state
        self._entries.setdefault(txn_id, {"status": PREPARED, "effect_hash": effect_hash})

    def commit(self, txn_id: str) -> None:
        if txn_id in self._entries:
            self._entries[txn_id]["status"] = COMMITTED

    def status(self, txn_id: str) -> Optional[str]:
        e = self._entries.get(txn_id)
        return e["status"] if e else None


def detect_ghosts(log: IntentLog) -> list[str]:
    """Recovery scan: txns PREPARED but never COMMITTED = ghost executions."""
    return sorted(
        txn for txn, e in log._entries.items() if e["status"] == PREPARED
    )


def run_with_intent(
    log: IntentLog,
    txn_id: str,
    effect_hash: str,
    effect: Callable[[], None],
    *,
    crash_before_commit: bool = False,
) -> str:
    """Write-ahead wrapper: PREPARE → effect → COMMIT. crash_before_commit simulates a
    process death after the side effect but before the receipt/commit is durable.
    Returns final status of the txn as seen by a subsequent recovery scan."""
    log.prepare(txn_id, effect_hash)   # persisted BEFORE the effect — the load-bearing order
    effect()                           # governed side effect happens here (ΔG ≠ 0)
    if crash_before_commit:
        return log.status(txn_id)      # 💥 died before commit — intent left PREPARED
    log.commit(txn_id)                 # receipt persisted → intent cleared to COMMITTED
    return log.status(txn_id)
