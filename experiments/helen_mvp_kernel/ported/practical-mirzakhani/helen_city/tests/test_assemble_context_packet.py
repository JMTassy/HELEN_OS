"""
Tests for assemble_context_packet.py

Invariants proven here:
  T1. Determinism: same inputs → identical packet_hash (bit-for-bit)
  T2. Stability under corpus permutation: order of input objects does not affect output
  T3. core_now dominance: a core_now thread beats a lexically closer non-core_now thread
  T4. Exactly one object per slot type
  T5. next_action coherent with corpus (sourced from a real core_now thread)
  T6. authority is always "NONE"
  T7. Zero side effects: corpus objects unchanged after call

Failure modes that must be impossible:
  - Two objects of the same type in one packet
  - authority != "NONE"
  - packet_hash changes across runs on same inputs
  - corpus mutation
"""
from __future__ import annotations

import copy
import hashlib
import json
import random
from typing import Any, Dict, List

import pytest

from helen_city.knowledge.assemble_context_packet import (
    ContextPacket,
    assemble_context_packet,
)


# ── Minimal registry fixture ──────────────────────────────────────────────────


def _make_object(
    id: str,
    object_type: str,
    title: str,
    salience_now: str = "active_supporting",
    priority: str = "medium",
    description: str = "",
    relevance: str = "",
    links: list = None,
    source_of_truth: str = "human_curated",
    authority_class: str = "non_sovereign",
    helen_stance: str = "moderate_interest",
    status: str = "active",
    district: str = "",
) -> Dict[str, Any]:
    return {
        "id": id,
        "object_type": object_type,
        "title": title,
        "description": description,
        "relevance": relevance,
        "salience_now": salience_now,
        "priority": priority,
        "links": links or [],
        "source_of_truth": source_of_truth,
        "authority_class": authority_class,
        "helen_stance": helen_stance,
        "status": status,
        "district": district,
    }


MINIMAL_CORPUS: List[Dict[str, Any]] = [
    _make_object(
        "law.reducer",
        "TOWN_LAW",
        "Only Reducer May Mutate State",
        salience_now="core_now",
        priority="critical",
        description="Reducer is sole authority. No bypass allowed.",
        authority_class="sovereign",
        helen_stance="deep_helen_interest",
        source_of_truth="human_curated",
    ),
    _make_object(
        "district.companion",
        "DISTRICT_PROFILE",
        "Companion District",
        salience_now="core_now",
        description="Memory-backed cognitive continuity",
        district="Companion",
        helen_stance="deep_helen_interest",
    ),
    _make_object(
        "project.helen_os",
        "PROJECT_PROFILE",
        "HELEN OS",
        salience_now="core_now",
        priority="critical",
        description="Constitutional kernel for governed AI autonomy",
        helen_stance="deep_helen_interest",
        source_of_truth="human_curated",
    ),
    _make_object(
        "thread.init_wedge",
        "CANONICAL_THREAD_NOTE",
        "Prove /init HELEN after interruption",
        salience_now="core_now",
        priority="critical",
        description="Boot wedge that reconstructs HELEN state from corpus",
        relevance="Proves recovery. Real sessions not yet injected.",
        links=["project.helen_os", "law.reducer"],
        helen_stance="deep_helen_interest",
        source_of_truth="human_curated",
    ),
    _make_object(
        "topic.memory_spine",
        "RESEARCH_TOPIC",
        "Memory Spine Architecture",
        salience_now="active_supporting",
        description="Structured corpus for boot context",
        helen_stance="deep_helen_interest",
    ),
]

# An extra thread that is lexically close but NOT core_now
EXTRA_THREAD_NOT_CORE_NOW: Dict[str, Any] = _make_object(
    "thread.conquest_ui",
    "CANONICAL_THREAD_NOTE",
    "CONQUEST UI MVP",
    salience_now="watchlist",
    priority="medium",
    description="HELEN OS init wedge prove recovery after interruption boot context",
    relevance="Lexically close to /init but low salience",
    helen_stance="moderate_interest",
    source_of_truth="human_curated",
)


# ── T1: Determinism ───────────────────────────────────────────────────────────


def test_t1_same_inputs_same_packet_hash():
    """T1: Running assemble_context_packet twice on identical inputs → same packet_hash."""
    objects = copy.deepcopy(MINIMAL_CORPUS)
    p1 = assemble_context_packet("prove init helen after interruption", "companion", objects)
    p2 = assemble_context_packet("prove init helen after interruption", "companion", objects)
    assert p1.packet_hash == p2.packet_hash, (
        f"Hash drift detected: {p1.packet_hash} != {p2.packet_hash}"
    )


