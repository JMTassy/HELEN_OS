"""Lifecycle transition legality, including the sovereignty gate on
APPROVED_BY_ROSE: only an explicit Rose GO decision can mint it."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from validate_workspace import transition_allowed  # noqa: E402

GO_LEDGER = {"R-001": {"decision_id": "R-001", "outcome": "GO"}}
HOLD_LEDGER = {"R-001": {"decision_id": "R-001", "outcome": "HOLD"}}


class TestLegalTransitions(unittest.TestCase):
    def test_legal_paths(self):
        legal = [
            ("PROPOSED", "RESEARCHED"),
            ("PROPOSED", "HOLD"),
            ("PROPOSED", "REJECTED"),
            ("RESEARCHED", "TESTED"),
            ("RESEARCHED", "HOLD"),
            ("APPROVED_BY_ROSE", "EXECUTED"),
            ("EXECUTED", "VERIFIED"),
        ]
        for src, dst in legal:
            self.assertTrue(transition_allowed(src, dst), f"{src} -> {dst} should be legal")

    def test_approval_with_rose_go_decision(self):
        self.assertTrue(transition_allowed("TESTED", "APPROVED_BY_ROSE",
                                           rose_decision_id="R-001", ledger=GO_LEDGER))


class TestForbiddenTransitions(unittest.TestCase):
    def test_forbidden_paths(self):
        forbidden = [
            ("PROPOSED", "APPROVED_BY_ROSE"),
            ("RESEARCHED", "EXECUTED"),
            ("TESTED", "VERIFIED"),
            ("EXECUTED", "APPROVED_BY_ROSE"),
            ("PROPOSED", "EXECUTED"),
            ("PROPOSED", "VERIFIED"),
            ("VERIFIED", "PROPOSED"),
            ("REJECTED", "EXECUTED"),
        ]
        for src, dst in forbidden:
            self.assertFalse(
                transition_allowed(src, dst, rose_decision_id="R-001", ledger=GO_LEDGER),
                f"{src} -> {dst} should be forbidden even with a GO decision",
            )

    def test_approval_never_minted_without_decision(self):
        # legal edge shape, but no decision record -> refused
        self.assertFalse(transition_allowed("TESTED", "APPROVED_BY_ROSE"))
        self.assertFalse(transition_allowed("TESTED", "APPROVED_BY_ROSE",
                                            rose_decision_id="R-404", ledger=GO_LEDGER))
        self.assertFalse(transition_allowed("TESTED", "APPROVED_BY_ROSE",
                                            rose_decision_id="R-001", ledger=HOLD_LEDGER))

    def test_unknown_states_rejected(self):
        self.assertFalse(transition_allowed("DRAFT", "PROPOSED"))
        self.assertFalse(transition_allowed("PROPOSED", "SHIPPED"))


if __name__ == "__main__":
    unittest.main()
