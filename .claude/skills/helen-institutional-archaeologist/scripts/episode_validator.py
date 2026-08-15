#!/usr/bin/env python3
"""Validate TRAINING_EXTRACTION episodes before they leave a run.

The membrane this script enforces: ObservedHistory ->
GovernedTrainingProjection, never RawArchive -> Train. An episode is
a governed projection — schema-complete, temporally sound,
provenance-counted, scored on the six verifiers, and free of
restricted material (emails, IBANs, currency figures, raw quotes).

Input (stdin or file arg): JSON list of episodes (schemas in
references/output-contract.md). Output: verdict per episode; exit 1
if any episode fails. Deterministic, stdlib only.
Run `episode_validator.py --selftest` first.
"""
from __future__ import annotations

import json
import re
import sys

SCHEMAS = {
    "recovery_episode": ("state_before", "evidence_available",
                         "tempting_prediction", "later_evidence",
                         "actual_transition", "lesson", "falsifier",
                         "provenance_roots"),
    "causal_bound_episode": ("observation", "naive_cause",
                             "additional_evidence",
                             "authorized_conclusion",
                             "forbidden_conclusion",
                             "provenance_roots"),
}
VERIFIERS = ("V1_execution_vs_outcome", "V2_roots_not_artifacts",
             "V3_no_edgeless_attribution", "V4_blocked_not_terminal",
             "V5_no_unwitnessed_promotion", "V6_no_future_leakage")

