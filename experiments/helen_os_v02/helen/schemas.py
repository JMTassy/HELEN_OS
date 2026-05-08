from typing import Literal, TypedDict, NotRequired

Authority = Literal["NON_SOVEREIGN", "SYSTEM", "OPERATOR"]
Route = Literal["THINK", "INSPECT", "EXECUTE", "MEMORY_LOOKUP", "ORACLE_GATE"]
ActionType = Literal["SHELL", "NOOP"]
Verdict = Literal["NO_SHIP", "SHIP", "ABORT"]


class Intent(TypedDict):
    intent_id: str
    text: str
    requested_effect: str


class Action(TypedDict):
    action_id: str
    type: ActionType
    command: NotRequired[str]
    reason: str


class Proposal(TypedDict):
    proposal_id: str
    intent_id: str
    route: Route
    authority: Authority
    actions: list[Action]
    expected_artifacts: list[str]


class Artifact(TypedDict):
    artifact_id: str
    type: str
    content_hash: str
    content_preview: str


class Receipt(TypedDict):
    receipt_id: str
    proposal_id: str
    verified: bool
    artifacts: list[Artifact]
    verifier: str
    timestamp_utc: str


class LedgerEvent(TypedDict):
    event_id: str
    event_type: str
    timestamp_utc: str
    prev_hash: str
    payload_hash: str
    payload: dict
    event_hash: str
