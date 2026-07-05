"""Tests for apps/goblin-warren/build_warren_feed.py (WARREN_FEED_V0).

NON_SOVEREIGN | authority=false | ledger_effect=none

Gate contract:
  - deterministic: same outbox bytes -> same feed bytes (replay witness)
  - HAL is never a courier
  - authority stays false in the emitted feed
  - unreadable packets are fail-visible (skipped as BAD_JSON), never dropped
  - operator marks surface display-only; pen log overrides triage/resolved
"""

import importlib.util
import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
BUILDER = REPO_ROOT / "apps" / "goblin-warren" / "build_warren_feed.py"

spec = importlib.util.spec_from_file_location("build_warren_feed", BUILDER)
bwf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bwf)


def _packet(pid, finding_type="proposal", **over):
    d = {
        "schema": "AUTORESEARCH_PACKET_V1",
        "packet_id": pid,
        "finding_type": finding_type,
        "summary": f"summary for {pid}",
        "recommended_action": "ROUTE_TO_OPERATOR_FOR_REVIEW",
        "authority": False,
        "sovereign": False,
        "canon": False,
        "ledger_effect": "none",
        "reducer_required": True,
        "scanned_at": "2026-07-03T00:00:00Z",
        "provenance": {"proposer": "gemma4-12b:latest (test)"},
    }
    d.update(over)
    return d


@pytest.fixture
def garden(tmp_path):
    outbox = tmp_path / "outbox"
    resolved = tmp_path / "resolved"
    outbox.mkdir()
    resolved.mkdir()
    for pid, ft in [
        ("AR-000000000001", "risk"),
        ("AR-000000000002", "risk"),
        ("AR-000000000003", "test_gap"),
        ("AR-000000000004", "proposal"),
        ("AR-000000000005", "weird_new_type"),
    ]:
        (outbox / f"{pid}.json").write_text(json.dumps(_packet(pid, ft)))
    return outbox, resolved, tmp_path / "consumption_log.ndjson"


def test_deterministic_replay(garden):
    outbox, resolved, pen = garden
    a = bwf.render_js(bwf.build_feed(outbox, resolved, pen))
    b = bwf.render_js(bwf.build_feed(outbox, resolved, pen))
    assert a == b


def test_hal_never_carries_and_all_routed(garden):
    outbox, resolved, pen = garden
    feed = bwf.build_feed(outbox, resolved, pen)
    assert "HAL" not in feed["roles"]
    assert sum(len(v) for v in feed["roles"].values()) == feed["packet_count"] == 5


def test_feed_stays_non_sovereign(garden):
    outbox, resolved, pen = garden
    feed = bwf.build_feed(outbox, resolved, pen)
    assert feed["authority"] is False
    assert feed["sovereign"] is False
    assert feed["canon"] is False
    assert feed["ledger_effect"] == "none"


def test_bad_json_is_fail_visible_not_dropped(garden):
    outbox, resolved, pen = garden
    (outbox / "AR-00000000dead.json").write_text("{not json")
    feed = bwf.build_feed(outbox, resolved, pen)
    assert feed["packet_count"] == 5
    assert len(feed["skipped"]) == 1
    assert feed["skipped"][0]["file"] == "AR-00000000dead.json"
    assert feed["skipped"][0]["reason"].startswith("BAD_JSON")


def test_bad_json_changes_digest(garden):
    outbox, resolved, pen = garden
    before = bwf.build_feed(outbox, resolved, pen)["source_digest"]
    (outbox / "AR-00000000dead.json").write_text("{not json")
    after = bwf.build_feed(outbox, resolved, pen)["source_digest"]
    assert before != after


def test_marks_surface_and_pen_overrides_resolved(garden):
    outbox, resolved, pen = garden
    (resolved / "AR-000000000001_marked.json").write_text(
        json.dumps({"packet_id": "AR-000000000001", "decision": "deferred"})
    )
    pen.write_text(
        json.dumps({"packet_id": "AR-000000000001", "decision": "acted"}) + "\n"
    )
    feed = bwf.build_feed(outbox, resolved, pen)
    by_id = {p["packet_id"]: p for v in feed["roles"].values() for p in v}
    assert by_id["AR-000000000001"]["mark"] == "acted"
    assert by_id["AR-000000000002"]["mark"] is None


def test_unknown_finding_type_routes_forward_compatible(garden):
    outbox, resolved, pen = garden
    feed = bwf.build_feed(outbox, resolved, pen)
    by_id = {p["packet_id"]: role for role, v in feed["roles"].items() for p in v}
    assert by_id["AR-000000000005"] in bwf.DEFAULT_GROUP


def test_check_mode_passes_then_detects_drift(garden, tmp_path):
    outbox, resolved, pen = garden
    out = tmp_path / "warren_town_feed.js"
    argv_base = [
        "--outbox", str(outbox), "--resolved", str(resolved),
        "--pen-log", str(pen), "--out", str(out),
    ]
    assert bwf.main(argv_base) == 0
    assert bwf.main(argv_base + ["--check"]) == 0
    # outbox mutates after build -> the on-disk feed no longer replays
    (outbox / "AR-000000000009.json").write_text(json.dumps(_packet("AR-000000000009")))
    assert bwf.main(argv_base + ["--check"]) == 1


