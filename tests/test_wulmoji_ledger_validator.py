"""
tests/test_wulmoji_ledger_validator.py — CI tests for the WULmoji bulletin parser.

NON_SOVEREIGN. NOT the HELEN sovereign ledger.
authority=false. No ledger writes. No sovereign interactions.
"""
import sys

import pytest

from tools.wulmoji_ledger_validator import (
    LineResult,
    grapheme_clusters,
    validate_bulletin,
    validate_line,
)


# ---------------------------------------------------------------------------
# Grapheme cluster splitter
# ---------------------------------------------------------------------------
class TestGraphemeClusters:
    def test_empty(self):
        assert grapheme_clusters("") == []

    def test_ascii(self):
        assert grapheme_clusters("abc") == ["a", "b", "c"]

    def test_warning_sign_with_vs16(self):
        # ⚠️ = U+26A0 + U+FE0F → 1 cluster (FE0F is a variation selector)
        assert grapheme_clusters("⚠️") == ["⚠️"]
        assert len(grapheme_clusters("⚠️")) == 1

    def test_two_alchemy_glyphs_are_two_clusters(self):
        # 🜃🏰 — no combining chars between them
        assert len(grapheme_clusters("🜃🏰")) == 2

    def test_warning_plus_emoji_is_two_clusters(self):
        # ⚠️🌀 — VS16 attaches to ⚠, then 🌀 is a new cluster
        clusters = grapheme_clusters("⚠️🌀")
        assert len(clusters) == 2
        assert clusters[0] == "⚠️"
        assert clusters[1] == "🌀"

    def test_three_plain_emoji_are_three_clusters(self):
        assert len(grapheme_clusters("🏰📜✨")) == 3

    def test_lock_coffin_vs_is_two_clusters(self):
        # 🔒⚰️ = U+1F512 + U+26B0 + U+FE0F → [🔒, ⚰️]
        clusters = grapheme_clusters("🔒⚰️")
        assert len(clusters) == 2

    def test_cross_mark_with_vs_is_one_cluster(self):
        # ✝️ = U+271D + U+FE0F → 1 cluster
        assert len(grapheme_clusters("✝️")) == 1

    def test_shield_with_vs_is_one_cluster(self):
        # 🛡️ = U+1F6E1 + U+FE0F → 1 cluster
        assert len(grapheme_clusters("🛡️")) == 1

    def test_alembic_with_vs_is_one_cluster(self):
        # ⚗️ = U+2697 + U+FE0F → 1 cluster
        assert len(grapheme_clusters("⚗️")) == 1

    def test_alchemy_plus_alembic_is_two_clusters(self):
        assert len(grapheme_clusters("🜃⚗️")) == 2

    def test_castle_scroll_ribbon_is_two_clusters(self):
        assert len(grapheme_clusters("🏰📜")) == 2

    def test_warning_act_token_is_two_clusters(self):
        # ⚠️📜 as Act token — 2 grapheme clusters
        clusters = grapheme_clusters("⚠️📜")
        assert len(clusters) == 2
        assert clusters[0] == "⚠️"
        assert clusters[1] == "📜"

    def test_sealed_act_token_is_two_clusters(self):
        assert len(grapheme_clusters("🔒📜")) == 2

    def test_sparkle_salt_ribbon_is_two_clusters(self):
        assert len(grapheme_clusters("✨🜍")) == 2


# ---------------------------------------------------------------------------
# Valid lines — default mode
# ---------------------------------------------------------------------------
VALID_LINES_DEFAULT = [
    # From spec examples
    "(0) 🔵 ⟂◯⟂ 🜃🏰 📜 🔗#RET0 🏰📜",
    "(1) 🔵 ⟂◯⟂ 🜃⚗️ 📜 🔗#GATE ✨🜍",
    "(2) 🟢 ⟂◯⟂ 🜃🏰 🛡️ 🔗#WALL 🏰📜",
    "(7) ⚫ 🌀 🜁🜄 ⚠️📜 🔗#INJ1 ⚠️🌀",
    "(9) 🔴 ✝️ 🜂🜍 🔒📜 🔗#VETO 🔒⚰️",
    # Without index
    "🔵 ⟂◯⟂ 🜃🏰 📜 🔗#RET0 🏰📜",
    "🟣 🌹 🜄🏰 📜 🔗#ABC 📜✨",
    # All five states
    "🟢 🌀 🜃🏰 📜 🔗#X 🏰📜",
    "🟣 🌀 🜃🏰 📜 🔗#X 🏰📜",
    "⚫ 🌀 🜃🏰 📜 🔗#X 🏰📜",
    "🔴 🌀 🜃🏰 📜 🔗#X 🏰📜",
    # All four factions
    "🔵 ⟂◯⟂ 🜃🏰 📜 🔗#X 🏰📜",
    "🔵 🌹 🜃🏰 📜 🔗#X 🏰📜",
    "🔵 🌀 🜃🏰 📜 🔗#X 🏰📜",
    "🔵 ✝️ 🜃🏰 📜 🔗#X 🏰📜",
    # All four acts
    "🔵 🌀 🜃🏰 📜 🔗#X 🏰📜",
    "🔵 🌀 🜃🏰 🛡️ 🔗#X 🏰📜",
    "🔵 🌀 🜃🏰 🔒📜 🔗#X 🏰📜",
    "🔵 🌀 🜃🏰 ⚠️📜 🔗#X ⚠️🌀",
    # Proof ID with underscores and hyphens
    "🔵 🌀 🜃🏰 📜 🔗#MY_ID-1 🏰📜",
]


