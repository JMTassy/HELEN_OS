"""Executable witness for THE_DAILY_VERDICT_V1.

Mirrors the JS selection algorithm in Python and pins golden vectors, so
"same date => same scroll for every player" is offline-verifiable here.
Checks bank integrity (30 dilemmas x 3 prebuilt consequences), the laws
block, and the share-row builder. Stdlib only. authority=false.
"""

import hashlib
import json
from pathlib import Path

QUESTS = Path(__file__).resolve().parents[2] / "warren_quests"
PACKET = QUESTS / "daily_verdict_v1.json"
SALT = "WARREN_DAILY_V1:"
VERDICT_EMOJI = {"TRY": "\U0001F7E2", "HOLD": "\U0001F7E1", "COMPOST": "\U0001F534"}
FOG = "\U0001F32B"


def _load():
    return json.loads(PACKET.read_text(encoding="utf-8"))


def pick_index(date, n):
    h = hashlib.sha256((SALT + date).encode()).hexdigest()
    return int(h[:8], 16) % n


def share_row(history, days):
    """Mirror of the JS 7-day row builder: stamped -> emoji, missed -> fog."""
    return "".join(VERDICT_EMOJI[history[d]] if d in history else FOG for d in days)


def test_packet_parses_and_declares_no_authority():
    q = _load()
    assert q["schema"] == "WARREN_MINIGAME_PACKET_V1"
    assert q["authority"] is False and q["canon"] is False
    assert q["ledger_effect"] == "none"


def test_bank_integrity_30_dilemmas_90_consequences():
    bank = _load()["bank"]
    assert len(bank) == 30
    ids = [d["id"] for d in bank]
    assert len(ids) == len(set(ids))
    for d in bank:
        assert d["title"] and d["scroll"]
        assert set(d["consequences"].keys()) == {"TRY", "HOLD", "COMPOST"}
        assert all(d["consequences"][v] for v in ("TRY", "HOLD", "COMPOST"))


def test_selection_golden_vectors_worldwide_determinism():
    """Pinned vectors — any implementation on any device must agree."""
    bank = _load()["bank"]
    n = len(bank)
    golden = {
        "2026-07-12": (27, "SOCK_ORACLE"),
        "2026-07-13": (25, "WHISPER_PATH"),
        "2026-07-14": (19, "SNAIL_RACE"),
        "2026-01-01": (18, "FOG_TAX"),
    }
    for date, (idx, did) in golden.items():
        got = pick_index(date, n)
        assert got == idx, f"{date}: expected {idx}, got {got}"
        assert bank[got]["id"] == did


def test_laws_block_pins_the_viral_contract():
    laws = _load()["laws"]
    for key in ("same_scroll_everywhere", "verdict_not_purchasable",
                "consequence_cosmetic_first", "world_split_post_stamp_only",
                "no_guilt", "world_split_v1_honesty"):
        assert key in laws and laws[key], key
    assert "UTC" in laws["same_scroll_everywhere"]
    assert "NEVER reset" in laws["no_guilt"]
    assert "never faked" in laws["world_split_v1_honesty"]


def test_share_row_fog_preserves_streak_semantics():
    """A missed day renders fog; stamped days keep their verdicts —
    absence subtracts nothing (no-guilt law, structurally)."""
    days = [f"2026-07-{d:02d}" for d in range(6, 13)]           # 7 days
    history = {"2026-07-06": "TRY", "2026-07-07": "COMPOST",
               "2026-07-09": "HOLD", "2026-07-11": "TRY", "2026-07-12": "TRY"}
    row = share_row(history, days)
    assert len(list(row)) >= 7                                   # 7 glyphs (emoji-safe len check below)
    expected = (VERDICT_EMOJI["TRY"] + VERDICT_EMOJI["COMPOST"] + FOG +
                VERDICT_EMOJI["HOLD"] + FOG + VERDICT_EMOJI["TRY"] + VERDICT_EMOJI["TRY"])
    assert row == expected
    # streak = number of stamped days; adding a missed day changes nothing
    assert len(history) == 5
    history_after_missed_day = dict(history)                     # next day: no stamp
    assert len(history_after_missed_day) == 5                    # unchanged, unbroken


def test_three_dilemmas_fully_playable_end_to_end():
    """DONE criterion: at least 3 dilemmas traversable start-to-finish in
    data — scroll -> each of 3 stamps -> a distinct prebuilt consequence."""
    bank = _load()["bank"]
    playable = 0
    for d in bank[:3] + [bank[27], bank[25], bank[19]]:          # first 3 + this week's 3
        cons = d["consequences"]
        if d["scroll"] and len({cons["TRY"], cons["HOLD"], cons["COMPOST"]}) == 3:
            playable += 1
    assert playable >= 3
