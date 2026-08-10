"""Tests for the Board Memory falsifier itself.

The falsifier must be proven before it may judge: a harness that cannot
detect collapse would pass any believer. These tests pin (1) a perfect
pipeline scores clean, (2) collapse is detected AND attributed to the
right layer, (3) the baseline demonstrably fails the baits (the teeth),
(4) the scorer is deterministic.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import baseline_rag
import scorer

GOLD = json.loads((HERE / "fixtures" / "gold_v0.json").read_text(encoding="utf-8"))
CORPUS = json.loads((HERE / "fixtures" / "corpus_v0.json").read_text(encoding="utf-8"))


def _answer(aid, statement, final, extractor, verifier, gate, prov):
    return {
        "answer_id": aid, "statement": statement, "final_status": final,
        "layers": {"extractor_status": extractor, "verifier_verdict": verifier,
                   "gate_verdict": gate},
        "provenance": prov,
    }


def _out(answers):
    return {"schema_name": "BOARD_MEMORY_OUTPUT_V1", "schema_version": "1.0.0",
            "pipeline_id": "handcrafted", "corpus_id": "board_corpus_v0",
            "answers": answers}


PERFECT = _out([
    _answer("A1", "The board approved allocating €200k to Project Y, vote 4-1.",
            "decision", "decided", "PASS", "ADMIT", ["D1"]),
    _answer("A2", "Alice will draft the Corsica partnership contract by Friday.",
            "commitment", "committed", "PASS", "ADMIT", ["C1"]),
    _answer("A3", "Who owns the data-center lease renewal?",
            "open_question", "open", "PASS", "HOLD", ["M2"]),
    _answer("A4", "Karim said the mayor's office already signed off on the site permit.",
            "abstain", "unknowable", "UNKNOWN", "HOLD", ["M5"]),
])


def test_perfect_pipeline_scores_clean():
    r = scorer.score(GOLD, PERFECT)
    m = r["metrics"]
    assert m["e_collapse"] == 0.0
    assert m["precision"] == 1.0
    assert m["recall"] == 1.0
    assert m["p_prov"] == 1.0
    assert m["c_abstain"] == 1.0
    assert m["bait_catch_rate"] == 1.0


def test_collapse_attributed_to_extractor():
    out = _out([_answer(
        "A1", "Allocate €500k to Project X next quarter.",
        "decision", "decided", "PASS", "ADMIT", ["M1"])])
    r = scorer.score(GOLD, out)
    assert r["metrics"]["e_collapse"] > 0
    assert r["metrics"]["e_collapse_by_layer"]["extractor"] == 1
    assert r["collapse_events"][0]["bait_class"] == "proposal_as_decision"


def test_collapse_attributed_to_verifier_when_extractor_honest():
    # Extractor honestly says "proposed"; verifier PASSes the upgrade anyway.
    out = _out([_answer(
        "A1", "Allocate €500k to Project X next quarter.",
        "decision", "proposed", "PASS", "ADMIT", ["M1"])])
    r = scorer.score(GOLD, out)
    assert r["metrics"]["e_collapse_by_layer"]["verifier"] == 1
    assert r["metrics"]["e_collapse_by_layer"]["extractor"] == 0


def test_collapse_attributed_to_gate_when_lower_layers_honest():
    out = _out([_answer(
        "A1", "Allocate €500k to Project X next quarter.",
        "decision", "proposed", "UNKNOWN", "ADMIT", ["M1"])])
    r = scorer.score(GOLD, out)
    assert r["metrics"]["e_collapse_by_layer"]["gate"] == 1


def test_baseline_fails_the_baits__falsifier_has_teeth():
    output = baseline_rag.run(CORPUS)
    r = scorer.score(GOLD, output)
    m = r["metrics"]
    # The flat pipeline MUST collapse: proposal->decision, paraphrase->agreement.
    assert m["e_collapse"] > 0, "fixtures rotted: baseline no longer collapses"
    assert m["bait_catch_rate"] < 1.0
    bait_classes = {e.get("bait_class") for e in r["collapse_events"]}
    assert "proposal_as_decision" in bait_classes or "paraphrase_agreement" in bait_classes
    # Flat architecture -> collapse attributed to the extractor layer.
    assert m["e_collapse_by_layer"]["extractor"] >= 1


def test_baseline_still_finds_the_real_decision():
    # The falsifier must not reward blanket refusal: baseline recall on the
    # genuine decision should be nonzero (it does find D1).
    output = baseline_rag.run(CORPUS)
    r = scorer.score(GOLD, output)
    assert r["metrics"]["recall"] > 0


def test_scorer_deterministic():
    a = scorer.canon_report(scorer.score(GOLD, baseline_rag.run(CORPUS)))
    b = scorer.canon_report(scorer.score(GOLD, baseline_rag.run(CORPUS)))
    assert a == b


def test_abstain_scored_on_hearsay():
    # A pipeline that upgrades hearsay must lose c_abstain; one that abstains keeps it.
    upgraded = _out([_answer(
        "A1", "Karim said the mayor's office already signed off on the site permit.",
        "decision", "decided", "PASS", "ADMIT", ["M5"])])
    r_bad = scorer.score(GOLD, upgraded)
    r_good = scorer.score(GOLD, PERFECT)
    assert r_bad["metrics"]["c_abstain"] == 0.0
    assert r_good["metrics"]["c_abstain"] == 1.0
