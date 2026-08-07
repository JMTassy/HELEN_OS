"""Acceptance tests for J1_MEETING_BRIEF_V0 (synthetic fixtures only)."""

import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from j1_meeting_brief import (  # noqa: E402
    MAX_LINES, BriefError, build_j1_brief, render_brief,
)

REGISTRY = [
    {"entity_id": "PERSON-A", "display_name": "Alex Martin",
     "known_emails": ["a.martin@example.org"], "domains": [], "aliases": []},
    {"entity_id": "PERSON-B", "display_name": "Alex Durand",
     "known_emails": ["a.durand@example.org"], "domains": [], "aliases": []},
    {"entity_id": "ORG-ALPHA", "display_name": "Alpha",
     "known_emails": [], "domains": ["alpha.example"],
     "aliases": [{"alias": "alpha-typo", "confirmed_by_operator": True}]},
]

EVENT = {"title": "Point Alpha", "start": "2099-01-02T09:00",
         "observed_in_calendar": True, "source_ref": "calendar:evt1"}

PARTICIPANTS = [
    {"display": "Alex Martin", "email": "a.martin@example.org",
     "names": ["Alex"], "source_ref": "calendar:evt1"},
    {"display": "Alex", "email": "", "names": ["Alex"],
     "source_ref": "calendar:evt1"},
]

EXCHANGES = [{"date": "2099-01-01", "person_id": "PERSON-A",
              "summary": "Envoi de l'ordre du jour.",
              "source_ref": "gmail:m1"}]

QUESTIONS = [{"question": "Budget validé ?", "status": "OPEN",
              "source_ref": "gmail:m1"}]

DOCS = [{"title": "Cadrage", "drive_ref": "drive:d1",
         "relevance_basis": "cité dans gmail:m1"}]

CONTRA = [{"statement_a": "réunion annoncée", "statement_b": "aucun événement",
           "source_refs": ["gmail:m1", "calendar:scan1"]}]

SCANNED = ["gmail:m1", "gmail:m2", "calendar:scan1"]
DISPOSITIONS = [
    {"source_id": "gmail:m1", "status": "RETAINED",
     "reason_code": "RELEVANT_TO_REQUEST"},
    {"source_id": "gmail:m2", "status": "DISMISSED", "reason_code": "NEWSLETTER"},
    {"source_id": "calendar:scan1", "status": "RETAINED",
     "reason_code": "NEGATIVE_OBSERVATION"},
]


def build_default(**over):
    kwargs = dict(event=copy.deepcopy(EVENT),
                  participants=copy.deepcopy(PARTICIPANTS),
                  registry=REGISTRY,
                  scanned_ids=list(SCANNED),
                  dispositions=copy.deepcopy(DISPOSITIONS),
                  latest_exchanges=copy.deepcopy(EXCHANGES),
                  unresolved_questions=copy.deepcopy(QUESTIONS),
                  documents_to_review=copy.deepcopy(DOCS),
                  contradictions=copy.deepcopy(CONTRA),
                  unknowns=["video_link"])
    kwargs.update(over)
    return build_j1_brief(**kwargs)


class TestJ1MeetingBrief(unittest.TestCase):

    def test_A1_unsourced_claim_raises(self):
        bad = [{"date": "2099-01-01", "summary": "sans source"}]
        with self.assertRaises(BriefError):
            build_default(latest_exchanges=bad)
        with self.assertRaises(BriefError):
            build_default(unresolved_questions=[
                {"question": "q", "status": "OPEN"}])

    def test_A2_participants_resolved_or_ambiguous_never_guessed(self):
        b = build_default()
        exact = b["participants"][0]
        self.assertEqual(exact["resolution_status"], "CONFIRMED")
        self.assertEqual(exact["person_id"], "PERSON-A")
        name_only = b["participants"][1]
        self.assertEqual(name_only["resolution_status"], "AMBIGUOUS")
        self.assertIsNone(name_only["person_id"])
        self.assertEqual(name_only["candidates"], ["PERSON-A", "PERSON-B"])

    def test_A3_undisposed_message_raises(self):
        with self.assertRaises(BriefError):
            build_default(dispositions=DISPOSITIONS[:2])

    def test_A4_no_autonomous_action_surface(self):
        b = build_default()
        self.assertEqual(b["distribution"], "JM_PRIVATE_DRAFT")
        for forbidden in ("actions", "proposals", "sent", "execution_status"):
            self.assertNotIn(forbidden, b)
        self.assertIn("aucune action", render_brief(b))

    def test_A5_deterministic_hash(self):
        self.assertEqual(build_default()["brief_hash"],
                         build_default()["brief_hash"])
        changed = copy.deepcopy(EXCHANGES)
        changed[0]["summary"] = "Autre résumé."
        self.assertNotEqual(build_default()["brief_hash"],
                            build_default(latest_exchanges=changed)["brief_hash"])

    def test_reported_event_never_rendered_confirmed(self):
        ev = {"title": "Point Alpha", "start": "2099-01-02T09:00",
              "observed_in_calendar": False, "source_ref": "gmail:m1"}
        b = build_default(event=ev)
        self.assertEqual(b["event"]["epistemic_status"], "REPORTED")
        out = render_brief(b)
        self.assertIn("RAPPORTÉ", out)
        self.assertIn("aucun événement observé dans Calendar", out)
        self.assertNotIn("confirmé", out.lower())

    def test_event_must_declare_observation_axis(self):
        with self.assertRaises(BriefError):
            build_default(event={"title": "X", "start": "…",
                                 "source_ref": "calendar:evt1"})

    def test_render_max_15_lines_hard(self):
        b = build_default()
        out = render_brief(b)
        self.assertLessEqual(len(out.splitlines()), MAX_LINES)
        many = [{"question": f"q{i}", "status": "OPEN", "source_ref": "gmail:m1"}
                for i in range(20)]
        over = build_default(unresolved_questions=many)
        with self.assertRaises(BriefError):
            render_brief(over)

    def test_every_rendered_factual_line_carries_a_ref(self):
        out = render_brief(build_default())
        for line in out.splitlines():
            if line.startswith(("Échange", "Question", "Doc:", "CONTRADICTION")):
                self.assertTrue("(" in line and ":" in line,
                                f"line without source ref: {line}")

    def test_invalid_question_status_raises(self):
        with self.assertRaises(BriefError):
            build_default(unresolved_questions=[
                {"question": "q", "status": "MAYBE", "source_ref": "gmail:m1"}])

    def test_posture_flags(self):
        b = build_default()
        self.assertFalse(b["authority"])
        self.assertFalse(b["canon"])
        self.assertEqual(b["ledger_effect"], "none")
        self.assertEqual(b["claim_status"], "LOCAL_OBSERVATION")


if __name__ == "__main__":
    unittest.main(verbosity=2)
