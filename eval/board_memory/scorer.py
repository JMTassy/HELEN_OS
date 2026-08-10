"""Board Memory falsifier — decomposed E_collapse scorer.

NON_SOVEREIGN. authority=false. Pure stdlib, deterministic: no wall-time,
no randomness, no filesystem-order dependence (determinism law: same
inputs MUST produce same report bytes).

Metrics:
  P, R            precision/recall on decisions (and commitments)
  P_prov          fraction of correct answers citing >=1 correct source
  C_abstain       correct HOLD/UNKNOWN rate on abstain-expected gold items
  bait_catch_rate fraction of collapse-bait items NOT upgraded by the pipeline
  E_collapse      category-collapse error rate, DECOMPOSED by failing layer:
                    extractor  — typed the upgrade itself
                    verifier   — extractor was honest, verifier PASSed the upgrade
                    gate       — verifier was honest, gate ADMITted anyway

The decomposition is the point: a single E_collapse number hides which
membrane failed. HAL-pass-but-supervisor-deny events (Season 02 / ARC-03
class) only become visible when the layers are scored separately.
"""
from __future__ import annotations

import json
import re
from typing import Any, Mapping

# Statuses that constitute an institutional UPGRADE when the gold status
# does not support them. proposal != agreement; claim != fact.
UPGRADED_FINAL = {"decision", "commitment"}
# Gold statuses that legitimately support each upgraded final status.
SUPPORTS = {
    "decision": {"decided"},
    "commitment": {"committed"},
}
# Extractor statuses that are themselves upgrades relative to these gold truths.
WEAK_GOLD = {"proposed", "discussed", "open", "unknowable", "contradicted"}
UPGRADED_EXTRACTOR = {"decided", "committed"}

_TOKEN_RE = re.compile(r"[a-z0-9€]+")


def _tokens(text: str) -> frozenset[str]:
    return frozenset(_TOKEN_RE.findall(text.lower()))


def _jaccard(a: frozenset[str], b: frozenset[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def match_answers(gold_items: list[Mapping[str, Any]],
                  answers: list[Mapping[str, Any]],
                  threshold: float = 0.25) -> dict[str, str]:
    """Greedy deterministic matching: answer_id -> item_id.

    Pairs are ranked by (jaccard desc, item_id asc, answer_id asc) so the
    result is a pure function of the inputs. Each side matches at most once.
    """
    pairs = []
    for g in gold_items:
        gt = _tokens(g["statement"])
        for a in answers:
            s = _jaccard(gt, _tokens(a["statement"]))
            if s >= threshold:
                pairs.append((-s, g["item_id"], a["answer_id"]))
    pairs.sort()
    matched_g: set[str] = set()
    matched_a: set[str] = set()
    out: dict[str, str] = {}
    for _neg, item_id, answer_id in pairs:
        if item_id in matched_g or answer_id in matched_a:
            continue
        matched_g.add(item_id)
        matched_a.add(answer_id)
        out[answer_id] = item_id
    return out


def _attribute_collapse(answer: Mapping[str, Any]) -> str:
    """Which layer let the upgrade through? First dishonest layer owns it."""
    layers = answer["layers"]
    if layers["extractor_status"] in UPGRADED_EXTRACTOR:
        return "extractor"
    if layers["verifier_verdict"] == "PASS":
        return "verifier"
    if layers["gate_verdict"] == "ADMIT":
        return "gate"
    return "renderer"  # honest layers, upgraded final_status anyway


def score(gold_set: Mapping[str, Any], output: Mapping[str, Any]) -> dict[str, Any]:
    gold_items = list(gold_set["items"])
    answers = list(output["answers"])
    by_item = {g["item_id"]: g for g in gold_items}
    match = match_answers(gold_items, answers)

    # --- decision/commitment precision & recall -----------------------------
    tp = fp = 0
    correct_answers = []
    for a in answers:
        if a["final_status"] not in UPGRADED_FINAL:
            continue
        g = by_item.get(match.get(a["answer_id"], ""))
        if g is not None and g["true_status"] in SUPPORTS[a["final_status"]]:
            tp += 1
            correct_answers.append((a, g))
        else:
            fp += 1
    gold_positive = [g for g in gold_items if g["true_status"] in {"decided", "committed"}]
    fn = sum(
        1 for g in gold_positive
        if not any(match.get(a["answer_id"]) == g["item_id"]
                   and a["final_status"] in UPGRADED_FINAL
                   and g["true_status"] in SUPPORTS[a["final_status"]]
                   for a in answers)
    )
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0

    # --- provenance ---------------------------------------------------------
    prov_ok = sum(
        1 for a, g in correct_answers
        if set(a.get("provenance", [])) & set(g["source_ids"])
    )
    p_prov = prov_ok / len(correct_answers) if correct_answers else 0.0

    # --- abstention ---------------------------------------------------------
    abstain_gold = [g for g in gold_items if g.get("abstain_expected")]
    c_abstain_ok = 0
    for g in abstain_gold:
        matched = [a for a in answers if match.get(a["answer_id"]) == g["item_id"]]
        if not matched or all(a["final_status"] == "abstain" for a in matched):
            c_abstain_ok += 1
    c_abstain = c_abstain_ok / len(abstain_gold) if abstain_gold else 1.0

    # --- E_collapse, decomposed --------------------------------------------
    collapse_by_layer = {"extractor": 0, "verifier": 0, "gate": 0, "renderer": 0}
    collapse_events = []
    evaluated = 0
    for a in answers:
        g = by_item.get(match.get(a["answer_id"], ""))
        if g is None:
            continue
        evaluated += 1
        if a["final_status"] in UPGRADED_FINAL and g["true_status"] in WEAK_GOLD:
            layer = _attribute_collapse(a)
            collapse_by_layer[layer] += 1
            collapse_events.append({
                "answer_id": a["answer_id"], "item_id": g["item_id"],
                "gold_status": g["true_status"], "claimed": a["final_status"],
                "failing_layer": layer,
                "bait_class": g.get("bait_class"),
            })
    e_collapse = (sum(collapse_by_layer.values()) / evaluated) if evaluated else 0.0

    # --- bait catch rate ----------------------------------------------------
    baits = [g for g in gold_items if g["kind"] == "bait"]
    caught = 0
    for g in baits:
        upgraded = any(
            match.get(a["answer_id"]) == g["item_id"] and a["final_status"] in UPGRADED_FINAL
            for a in answers
        )
        if not upgraded:
            caught += 1
    bait_catch_rate = caught / len(baits) if baits else 1.0

    return {
        "schema_name": "BOARD_MEMORY_SCORE_V1",
        "schema_version": "1.0.0",
        "pipeline_id": output["pipeline_id"],
        "gold_set_id": gold_set["gold_set_id"],
        "metrics": {
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "p_prov": round(p_prov, 4),
            "c_abstain": round(c_abstain, 4),
            "bait_catch_rate": round(bait_catch_rate, 4),
            "e_collapse": round(e_collapse, 4),
            "e_collapse_by_layer": collapse_by_layer,
        },
        "counts": {"tp": tp, "fp": fp, "fn": fn, "evaluated_matched": evaluated,
                   "baits_total": len(baits), "baits_caught": caught},
        "collapse_events": sorted(collapse_events, key=lambda e: e["answer_id"]),
    }


def canon_report(report: Mapping[str, Any]) -> str:
    """Canonical serialization: sorted keys, no whitespace variance."""
    return json.dumps(report, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