def test_real_feed_on_disk_replays_if_present():
    """The committed sidecar must replay from the committed outbox (skip if absent)."""
    out = REPO_ROOT / "apps" / "goblin-warren" / "warren_town_feed.js"
    outbox = REPO_ROOT / "temple" / "autoresearch" / "outbox"
    if not (out.is_file() and outbox.is_dir()):
        pytest.skip("real feed or outbox not present")
    rc = bwf.main([
        "--outbox", str(outbox),
        "--resolved", str(REPO_ROOT / "temple" / "autoresearch" / "triage" / "resolved"),
        "--pen-log", str(REPO_ROOT / "temple" / "autoresearch" / "consumption_log.ndjson"),
        "--out", str(out), "--check",
    ])
    assert rc == 0, "warren_town_feed.js is stale — rerun build_warren_feed.py"


# --- AAA_FRAMEWORK_PASS: feed enrichment + safety-boundary invariants -----------

def _all_packets(feed):
    return [p for ps in feed["roles"].values() for p in ps]


def test_every_packet_is_authority_false(garden):
    feed = bwf.build_feed(*garden)
    assert all(p["authority"] is False for p in _all_packets(feed))


def test_every_packet_forbids_admission(garden):
    feed = bwf.build_feed(*garden)
    assert all(p["admission"] == "FORBIDDEN" for p in _all_packets(feed))


def test_severity_is_deterministic_and_bounded(garden):
    feed = bwf.build_feed(*garden)
    allowed = {"info", "low", "medium", "high"}
    by_id = {p["packet_id"]: p for p in _all_packets(feed)}
    assert all(p["severity"] in allowed for p in _all_packets(feed))
    # risk maps to high; proposal to low; unknown type to info
    assert by_id["AR-000000000001"]["severity"] == "high"      # risk
    assert by_id["AR-000000000004"]["severity"] == "low"       # proposal
    assert by_id["AR-000000000005"]["severity"] == "info"      # weird_new_type


def test_risk_flags_bump_severity_one_step(garden):
    outbox, resolved, pen = garden
    (outbox / "AR-0000000000ff.json").write_text(
        json.dumps(bwf and _packet("AR-0000000000ff", "proposal", risk_flags=["contains_risk_markers"]))
    )
    feed = bwf.build_feed(outbox, resolved, pen)
    by_id = {p["packet_id"]: p for p in _all_packets(feed)}
    assert by_id["AR-0000000000ff"]["severity"] == "medium"  # proposal(low) bumped by flags


def test_proof_status_reflects_source_refs(garden):
    outbox, resolved, pen = garden
    (outbox / "AR-0000000000aa.json").write_text(
        json.dumps(_packet("AR-0000000000aa", "proposal", source_refs=["tools/x.py"]))
    )
    feed = bwf.build_feed(outbox, resolved, pen)
    by_id = {p["packet_id"]: p for p in _all_packets(feed)}
    assert by_id["AR-0000000000aa"]["proof_status"] == "grounded"
    assert by_id["AR-000000000001"]["proof_status"] == "ungrounded"  # no source_refs


def test_title_is_stable_and_capped(garden):
    feed = bwf.build_feed(*garden)
    for p in _all_packets(feed):
        assert 0 < len(p["title"]) <= 72
    # same input twice → identical titles (determinism)
    a = {p["packet_id"]: p["title"] for p in _all_packets(bwf.build_feed(*garden))}
    b = {p["packet_id"]: p["title"] for p in _all_packets(bwf.build_feed(*garden))}
    assert a == b


def test_marked_packet_carries_no_admission(garden):
    outbox, resolved, pen = garden
    (resolved / "AR-000000000001_marked.json").write_text(
        json.dumps({"packet_id": "AR-000000000001", "decision": "acted"})
    )
    feed = bwf.build_feed(outbox, resolved, pen)
    by_id = {p["packet_id"]: p for p in _all_packets(feed)}
    m = by_id["AR-000000000001"]
    assert m["mark"] == "acted"           # garden mark surfaces
    assert m["admission"] == "FORBIDDEN"  # ...but never becomes admission


def test_html_references_feed_js():
    html = (REPO_ROOT / "apps" / "goblin-warren" / "warren_town.html").read_text()
    assert "warren_town_feed.js" in html


def test_no_external_assets_in_html():
    html = (REPO_ROOT / "apps" / "goblin-warren" / "warren_town.html").read_text()
    assert "http://" not in html and "https://" not in html, "no external assets allowed"


def test_no_ui_text_claims_admission():
    for name in ("warren_town.html", "warren_town_feed.js"):
        txt = (REPO_ROOT / "apps" / "goblin-warren" / name).read_text().upper()
        assert "CONQUEST IS ADMITTED" not in txt
        assert "IS ADMITTED" not in txt
