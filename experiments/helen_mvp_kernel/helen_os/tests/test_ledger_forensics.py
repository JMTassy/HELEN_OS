"""Witness for the FRICTION-1 ledger forensics instrument.

Plants four known divergences against the live sovereign ledger (in tmp
copies — the sovereign file is never written) and asserts the differ names
each one correctly. Includes a regression pin for the bug found while
building this: shipping STORED hashes made a payload edit invisible
cross-device; the fingerprint must ship RECOMPUTED hashes.

Read-only on town/. NON_SOVEREIGN. authority=false.
"""

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# tests/ -> helen_os/ -> helen_mvp_kernel/ -> experiments/ -> <repo root>
REPO = Path(__file__).resolve().parents[4]
FORENSICS = REPO / "experiments" / "helen_mvp_kernel" / "ledger_forensics"
FP = FORENSICS / "ledger_fingerprint.py"
DIFF = FORENSICS / "ledger_diff.py"
LEDGER_REL = "town/ledger_v1.ndjson"
LEDGER = REPO / LEDGER_REL


def _fingerprint(repo_root: Path, label: str) -> dict:
    out = subprocess.run(
        [sys.executable, str(FP), "--label", label, "--repo", str(repo_root),
         "--ledger", LEDGER_REL],
        capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def _diff_text(a: dict, b: dict, tmp: Path) -> str:
    pa, pb = tmp / "a.json", tmp / "b.json"
    pa.write_text(json.dumps(a), encoding="utf-8")
    pb.write_text(json.dumps(b), encoding="utf-8")
    return subprocess.run([sys.executable, str(DIFF), str(pa), str(pb)],
                          capture_output=True, text=True, check=True).stdout


def _rows():
    return [json.loads(l) for l in
            LEDGER.read_text(encoding="utf-8").splitlines() if l.strip()]


def _device(tmp: Path, name: str, rows=None, raw: bytes = None) -> Path:
    root = tmp / name
    (root / "town").mkdir(parents=True, exist_ok=True)
    target = root / LEDGER_REL
    if raw is not None:
        target.write_bytes(raw)
    elif rows is not None:
        target.write_text("\n".join(json.dumps(r, ensure_ascii=False)
                                    for r in rows) + "\n", encoding="utf-8")
    else:
        shutil.copy2(LEDGER, target)
    return root


def test_sovereign_ledger_is_self_consistent_here():
    """Precondition: this device's ledger recomputes against itself."""
    fp = _fingerprint(REPO, "REF")
    led = fp["ledgers"][0]
    assert led["present"] and led["rows"] > 0
    integ = led["integrity"]
    assert integ["payload_hash_mismatch"] == 0
    assert integ["cum_hash_mismatch"] == 0
    assert integ["linkage_breaks"] == 0
    assert led["seq"]["monotone"] and led["seq"]["unique"]


def test_identical_copy_reports_no_divergence():
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        a = _fingerprint(REPO, "A")
        b = _fingerprint(_device(tmp, "clone"), "B")
        out = _diff_text(a, b, tmp)
        assert "NO_DIVERGENCE_DETECTED" in out


def test_payload_edit_is_localized_to_exact_seq_and_flagged_as_tamper():
    """REGRESSION PIN: shipping stored hashes hid this entirely. The
    fingerprint must recompute, so an edited payload is localized."""
    rows = _rows()
    target_seq = rows[len(rows) // 2]["seq"]
    for r in rows:
        if r["seq"] == target_seq:
            r["payload"]["__planted__"] = "divergence"
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        a = _fingerprint(REPO, "A")
        b = _fingerprint(_device(tmp, "edited", rows=rows), "B")
        out = _diff_text(a, b, tmp)
        assert f"FIRST DIVERGENT SEQ: {target_seq}" in out, out
        assert "payload_hash" in out
        assert "PAYLOAD_DRIFT" in out
        assert "TAMPER_FLAG" in out


def test_truncated_device_reports_row_count_and_missing_seqs():
    rows = _rows()
    keep = rows[:-3]
    missing_first = rows[-3]["seq"]
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        a = _fingerprint(REPO, "A")
        b = _fingerprint(_device(tmp, "short", rows=keep), "B")
        out = _diff_text(a, b, tmp)
        assert "ROW_COUNT_DIFFERS" in out
        assert f"FIRST DIVERGENT SEQ: {missing_first}" in out
        assert "only_in_A" in out


def test_crlf_is_classified_as_encoding_not_fork():
    raw = LEDGER.read_bytes().replace(b"\n", b"\r\n")
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        a = _fingerprint(REPO, "A")
        b = _fingerprint(_device(tmp, "crlf", raw=raw), "B")
        out = _diff_text(a, b, tmp)
        assert "BYTES_DIFFER_CONTENT_IDENTICAL" in out
        assert "CRLF" in out
        assert "not a ledger fork" in out


def test_tool_never_writes_to_sovereign_path():
    """The instrument is read-only: sovereign file unchanged by a full run."""
    before = LEDGER.read_bytes()
    _fingerprint(REPO, "READONLY_CHECK")
    assert LEDGER.read_bytes() == before
