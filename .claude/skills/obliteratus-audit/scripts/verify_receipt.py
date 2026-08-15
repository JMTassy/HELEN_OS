#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from compare_runs import evaluate_candidate


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def resolve(base: Path, value: str) -> Path:
    path = Path(value)
    return (
        path.resolve()
        if path.is_absolute()
        else (base / path).resolve()
    )


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def hold(error, details=None):
    return {
        "schema": "OBLITERATUS_VERIFIED_RECEIPT_V1",
        "receipt_verification": "HOLD",
        "error": error,
        "details": details or [],
        "verdict": "HOLD",
    }


def main():
    ap = argparse.ArgumentParser(
        description=(
            "Re-derive and verify a claimed OBLITERATUS "
            "result receipt."
        )
    )
    ap.add_argument("--receipt", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    receipt_path = Path(args.receipt).resolve()
    if not receipt_path.is_file():
        result = hold("E_RECEIPT_MISSING", [str(receipt_path)])
    else:
        try:
            claim = load_json(receipt_path)
        except Exception as exc:
            result = hold("E_RECEIPT_JSON", [repr(exc)])
        else:
            base = receipt_path.parent
            required = [
                "experiment_path",
                "baseline_score_path",
                "candidate_score_paths",
                "exact_replay_command",
            ]
            missing_fields = [x for x in required if x not in claim]
            if missing_fields:
                result = hold("E_RECEIPT_FIELDS", missing_fields)
            elif (
                not isinstance(claim.get("candidate_score_paths"), list)
                or len(claim["candidate_score_paths"]) != 2
            ):
                result = hold(
                    "E_REPLAY_PAIR_REQUIRED",
                    [
                        "candidate_score_paths must contain exactly "
                        "two consecutive full-corpus score files"
                    ],
                )
            elif (
                not isinstance(claim.get("exact_replay_command"), str)
                or not claim["exact_replay_command"].strip()
            ):
                result = hold("E_REPLAY_COMMAND_MISSING")
            else:
                exp_path = resolve(base, claim["experiment_path"])
                baseline_path = resolve(
                    base, claim["baseline_score_path"]
                )
                cand_paths = [
                    resolve(base, x)
                    for x in claim["candidate_score_paths"]
                ]
                all_paths = [exp_path, baseline_path] + cand_paths
                absent = [
                    str(p) for p in all_paths if not p.is_file()
                ]
                if absent:
                    result = hold(
                        "E_REFERENCED_ARTIFACT_MISSING", absent
                    )
                else:
                    try:
                        exp = load_json(exp_path)
                        baseline = load_json(baseline_path)
                        c1 = load_json(cand_paths[0])
                        c2 = load_json(cand_paths[1])
                    except Exception as exc:
                        result = hold(
                            "E_REFERENCED_ARTIFACT_JSON", [repr(exc)]
                        )
                    else:
                        surgery_id = claim.get("surgery_id")
                        reverted = claim.get("reverted_surgeries") or []
                        r1 = evaluate_candidate(
                            exp, baseline, c1, surgery_id, reverted
                        )
                        r2 = evaluate_candidate(
                            exp, baseline, c2, surgery_id, reverted
                        )
                        details = []
                        if not r1.get("single_run_acceptance_gate"):
                            details.append(
                                "candidate rerun 1 did not pass the "
                                "single-run acceptance gate"
                            )
                        if not r2.get("single_run_acceptance_gate"):
                            details.append(
                                "candidate rerun 2 did not pass the "
                                "single-run acceptance gate"
                            )
                        if (
                            r1.get("verdict") == "REVERT"
                            or r2.get("verdict") == "REVERT"
                        ):
                            details.append(
                                "at least one candidate rerun "
                                "requires REVERT"
                            )
                        if c1.get("behavioral_result_hash") != c2.get(
                            "behavioral_result_hash"
                        ):
                            details.append(
                                "two consecutive reruns have different "
                                "behavioral_result_hash values"
                            )
                        if c1.get("metrics") != c2.get("metrics"):
                            details.append(
                                "two consecutive reruns have different "
                                "aggregate metrics"
                            )
                        if claim.get(
                            "require_raw_identity", False
                        ) and c1.get("results_hash") != c2.get(
                            "results_hash"
                        ):
                            details.append(
                                "raw result identity was required but "
                                "results_hash differs"
                            )
                        claimed = claim.get("claimed_result") or {}
                        if claimed:
                            if claimed.get("experiment_id") not in (
                                None,
                                exp.get("experiment_id"),
                            ):
                                details.append(
                                    "claimed experiment_id differs "
                                    "from frozen experiment"
                                )
                            if claimed.get(
                                "candidate_metrics"
                            ) not in (None, c2.get("metrics")):
                                details.append(
                                    "claimed candidate metrics do not "
                                    "match re-derived metrics"
                                )
                            if claimed.get("verdict") not in (
                                None,
                                "PASS",
                            ):
                                details.append(
                                    "claimed final verdict is not PASS"
                                )
                        artifact_hashes = {
                            "experiment": sha256_file(exp_path),
                            "baseline_score": sha256_file(
                                baseline_path
                            ),
                            "candidate_score_1": sha256_file(
                                cand_paths[0]
                            ),
                            "candidate_score_2": sha256_file(
                                cand_paths[1]
                            ),
                            "claim_receipt": sha256_file(receipt_path),
                        }
                        common = {
                            "schema": (
                                "OBLITERATUS_VERIFIED_RECEIPT_V1"
                            ),
                            "experiment_id": exp.get("experiment_id"),
                            "baseline_bid": baseline.get(
                                "experiment_id"
                            ),
                            "candidate_bid": c2.get("experiment_id"),
                            "baseline_metrics": baseline.get("metrics"),
                            "candidate_metrics": c2.get("metrics"),
                            "deltas": r2.get("deltas"),
                            "failure_clusters": c2.get(
                                "failure_clusters", {}
                            ),
                            "accepted_surgery": r2.get(
                                "accepted_surgery"
                            ),
                            "reverted_surgeries": r2.get(
                                "reverted_surgeries", []
                            ),
                            "safety_regression": r2.get(
                                "safety_regression"
                            ),
                            "quality_regression": r2.get(
                                "quality_regression"
                            ),
                            "style_regression": r2.get(
                                "style_regression"
                            ),
                            "artifact_hashes": artifact_hashes,
                            "exact_replay_command": claim[
                                "exact_replay_command"
                            ],
                        }
                        if details:
                            result = {
                                **common,
                                "receipt_verification": "HOLD",
                                "verification_details": details,
                                "verdict": "HOLD",
                            }
                        else:
                            result = {
                                **common,
                                "receipt_verification": "PASS",
                                "replay_consistency": {
                                    "behavioral_result_hash": c2.get(
                                        "behavioral_result_hash"
                                    ),
                                    "metrics_identical": True,
                                    "raw_identity_required": bool(
                                        claim.get(
                                            "require_raw_identity",
                                            False,
                                        )
                                    ),
                                },
                                "verdict": "PASS",
                            }

    out = Path(args.output).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False)
        + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "receipt_verification": result.get(
                    "receipt_verification"
                ),
                "verdict": result.get("verdict"),
                "output": str(out),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
