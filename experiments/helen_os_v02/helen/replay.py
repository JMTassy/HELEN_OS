from helen.hashing import sha256
from helen.ledger import load_ledger


class ReplayError(Exception):
    pass


def verify_chain(events: list[dict]) -> bool:
    prev = "GENESIS"
    for ev in events:
        if ev["prev_hash"] != prev:
            raise ReplayError("prev_hash mismatch")
        event_copy = dict(ev)
        event_hash = event_copy.pop("event_hash")
        if sha256(event_copy) != event_hash:
            raise ReplayError("event_hash mismatch")
        prev = event_hash
    return True


def replay_state(events: list[dict]) -> dict:
    verify_chain(events)
    state = {
        "admitted_receipts": [],
        "last_route": None,
        "last_receipt_id": None,
        "last_proposal_id": None
    }
    for ev in events:
        if ev["event_type"] == "STATE_MUTATION":
            mutation = ev["payload"]["mutation"]
            state.update(mutation)
    return state


def replay(path="data/ledger.ndjson") -> dict:
    events = load_ledger()
    state = replay_state(events)
    return {
        "event_count": len(events),
        "state": state,
        "state_hash": sha256(state)
    }
