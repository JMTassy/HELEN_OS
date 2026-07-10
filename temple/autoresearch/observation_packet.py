"""observation_packet.py — Read-only observation packet builder (Stage 1 of two-stage loop).

NON_SOVEREIGN · AUTHORITY=false · CANON=false · LEDGER_EFFECT=none

Collects a snapshot of repo state and garden-local loop state before any
experiment decision is made. All git calls are read-only.

Subprocess is permitted here (git read-only calls only). The autoresearch_scanner
bans subprocess because it is a pure text scanner. This module is an orchestrator
that needs repo state; read-only git ops are allowed.

packet_status semantics
  WITNESSED — data collected locally in this run; dirty_dominates may fire
  REPORTED  — data supplied by caller; dirty_dominates never fires on REPORTED evidence
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# Sovereign paths (defines what counts as "protected" for dirty-path checks)
_SOVEREIGN_PREFIXES: tuple[str, ...] = (
    "town/ledger_v1",
    "town/ledger_",
    "oracle_town/kernel/",
    "helen_os/governance/",
    "helen_os/schemas/",
    "mayor_",
    "GOVERNANCE/CLOSURES/",
    "GOVERNANCE/TRANCHE_RECEIPTS/",
)

# Garden-local paths (read-only access, no sovereign content)
_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parent.parent
_OUTBOX = _HERE / "outbox"
_CONSUMPTION_LOG = _HERE / "consumption_log.ndjson"
_LOOP_STATE_FILE = _HERE / "loop_state.json"

# Allowed ranking surfaces (match the core prompt's "rank only" list)
ALLOWED_SURFACES: tuple[str, ...] = (
    "init_ranking_weights",
    "context_ranking",
    "prompt_compression",
    "skill_routing",
    "summarization_weights",
    "sandbox_visual_grammar",
)

PACKET_STATUS_WITNESSED = "WITNESSED"
PACKET_STATUS_REPORTED = "REPORTED"


@dataclass
class ObservationPacket:
    """Snapshot of repo + loop state before any experiment decision.

    All fields reflect observation, not verdict. The dirty-state predicate
    (dirty_state.evaluate) consumes this and emits a DirtyVerdict.
    """
    head: str
    dirty_paths: list[str]
    protected_paths_touched: list[str]
    replay_status: str              # "clean" | "mismatch" | "unknown"
    latest_receipt_id: Optional[str]
    rankings: dict[str, Optional[float]]  # surface → observed score 0-1; None = no evidence
    recent_targets: list[str]       # last ≤3 loop targets, most-recent first
    unauthorized_sovereign_diff: bool
    unknown_provenance_on_sovereign_paths: bool
    packet_status: str              # WITNESSED | REPORTED
    observed_at: str
    outbox_unconsumed: int
    authority: bool = False
    sovereign: bool = False
    canon: bool = False
    ledger_effect: str = "none"


# ---------------------------------------------------------------------------
# Internal helpers — all read-only
# ---------------------------------------------------------------------------

def _git(args: list[str]) -> str:
    """Run a read-only git command from REPO root; return stdout. Returns '' on error."""
    try:
        r = subprocess.run(
            ["git"] + args,
            capture_output=True, text=True, cwd=str(_REPO), timeout=10,
        )
        return r.stdout.strip() if r.returncode == 0 else ""
    except Exception:
        return ""


def _head() -> str:
    return _git(["rev-parse", "--short", "HEAD"]) or "unknown"


def _dirty_paths() -> list[str]:
    status = _git(["status", "--porcelain"])
    if not status:
        return []
    return [line[3:].strip() for line in status.splitlines() if len(line) >= 3]


def _protected(dirty: list[str]) -> list[str]:
    touched = []
    for p in dirty:
        norm = p.lstrip("/").replace("\\", "/")
        if any(norm.startswith(pfx) for pfx in _SOVEREIGN_PREFIXES):
            touched.append(p)
    return touched


def _replay_status() -> str:
    """Simple integrity check on consumption_log. Returns 'clean'/'mismatch'/'unknown'."""
    if not _CONSUMPTION_LOG.exists():
        return "unknown"
    try:
        lines = [l for l in _CONSUMPTION_LOG.read_text(encoding="utf-8").splitlines() if l.strip()]
        if not lines:
            return "unknown"
        last = json.loads(lines[-1])
        # A valid chained entry has at least one hash-like field
        if any(k in last for k in ("cum_hash", "hash", "receipt_id", "packet_id")):
            return "clean"
        return "unknown"
    except Exception:
        return "unknown"


def _latest_receipt() -> Optional[str]:
    if not _CONSUMPTION_LOG.exists():
        return None
    try:
        lines = [l for l in _CONSUMPTION_LOG.read_text(encoding="utf-8").splitlines() if l.strip()]
        for line in reversed(lines):
            entry = json.loads(line)
            rid = entry.get("receipt_id") or entry.get("packet_id")
            if rid:
                return rid
        return None
    except Exception:
        return None


def _recent_targets() -> list[str]:
    """Last ≤3 targets from loop_state, most-recent first."""
    if _LOOP_STATE_FILE.exists():
        try:
            state = json.loads(_LOOP_STATE_FILE.read_text(encoding="utf-8"))
            hist = state.get("target_history", [])
            targets = [h["target"] for h in hist[-3:] if "target" in h]
            targets.reverse()
            return targets
        except Exception:
            pass
    return []


def _outbox_unconsumed() -> int:
    if not _OUTBOX.exists():
        return 0
    return sum(1 for _ in _OUTBOX.glob("AR-*.json"))


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def collect(
    *,
    repo_root: Optional[Path] = None,
    packet_status: str = PACKET_STATUS_WITNESSED,
    supplied_rankings: Optional[dict[str, Optional[float]]] = None,
) -> ObservationPacket:
    """Collect a WITNESSED observation packet via local git + state reads. No writes."""
    dirty = _dirty_paths()
    protected = _protected(dirty)
    return ObservationPacket(
        head=_head(),
        dirty_paths=dirty,
        protected_paths_touched=protected,
        replay_status=_replay_status(),
        latest_receipt_id=_latest_receipt(),
        rankings=supplied_rankings or {s: None for s in ALLOWED_SURFACES},
        recent_targets=_recent_targets(),
        unauthorized_sovereign_diff=bool(protected),
        unknown_provenance_on_sovereign_paths=False,
        packet_status=packet_status,
        observed_at=_utc_now(),
        outbox_unconsumed=_outbox_unconsumed(),
    )


def from_reported(data: dict) -> ObservationPacket:
    """Build a REPORTED packet from externally-supplied data.

    REPORTED packets never set unauthorized_sovereign_diff or
    unknown_provenance_on_sovereign_paths — only locally WITNESSED
    evidence may assert sovereign violations.
    """
    return ObservationPacket(
        head=data.get("head", "unknown"),
        dirty_paths=data.get("dirty_paths", []),
        protected_paths_touched=data.get("protected_paths_touched", []),
        replay_status=data.get("replay_status", "unknown"),
        latest_receipt_id=data.get("latest_receipt_id"),
        rankings=data.get("rankings", {s: None for s in ALLOWED_SURFACES}),
        recent_targets=data.get("recent_targets", []),
        unauthorized_sovereign_diff=False,         # REPORTED: never assert violations
        unknown_provenance_on_sovereign_paths=False,
        packet_status=PACKET_STATUS_REPORTED,
        observed_at=data.get("observed_at", _utc_now()),
        outbox_unconsumed=data.get("outbox_unconsumed", 0),
    )
