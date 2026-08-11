"""Falsifiers for the Constraint Dividend. Each attacks one of the three
laws, plus the pinned-context persistence claim."""
from __future__ import annotations

import dataclasses
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import goblin_grammar as gg
from goblin_grammar import (
    EMISSION_KINDS,
    GoblinContext,
    GoblinEmission,
    route,
    to_candidate_packet,
    validate_emission_dict,
)


def _e(kind="HYPOTHESIS", conf=0.5, refs=(), **kw):
    return GoblinEmission("e1", kind, "payload", evidence_refs=refs,
                          confidence=conf, **kw)


# ── law 1: the closed grammar — illegal rows are never scored ───────────

@pytest.mark.parametrize("illegal", [
    "ANSWER", "EXECUTE_ACTION", "ADMIT", "FACT", "TRUTH", "COMMAND",
    "observation",   # case is part of the grammar; near-misses rejected
])
def test_outside_grammar_is_unconstructible(illegal):
    with pytest.raises(ValueError, match="E_OUTSIDE_GRAMMAR"):
        _e(kind=illegal)


def test_grammar_is_exactly_five_kinds():
    """The closure IS the constitutional object. Extension requires a
    GRAMMAR_VERSION bump — this count fails on silent widening."""
    assert EMISSION_KINDS == {"OBSERVATION", "HYPOTHESIS", "COUNTEREXAMPLE",
                              "REQUEST_WITNESS", "PROPOSAL"}
    assert len(EMISSION_KINDS) == 5


def test_constraint_dividend_no_posthoc_parsing_needed():
    """Every constructible emission is already well-typed: the dividend
    is that validation happened at the boundary, so downstream consumers
    never meet a malformed utterance."""
    for kind in sorted(EMISSION_KINDS):
        refs = ("exhibit://x",) if kind == "OBSERVATION" else ()
        e = _e(kind=kind, refs=refs)
        assert e.kind in EMISSION_KINDS       # trivially — by construction


# ── law 1b: authority unrepresentable, wire and type ────────────────────

def test_emission_type_has_no_authority_surface():
    fields = {f.name for f in dataclasses.fields(GoblinEmission)}
    forbidden = {"authority", "admit", "execute", "act", "mint_capability",
                 "ledger_append", "commit", "device_action"}
    assert forbidden.isdisjoint(fields)       # boundary, not vocabulary
    with pytest.raises(TypeError):
        _e(authority=1)                        # type: ignore[arg-type]


@pytest.mark.parametrize("banned", sorted(gg._FORBIDDEN_FIELDS))
def test_wire_schema_rejects_authority_by_name(banned):
    with pytest.raises(ValueError, match="E_AUTHORITY_INJECTION"):
        validate_emission_dict({"emission_id": "e", "kind": "PROPOSAL",
                                "payload": "p", banned: True})


def test_wire_schema_rejects_unknown_fields_never_ignores():
    with pytest.raises(ValueError, match="E_UNKNOWN_FIELDS"):
        validate_emission_dict({"emission_id": "e", "kind": "PROPOSAL",
                                "payload": "p", "sovereign_hint": 1})


# ── law 2: confidence > tau ⊬ ADMIT — at ANY tau ───────────────────────

def test_confidence_is_routing_never_authority():
    e = _e(kind="PROPOSAL", conf=1.0)          # maximum confidence
    r = route(e, tau=0.5)
    assert r["route"] == "local_handler_eligible"
    assert r["route"] in gg.ROUTE_CODOMAIN
    # the codomain simply does not contain admission:
    assert not any(w in gg.ROUTE_CODOMAIN
                   for w in ("ADMIT", "admit", "execute", "act"))


def test_low_confidence_escalates_high_confidence_stays_local():
    assert route(_e(conf=0.2), tau=0.5)["route"] == "escalate"
    assert route(_e(conf=0.9), tau=0.5)["route"] == "local_handler_eligible"