def test_t1_twenty_runs_identical_hash():
    """T1 extended: 20 runs → all packet_hashes identical."""
    objects = copy.deepcopy(MINIMAL_CORPUS)
    hashes = [
        assemble_context_packet("init helen boot state", "companion", objects).packet_hash
        for _ in range(20)
    ]
    assert len(set(hashes)) == 1, f"Drift across 20 runs: {set(hashes)}"


# ── T2: Stability under permutation ──────────────────────────────────────────


def test_t2_corpus_permutation_stable():
    """T2: Shuffling the input objects list does not change the output packet."""
    objects = copy.deepcopy(MINIMAL_CORPUS)
    p_original = assemble_context_packet("init helen", "companion", objects)

    shuffled = copy.deepcopy(MINIMAL_CORPUS)
    random.seed(42)
    random.shuffle(shuffled)
    p_shuffled = assemble_context_packet("init helen", "companion", shuffled)

    assert p_original.packet_hash == p_shuffled.packet_hash, (
        "Packet changed under corpus permutation — scoring is not deterministic"
    )


def test_t2_five_permutations_identical():
    """T2 extended: 5 different random shuffles → same packet_hash."""
    hashes = []
    for seed in range(5):
        objects = copy.deepcopy(MINIMAL_CORPUS)
        random.seed(seed)
        random.shuffle(objects)
        p = assemble_context_packet("init helen boot", "companion", objects)
        hashes.append(p.packet_hash)
    assert len(set(hashes)) == 1, f"Permutation instability: {set(hashes)}"


# ── T3: core_now dominance ────────────────────────────────────────────────────


def test_t3_core_now_thread_beats_lexically_similar_watchlist():
    """
    T3: A core_now thread wins over a lexically closer watchlist thread.

    EXTRA_THREAD_NOT_CORE_NOW has the query words in its description,
    but salience_now=watchlist. The core_now thread must still win.
    """
    objects = copy.deepcopy(MINIMAL_CORPUS) + [copy.deepcopy(EXTRA_THREAD_NOT_CORE_NOW)]
    p = assemble_context_packet("init helen boot prove recovery", "companion", objects)

    assert p.active_thread.id == "thread.init_wedge", (
        f"core_now thread lost to {p.active_thread.id} (salience={p.active_thread.salience_now}). "
        "Salience weight is too low — fix weights.py, not the test."
    )
    assert p.active_thread.salience_now == "core_now"


def test_t3_next_action_from_core_now_not_watchlist():
    """T3: next_action.source_id must point to a core_now thread."""
    objects = copy.deepcopy(MINIMAL_CORPUS) + [copy.deepcopy(EXTRA_THREAD_NOT_CORE_NOW)]
    p = assemble_context_packet("conquest ui", "companion", objects)

    assert p.next_action.source_id != "thread.conquest_ui", (
        "next_action pointed to a watchlist thread even though core_now threads exist"
    )
    assert p.next_action.source_id == "thread.init_wedge"


# ── T4: Exactly one object per slot type ─────────────────────────────────────


def test_t4_exactly_one_object_per_slot():
    """T4: Each slot contains exactly one object. No slot type appears twice."""
    objects = copy.deepcopy(MINIMAL_CORPUS)
    p = assemble_context_packet("boot helen", "companion", objects)

    slots_types = [
        p.law.object_type,
        p.district.object_type,
        p.project.object_type,
        p.active_thread.object_type,
        p.topic.object_type,
    ]

    assert p.law.object_type == "TOWN_LAW"
    assert p.district.object_type == "DISTRICT_PROFILE"
    assert p.project.object_type == "PROJECT_PROFILE"
    assert p.active_thread.object_type == "CANONICAL_THREAD_NOTE"
    assert p.topic.object_type == "RESEARCH_TOPIC"

    # No duplicate ids across slots
    slot_ids = [p.law.id, p.district.id, p.project.id, p.active_thread.id, p.topic.id]
    assert len(slot_ids) == len(set(slot_ids)), f"Duplicate ids in packet: {slot_ids}"


def test_t4_duplicate_type_objects_still_one_per_slot():
    """T4: Even with multiple objects of the same type, only one per slot is selected."""
    extra_law = _make_object(
        "law.memory", "TOWN_LAW", "Memory Must Be Backed",
        salience_now="core_now", priority="high",
        source_of_truth="human_curated",
    )
    extra_thread = _make_object(
        "thread.temple", "CANONICAL_THREAD_NOTE", "Temple Consensus Loop",
        salience_now="core_now", priority="high",
        source_of_truth="human_curated",
        helen_stance="deep_helen_interest",
    )
    objects = copy.deepcopy(MINIMAL_CORPUS) + [extra_law, extra_thread]
    p = assemble_context_packet("temple consensus", "companion", objects)

    # Still exactly one of each type
    assert p.law.object_type == "TOWN_LAW"
    assert p.active_thread.object_type == "CANONICAL_THREAD_NOTE"
    slot_ids = [p.law.id, p.district.id, p.project.id, p.active_thread.id, p.topic.id]
    assert len(slot_ids) == len(set(slot_ids)), f"Duplicate ids: {slot_ids}"


