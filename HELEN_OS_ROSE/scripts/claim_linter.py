#!/usr/bin/env python3
"""Deterministic claim linter for HELEN_OS_ROSE.

Scans Markdown, JSON, and JSONL files for authority-bearing terms that are
not supported by a nearby hedge, evidence marker, or machine-checkable
decision reference.

Verdicts per finding:
  ALLOWED       - term is hedged, evidence-linked, or a verified decision ref
  FLAGGED       - authority-bearing term with no supporting marker
  UNCLASSIFIED  - construct the linter cannot classify; never silently admitted

Stdlib only. Deterministic: same input files -> same findings, same order.

Sovereignty rule enforced here: a generated sentence never becomes an
admitted claim by default. Unknown constructs stay UNCLASSIFIED.
"""

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

OUTCOMES = {"GO", "HOLD", "REVISE", "REJECT", "RESEARCH"}

# Longest-first so multiword terms match before their substrings.
RISKY_TERMS = [
    "scientifically proven",
    "partnered",
    "validated",
    "verified",
    "integrated",
    "implemented",
    "deployed",
    "approved",
    "canonical",
    "official",
    "complete",
    "admitted",
    "customer",
    "partner",
    "sealed",
    "funded",
    "active",
    "ready",
]

def _term_regex(term):
    # \b fails around non-word edges; use explicit lookarounds. Underscore is
    # a word char, so compound tokens like APPROVED_BY_ROSE never match.
    # '/' and '.' adjacency is excluded: path segments (execution/active/)
    # are references, not claims.
    pattern = r"(?<![\w`/.])" + r"\s+".join(re.escape(w) for w in term.split()) + r"(?![\w`/])"
    return re.compile(pattern, re.IGNORECASE)

TERM_REGEXES = [(t, _term_regex(t)) for t in RISKY_TERMS]

HEDGE_RE = re.compile(
    r"(?<!\w)("
    r"hypothes\w*|proposed|propose[sd]?|candidate|prospective|potential|"
    r"unverified|unvalidated|unapproved|not|no|never|without|pending|"
    r"planned|draft|would|could|might|may|must|shall|should|cannot|"
    r"requires?|required|until|unless|if|when|before|target|outreach|"
    r"discovery|template|criterion|criteria|checklist|to be|"
    r"marked? for verification|open question|assum\w*|risk|risks"
    r")(?!\w)",
    re.IGNORECASE,
)

EVIDENCE_RE = re.compile(
    r"(?<![\w])(E[0-5]|R-\d{3}|EV-\d{3}|P-\d{3}|T-\d{3})(?![\w-])"
    r"|receipts/|decision_ledger|evidence_register|evidence_class"
)

DECISION_REF_RE = re.compile(r"decision\s+(R-\d{3})\s+as\s+([A-Z_]+)")

FENCE_RE = re.compile(r"^(```|~~~)")
INLINE_CODE_RE = re.compile(r"`[^`]*`")


def load_ledger(ledger_path):
    """Return {decision_id: outcome} from a decision ledger JSONL file."""
    ledger = {}
    p = Path(ledger_path)
    if not p.exists():
        return ledger
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        did = rec.get("decision_id")
        if did:
            ledger[did] = rec.get("outcome")
    return ledger


def lint_text(text, path="<memory>", ledger=None, skip_fences=True):
    """Lint raw text line by line. Returns a list of finding dicts."""
    ledger = ledger if ledger is not None else {}
    findings = []
    in_fence = False
    for lineno, raw_line in enumerate(text.splitlines(), start=1):
        if skip_fences and FENCE_RE.match(raw_line.strip()):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        # Inline code spans are vocabulary mentions, not claims.
        line = INLINE_CODE_RE.sub(" ", raw_line)

        # 1) Machine-checkable decision references take precedence.
        line_has_verified_ref = False
        for m in DECISION_REF_RE.finditer(line):
            did, outcome = m.group(1), m.group(2)
            if outcome not in OUTCOMES:
                findings.append(_finding(path, lineno, raw_line, m.group(0),
                                         "UNCLASSIFIED",
                                         "unknown outcome token in decision reference"))
                continue
            if ledger.get(did) == outcome:
                line_has_verified_ref = True
                findings.append(_finding(path, lineno, raw_line, m.group(0),
                                         "ALLOWED",
                                         "decision reference matches ledger"))
            else:
                findings.append(_finding(path, lineno, raw_line, m.group(0),
                                         "FLAGGED",
                                         "decision reference not supported by decision ledger"))

        # 2) Risky authority-bearing terms.
        has_hedge = bool(HEDGE_RE.search(line))
        has_evidence = bool(EVIDENCE_RE.search(line)) or line_has_verified_ref
        for term, rx in TERM_REGEXES:
            if not rx.search(line):
                continue
            if has_evidence:
                verdict, why = "ALLOWED", "evidence marker or verified reference on line"
            elif has_hedge:
                verdict, why = "ALLOWED", "hedged / normative phrasing on line"
            else:
                verdict, why = "FLAGGED", "authority-bearing term without receipt, decision id, or hedge"
            findings.append(_finding(path, lineno, raw_line, term, verdict, why))
    return findings


def _finding(path, lineno, line, token, verdict, reason):
    return {
        "path": str(path),
        "line": lineno,
        "token": token,
        "verdict": verdict,
        "reason": reason,
        "text": line.strip()[:200],
    }


DEFAULT_EXCLUDES = ("schemas/", "scripts/", "tests/")


def iter_target_files(root):
    root = Path(root)
    for p in sorted(root.rglob("*")):
        if not p.is_file() or p.suffix not in (".md", ".json", ".jsonl"):
            continue
        rel = p.relative_to(root).as_posix()
        if any(rel.startswith(x) for x in DEFAULT_EXCLUDES):
            continue
        yield p


def lint_paths(paths, ledger_path):
    ledger = load_ledger(ledger_path)
    findings = []
    for p in paths:
        text = Path(p).read_text(encoding="utf-8")
        skip_fences = Path(p).suffix == ".md"
        findings.extend(lint_text(text, path=p, ledger=ledger, skip_fences=skip_fences))
    return findings


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("targets", nargs="*", help="files to lint (default: workspace md/json/jsonl)")
    ap.add_argument("--ledger", default=str(ROOT / "decisions" / "decision_ledger.jsonl"))
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--strict", action="store_true", help="UNCLASSIFIED also fails")
    args = ap.parse_args(argv)

    targets = args.targets or [str(p) for p in iter_target_files(ROOT)]
    findings = lint_paths(targets, args.ledger)
    flagged = [f for f in findings if f["verdict"] == "FLAGGED"]
    unclassified = [f for f in findings if f["verdict"] == "UNCLASSIFIED"]

    if args.json:
        print(json.dumps({"findings": findings,
                          "counts": {"flagged": len(flagged),
                                     "unclassified": len(unclassified),
                                     "allowed": len(findings) - len(flagged) - len(unclassified)}},
                         indent=2))
    else:
        for f in flagged + unclassified:
            print(f"{f['verdict']}: {f['path']}:{f['line']} [{f['token']}] {f['reason']}\n    {f['text']}")
        print(f"claim_linter: {len(flagged)} flagged, {len(unclassified)} unclassified, "
              f"{len(findings) - len(flagged) - len(unclassified)} allowed "
              f"across {len(targets)} file(s)")

    if flagged or (args.strict and unclassified):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
