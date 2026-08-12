"""The Causal Commit Cell — HELEN's constitutional atom, made real.

NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none.

Frame fact, witnessed 2026-08-12: the Architect lane reported commit
3e0e2b4 for this material; that object exists NOWHERE in the
repository (all branches fetched and searched). This module is the
first Causal Commit Cell on the source of truth. A reported hash is a
claim; only the ledger is law.

    CCC = one candidate transition bound to
          (state roots, evidence closure, policy, authority, effects,
           admitted receipt)

    HELEN is a governed history compiler:
    cognition may branch freely; history changes only through
    admissible causal commits.

The three laws the Director's recap adds, executable here:

  INSTITUTIONAL ARROW OF TIME   Later evidence cannot manufacture
      earlier missing authority. Authorization must precede effect
      (E_RETROACTIVE_AUTHORITY). A later cell may AMEND or SUPERSEDE —
      appending a correction that cites the original — but rewriting
      the original is refused (E_HISTORY_REWRITE). Append-only
      provenance and acyclic authority are two views of this one
      property.

  NEGATIVE RECEIPTS             A rejected commit writes an audit
      record and mutates nothing: the refusal is remembered, the
      state roots are untouched. Rejected promotions belong in audit
      history, never in governed state.

  RECEIPT IS LOCAL, REPLAY+CONSERVATION IS GLOBAL   A receipt
      witnesses ONE transition. A chain of individually receipted
      cells can still be globally invalid — broken state-root
      continuity, or a conservation law violated by the composition.
      replay_chain is the global composition witness; no local
      receipt can substitute for it.

Deterministic: time is passed in, no randomness, canonical JSON.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field, replace

LEDGER_LAW = ("cognition may branch freely; history changes only "
              "through admissible causal commits")


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


def canon_hash(obj) -> str:
    return hashlib.sha256(canon(obj).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class CommitCell:
    """One candidate transition. No field grants anything: the cell is
    a CANDIDATE until commit_cell() admits it, and the receipt lands on
    the returned record, never inside the candidate."""
    cell_id: str
    state_root_before: str
    state_root_after: str
    transformation: str
    evidence_closure: tuple            # refs; empty = open evidence
    policy_version: str
    lease_ref: str                     # scoped authority
    admission_ref: str                 # the principal's act
    t_authorized: int
    t_effect: int
    quantity_delta: float = 0.0        # for conservation accounting
    supersedes: str = ""               # cites an earlier receipt, if amending


def commit_cell(cell: CommitCell) -> dict:
    """The gate stack of the atom. Success mints the LOCAL witness."""
    if not cell.lease_ref or not cell.admission_ref:
        return _negative(cell, "E_NO_AUTHORITY")
    if cell.t_authorized > cell.t_effect:
        return _negative(cell, "E_RETROACTIVE_AUTHORITY",
                         law="later evidence cannot manufacture earlier "
                             "missing authority")
    if not cell.evidence_closure:
        return _negative(cell, "E_OPEN_EVIDENCE")
    return {"verdict": "COMMITTED",
            "receipt": canon_hash([cell.cell_id, cell.state_root_before,
                                   cell.state_root_after,
                                   cell.transformation, cell.lease_ref,
                                   cell.admission_ref, cell.t_effect]),
            "scope": "LOCAL_TRANSITION_WITNESS_ONLY",
            "cell_id": cell.cell_id,
            "mutates": True}


def _negative(cell: CommitCell, reason: str, law: str = "") -> dict:
    """The negative receipt: audit history gains a record; governed
    state gains nothing."""
    out = {"verdict": "REJECTED", "reason": reason,
           "negative_receipt": canon_hash(["REJECTED", cell.cell_id,
                                           reason]),
           "cell_id": cell.cell_id,
           "mutates": False,
           "note": "the refusal is remembered; the state is untouched"}
    if law:
        out["law"] = law
    return out


# ── the arrow of time: amend appends, rewrite refuses ───────────────────

def amend(original_receipt: str, correction: CommitCell) -> dict:
    """A later cell may compensate, amend, or supersede — citing the
    original. It never edits it."""
    if correction.supersedes != original_receipt:
        return {"verdict": "REFUSED", "reason": "E_AMENDMENT_MUST_CITE",
                "note": "an amendment that does not name what it "
                        "supersedes is a rewrite wearing a coat"}
    r = commit_cell(correction)
    if r["verdict"] != "COMMITTED":
        return r
    return {**r, "amends": original_receipt,
            "original_status": "SUPERSEDED_NOT_ERASED"}


def rewrite(ledger: tuple, index: int, replacement: CommitCell) -> dict:
    """The forbidden operation, present so the refusal is executable."""
    return {"verdict": "REFUSED", "reason": "E_HISTORY_REWRITE",
            "law": "append-only provenance and acyclic authority are "
                   "two views of the institutional arrow of time"}


# ── the global composition witness ──────────────────────────────────────

def replay_chain(committed: tuple, cells: tuple,
                 conserved_budget: float | None = None) -> dict:
    """receipt = local transition witness; replay + conservation =
    global composition witness. Checks (1) every cell carries a
    COMMITTED receipt, (2) state-root continuity after_i == before_i+1,
    (3) the conservation law over the whole chain."""
    for rec, cell in zip(committed, cells):
        if rec.get("verdict") != "COMMITTED" or \
                rec.get("cell_id") != cell.cell_id:
            return {"verdict": "E_UNRECEIPTED_LINK", "at": cell.cell_id}
    for a, b in zip(cells, cells[1:]):
        if a.state_root_after != b.state_root_before:
            return {"verdict": "E_BROKEN_CONTINUITY",
                    "between": (a.cell_id, b.cell_id),
                    "note": "each link locally receipted; the CHAIN "
                            "is still invalid"}
    total = sum(c.quantity_delta for c in cells)
    if conserved_budget is not None and abs(total) > conserved_budget:
        return {"verdict": "E_GLOBAL_COMPOSITION_INVALID",
                "total_delta": total, "budget": conserved_budget,
                "law": "locally valid receipts composed into a "
                       "globally invalid flow; only replay+conservation "
                       "witnesses the composition"}
    return {"verdict": "GLOBALLY_WITNESSED", "links": len(cells),
            "total_delta": total}
