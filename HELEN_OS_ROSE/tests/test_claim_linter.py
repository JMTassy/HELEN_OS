"""Tests for the deterministic claim linter (mandated cases + guards)."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import claim_linter  # noqa: E402


def verdicts(text, ledger=None):
    return [f["verdict"] for f in claim_linter.lint_text(text, ledger=ledger or {})]


class TestMandatedCases(unittest.TestCase):
    def test_1_generation_statement_allowed(self):
        # generation is not authority
        self.assertNotIn("FLAGGED", verdicts("The strategy was generated."))

    def test_2_approved_without_receipt_flagged(self):
        self.assertIn("FLAGGED", verdicts("The strategy is approved."))

    def test_3_implemented_without_artifact_flagged(self):
        self.assertIn("FLAGGED", verdicts("The prototype was implemented."))

    def test_4_verified_without_test_receipt_flagged(self):
        self.assertIn("FLAGGED", verdicts("The prototype was verified."))

    def test_5_partner_without_agreement_flagged(self):
        self.assertIn("FLAGGED", verdicts("A hotel is a partner."))

    def test_6_working_hypothesis_allowed(self):
        self.assertNotIn("FLAGGED", verdicts("This is the current working hypothesis."))

    def test_7_decision_reference_verified_against_ledger(self):
        line = "Rose marked decision R-001 as GO."
        # without ledger entry -> flagged
        self.assertIn("FLAGGED", verdicts(line, ledger={}))
        # wrong outcome in ledger -> flagged
        self.assertIn("FLAGGED", verdicts(line, ledger={"R-001": "HOLD"}))
        # matching ledger entry -> allowed
        v = verdicts(line, ledger={"R-001": "GO"})
        self.assertIn("ALLOWED", v)
        self.assertNotIn("FLAGGED", v)


class TestNoSemanticPromotion(unittest.TestCase):
    def test_unknown_outcome_stays_unclassified(self):
        v = verdicts("Rose marked decision R-002 as WIN.")
        self.assertIn("UNCLASSIFIED", v)
        self.assertNotIn("ALLOWED", v)


class TestSupportMarkers(unittest.TestCase):
    def test_evidence_marker_allows(self):
        v = verdicts("The prototype was implemented (E3, receipts/run_001.json).")
        self.assertNotIn("FLAGGED", v)

    def test_hedge_allows(self):
        self.assertNotIn("FLAGGED", verdicts("The wedge is not validated yet."))

    def test_backticked_vocabulary_mention_skipped(self):
        self.assertEqual([], verdicts("Never mark work `approved` on your own."))

    def test_fenced_code_block_skipped(self):
        text = "```\nstatus = approved\n```\n"
        self.assertEqual([], verdicts(text))


class TestLedgerLoading(unittest.TestCase):
    def test_load_ledger_roundtrip(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "ledger.jsonl"
            p.write_text(json.dumps({"decision_id": "R-001", "outcome": "GO"}) + "\n")
            self.assertEqual(claim_linter.load_ledger(p), {"R-001": "GO"})


if __name__ == "__main__":
    unittest.main()