@pytest.mark.parametrize("line", VALID_LINES_DEFAULT)
def test_valid_line_default(line):
    result = validate_line(line, 1)
    assert result.ok, f"Expected valid but got errors: {result.errors!r}"


# ---------------------------------------------------------------------------
# Invalid lines — one rule per test
# ---------------------------------------------------------------------------
class TestInvalidLines:
    def test_arity_too_few(self):
        r = validate_line("🔵 ⟂◯⟂ 🜃🏰 📜 🔗#X", 1)
        assert not r.ok
        assert any("ARITY" in e for e in r.errors)

    def test_arity_too_many(self):
        r = validate_line("(0) 🔵 ⟂◯⟂ 🜃🏰 📜 🔗#X 🏰📜 EXTRA", 1)
        assert not r.ok
        assert any("ARITY" in e for e in r.errors)

    def test_invalid_index_bare_digit(self):
        r = validate_line("0 🔵 ⟂◯⟂ 🜃🏰 📜 🔗#X 🏰📜", 1)
        assert not r.ok
        assert any("INDEX" in e for e in r.errors)

    def test_invalid_state(self):
        r = validate_line("🟡 ⟂◯⟂ 🜃🏰 📜 🔗#X 🏰📜", 1)
        assert not r.ok
        assert any("STATE" in e for e in r.errors)

    def test_invalid_faction(self):
        r = validate_line("🔵 🏴 🜃🏰 📜 🔗#X 🏰📜", 1)
        assert not r.ok
        assert any("FACTION" in e for e in r.errors)

    def test_warning_in_pair(self):
        r = validate_line("🔵 ⟂◯⟂ 🜄⚠️ 📜 🔗#A1B2 ✨🜍", 1)
        assert not r.ok
        assert any("WARNING_IN_PAIR" in e for e in r.errors)

    def test_pair_one_cluster(self):
        r = validate_line("🔵 ⟂◯⟂ 🜃 📜 🔗#X 🏰📜", 1)
        assert not r.ok
        assert any("PAIR_LENGTH" in e for e in r.errors)

    def test_pair_three_clusters(self):
        r = validate_line("🔵 ⟂◯⟂ 🜃🏰🌀 📜 🔗#X 🏰📜", 1)
        assert not r.ok
        assert any("PAIR_LENGTH" in e for e in r.errors)

    def test_invalid_act(self):
        r = validate_line("🔵 ⟂◯⟂ 🜃🏰 ⚔️ 🔗#A1B2 🏰📜", 1)
        assert not r.ok
        assert any("ACT" in e for e in r.errors)

    def test_proof_missing_link_emoji(self):
        r = validate_line("🔵 ⟂◯⟂ 🜃🏰 📜 #A1B2 🏰📜", 1)
        assert not r.ok
        assert any("PROOF" in e for e in r.errors)

    def test_proof_confusion_lock_for_link(self):
        r = validate_line("🔵 ⟂◯⟂ 🜃🏰 📜 🔒#A1B2 🏰📜", 1)
        assert not r.ok
        assert any("PROOF_CONFUSION" in e for e in r.errors)

    def test_warning_in_proof_id(self):
        r = validate_line("🔵 ⟂◯⟂ 🜃🏰 📜 🔗#A⚠️B 🏰📜", 1)
        assert not r.ok
        assert any("WARNING_IN_PROOF" in e for e in r.errors)

    def test_proof_id_lowercase_fails_default(self):
        r = validate_line("🔵 ⟂◯⟂ 🜃🏰 📜 🔗#a1b2 🏰📜", 1)
        assert not r.ok
        assert any("PROOF_ID" in e for e in r.errors)

    def test_ribbon_three_clusters(self):
        r = validate_line("🔵 ⟂◯⟂ 🜃🏰 📜 🔗#A1B2 🏰📜✨", 1)
        assert not r.ok
        assert any("RIBBON_LENGTH" in e for e in r.errors)

    def test_ribbon_one_cluster(self):
        r = validate_line("🔵 ⟂◯⟂ 🜃🏰 📜 🔗#A1B2 🏰", 1)
        assert not r.ok
        assert any("RIBBON_LENGTH" in e for e in r.errors)

    def test_warning_in_ribbon_without_warning_act(self):
        # Ribbon ⚠️🌀 is invalid when Act is plain 📜
        r = validate_line("(7) ⚫ 🌀 🜁🜄 📜 🔗#INJ1 ⚠️🌀", 1)
        assert not r.ok
        assert any("WARNING_IN_RIBBON" in e for e in r.errors)

    def test_warning_in_ribbon_allowed_with_warning_act(self):
        r = validate_line("(7) ⚫ 🌀 🜁🜄 ⚠️📜 🔗#INJ1 ⚠️🌀", 1)
        assert r.ok, f"Expected valid: {r.errors!r}"