def test_even_certainty_produces_only_a_proposal():
    e = _e(kind="PROPOSAL", conf=1.0)
    packet = to_candidate_packet(e)
    assert packet["status"] == "PROPOSED"      # the only status it can have
    assert "authority" not in packet and "admit" not in packet
    assert packet["routing_confidence"] == 1.0  # travels as a LABEL only


# ── law 3: grounding — weight-memory cannot masquerade as observation ───

def test_ungrounded_observation_is_unconstructible():
    with pytest.raises(ValueError, match="E_UNGROUNDED_OBSERVATION"):
        _e(kind="OBSERVATION", refs=())


def test_grounded_observation_constructs():
    e = _e(kind="OBSERVATION", refs=("exhibit://run-7/event/3",))
    assert e.evidence_refs == ("exhibit://run-7/event/3",)


def test_honest_downgrade_unreferenced_claim_becomes_hypothesis():
    """The escape path is typed: content without evidence may still enter
    the Garden — as HYPOTHESIS, which is what it actually is. And the
    grounding law survives mutation: stripping evidence from an
    OBSERVATION re-validates and raises — you cannot de-ground a claim
    and keep its label."""
    h = _e(kind="HYPOTHESIS", refs=())         # fine: speculation is free
    assert h.kind == "HYPOTHESIS"
    e = _e(kind="OBSERVATION", refs=("r1",))
    with pytest.raises(ValueError, match="E_UNGROUNDED_OBSERVATION"):
        dataclasses.replace(e, evidence_refs=())   # the law holds under replace
    # the honest route down is explicit and changes the LABEL too:
    assert e.as_hypothesis().kind == "HYPOTHESIS"


# ── PROPOSAL is the only door to the trellis ────────────────────────────

@pytest.mark.parametrize("kind", ["HYPOTHESIS", "COUNTEREXAMPLE",
                                  "REQUEST_WITNESS"])
def test_only_proposals_become_candidate_packets(kind):
    with pytest.raises(ValueError, match="E_NOT_A_PROPOSAL"):
        to_candidate_packet(_e(kind=kind))


def test_observation_is_evidence_not_candidate():
    e = _e(kind="OBSERVATION", refs=("r1",))
    with pytest.raises(ValueError, match="E_NOT_A_PROPOSAL"):
        to_candidate_packet(e)


# ── pinned context: structurally persistent ────────────────────────────

PIN = {"schema": "GOBLIN_GRAMMAR_V1", "tool_vocabulary": ("lookup",),
       "a": 0, "output_contract": "five kinds",
       "prohibited_crossings": ("goblin->lease",)}


def test_pinned_survives_any_eviction_sequence():
    ctx = GoblinContext(pinned=PIN, capacity=3)
    for i in range(100):                       # heavy pressure
        ctx.push(f"obs-{i}")
    assert len(ctx.sliding) == 3               # window slid
    assert ctx.sliding == ("obs-97", "obs-98", "obs-99")
    assert ctx.pinned["a"] == 0                # constitution never left
    assert ctx.pinned["output_contract"] == "five kinds"


def test_pin_requires_the_full_constitutional_set():
    with pytest.raises(ValueError, match="E_PIN_INCOMPLETE"):
        GoblinContext(pinned={"schema": "x", "a": 0}, capacity=3)


def test_pinned_authority_must_be_zero():
    with pytest.raises(ValueError, match="E_PINNED_AUTHORITY_NONZERO"):
        GoblinContext(pinned={**PIN, "a": 1}, capacity=3)


def test_no_public_eviction_or_mutation_path_over_pinned():
    ctx = GoblinContext(pinned=PIN, capacity=3)
    names = {n for n in dir(ctx) if not n.startswith("_")}
    for banned in ("evict_pinned", "unpin", "set_pinned", "clear"):
        assert banned not in names
    ctx.pinned["a"] = 1                        # mutate the COPY
    assert ctx.pinned["a"] == 0                # original unreachable


# ── determinism ─────────────────────────────────────────────────────────

def test_deterministic():
    a = gg.canon(to_candidate_packet(_e(kind="PROPOSAL", conf=0.7)))
    b = gg.canon(to_candidate_packet(_e(kind="PROPOSAL", conf=0.7)))
    assert a == b
