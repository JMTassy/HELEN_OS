"""
tests/test_helen_intake_agent.py
NON_SOVEREIGN · NO_SHIP · PROPOSAL

Acceptance tests for HELEN PULL intake bridge.
Claim: HELEN_PULL_INTAKE_BRIDGE_V1
All tests must pass before MAYOR receipt.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from src.helen_intake_agent import (
    intake_signal, admit_intake, admit_intake_to_graph, project_context,
    CSOCandidate, CoherenceSlice,
    SIGNAL_FILE, SIGNAL_MAIL, SIGNAL_MEDIA, SIGNAL_SCREEN,
    NAMESPACE_FILE, NAMESPACE_MAIL, NAMESPACE_MEDIA, NAMESPACE_SCREEN,
)
from src.cso_identity_contract import ADMIT, REJECT, QUARANTINE
from src.semantic_object_model import SemanticGraph


# ── intake_signal: FILE ───────────────────────────────────────────────────────

def test_file_path_string_classified():
    c = intake_signal("/home/user/docs/report.pdf")
    assert c.cso_type == "FILE_PDF"
    assert c.namespace == NAMESPACE_FILE
    assert c.payload["extension"] == ".pdf"
    assert "date" not in c.payload
    assert "mtime" not in c.payload


def test_file_dict_classified():
    c = intake_signal({"signal": "FILE", "path": "/home/user/code/main.py"})
    assert c.cso_type == "FILE_CODE"
    assert c.namespace == NAMESPACE_FILE


def test_file_text_classified():
    c = intake_signal("/notes/todo.txt")
    assert c.cso_type == "FILE_TEXT"


def test_file_generic_classified():
    c = intake_signal("/data/archive.zip")
    assert c.cso_type == "FILE_GENERIC"


def test_file_local_id_is_content_addressed():
    c = intake_signal("/path/to/report.pdf")
    from src.cso_identity_contract import law_1_identity_determinism
    expected = law_1_identity_determinism(c.namespace, c.payload)
    assert c.local_id == expected


def test_file_timestamp_excluded():
    c = intake_signal("/any/file.pdf")
    for key in c.payload:
        assert "time" not in key.lower()
        assert "date" not in key.lower()
        assert "mtime" not in key.lower()


# ── intake_signal: MEDIA ──────────────────────────────────────────────────────

def test_media_video_file_path():
    c = intake_signal("/footage/scene01.mp4")
    assert c.cso_type == "MEDIA_VIDEO"
    assert c.namespace == NAMESPACE_MEDIA


def test_media_image_file_path():
    c = intake_signal("/assets/hero.jpg")
    assert c.cso_type == "MEDIA_IMAGE"
    assert c.namespace == NAMESPACE_MEDIA


def test_media_audio_file_path():
    c = intake_signal("/audio/track.mp3")
    assert c.cso_type == "MEDIA_AUDIO"
    assert c.namespace == NAMESPACE_MEDIA


def test_media_dict_with_meta():
    c = intake_signal({
        "signal": "MEDIA",
        "title": "HELEN intro",
        "duration_seconds": 30.0,
        "codec": "h264",
        "width": 1920,
        "height": 1080,
        "mime_type": "video/mp4",
    })
    assert c.cso_type == "MEDIA_VIDEO"
    assert c.payload["width"] == 1920
    assert "duration_seconds" in c.payload
    assert "date" not in c.payload


# ── intake_signal: MAIL ───────────────────────────────────────────────────────

def test_mail_envelope_classified():
    c = intake_signal({
        "signal": "MAIL",
        "subject": "HELEN demo review",
        "from_addr": "jm@uzik.com",
        "to_addrs": ["partner@rothschild.com"],
        "message_id": "<abc@mail>",
        "body_snippet": "Please review the attached deck.",
    })
    assert c.cso_type == "MAIL_MESSAGE"
    assert c.namespace == NAMESPACE_MAIL
    assert c.payload["subject"] == "HELEN demo review"
    assert "date" not in c.payload


def test_mail_to_addrs_sorted():
    c = intake_signal({
        "signal": "MAIL",
        "from_addr": "a@b.com",
        "to_addrs": ["z@b.com", "a@b.com"],
        "message_id": "<x>",
    })
    assert c.payload["to_addrs"] == sorted(["z@b.com", "a@b.com"])


def test_mail_body_snippet_truncated():
    c = intake_signal({
        "signal": "MAIL",
        "from_addr": "a@b.com",
        "message_id": "<x>",
        "body_snippet": "X" * 1000,
    })
    assert len(c.payload["body_snippet"]) <= 512


# ── intake_signal: SCREEN ─────────────────────────────────────────────────────

def test_screen_region_classified():
    c = intake_signal({
        "signal": "SCREEN",
        "ocr_text": "Open in HELEN",
        "app_hint": "Finder",
        "region_label": "toolbar",
    })
    assert c.cso_type == "SCREEN_REGION"
    assert c.namespace == NAMESPACE_SCREEN


# ── intake_signal: unknown / errors ──────────────────────────────────────────

def test_unknown_signal_quarantine_namespace():
    c = intake_signal({"signal": "WIDGET", "data": "xyz"})
    assert c.namespace == "quarantine"
    assert c.cso_type == "UNKNOWN"


def test_none_input_does_not_raise():
    c = intake_signal(None)
    assert c.namespace == "quarantine"
    assert c.cso_type in {"INTAKE_ERROR", "UNKNOWN"}


# ── intake_signal: determinism ────────────────────────────────────────────────

def test_same_file_same_local_id():
    c1 = intake_signal("/docs/report.pdf")
    c2 = intake_signal("/docs/report.pdf")
    assert c1.local_id == c2.local_id


def test_different_file_different_local_id():
    c1 = intake_signal("/docs/report.pdf")
    c2 = intake_signal("/docs/other.pdf")
    assert c1.local_id != c2.local_id


# ── admit_intake ──────────────────────────────────────────────────────────────

def test_admit_with_receipt_accepted():
    c = intake_signal("/docs/report.pdf")
    result = admit_intake(c, operator_receipt="user:open:2026-05-06")
    assert result.status == ADMIT


def test_admit_without_receipt_rejected():
    c = intake_signal("/docs/report.pdf")
    result = admit_intake(c, operator_receipt="")
    assert result.status == REJECT


def test_admit_unknown_signal_quarantined():
    c = intake_signal({"signal": "UNKNOWN"})
    result = admit_intake(c, operator_receipt="user:open:2026-05-06")
    # quarantine namespace → empty provenance chain → QUARANTINE
    assert result.status == QUARANTINE


def test_admit_duplicate_idempotent():
    from src.cso_identity_contract import law_1_identity_determinism
    c = intake_signal("/docs/report.pdf")
    existing_hash = law_1_identity_determinism(c.namespace, c.payload)
    existing_graph = {c.global_id: existing_hash}
    result = admit_intake(c, "user:open:2026-05-06", existing_graph=existing_graph)
    assert result.status == ADMIT
    assert "idempotent" in result.reason.lower()


def test_admit_to_graph_appends_cso():
    g = SemanticGraph()
    c = intake_signal("/docs/report.pdf")
    result = admit_intake_to_graph(c, "user:open:2026-05-06", g)
    assert result.status == ADMIT
    assert len(g) == 1
    assert g.get(c.global_id) is not None


def test_admit_to_graph_duplicate_noop():
    g = SemanticGraph()
    c = intake_signal("/docs/report.pdf")
    admit_intake_to_graph(c, "user:open:2026-05-06", g)
    result = admit_intake_to_graph(c, "user:open:2026-05-06", g)
    assert result.status == ADMIT
    assert len(g) == 1  # graph did not grow


# ── project_context ───────────────────────────────────────────────────────────

def _build_mixed_graph() -> SemanticGraph:
    g = SemanticGraph()
    for path in ["/doc/a.pdf", "/doc/b.txt"]:
        c = intake_signal(path)
        admit_intake_to_graph(c, "rcpt-file", g)
    mail = intake_signal({"signal": "MAIL", "from_addr": "a@b.com",
                           "message_id": "<x1>", "subject": "S1"})
    admit_intake_to_graph(mail, "rcpt-mail", g)
    return g


def test_project_context_namespace_filter():
    g = _build_mixed_graph()
    slice_ = project_context(g, {"namespace_filter": NAMESPACE_MAIL})
    assert slice_.node_count == 1
    for gid in slice_.nodes:
        assert gid.startswith(NAMESPACE_MAIL + "/")


def test_project_context_no_filter_all_nodes():
    g = _build_mixed_graph()
    slice_ = project_context(g, {})
    assert slice_.node_count == 3


def test_project_context_deterministic():
    g = _build_mixed_graph()
    s1 = project_context(g, {"namespace_filter": NAMESPACE_FILE})
    s2 = project_context(g, {"namespace_filter": NAMESPACE_FILE})
    assert s1.graph_hash == s2.graph_hash
    assert s1.nodes == s2.nodes


def test_project_context_type_filter():
    g = _build_mixed_graph()
    slice_ = project_context(g, {"type_filter": "FILE_TEXT"})
    assert slice_.node_count == 1
    for info in slice_.nodes.values():
        assert info["type"] == "FILE_TEXT"


def test_project_context_empty_graph():
    g = SemanticGraph()
    slice_ = project_context(g, {})
    assert slice_.node_count == 0
    assert isinstance(slice_.graph_hash, str)


def test_project_context_returns_coherence_slice():
    g = _build_mixed_graph()
    result = project_context(g, {"namespace_filter": NAMESPACE_FILE})
    assert isinstance(result, CoherenceSlice)
    assert result.namespace_filter == NAMESPACE_FILE
