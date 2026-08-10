"""Baseline pipeline: deliberately ordinary RAG-style extraction.

NON_SOVEREIGN. Deterministic (keyword rules, no model calls) so the
falsifier's teeth can be demonstrated without inference infrastructure.
This baseline does what naive organizational RAG does: any sentence that
SOUNDS decisional becomes a "decision". It has one flat layer — its
extractor verdict is rubber-stamped by verifier and gate — which is
exactly the architecture the falsifier exists to indict.

It is supposed to fail the baits. If it ever stops failing them, the
fixtures have rotted, not the baseline improved.
"""
from __future__ import annotations

import re
from typing import Any, Mapping

_SENT_SPLIT = re.compile(r"(?<=[.!?])\s+|\n+")
_DECISION_CUES = re.compile(
    r"\b(decid\w*|approv\w*|allocat\w*|agree\w*|aligned|sign\w* off|budget\w* (?:set|is))\b",
    re.IGNORECASE,
)
_COMMIT_CUES = re.compile(r"\b(i'?ll|will)\b.*\bby\b", re.IGNORECASE)


def run(corpus: Mapping[str, Any]) -> dict[str, Any]:
    answers = []
    n = 0
    for doc in corpus["documents"]:
        for sent in _SENT_SPLIT.split(doc["text"]):
            sent = sent.strip()
            if not sent:
                continue
            status = None
            if _COMMIT_CUES.search(sent):
                status, extractor = "commitment", "committed"
            elif _DECISION_CUES.search(sent):
                status, extractor = "decision", "decided"
            if status is None:
                continue
            n += 1
            answers.append({
                "answer_id": f"BASE-{n:03d}",
                "statement": sent,
                "final_status": status,
                # Flat architecture: one opinion, three rubber stamps.
                "layers": {
                    "extractor_status": extractor,
                    "verifier_verdict": "PASS",
                    "gate_verdict": "ADMIT",
                },
                "provenance": [doc["doc_id"]],
            })
    return {
        "schema_name": "BOARD_MEMORY_OUTPUT_V1",
        "schema_version": "1.0.0",
        "pipeline_id": "baseline_rag_v0",
        "corpus_id": corpus["corpus_id"],
        "answers": answers,
    }