# Restricted-material detectors (privacy zone law). Patterns are
# deliberately eager: a false positive costs a pseudonymization pass,
# a false negative leaks into training material.
RESTRICTED_PATTERNS = (
    ("email_address", re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")),
    ("iban", re.compile(r"\b[A-Z]{2}\d{2}[A-Z0-9]{10,30}\b")),
    ("currency_figure", re.compile(
        r"[€$£]\s?\d|\d[\d\s.,]*\s?(?:€|\$|£|k€|K€|EUR\b|USD\b)")),
)
MAX_QUOTE_SPAN = 240  # chars; longer verbatim spans smell like raw archive


def _scan_text(obj) -> list[dict]:
    hits = []
    def walk(x, path):
        if isinstance(x, dict):
            for k, v in sorted(x.items()):
                walk(v, f"{path}.{k}")
        elif isinstance(x, (list, tuple)):
            for i, v in enumerate(x):
                walk(v, f"{path}[{i}]")
        elif isinstance(x, str):
            for name, pat in RESTRICTED_PATTERNS:
                if pat.search(x):
                    hits.append({"kind": name, "at": path})
            if len(x) > MAX_QUOTE_SPAN:
                hits.append({"kind": "raw_span_too_long", "at": path,
                             "len": len(x)})
    walk(obj, "$")
    return hits


def validate_episode(e: dict) -> dict:
    errs = []
    cls = e.get("episode_type")
    if cls not in SCHEMAS:
        return {"ok": False,
                "errors": [{"reason": "E_UNKNOWN_EPISODE_CLASS",
                            "got": cls}]}

    missing = sorted(f for f in SCHEMAS[cls] if f not in e)
    if missing:
        errs.append({"reason": "E_SCHEMA_INCOMPLETE", "missing": missing})

    roots = e.get("provenance_roots", [])
    if not isinstance(roots, list) or not roots:
        errs.append({"reason": "E_NO_PROVENANCE_ROOTS"})
    elif len(roots) != len(set(roots)):
        errs.append({"reason": "E_DUPLICATE_ROOTS_COUNTED_TWICE"})

    if cls == "recovery_episode":
        if e.get("state_before") != "BLOCKED":
            errs.append({"reason": "E_RECOVERY_NEEDS_BLOCKED_START"})
        if e.get("actual_transition") not in ("RECOVERED", "RESUMED"):
            errs.append({"reason": "E_NOT_A_RECOVERY"})
        # The lesson IS the wrongness of the tempting prediction; an
        # episode where the temptation matched reality teaches nothing.
        if e.get("tempting_prediction") == e.get("actual_transition"):
            errs.append({"reason": "E_NO_TEMPTATION_NO_LESSON"})
        if not e.get("later_evidence"):
            errs.append({"reason": "E_RECOVERY_WITHOUT_LATER_EVIDENCE"})

    if cls == "causal_bound_episode":
        if e.get("naive_cause") == e.get("authorized_conclusion"):
            errs.append({"reason": "E_NO_BOUND_ESTABLISHED"})
        if not e.get("forbidden_conclusion"):
            errs.append({"reason": "E_FORBIDDEN_CONCLUSION_UNNAMED"})

    ver = e.get("verifiers")
    if not isinstance(ver, dict):
        errs.append({"reason": "E_VERIFIERS_MISSING"})
    else:
        unknown = sorted(set(ver) - set(VERIFIERS))
        absent = sorted(set(VERIFIERS) - set(ver))
        if unknown:
            errs.append({"reason": "E_UNKNOWN_VERIFIER", "got": unknown})
        if absent:
            errs.append({"reason": "E_VERIFIER_UNSCORED", "missing": absent})
        for k, v in sorted(ver.items()):
            if v not in (True, False):
                errs.append({"reason": "E_VERIFIER_NOT_BOOLEAN", "at": k})
        # V6 is the hard gate: an episode built with future leakage is
        # not repairable by pseudonymization — it is the wrong object.
        if ver.get("V6_no_future_leakage") is False:
            errs.append({"reason": "E_FUTURE_LEAKAGE"})

    leaks = _scan_text({k: v for k, v in e.items() if k != "verifiers"})
    for hit in leaks:
        errs.append({"reason": "E_RESTRICTED_MATERIAL", **hit})

    return {"ok": not errs, "errors": errs}


def validate(episodes: list[dict]) -> dict:
    results = [validate_episode(e) for e in episodes]
    return {"ok": all(r["ok"] for r in results),
            "n_episodes": len(episodes), "results": results}


def _good_recovery() -> dict:
    return {
        "episode_type": "recovery_episode",
        "state_before": "BLOCKED",
        "evidence_available": ["root_1:silence_8w", "root_1:block_notice"],
        "tempting_prediction": "TERMINAL_LOSS",
        "later_evidence": ["root_2:budget_reactivation"],
        "actual_transition": "RECOVERED",
        "lesson": "blocked_not_terminal",
        "falsifier": "a closure receipt dated inside the silence window",
        "provenance_roots": ["root_1", "root_2"],
        "verifiers": {k: True for k in VERIFIERS},
    }


def selftest() -> None:
    assert validate([_good_recovery()])["ok"]

    # Schema holes are named, not tolerated.
    e = _good_recovery(); del e["falsifier"]
    v = validate_episode(e)
    assert {"reason": "E_SCHEMA_INCOMPLETE",
            "missing": ["falsifier"]} in v["errors"]

    # A temptation that came true teaches nothing.
    e = _good_recovery()
    e["tempting_prediction"] = e["actual_transition"] = "RECOVERED"
    assert any(x["reason"] == "E_NO_TEMPTATION_NO_LESSON"
               for x in validate_episode(e)["errors"])

    # Roots are counted as roots.
    e = _good_recovery(); e["provenance_roots"] = ["root_1", "root_1"]
    assert any(x["reason"] == "E_DUPLICATE_ROOTS_COUNTED_TWICE"
               for x in validate_episode(e)["errors"])

    # All six verifiers scored, booleans only, V6 fatal.
    e = _good_recovery(); del e["verifiers"]["V4_blocked_not_terminal"]
    assert any(x["reason"] == "E_VERIFIER_UNSCORED"
               for x in validate_episode(e)["errors"])
    e = _good_recovery(); e["verifiers"]["V6_no_future_leakage"] = False
    assert any(x["reason"] == "E_FUTURE_LEAKAGE"
               for x in validate_episode(e)["errors"])

    # Privacy zone law: emails, IBANs, currency figures, raw spans.
    for field, val, kind in (
            ("lesson", "contact jm@uzik.com", "email_address"),
            ("lesson", "pay FR7630006000011234567890189", "iban"),
            ("lesson", "budget was 100 000 €", "currency_figure"),
            ("lesson", "x" * 300, "raw_span_too_long")):
        e = _good_recovery(); e[field] = val
        errs = validate_episode(e)["errors"]
        assert any(x["reason"] == "E_RESTRICTED_MATERIAL"
                   and x["kind"] == kind for x in errs), (kind, errs)

    # causal_bound: the bound must exist and the forbidden conclusion
    # must be named.
    cb = {"episode_type": "causal_bound_episode",
          "observation": "fidelity below acceptance",
          "naive_cause": "model insufficient",
          "additional_evidence": ["root_1:asset_coverage_gap"],
          "authorized_conclusion":
              "feasibility is multivariate: capability x coverage x scale",
          "forbidden_conclusion": "model quality alone caused failure",
          "provenance_roots": ["root_1"],
          "verifiers": {k: True for k in VERIFIERS}}
    assert validate([cb])["ok"]
    bad = dict(cb); bad["authorized_conclusion"] = bad["naive_cause"]
    assert any(x["reason"] == "E_NO_BOUND_ESTABLISHED"
               for x in validate_episode(bad)["errors"])

    assert validate_episode({"episode_type": "vibes"})["errors"][0][
        "reason"] == "E_UNKNOWN_EPISODE_CLASS"

    # Determinism.
    batch = [_good_recovery(), cb]
    assert json.dumps(validate(batch), sort_keys=True) == \
        json.dumps(validate(batch), sort_keys=True)
    print("episode_validator selftest: OK (13 checks)")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
        sys.exit(0)
    src = sys.argv[1] if len(sys.argv) > 1 else None
    data = json.load(open(src)) if src else json.load(sys.stdin)
    out = validate(data)
    print(json.dumps(out, indent=2, sort_keys=True))
    sys.exit(0 if out["ok"] else 1)
