"""Tests T01–T15 for BEAD-GOVERNED-CONTEXT-PACKET-001."""

import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from governed_context_packet import (  # noqa: E402
    PacketError, build_packet, derive, evaluate_permission, memory_candidacy,
    packet_hash, reconcile, render_brief, resolve_entity, resolve_taint,
)

# ------------------------------------------------------------------ fixtures

REGISTRY = [
    {"entity_id": "ORG-ALPHA", "display_name": "Alpha",
     "known_emails": [], "domains": ["alpha.example"],
     "aliases": [{"alias": "alpha-typo", "confirmed_by_operator": True},
                 {"alias": "alfa", "confirmed_by_operator": True}]},
    {"entity_id": "PERSON-A", "display_name": "Alex Martin",
     "known_emails": ["a.martin@example.org"], "domains": [], "aliases": []},
    {"entity_id": "PERSON-B", "display_name": "Alex Durand",
     "known_emails": ["a.durand@example.org"], "domains": [], "aliases": []},
]

PERMISSION = {
    "source_access_allowed": True,
    "intended_recipient": "JM",
    "lawful_purpose": "MEETING_PREPARATION",
    "permitted_use": ["READ", "SUMMARIZE"],
    "forbidden_use": ["SEND", "SHARE_EXTERNALLY", "WRITE_MEMORY"],
    "destination_scope": ["JM_PRIVATE_BRIEF"],
    "retention": {"mode": "SESSION_ONLY", "expires_on": None},
}


def make_sources():
    return [
        {"source_id": "gmail:m1", "source_type": "GMAIL_MESSAGE",
         "retrieved": True,
         "disposition": {"status": "RETAINED",
                         "reason_code": "RELEVANT_TO_REQUEST"},
         "entity_links": [{"entity_id": "ORG-ALPHA", "status": "CONFIRMED",
                           "basis": ["exact_email_domain"]}],
         "extracted_claims": [
             {"claim_id": "c1",
              "statement": "Un rendez-vous est annoncé pour le 5 août.",
              "epistemic_status": "REPORTED",
              "contradiction_status": "UNRESOLVED"}]},
        {"source_id": "calendar:scan1", "source_type": "CALENDAR_SCAN",
         "retrieved": True,
         "disposition": {"status": "RETAINED",
                         "reason_code": "NEGATIVE_OBSERVATION"},
         "entity_links": [],
         "extracted_claims": [
             {"claim_id": "c2",
              "statement": "Aucun événement correspondant dans Calendar.",
              "epistemic_status": "OBSERVED",
              "contradiction_status": "UNRESOLVED"}]},
        {"source_id": "gmail:m2", "source_type": "GMAIL_MESSAGE",
         "retrieved": True,
         "disposition": {"status": "DISMISSED", "reason_code": "NEWSLETTER"},
         "entity_links": [], "extracted_claims": []},
    ]


CONTRADICTION = {
    "contradiction_id": "x1", "field": "meeting_exists",
    "propositions": [
        {"value": True, "status": "REPORTED", "source_refs": ["gmail:m1"]},
        {"value": False, "status": "OBSERVED",
         "meaning": "Aucun événement correspondant trouvé dans Calendar.",
         "source_refs": ["calendar:scan1"]},
    ],
    "resolution_status": "UNRESOLVED",
}

UNKNOWNS = [
    {"field": "meeting_time", "reason": "NO_SUPPORTING_SOURCE"},
    {"field": "participants", "reason": "NO_SUPPORTING_SOURCE"},
    {"field": "video_link", "reason": "NO_SUPPORTING_SOURCE"},
]

PROPOSAL = {"action": "CREATE_CALENDAR_EVENT", "authority": False,
            "execution_status": "NOT_EXECUTED"}


def build_default(**over):
    kwargs = dict(
        query={"text": "Prepare le rendez-vous ORG-ALPHA"},
        sources=make_sources(),
        scanned_ids=["gmail:m1", "calendar:scan1", "gmail:m2"],
        entities=[{"entity_id": "ORG-ALPHA", "status": "CONFIRMED"}],
        permission=copy.deepcopy(PERMISSION),
        requested_purpose="MEETING_PREPARATION",
        requested_use="READ",
        recipient="JM_PRIVATE_BRIEF",
        contradictions=[copy.deepcopy(CONTRADICTION)],
        unknowns=copy.deepcopy(UNKNOWNS),
        proposals=[copy.deepcopy(PROPOSAL)],
    )
    kwargs.update(over)
    return build_packet(**kwargs)


# ------------------------------------------------------------------ tests

