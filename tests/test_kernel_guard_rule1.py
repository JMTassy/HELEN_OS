"""Tests for tools/kernel_guard_rule1.py — AST-precise RULE 1 ledger-write scan.

Proves the AST detector is strictly more precise than the legacy text-regex it
replaced: it still catches every real ``open(<ledger .ndjson>, "a"/"w"/…)`` call
(single-line, multi-line, io.open, keyword args) while never flagging the
pattern when it merely appears inside a string literal, comment, or docstring —
the false-positive class that failed CI on tests/test_scanner_crossing.py.

NON_SOVEREIGN · authority=false · no ledger writes.

Run: .venv/bin/pytest tests/test_kernel_guard_rule1.py -v
"""
from __future__ import annotations

import importlib.util
import textwrap
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
_MODULE_PATH = REPO / "tools" / "kernel_guard_rule1.py"

_spec = importlib.util.spec_from_file_location("kernel_guard_rule1", _MODULE_PATH)
kg = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(kg)


def _write(tmp_path: Path, name: str, body: str) -> Path:
    f = tmp_path / name
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(textwrap.dedent(body), encoding="utf-8")
    return f


# --------------------------------------------------------------------------
# Real violations — must be caught.
# --------------------------------------------------------------------------

def test_direct_append_write_is_flagged(tmp_path):
    f = _write(tmp_path, "w.py", '''
        f = open("town/ledger_v1.ndjson", "a")
    ''')
    hits = list(kg.violations_in(str(f)))
    assert len(hits) == 1
    assert hits[0][2] == "a"


def test_write_mode_is_flagged(tmp_path):
    f = _write(tmp_path, "w.py", '''
        open("events_ledger.ndjson", "w").write("x")
    ''')
    assert len(list(kg.violations_in(str(f)))) == 1


def test_multiline_io_open_is_flagged(tmp_path):
    # The legacy single-line regex could not see this; the AST does.
    f = _write(tmp_path, "w.py", '''
        import io
        h = io.open(
            "town/wisdom_ledger.ndjson",
            mode="a",
        )
    ''')
    hits = list(kg.violations_in(str(f)))
    assert len(hits) == 1
    assert hits[0][2] == "a"


def test_keyword_file_and_mode_args_flagged(tmp_path):
    f = _write(tmp_path, "w.py", '''
        open(file="dialogue_ledger.ndjson", mode="a+")
    ''')
    assert len(list(kg.violations_in(str(f)))) == 1


# --------------------------------------------------------------------------
# False positives — must NOT be caught (this is the CI-breaking class).
# --------------------------------------------------------------------------

def test_string_literal_fixture_is_not_flagged(tmp_path):
    # Mirrors tests/test_scanner_crossing.py: the forbidden pattern quoted as
    # data inside a triple-quoted string.
    f = _write(tmp_path, "fixture.py", '''
        DOC = """
        example the scanner must reject:
        open("town/ledger_v1.ndjson", "a")
        """
    ''')
    assert list(kg.violations_in(str(f))) == []


def test_comment_is_not_flagged(tmp_path):
    f = _write(tmp_path, "c.py", '''
        # open("town/ledger_v1.ndjson", "w") — do not do this
        x = 1
    ''')
    assert list(kg.violations_in(str(f))) == []


def test_read_mode_is_not_flagged(tmp_path):
    f = _write(tmp_path, "r.py", '''
        r = open("town/ledger_v1.ndjson", "r")
    ''')
    assert list(kg.violations_in(str(f))) == []


def test_non_ledger_ndjson_is_not_flagged(tmp_path):
    # .ndjson without a ledger-ish marker in the path is out of scope, matching
    # the legacy heuristic.
    f = _write(tmp_path, "misc.py", '''
        open("artifacts/scan_output.ndjson", "a")
    ''')
    assert list(kg.violations_in(str(f))) == []


def test_json_config_is_not_flagged(tmp_path):
    f = _write(tmp_path, "cfg.py", '''
        open("town/mayor_config.json", "w")
    ''')
    assert list(kg.violations_in(str(f))) == []


# --------------------------------------------------------------------------
# Directory walk + allowed-writer exclusion (main()).
# --------------------------------------------------------------------------

def test_main_excludes_allowed_writers_and_counts(tmp_path, capsys):
    _write(tmp_path, "rogue.py", 'open("town/ledger_v1.ndjson", "a")\n')
    _write(tmp_path, "tools/ndjson_writer.py", 'open("town/ledger_v1.ndjson", "a")\n')

    rc = kg.main(["kernel_guard_rule1.py", str(tmp_path), "tools/ndjson_writer.py"])
    out = capsys.readouterr().out

    assert rc == 1
    assert "RULE1_VIOLATIONS=1" in out          # only rogue.py counts
    assert "rogue.py" in out
    assert "ndjson_writer.py" not in out         # allowed writer excluded


def test_main_clean_tree_exits_zero(tmp_path, capsys):
    _write(tmp_path, "ok.py", 'open("town/ledger_v1.ndjson", "r")\n')
    rc = kg.main(["kernel_guard_rule1.py", str(tmp_path)])
    out = capsys.readouterr().out
    assert rc == 0
    assert "RULE1_VIOLATIONS=0" in out


def test_syntax_error_file_is_skipped(tmp_path):
    f = _write(tmp_path, "broken.py", "def (:\n")
    # Unparseable files are skipped, not crashed on.
    assert list(kg.violations_in(str(f))) == []


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
