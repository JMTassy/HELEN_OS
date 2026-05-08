from pathlib import Path
import json
from helen.ids import new_id
from helen.planner import plan
from helen.executor import execute_proposal
from helen.receipts import build_receipt
from helen.reducer import reduce
from helen.ledger import append_event
from helen.mayor import explain_verdict
from helen.latent_trace import build_latent_trace
from helen.oracle_gate import assess as oracle_assess

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
    trace = build_latent_trace(proposal, artifacts)
    append_event("LATENT_TRACE", {"trace": trace})
    oracle = oracle_assess(intent["text"])
    append_event("ORACLE_ASSESSMENT", {"oracle": oracle})
    receipt = build_receipt(proposal, artifacts)
    save_receipt(receipt)
    append_event("RECEIPT_BUILT", {"receipt": receipt})
    verdict = reduce(proposal, receipt, state, trace=trace, oracle_assessment=oracle)
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
        "latent_trace": trace,
        "oracle": oracle,
        "receipt": receipt,
        "reducer": verdict,
        "mayor": mayor
    }
