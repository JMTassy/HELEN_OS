"""
REFERENCE_DRIFT_WITNESS_V1
oracle_town/skills/reference_drift_witness/skill.py

Scans a declared set of non-sovereign artifacts and reports SHA drift,
missing files, and stale receipts.

authority  : NONE
world_effect: NONE
sovereign_touch: False
domain     : observability
provider   : INTERNAL
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# ── Output schema ─────────────────────────────────────────────────────────────

REPORT_SCHEMA = "REFERENCE_DRIFT_REPORT_V1"

@dataclass
class ArtifactStatus:
    path: str
    expected_sha: str | None
    actual_sha: str | None
    present: bool
    drift: bool           # present but SHA changed
    missing: bool         # expected but absent
    stale: bool           # receipt older than staleness_epochs threshold
    stale_reason: str | None = None


@dataclass
class ReferenceDriftReport:
    schema: str = REPORT_SCHEMA
    scanned_at: str = ""
    manifest_source: str = "explicit"
    drift_count: int = 0
    missing_count: int = 0
    stale_count: int = 0
    total_artifacts: int = 0
    artifacts: list[ArtifactStatus] = field(default_factory=list)
    authority: str = "NONE"
    world_effect: str = "NONE"
    sovereign_touch: bool = False

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["artifacts"] = [asdict(a) for a in self.artifacts]
        return d

    @property
    def clean(self) -> bool:
        return self.drift_count == 0 and self.missing_count == 0 and self.stale_count == 0


# ── Core logic ────────────────────────────────────────────────────────────────

def _sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _epoch_number(path: Path) -> int | None:
    """Extract epoch number from a receipt filename, e.g. EPOCH_RECEIPT_E15.json → 15."""
    m = re.search(r"[_-]E(\d+)", path.stem, re.IGNORECASE)
    return int(m.group(1)) if m else None


def _is_stale_receipt(path: Path, current_epoch: int, staleness_epochs: int) -> tuple[bool, str | None]:
    if not path.exists():
        return False, None
    ep = _epoch_number(path)
    if ep is None:
        return False, None
    lag = current_epoch - ep
    if lag > staleness_epochs:
        return True, f"epoch_lag={lag} > threshold={staleness_epochs}"
    return False, None


# ── Public API ────────────────────────────────────────────────────────────────

class ReferenceDriftWitness:
    """
    Scans artifact manifests for drift, missing files, and stale receipts.

    Usage::

        witness = ReferenceDriftWitness(sot_root="/path/to/helen_os_v1")
        manifest = [
            {"path": "oracle_town/.../EPOCH_RECEIPT_E51.json",
             "expected_sha": "sha256:abc..."},
        ]
        report = witness.scan(manifest)
    """

    def __init__(
        self,
        sot_root: str | Path = ".",
        current_epoch: int = 0,
        staleness_epochs: int = 10,
    ):
        self.sot_root = Path(sot_root).resolve()
        self.current_epoch = current_epoch
        self.staleness_epochs = staleness_epochs

    def scan(
        self,
        manifest: list[dict[str, str | None]],
        manifest_source: str = "explicit",
    ) -> ReferenceDriftReport:
        """
        Scan each entry in *manifest* and return a ReferenceDriftReport.

        Each manifest entry must have at least ``path``.
        ``expected_sha`` is optional — if absent, drift detection is skipped
        (but missing/stale checks still run).
        """
        report = ReferenceDriftReport(
            scanned_at=datetime.now(timezone.utc).isoformat(),
            manifest_source=manifest_source,
            total_artifacts=len(manifest),
        )

        for entry in manifest:
            rel = entry["path"]
            expected = entry.get("expected_sha")
            p = self.sot_root / rel

            present = p.exists()
            actual = _sha256(p) if present else None

            drift   = present and expected is not None and actual != expected
            missing = not present and expected is not None

            stale, stale_reason = (
                _is_stale_receipt(p, self.current_epoch, self.staleness_epochs)
                if present else (False, None)
            )

            report.artifacts.append(ArtifactStatus(
                path=rel,
                expected_sha=expected,
                actual_sha=actual,
                present=present,
                drift=drift,
                missing=missing,
                stale=stale,
                stale_reason=stale_reason,
            ))

        report.drift_count   = sum(1 for a in report.artifacts if a.drift)
        report.missing_count = sum(1 for a in report.artifacts if a.missing)
        report.stale_count   = sum(1 for a in report.artifacts if a.stale)
        return report

    def scan_directory(
        self,
        directory: str | Path,
        pattern: str = "*.json",
        expected_shas: dict[str, str] | None = None,
        manifest_source: str = "directory_scan",
    ) -> ReferenceDriftReport:
        """
        Auto-build manifest from *directory* glob and then scan.

        *expected_shas* maps relative-to-sot_root path strings → expected SHA.
        Entries with no entry in expected_shas have expected_sha=None (stale/missing
        checks still apply).
        """
        d = Path(directory)
        paths = sorted(d.glob(pattern))
        manifest = []
        for p in paths:
            try:
                rel = str(p.relative_to(self.sot_root))
            except ValueError:
                rel = str(p)
            manifest.append({
                "path": rel,
                "expected_sha": (expected_shas or {}).get(rel),
            })
        return self.scan(manifest, manifest_source=manifest_source)

    def snapshot(
        self,
        manifest: list[dict[str, str | None]],
    ) -> list[dict[str, str]]:
        """
        Compute current SHAs for all present artifacts.
        Returns a list of {path, sha} entries suitable as future expected_shas.
        """
        result = []
        for entry in manifest:
            p = self.sot_root / entry["path"]
            if p.exists():
                result.append({"path": entry["path"], "sha": _sha256(p)})
        return result
