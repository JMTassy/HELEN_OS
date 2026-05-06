"""
tests/test_helen_computer_use_api.py
NON_SOVEREIGN · NO_SHIP · PROPOSAL

Acceptance tests for HELEN Computer Use API V1.
Claim: HELEN_COMPUTER_USE_API_V1
All tests must pass before MAYOR receipt.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from src.helen_computer_use_api import (
    HELENSession,
    RenderEnvelope, RelationResult, SessionState,
    SessionViolation, RendererViolation,
    UnboundedOpenRejected, UnboundedSearchRejected, RelationReceiptMissing,
    RELATION_BRIDGE, RELATION_CONTAINS, RELATION_REFERENCES,
    VALID_RELATION_TYPES,
)
from src.cso_identity_contract import ADMIT, REJECT, QUARANTINE
from src.helen_intake_agent import CoherenceSlice


# ── helpers ───────────────────────────────────────────────────────────────────

def _session():
    return HELENSession(session_id="test-session")

def _ingest_file(session, path="/docs/report.pdf", receipt="rcpt-file"):
    return session.ingest(path, receipt)

def _ingest_mail(session, msg_id="<x1>", receipt="rcpt-mail"):
    return session.ingest({
        "signal": "MAIL",
        "from_addr": "a@uzik.com",
        "to_addrs": ["b@c.com"],
        "message_id": msg_id,
        "subject": "HELEN demo",
    }, receipt)


# ── ingest ────────────────────────────────────────────────────────────────────

def test_ingest_file_accepted():
    s = _session()
    r = _ingest_file(s)
    assert r.status == ADMIT
    assert s.state().node_count == 1


def test_ingest_no_receipt_rejected():
    s = _session()
    r = s.ingest("/docs/report.pdf", "")
    assert r.status == REJECT
    assert s.state().node_count == 0


def test_ingest_unknown_signal_quarantined():
    s = _session()
    r = s.ingest({"signal": "WIDGET", "data": "x"}, "rcpt-1")
    assert r.status == QUARANTINE
    assert s.state().node_count == 0


def test_ingest_duplicate_idempotent():
    s = _session()
    _ingest_file(s)
    r2 = _ingest_file(s)
    assert r2.status == ADMIT
    assert s.state().node_count == 1  # no growth


def test_ingest_multiple_types():
    s = _session()
    _ingest_file(s, "/doc/a.pdf", "r1")
    _ingest_file(s, "/doc/b.mp4", "r2")
    _ingest_mail(s, "<m1>", "r3")
    assert s.state().node_count == 3


def test_ingest_timestamps_excluded():
    s = _session()
    r = s.ingest("/doc/a.pdf", "rcpt-1")
    node = list(s._graph._nodes.values())[0]
    for key in node.payload:
        assert "time" not in key.lower()
        assert "date" not in key.lower()


# ── open ──────────────────────────────────────────────────────────────────────

def test_open_with_namespace_filter():
    s = _session()
    _ingest_file(s, "/doc/a.pdf", "r1")
    _ingest_mail(s, "<m1>", "r2")
    slice_ = s.open({"namespace_filter": "files"})
    assert isinstance(slice_, CoherenceSlice)
    assert slice_.node_count == 1


def test_open_with_type_filter():
    s = _session()
    _ingest_file(s, "/a.pdf", "r1")
    _ingest_file(s, "/b.txt", "r2")
    slice_ = s.open({"type_filter": "FILE_PDF"})
    assert slice_.node_count == 1


def test_open_unbounded_rejected():
    s = _session()
    _ingest_file(s)
    with pytest.raises(UnboundedOpenRejected):
        s.open({})


def test_open_returns_coherence_slice():
    s = _session()
    _ingest_file(s)
    result = s.open({"namespace_filter": "files"})
    assert isinstance(result, CoherenceSlice)
    assert result.node_count >= 1


def test_open_empty_graph_returns_empty_slice():
    s = _session()
    slice_ = s.open({"namespace_filter": "files"})
    assert slice_.node_count == 0


def test_open_deterministic():
    s = _session()
    _ingest_file(s, "/doc/a.pdf", "r1")
    s1 = s.open({"namespace_filter": "files"})
    s2 = s.open({"namespace_filter": "files"})
    assert s1.graph_hash == s2.graph_hash
    assert s1.nodes == s2.nodes


# ── search ────────────────────────────────────────────────────────────────────

def test_search_by_namespace():
    s = _session()
    _ingest_file(s, "/a.pdf", "r1")
    _ingest_mail(s, "<m1>", "r2")
    result = s.search({"namespace_filter": "mail"})
    assert result.node_count == 1


def test_search_untyped_rejected():
    s = _session()
    with pytest.raises(UnboundedSearchRejected):
        s.search({})


def test_search_by_type():
    s = _session()
    _ingest_file(s, "/a.pdf", "r1")
    _ingest_file(s, "/b.mp3", "r2")
    result = s.search({"type_filter": "MEDIA_AUDIO"})
    assert result.node_count == 1


def test_search_relation_to():
    s = _session()
    r1 = _ingest_file(s, "/a.pdf", "rcpt-a")
    # ingest a mail that references the file
    r2 = _ingest_mail(s, "<m1>", "rcpt-m")
    file_id = r1.global_id
    mail_id = r2.global_id
    # relate them
    s.relate(mail_id, file_id, RELATION_REFERENCES, "rcpt-rel")
    # search for objects related to the file
    result = s.search({"relation_to": mail_id})
    assert result.node_count >= 1


def test_search_deterministic():
    s = _session()
    _ingest_file(s, "/a.pdf", "r1")
    q = {"namespace_filter": "files"}
    r1 = s.search(q)
    r2 = s.search(q)
    assert r1.graph_hash == r2.graph_hash


# ── render ────────────────────────────────────────────────────────────────────

def test_render_returns_envelope():
    s = _session()
    r = _ingest_file(s)
    envelope = s.render(r.global_id, "PDF_VIEWER")
    assert isinstance(envelope, RenderEnvelope)
    assert envelope.renderer_hint == "PDF_VIEWER"


def test_render_authority_always_zero():
    s = _session()
    r = _ingest_file(s)
    envelope = s.render(r.global_id)
    assert envelope.authority == 0


def test_render_unknown_id_raises():
    s = _session()
    with pytest.raises(KeyError):
        s.render("files/nonexistent-id-abc")


def test_render_logs_to_session():
    s = _session()
    r = _ingest_file(s)
    assert s.state().render_log_count == 0
    s.render(r.global_id)
    assert s.state().render_log_count == 1


def test_render_contains_slice():
    s = _session()
    r = _ingest_file(s)
    envelope = s.render(r.global_id)
    assert isinstance(envelope.slice, CoherenceSlice)
    assert r.global_id in envelope.slice.nodes


def test_render_receipt_is_string():
    s = _session()
    r = _ingest_file(s)
    envelope = s.render(r.global_id)
    assert isinstance(envelope.session_receipt, str)
    assert len(envelope.session_receipt) > 0


# ── relate ────────────────────────────────────────────────────────────────────

def test_relate_valid_relation():
    s = _session()
    ra = _ingest_file(s, "/a.pdf", "r1")
    rm = _ingest_mail(s, "<m1>", "r2")
    result = s.relate(rm.global_id, ra.global_id, RELATION_REFERENCES, "rcpt-rel")
    assert result.status == ADMIT


def test_relate_no_receipt_raises():
    s = _session()
    ra = _ingest_file(s, "/a.pdf", "r1")
    rm = _ingest_mail(s, "<m1>", "r2")
    with pytest.raises(RelationReceiptMissing):
        s.relate(rm.global_id, ra.global_id, RELATION_REFERENCES, "")


def test_relate_invalid_type_rejected():
    s = _session()
    ra = _ingest_file(s, "/a.pdf", "r1")
    rm = _ingest_mail(s, "<m1>", "r2")
    result = s.relate(rm.global_id, ra.global_id, "INVENTED_RELATION", "rcpt-1")
    assert result.status == REJECT


def test_relate_unknown_id_rejected():
    s = _session()
    _ingest_file(s, "/a.pdf", "r1")
    result = s.relate("files/nonexistent", "files/also-nonexistent",
                       RELATION_CONTAINS, "rcpt-1")
    assert result.status == REJECT


def test_relate_adds_to_graph_edges():
    s = _session()
    ra = _ingest_file(s, "/a.pdf", "r1")
    rm = _ingest_mail(s, "<m1>", "r2")
    s.relate(rm.global_id, ra.global_id, RELATION_REFERENCES, "rcpt-rel")
    mail_node = s._graph.get(rm.global_id)
    assert ra.global_id in mail_node.relations


def test_relate_duplicate_idempotent():
    s = _session()
    ra = _ingest_file(s, "/a.pdf", "r1")
    rm = _ingest_mail(s, "<m1>", "r2")
    r1 = s.relate(rm.global_id, ra.global_id, RELATION_REFERENCES, "rcpt-1")
    r2 = s.relate(rm.global_id, ra.global_id, RELATION_REFERENCES, "rcpt-2")
    assert r1.status == ADMIT
    assert r2.status == ADMIT
    # edge not duplicated
    mail_node = s._graph.get(rm.global_id)
    assert mail_node.relations.count(ra.global_id) == 1


# ── session state + replay determinism ───────────────────────────────────────

def test_session_state_is_deterministic():
    s1 = HELENSession(session_id="s1")
    s2 = HELENSession(session_id="s2")
    for session in [s1, s2]:
        session.ingest("/a.pdf", "r1")
        session.ingest({"signal": "MAIL", "from_addr": "x@y.com",
                        "message_id": "<m1>", "subject": "T"}, "r2")
    assert s1.state().graph_hash == s2.state().graph_hash
    assert s1.state().node_count == s2.state().node_count


def test_session_receipt_count_grows():
    s = _session()
    assert s.state().receipt_count == 0
    _ingest_file(s, "/a.pdf", "r1")
    assert s.state().receipt_count == 1
    _ingest_mail(s, "<m1>", "r2")
    assert s.state().receipt_count == 2


def test_session_repr():
    s = _session()
    r = repr(s)
    assert "HELENSession" in r
    assert "nodes=" in r
