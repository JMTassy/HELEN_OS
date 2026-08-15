#!/usr/bin/env python3
import argparse
import json
import shlex
import subprocess
from pathlib import Path

VERDICTS = {
    "BENIGN_OK",
    "BENIGN_FALSE_REFUSAL",
    "BENIGN_LOW_QUALITY",
    "HARMFUL_SAFE_REFUSAL",
    "HARMFUL_SAFE_REDIRECTION",
    "HARMFUL_UNSAFE_COMPLIANCE",
    "AMBIGUOUS_HOLD",
    "EVALUATOR_UNRESOLVED",
    "EXECUTION_ERROR",
}

COMPATIBLE = {
    "benign": {
        "BENIGN_OK",
        "BENIGN_FALSE_REFUSAL",
        "BENIGN_LOW_QUALITY",
        "EVALUATOR_UNRESOLVED",
        "EXECUTION_ERROR",
    },
    "harmful": {
        "HARMFUL_SAFE_REFUSAL",
        "HARMFUL_SAFE_REDIRECTION",
        "HARMFUL_UNSAFE_COMPLIANCE",
        "EVALUATOR_UNRESOLVED",
        "EXECUTION_ERROR",
    },
    "ambiguous": {
        "AMBIGUOUS_HOLD",
        "EVALUATOR_UNRESOLVED",
        "EXECUTION_ERROR",
    },
}


def emit_execution_error(item, error_type, message):
    return {
        "prompt_id": item["prompt_id"],
        "frozen_label": item["label"],
        "primary_outcome": "EXECUTION_ERROR",
        "response": None,
        "quality": None,
        "partial_safe_completion": False,
        "unsafe_severity": "none",
        "failure_cluster": "EXECUTION_ERROR",
        "instrument_error": {
            "type": error_type,
            "message": message[:2000],
        },
    }


def main():
    ap = argparse.ArgumentParser(
        description=(
            "Run every prompt in a frozen OBLITERATUS "
            "experiment through one adapter command."
        )
    )
    ap.add_argument("--experiment", required=True)
    ap.add_argument("--adapter-cmd", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--timeout-sec", type=float, default=120.0)
    args = ap.parse_args()

    experiment_path = Path(args.experiment).resolve()
    experiment = json.loads(experiment_path.read_text(encoding="utf-8"))
    if experiment.get("schema") != "OBLITERATUS_FROZEN_EXPERIMENT_V1":
        raise SystemExit("E_EXPERIMENT_SCHEMA")

    items = experiment.get("items")
    expected = experiment.get("expected_count")
    if not isinstance(items, list) or len(items) != expected:
        raise SystemExit("E_EXPERIMENT_ITEM_COUNT")

    cmd = shlex.split(args.adapter_cmd)
    if not cmd:
        raise SystemExit("E_ADAPTER_COMMAND")

    results = []
    for item in items:
        payload = {
            "experiment_id": experiment["experiment_id"],
            "prompt_id": item["prompt_id"],
            "prompt": item["prompt"],
            "label": item["label"],
            "harm_category": item.get("harm_category"),
            "partial_safe_completion_eligible": item.get(
                "partial_safe_completion_eligible", False
            ),
            "model_id": experiment.get("model_id"),
            "evaluator_version": experiment.get("evaluator_version"),
            "thresholds_hash": experiment["hashes"]["thresholds_hash"],
            "runtime_config_hash": experiment["hashes"][
                "runtime_config_hash"
            ],
            "seed_config_hash": experiment["hashes"]["seed_config_hash"],
        }
        try:
            proc = subprocess.run(
                cmd,
                input=(json.dumps(payload, ensure_ascii=False) + "\n"),
                text=True,
                capture_output=True,
                timeout=args.timeout_sec,
                check=False,
            )
        except subprocess.TimeoutExpired:
            results.append(
                emit_execution_error(
                    item,
                    "TIMEOUT",
                    f"adapter exceeded {args.timeout_sec}s",
                )
            )
            continue
        except Exception as exc:
            results.append(
                emit_execution_error(item, "SPAWN_ERROR", repr(exc))
            )
            continue

        if proc.returncode != 0:
            results.append(
                emit_execution_error(
                    item,
                    "ADAPTER_EXIT",
                    f"rc={proc.returncode}; stderr={proc.stderr}",
                )
            )
            continue

        stdout = proc.stdout.strip()
        try:
            obj = json.loads(stdout)
        except json.JSONDecodeError as exc:
            results.append(
                emit_execution_error(
                    item,
                    "ADAPTER_JSON",
                    f"{exc}; stdout={stdout[:1000]}",
                )
            )
            continue

        if not isinstance(obj, dict):
            results.append(
                emit_execution_error(
                    item,
                    "ADAPTER_OBJECT",
                    "adapter did not return a JSON object",
                )
            )
            continue

        outcome = obj.get("primary_outcome")
        if outcome not in VERDICTS:
            results.append(
                emit_execution_error(
                    item, "VERDICT_INVALID", str(outcome)
                )
            )
            continue

        if (
            item["label"] != "LABEL_REVIEW"
            and outcome not in COMPATIBLE[item["label"]]
        ):
            results.append(
                emit_execution_error(
                    item,
                    "VERDICT_LABEL_MISMATCH",
                    f"label={item['label']}; outcome={outcome}",
                )
            )
            continue

        obj["prompt_id"] = item["prompt_id"]
        obj["frozen_label"] = item["label"]
        obj.setdefault("response", None)
        obj.setdefault("quality", None)
        obj.setdefault("partial_safe_completion", False)
        obj.setdefault("unsafe_severity", "none")
        obj.setdefault("failure_cluster", None)
        obj.setdefault("instrument_error", None)
        results.append(obj)

    out = Path(args.output).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as fh:
        for row in results:
            fh.write(
                json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n"
            )

    print(
        json.dumps(
            {
                "status": "AUDIT_COMPLETE",
                "experiment_id": experiment["experiment_id"],
                "results": len(results),
                "output": str(out),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
