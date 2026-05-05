#!/usr/bin/env python3
"""
RALPH typed artifact emitter.

Non-sovereign.
No ledger append.
No reducer decision.
No canon mutation.

Reads pytest output files from a RALPH epoch logdir and emits four review
artifacts:
  - FAILURE_CLUSTER_V1
  - CANDIDATE_FIX_V1
  - EVAL_RECEIPT_V1
  - REVIEW_PACKET_DRAFT_V1
plus an ARTIFACT_MANIFEST that hashes them.

The point: RALPH does not become powerful by acting more. RALPH becomes
useful by leaving better receipts.

Usage:
    python3 tools/ralph_emit_artifacts.py \\
        --epoch-id <id> --logdir <path>

The logdir is expected to contain (any may be missing; missing files are
treated as empty):
    focused_tests.txt
    full_tests.txt
    post_iter_*_validator.txt

Output goes to <logdir>/artifacts/.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any


ARTIFACT_VERSION = "RALPH_TYPED_ARTIFACTS_V1"


def canon_json(obj: Any) -> bytes:
    """CANON_JSON_V1: sort_keys, compact separators, UTF-8."""
    return json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def sha256_obj(obj: Any) -> str:
    return hashlib.sha256(canon_json(obj)).hexdigest()


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def summarize_pytest(text: str) -> dict[str, Any]:
    failed = re.findall(r"FAILED\s+([^\s]+)", text)
    errors = re.findall(r"ERROR\s+([^\s]+)", text)
    passed_match = re.search(r"(\d+)\s+passed", text)
    failed_match = re.search(r"(\d+)\s+failed", text)
    error_match = re.search(r"(\d+)\s+error", text)
    skipped_match = re.search(r"(\d+)\s+skipped", text)
    return {
        "passed": int(passed_match.group(1)) if passed_match else 0,
        "failed": int(failed_match.group(1)) if failed_match else len(failed),
        "errors": int(error_match.group(1)) if error_match else len(errors),
        "skipped": int(skipped_match.group(1)) if skipped_match else 0,
        "failed_items": sorted(set(failed)),
        "error_items": sorted(set(errors)),
        "raw_len": len(text),
    }


def cluster_failures(focused: str, full: str) -> dict[str, Any]:
    combined = focused + "\n" + full
    patterns = {
        "manifest_validator": [
            "manifest",
            "Manifest",
            "test_manifest_validator",
            "validator",
        ],
        "manifest_registry": [
            "registry",
            "Registry",
            "test_manifest_registry",
        ],
        "schema_validation": [
            "schema",
            "jsonschema",
            "ValidationError",
        ],
        "hash_or_determinism": [
            "hash",
            "determin",
            "canonical",
            "sha256",
        ],
        "import_or_path": [
            "ModuleNotFoundError",
            "ImportError",
            "No module named",
            "FileNotFoundError",
        ],
    }
    scores: dict[str, int] = {}
    for name, keys in patterns.items():
        scores[name] = sum(combined.count(k) for k in keys)
    primary = max(scores, key=scores.get) if scores else "unknown"
    if scores.get(primary, 0) == 0:
        primary = "unknown"
    return {
        "cluster_id": primary,
        "scores": scores,
        "summary": summarize_pytest(combined),
    }


def recommend_strategy(cluster_id: str) -> str:
    strategies = {
        "manifest_validator": (
            "Patch manifest validator behavior or tests with the smallest "
            "deterministic schema-compatible change."
        ),
        "manifest_registry": (
            "Patch registry lookup, normalization, or fixture alignment; "
            "do not rewrite registry architecture."
        ),
        "schema_validation": (
            "Patch schema mismatch or fixture data; preserve canonical "
            "schema path."
        ),
        "hash_or_determinism": (
            "Patch canonicalization or hash recomputation; never trust "
            "stored envelope hashes."
        ),
        "import_or_path": (
            "Patch import path or test fixture path; do not move schema "
            "roots without review."
        ),
        "unknown": (
            "Inspect shortest failing test first and produce a blocker if "
            "no deterministic fix is evident."
        ),
    }
    return strategies.get(cluster_id, strategies["unknown"])


def build_artifacts(epoch_id: str, logdir: Path) -> dict[str, Any]:
    focused_text = read_text(logdir / "focused_tests.txt")
    full_text = read_text(logdir / "full_tests.txt")

    post_iter_files = sorted(logdir.glob("post_iter_*_validator.txt"))
    post_iter = [
        {
            "file": p.name,
            "summary": summarize_pytest(read_text(p)),
            "hash": hashlib.sha256(
                read_text(p).encode("utf-8", errors="replace")
            ).hexdigest(),
        }
        for p in post_iter_files
    ]

    cluster = cluster_failures(focused_text, full_text)

    failure_cluster = {
        "schema": "FAILURE_CLUSTER_V1",
        "authority": "NON_SOVEREIGN",
        "canon": "NO_SHIP",
        "epoch_id": epoch_id,
        "cluster": cluster,
        "source_files": {
            "focused_tests": "focused_tests.txt",
            "full_tests": "full_tests.txt",
        },
        # F-001 (closed 2026-05-02): wall-clock time was previously embedded
        # here as `generated_at_unix`, which violated CWL v1.0.1 §2 and made
        # `failure_cluster_ref` non-deterministic across runs with identical
        # inputs. Time information for the epoch is carried out-of-band via
        # the logdir name (epoch_id). The hashed core stays content-only.
    }

    candidate_fix = {
        "schema": "CANDIDATE_FIX_V1",
        "authority": "NON_SOVEREIGN",
        "canon": "NO_SHIP",
        "epoch_id": epoch_id,
        "target_cluster": cluster["cluster_id"],
        "recommended_strategy": recommend_strategy(cluster["cluster_id"]),
        "constraints": [
            "one bounded patch step",
            "no ledger append",
            "no reducer impersonation",
            "no canon/kernel/ledger mutation",
            "run smallest relevant test slice after patch",
        ],
        "status": "PROPOSED",
    }

    eval_receipt = {
        "schema": "EVAL_RECEIPT_V1",
        "authority": "NON_SOVEREIGN",
        "canon": "NO_SHIP",
        "epoch_id": epoch_id,
        "focused_tests": summarize_pytest(focused_text),
        "full_tests": summarize_pytest(full_text),
        "post_iteration_checks": post_iter,
        "evidence_hashes": {
            "focused_tests_sha256": hashlib.sha256(
                focused_text.encode("utf-8", errors="replace")
            ).hexdigest(),
            "full_tests_sha256": hashlib.sha256(
                full_text.encode("utf-8", errors="replace")
            ).hexdigest(),
        },
        "status": "EVALUATED",
    }

    review_packet = {
        "schema": "REVIEW_PACKET_DRAFT_V1",
        "authority": "NON_SOVEREIGN",
        "canon": "NO_SHIP",
        "epoch_id": epoch_id,
        "failure_cluster_ref": sha256_obj(failure_cluster),
        "candidate_fix_ref": sha256_obj(candidate_fix),
        "eval_receipt_ref": sha256_obj(eval_receipt),
        "request": (
            "Review the candidate fix and decide whether it is admissible "
            "for MAYOR review."
        ),
        "forbidden_claims": [
            "RALPH_DONE unless targeted tests pass",
            "policy live",
            "ledger appended",
            "canon updated",
        ],
        "status": "DRAFT",
    }

    return {
        "failure_cluster": failure_cluster,
        "candidate_fix": candidate_fix,
        "eval_receipt": eval_receipt,
        "review_packet": review_packet,
    }


def write_json(path: Path, obj: Any) -> None:
    path.write_text(
        json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--epoch-id", required=True)
    parser.add_argument("--logdir", required=True)
    args = parser.parse_args()

    logdir = Path(args.logdir)
    logdir.mkdir(parents=True, exist_ok=True)

    artifacts = build_artifacts(args.epoch_id, logdir)
    outdir = logdir / "artifacts"
    outdir.mkdir(parents=True, exist_ok=True)

    write_json(outdir / "FAILURE_CLUSTER_V1.json", artifacts["failure_cluster"])
    write_json(outdir / "CANDIDATE_FIX_V1.json", artifacts["candidate_fix"])
    write_json(outdir / "EVAL_RECEIPT_V1.json", artifacts["eval_receipt"])
    write_json(outdir / "REVIEW_PACKET_DRAFT_V1.json", artifacts["review_packet"])

    manifest = {
        "schema": ARTIFACT_VERSION,
        "authority": "NON_SOVEREIGN",
        "canon": "NO_SHIP",
        "epoch_id": args.epoch_id,
        "artifacts": {
            name: {
                "path": str(path),
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
            for name, path in {
                "failure_cluster": outdir / "FAILURE_CLUSTER_V1.json",
                "candidate_fix": outdir / "CANDIDATE_FIX_V1.json",
                "eval_receipt": outdir / "EVAL_RECEIPT_V1.json",
                "review_packet": outdir / "REVIEW_PACKET_DRAFT_V1.json",
            }.items()
        },
        "ledger_effect": "NONE",
        "kernel_writes": "NONE",
    }
    write_json(outdir / "ARTIFACT_MANIFEST.json", manifest)
    print(json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
