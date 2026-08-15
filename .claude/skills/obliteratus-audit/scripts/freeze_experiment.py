#!/usr/bin/env python3
import argparse
import hashlib
import json
from pathlib import Path

ALLOWED_LABELS = {"benign", "ambiguous", "harmful", "LABEL_REVIEW"}
SCRIPT_VERSION = "obliteratus-freeze-v1"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_hash(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canon(obj) -> str:
    return json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def read_jsonl(path: Path):
    rows = []
    for lineno, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), 1
    ):
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"E_JSONL:{path}:{lineno}:{exc}")
        if not isinstance(obj, dict):
            raise SystemExit(f"E_JSONL_OBJECT:{path}:{lineno}")
        rows.append(obj)
    return rows


def main():
    ap = argparse.ArgumentParser(
        description="Freeze an OBLITERATUS experiment identity."
    )
    ap.add_argument("--corpus", required=True)
    ap.add_argument("--labels", required=True)
    ap.add_argument("--thresholds", required=True)
    ap.add_argument("--evaluator", required=True)
    ap.add_argument("--model-config", required=True)
    ap.add_argument("--system-prompt", required=True)
    ap.add_argument("--runtime-config", required=True)
    ap.add_argument("--seed-config", required=True)
    ap.add_argument("--expected-count", type=int, default=842)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    paths = {
        k: Path(v).resolve()
        for k, v in {
            "corpus": args.corpus,
            "labels": args.labels,
            "thresholds": args.thresholds,
            "evaluator": args.evaluator,
            "model_config": args.model_config,
            "system_prompt": args.system_prompt,
            "runtime_config": args.runtime_config,
            "seed_config": args.seed_config,
        }.items()
    }
    for name, path in paths.items():
        if not path.is_file():
            raise SystemExit(f"E_MISSING_INPUT:{name}:{path}")

    corpus = read_jsonl(paths["corpus"])
    labels = read_jsonl(paths["labels"])

    if len(corpus) != args.expected_count:
        raise SystemExit(
            f"E_CORPUS_COUNT:"
            f"expected={args.expected_count}:"
            f"actual={len(corpus)}"
        )
    if len(labels) != args.expected_count:
        raise SystemExit(
            f"E_LABEL_COUNT:"
            f"expected={args.expected_count}:"
            f"actual={len(labels)}"
        )

    corpus_map = {}
    for row in corpus:
        pid = row.get("prompt_id")
        prompt = row.get("prompt")
        if not isinstance(pid, str) or not pid:
            raise SystemExit("E_PROMPT_ID")
        if not isinstance(prompt, str):
            raise SystemExit(f"E_PROMPT_TEXT:{pid}")
        if pid in corpus_map:
            raise SystemExit(f"E_DUPLICATE_PROMPT_ID:{pid}")
        corpus_map[pid] = row

    label_map = {}
    for row in labels:
        pid = row.get("prompt_id")
        label = row.get("label")
        if pid in label_map:
            raise SystemExit(f"E_DUPLICATE_LABEL_ID:{pid}")
        if pid not in corpus_map:
            raise SystemExit(f"E_LABEL_ORPHAN:{pid}")
        if label not in ALLOWED_LABELS:
            raise SystemExit(f"E_LABEL_INVALID:{pid}:{label}")
        label_map[pid] = row

    if set(corpus_map) != set(label_map):
        missing = sorted(set(corpus_map) - set(label_map))
        extra = sorted(set(label_map) - set(corpus_map))
        raise SystemExit(
            f"E_LABEL_ID_SET:"
            f"missing={missing[:5]}:"
            f"extra={extra[:5]}"
        )

    try:
        thresholds = json.loads(
            paths["thresholds"].read_text(encoding="utf-8")
        )
    except json.JSONDecodeError as exc:
        raise SystemExit(f"E_THRESHOLDS_JSON:{exc}")
    if not isinstance(thresholds, dict):
        raise SystemExit("E_THRESHOLDS_OBJECT")
    for required in (
        "epsilon_safety",
        "frr_target",
        "allowed_tolerance",
    ):
        if required not in thresholds:
            raise SystemExit(f"E_THRESHOLD_MISSING:{required}")

    hashes = {
        name + "_hash": file_hash(path)
        for name, path in paths.items()
    }
    scoring_rules_hash = sha256_bytes(SCRIPT_VERSION.encode("utf-8"))

    identity_body = {
        **hashes,
        "scoring_rules_hash": scoring_rules_hash,
        "expected_count": args.expected_count,
        "freeze_script_version": SCRIPT_VERSION,
    }
    bid = sha256_bytes(canon(identity_body).encode("utf-8"))

    items = []
    for row in corpus:
        pid = row["prompt_id"]
        lab = label_map[pid]
        items.append(
            {
                "prompt_id": pid,
                "prompt": row["prompt"],
                "label": lab["label"],
                "harm_category": lab.get("harm_category"),
                "partial_safe_completion_eligible": bool(
                    lab.get("partial_safe_completion_eligible", False)
                ),
            }
        )

    model_id = None
    evaluator_version = None
    try:
        model_obj = json.loads(
            paths["model_config"].read_text(encoding="utf-8")
        )
        if isinstance(model_obj, dict):
            model_id = model_obj.get("model_id") or model_obj.get("model")
    except Exception:
        pass
    try:
        eval_obj = json.loads(
            paths["evaluator"].read_text(encoding="utf-8")
        )
        if isinstance(eval_obj, dict):
            evaluator_version = eval_obj.get(
                "evaluator_version"
            ) or eval_obj.get("version")
    except Exception:
        pass

    frozen = {
        "schema": "OBLITERATUS_FROZEN_EXPERIMENT_V1",
        "experiment_id": bid,
        "baseline_bid": bid,
        "expected_count": args.expected_count,
        "hashes": hashes,
        "scoring_rules_hash": scoring_rules_hash,
        "thresholds": thresholds,
        "model_id": model_id,
        "evaluator_version": evaluator_version,
        "items": items,
        "source_paths": {
            name: str(path) for name, path in paths.items()
        },
    }

    out = Path(args.output).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(frozen, indent=2, sort_keys=True, ensure_ascii=False)
        + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": "FROZEN",
                "experiment_id": bid,
                "expected_count": args.expected_count,
                "output": str(out),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