class TestGovernedContextPacket(unittest.TestCase):

    def test_T01_every_message_disposed(self):
        p = build_default()
        r = p["scan_reconciliation"]
        self.assertEqual(r["undisposed"], 0)
        self.assertTrue(r["balanced"])
        self.assertEqual(r["scanned"],
                         r["retained"] + r["dismissed"]
                         + r["deferred"] + r["duplicate"])

    def test_T02_reconciliation_fails_on_disappeared_message(self):
        sources = make_sources()[:2]  # gmail:m2 scanned but never disposed
        with self.assertRaises(PacketError):
            build_default(sources=sources)

    def test_T03_same_first_name_stays_ambiguous(self):
        binding = resolve_entity({"names_mentioned": ["Alex"]}, REGISTRY)
        self.assertEqual(binding["status"], "AMBIGUOUS")
        self.assertIn("PERSON-A", binding["candidates"])
        self.assertIn("PERSON-B", binding["candidates"])
        self.assertIsNone(binding["entity_id"])

    def test_T04_operator_confirmed_alias_confirms(self):
        b1 = resolve_entity({"names_mentioned": ["Alpha-Typo"]}, REGISTRY)
        self.assertEqual(b1["status"], "CONFIRMED")
        self.assertEqual(b1["entity_id"], "ORG-ALPHA")
        b2 = resolve_entity({"names_mentioned": ["alfa"]}, REGISTRY)
        self.assertEqual(b2["status"], "CONFIRMED")
        self.assertEqual(b2["entity_id"], "ORG-ALPHA")

    def test_T05_reported_and_contradicted_coexist(self):
        claim = {"claim_id": "c", "statement": "s",
                 "epistemic_status": "REPORTED",
                 "contradiction_status": "CONTRADICTED"}
        src = {"source_id": "gmail:m9", "source_type": "GMAIL_MESSAGE",
               "disposition": {"status": "RETAINED", "reason_code": "X"},
               "entity_links": [], "extracted_claims": [claim]}
        p = build_default(sources=make_sources() + [src],
                          scanned_ids=["gmail:m1", "calendar:scan1",
                                       "gmail:m2", "gmail:m9"])
        stored = [c for s in p["sources"]
                  for c in s.get("extracted_claims", [])
                  if c["claim_id"] == "c"][0]
        self.assertEqual(stored["epistemic_status"], "REPORTED")
        self.assertEqual(stored["contradiction_status"], "CONTRADICTED")

    def test_T06_missing_calendar_event_does_not_erase_report(self):
        p = build_default()
        claims = [c for s in p["sources"]
                  for c in s.get("extracted_claims", [])]
        reported = [c for c in claims if c["epistemic_status"] == "REPORTED"]
        self.assertTrue(reported, "reported meeting must survive")
        contr = p["contradictions"][0]
        self.assertEqual(contr["resolution_status"], "UNRESOLVED")
        self.assertEqual(len(contr["propositions"]), 2)

    def test_T07_summarization_preserves_contradiction_taint(self):
        p = build_default()
        src = p["sources"][0]
        self.assertTrue(any(t["type"] == "CONTRADICTION_UNRESOLVED"
                            for t in src["taints"]))
        summary = derive(src, "summarization", content="résumé")
        for t in src["taints"]:
            self.assertIn(t, summary["taints"])

    def test_T08_export_preserves_entity_ambiguity_taint(self):
        obj = {"id": "o1", "content": "x",
               "taints": [{"type": "ENTITY_AMBIGUITY", "source_ref": "gmail:m1"}]}
        exported = derive(derive(obj, "summarization"), "export")
        self.assertIn({"type": "ENTITY_AMBIGUITY", "source_ref": "gmail:m1"},
                      exported["taints"])
        # removal requires a typed receipt
        with self.assertRaises(PacketError):
            resolve_taint(exported, exported["taints"][0], {})

    def test_T09_purpose_forbidden_blocks_packet(self):
        p = build_default(requested_purpose="MARKETING")
        self.assertEqual(p["packet_status"], "BLOCKED")
        self.assertIn("PURPOSE_FORBIDDEN",
                      p["permission_gate"]["blocking_reasons"])

    def test_T10_retention_forbidden_no_memory_candidate(self):
        p = build_default()
        self.assertEqual(p["permissions"]["memory_candidacy"], "NOT_CANDIDATE")
        self.assertEqual(memory_candidacy(PERMISSION), "NOT_CANDIDATE")

    def test_T11_same_inputs_same_hash(self):
        p1, p2 = build_default(), build_default()
        self.assertEqual(p1["packet_id"], p2["packet_id"])

    def test_T12_changed_source_changes_hash(self):
        p1 = build_default()
        sources = make_sources()
        sources[0]["extracted_claims"][0]["statement"] = "Autre chose."
        p2 = build_default(sources=sources)
        self.assertNotEqual(p1["packet_id"], p2["packet_id"])

    def test_T13_brief_contains_all_unknowns(self):
        p = build_default()
        brief = render_brief(p)
        for u in UNKNOWNS:
            self.assertIn(u["field"], brief)
        # and the unresolved contradiction is visible
        self.assertIn("meeting_exists", brief)

    def test_T14_no_proposal_marked_executed(self):
        bad = {"action": "SEND_EMAIL", "authority": False,
               "execution_status": "EXECUTED"}
        with self.assertRaises(PacketError):
            build_default(proposals=[bad])

    def test_T15_run_yields_local_observation_only(self):
        p = build_default()
        self.assertEqual(p["claim_status"], "LOCAL_OBSERVATION")
        self.assertFalse(p["authority"])
        self.assertFalse(p["canon"])
        self.assertEqual(p["ledger_effect"], "none")


if __name__ == "__main__":
    unittest.main(verbosity=2)
