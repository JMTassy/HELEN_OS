"""
Tests for the surface_grammar skill (check_leakage + score_runs + manifest).

Fixtures are synthetic HTML strings — no file I/O, no network, deterministic.

Run: pytest experiments/helen_mvp_kernel/helen_os/tests/test_surface_grammar.py -v
"""
from __future__ import annotations

import json
import textwrap

import pytest

from helen_os.skills.surface_grammar.check_leakage import (
    _find_violations,
    scan_file,
    scan_glob,
)
from helen_os.skills.surface_grammar.score_runs import score
from helen_os.skills.surface_grammar import manifest as M


# ── HTML fixtures ─────────────────────────────────────────────────────────────

HTML_VIOLATION = textwrap.dedent("""\
    <html>
    <!-- authority: false -->
    <head><style>
    :root { --green: #00ff88; }
    .badge.live { color: var(--green); }
    .task-check.done { background: #00ff88; }
    </style></head>
    <body>authority: false</body>
    </html>
""")

HTML_CLEAN_NO_AUTHORITY = textwrap.dedent("""\
    <html>
    <head><style>
    .badge.live { color: #00ff88; }
    </style></head>
    <body>This file has no authority declaration.</body>
    </html>
""")

HTML_CLEAN_AUTHORITY_FALSE_NO_GREEN = textwrap.dedent("""\
    <html>
    <!-- authority: false -->
    <head><style>
    .badge.live { color: #bb88ff; }
    .mrow-dot.live { background: #00d4ff; }
    </style></head>
    <body>authority: false</body>
    </html>
""")

HTML_VIOLATION_MULTITOKEN = textwrap.dedent("""\
    <html>
    <body>authority=false</body>
    <style>
    :root { --grn: #00ff41; }
    .si-state.shipped { color: var(--grn); }
    .si-state.live    { background: var(--grn); }
    </style>
    </html>
""")

HTML_GOVERNANCE_LABEL_OK = textwrap.dedent("""\
    <html>
    <!-- authority: false -->
    <head><style>
    /* governance palette — ADMITTED only */
    .verdict-admitted { color: #00ff88; }
    </style></head>
    <body>authority: false</body>
    </html>
""")


# ── check_leakage tests ───────────────────────────────────────────────────────

class TestFindViolations:
    def test_detects_green_in_live_class(self):
        v = _find_violations(HTML_VIOLATION, "test.html")
        assert len(v) >= 1
        selectors = [x["selector"].strip() for x in v]
        assert any("live" in s for s in selectors)

    def test_detects_green_in_done_class(self):
        v = _find_violations(HTML_VIOLATION, "test.html")
        selectors = [x["selector"].strip() for x in v]
        assert any("done" in s for s in selectors)

    def test_no_authority_false_skips_file(self):
        v = _find_violations(HTML_CLEAN_NO_AUTHORITY, "test.html")
        assert v == []

    def test_authority_false_no_green_passes(self):
        v = _find_violations(HTML_CLEAN_AUTHORITY_FALSE_NO_GREEN, "test.html")
        assert v == []

    def test_grn_token_detected(self):
        v = _find_violations(HTML_VIOLATION_MULTITOKEN, "test.html")
        assert len(v) >= 1
        tokens = [x["token"] for x in v]
        assert any("grn" in t.lower() for t in tokens)

    def test_violation_has_required_fields(self):
        v = _find_violations(HTML_VIOLATION, "test.html")
        assert len(v) > 0
        required = {"file", "line", "selector", "token", "semantic_meaning", "body_excerpt"}
        assert required.issubset(v[0].keys())

    def test_violation_line_is_positive_int(self):
        v = _find_violations(HTML_VIOLATION, "test.html")
        for item in v:
            assert isinstance(item["line"], int)
            assert item["line"] >= 1

    def test_admitted_selector_name_not_flagged(self):
        # '.verdict-admitted { color: #00ff88 }' is a CORRECT governance use:
        # displaying an admitted item in admitted green.
        # 'verdict' is excluded from SEMANTIC_STATE_KEYWORDS to avoid this
        # false positive; 'admitted' was never in the list.
        v = _find_violations(HTML_GOVERNANCE_LABEL_OK, "test.html")
        assert v == []


# ── score_runs tests ──────────────────────────────────────────────────────────

