"""Phase A item 4, adversarially tested: an edited event breaks the
chain arithmetically; tail truncation survives verify_chain and dies
at the anchor; raw values never enter; the module exports no delete
verb; and no operation mutates its input.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import audit_runtime as ar
from audit_runtime import (
    anchor,
    append,
    boot,
    chain_receipt,
    verify_against_anchor,
    verify_chain,
)


def _chain(n=4):
    s = boot()
    for i in range(n):
        s, r = append(s, "A", {"kind": "WRITE", "actor": "user",
                               "key": f"k{i}",
                               "value_digest": f"d{i}"})
        assert r["ok"] is True
    return s


# ── append discipline ──────────────────────────────────────────────────

def test_an_unattributed_event_is_refused():
    s = boot()
    _, r = append(s, "A", {"kind": "WRITE"})
    assert r["reason"] == "E_UNATTRIBUTED_EVENT"
    _, r2 = append(s, "A", {"actor": "user"})
    assert r2["reason"] == "E_UNATTRIBUTED_EVENT"


def test_raw_values_never_enter_the_audit_log():
    s = boot()
    _, r = append(s, "A", {"kind": "WRITE", "actor": "u",
                           "value": {"secret": "x"}})
    assert r["reason"] == "E_RAW_VALUE_IN_AUDIT"


def test_chains_are_per_tenant():
    s = boot()
    s, _ = append(s, "A", {"kind": "K", "actor": "u"})
    s, _ = append(s, "B", {"kind": "K", "actor": "u"})
    assert len(s["chains"]["A"]) == len(s["chains"]["B"]) == 1
    assert s["chains"]["A"][0]["prev"] == ar.GENESIS
    assert s["chains"]["B"][0]["prev"] == ar.GENESIS


def test_append_only_is_an_api_fact():
    """The module exports no update and no delete — asserted, not
    promised."""
    verbs = [n for n in dir(ar) if not n.startswith("_")]
    assert not any("delete" in v or "update" in v or "remove" in v
                   for v in verbs)


# ── tampering is arithmetic ────────────────────────────────────────────

def test_an_intact_chain_verifies():
    v = verify_chain(_chain(), "A")
    assert v["intact"] is True and v["length"] == 4


def test_an_edited_event_breaks_the_chain_at_its_seq():
    s = _chain()
    chain = list(s["chains"]["A"])
    ev = dict(chain[1])
    ev["key"] = "k1_tampered"                # edit without re-hashing
    chain[1] = ev
    tampered = dict(s)
    tampered["chains"] = {**s["chains"], "A": tuple(chain)}
    v = verify_chain(tampered, "A")
    assert v["intact"] is False
    assert v["reason"] == "E_CHAIN_BROKEN"
    assert v["at_seq"] == 2


def test_a_rehashed_edit_still_breaks_the_next_link():
    """Re-hashing the edited event does not help: the successor's
    prev pointer no longer matches."""
    s = _chain()
    chain = list(s["chains"]["A"])
    body = {k: v for k, v in chain[1].items() if k != "hash"}
    body["key"] = "k1_tampered"
    chain[1] = {**body, "hash": ar._sha(body)}
    tampered = dict(s)
    tampered["chains"] = {**s["chains"], "A": tuple(chain)}
    v = verify_chain(tampered, "A")
    assert v["intact"] is False
    assert v["at_seq"] == 3                  # the break moves DOWN the chain


# ── truncation dies at the anchor ──────────────────────────────────────

def test_tail_truncation_survives_verify_chain():
    """The honest limit: a cut tail is internally consistent."""
    s = _chain()
    cut = dict(s)
    cut["chains"] = {**s["chains"], "A": s["chains"]["A"][:2]}
    assert verify_chain(cut, "A")["intact"] is True


def test_the_anchor_catches_the_truncation():
    s = _chain()
    a = anchor(s, "A")
    assert a["anchored"] is True and a["length"] == 4
    cut = dict(s)
    cut["chains"] = {**s["chains"], "A": s["chains"]["A"][:2]}
    v = verify_against_anchor(cut, "A", a)
    assert v["intact"] is False
    assert v["reason"] == "E_CHAIN_TRUNCATED"
    assert v["found_length"] == 2


def test_growth_after_the_anchor_is_lawful():
    s = _chain()
    a = anchor(s, "A")
    s, _ = append(s, "A", {"kind": "K", "actor": "u"})
    v = verify_against_anchor(s, "A", a)
    assert v["intact"] is True and v["grew_by"] == 1


def test_an_unanchored_chain_is_unanchored_not_safe():
    s = _chain()
    v = verify_against_anchor(s, "A", {"anchored": False})
    assert v["intact"] is None
    assert v["reason"] == "E_UNANCHORED"


# ── the RDK recipe and purity ──────────────────────────────────────────

def test_the_chain_carries_its_own_rederivation_recipe():
    v = chain_receipt(_chain(), "A")
    assert v["rederivable"] is True
    assert "sha256" in v["derivation_recipe"]
    assert v["result"]["intact"] is True


def test_no_operation_mutates_its_input_state():
    s = _chain()
    frozen = ar.canon(s)
    append(s, "A", {"kind": "K", "actor": "u"})
    verify_chain(s, "A")
    anchor(s, "A")
    assert ar.canon(s) == frozen


def test_deterministic_replay():
    assert ar.canon(_chain()) == ar.canon(_chain())
