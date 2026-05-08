import json
from pathlib import Path
from helen.ids import new_id, now_utc
from helen.hashing import sha256

LEDGER_PATH = Path("data/ledger.ndjson")


def load_ledger(path: Path = LEDGER_PATH) -> list[dict]:
    if not path.exists():
        return []
    events = []
    for line in path.read_text().splitlines():
        if line.strip():
            events.append(json.loads(line))
    return events


def last_hash(events: list[dict]) -> str:
    if not events:
        return "GENESIS"
    return events[-1]["event_hash"]


def make_event(event_type: str, payload: dict, prev_hash: str) -> dict:
    payload_hash = sha256(payload)
    base = {
        "event_id": new_id("E"),
        "event_type": event_type,
        "timestamp_utc": now_utc(),
        "prev_hash": prev_hash,
        "payload_hash": payload_hash,
        "payload": payload
    }
    event_hash = sha256(base)
    return {
        **base,
        "event_hash": event_hash
    }


def append_event(event_type: str, payload: dict, path: Path = LEDGER_PATH) -> dict:
    path.parent.mkdir(parents=True, exist_ok=True)
    events = load_ledger(path)
    ev = make_event(event_type, payload, last_hash(events))
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(ev, sort_keys=True, separators=(",", ":")) + "\n")
    return ev