class TestScoreRuns:
    def _trace(self, violations):
        return {
            "skill_id": "surface_grammar_v1",
            "gate": "check_leakage",
            "authority": False,
            "claim_status": "NO_CLAIM",
            "violation_count": len(violations),
            "violations": violations,
        }

    def test_clean_trace_passes(self):
        result = score(self._trace([]))
        assert result["verdict"] == "PASS"
        assert result["score"] == 1.0

    def test_one_violation_blocks(self):
        v = [{"file": "f.html", "line": 5, "selector": ".live", "token": "#00ff88",
               "semantic_meaning": "live", "body_excerpt": "color:#00ff88"}]
        result = score(self._trace(v))
        assert result["verdict"] == "BLOCK"
        assert result["score"] == 0.0

    def test_threshold_relaxation(self):
        v = [{"file": "f.html", "line": 5, "selector": ".live", "token": "#00ff88",
               "semantic_meaning": "live", "body_excerpt": "color:#00ff88"}]
        result = score(self._trace(v), pass_threshold=1)
        assert result["verdict"] == "PASS"

    def test_threshold_exceeded_blocks(self):
        v = [
            {"file": "f.html", "line": 5, "selector": ".live", "token": "--green",
             "semantic_meaning": "live", "body_excerpt": "color:var(--green)"},
            {"file": "f.html", "line": 6, "selector": ".done", "token": "--green",
             "semantic_meaning": "done", "body_excerpt": "background:var(--green)"},
            {"file": "f.html", "line": 7, "selector": ".shipped", "token": "--green",
             "semantic_meaning": "shipped", "body_excerpt": "color:var(--green)"},
        ]
        result = score(self._trace(v), pass_threshold=2)
        assert result["verdict"] == "BLOCK"

    def test_score_result_fields(self):
        result = score(self._trace([]))
        for field in ("skill_id", "gate", "authority", "claim_status",
                      "pass_threshold", "violation_count", "score", "verdict",
                      "violations_summary"):
            assert field in result

    def test_authority_always_false(self):
        result = score(self._trace([]))
        assert result["authority"] is False

    def test_claim_status_no_claim(self):
        result = score(self._trace([]))
        assert result["claim_status"] == "NO_CLAIM"


# ── manifest tests ────────────────────────────────────────────────────────────

class TestManifest:
    def test_authority_false(self):
        assert M.AUTHORITY is False

    def test_claim_status(self):
        assert M.CLAIM_STATUS == "NO_CLAIM"

    def test_ledger_effect(self):
        assert M.LEDGER_EFFECT == "none"

    def test_gates_listed(self):
        assert "check_leakage" in M.GATES
        assert "score_runs" in M.GATES

    def test_as_dict_serialisable(self):
        d = M.as_dict()
        raw = json.dumps(d)
        assert json.loads(raw) == d

    def test_governance_green_tokens_non_empty(self):
        assert len(M.GOVERNANCE_GREEN_TOKENS) >= 3

    def test_semantic_state_keywords_non_empty(self):
        assert len(M.SEMANTIC_STATE_KEYWORDS) >= 5

    def test_admitted_color_in_tokens(self):
        assert "#00ff88" in M.GOVERNANCE_GREEN_TOKENS

    def test_live_in_semantic_keywords(self):
        assert "live" in M.SEMANTIC_STATE_KEYWORDS

    def test_shipped_in_semantic_keywords(self):
        assert "shipped" in M.SEMANTIC_STATE_KEYWORDS


# ── integration: real surface files ──────────────────────────────────────────

class TestRealSurface:
    """Probe the actual apps/helen-surface/ tree. These tests assert the
    known baseline from E13 autoresearch: 10 violations across 3 files."""

    def test_real_scan_finds_violations(self):
        violations = scan_glob("apps/helen-surface/**/*.html", repo_root=".")
        assert len(violations) >= 1, (
            "Expected at least 1 CSS green-leakage violation in authority=false surface files"
        )

    def test_known_violation_files(self):
        violations = scan_glob("apps/helen-surface/**/*.html", repo_root=".")
        files_hit = {v["file"] for v in violations}
        known = {
            "apps/helen-surface/index.html",
            "apps/helen-surface/cockpit_v4.html",
            "apps/helen-surface/temple.html",
        }
        assert known.issubset(files_hit), (
            f"Expected all 3 known violation files; got {files_hit}"
        )

    def test_garden_conquest_avalon_clean(self):
        violations = scan_glob(
            "apps/helen-surface/goblin/garden_conquest_avalon.html", repo_root="."
        )
        # E12 fix (commit e9ae8f9) removed the emoji violations;
        # the garden file does NOT declare authority=false, so no CSS violations either.
        assert violations == [], (
            f"garden_conquest_avalon.html should be clean after E12 fix; got {violations}"
        )
