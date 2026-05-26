#!/usr/bin/env python3
"""
mayor_readiness_check.py — V0 read-only admission-readiness scanner.

INVARIANT: READINESS IS NOT ADMISSION.

Checks an object (doctrine markdown or M2 receipt JSON) against:
  - the six admission conjuncts in MAYOR_ADMISSION_PROTOCOL_V0 §3
  - the system-level prerequisites for MAYOR to exist at all
  - the suspicious-events resolution requirement from §7

Reports READY / NOT_READY with enumeration of missing receipts.

DOES NOT
  - seal anything
  - admit anything
  - mutate canon
  - write to helensh/.state/admitted_canon.jsonl (which under §13.3 default
    must NOT exist; presence is an anomaly the scanner reports)
  - change lifecycle_entry on any receipt
  - override RAW
  - bootstrap MAYOR
  - call the model

Build the shadow of the crown before touching the crown.

USAGE
=====
  python tools/mayor_readiness_check.py --object <path>

  Examples:
    python tools/mayor_readiness_check.py \\
        --object docs/proposals/MAYOR_ADMISSION_PROTOCOL_V0.md

    python tools/mayor_readiness_check.py \\
        --object GOVERNANCE/GEMMA_PROPOSALS/gemma_proposal_X.json

HARD BOUNDARY (V0 — Phase 2 lock)
==================================
  No --seal, --admit, --bootstrap, --override flags exist.
  Adding any of these is a future amendment, not a V0 patch.
  This tool ONLY observes. It cannot grant. It cannot deny. It cannot mutate.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


# ── Constants ─────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).resolve().parents[1]

# Under §13.3 default this file must NOT exist. If it does, it is an anomaly.
ADMITTED_CANON_PATH = REPO_ROOT / "helensh" / ".state" / "admitted_canon.jsonl"

# Where bootstrap election receipts would live (currently doesn't exist).
BOOTSTRAP_ELECTIONS_DIR = REPO_ROOT / "GOVERNANCE" / "BOOTSTRAP_ELECTIONS"

# The eventual MAYOR tool — its presence is a system prerequisite signal.
MAYOR_ADMISSION_TOOL = REPO_ROOT / "tools" / "mayor_admission.py"

# §5.2 / §6.2 — minimum notes length for HAL and operator annotations.
MIN_NOTES_LENGTH = 32


# ── Tolerant text/JSON read ───────────────────────────────────────────

def _read_tolerant(path: Path) -> str:
    raw = path.read_bytes()
    for enc in ("utf-8", "cp1252"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


# ── Object classification ─────────────────────────────────────────────

def classify_object(path: Path) -> str:
    """Return 'doctrine_markdown', 'm2_receipt_json', 'missing', or 'unknown'."""
    if not path.exists():
        return "missing"
    if path.suffix.lower() == ".md":
        return "doctrine_markdown"
    if path.suffix.lower() == ".json":
        return "m2_receipt_json"
    return "unknown"


def load_object_metadata(path: Path, kind: str) -> dict:
    """Extract a normalized metadata dict from either kind of object."""
    if kind == "doctrine_markdown":
        text = _read_tolerant(path)
        meta: dict = {
            "_raw_text_length": len(text),
            "operator_decision": None,
            "hal_verdict": None,
            "annotation_events": [],
            "envelope_complete": True,  # doctrines have their own envelope
        }
        # Crude frontmatter scrape — looks at first 40 lines
        for line in text.split("\n")[:40]:
            stripped = line.strip().strip("*").strip()
            for key in ("authority", "canon", "lifecycle",
                        "implementation_status", "auto_promotion_ceiling",
                        "status", "lifecycle_entry"):
                low = stripped.lower()
                if low.startswith(f"{key}:"):
                    val = stripped.split(":", 1)[-1].strip().strip("*").strip()
                    meta[key] = val
        # Normalize lifecycle field — doctrines use 'lifecycle' not 'lifecycle_entry'
        if "lifecycle_entry" not in meta and "lifecycle" in meta:
            meta["lifecycle_entry"] = meta["lifecycle"]
        return meta

    if kind == "m2_receipt_json":
        try:
            return json.loads(_read_tolerant(path))
        except json.JSONDecodeError as e:
            return {"_parse_error": str(e)}

    return {}


# ── Per-conjunct checks (§3) ──────────────────────────────────────────

def check_valid_receipts(meta: dict, kind: str) -> tuple[str, str]:
    """§3 conjunct 1: receipt fields valid + lifecycle RAW + authority False."""
    lifecycle = meta.get("lifecycle_entry") or meta.get("lifecycle") or ""
    lifecycle_str = str(lifecycle).upper()
    if not lifecycle_str:
        return "FAIL", "no lifecycle_entry / lifecycle field detected"
    if "RAW" not in lifecycle_str and "DRAFT" not in lifecycle_str:
        return "FAIL", f"lifecycle is not RAW or DRAFT: {lifecycle!r}"

    if kind == "m2_receipt_json":
        if not meta.get("envelope_complete"):
            return "FAIL", "envelope_complete is false"
        # Authority must be structurally false on every M2 receipt
        if meta.get("authority") not in (False, None):
            return "FAIL", f"authority is not False: {meta.get('authority')!r}"

    return "PASS", f"lifecycle={lifecycle!r}"


def check_hal_pass(meta: dict) -> tuple[str, str]:
    """§3 conjunct 2 / §5: hal_verdict.status == PASS with non-trivial notes."""
    hal = meta.get("hal_verdict")
    if not hal:
        return "FAIL", "no hal_verdict written (HAL has not reviewed)"
    if isinstance(hal, str):
        return "FAIL", f"hal_verdict is a bare string, not a structured dict"
    status = hal.get("status")
    if status != "PASS":
        return "FAIL", f"hal_verdict.status = {status!r} (need 'PASS')"
    notes = hal.get("notes") or ""
    if len(notes) < MIN_NOTES_LENGTH:
        return "FAIL", (f"hal_verdict.notes too short "
                       f"({len(notes)} chars, need ≥{MIN_NOTES_LENGTH})")
    return "PASS", f"HAL PASS by {hal.get('reviewer', '?')!r}, notes={len(notes)} chars"


def check_operator_intent(meta: dict) -> tuple[str, str]:
    """§3 conjunct 3 / §6: operator_decision.status == APPROVED_FOR_SANDBOX_ONLY."""
    op = meta.get("operator_decision")
    if not op:
        return "FAIL", "no operator_decision written"
    if isinstance(op, str):
        return "FAIL", "operator_decision is a bare string, not a structured dict"
    status = op.get("status")
    if status != "APPROVED_FOR_SANDBOX_ONLY":
        return "FAIL", (f"operator_decision.status = {status!r} "
                       f"(need 'APPROVED_FOR_SANDBOX_ONLY')")
    notes = op.get("notes") or ""
    if len(notes) < MIN_NOTES_LENGTH:
        return "FAIL", (f"operator_decision.notes too short "
                       f"({len(notes)} chars, need ≥{MIN_NOTES_LENGTH})")
    return "PASS", f"operator APPROVED by {op.get('reviewer', '?')!r}, notes={len(notes)} chars"


def check_replay_pass(meta: dict) -> tuple[str, str]:
    """§3 conjunct 4 / §8: REPLAY_ATTESTATION_V1 receipt exists for this object."""
    # V0 fact: the REPLAY_ATTESTATION_V1 schema is referenced by
    # MAYOR_ADMISSION_PROTOCOL_V0 §4.4 but has not been drafted.
    # Therefore no replay receipt can exist for any object yet.
    return "FAIL", ("REPLAY_ATTESTATION_V1 schema not yet drafted; "
                    "no replay receipt possible for any object in V0")


def check_no_suspicious_events(meta: dict) -> tuple[str, str]:
    """§3 conjunct 5 / §7: annotation_events has no UNRESOLVED suspicious entries."""
    events = meta.get("annotation_events") or []
    if not events:
        # No events at all — vacuously satisfies "no unresolved suspicious"
        # (but flag in scanner output that no audit trail exists yet)
        return "PASS", "no annotation_events (vacuously clean)"

    # Detect suspicious patterns + collect resolution-event coverage
    resolved_indices: set[int] = set()
    suspicious: list[tuple[int, str]] = []

    for i, ev in enumerate(events):
        lane = ev.get("lane", "")

        # Resolution events mark their target by index
        if lane == "resolution":
            nxt = ev.get("next") if isinstance(ev.get("next"), dict) else {}
            refers = nxt.get("refers_to_event_index")
            if isinstance(refers, int):
                resolved_indices.add(refers)
            continue

        prev = ev.get("previous")
        nxt = ev.get("next")
        prev_status = prev.get("status") if isinstance(prev, dict) else None
        next_status = nxt.get("status") if isinstance(nxt, dict) else None

        if lane == "hal_verdict":
            if prev_status == "PASS" and next_status != "PASS":
                suspicious.append((i, "HAL downgrade"))
            elif prev_status and next_status is None:
                suspicious.append((i, "HAL clobber"))
        elif lane == "operator_decision":
            if (prev_status == "APPROVED_FOR_SANDBOX_ONLY"
                    and next_status != "APPROVED_FOR_SANDBOX_ONLY"):
                suspicious.append((i, "operator downgrade"))
            elif prev_status == "REJECTED" and next_status != "REJECTED":
                suspicious.append((i, "operator reversal"))

    unresolved = [(i, w) for i, w in suspicious if i not in resolved_indices]
    if unresolved:
        details = ", ".join(f"#{i}({w})" for i, w in unresolved)
        return "FAIL", f"{len(unresolved)} unresolved suspicious event(s): {details}"
    return "PASS", (f"{len(events)} events, {len(suspicious)} suspicious, "
                   f"all resolved")


def check_mayor_seal_possible() -> tuple[str, str]:
    """§3 conjunct 6 / §9: MAYOR identity exists and could produce a seal.

    Under §13.3 default this is structurally impossible.
    """
    if not ADMITTED_CANON_PATH.exists():
        return "BLOCKED", (
            "admitted_canon.jsonl does not exist (correct under §13.3 default — "
            "no MAYOR identity has ever been admitted)"
        )
    # The file existing without proper bootstrap is itself a §10 #6 anomaly
    return "BLOCKED", (
        f"admitted_canon.jsonl exists at {ADMITTED_CANON_PATH.relative_to(REPO_ROOT)} "
        f"but V0 cannot verify MAYOR identity without --object-specific seal lookup"
    )


# ── System-level prerequisite check ───────────────────────────────────

def check_system_prerequisites() -> dict:
    """System-level facts that must hold for ANY admission to be possible."""
    out: dict[str, str] = {}

    # Bootstrap election receipt
    if BOOTSTRAP_ELECTIONS_DIR.exists() and any(BOOTSTRAP_ELECTIONS_DIR.iterdir()):
        out["bootstrap_election_receipt"] = (
            f"PRESENT (files in {BOOTSTRAP_ELECTIONS_DIR.relative_to(REPO_ROOT)}/)"
        )
    else:
        out["bootstrap_election_receipt"] = (
            "MISSING (no BOOTSTRAP_ELECTION_V0 receipt; election not performed)"
        )

    # MAYOR identity (A5 admitted)
    out["MAYOR_identity_A5_admitted"] = (
        "MISSING (no A5 identity admissions performed in any session)"
    )

    # MAYOR_ADMISSION_RECEIPT_V1 schema admitted
    out["MAYOR_seal_schema_admitted"] = (
        "MISSING (MAYOR_ADMISSION_RECEIPT_V1 schema not built; "
        "referenced in MAYOR_ADMISSION_PROTOCOL_V0 §9 only)"
    )

    # admitted_canon ledger
    if ADMITTED_CANON_PATH.exists():
        out["admitted_canon_ledger"] = (
            f"ANOMALY: file EXISTS at "
            f"{ADMITTED_CANON_PATH.relative_to(REPO_ROOT)} "
            f"— under §13.3 default it must NOT exist"
        )
    else:
        out["admitted_canon_ledger"] = "ABSENT (correct under §13.3 default)"

    # mayor_admission.py tool
    if MAYOR_ADMISSION_TOOL.exists():
        out["mayor_admission_tool"] = (
            f"PRESENT at {MAYOR_ADMISSION_TOOL.relative_to(REPO_ROOT)}"
        )
    else:
        out["mayor_admission_tool"] = (
            "MISSING (tool/mayor_admission.py not built; no seal mechanism exists)"
        )

    return out


# ── Main ──────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--object",
        required=True,
        metavar="PATH",
        help="Path to the candidate object (markdown doctrine or JSON receipt). "
             "Relative paths resolve against the repo root.",
    )
    args = parser.parse_args()

    raw_path = Path(args.object)
    path = raw_path if raw_path.is_absolute() else (REPO_ROOT / raw_path)
    kind = classify_object(path)

    bar = "=" * 60
    print("MAYOR READINESS CHECK V0")
    print("READINESS IS NOT ADMISSION.")
    print(bar)
    print(f"object:     {args.object}")
    print(f"resolved:   {path}")
    print(f"kind:       {kind}")

    if kind == "missing":
        print()
        print("status:  NOT_READY")
        print("verdict: NO ADMISSION POSSIBLE — object file does not exist.")
        return 0

    if kind == "unknown":
        print()
        print("status:  NOT_READY")
        print(f"verdict: NO ADMISSION POSSIBLE — unsupported file type "
              f"{path.suffix!r}; expected .md or .json")
        return 0

    meta = load_object_metadata(path, kind)
    if "_parse_error" in meta:
        print()
        print(f"status:  NOT_READY (parse error: {meta['_parse_error']})")
        print("verdict: NO ADMISSION POSSIBLE")
        return 0

    # ── System prerequisites ───────────────────────────────────────────
    print()
    print("SYSTEM PREREQUISITES (must hold for ANY admission):")
    sys_pre = check_system_prerequisites()
    for key, val in sys_pre.items():
        print(f"  {key}: {val}")

    # ── Per-conjunct evaluation ────────────────────────────────────────
    print()
    print("PER-CONJUNCT EVALUATION (MAYOR_ADMISSION_PROTOCOL_V0 §3):")

    conjuncts: list[tuple[str, tuple[str, str]]] = [
        ("valid_receipts",       check_valid_receipts(meta, kind)),
        ("HAL_PASS",             check_hal_pass(meta)),
        ("operator_intent",      check_operator_intent(meta)),
        ("replay_pass",          check_replay_pass(meta)),
        ("no_suspicious_events", check_no_suspicious_events(meta)),
        ("MAYOR_SEAL_possible",  check_mayor_seal_possible()),
    ]
    for name, (status, reason) in conjuncts:
        print(f"  {name:24s} {status:8s} — {reason}")

    # ── Verdict ────────────────────────────────────────────────────────
    print()
    all_conjuncts_pass = all(s == "PASS" for _, (s, _) in conjuncts)
    sys_pre_blockers = [
        k for k, v in sys_pre.items()
        if "MISSING" in v or "ANOMALY" in v
    ]

    if all_conjuncts_pass and not sys_pre_blockers:
        print("status:  READY")
        print()
        print("verdict: ALL PRECONDITIONS MET")
        print("         (Admission still requires the operator to explicitly run")
        print("          the bootstrap election + MAYOR seal — out of scope for V0.)")
    else:
        print("status:  NOT_READY")
        print()
        missing_conjuncts = [name for name, (s, _) in conjuncts if s != "PASS"]
        if missing_conjuncts:
            print("missing per-conjunct:")
            for m in missing_conjuncts:
                print(f"  - {m}")
        if sys_pre_blockers:
            print("missing system prerequisites:")
            for k in sys_pre_blockers:
                print(f"  - {k}")
        print()
        print("verdict: NO ADMISSION POSSIBLE")

    return 0


if __name__ == "__main__":
    sys.exit(main())
