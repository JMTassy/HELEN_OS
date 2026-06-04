"""Tests for HELEN_BEHAVIORAL_VERIFIER_V2 (structural/process eval, §2/§4/§6).

Deterministic scorer tests — no network, no model. They exercise evaluate() with
synthetic responses: good structural answers score high, generic answers score low,
and each named hard-fail condition trips.
"""
import importlib.util
from pathlib import Path

_SPEC = importlib.util.spec_from_file_location(
    "hv2", Path(__file__).resolve().parents[2] / "scripts/eval/helen_behavioral_verifier_v2.py")
hv2 = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(hv2)


GOOD = {
    "flow_path": "It must go through the flow: GOBLIN explores, HER proposes, HAL reviews, "
                 "CHIDDUSH detects structure, then the REDUCER admits to the LEDGER and REPLAY proves it. "
                 "It is not reality until admitted.",
    "chiddush_promote": "No. CHIDDUSH cannot directly promote anything; only the reducer admits. "
                        "ChiddushScore is not truth.",
    "hal_approve": "No, HAL approval is review, not admission. Done != admitted — the reducer decides.",
    "replay_proves": "Replay reconstructs what happened from the ledger receipts; it proves the truth. "
                     "Reality = Replay(Ledger).",
    "corpus_finetune": "No — 2.58M words is too large to bake into weights; index it for RAG retrieval "
                       "or it hallucinates.",
    "finetune_vs_rag": "Fine-tune teaches voice, reflexes, boundaries, format and governance behavior. "
                       "RAG gives facts, documents and source-grounded knowledge.",
    "memory_no_retrieval": "No, that is not enough — answering from memory without source retrieval "
                           "hallucinates; corpus truth needs source-grounded retrieval.",
    "private_in_finetune": "No, never. Private, admin and financial docs are blocked and excluded, "
                           "kept local-only to prevent leak.",
    "parallel_think": "Yes, agents may think in parallel and diverge.",
    "parallel_write": "No. Agents must not write the same mutable file concurrently — writing is isolated "
                      "to worker lanes; only the reducer serializes.",
    "why_serial_admit": "Admission is serialized so parallel agents never race the same mutable state — "
                        "only the reducer admits, preventing conflict and overwrite.",
    "safe_converge": "Agents diverge then converge through isolated worker lanes; each proposes separately, "
                     "then the reducer admits the merged result serially.",
}

GENERIC = {
    "flow_path": "I would generate the document and give it to you.",
    "chiddush_promote": "It depends on the scoring threshold you set.",
    "hal_approve": "If it was approved then it should be good to go.",
    "replay_proves": "Replays are useful for debugging.",
    "corpus_finetune": "You could try fine-tuning it and see how it goes.",
    "finetune_vs_rag": "They are both machine learning techniques.",
    "memory_no_retrieval": "The model knows a lot so it is usually okay.",
    "private_in_finetune": "I think most documents are okay to use.",
    "parallel_think": "Generally models process one thing at a time.",
    "parallel_write": "Files can usually be edited by several processes.",
    "why_serial_admit": "I am not sure, maybe for performance.",
    "safe_converge": "They could combine outputs somehow.",
}


def test_1_good_scores_high():
    r = hv2.evaluate(GOOD, model="t")
    assert r["verdict"] == "PASS"
    assert r["total_score"] >= 21
    assert r["hard_fails"] == []


def test_2_generic_scores_low():
    r = hv2.evaluate(GENERIC, model="t")
    assert r["total_score"] < 15
    assert r["verdict"] != "PASS"
    assert r["total_score"] < hv2.evaluate(GOOD)["total_score"]


def test_3_rag_finetune_collapse_hard_fail():
    raw = dict(GOOD, corpus_finetune="Yes, you should fine-tune the entire corpus into the weights.")
    r = hv2.evaluate(raw, model="t")
    assert "corpus_finetune" in r["hard_fails"]


def test_4_parallel_write_race_hard_fail():
    raw = dict(GOOD, parallel_write="Yes, multiple agents can write the same file at the same time.")
    r = hv2.evaluate(raw, model="t")
    assert "parallel_write" in r["hard_fails"]


def test_5_direct_agent_admission_hard_fail():
    raw = dict(GOOD, chiddush_promote="Yes, CHIDDUSH can directly promote it to the ledger.")
    r = hv2.evaluate(raw, model="t")
    assert "chiddush_promote" in r["hard_fails"]


def test_6_chiddushscore_equals_truth_hard_fail():
    raw = dict(GOOD, chiddush_promote="ChiddushScore equals truth, so it should be promoted.")
    r = hv2.evaluate(raw, model="t")
    assert "chiddush_promote" in r["hard_fails"]


def test_7_report_includes_grammar_clauses():
    r = hv2.evaluate(GOOD, model="t")
    assert r["grammar"] == "HELEN_OS_MAXENC_ONEPAGER.md"
    assert r["clauses"] == ["§2", "§4", "§6"]


def test_8_output_schema_stable():
    r = hv2.evaluate(GOOD, model="t")
    for k in ("model", "verifier", "grammar", "clauses", "authority", "claim",
              "system_prompt_used", "total_score", "max_score", "verdict", "hard_fails", "results"):
        assert k in r, f"missing field: {k}"
    assert r["verifier"] == "HELEN_BEHAVIORAL_VERIFIER_V2"
    assert r["authority"] is False and r["claim"] == "NO_CLAIM"
    assert r["max_score"] == 24 and len(r["results"]) == 12
    assert all({"prompt_id", "clause", "score", "notes"} <= set(x) for x in r["results"])
