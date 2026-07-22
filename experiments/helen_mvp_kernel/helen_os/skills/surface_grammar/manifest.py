"""
Surface Grammar Skill — Manifest V1

NON_SOVEREIGN · authority=false · NO_CLAIM · ledger_effect=none

Detects CSS governance-color leakage in HTML surface files that declare
authority=false. Enforces the Source Atlas one-meaning-per-color invariant
and the WULMOJI Status Rendering Rule (CLAUDE.md).

Run:  python manifest.py [--format json|yaml]
"""
from __future__ import annotations

import argparse
import json
import sys

SKILL_ID = "surface_grammar_v1"
VERSION = "0.1.0"
AUTHORITY = False
CLAIM_STATUS = "NO_CLAIM"
LEDGER_EFFECT = "none"
SCHEMA = "SKILL_MANIFEST_V1"

GATES = ["check_leakage", "score_runs"]

INPUT_SPEC = {
    "path_glob": {
        "type": "str",
        "default": "apps/helen-surface/**/*.html",
        "description": "Glob of HTML surface files to scan",
    },
    "repo_root": {
        "type": "str",
        "default": ".",
        "description": "Repo root for resolving relative globs",
    },
    "output_format": {
        "type": "str",
        "enum": ["json", "yaml"],
        "default": "json",
        "description": "Output serialisation format",
    },
    "pass_threshold": {
        "type": "int",
        "default": 0,
        "description": "Max allowed violations before BLOCK verdict",
    },
}

OUTPUT_SPEC = {
    "violations": {
        "type": "list",
        "items": {
            "file": "str",
            "line": "int",
            "selector": "str",
            "token": "str",
            "semantic_meaning": "str",
        },
        "description": "CSS governance-color leakage events",
    },
    "score": {
        "type": "float",
        "range": [0.0, 1.0],
        "description": "1.0 = clean; 0.0 = all candidates violated",
    },
    "verdict": {
        "type": "str",
        "enum": ["PASS", "BLOCK"],
        "description": "PASS only when violations == 0",
    },
}

# Tokens that carry the ADMITTED (#00ff88) governance meaning in Source Atlas.
# Any of these in a CSS rule body triggers leakage detection.
GOVERNANCE_GREEN_TOKENS = [
    "#00ff88",
    "#00ff41",
    "--green",
    "--grn",
    "--g:",
    "--g2:",
]

# CSS selector substrings that imply a non-governance semantic state.
# A green rule targeting any of these is a leakage candidate.
SEMANTIC_STATE_KEYWORDS = [
    "live",
    "done",
    "committed",
    "shipped",
    "go",
    "active",
    "success",
    "complete",
    "approved",
    "pulse",
]
# "verdict" intentionally excluded: .verdict-admitted is a legitimate
# governance-color use (displaying an admitted item). Selectors like
# .station-verdict.go are caught by the "go" keyword instead.

# HTML patterns that confirm a file declares authority=false.
AUTHORITY_FALSE_PATTERNS = [
    "authority=false",
    "authority: false",
    "authority:false",
    "AUTHORITY: FALSE",
    "authority <b class=\"red\">false</b>",
]


def as_dict() -> dict:
    return {
        "skill_id": SKILL_ID,
        "version": VERSION,
        "authority": AUTHORITY,
        "claim_status": CLAIM_STATUS,
        "ledger_effect": LEDGER_EFFECT,
        "schema": SCHEMA,
        "gates": GATES,
        "input_spec": INPUT_SPEC,
        "output_spec": OUTPUT_SPEC,
        "governance_green_tokens": GOVERNANCE_GREEN_TOKENS,
        "semantic_state_keywords": SEMANTIC_STATE_KEYWORDS,
    }


def _emit(data: dict, fmt: str) -> str:
    if fmt == "yaml":
        try:
            import yaml  # type: ignore[import]
            return yaml.dump(data, sort_keys=False, allow_unicode=True)
        except ImportError:
            print("warning: pyyaml not installed — falling back to JSON", file=sys.stderr)
    return json.dumps(data, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Surface Grammar skill manifest")
    parser.add_argument("--format", choices=["json", "yaml"], default="json")
    args = parser.parse_args()
    print(_emit(as_dict(), args.format))
