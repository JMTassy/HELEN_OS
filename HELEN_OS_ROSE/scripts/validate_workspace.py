#!/usr/bin/env python3
"""Workspace validator for HELEN_OS_ROSE.

Checks structure, JSON/JSONL parseability, decision-ledger integrity,
lifecycle transition legality, execution-packet linkage, privacy
classification, forbidden provider/model names, and unsupported authority
claims (via claim_linter). Exits non-zero on failure.

Stdlib only.
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import claim_linter  # noqa: E402

OUTCOMES = {"GO", "HOLD", "REVISE", "REJECT", "RESEARCH"}
EVIDENCE_CLASSES = {"E0", "E1", "E2", "E3", "E4", "E5"}
PRIVACY_CLASSES = {
    "PUBLIC", "INTERNAL_BUSINESS", "CONFIDENTIAL_STRATEGY", "PARTNER_RESTRICTED",
    "PERSONAL_PRIVATE", "MEDICAL_PRIVATE", "LEGAL_PRIVATE", "FINANCIAL_PRIVATE",
}
PACKET_STATUSES = {"PLANNED", "IN_PROGRESS", "BLOCKED", "DONE_UNVERIFIED", "VERIFIED", "ARCHIVED"}

LIFECYCLE_STATES = {
    "PROPOSED", "RESEARCHED", "TESTED", "APPROVED_BY_ROSE",
    "EXECUTED", "VERIFIED", "REJECTED", "HOLD",
}

# Legal lifecycle transitions. APPROVED_BY_ROSE additionally requires an
# explicit Rose decision record (see transition_allowed).
LEGAL_TRANSITIONS = {
    "PROPOSED": {"RESEARCHED", "HOLD", "REJECTED"},
    "RESEARCHED": {"TESTED", "HOLD", "REJECTED"},
    "TESTED": {"APPROVED_BY_ROSE", "HOLD", "REJECTED"},
    "APPROVED_BY_ROSE": {"EXECUTED", "HOLD"},
    "EXECUTED": {"VERIFIED", "HOLD"},
    "HOLD": {"PROPOSED", "RESEARCHED", "TESTED", "REJECTED"},
    "VERIFIED": set(),
    "REJECTED": set(),
}


def transition_allowed(src, dst, rose_decision_id=None, ledger=None):
    """True when src -> dst is legal.

    dst == APPROVED_BY_ROSE requires a decision id that exists in the
    ledger with outcome GO. Nothing else can mint that state.
    """
    if src not in LIFECYCLE_STATES or dst not in LIFECYCLE_STATES:
        return False
    if dst not in LEGAL_TRANSITIONS.get(src, set()):
        return False
    if dst == "APPROVED_BY_ROSE":
        if not rose_decision_id or ledger is None:
            return False
        rec = ledger.get(rose_decision_id)
        return rec is not None and rec.get("outcome") == "GO"
    return True


REQUIRED_PATHS = [
    "README.md", "OPERATING_CONTRACT.md", "CURRENT_STATE.md",
    "strategy/current_thesis.md", "strategy/priority_stack.md",
    "strategy/ninety_day_plan.md", "strategy/assumptions.md",
    "strategy/kill_criteria.md", "strategy/opportunity_register.md",
    "execution/EXECUTION_PACKET_TEMPLATE.md",
    "decisions/ROSE_DECISION_TEMPLATE.md", "decisions/decision_ledger.jsonl",
    "research/open_questions.md", "research/evidence_register.jsonl",
    "research/RESEARCH_PACKET_TEMPLATE.md",
    "receipts/README.md", "receipts/bootstrap_receipt.json",
    "schemas/decision.schema.json", "schemas/execution_packet.schema.json",
    "schemas/evidence.schema.json", "schemas/receipt.schema.json",
    "prompts/strategy.md", "prompts/execution.md",
    "prompts/sovereign_review.md", "prompts/weekly_review.md",
    "scripts/validate_workspace.py", "scripts/create_execution_packet.py",
    "scripts/append_decision.py", "scripts/claim_linter.py",
    "domains/cielo_impact/README.md", "domains/public_brand/README.md",
    "domains/hospitality/README.md", "domains/partnerships_funding/README.md",
    "domains/corporate/README.md", "domains/private/README.md",
]

DECISION_REQUIRED = ["decision_id", "date", "subject", "outcome", "scope",
                     "rationale", "authorized_by"]
PACKET_REQUIRED = ["packet_id", "approved_decision_id", "outcome", "scope",
                   "non_goals", "owner", "inputs", "steps", "artifacts",
                   "acceptance_tests", "stop_conditions", "privacy_class",
                   "status", "receipts"]
EVIDENCE_REQUIRED = ["claim", "evidence_class", "source", "date", "scope",
                     "limitations"]

# Provider/model names must not appear in permanent architecture files.
# Tokens are assembled from fragments so this file passes its own scan
# even though scripts/ is excluded by default.
FORBIDDEN_NAME_TOKENS = [
    "anthro" + "pic", "cla" + "ude", "open" + "ai", "chat" + "gpt",
    "gpt-", "gem" + "ini", "mis" + "tral", "lla" + "ma", "gro" + "k",
    "deep" + "seek", "copi" + "lot", "son" + "net", "op" + "us",
]
FORBIDDEN_SCAN_EXCLUDES = ("scripts/", "tests/")


def _err(errors, msg):
    errors.append(msg)


def load_jsonl(path):
    records = []
    for i, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        records.append((i, json.loads(line)))
    return records


def check_structure(errors):
    for rel in REQUIRED_PATHS:
        if not (ROOT / rel).exists():
            _err(errors, f"missing required path: {rel}")
    for rel in ("execution/active", "execution/archive"):
        if not (ROOT / rel).is_dir():
            _err(errors, f"missing required directory: {rel}")


def check_json_parse(errors):
    for p in sorted(ROOT.rglob("*.json")):
        try:
            json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            _err(errors, f"invalid JSON: {p.relative_to(ROOT)}: {e}")
    for p in sorted(ROOT.rglob("*.jsonl")):
        try:
            load_jsonl(p)
        except json.JSONDecodeError as e:
            _err(errors, f"invalid JSONL: {p.relative_to(ROOT)}: {e}")


def load_ledger_map(errors):
    ledger = {}
    path = ROOT / "decisions" / "decision_ledger.jsonl"
    if not path.exists():
        return ledger
    try:
        records = load_jsonl(path)
    except json.JSONDecodeError:
        return ledger  # reported by check_json_parse
    for lineno, rec in records:
        for field in DECISION_REQUIRED:
            if field not in rec:
                _err(errors, f"decision_ledger line {lineno}: missing field '{field}'")
        did = rec.get("decision_id", f"<line {lineno}>")
        if did in ledger:
            _err(errors, f"decision_ledger line {lineno}: duplicate decision_id {did}")
        if rec.get("outcome") not in OUTCOMES:
            _err(errors, f"decision_ledger line {lineno}: outcome '{rec.get('outcome')}' not in {sorted(OUTCOMES)}")
        if "rose" not in str(rec.get("authorized_by", "")).lower():
            _err(errors, f"decision_ledger line {lineno}: authorized_by must explicitly indicate Rose")
        ledger[did] = rec
    return ledger


def check_packets(errors, ledger):
    for p in sorted((ROOT / "execution" / "active").glob("*.json")):
        try:
            packet = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue  # reported by check_json_parse
        rel = p.relative_to(ROOT)
        for field in PACKET_REQUIRED:
            if field not in packet:
                _err(errors, f"{rel}: missing packet field '{field}'")
        did = packet.get("approved_decision_id")
        if did not in ledger:
            _err(errors, f"{rel}: approved_decision_id '{did}' not found in decision ledger")
        elif ledger[did].get("outcome") != "GO":
            _err(errors, f"{rel}: decision '{did}' outcome is '{ledger[did].get('outcome')}', packet requires GO")
        if packet.get("privacy_class") not in PRIVACY_CLASSES:
            _err(errors, f"{rel}: privacy_class '{packet.get('privacy_class')}' not in {sorted(PRIVACY_CLASSES)}")
        if packet.get("status") not in PACKET_STATUSES:
            _err(errors, f"{rel}: status '{packet.get('status')}' not in {sorted(PACKET_STATUSES)}")
        _check_state_history(errors, rel, packet.get("state_history"), ledger)


def _check_state_history(errors, rel, history, ledger):
    if not history:
        return
    for i in range(1, len(history)):
        src = history[i - 1].get("state")
        dst = history[i].get("state")
        did = history[i].get("decision_id")
        if not transition_allowed(src, dst, rose_decision_id=did, ledger=ledger):
            _err(errors, f"{rel}: illegal lifecycle transition {src} -> {dst}"
                         f" (decision_id={did})")


def check_evidence_register(errors):
    path = ROOT / "research" / "evidence_register.jsonl"
    if not path.exists():
        return
    try:
        records = load_jsonl(path)
    except json.JSONDecodeError:
        return
    for lineno, rec in records:
        for field in EVIDENCE_REQUIRED:
            if field not in rec:
                _err(errors, f"evidence_register line {lineno}: missing field '{field}'")
        if rec.get("evidence_class") not in EVIDENCE_CLASSES:
            _err(errors, f"evidence_register line {lineno}: evidence_class "
                         f"'{rec.get('evidence_class')}' not in {sorted(EVIDENCE_CLASSES)}")


def check_schema_conformance(errors, ledger):
    """Minimal schema conformance: required keys + enum membership."""
    schema_path = ROOT / "schemas" / "decision.schema.json"
    if not schema_path.exists():
        return
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return
    required = schema.get("required", [])
    enums = {k: set(v["enum"]) for k, v in schema.get("properties", {}).items()
             if isinstance(v, dict) and "enum" in v}
    for did, rec in ledger.items():
        for field in required:
            if field not in rec:
                _err(errors, f"decision {did}: fails schema, missing '{field}'")
        for field, allowed in enums.items():
            if field in rec and rec[field] not in allowed:
                _err(errors, f"decision {did}: field '{field}' value '{rec[field]}' not in schema enum")


def check_forbidden_names(errors):
    for p in sorted(ROOT.rglob("*")):
        if not p.is_file() or p.suffix not in (".md", ".json", ".jsonl"):
            continue
        rel = p.relative_to(ROOT).as_posix()
        if any(rel.startswith(x) for x in FORBIDDEN_SCAN_EXCLUDES):
            continue
        text = p.read_text(encoding="utf-8").lower()
        for token in FORBIDDEN_NAME_TOKENS:
            if re.search(r"(?<![a-z0-9])" + re.escape(token), text):
                _err(errors, f"{rel}: contains forbidden provider/model token '{token}'")


def check_privacy_declarations(errors):
    for p in sorted((ROOT / "domains").glob("*/README.md")):
        text = p.read_text(encoding="utf-8")
        if not any(cls in text for cls in PRIVACY_CLASSES):
            _err(errors, f"{p.relative_to(ROOT)}: no privacy class declared")


def check_claims(errors, warnings):
    targets = [str(p) for p in claim_linter.iter_target_files(ROOT)]
    findings = claim_linter.lint_paths(targets, ROOT / "decisions" / "decision_ledger.jsonl")
    for f in findings:
        loc = f"{Path(f['path']).name}:{f['line']}"
        if f["verdict"] == "FLAGGED":
            _err(errors, f"claim_linter FLAGGED {loc} [{f['token']}]: {f['text']}")
        elif f["verdict"] == "UNCLASSIFIED":
            warnings.append(f"claim_linter UNCLASSIFIED {loc} [{f['token']}]: {f['text']}")


def validate(root=None):
    errors, warnings = [], []
    check_structure(errors)
    check_json_parse(errors)
    ledger = load_ledger_map(errors)
    check_packets(errors, ledger)
    check_evidence_register(errors)
    check_schema_conformance(errors, ledger)
    check_forbidden_names(errors)
    check_privacy_declarations(errors)
    check_claims(errors, warnings)
    return errors, warnings


def main():
    errors, warnings = validate()
    for w in warnings:
        print(f"WARN  {w}")
    for e in errors:
        print(f"ERROR {e}")
    print(f"validate_workspace: {len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
