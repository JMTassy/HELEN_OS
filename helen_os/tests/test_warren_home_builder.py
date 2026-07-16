"""test_warren_home_builder.py — WARREN HOME V1 rails.

Mirrors TRIAGE CANNOT CONSUME at the surface layer:
    SURFACE CANNOT MARK — the home displays organs, it never writes them.
authority=false · ledger_effect=none
"""

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "apps" / "goblin-warren"))
sys.path.insert(0, str(REPO / "temple" / "autoresearch"))

from build_warren_home import build_payload, render_js  # noqa: E402
import operator_pen as pen  # noqa: E402

HOME_HTML = (REPO / "apps" / "goblin-warren" / "warren_home.html").read_text()


def make_organs(tmp_path, n_packets=3, marks=()):
    outbox = tmp_path / "outbox"; outbox.mkdir()
    log = tmp_path / "consumption_log.ndjson"
    for i in range(n_packets):
        pid = f"AR-{i:012x}"
        (outbox / f"{pid}.json").write_text(json.dumps({
            "schema": "AUTORESEARCH_PACKET_V1", "packet_id": pid,
            "finding_type": "risk" if i == 0 else "proposal",
            "summary": f"Boundary-crossing findings in docs/x{i}.md: risk_marker",
            "source_refs": [], "risk_flags": [], "authority": False,
            "sovereign": False, "canon": False, "ledger_effect": "none",
            "reducer_required": True}))
    for pid, decision in marks:
        pen.mark(outbox, log, pid, decision, "test note", "JM")
    return outbox, log


def test_dreams_are_unconsumed_only(tmp_path):
    outbox, log = make_organs(tmp_path, 3, marks=[("AR-000000000000", "acted")])
    p = build_payload(outbox, log)
    ids = [d["packet_id"] for d in p["dreams"]]
    assert "AR-000000000000" not in ids and len(ids) == 2
    assert p["meters"]["reves_badge"] == 2


def test_payload_is_deterministic(tmp_path):
    outbox, log = make_organs(tmp_path, 3, marks=[("AR-000000000001", "rejected")])
    assert render_js(build_payload(outbox, log)) == render_js(build_payload(outbox, log))


def test_surface_cannot_mark_flag_and_no_pen_write(tmp_path):
    outbox, log = make_organs(tmp_path, 2)
    before = log.read_text() if log.exists() else ""
    p = build_payload(outbox, log)
    after = log.read_text() if log.exists() else ""
    assert p["surface_can_mark"] is False
    assert before == after, "building the home must never write the pen log"


def test_broken_chain_is_surfaced_not_hidden(tmp_path):
    outbox, log = make_organs(tmp_path, 2, marks=[("AR-000000000000", "acted")])
    entry = json.loads(log.read_text().splitlines()[0])
    entry["decision"] = "rejected"  # tamper without re-hash
    log.write_text(json.dumps(entry, separators=(",", ":")) + "\n")
    p = build_payload(outbox, log)
    assert p["pen_chain"].startswith("BROKEN")


def test_meters_are_bounded_and_labeled_as_renders(tmp_path):
    outbox, log = make_organs(tmp_path, 3,
                              marks=[("AR-000000000000", "acted"),
                                     ("AR-000000000001", "deferred")])
    p = build_payload(outbox, log)
    for k, v in p["meters"].items():
        assert 0 <= v <= 100, k
    assert "renderings of state" in p["law"]


def test_payload_carries_no_authority(tmp_path):
    outbox, log = make_organs(tmp_path, 1)
    p = build_payload(outbox, log)
    assert p["authority"] is False and p["ledger_effect"] == "none"
    js = render_js(p).upper()
    assert "IS ADMITTED" not in js and "CONQUEST ADMITTED" not in js


# --- surface (HTML) rails ------------------------------------------------------

def test_home_html_has_no_mark_or_admit_control():
    lowered = HOME_HTML.lower()
    for forbidden in ("--mark", "data-decision", "admit(", "mark(",
                      'name="decision"', "reducer_decision"):
        assert forbidden not in lowered, f"surface control found: {forbidden}"
    assert "SURFACE CANNOT MARK" in HOME_HTML


def test_home_html_has_no_external_assets():
    assert not re.findall(r'(?:src|href)\s*=\s*["\']https?://', HOME_HTML)
    assert not re.findall(r'url\(\s*["\']?https?://', HOME_HTML)
    assert "Math.random" not in HOME_HTML  # seeded rng only


def test_home_html_text_laws():
    for law in ("Les Gobelins rêvent", "Vous décidez",
                "rêve affiché ⊬ rêve admis", "authority=false",
                "ledger_effect=none", "operator_pen.py",
                "Chaque choix compte"):
        assert law in HOME_HTML, f"missing law text: {law}"
    up = HOME_HTML.upper().replace("N'EST PAS ADMIS", "X").replace("IS NOT ADMITTED", "X")
    assert "CONQUEST IS ADMITTED" not in up
