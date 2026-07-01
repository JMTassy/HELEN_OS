"""autoresearch_scanner.py — Dry-run Autoresearch candidate scanner.

NON_SOVEREIGN · AUTHORITY=false · CANON=false · LEDGER_EFFECT=none

Usage:
    python autoresearch_scanner.py --input-dir docs/proposals/ [--outbox temple/autoresearch/outbox/] [--write]

Defaults to dry-run (prints packets, writes nothing). Pass --write to persist
packets to --outbox (only temple/autoresearch/outbox/ is a legal write target).

Rules enforced by this module:
  - No network calls (no urllib, requests, httpx, socket, etc.)
  - No subprocess calls
  - No training actions
  - No ledger writes
  - No kernel edits
  - Writes only to temple/autoresearch/outbox/ (when --write is active)
  - Skips secrets files (.env, *.key, *.pem, id_rsa, credentials)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import timezone, datetime
from pathlib import Path
from typing import Iterator

try:
    from .autoresearch_policy import (
        classify_finding,
        validate_packet,
        check_forbidden_paths,
        check_stop_conditions,
        PACKET_SCHEMA,
    )
except ImportError:  # direct script execution (python autoresearch_scanner.py)
    from autoresearch_policy import (
        classify_finding,
        validate_packet,
        check_forbidden_paths,
        check_stop_conditions,
        PACKET_SCHEMA,
    )

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_OUTBOX_PREFIX = "temple/autoresearch/outbox"
_SCANNABLE_SUFFIXES = frozenset({".md", ".txt", ".json", ".ndjson"})
_SECRET_FILENAME_SIGNALS = frozenset({
    ".env", ".key", ".pem", "id_rsa", "id_ed25519",
    "credentials", "secret", "private_key",
})

# Only scan these paths — never write to sovereign paths
_ALLOWED_INPUT_PREFIXES = (
    "docs/",
    "temple/",
    "artifacts/",
    "GOVERNANCE/STEP_4_CONFORMANCE/",
    "scratchpad/",
    "helen_dialog/",
)

# Max bytes to read per file (guard against huge binaries)
_MAX_FILE_BYTES = 128 * 1024


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _packet_id(source_path: str, summary: str) -> str:
    raw = f"{source_path}:{summary}"
    return "AR-" + hashlib.sha256(raw.encode()).hexdigest()[:12]


def _is_secret_file(path: Path) -> bool:
    name_lower = path.name.lower()
    return any(sig in name_lower for sig in _SECRET_FILENAME_SIGNALS)


def _is_allowed_input(path: Path, repo_root: Path) -> bool:
    try:
        rel = path.relative_to(repo_root).as_posix()
    except ValueError:
        return False
    return any(rel.startswith(pfx) for pfx in _ALLOWED_INPUT_PREFIXES)


def _safe_read(path: Path) -> str | None:
    """Read a file safely, returning None on any error or if file is too large."""
    try:
        if path.stat().st_size > _MAX_FILE_BYTES:
            return None
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return None


def _assert_outbox_only(outbox: Path, write_path: Path) -> None:
    """Raise ValueError if write_path is outside outbox."""
    try:
        write_path.resolve().relative_to(outbox.resolve())
    except ValueError:
        raise ValueError(
            f"WRITE BLOCKED: {write_path} is outside the allowed outbox {outbox}. "
            "Autoresearch may only write to temple/autoresearch/outbox/."
        )


# ---------------------------------------------------------------------------
# Scanning
# ---------------------------------------------------------------------------

def scan_file(path: Path, repo_root: Path) -> Iterator[dict]:
    """Yield raw finding dicts from a single file. Pure extraction — no policy."""
    if _is_secret_file(path):
        return
    if path.suffix not in _SCANNABLE_SUFFIXES:
        return
    if not _is_allowed_input(path, repo_root):
        return

    text = _safe_read(path)
    if text is None:
        return

    rel = path.relative_to(repo_root).as_posix()

    # Heuristic: look for doc-gap signals (TODO / FIXME / MISSING / TBD)
    for i, line in enumerate(text.splitlines(), 1):
        lower = line.lower().strip()
        if not lower:
            continue

        if any(kw in lower for kw in ("todo", "fixme", "tbd", "missing:", "gap:", "open question")):
            yield {
                "source_ref": f"{rel}:{i}",
                "raw_text": line.strip()[:300],
                "signal": "gap_marker",
            }
        elif any(kw in lower for kw in ("risk:", "warning:", "danger:", "forbidden:", "violation:")):
            yield {
                "source_ref": f"{rel}:{i}",
                "raw_text": line.strip()[:300],
                "signal": "risk_marker",
            }
        elif any(kw in lower for kw in ("proposal:", "hypothesis:", "candidate:")):
            yield {
                "source_ref": f"{rel}:{i}",
                "raw_text": line.strip()[:300],
                "signal": "proposal_marker",
            }


def build_packet(findings: list[dict], source_file: str) -> dict:
    """Convert raw findings from a file into an AUTORESEARCH_PACKET_V1."""
    if not findings:
        return {}

    evidence = [f["raw_text"] for f in findings[:10]]
    # sorted: set iteration order varies with PYTHONHASHSEED, and packet_id
    # hashes the summary — unsorted signals would make packet IDs nondeterministic
    source_refs = sorted({f["source_ref"] for f in findings})

    summary_signals = sorted({f.get("signal", "") for f in findings})
    summary = f"Scanner findings in {source_file}: signals={summary_signals}"

    finding_type = classify_finding(summary, evidence)

    risk_flags: list[str] = []
    if any(f.get("signal") == "risk_marker" for f in findings):
        risk_flags.append("contains_risk_markers")

    packet = {
        "schema": PACKET_SCHEMA,
        "packet_id": _packet_id(source_file, summary),
        "source_refs": source_refs,
        "finding_type": finding_type,
        "summary": summary,
        "evidence": evidence,
        "risk_flags": risk_flags,
        "recommended_action": "ROUTE_TO_OPERATOR_FOR_REVIEW",
        "authority": False,
        "sovereign": False,
        "canon": False,
        "ledger_effect": "none",
        "reducer_required": True,
        "scanned_at": _utc_now(),
    }
    return packet


# ---------------------------------------------------------------------------
# Write (outbox-only)
# ---------------------------------------------------------------------------

def write_packet(packet: dict, outbox: Path) -> Path:
    """Write a validated packet to the outbox. Enforces outbox-only constraint."""
    packet_id = packet["packet_id"]
    write_path = outbox / f"{packet_id}.json"
    _assert_outbox_only(outbox, write_path)
    outbox.mkdir(parents=True, exist_ok=True)
    write_path.write_text(
        json.dumps(packet, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return write_path


def reject_write_outside_outbox(target_path: Path, outbox: Path) -> bool:
    """Return True if write is safe (inside outbox), False if it must be blocked."""
    try:
        target_path.resolve().relative_to(outbox.resolve())
        return True
    except ValueError:
        return False


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def run(
    input_dir: Path,
    outbox: Path,
    *,
    dry_run: bool = True,
    repo_root: Path | None = None,
    verbose: bool = False,
) -> list[dict]:
    """Run a scan pass. Returns list of validated packets. Writes nothing if dry_run=True."""
    if repo_root is None:
        repo_root = Path(__file__).resolve().parent.parent.parent

    # Resolve relative paths against repo_root (not CWD) so results do not
    # depend on where the scanner is invoked from
    repo_root = repo_root.resolve()
    if not input_dir.is_absolute():
        input_dir = repo_root / input_dir
    input_dir = input_dir.resolve()
    if not outbox.is_absolute():
        outbox = repo_root / outbox
    outbox = outbox.resolve()

    if not input_dir.is_dir():
        print(f"STOP: input dir does not exist: {input_dir}", file=sys.stderr)
        return []

    # Stop condition: writes are legal only under temple/autoresearch/outbox/
    if not dry_run:
        allowed_outbox = (repo_root / _OUTBOX_PREFIX).resolve()
        if not reject_write_outside_outbox(outbox / "_probe", allowed_outbox):
            print(
                f"STOP: outbox {outbox} is outside allowed prefix {allowed_outbox}",
                file=sys.stderr,
            )
            return []

    collected: dict[str, list[dict]] = {}

    for path in sorted(input_dir.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(repo_root).as_posix()
        for finding in scan_file(path, repo_root):
            collected.setdefault(rel, []).append(finding)

    packets: list[dict] = []

    for source_file, findings in collected.items():
        if not findings:
            continue

        packet = build_packet(findings, source_file)
        if not packet:
            continue

        ok, errors = validate_packet(packet)
        if not ok:
            if verbose:
                print(f"[SKIP] {source_file}: {errors}", file=sys.stderr)
            continue

        # Stop-condition check on each packet (pass full JSON so "evidence" key is present)
        should_stop, reason = check_stop_conditions(
            text_output=json.dumps(packet),
            tests_passed=True,
        )
        if should_stop:
            print(f"STOP CONDITION: {reason}", file=sys.stderr)
            break

        packets.append(packet)

        if dry_run:
            if verbose:
                print(f"[DRY-RUN] {packet['packet_id']} ({packet['finding_type']}) — {source_file}")
        else:
            out_path = write_packet(packet, outbox)
            if verbose:
                print(f"[WRITTEN] {out_path}")

    return packets


def main() -> None:
    parser = argparse.ArgumentParser(
        description="HELEN Autoresearch dry-run scanner (NON_SOVEREIGN)"
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path("docs/proposals"),
        help="Directory to scan (default: docs/proposals/)",
    )
    parser.add_argument(
        "--outbox",
        type=Path,
        default=Path("temple/autoresearch/outbox"),
        help="Output directory for packets (default: temple/autoresearch/outbox/)",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        default=False,
        help="Write packets to --outbox (default: dry-run only)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        default=False,
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent.parent

    packets = run(
        args.input_dir,
        args.outbox,
        dry_run=not args.write,
        repo_root=repo_root,
        verbose=args.verbose,
    )

    print(json.dumps({
        "schema": "AUTORESEARCH_SCAN_RESULT_V1",
        "authority": False,
        "sovereign": False,
        "canon": False,
        "ledger_effect": "none",
        "dry_run": not args.write,
        "packet_count": len(packets),
        "packets": [p["packet_id"] for p in packets],
    }, indent=2))


if __name__ == "__main__":
    main()
