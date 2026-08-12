"""Falsifiers for the Causal Commit Cell — the arrow of time, negative
receipts, and the local/global witness split.
"""
from __future__ import annotations

import sys
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import causal_commit_cell as ccc
from causal_commit_cell import (
    CommitCell,
    amend,
    commit_cell,
    replay_chain,
    rewrite,
)


def _cell(cid="c1", before="root:s0", after="root:s1", t_auth=10,
          t_eff=15, delta=0.0, **over):
    base = dict(cell_id=cid, state_root_before=before,
                state_root_after=after, transformation="send_followup",
                evidence_closure=("transcript#1042",),
                policy_version="v1", lease_ref="L1",
                admission_ref="adm:jm:1", t_authorized=t_auth,
                t_effect=t_eff, quantity_delta=delta)
    base.update(over)
    return CommitCell(**base)


# ── the atom commits, and refusals are negative receipts ───────────────

def test_a_complete_cell_commits_with_a_local_receipt():
    r = commit_cell(_cell())
    assert r["verdict"] == "COMMITTED" and r["receipt"]
    assert r["scope"] == "LOCAL_TRANSITION_WITNESS_ONLY"


def test_missing_authority_and_open_evidence_are_negative_receipts():
    no_auth = commit_cell(_cell(lease_ref=""))
    assert no_auth["verdict"] == "REJECTED"
    assert no_auth["reason"] == "E_NO_AUTHORITY"
    assert no_auth["mutates"] is False          # audit yes, state no
    assert no_auth["negative_receipt"]           # the refusal is remembered
    open_ev = commit_cell(_cell(evidence_closure=()))
    assert open_ev["reason"] == "E_OPEN_EVIDENCE"
    assert open_ev["mutates"] is False


# ── the institutional arrow of time ────────────────────────────────────

def test_authority_arriving_after_the_effect_is_refused():
    r = commit_cell(_cell(t_auth=20, t_eff=15))
    assert r["verdict"] == "REJECTED"
    assert r["reason"] == "E_RETROACTIVE_AUTHORITY"
    assert "cannot manufacture earlier missing authority" in r["law"]


def test_amend_appends_and_cites_never_erases():
    original = commit_cell(_cell())
    fix = _cell(cid="c1-fix", before="root:s1", after="root:s1b",
                supersedes=original["receipt"])
    a = amend(original["receipt"], fix)
    assert a["verdict"] == "COMMITTED"
    assert a["amends"] == original["receipt"]
    assert a["original_status"] == "SUPERSEDED_NOT_ERASED"
    # an amendment that does not cite is a rewrite wearing a coat
    uncited = _cell(cid="c1-sneak", before="root:s1", after="root:s1c")
    assert amend(original["receipt"], uncited)["reason"] == \
        "E_AMENDMENT_MUST_CITE"


def test_rewrite_is_refused_unconditionally():
    r = rewrite((), 0, _cell())
    assert r["verdict"] == "REFUSED" and r["reason"] == "E_HISTORY_REWRITE"
    assert "arrow of time" in r["law"]


# ── receipt is local; replay + conservation is global ──────────────────

def _chain(deltas, roots=None):
    roots = roots or ["s0", "s1", "s2"]
    cells = tuple(
        _cell(cid=f"c{i}", before=f"root:{roots[i]}",
              after=f"root:{roots[i + 1]}", delta=d)
        for i, d in enumerate(deltas))
    return tuple(commit_cell(c) for c in cells), cells


def test_locally_receipted_chain_can_be_globally_invalid():
    committed, cells = _chain([-60.0, -60.0])
    assert all(r["verdict"] == "COMMITTED" for r in committed)  # local: fine
    g = replay_chain(committed, cells, conserved_budget=100.0)
    assert g["verdict"] == "E_GLOBAL_COMPOSITION_INVALID"
    assert g["total_delta"] == -120.0
    assert "locally valid receipts" in g["law"]


def test_broken_continuity_is_caught_despite_valid_receipts():
    committed, cells = _chain([-10.0, -10.0], roots=["s0", "s1", "s2"])
    torn = (cells[0], replace(cells[1], state_root_before="root:sX"))
    torn_committed = (committed[0], commit_cell(torn[1]))
    g = replay_chain(torn_committed, torn, conserved_budget=100.0)
    assert g["verdict"] == "E_BROKEN_CONTINUITY"


def test_an_unreceipted_link_sinks_the_chain():
    committed, cells = _chain([-10.0, -10.0])
    forged = (committed[0], {"verdict": "REJECTED", "cell_id": "c1"})
    assert replay_chain(forged, cells, 100.0)["verdict"] == \
        "E_UNRECEIPTED_LINK"


def test_a_lawful_chain_is_globally_witnessed():
    committed, cells = _chain([-30.0, -40.0])
    g = replay_chain(committed, cells, conserved_budget=100.0)
    assert g["verdict"] == "GLOBALLY_WITNESSED" and g["links"] == 2


# ── determinism ─────────────────────────────────────────────────────────

def test_deterministic():
    assert ccc.canon(commit_cell(_cell())) == ccc.canon(commit_cell(_cell()))
