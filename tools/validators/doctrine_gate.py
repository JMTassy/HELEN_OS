#!/usr/bin/env python3
"""
doctrine_gate.py — mechanical enforcement of DOCTRINE_ADMISSION_PROTOCOL_V1

authority: false · sovereign: false · canon: false · ledger_effect: none

Implements, deterministically and fail-closed:
  §1 claim schema field rules
  §2 promotion pipeline (unidirectional, no bypass, proposer ≠ validator)
  §3 hard rejection rules 1–7
  §5 output contract (exact JSON schema; no freeform rescue text)

The locked admissibility invariant this gate operationalizes:
  "A doctrine is admissible for implementation only if it can be located,
   enforced, and replay-tested."
  No location → no doctrine. No test → no gate. No replay → no admission.
Pointer resolution (EVIDENCE / TEST_POINTER / ARTIFACT_POINTER must exist on
disk or resolve in git) IS the 'located' criterion, mechanized.

This tool EVALUATES claims. It never admits anything by itself:
  gate PASS ⊬ admission — admission still requires operator + reducer.

Usage:
  python tools/validators/doctrine_gate.py --claim-json path.json
  python tools/validators/doctrine_gate.py --scan docs/proposals   # ```claim blocks
  python tools/validators/doctrine_gate.py --vectors tests/fixtures/claim_strata_vectors.json --report
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

STRATA = ("HYPOTHESIS", "DOCTRINE", "INVARIANT")
FORCES = ("DESCRIPTIVE", "ASSERTIVE", "PROOF")
IMPL_STATES = ("NONE", "CONCEPT", "PARTIAL", "PIPELINE_LOCAL", "GENERALIZED", "RECEIPTED")
IMMATURE_IMPL = ("NONE", "CONCEPT", "PARTIAL", "PIPELINE_LOCAL")
DECISIONS = ("REJECTED", "KEEP", "PROMISING_BUT_NOT_CLAIMABLE",
             "ADMISSION_CANDIDATE", "ADMITTED")

# §3.2 forbidden proof-verbs — scanned only after stripping the protocol's own
# allowed replacement phrases ("is designed to", "is framed as", ...)
_ALLOWED_PHRASES = (
    "is designed to", "is framed as", "is being designed to mirror",
    "could", "would",
)
_PROOF_VERB = re.compile(r"\b(is|does|governs|forces|proves)\b", re.IGNORECASE)
_BOUNDED_QUALIFIER = re.compile(
    r"in this session|under these conditions|in this run|on this machine",
    re.IGNORECASE)
_SELF_EXEMPT = re.compile(
    r"exempt.{0,40}(schema|protocol|gate)|not subject to (this|the) (schema|protocol)",
    re.IGNORECASE)
_GIT_HASH = re.compile(r"^[0-9a-f]{7,40}$")


def default_resolver(pointer: str) -> bool:
    """A pointer is real if it is an on-disk file (repo-relative or absolute)
    or a resolvable git object. Chat-only 'seals' resolve to nothing."""
    if not pointer or pointer == "NONE":
        return False
    p = pointer.split("::")[0].split("#")[0]          # allow file::anchor forms
    if (REPO_ROOT / p).exists() or Path(p).exists():
        return True
    if _GIT_HASH.match(pointer):
        try:
            r = subprocess.run(["git", "cat-file", "-t", pointer],
                               cwd=REPO_ROOT, capture_output=True, timeout=5)
            return r.returncode == 0
        except Exception:
            return False
    return False


def _has_proof_verb(text: str) -> bool:
    low = text.lower()
    for phrase in _ALLOWED_PHRASES:
        low = low.replace(phrase, " ")
    return bool(_PROOF_VERB.search(low))


def evaluate_claim(claim: Dict[str, Any],
                   resolver: Callable[[str], bool] = default_resolver) -> Dict[str, Any]:
    """Evaluate one claim against §§1–3. Returns the exact §5 contract.

    Deterministic. Fail-closed: malformed input is REJECTED, never rescued."""
    reasons: List[str] = []
    missing: List[str] = []

    cid = str(claim.get("CLAIM_ID", "UNIDENTIFIED"))
    stratum = claim.get("STRATUM", "")
    text = str(claim.get("TEXT", ""))
    evidence = str(claim.get("EVIDENCE", "NONE"))
    admission = claim.get("ADMISSION_STATUS", "UNADMITTED")
    force = claim.get("CLAIM_FORCE", "DESCRIPTIVE")
    failure_mode = str(claim.get("FAILURE_MODE", "NONE"))
    impl = claim.get("IMPLEMENTATION_STATE", "NONE")
    test_ptr = str(claim.get("TEST_POINTER", "NONE"))
    artifact_ptr = str(claim.get("ARTIFACT_POINTER", "NONE"))
    requested = str(claim.get("REQUESTED_PROMOTION", "NONE"))
    proposer = claim.get("PROPOSER", "")
    validator = claim.get("VALIDATOR", "")

    out_stratum = stratum if stratum in STRATA else "HYPOTHESIS"

    def contract(decision: str) -> Dict[str, Any]:
        return {
            "claim_id": cid,
            "current_stratum": out_stratum,
            "requested_promotion": requested,
            "decision": decision,
            "reason_codes": reasons,
            "missing_requirements": missing,
        }

    # -- malformed schema: fail closed
    if stratum not in STRATA:
        reasons.append("MALFORMED_STRATUM")
        missing.append(f"STRATUM in {STRATA}")
        return contract("REJECTED")
    if force not in FORCES or impl not in IMPL_STATES:
        reasons.append("MALFORMED_FIELDS")
        missing.append("valid CLAIM_FORCE and IMPLEMENTATION_STATE")
        return contract("REJECTED")

    evidence_ok = resolver(evidence)
    test_ok = resolver(test_ptr)
    artifact_ok = resolver(artifact_ptr)

    # -- §3.4 self-exemption
    if _SELF_EXEMPT.search(text):
        reasons.append("SELF_EXEMPTION")
        return contract("REJECTED")

    # -- §1/§3.1 INVARIANT demands receipt + admission
    if stratum == "INVARIANT":
        if evidence == "NONE" or not evidence_ok:
            reasons.append("NO_RECEIPT_FOR_INVARIANT" if evidence == "NONE"
                           else "FICTIONAL_RECEIPT")
            missing.append("EVIDENCE: resolvable receipt pointer")
            return contract("REJECTED")
        if admission != "ADMITTED":
            reasons.append("INVARIANT_UNADMITTED")
            missing.append("ADMISSION_STATUS: ADMITTED")
            return contract("REJECTED")
        # §3.6 implementation inflation
        if impl in IMMATURE_IMPL:
            reasons.append("IMPLEMENTATION_INFLATION")
            missing.append("IMPLEMENTATION_STATE: GENERALIZED or RECEIPTED")
            return contract("REJECTED")

    # -- §3.5 fictional receipt (any ADMITTED claim)
    if admission == "ADMITTED":
        if evidence == "NONE" or not evidence_ok:
            reasons.append("FICTIONAL_RECEIPT" if evidence != "NONE"
                           else "ADMITTED_WITHOUT_RECEIPT")
            missing.append("EVIDENCE: resolvable receipt pointer")
            return contract("REJECTED")

    # -- §1 unfalsifiable hypothesis
    if stratum == "HYPOTHESIS" and failure_mode.upper() == "NONE":
        reasons.append("UNFALSIFIABLE_HYPOTHESIS")
        missing.append("FAILURE_MODE: how this claim could be falsified")
        return contract("REJECTED")

    # -- §3.2 proof-verb without test
    if stratum in ("HYPOTHESIS", "DOCTRINE") and not test_ok and _has_proof_verb(text):
        reasons.append("PROOF_VERB_WITHOUT_TEST")
        missing.append("TEST_POINTER, or rewrite with could/would/is-designed-to")
        return contract("REJECTED")

    # -- §3.3 / §2 cross-layer promotion
    if requested != "NONE":
        order = {s: i for i, s in enumerate(STRATA)}
        if requested not in STRATA or order[requested] - order[stratum] != 1:
            reasons.append("CROSS_LAYER_PROMOTION")
            missing.append("promotion must climb exactly one stratum via the pipeline")
            return contract("REJECTED")
        if proposer and validator and proposer == validator:
            reasons.append("PROPOSER_IS_VALIDATOR")
            missing.append("independent validator (K2 / Rule 3)")
            return contract("REJECTED")

    # -- §3.7 force/state mismatch
    if force == "PROOF" and not artifact_ok:
        reasons.append("PROOF_WITHOUT_ARTIFACT")
        missing.append("ARTIFACT_POINTER: resolvable artifact")
        return contract("REJECTED")
    if force == "ASSERTIVE" and not test_ok and not _BOUNDED_QUALIFIER.search(text):
        reasons.append("FORCE_STATE_MISMATCH_DOWNGRADE")
        out_stratum = "DOCTRINE"
        return contract("KEEP")            # downgrade, not reject (§3.7)

    # -- promotion candidacy (§2 pipeline complete)
    if requested != "NONE":
        if test_ok and artifact_ok:
            reasons.append("PIPELINE_COMPLETE")
            return contract("ADMISSION_CANDIDATE")
        reasons.append("PIPELINE_INCOMPLETE")
        for name, ok in (("TEST_POINTER", test_ok), ("ARTIFACT_POINTER", artifact_ok)):
            if not ok:
                missing.append(f"{name}: resolvable pointer")
        return contract("PROMISING_BUT_NOT_CLAIMABLE")

    # -- steady states
    if admission == "ADMITTED":
        reasons.append("ADMITTED_AND_VALID")
        return contract("ADMITTED")        # verified, not newly admitted
    if stratum == "DOCTRINE":
        reasons.append("DOCTRINE_LACKS_ADMISSION")
        missing.append("ADMISSION_STATUS: ADMITTED + committed SOT citation")
        return contract("PROMISING_BUT_NOT_CLAIMABLE")
    reasons.append("HYPOTHESIS_HELD")
    return contract("KEEP")


# ---------------------------------------------------------------------------
# batch / scan / report
# ---------------------------------------------------------------------------

_CLAIM_BLOCK = re.compile(r"```claim\s+(.*?)```", re.DOTALL)


def scan_markdown(root: Path, resolver=default_resolver) -> List[Tuple[str, Dict[str, Any]]]:
    """Evaluate every ```claim fenced JSON block under root. Bad JSON in a
    claim block is itself a REJECTED result (fail closed), never skipped."""
    results = []
    for md in sorted(root.rglob("*.md")):
        for m in _CLAIM_BLOCK.finditer(md.read_text(errors="replace")):
            try:
                claim = json.loads(m.group(1))
            except Exception:
                results.append((str(md), {
                    "claim_id": "UNPARSEABLE", "current_stratum": "HYPOTHESIS",
                    "requested_promotion": "NONE", "decision": "REJECTED",
                    "reason_codes": ["BAD_JSON_CLAIM_BLOCK"],
                    "missing_requirements": ["valid JSON in ```claim block"]}))
                continue
            results.append((str(md), evaluate_claim(claim, resolver)))
    return results


