#!/usr/bin/env python3
"""FRICTION 1 — device ledger fingerprint (READ-ONLY).

Emits a compact, paste-able fingerprint of a ledger's hash chain plus the
device facts most likely to cause two "identical" ledgers to diverge.

Reads only. NEVER writes to town/ or any sovereign path. Recomputes every
hash from the payload rather than trusting stored values, per the WUL law:

    DO NOT TRUST HASHES. RECOMPUTE HASHES. THEN TRUST THE MATCH.

Usage (run on EACH device, from the repo root):

    python3 experiments/helen_mvp_kernel/ledger_forensics/ledger_fingerprint.py \
        --label IMAC > imac.fingerprint.json

    python3 experiments/helen_mvp_kernel/ledger_forensics/ledger_fingerprint.py \
        --label MACBOOK > macbook.fingerprint.json

Then diff them:

    python3 experiments/helen_mvp_kernel/ledger_forensics/ledger_diff.py \
        imac.fingerprint.json macbook.fingerprint.json

NON_SOVEREIGN. authority=false. canon=false. ledger_effect=none.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import locale
import os
import platform
import subprocess
import sys
from pathlib import Path

SCHEMA = "LEDGER_DEVICE_FINGERPRINT_V1"
DEFAULT_LEDGERS = [
    "town/ledger_v1.ndjson",
    "experiments/helen_mvp_kernel/ledger/events.ndjson",
]
CHECKPOINT_STRIDE = 16
FULL_ROWS_LIMIT = 2000  # ship per-seq hashes when the ledger is small enough


def canon(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False).encode("utf-8")


def sha_hex(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _git(repo: Path, *args) -> str:
    try:
        return subprocess.run(["git", "-C", str(repo), *args],
                              capture_output=True, text=True,
                              check=True).stdout.strip()
    except Exception:
        return "UNAVAILABLE"


def device_block(repo: Path) -> dict:
    """The facts that actually cause divergence between 'identical' clones."""
    return {
        "platform": platform.platform(),
        "machine": platform.machine(),
        "python": sys.version.split()[0],
        "python_impl": platform.python_implementation(),
        "float_repr_check": repr(0.1 + 0.2),          # IEEE repr sanity
        "hash_randomization": os.environ.get("PYTHONHASHSEED", "unset"),
        "fs_encoding": sys.getfilesystemencoding(),
        "preferred_encoding": locale.getpreferredencoding(False),
        "tz": os.environ.get("TZ", "unset"),
        "git_head": _git(repo, "rev-parse", "HEAD"),
        "git_branch": _git(repo, "rev-parse", "--abbrev-ref", "HEAD"),
        "git_dirty": bool(_git(repo, "status", "--porcelain")),
    }


def fingerprint_ledger(path: Path) -> dict:
    """Recompute a ledger's chain and summarize it. Read-only."""
    if not path.exists():
        return {"path": str(path), "present": False}

    raw = path.read_bytes()
    out = {
        "path": str(path),
        "present": True,
        "bytes": len(raw),
        "raw_sha256": sha_hex(raw),
        "line_ending": ("CRLF" if b"\r\n" in raw else
                        "LF" if b"\n" in raw else "NONE"),
        "trailing_newline": raw.endswith(b"\n") if raw else False,
    }

    rows, malformed = [], 0
    for line in raw.decode("utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except Exception:
            malformed += 1

    out["rows"] = len(rows)
    out["malformed_lines"] = malformed
    if not rows:
        return out

    # Normalized content hash: order-preserving, whitespace/line-ending immune.
    out["content_sha256"] = sha_hex(b"\n".join(canon(r) for r in rows))

    payload_ok = cum_ok = 0
    first_payload_mismatch = first_cum_mismatch = None
    checkpoints, full = {}, {}

    for r in rows:
        seq = r.get("seq")
        stored_ph = r.get("payload_hash", "")
        computed_ph = sha_hex(canon(r.get("payload"))) if "payload" in r else ""
        if computed_ph and computed_ph == stored_ph:
            payload_ok += 1
        elif first_payload_mismatch is None:
            first_payload_mismatch = {"seq": seq, "stored": stored_ph[:16],
                                      "computed": computed_ph[:16]}

        stored_cum = r.get("cum_hash", "")
        try:
            computed_cum = sha_hex(bytes.fromhex(r.get("prev_cum_hash", "")) +
                                   bytes.fromhex(stored_ph))
        except Exception:
            computed_cum = ""
        if computed_cum and computed_cum == stored_cum:
            cum_ok += 1
        elif first_cum_mismatch is None:
            first_cum_mismatch = {"seq": seq, "stored": stored_cum[:16],
                                  "computed": computed_cum[:16]}

        if isinstance(seq, int):
            # Ship RECOMPUTED hashes, not stored ones. A payload edited without
            # updating its hash field is invisible to a stored-hash comparison;
            # recomputing makes payload drift localizable to an exact seq AND
            # keeps tampering visible via the stored-vs-computed mismatch flag.
            if seq % CHECKPOINT_STRIDE == 0:
                checkpoints[str(seq)] = computed_ph[:16] or stored_ph[:16]
            if len(rows) <= FULL_ROWS_LIMIT:
                full[str(seq)] = {
                    "t": r.get("type", ""),
                    "p": computed_ph[:12],           # recomputed from payload
                    "c": stored_cum[:12],            # chain position as recorded
                    "tamper": stored_ph != computed_ph,
                }

    seqs = [r.get("seq") for r in rows if isinstance(r.get("seq"), int)]
    linkage_breaks = [
        {"after_seq": a.get("seq"), "at_seq": b.get("seq")}
        for a, b in zip(rows, rows[1:])
        if b.get("prev_cum_hash") != a.get("cum_hash")
    ]

    out.update({
        "integrity": {
            "payload_hash_recomputed_ok": payload_ok,
            "payload_hash_mismatch": len(rows) - payload_ok,
            "cum_hash_recomputed_ok": cum_ok,
            "cum_hash_mismatch": len(rows) - cum_ok,
            "first_payload_mismatch": first_payload_mismatch,
            "first_cum_mismatch": first_cum_mismatch,
            "linkage_breaks": len(linkage_breaks),
            "first_linkage_breaks": linkage_breaks[:5],
        },
        "seq": {
            "min": min(seqs) if seqs else None,
            "max": max(seqs) if seqs else None,
            "count": len(seqs),
            "unique": len(set(seqs)) == len(seqs),
            "monotone": all(y > x for x, y in zip(seqs, seqs[1:])),
        },
        "final_cum_hash": rows[-1].get("cum_hash", ""),
        "checkpoints": checkpoints,
        "per_seq": full if full else None,
    })
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Device ledger fingerprint (read-only)")
    ap.add_argument("--label", required=True,
                    help="device label, e.g. IMAC / MACBOOK / CONTAINER")
    ap.add_argument("--repo", default=None, help="repo root (default: auto)")
    ap.add_argument("--ledger", action="append", default=None,
                    help="ledger path (repeatable; default: standard set)")
    args = ap.parse_args()

    repo = Path(args.repo) if args.repo else Path(__file__).resolve().parents[3]
    targets = args.ledger or DEFAULT_LEDGERS

    doc = {
        "schema": SCHEMA,
        "label": args.label,
        "repo_root": str(repo),
        "device": device_block(repo),
        "ledgers": [fingerprint_ledger(repo / t) for t in targets],
        "authority": False,
        "canon": False,
        "ledger_effect": "none",
    }
    json.dump(doc, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
