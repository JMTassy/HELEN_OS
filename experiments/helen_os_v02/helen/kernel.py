from pathlib import Path
import json
from helen.ids import new_id
from helen.planner import plan
from helen.executor import execute_proposal
from helen.receipts import build_receipt
from helen.reducer import reduce
from helen.ledger import append_event
from helen.mayor import explain_verdict

STATE_PATH = Path("data/state.json")
RECEIPTS_DIR = Path("data/receipts")


def load_state() -> dict:
    if not STATE_PATH.exists():
        return {
            "admitted_receipts": [],
            "last_route": None,
            "last_receipt_id": None,
            "last_proposal_id": None
        }
    return json.loads(STATE_PATH.read_text())


def save_state(state: dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=2, sort_keys=True))


def save_receipt(receipt: dict) -> None:
    RECEIPTS_DIR.mkdir(parents=True, exist_ok=True)
    path = RECEIPTS_DIR / f"{receipt['receipt_id']}.json"
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True))


def run_intent(text: str, requested_effect: str = "INSPECT") -> dict:
    intent = {
        "intent_id": new_id("I"),
        "text": text,
        "requested_effect": requested_effect
    }
    state = load_state()
    proposal = plan(intent)
    append_event("INTENT_RECEIVED", {"intent": intent})
    append_event("PROPOSAL_CREATED", {"proposal": proposal})
    artifacts = execute_proposal(proposal)
    append_event("ACTIONS_EXECUTED", {"artifacts": artifacts})
    receipt = build_receipt(proposal, artifacts)
    save_receipt(receipt)
    append_event("RECEIPT_BUILT", {"receipt": receipt})
    verdict = reduce(proposal, receipt, state)
    append_event("REDUCER_VERDICT", {"verdict": verdict})
    if verdict["admit"]:
        state.update(verdict["mutation"])
        save_state(state)
        append_event("STATE_MUTATION", {"mutation": verdict["mutation"]})
    mayor = explain_verdict(state)
    append_event("MAYOR_VERDICT", {"mayor": mayor})
    return {
        "intent": intent,
        "proposal": proposal,
        "artifacts": artifacts,
        "receipt": receipt,
        "reducer": verdict,
        "mayor": mayor
    }
