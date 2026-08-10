"""Internal transaction integrity — crash-recovery convergence. 🔵 OBSERVED · NON_SOVEREIGN.

E008 (extends E005 write-ahead intent). The kernel question is no longer "was the effect
authorized?" but: after any crash point, can the system converge to ONE unambiguous
governed history? Target:

    Recover(τ) ∈ {NO_COMMIT, ONE_COMMITTED}     never AMBIGUOUS_HALF_STATE

Four distinct propositions — do NOT collapse them:
    P = intent persisted · E = effect observed · R = evidence persisted · C = governed commit
    E ⊬ C · R ⊬ C · C ⇒ R      and      ΔG_governed ≠ 0 ⇒ C

Central discipline (same anti-vacuity law as HAL/κ): status="COMMITTED" ≠ Committed(τ).
Committed is DERIVED from durable facts, never read from the status field. Replay consumes
COMMITTED transitions only, so merely persisting an intent/receipt cannot change history.

SCOPE: internal governed state only. External effects (email/payment) obey ΔW ≠ 0 ⊬ ΔG ≠ 0
and need reconciliation, not this — see the physical-vs-governed distinction. In-memory MVP;
durable fsync WAL is the production substrate (E005 residual, unchanged).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Optional

from helen_os.ledger.hash_chain import canonical_json, sha256_hex

PREPARED, EXECUTED, EVIDENCED, COMMITTED, ABORTED = (
    "PREPARED", "EXECUTED", "EVIDENCED", "COMMITTED", "ABORTED",
)


def h_v(x) -> str:
    return sha256_hex(canonical_json(x))


@dataclass
class TransitionIntent:
    tx_id: str
    pre_state_hash: str
    effect_hash: str
    status: str = PREPARED
    post_state_hash: Optional[str] = None
    execution_receipt_hash: Optional[str] = None
    commit_marker: Optional[str] = None  # binds the receipt hash at commit time


@dataclass
class TransactionRuntime:
    """Minimal PREPARED→EXECUTED→EVIDENCED→COMMITTED machine with crash injection.
    `current_state_hash` is the authoritative governed-state hash source — unless a
    GovernedStore is bound (E009), in which case the SINGLE store head is authoritative
    and current_state_hash is kept in sync so the capability layer and the transaction
    layer read one root, not two."""
    current_state_hash: str
    store: object = None                          # E009: optional GovernedStore (single head)
    _txs: dict = field(default_factory=dict)      # tx_id -> TransitionIntent
    _committed_log: list = field(default_factory=list)  # ordered committed tx_ids (history)

    def __post_init__(self):
        if self.store is not None:                # store head wins on construction
            self.current_state_hash = self.store.head()

    def _head(self) -> str:
        return self.store.head() if self.store is not None else self.current_state_hash

    def _advance(self, new_head: str) -> None:
        self.current_state_hash = new_head
        if self.store is not None:                # advance the single head on execute
            self.store.advance(new_head)

    # ---- forward path (each step is a separate durable proposition) ----
    def prepare(self, tx_id: str, effect_hash: str) -> TransitionIntent:
        tx = TransitionIntent(tx_id, pre_state_hash=self._head(),
                              effect_hash=effect_hash)
        self._txs[tx_id] = tx
        return tx

    def execute(self, tx_id: str, mutation: Callable[[], str]) -> None:
        """Run the deterministic internal mutation; mutation() returns the new state hash."""
        tx = self._txs[tx_id]
        if tx.pre_state_hash != self._head():
            tx.status = ABORTED
            return
        new_hash = mutation()
        self._advance(new_hash)                   # E009: advance the single head
        tx.post_state_hash = new_hash
        tx.status = EXECUTED

    def evidence(self, tx_id: str) -> None:
        tx = self._txs[tx_id]
        if tx.status != EXECUTED:
            return
        tx.execution_receipt_hash = h_v(
            {"tx": tx_id, "pre": tx.pre_state_hash, "post": tx.post_state_hash,
             "effect": tx.effect_hash})
        tx.status = EVIDENCED

    def commit(self, tx_id: str) -> str:
        tx = self._txs[tx_id]
        if not self._commit_derivable(tx):
            return "COMMIT_REFUSED"
        if tx.commit_marker is not None:        # idempotent: already committed
            return "ALREADY_COMMITTED"
        tx.commit_marker = tx.execution_receipt_hash
        tx.status = COMMITTED
        self._committed_log.append(tx_id)
        return COMMITTED

    # ---- DERIVED committed predicate — never trusts tx.status ----
    def _commit_derivable(self, tx: TransitionIntent) -> bool:
        return (
            tx.execution_receipt_hash is not None
            and tx.post_state_hash is not None
            and tx.execution_receipt_hash == h_v(
                {"tx": tx.tx_id, "pre": tx.pre_state_hash, "post": tx.post_state_hash,
                 "effect": tx.effect_hash})
        )

    def is_committed(self, tx_id: str) -> bool:
        """Committed(τ) DERIVED from durable facts: valid receipt + bound commit marker.
        status='COMMITTED' alone is NOT trusted."""
        tx = self._txs.get(tx_id)
        if tx is None:
            return False
        return tx.commit_marker is not None and tx.commit_marker == tx.execution_receipt_hash \
            and self._commit_derivable(tx)

    # ---- recovery: converge to NO_COMMIT or ONE_COMMITTED, never half-state ----
    def recover(self, tx_id: str) -> str:
        tx = self._txs.get(tx_id)
        if tx is None:
            return "NO_COMMIT"
        # a durably-committed tx stays committed (idempotent)
        if self.is_committed(tx_id):
            return "COMMITTED_ONCE"
        # stale pre-state: another transition moved the world — never resume
        if tx.pre_state_hash != self._head() and tx.status in (PREPARED, ABORTED):
            tx.status = ABORTED
            return "STALE_PRE_STATE"
        # effect happened but no committed marker: do NOT auto-commit / fabricate a receipt
        if tx.status in (EXECUTED,):
            return "RECOVERY_REQUIRED"          # E=1,R=0 ⊬ C=1
        if tx.status in (EVIDENCED,):
            # receipt exists but not committed: revalidate before completing commit
            return self.commit(tx_id) if self._commit_derivable(tx) else "COMMIT_REFUSED"
        return "NO_COMMIT"

    # ---- replay reads committed history only ----
    def replay_committed(self) -> list:
        return [t for t in self._committed_log if self.is_committed(t)]