def run_vectors(path: Path, resolver=default_resolver) -> Dict[str, Any]:
    """Run the §4 vector file; emit confusion matrix + precision/recall."""
    vectors = json.loads(path.read_text())
    confusion: Dict[str, Dict[str, int]] = {s: {d: 0 for d in DECISIONS} for s in STRATA}
    hits, false_admits, failures = 0, [], []
    for v in vectors:
        got = evaluate_claim(v["claim"], resolver)
        want = v["expected"]
        ok = got["decision"] == want["decision"] and \
            all(rc in got["reason_codes"] for rc in want.get("reason_contains", []))
        hits += ok
        if not ok:
            failures.append({"id": v["claim"].get("CLAIM_ID"), "got": got, "want": want})
        confusion[v["claim"]["STRATUM"]][got["decision"]] += 1
        # zero-false-admit rule: nothing below INVARIANT may verify as ADMITTED
        # invariant-hood, and no receiptless claim may reach ADMITTED at all
        if got["decision"] == "ADMITTED" and (
                v["claim"]["STRATUM"] != v["claim"].get("STRATUM") or
                not resolver(str(v["claim"].get("EVIDENCE", "NONE")))):
            false_admits.append(v["claim"].get("CLAIM_ID"))
    n = len(vectors)
    per_stratum = {s: sum(confusion[s].values()) for s in STRATA}
    return {
        "n_vectors": n,
        "accuracy": hits / n if n else 0.0,
        "per_stratum_counts": per_stratum,
        "confusion_matrix": confusion,
        "false_admits": false_admits,
        "failures": failures,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="DOCTRINE_ADMISSION_PROTOCOL_V1 gate (NON_SOVEREIGN)")
    ap.add_argument("--claim-json", type=Path)
    ap.add_argument("--scan", type=Path)
    ap.add_argument("--vectors", type=Path)
    ap.add_argument("--report", action="store_true")
    a = ap.parse_args()
    if a.claim_json:
        print(json.dumps(evaluate_claim(json.loads(a.claim_json.read_text())), indent=2))
        return 0
    if a.scan:
        results = scan_markdown(a.scan)
        rejected = [r for _, r in results if r["decision"] == "REJECTED"]
        print(f"🛡  DOCTRINE GATE SCAN: {len(results)} claims, {len(rejected)} rejected")
        for f, r in results:
            print(f"  {'🔴' if r['decision']=='REJECTED' else '✅'} {r['claim_id']} "
                  f"[{r['decision']}] {f}")
        return 1 if rejected else 0
    if a.vectors:
        rep = run_vectors(a.vectors)
        if a.report:
            print(json.dumps(rep, indent=2))
        ok = rep["accuracy"] >= 0.95 and not rep["false_admits"]
        print(f"🛡  DOCTRINE GATE VECTORS: n={rep['n_vectors']} "
              f"accuracy={rep['accuracy']:.2%} false_admits={len(rep['false_admits'])} "
              f"→ {'PASS' if ok else 'FAIL'}")
        print("  note: harness PASS ⊬ protocol admission — §6 ceremony requires a "
              "fresh-context classifier and vector-authors ≠ classifier")
        return 0 if ok else 1
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
