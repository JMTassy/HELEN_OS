"""test_scanner_crossing.py — SCANNER_CROSSING_V1 regression rails.

Repairs the label-leak defect found by INIT_RANKING_LOOP_2H_V1:
the scanner flagged marker KEYWORDS in proposal docs (lexical mention),
which then leaked into ranking gold sets as feature=label circularity.

Law under test: flag the CROSSING, not the glyph.
authority=false · ledger_effect=none · no rescan · no pen mutation
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "temple" / "autoresearch"))
from autoresearch_scanner import scan_file, build_packet, _is_crossing  # noqa: E402


def write_doc(tmp_path: Path, body: str, name: str = "sample.md") -> tuple[Path, Path]:
    docdir = tmp_path / "docs" / "proposals"
    docdir.mkdir(parents=True)
    f = docdir / name
    f.write_text(body)
    return f, tmp_path


LEXICAL_PROPOSAL_DOC = """# Some Proposal V0

Proposal: adopt a nicer visual grammar for the garden.
Risk: the palette may clash with parchment.
TODO: polish the WULmoji table.
Open question: which font for commentary?
warning: this document contains the word warning.
"""

CROSSING_DOC = """# Incident Note

risk: this helper script writes directly to the ledger and bypasses the reducer.
"""

FENCED_CROSSING_DOC = """# Spec With Example

Example of what the guard must reject:

```python
# risk: agent writes directly to the ledger, bypassing the reducer
open("town/ledger_v1.ndjson", "a")
```

> risk: quoted incident text — writes to the ledger bypassing the guard.
"""


def test_lexical_markers_in_proposal_doc_do_not_trigger(tmp_path):
    f, root = write_doc(tmp_path, LEXICAL_PROPOSAL_DOC)
    assert list(scan_file(f, root)) == [], \
        "marker words in proposal prose are glyphs, not crossings"


def test_real_boundary_crossing_still_triggers(tmp_path):
    f, root = write_doc(tmp_path, CROSSING_DOC)
    found = list(scan_file(f, root))
    assert len(found) == 1
    assert found[0]["signal"] == "risk_marker"
    assert "ledger" in found[0]["raw_text"].lower()


def test_code_fences_and_blockquotes_are_quoted_context(tmp_path):
    f, root = write_doc(tmp_path, FENCED_CROSSING_DOC)
    assert list(scan_file(f, root)) == [], \
        "crossing text inside fences/quotes is content, not a crossing"


def test_gap_marker_with_crossing_triggers(tmp_path):
    f, root = write_doc(
        tmp_path,
        "TODO: remove the shim that appends to the ledger bypassing the guard.\n")
    found = list(scan_file(f, root))
    assert len(found) == 1 and found[0]["signal"] == "gap_marker"


def test_scanner_is_deterministic(tmp_path):
    f, root = write_doc(tmp_path, CROSSING_DOC + "\nrisk: cron job mutates the kernel gate config.\n")
    r1 = list(scan_file(f, root))
    r2 = list(scan_file(f, root))
    assert r1 == r2
    p1 = build_packet(r1, "docs/proposals/sample.md")
    p2 = build_packet(r2, "docs/proposals/sample.md")
    p1.pop("scanned_at"); p2.pop("scanned_at")
    assert p1 == p2, "same bytes in, same packet out (modulo timestamp)"


def test_summary_format_drops_label_leak_token(tmp_path):
    f, root = write_doc(tmp_path, CROSSING_DOC)
    packet = build_packet(list(scan_file(f, root)), "docs/proposals/sample.md")
    assert "signals=[" not in packet["summary"], \
        "V2 summaries must not carry the V1 lexical-noise token"
    assert packet["authority"] is False
    assert packet["ledger_effect"] == "none"


def test_is_crossing_needs_both_boundary_and_verb():
    assert _is_crossing("this writes directly to the ledger")
    assert not _is_crossing("the ledger is beautiful today")          # boundary, no verb
    assert not _is_crossing("please write a poem about autumn")       # verb, no boundary
    assert not _is_crossing("risk: palette may clash with parchment") # neither
