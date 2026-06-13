#!/usr/bin/env python3
"""
REALITY_COUPLING_WITNESS_V1

Measures the gap between R_trust (what the ledger asserts) and R_runtime
(what the filesystem actually shows). Returns one of three verdicts:

  COUPLED    — Δ_R = 0, no drift detected
  SOFT_DRIFT — minor divergence, non-critical
  HARD_DRIFT — invariant breach, operator attention required

HARD_DRIFT triggers:
  UNANCHORED_DANGLING   — duplicate seq with no anchoring correction entry
  CHAIN_BREAK           — unexplained prev_cum_hash linkage failure
  SKILL_MISSING_ON_DISK — sovereignly active skill's skill.py not found
  SKILL_HASH_MISMATCH   — skill.py SHA256 ≠ candidate_identity_hash at promotion
  SOVEREIGN_FILE_DIRTY  — sovereign path modified outside authorized writer (git)

Usage:
    python3 tools/reality_coupling_probe.py
    python3 tools/reality_coupling_probe.py --ledger PATH
    python3 tools/reality_coupling_probe.py --json    # machine-readable, exit 1 on drift
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

_REPO_ROOT = Path(__file__).parent.parent
LEDGER_DEFAULT = str(_REPO_ROOT / "town" / "ledger_v1.ndjson")
SKILLS_ROOT = _REPO_ROOT / "oracle_town" / "skills"

# Sovereign paths mirroring the firewall hook patterns
_SOVEREIGN_PATTERNS = [
    re.compile(r"oracle_town/kernel(/|$)"),
    re.compile(r"helen_os/governance(/|$)"),
    re.compile(r"helen_os/schemas(/|$)"),
    re.compile(r"town/ledger_v1[^/]*\.ndjson$"),
    re.compile(r"mayor_[^/]*\.json$"),
    re.compile(r"GOVERNANCE/CLOSURES(/|$)"),
    re.compile(r"GOVERNANCE/TRANCHE_RECEIPTS(/|$)"),
]

STATUS_COUPLED    = "COUPLED"
STATUS_SOFT_DRIFT = "SOFT_DRIFT"
STATUS_HARD_DRIFT = "HARD_DRIFT"


@dataclass
class DriftEvent:
    severity: str   # "HARD" | "SOFT"
    code: str
    detail: str
    seq: Optional[int] = None


@dataclass
class RTrust:
    """What the ledger asserts."""
    active_sovereign_skills: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    dangling_cum_hashes: List[str] = field(default_factory=list)
    anchored_cum_hashes: List[str] = field(default_factory=list)
    correction_entries: List[Dict] = field(default_factory=list)
    chain_breaks: List[Dict] = field(default_factory=list)
    total_entries: int = 0


@dataclass
class RRuntime:
    """What the filesystem shows."""
    skill_hashes: Dict[str, Optional[str]] = field(default_factory=dict)
    sovereign_git_dirty: List[str] = field(default_factory=list)


def _sha256_file(path: str) -> Optional[str]:
    try:
        with open(path, "rb") as f:
            return "sha256:" + hashlib.sha256(f.read()).hexdigest()
    except OSError:
        return None


def _skill_id_to_skill_file(skill_id: str) -> Path:
    """REFERENCE_DRIFT_WITNESS_V1 -> oracle_town/skills/reference_drift_witness/skill.py"""
    name = re.sub(r"_V\d+$", "", skill_id).lower()
    return SKILLS_ROOT / name / "skill.py"


def _replay_trust(ledger_path: str) -> RTrust:
    trust = RTrust()
    if not os.path.exists(ledger_path):
        return trust

    entries = []
    with open(ledger_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    trust.total_entries = len(entries)
    if not entries:
        return trust

    # 1. Active sovereign skills — last SKILL_PROMOTION_DECISION_V1 per skill_id
    for ev in entries:
        if ev.get("type") == "SKILL_PROMOTION_DECISION_V1":
            p = ev.get("payload", {})
            if p.get("sovereign_promotion") is True:
                trust.active_sovereign_skills[p["skill_id"]] = {
                    "candidate_identity_hash": p.get("candidate_identity_hash", ""),
                    "decision_id": p.get("decision_id", ""),
                    "seq": ev.get("seq"),
                }

    # 2. Correction anchors
    correction_anchors: set = set()
    for ev in entries:
        if ev.get("type") == "LEDGER_SEQ_CORRECTION_V1":
            p = ev.get("payload", {})
            dangling_cum = p.get("dangling_cum_hash", "")
            if dangling_cum:
                correction_anchors.add(dangling_cum)
            trust.correction_entries.append({
                "seq": ev.get("seq"),
                "correction_id": p.get("correction_id", ""),
                "dangling_seq": p.get("dangling_seq"),
                "dangling_cum_hash": dangling_cum,
            })

    # 3. Dangling classification
    all_prev_cums = {ev.get("prev_cum_hash") for ev in entries}
    tail_cum = entries[-1]["cum_hash"]
    for ev in entries:
        cum = ev.get("cum_hash", "")
        if cum and cum not in all_prev_cums and cum != tail_cum:
            if cum in correction_anchors:
                trust.anchored_cum_hashes.append(cum)
            else:
                trust.dangling_cum_hashes.append(cum)

    # 4. Chain linkage scan (file order)
    for i in range(1, len(entries)):
        prev_ev = entries[i - 1]
        curr_ev = entries[i]
        if curr_ev.get("prev_cum_hash") != prev_ev.get("cum_hash"):
            prev_cum = curr_ev.get("prev_cum_hash", "")
            # If curr's prev_cum links back to any earlier entry it's a known fork
            fork_found = any(e.get("cum_hash") == prev_cum for e in entries[:i])
            if not fork_found:
                trust.chain_breaks.append({
                    "position": i,
                    "seq_prev": prev_ev.get("seq"),
                    "seq_curr": curr_ev.get("seq"),
                    "expected_cum": prev_ev.get("cum_hash"),
                    "actual_prev_cum": prev_cum,
                })

    return trust


def _probe_runtime(trust: RTrust) -> RRuntime:
    runtime = RRuntime()

    # 1. Probe skill.py SHA256 for each active sovereign skill
    for skill_id in trust.active_sovereign_skills:
        skill_file = _skill_id_to_skill_file(skill_id)
        runtime.skill_hashes[skill_id] = _sha256_file(str(skill_file))

    # 2. Git status — sovereign paths modified outside authorized writer
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True, timeout=10,
            cwd=str(_REPO_ROOT),
        )
        for line in result.stdout.splitlines():
            if not line.strip():
                continue
            git_path = line[3:].strip()
            # ledger dirty is expected by design
            if "ledger_v1.ndjson" in git_path:
                continue
            for pat in _SOVEREIGN_PATTERNS:
                if pat.search(git_path):
                    runtime.sovereign_git_dirty.append(git_path)
                    break
    except Exception:
        pass

    return runtime


def _compute_delta(trust: RTrust, runtime: RRuntime) -> List[DriftEvent]:
    events: List[DriftEvent] = []

    for cum in trust.dangling_cum_hashes:
        events.append(DriftEvent(
            severity="HARD",
            code="UNANCHORED_DANGLING",
            detail=f"dangling cum_hash {cum[:16]}... has no LEDGER_SEQ_CORRECTION_V1 anchor",
        ))

    for brk in trust.chain_breaks:
        events.append(DriftEvent(
            severity="HARD",
            code="CHAIN_BREAK",
            detail=(
                f"position {brk['position']}: seq={brk['seq_curr']} "
                f"prev_cum {str(brk['actual_prev_cum'])[:16]}... "
                f"≠ seq={brk['seq_prev']} cum {str(brk['expected_cum'])[:16]}..."
            ),
            seq=brk["seq_curr"],
        ))

    for skill_id, info in trust.active_sovereign_skills.items():
        trusted = info["candidate_identity_hash"]
        runtime_hash = runtime.skill_hashes.get(skill_id)
        if runtime_hash is None:
            events.append(DriftEvent(
                severity="HARD",
                code="SKILL_MISSING_ON_DISK",
                detail=f"{skill_id}: skill.py not found",
                seq=info.get("seq"),
            ))
        elif runtime_hash != trusted:
            events.append(DriftEvent(
                severity="HARD",
                code="SKILL_HASH_MISMATCH",
                detail=f"{skill_id}: trusted={trusted[:24]}... runtime={runtime_hash[:24]}...",
                seq=info.get("seq"),
            ))

    for path in runtime.sovereign_git_dirty:
        events.append(DriftEvent(
            severity="HARD",
            code="SOVEREIGN_FILE_DIRTY",
            detail=f"sovereign path modified outside authorized writer: {path}",
        ))

    return events


def _classify(events: List[DriftEvent]) -> str:
    if any(e.severity == "HARD" for e in events):
        return STATUS_HARD_DRIFT
    if any(e.severity == "SOFT" for e in events):
        return STATUS_SOFT_DRIFT
    return STATUS_COUPLED


def probe(ledger_path: str = LEDGER_DEFAULT) -> Dict[str, Any]:
    """Run the reality coupling probe. Returns REALITY_COUPLING_WITNESS_V1 dict."""
    trust   = _replay_trust(ledger_path)
    runtime = _probe_runtime(trust)
    delta   = _compute_delta(trust, runtime)
    status  = _classify(delta)

    return {
        "schema_name":    "REALITY_COUPLING_WITNESS_V1",
        "schema_version": "1.0.0",
        "status":         status,
        "ledger_path":    ledger_path,
        "r_trust": {
            "total_entries":            trust.total_entries,
            "active_sovereign_skills": {
                sid: {
                    "seq":                    v["seq"],
                    "candidate_identity_hash": v["candidate_identity_hash"],
                }
                for sid, v in trust.active_sovereign_skills.items()
            },
            "anchored_dangling_count":  len(trust.anchored_cum_hashes),
            "unanchored_dangling_count": len(trust.dangling_cum_hashes),
            "correction_count":         len(trust.correction_entries),
            "chain_break_count":        len(trust.chain_breaks),
        },
        "r_runtime": {
            "skill_hashes":          runtime.skill_hashes,
            "sovereign_dirty_paths": runtime.sovereign_git_dirty,
        },
        "delta": [
            {
                "severity": e.severity,
                "code":     e.code,
                "detail":   e.detail,
                **({"seq": e.seq} if e.seq is not None else {}),
            }
            for e in delta
        ],
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="REALITY_COUPLING_WITNESS_V1 probe")
    parser.add_argument("--ledger", default=LEDGER_DEFAULT, help="Ledger path")
    parser.add_argument("--json",   action="store_true", dest="json_out",
                        help="Machine-readable JSON output; exit 1 on drift")
    args = parser.parse_args()

    result = probe(args.ledger)

    if args.json_out:
        print(json.dumps(result, indent=2))
        sys.exit(0 if result["status"] == STATUS_COUPLED else 1)

    status = result["status"]
    _C = {STATUS_COUPLED: "\x1b[32m", STATUS_SOFT_DRIFT: "\x1b[33m", STATUS_HARD_DRIFT: "\x1b[31m"}
    R  = "\x1b[0m"
    c  = _C.get(status, "")

    print(f"\n{c}REALITY COUPLING: {status}{R}")
    print(f"  Ledger           : {result['ledger_path']}")
    rt = result["r_trust"]
    print(f"  Total entries    : {rt['total_entries']}")
    print(f"  Sovereign skills : {list(rt['active_sovereign_skills'].keys())}")
    print(f"  Chain breaks     : {rt['chain_break_count']}")
    print(f"  Dangling         : {rt['unanchored_dangling_count']} unanchored / "
          f"{rt['anchored_dangling_count']} anchored")
    print(f"  Corrections      : {rt['correction_count']}")

    if result["delta"]:
        print(f"\n  Drift events ({len(result['delta'])}):")
        for ev in result["delta"]:
            ec = "\x1b[31m" if ev["severity"] == "HARD" else "\x1b[33m"
            seq_str = f" [seq={ev['seq']}]" if "seq" in ev else ""
            print(f"    {ec}[{ev['severity']}] {ev['code']}{R}{seq_str}: {ev['detail']}")
    else:
        print(f"\n  {c}Δ_R = 0 — no drift detected{R}")

    sys.exit(0 if status == STATUS_COUPLED else 1)


if __name__ == "__main__":
    main()