# ── T5: next_action coherence ─────────────────────────────────────────────────


def test_t5_next_action_traceable_to_corpus():
    """T5: next_action.source_id must exist in the input objects."""
    objects = copy.deepcopy(MINIMAL_CORPUS)
    p = assemble_context_packet("what should helen do now", "companion", objects)

    corpus_ids = {obj["id"] for obj in objects}
    assert p.next_action.source_id in corpus_ids, (
        f"next_action.source_id={p.next_action.source_id!r} not found in corpus"
    )


def test_t5_next_action_what_matches_thread_title():
    """T5: next_action.what must equal the title of the thread in the corpus."""
    objects = copy.deepcopy(MINIMAL_CORPUS)
    p = assemble_context_packet("next step helen", "companion", objects)

    source = next(o for o in objects if o["id"] == p.next_action.source_id)
    assert p.next_action.what == source["title"], (
        f"next_action.what={p.next_action.what!r} does not match "
        f"corpus title={source['title']!r}"
    )


# ── T6: authority == "NONE" ───────────────────────────────────────────────────


def test_t6_packet_authority_is_none():
    """T6: authority must always be 'NONE'. No exception."""
    objects = copy.deepcopy(MINIMAL_CORPUS)
    p = assemble_context_packet("anything", "companion", objects)
    assert p.authority == "NONE", f"authority={p.authority!r} — must always be NONE"


def test_t6_next_action_authority_is_none():
    """T6: next_action.authority must also be 'NONE'."""
    objects = copy.deepcopy(MINIMAL_CORPUS)
    p = assemble_context_packet("anything", "companion", objects)
    assert p.next_action.authority == "NONE"


# ── T7: Zero side effects ─────────────────────────────────────────────────────


def test_t7_corpus_unchanged_after_call():
    """T7: The input objects list and all dicts must be unmodified after assembly."""
    objects = copy.deepcopy(MINIMAL_CORPUS)
    snapshot_before = json.dumps(objects, sort_keys=True)

    assemble_context_packet("init helen", "companion", objects)

    snapshot_after = json.dumps(objects, sort_keys=True)
    assert snapshot_before == snapshot_after, "Corpus was mutated by assemble_context_packet"


def test_t7_multiple_calls_no_mutation():
    """T7: Calling assemble_context_packet N times never mutates the corpus."""
    objects = copy.deepcopy(MINIMAL_CORPUS)
    snapshot = json.dumps(objects, sort_keys=True)

    for _ in range(5):
        assemble_context_packet("boot helen recovery", "companion", objects)

    assert json.dumps(objects, sort_keys=True) == snapshot


# ── T8: packet_hash integrity ─────────────────────────────────────────────────


def test_t8_packet_hash_covers_all_fields():
    """T8: Changing any field in the packet invalidates the hash."""
    objects = copy.deepcopy(MINIMAL_CORPUS)
    p = assemble_context_packet("init helen", "companion", objects)

    # Recompute hash manually and confirm it matches
    d = p.as_dict()
    without_hash = {k: v for k, v in d.items() if k != "packet_hash"}
    canonical = json.dumps(without_hash, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode("utf-8")
    expected = "sha256:" + hashlib.sha256(canonical).hexdigest()
    assert p.packet_hash == expected, "packet_hash does not match recomputed value"


def test_t8_different_request_different_hash():
    """T8: Different request strings produce different packet_hashes."""
    objects = copy.deepcopy(MINIMAL_CORPUS)
    p1 = assemble_context_packet("init helen", "companion", objects)
    p2 = assemble_context_packet("temple consensus loop", "temple", objects)
    assert p1.packet_hash != p2.packet_hash


# ── T9: Empty / edge cases ────────────────────────────────────────────────────


def test_t9_empty_corpus_returns_empty_slots():
    """T9: Empty corpus returns packet with empty-slot defaults, no crash."""
    p = assemble_context_packet("anything", "companion", [])
    assert p.law.id == "none"
    assert p.district.id == "none"
    assert p.project.id == "none"
    assert p.active_thread.id == "none"
    assert p.topic.id == "none"
    assert p.authority == "NONE"
    assert p.next_action.source_id == "none"


def test_t9_missing_one_type_no_crash():
    """T9: If one type is absent, remaining slots are filled correctly."""
    # Remove RESEARCH_TOPIC from corpus
    objects = [o for o in copy.deepcopy(MINIMAL_CORPUS) if o["object_type"] != "RESEARCH_TOPIC"]
    p = assemble_context_packet("init helen", "companion", objects)
    assert p.topic.id == "none"
    # Other slots still populated
    assert p.law.id != "none"
    assert p.project.id != "none"