# ---------------------------------------------------------------------------
# StrictProof mode
# ---------------------------------------------------------------------------
class TestStrictProof:
    def test_valid_4hex(self):
        r = validate_line("(1) 🔵 ⟂◯⟂ 🜄🜁 📜 🔗#A1B2 ✨🜍", 1, strict_proof=True)
        assert r.ok, f"Expected valid: {r.errors!r}"

    @pytest.mark.parametrize("hex_id", ["0000", "FFFF", "9A8B", "C3D4", "E5F6"])
    def test_valid_hex_ids(self, hex_id):
        r = validate_line(f"🔵 ⟂◯⟂ 🜃🏰 📜 🔗#{hex_id} 🏰📜", 1, strict_proof=True)
        assert r.ok, f"Expected valid for {hex_id}: {r.errors!r}"

    def test_rejects_non_hex_char(self):
        # RET0 — R is not in [0-9A-F]
        r = validate_line("(0) 🔵 ⟂◯⟂ 🜃🏰 📜 🔗#RET0 🏰📜", 1, strict_proof=True)
        assert not r.ok
        assert any("STRICT" in e for e in r.errors)

    def test_rejects_five_hex_chars(self):
        r = validate_line("🔵 ⟂◯⟂ 🜃🏰 📜 🔗#ABCDE 🏰📜", 1, strict_proof=True)
        assert not r.ok

    def test_rejects_three_hex_chars(self):
        r = validate_line("🔵 ⟂◯⟂ 🜃🏰 📜 🔗#ABC 🏰📜", 1, strict_proof=True)
        assert not r.ok

    def test_default_mode_allows_longer_alphanumeric(self):
        r = validate_line("(1) 🔵 ⟂◯⟂ 🜃⚗️ 📜 🔗#GATE ✨🜍", 1, strict_proof=False)
        assert r.ok, f"Expected valid: {r.errors!r}"

    def test_strict_proof_bulletin_from_spec(self):
        text = "\n".join([
            "(1) 🔵 ⟂◯⟂ 🜄🜁 📜 🔗#A1B2 ✨🜍",
            "(2) 🟢 ⟂◯⟂ 🜁🜂 🛡️ 🔗#C3D4 🏰📜",
            "(3) ⚫ 🌀 🜂🜍 🔒📜 🔗#E5F6 🔒⚰️",
        ])
        results = validate_bulletin(text, strict_proof=True)
        assert all(r.ok for r in results), [r.errors for r in results]


