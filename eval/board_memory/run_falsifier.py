#!/usr/bin/env python3
"""Board Memory falsifier runner.

NON_SOVEREIGN · authority=false · read-only over fixtures · no ledger path.

Usage:
    python3 eval/board_memory/run_falsifier.py --pipeline baseline
    python3 eval/board_memory/run_falsifier.py --pipeline helen

The falsifier exists BEFORE the believer: the `helen` pipeline is a typed
interface that raises until the governed pipeline is actually built. The
baseline is expected to fail the baits — that failure is the harness
demonstrating it has teeth, not a bug.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import baseline_rag  # noqa: E402
import scorer  # noqa: E402


class HelenPipeline:
    """Interface the governed pipeline must implement to be scored.

    Contract: run(corpus) -> BOARD_MEMORY_OUTPUT_V1 dict, with honest
    per-layer verdicts (extractor_status / verifier_verdict / gate_verdict).
    A pipeline that rubber-stamps its own extractor will be exposed by the
    e_collapse_by_layer decomposition, not hidden by it.
    """

    pipeline_id = "helen_governed_v0"

    def run(self, corpus):  # pragma: no cover - deliberate
        raise NotImplementedError(
            "The believer is not built. The falsifier is ready: implement "
            "HelenPipeline.run() emitting BOARD_MEMORY_OUTPUT_V1 and this "
            "runner will score it against the same gold set as the baseline."
        )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pipeline", choices=["baseline", "helen"], required=True)
    ap.add_argument("--corpus", default=str(HERE / "fixtures" / "corpus_v0.json"))
    ap.add_argument("--gold", default=str(HERE / "fixtures" / "gold_v0.json"))
    ap.add_argument("--json", action="store_true", help="emit canonical JSON report only")
    args = ap.parse_args()

    corpus = json.loads(Path(args.corpus).read_text(encoding="utf-8"))
    gold = json.loads(Path(args.gold).read_text(encoding="utf-8"))

    if args.pipeline == "baseline":
        output = baseline_rag.run(corpus)
    else:
        output = HelenPipeline().run(corpus)

    report = scorer.score(gold, output)

    if args.json:
        print(scorer.canon_report(report))
        return 0

    m = report["metrics"]
    print(f"pipeline        : {report['pipeline_id']}")
    print(f"gold set        : {report['gold_set_id']}")
    print(f"precision       : {m['precision']}")
    print(f"recall          : {m['recall']}")
    print(f"p_prov          : {m['p_prov']}")
    print(f"c_abstain       : {m['c_abstain']}")
    print(f"bait_catch_rate : {m['bait_catch_rate']}")
    print(f"e_collapse      : {m['e_collapse']}  by_layer={m['e_collapse_by_layer']}")
    for ev in report["collapse_events"]:
        print(f"  COLLAPSE {ev['item_id']} [{ev.get('bait_class')}] "
              f"gold={ev['gold_status']} claimed={ev['claimed']} layer={ev['failing_layer']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
