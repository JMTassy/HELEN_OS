from helen.ledger import append_event, load_ledger
from helen.replay import replay_state, verify_chain


def test_replay_chain_valid(tmp_path):
    path = tmp_path / "ledger.ndjson"
    append_event("STATE_MUTATION", {
        "mutation": {
            "last_receipt_id": "R-1",
            "admitted_receipts": ["R-1"]
        }
    }, path=path)
    events = load_ledger(path)
    assert verify_chain(events) is True
    state = replay_state(events)
    assert state["last_receipt_id"] == "R-1"


def test_replay_multi_event_chain(tmp_path):
    path = tmp_path / "ledger.ndjson"
    append_event("INTENT_RECEIVED", {"intent": {"intent_id": "I-1"}}, path=path)
    append_event("STATE_MUTATION", {
        "mutation": {"last_receipt_id": "R-2", "admitted_receipts": ["R-2"]}
    }, path=path)
    events = load_ledger(path)
    assert verify_chain(events) is True
    assert len(events) == 2