# ---------------------------------------------------------------------------
# AlchemyStrict mode
# ---------------------------------------------------------------------------
class TestAlchemyStrict:
    @pytest.mark.parametrize("pair,label", [
        ("🜃🜄", "Earth→Water"),
        ("🜄🜁", "Water→Air"),
        ("🜁🜂", "Air→Fire"),
        ("🜂🜍", "Fire→Salt"),
    ])
    def test_valid_forward_transitions(self, pair, label):
        r = validate_line(f"🔵 ⟂◯⟂ {pair} 📜 🔗#X 🏰📜", 1, alchemy_strict=True)
        assert r.ok, f"{label}: {r.errors!r}"

    def test_invalid_earth_to_fire(self):
        # 🜃→🜂 skips Water and Air
        r = validate_line("🔵 ⟂◯⟂ 🜃🜂 📜 🔗#A1B2 ✨🜍", 1, alchemy_strict=True)
        assert not r.ok
        assert any("ALCHEMY" in e for e in r.errors)

    def test_invalid_reverse_water_earth(self):
        r = validate_line("🔵 ⟂◯⟂ 🜄🜃 📜 🔗#X 🏰📜", 1, alchemy_strict=True)
        assert not r.ok
        assert any("ALCHEMY" in e for e in r.errors)

    def test_invalid_same_glyph(self):
        r = validate_line("🔵 ⟂◯⟂ 🜃🜃 📜 🔗#X 🏰📜", 1, alchemy_strict=True)
        assert not r.ok
        assert any("ALCHEMY" in e for e in r.errors)

    def test_non_alchemy_pair_skips_transition_check(self):
        # 🜃⚗️ — ⚗️ is not an alchemy glyph → transition check is skipped
        r = validate_line("(1) 🔵 ⟂◯⟂ 🜃⚗️ 📜 🔗#GATE ✨🜍", 1, alchemy_strict=True)
        assert r.ok, f"Expected valid (non-alchemy pair): {r.errors!r}"

    def test_castle_pair_skips_transition_check(self):
        # 🜃🏰 — 🏰 is not alchemy → skipped
        r = validate_line("(0) 🔵 ⟂◯⟂ 🜃🏰 📜 🔗#RET0 🏰📜", 1, alchemy_strict=True)
        assert r.ok, f"Expected valid: {r.errors!r}"

    def test_default_mode_allows_invalid_alchemy_pair(self):
        # Without --alchemy-strict, 🜃🜂 is fine
        r = validate_line("🔵 ⟂◯⟂ 🜃🜂 📜 🔗#A1B2 ✨🜍", 1, alchemy_strict=False)
        assert r.ok, f"Expected valid in default mode: {r.errors!r}"


# ---------------------------------------------------------------------------
# Multi-line bulletin
# ---------------------------------------------------------------------------
class TestBulletin:
    def test_all_valid_bulletin_from_spec(self):
        text = "\n".join([
            "(0) 🔵 ⟂◯⟂ 🜃🏰 📜 🔗#RET0 🏰📜",
            "(1) 🔵 ⟂◯⟂ 🜃⚗️ 📜 🔗#GATE ✨🜍",
            "(2) 🟢 ⟂◯⟂ 🜃🏰 🛡️ 🔗#WALL 🏰📜",
            "(7) ⚫ 🌀 🜁🜄 ⚠️📜 🔗#INJ1 ⚠️🌀",
            "(9) 🔴 ✝️ 🜂🜍 🔒📜 🔗#VETO 🔒⚰️",
        ])
        results = validate_bulletin(text)
        assert all(r.ok for r in results), [r.errors for r in results if not r.ok]

    def test_first_valid_second_invalid(self):
        text = "\n".join([
            "(0) 🔵 ⟂◯⟂ 🜃🏰 📜 🔗#RET0 🏰📜",
            "🔵 ⟂◯⟂ 🜄⚠️ 📜 🔗#A1B2 ✨🜍",
        ])
        results = validate_bulletin(text)
        assert results[0].ok
        assert not results[1].ok

    def test_empty_lines_skipped(self):
        text = "\n".join([
            "(0) 🔵 ⟂◯⟂ 🜃🏰 📜 🔗#RET0 🏰📜",
            "",
            "   ",
            "(1) 🟢 ⟂◯⟂ 🜃🏰 🛡️ 🔗#WALL 🏰📜",
        ])
        results = validate_bulletin(text)
        assert len(results) == 2
        assert all(r.ok for r in results)

    def test_returns_line_result_objects(self):
        results = validate_bulletin("🔵 ⟂◯⟂ 🜃🏰 📜 🔗#X 🏰📜")
        assert len(results) == 1
        assert isinstance(results[0], LineResult)


# ---------------------------------------------------------------------------
# Non-sovereign contract checks
# ---------------------------------------------------------------------------
class TestNonSovereign:
    def test_does_not_import_sovereign_modules(self):
        # Validator must never import HELEN sovereign machinery
        loaded = set(sys.modules.keys())
        sovereign = {"helen_say", "ndjson_writer", "kernel_guard"}
        for mod in sovereign:
            assert mod not in loaded, f"Sovereign module {mod!r} imported"

    def test_line_result_has_no_authority_field(self):
        # LineResult is a bulletin parse result, not a ledger entry — no authority
        r = validate_line("🔵 ⟂◯⟂ 🜃🏰 📜 🔗#X 🏰📜", 1)
        assert not hasattr(r, "authority")
        assert not hasattr(r, "sovereign")
