"""Workspace validator and script-refusal tests."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import validate_workspace  # noqa: E402
from append_decision import append_decision  # noqa: E402
from create_execution_packet import create_packet  # noqa: E402


class TestShippedWorkspaceIsValid(unittest.TestCase):
    def test_validator_passes_on_shipped_workspace(self):
        errors, _warnings = validate_workspace.validate()
        self.assertEqual(errors, [], "shipped workspace must validate clean:\n"
                         + "\n".join(errors))


class TestAppendDecision(unittest.TestCase):
    def _ledger(self, td):
        return Path(td) / "decision_ledger.jsonl"

    def _valid(self):
        return {
            "decision_id": "R-001", "date": "2026-07-16",
            "subject": "test subject", "outcome": "GO",
            "scope": "test scope", "rationale": "test rationale",
            "authorized_by": "ROSE",
        }

    def test_appends_valid_decision(self):
        with tempfile.TemporaryDirectory() as td:
            path = self._ledger(td)
            append_decision(self._valid(), ledger_path=path)
            rec = json.loads(path.read_text().strip())
            self.assertEqual(rec["decision_id"], "R-001")

    def test_refuses_missing_fields(self):
        rec = self._valid()
        del rec["rationale"]
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(ValueError):
                append_decision(rec, ledger_path=self._ledger(td))

    def test_refuses_bad_outcome(self):
        rec = self._valid()
        rec["outcome"] = "SHIP"
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(ValueError):
                append_decision(rec, ledger_path=self._ledger(td))

    def test_refuses_non_rose_authorizer(self):
        rec = self._valid()
        rec["authorized_by"] = "the strategy function"
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(ValueError):
                append_decision(rec, ledger_path=self._ledger(td))

    def test_refuses_duplicate_id(self):
        with tempfile.TemporaryDirectory() as td:
            path = self._ledger(td)
            append_decision(self._valid(), ledger_path=path)
            with self.assertRaises(ValueError):
                append_decision(self._valid(), ledger_path=path)


class TestCreateExecutionPacket(unittest.TestCase):
    def _setup(self, td, outcome="GO"):
        ledger = Path(td) / "decision_ledger.jsonl"
        ledger.write_text(json.dumps({
            "decision_id": "R-001", "date": "2026-07-16", "subject": "s",
            "outcome": outcome, "scope": "sc", "rationale": "r",
            "authorized_by": "ROSE"}) + "\n")
        active = Path(td) / "active"
        active.mkdir()
        return ledger, active

    def test_creates_packet_for_go_decision(self):
        with tempfile.TemporaryDirectory() as td:
            ledger, active = self._setup(td, "GO")
            path = create_packet("R-001", "outcome text", "scope text", "ROSE",
                                 "INTERNAL_BUSINESS", ledger_path=ledger,
                                 active_dir=active)
            packet = json.loads(path.read_text())
            self.assertEqual(packet["approved_decision_id"], "R-001")
            self.assertEqual(packet["status"], "PLANNED")

    def test_refuses_missing_decision(self):
        with tempfile.TemporaryDirectory() as td:
            ledger, active = self._setup(td, "GO")
            with self.assertRaises(ValueError):
                create_packet("R-999", "o", "s", "ROSE", "INTERNAL_BUSINESS",
                              ledger_path=ledger, active_dir=active)

    def test_refuses_non_go_decision(self):
        with tempfile.TemporaryDirectory() as td:
            ledger, active = self._setup(td, "HOLD")
            with self.assertRaises(ValueError):
                create_packet("R-001", "o", "s", "ROSE", "INTERNAL_BUSINESS",
                              ledger_path=ledger, active_dir=active)

    def test_refuses_bad_privacy_class(self):
        with tempfile.TemporaryDirectory() as td:
            ledger, active = self._setup(td, "GO")
            with self.assertRaises(ValueError):
                create_packet("R-001", "o", "s", "ROSE", "SECRETISH",
                              ledger_path=ledger, active_dir=active)


class TestForbiddenNameScan(unittest.TestCase):
    def test_token_list_is_nonempty_and_lowercase(self):
        toks = validate_workspace.FORBIDDEN_NAME_TOKENS
        self.assertGreater(len(toks), 5)
        for t in toks:
            self.assertEqual(t, t.lower())


if __name__ == "__main__":
    unittest.main()
