"""tests/test_wulmoji_palette_disjointness.py — PALETTE_DISJOINTNESS_V0.

NON_SOVEREIGN · authority=false · no ledger writes.

Machine-checks the palette laws that previously lived only in CLAUDE.md prose:
  1. one glyph → one meaning within each namespace
  2. STATUS_PREDICATES ∩ INTERACTION_VERBS = ∅
  3. validator VALID_STATES matches the canonical CONQUEST table
  4. CONQUEST glyphs ⊆ GOVERNANCE_STATUS glyphs; exclusions documented exactly
  5. cross-namespace meaning divergence is registered, never silent
  6. CLAUDE.md doctrine line and the canonical tables agree (drift detector)
"""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from tools.wulmoji_palette import (
    CONQUEST_BULLETIN_STATES,
    CONQUEST_EXCLUDED_GOVERNANCE_STATUS,
    CROSS_NAMESPACE_REUSE,
    GOVERNANCE_STATUS,
    INTERACTION_VERBS,
)
from tools.wulmoji_ledger_validator import VALID_STATES


# ---------------------------------------------------------------------------
# 1. One glyph, one meaning — within each namespace
# ---------------------------------------------------------------------------

class TestOneGlyphOneMeaning:
    def test_governance_meanings_unique(self):
        meanings = list(GOVERNANCE_STATUS.values())
        assert len(meanings) == len(set(meanings)), "two glyphs share a governance meaning"

    def test_interaction_meanings_unique(self):
        meanings = list(INTERACTION_VERBS.values())
        assert len(meanings) == len(set(meanings)), "two glyphs share an interaction meaning"

    def test_conquest_meanings_unique(self):
        meanings = list(CONQUEST_BULLETIN_STATES.values())
        assert len(meanings) == len(set(meanings)), "two glyphs share a conquest meaning"

    def test_governance_has_all_eight_statuses(self):
        assert set(GOVERNANCE_STATUS) == {"⚫", "🔵", "🟣", "🟠", "🟢", "🟡", "⚪", "🔴"}

    def test_interaction_has_all_seven_verbs(self):
        assert len(INTERACTION_VERBS) == 7


# ---------------------------------------------------------------------------
# 2. Role disjointness — status predicates are not interaction verbs
# ---------------------------------------------------------------------------

class TestRoleDisjointness:
    def test_status_and_verbs_disjoint(self):
        # Compare on base glyphs (strip variation selectors) so 📜 vs 📜️
        # cannot hide an overlap.
        def base(g: str) -> str:
            return g.replace("️", "")

        status = {base(g) for g in GOVERNANCE_STATUS}
        verbs = {base(g) for g in INTERACTION_VERBS}
        overlap = status & verbs
        assert overlap == set(), f"glyph(s) used as both status and verb: {overlap}"


# ---------------------------------------------------------------------------
# 3. Validator coverage — grammar set equals the canonical table
# ---------------------------------------------------------------------------

class TestValidatorCoverage:
    def test_valid_states_match_canonical_conquest_table(self):
        assert VALID_STATES == set(CONQUEST_BULLETIN_STATES), (
            "wulmoji_ledger_validator.VALID_STATES drifted from "
            "tools/wulmoji_palette.CONQUEST_BULLETIN_STATES"
        )


# ---------------------------------------------------------------------------
# 4. Subset law — conquest reuses governance colors; exclusions documented
# ---------------------------------------------------------------------------

class TestSubsetLaw:
    def test_conquest_states_subset_of_governance(self):
        assert set(CONQUEST_BULLETIN_STATES) <= set(GOVERNANCE_STATUS)

    def test_excluded_set_is_exactly_the_documented_one(self):
        actual_excluded = set(GOVERNANCE_STATUS) - set(CONQUEST_BULLETIN_STATES)
        assert actual_excluded == set(CONQUEST_EXCLUDED_GOVERNANCE_STATUS), (
            "governance statuses absent from the conquest grammar must match "
            "the documented exclusion set exactly — no silent absence"
        )

    def test_excluded_glyphs_rejected_by_validator(self):
        for glyph in CONQUEST_EXCLUDED_GOVERNANCE_STATUS:
            assert glyph not in VALID_STATES


# ---------------------------------------------------------------------------
# 5. Cross-namespace reuse — divergence registered, never silent
# ---------------------------------------------------------------------------

class TestCrossNamespaceRegister:
    def test_every_divergent_glyph_is_registered(self):
        for glyph, conquest_meaning in CONQUEST_BULLETIN_STATES.items():
            governance_meaning = GOVERNANCE_STATUS[glyph]
            if governance_meaning != conquest_meaning:
                assert glyph in CROSS_NAMESPACE_REUSE, (
                    f"{glyph} means {governance_meaning!r} in governance but "
                    f"{conquest_meaning!r} in conquest — unregistered divergence"
                )

    def test_register_entries_are_accurate(self):
        for glyph, (gov, conq) in CROSS_NAMESPACE_REUSE.items():
            assert GOVERNANCE_STATUS[glyph] == gov
            assert CONQUEST_BULLETIN_STATES[glyph] == conq


# ---------------------------------------------------------------------------
# 6. Doctrine sync — CLAUDE.md and the canonical tables agree
# ---------------------------------------------------------------------------

class TestDoctrineSync:
    @staticmethod
    def _palette_line() -> str:
        text = (REPO_ROOT / "CLAUDE.md").read_text(encoding="utf-8")
        for line in text.splitlines():
            if line.startswith("Palette (strict"):
                return line
        raise AssertionError("CLAUDE.md palette doctrine line not found")

    def test_every_governance_status_in_doctrine_line(self):
        line = self._palette_line()
        for glyph, meaning in GOVERNANCE_STATUS.items():
            assert glyph in line, f"{glyph} missing from CLAUDE.md palette line"
            assert meaning in line, f"{meaning!r} missing from CLAUDE.md palette line"

    def test_every_interaction_verb_in_doctrine_line(self):
        line = self._palette_line()
        for glyph, meaning in INTERACTION_VERBS.items():
            base = glyph.replace("️", "")
            assert base in line.replace("️", ""), (
                f"{glyph} missing from CLAUDE.md interaction vocabulary"
            )
            assert meaning in line, f"{meaning!r} missing from CLAUDE.md interaction vocabulary"
