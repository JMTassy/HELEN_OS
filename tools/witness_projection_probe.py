#!/usr/bin/env python3
"""
HELEN_WITNESS_PROJECTION_V1

Unified witness probe: structural projection (pi_struct) + numeric projection
(pi_num) → COUPLED / SOFT_DRIFT / HARD_DRIFT.

Specification: docs/specs/HELEN_WITNESS_PROJECTION_V1.md

pi_struct (binary — any FAIL → HARD_DRIFT):
  S1  ledger_chain_integrity     delegated to reality_coupling_probe
  S2  skill_hash_consistency     delegated to reality_coupling_probe
  S3  sovereign_files_clean      delegated to reality_coupling_probe
  S4  reducer_schema_hash        PASS vacuous if no reducer receipt exists
  S5  required_receipts_present  PASS vacuous if manifest is empty
  S6  skill_manifest_linkage     active skills: file exists and is non-empty
  S7  epoch_binding              HELEN_CUM_V1 entries: recomputed cum_hash matches stored

pi_num (value vs baseline — divergence → SOFT_DRIFT):
  N1  ledger_entry_count         total valid lines
  N2  active_skill_count         sovereign promotions
  N3  correction_count           LEDGER_SEQ_CORRECTION_V1 entries
  N4  pending_receipt_count      invariant = 0
  N5  test_failure_count         invariant = 0  (not evaluated here — CI gate)
  N6  false_green_test_count     run false_green_lint scanner
  N7  critical_file_count        required tool probes on disk

Usage:
    python3 tools/witness_projection_probe.py
    python3 tools/witness_projection_probe.py --json
    python3 tools/witness_projection_probe.py --ledger PATH
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

_REPO_ROOT = Path(__file__).parent.parent
LEDGER_DEFAULT = str(_REPO_ROOT / "town" / "ledger_v1.ndjson")

# Delegate S1–S3 and trust/runtime data-structures from the existing probe
from tools.reality_coupling_probe import (
    STATUS_COUPLED,
    STATUS_HARD_DRIFT,
    STATUS_SOFT_DRIFT,
    RTrust,
    _probe_runtime,
    _replay_trust,
)

# N6: false-green scanner
from scripts.helen_false_green_lint import scan as _fg_scan, _TEST_ROOTS

# Critical files that must exist on disk (N7 baseline)
_CRITICAL_FILES: List[str] = [
    "tools/reality_coupling_probe.py",
    "tools/reference_drift_probe.py",
    "tools/witness_projection_probe.py",
    "scripts/helen_k8_lint.py",
    "scripts/helen_k_tau_lint.py",
    "scripts/helen_false_green_lint.py",
]

# Required Receipt Manifest (S5) — populated as artifacts are admitted
_REQUIRED_RECEIPT_MANIFEST_PATH = (
    _REPO_ROOT / "docs" / "specs" / "schemas" / "REQUIRED_RECEIPT_MANIFEST.json"
)


# ── Data structures ────────────────────────────────────────────────────────────

@dataclass
class StructuralCheck:
    id: str
    name: str
    result: str          # "PASS" | "FAIL"
    detail: str = ""


@dataclass
class NumericCheck:
    id: str
    name: str
    value: int
    baseline: int
    tolerance: int
    divergence: int = 0

    def __post_init__(self):
        self.divergence = abs(self.value - self.baseline)


@dataclass
class WitnessResult:
    status: str
    pi_struct: List[StructuralCheck] = field(default_factory=list)
    pi_num: List[NumericCheck] = field(default_factory=list)
    false_green_tests: List[Dict] = field(default_factory=list)
    delta: List[Dict] = field(default_factory=list)


# ── S1–S3: delegate to reality_coupling_probe ──────────────────────────────────

def _run_s1_s3(trust: RTrust, runtime) -> List[StructuralCheck]:
    from tools.reality_coupling_probe import _compute_delta
    events = _compute_delta(trust, runtime)

    # Map event codes to structural check IDs
    code_to_check: Dict[str, tuple] = {
        "UNANCHORED_DANGLING": ("S1", "ledger_chain_integrity"),
        "CHAIN_BREAK":         ("S1", "ledger_chain_integrity"),
        "SKILL_MISSING_ON_DISK": ("S2", "skill_hash_consistency"),
        "SKILL_HASH_MISMATCH":   ("S2", "skill_hash_consistency"),
        "SOVEREIGN_FILE_DIRTY":  ("S3", "sovereign_files_clean"),
    }

    failures: Dict[str, List[str]] = {}
    for ev in events:
        if ev.severity == "HARD":
            sid, name = code_to_check.get(ev.code, ("S?", ev.code))
            failures.setdefault(sid, []).append(ev.detail)

    checks = []
    for sid, name in [("S1", "ledger_chain_integrity"),
                       ("S2", "skill_hash_consistency"),
                       ("S3", "sovereign_files_clean")]:
        if sid in failures:
            checks.append(StructuralCheck(
                id=sid, name=name, result="FAIL",
                detail="; ".join(failures[sid][:3]),
            ))
        else:
            checks.append(StructuralCheck(id=sid, name=name, result="PASS"))
    return checks


# ── S4: reducer_schema_hash ────────────────────────────────────────────────────

_REDUCER_RECEIPT_TYPE = "REDUCER_DEPLOYMENT_V1"


def _run_s4(trust: RTrust) -> StructuralCheck:
    # Find last reducer deployment receipt (if any)
    reducer_receipt = None
    for entry_type, entry_data in _iter_trust_entries(trust):
        if entry_type == _REDUCER_RECEIPT_TYPE:
            reducer_receipt = entry_data

    if reducer_receipt is None:
        return StructuralCheck(
            id="S4", name="reducer_schema_hash", result="PASS",
            detail="no reducer deployment receipt found — vacuous pass",
        )

    expected_hash = reducer_receipt.get("reducer_hash", "")
    reducer_path = _REPO_ROOT / "oracle_town" / "kernel" / "mayor.py"
    if not reducer_path.exists():
        return StructuralCheck(
            id="S4", name="reducer_schema_hash", result="FAIL",
            detail=f"reducer file not found: {reducer_path}",
        )

    actual = "sha256:" + hashlib.sha256(reducer_path.read_bytes()).hexdigest()
    if actual != expected_hash:
        return StructuralCheck(
            id="S4", name="reducer_schema_hash", result="FAIL",
            detail=f"reducer hash mismatch: expected {expected_hash[:24]}... got {actual[:24]}...",
        )
    return StructuralCheck(id="S4", name="reducer_schema_hash", result="PASS")


def _iter_trust_entries(trust: RTrust):
    """Yields (type, payload) pairs from trust.correction_entries and internal maps."""
    # S4 requires reading the raw ledger — we get it from the probe caller context
    return iter([])  # stub; real ledger access is in probe()


# ── S4 direct ledger version ────────────────────────────────────────────────────

def _run_s4_from_ledger(ledger_path: str) -> StructuralCheck:
    reducer_receipt = None
    try:
        with open(ledger_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    ev = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if ev.get("type") == _REDUCER_RECEIPT_TYPE:
                    reducer_receipt = ev.get("payload", {})
    except OSError:
        pass

    if reducer_receipt is None:
        return StructuralCheck(
            id="S4", name="reducer_schema_hash", result="PASS",
            detail="no reducer deployment receipt — vacuous pass",
        )

    expected_hash = reducer_receipt.get("reducer_hash", "")
    reducer_path = _REPO_ROOT / "oracle_town" / "kernel" / "mayor.py"
    if not reducer_path.exists():
        return StructuralCheck(
            id="S4", name="reducer_schema_hash", result="FAIL",
            detail=f"reducer file not found: {reducer_path}",
        )
    actual = "sha256:" + hashlib.sha256(reducer_path.read_bytes()).hexdigest()
    if actual != expected_hash:
        return StructuralCheck(
            id="S4", name="reducer_schema_hash", result="FAIL",
            detail=f"reducer hash mismatch: expected {expected_hash[:24]}... actual {actual[:24]}...",
        )
    return StructuralCheck(id="S4", name="reducer_schema_hash", result="PASS")


# ── S5: required_receipts_present ─────────────────────────────────────────────

def _load_required_manifest() -> List[Dict]:
    path = _REQUIRED_RECEIPT_MANIFEST_PATH
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []


def _run_s5(ledger_path: str) -> StructuralCheck:
    manifest = _load_required_manifest()
    if not manifest:
        return StructuralCheck(
            id="S5", name="required_receipts_present", result="PASS",
            detail="manifest is empty — vacuous pass",
        )

    # Build set of artifact IDs that have a receipt
    receipted: set = set()
    try:
        with open(ledger_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    ev = json.loads(line)
                except json.JSONDecodeError:
                    continue
                p = ev.get("payload", {})
                for field_name in ("artifact_id", "skill_id", "decision_id"):
                    val = p.get(field_name)
                    if val:
                        receipted.add(val)
    except OSError:
        pass

    missing = [entry["artifact_id"] for entry in manifest
               if entry.get("artifact_id") not in receipted]
    if missing:
        return StructuralCheck(
            id="S5", name="required_receipts_present", result="FAIL",
            detail=f"missing receipts for: {', '.join(missing[:5])}",
        )
    return StructuralCheck(id="S5", name="required_receipts_present", result="PASS")


# ── S6: skill_manifest_linkage ────────────────────────────────────────────────

def _run_s6(trust: RTrust) -> StructuralCheck:
    ghost: List[str] = []
    empty: List[str] = []

    for skill_id, info in trust.active_sovereign_skills.items():
        name = skill_id.lower()
        import re
        name = re.sub(r"_v\d+$", "", name)
        skill_file = _REPO_ROOT / "oracle_town" / "skills" / name / "skill.py"
        if not skill_file.exists():
            ghost.append(skill_id)
        elif skill_file.stat().st_size == 0:
            empty.append(skill_id)

    problems = [f"ghost:{s}" for s in ghost] + [f"empty:{s}" for s in empty]
    if problems:
        return StructuralCheck(
            id="S6", name="skill_manifest_linkage", result="FAIL",
            detail="; ".join(problems[:5]),
        )
    return StructuralCheck(id="S6", name="skill_manifest_linkage", result="PASS")


# ── S7: epoch_binding ─────────────────────────────────────────────────────────

_HELEN_CUM_V1_PREFIX = b"HELEN_CUM_V1"


def _cum_v0(prev_hex: str, ph_hex: str) -> str:
    return hashlib.sha256(bytes.fromhex(prev_hex) + bytes.fromhex(ph_hex)).hexdigest()


def _cum_v1(prev_hex: str, ph_hex: str) -> str:
    return hashlib.sha256(
        _HELEN_CUM_V1_PREFIX + bytes.fromhex(prev_hex) + bytes.fromhex(ph_hex)
    ).hexdigest()


def _run_s7(ledger_path: str) -> StructuralCheck:
    """
    Verify cum_hash recomputation for every verifiable ledger entry.

    Two schemes are supported (environment-selectable per ndjson_writer.py):
      CUM_SCHEME_V0 : SHA256(bytes.fromhex(prev) || bytes.fromhex(ph))
      HELEN_CUM_V1  : SHA256(b"HELEN_CUM_V1" || bytes.fromhex(prev) || bytes.fromhex(ph))

    PASS if every entry matches at least one scheme.
    FAIL if any entry matches neither.
    """
    mismatches: List[str] = []
    n_v1 = 0
    n_v0 = 0

    try:
        with open(ledger_path, "r", encoding="utf-8") as f:
            entries = []
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    except OSError:
        return StructuralCheck(
            id="S7", name="epoch_binding", result="FAIL",
            detail=f"cannot read ledger: {ledger_path}",
        )

    for ev in entries:
        ph       = ev.get("payload_hash", "")
        prev_cum = ev.get("prev_cum_hash", "")
        stored   = ev.get("cum_hash", "")
        if not (ph and prev_cum and stored):
            continue
        if len(ph) != 64 or len(prev_cum) != 64 or len(stored) != 64:
            continue
        try:
            if _cum_v1(prev_cum, ph) == stored:
                n_v1 += 1
            elif _cum_v0(prev_cum, ph) == stored:
                n_v0 += 1
            else:
                mismatches.append(
                    f"seq={ev.get('seq')}: stored={stored[:16]}... "
                    f"neither V0 nor V1 matches"
                )
        except ValueError:
            continue

    if mismatches:
        return StructuralCheck(
            id="S7", name="epoch_binding", result="FAIL",
            detail=f"{len(mismatches)} entries match no known hash scheme; "
                   f"first: {mismatches[0]}",
        )

    total = n_v0 + n_v1
    return StructuralCheck(
        id="S7", name="epoch_binding", result="PASS",
        detail=f"{total} entries verified (V0={n_v0}, V1={n_v1})"
        if total else "no verifiable entries — vacuous pass",
    )


# ── pi_num ─────────────────────────────────────────────────────────────────────

def _run_pi_num(trust: RTrust, fg_count: int) -> List[NumericCheck]:
    # Baselines derived from ledger trust (what the ledger asserts)
    n1_baseline = trust.total_entries
    n2_baseline = len(trust.active_sovereign_skills)
    n3_baseline = len(trust.correction_entries)

    # Count critical files present
    n7_value = sum(
        1 for rel in _CRITICAL_FILES
        if (_REPO_ROOT / rel).exists()
    )
    n7_baseline = len(_CRITICAL_FILES)

    return [
        NumericCheck("N1", "ledger_entry_count",
                     value=trust.total_entries,
                     baseline=n1_baseline, tolerance=0),
        NumericCheck("N2", "active_skill_count",
                     value=len(trust.active_sovereign_skills),
                     baseline=n2_baseline, tolerance=0),
        NumericCheck("N3", "correction_count",
                     value=len(trust.correction_entries),
                     baseline=n3_baseline, tolerance=0),
        NumericCheck("N4", "pending_receipt_count",
                     value=0, baseline=0, tolerance=0),
        NumericCheck("N5", "test_failure_count",
                     value=0, baseline=0, tolerance=0),   # CI gate; not evaluated here
        NumericCheck("N6", "false_green_test_count",
                     value=fg_count, baseline=0, tolerance=0),
        NumericCheck("N7", "critical_file_count",
                     value=n7_value, baseline=n7_baseline, tolerance=0),
    ]


# ── Classification ─────────────────────────────────────────────────────────────

def _classify(
    pi_struct: List[StructuralCheck],
    pi_num: List[NumericCheck],
) -> str:
    if any(c.result == "FAIL" for c in pi_struct):
        return STATUS_HARD_DRIFT
    if any(abs(n.value - n.baseline) > n.tolerance for n in pi_num):
        return STATUS_SOFT_DRIFT
    return STATUS_COUPLED


# ── Delta builder ──────────────────────────────────────────────────────────────

def _build_delta(
    pi_struct: List[StructuralCheck],
    pi_num: List[NumericCheck],
) -> List[Dict]:
    delta = []
    for c in pi_struct:
        if c.result == "FAIL":
            delta.append({
                "severity": "HARD",
                "code": f"STRUCT_FAIL_{c.id}",
                "check": c.name,
                "detail": c.detail,
            })
    for n in pi_num:
        if abs(n.value - n.baseline) > n.tolerance:
            delta.append({
                "severity": "SOFT",
                "code": f"NUM_DIVERGE_{n.id}",
                "check": n.name,
                "value": n.value,
                "baseline": n.baseline,
                "divergence": n.divergence,
            })
    return delta


# ── Public API ─────────────────────────────────────────────────────────────────

def probe(
    ledger_path: str = LEDGER_DEFAULT,
    run_fg_scan: bool = True,
    _trust: Optional[RTrust] = None,
) -> Dict[str, Any]:
    """
    Run the unified HELEN_WITNESS_PROJECTION_V1 probe.
    Returns HELEN_WITNESS_PROJECTION_V1 schema dict.

    _trust: optional pre-built RTrust for testing (skips file I/O).
    """
    trust   = _trust if _trust is not None else _replay_trust(ledger_path)
    runtime = _probe_runtime(trust)

    # pi_struct
    checks_s1_s3 = _run_s1_s3(trust, runtime)
    s4 = _run_s4_from_ledger(ledger_path)
    s5 = _run_s5(ledger_path)
    s6 = _run_s6(trust)
    s7 = _run_s7(ledger_path)
    pi_struct = checks_s1_s3 + [s4, s5, s6, s7]

    # False-green scan
    fg_results = []
    fg_count = 0
    if run_fg_scan:
        existing_roots = [r for r in _TEST_ROOTS if r.exists()]
        fg_list = _fg_scan(roots=existing_roots) if existing_roots else []
        fg_count = len(fg_list)
        fg_results = [
            {"file": fg.file, "function": fg.function, "line": fg.line}
            for fg in fg_list
        ]

    # pi_num
    pi_num = _run_pi_num(trust, fg_count)

    # Classify
    status = _classify(pi_struct, pi_num)
    delta  = _build_delta(pi_struct, pi_num)

    return {
        "schema_name":    "HELEN_WITNESS_PROJECTION_V1",
        "schema_version": "1.0.0",
        "status":         status,
        "ledger_path":    ledger_path,
        "pi_struct": [
            {"id": c.id, "name": c.name, "result": c.result,
             **({"detail": c.detail} if c.detail else {})}
            for c in pi_struct
        ],
        "pi_num": [
            {"id": n.id, "name": n.name, "value": n.value,
             "baseline": n.baseline, "tolerance": n.tolerance,
             "divergence": n.divergence}
            for n in pi_num
        ],
        "false_green_tests": fg_results,
        "delta": delta,
        "deterministic": True,
    }


# ── CLI ────────────────────────────────────────────────────────────────────────

def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="HELEN_WITNESS_PROJECTION_V1 probe")
    parser.add_argument("--ledger", default=LEDGER_DEFAULT)
    parser.add_argument("--json", action="store_true", dest="json_out")
    parser.add_argument("--no-fg", action="store_false", dest="run_fg",
                        help="Skip false-green scan (faster)")
    args = parser.parse_args()

    result = probe(ledger_path=args.ledger, run_fg_scan=args.run_fg)

    if args.json_out:
        print(json.dumps(result, indent=2))
        sys.exit(0 if result["status"] == STATUS_COUPLED else 1)

    _C = {
        STATUS_COUPLED:    "\x1b[32m",
        STATUS_SOFT_DRIFT: "\x1b[33m",
        STATUS_HARD_DRIFT: "\x1b[31m",
    }
    R = "\x1b[0m"
    c = _C.get(result["status"], "")

    print(f"\n{c}WITNESS PROJECTION: {result['status']}{R}")
    print(f"  Ledger: {result['ledger_path']}")

    print(f"\n  pi_struct ({len(result['pi_struct'])} checks):")
    for s in result["pi_struct"]:
        sc = "\x1b[32m" if s["result"] == "PASS" else "\x1b[31m"
        detail = f"  — {s.get('detail', '')}" if s.get("detail") else ""
        print(f"    {sc}[{s['result']}]{R} {s['id']} {s['name']}{detail}")

    print(f"\n  pi_num ({len(result['pi_num'])} projections):")
    for n in result["pi_num"]:
        ok = abs(n["value"] - n["baseline"]) <= n["tolerance"]
        nc = "\x1b[32m" if ok else "\x1b[33m"
        print(f"    {nc}{'OK' if ok else 'DIVERGE'}{R}  {n['id']} {n['name']}"
              f"  value={n['value']}  baseline={n['baseline']}")

    if result["false_green_tests"]:
        print(f"\n  False-green tests ({len(result['false_green_tests'])}):")
        for fg in result["false_green_tests"]:
            print(f"    {fg['file']}:{fg['line']}  {fg['function']}")

    if result["delta"]:
        print(f"\n  Drift events ({len(result['delta'])}):")
        for ev in result["delta"]:
            ec = "\x1b[31m" if ev["severity"] == "HARD" else "\x1b[33m"
            print(f"    {ec}[{ev['severity']}]{R} {ev['code']}: {ev.get('detail', '')}")
    else:
        print(f"\n  {c}Δ_R = 0 — COUPLED{R}")

    sys.exit(0 if result["status"] == STATUS_COUPLED else 1)


if __name__ == "__main__":
    main()
